# February 2026 - Change History

## Planning updates + requirements clarified

### Changes / Decisions (Plain English)
- We want better capture via a CLI menu and a chatbot ingestion flow.
- Classifications should be flexible and evolve over time.
- We will use Postgres as the primary store, and store schema definitions there too.
- Schema evolution should start with manual categories, plus LLM suggestions that require user approval.
- Chatbot is for conversation and capture only, with chat history tracked.
- Review queue should be accessible via CLI and chatbot.
- No push "tap on the shoulder" reminders; only pull-based reminders on request.
- Use local RunPod-based LLM only for now; optional OpenAI/Claude later.
- Replace curl usage with CLI usage where possible.
- Keep frontend available, but make CLI the primary capture path.

### In Progress
- None (implementation started)

### Complete
- CLI capture menu and chatbot capture mode
- Dynamic schema registry (CategorySchema)
- Capture queue and review endpoints (approve/reject)
- Audit trail (IngestionLog)
- Structured entries and classification service
- Documentation updates for CLI usage

### Implementation Notes
- Added a CLI at `backend/cli/assistant_cli.py` for capture, review, and chat.
- Added dynamic schema endpoints at `/api/schema`.
- Added capture endpoints at `/api/capture` and review endpoints at `/api/review`.
- Chat endpoint supports `mode: "capture"` for direct ingestion.
