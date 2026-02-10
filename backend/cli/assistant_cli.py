"""
CLI tool for capture and review workflows.
"""
import os
import json
import httpx


API_URL = os.getenv("ASSISTANT_API_URL", "http://localhost:8000")
TOKEN = os.getenv("ASSISTANT_TOKEN")


def get_headers():
    if not TOKEN:
        raise RuntimeError("ASSISTANT_TOKEN not set. Export it before using the CLI.")
    return {"Authorization": f"Bearer {TOKEN}"}


def print_menu():
    print("\nPersonal Assistant CLI")
    print("1) Quick Capture (raw thought)")
    print("2) Chat Capture (classification)")
    print("3) Review Queue")
    print("4) Chat (normal)")
    print("5) Exit")


def quick_capture():
    text = input("Enter content: ").strip()
    if not text:
        print("No content provided.")
        return
    payload = {"content": text, "source": "cli"}
    resp = httpx.post(f"{API_URL}/api/capture/", json=payload, headers=get_headers())
    if resp.status_code != 201:
        print("Error:", resp.text)
        return
    data = resp.json()
    print(f"Captured #{data['id']} (status: {data['status']})")
    if data.get("suggested_category"):
        print(f"Suggested category: {data['suggested_category']} (confidence {data.get('confidence')}%)")


def chat_capture():
    text = input("Enter content for capture: ").strip()
    if not text:
        print("No content provided.")
        return
    payload = {"message": text, "mode": "capture", "use_rag": False}
    resp = httpx.post(f"{API_URL}/api/chat/", json=payload, headers=get_headers())
    if resp.status_code != 200:
        print("Error:", resp.text)
        return
    data = resp.json()
    print(data.get("message"))
    if data.get("follow_up_questions"):
        print("Follow-up questions:")
        for q in data["follow_up_questions"]:
            print(f"- {q}")
    if data.get("capture_id"):
        print(f"Capture ID: {data['capture_id']}")


def review_queue():
    resp = httpx.get(f"{API_URL}/api/capture/queue", headers=get_headers())
    if resp.status_code != 200:
        print("Error:", resp.text)
        return
    items = resp.json()
    if not items:
        print("No items in review queue.")
        return
    print("\nReview Queue:")
    for item in items:
        print(f"- ID {item['id']} | status {item['status']} | conf {item.get('confidence')}")
        print(f"  content: {item['content'][:120]}")
        if item.get("suggested_category"):
            print(f"  suggested: {item['suggested_category']}")
    action = input("Approve (a) / Reject (r) / Back (b): ").strip().lower()
    if action not in ["a", "r"]:
        return
    item_id = input("Enter capture ID: ").strip()
    if action == "r":
        reason = input("Reason (optional): ").strip()
        resp = httpx.post(
            f"{API_URL}/api/review/{item_id}/reject",
            params={"reason": reason},
            headers=get_headers()
        )
        print(resp.json())
        return
    # Approve
    category = input("Category (leave blank to use suggested): ").strip() or None
    title = input("Title (optional): ").strip() or None
    fields_raw = input("Fields JSON (leave blank to use suggested): ").strip()
    fields = None
    if fields_raw:
        try:
            fields = json.loads(fields_raw)
        except json.JSONDecodeError:
            print("Invalid JSON. Aborting.")
            return
    payload = {
        "category": category,
        "title": title,
        "fields": fields
    }
    resp = httpx.post(
        f"{API_URL}/api/review/{item_id}/approve",
        json=payload,
        headers=get_headers()
    )
    if resp.status_code != 200:
        print("Error:", resp.text)
        return
    print("Approved entry:", resp.json())


def chat_normal():
    text = input("Message: ").strip()
    if not text:
        return
    payload = {"message": text, "use_rag": True}
    resp = httpx.post(f"{API_URL}/api/chat/", json=payload, headers=get_headers())
    if resp.status_code != 200:
        print("Error:", resp.text)
        return
    data = resp.json()
    print(data.get("message"))


def main():
    while True:
        print_menu()
        choice = input("Select: ").strip()
        if choice == "1":
            quick_capture()
        elif choice == "2":
            chat_capture()
        elif choice == "3":
            review_queue()
        elif choice == "4":
            chat_normal()
        elif choice == "5":
            print("Goodbye.")
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()
