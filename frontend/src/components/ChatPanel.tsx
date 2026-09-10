import { useEffect, useRef, useState } from 'react'
import { Bot, Send, User } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { ChatMarkdown } from '@/components/ChatMarkdown'
import { cn } from '@/lib/utils'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
}

interface ChatPanelProps {
  fund: { id: string; name: string } | null
}

export function ChatPanel({ fund }: ChatPanelProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '0',
      role: 'assistant',
      content: "Hi! I can help you analyse funds, compare performance, or explain anything you see on screen. What would you like to know?",
    },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  async function handleSend() {
    const text = input.trim()
    if (!text || loading || !fund) return

    const userMsg: Message = { id: crypto.randomUUID(), role: 'user', content: text }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setLoading(true)

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          fund_id: fund.id,
          message: text,
          history: messages.map(({ role, content }) => ({ role, content })),
        }),
      })

      if (!res.ok) throw new Error('Request failed')
      const data = await res.json()

      setMessages(prev => [
        ...prev,
        { id: crypto.randomUUID(), role: 'assistant', content: data.reply },
      ])
    } catch {
      setMessages(prev => [
        ...prev,
        { id: crypto.randomUUID(), role: 'assistant', content: "Sorry, I couldn't reach the server. Please try again." },
      ])
    } finally {
      setLoading(false)
    }
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="flex flex-col w-80 shrink-0 border-l bg-background h-full">
      {/* Header */}
      <div className="flex items-center gap-2 px-4 h-10 border-b shrink-0">
        <Bot className="size-4 text-primary" />
        <span className="text-sm font-semibold">AI Assistant</span>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-3 py-4 space-y-4 min-h-0">
        {messages.map(msg => (
          <div
            key={msg.id}
            className={cn('flex gap-2 items-start', msg.role === 'user' && 'flex-row-reverse')}
          >
            <div className={cn(
              'flex size-6 shrink-0 items-center justify-center rounded-full mt-0.5',
              msg.role === 'assistant' ? 'bg-primary text-primary-foreground' : 'bg-muted',
            )}>
              {msg.role === 'assistant'
                ? <Bot className="size-3.5" />
                : <User className="size-3.5" />
              }
            </div>

            <div className={cn(
              'rounded-lg px-3 py-2 text-sm leading-relaxed max-w-[calc(100%-2rem)]',
              msg.role === 'assistant'
                ? 'bg-muted text-foreground'
                : 'bg-primary text-primary-foreground',
            )}>
              <ChatMarkdown content={msg.content} />
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex gap-2 items-start">
            <div className="flex size-6 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground mt-0.5">
              <Bot className="size-3.5" />
            </div>
            <div className="bg-muted rounded-lg px-3 py-2">
              <span className="flex gap-1">
                <span className="size-1.5 rounded-full bg-muted-foreground animate-bounce [animation-delay:0ms]" />
                <span className="size-1.5 rounded-full bg-muted-foreground animate-bounce [animation-delay:150ms]" />
                <span className="size-1.5 rounded-full bg-muted-foreground animate-bounce [animation-delay:300ms]" />
              </span>
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="shrink-0 border-t px-3 py-3 flex gap-2">
        <Input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={fund ? 'Ask about funds...' : 'Select a fund to start chatting'}
          className="text-sm h-8"
          disabled={loading || !fund}
        />
        <Button
          size="icon-sm"
          onClick={handleSend}
          disabled={!input.trim() || loading || !fund}
        >
          <Send className="size-3.5" />
        </Button>
      </div>
    </div>
  )
}
