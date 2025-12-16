import './globals.css'
import type { Metadata } from 'next'
import { AuthProvider } from '../lib/auth'

export const metadata: Metadata = {
  title: 'Personal AI Assistant',
  description: 'Self-hosted personal AI assistant',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  )
}

