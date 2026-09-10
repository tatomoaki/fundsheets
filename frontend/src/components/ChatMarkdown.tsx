import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import type { Components } from 'react-markdown'

// Tight, chat-bubble-friendly markdown rendering. Colors are inherited from
// the bubble (`currentColor`) so it reads correctly on both the assistant's
// light bubble and the user's dark/primary bubble.
const components: Components = {
  p: ({ children }) => <p className="[&:not(:first-child)]:mt-2">{children}</p>,
  strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
  em: ({ children }) => <em className="italic">{children}</em>,
  a: ({ children, href }) => (
    <a href={href} target="_blank" rel="noreferrer" className="underline underline-offset-2 hover:no-underline">
      {children}
    </a>
  ),
  ul: ({ children }) => <ul className="mt-2 mb-1 list-disc space-y-1 pl-4 first:mt-0">{children}</ul>,
  ol: ({ children }) => <ol className="mt-2 mb-1 list-decimal space-y-1 pl-4 first:mt-0">{children}</ol>,
  li: ({ children }) => <li className="leading-snug">{children}</li>,
  code: ({ children, className }) => {
    const isBlock = /language-/.test(className ?? '')
    if (isBlock) {
      return (
        <code className="block whitespace-pre-wrap rounded bg-black/10 px-2 py-1 font-mono text-xs">
          {children}
        </code>
      )
    }
    return <code className="rounded bg-black/10 px-1 py-0.5 font-mono text-xs">{children}</code>
  },
  pre: ({ children }) => <pre className="mt-2 overflow-x-auto first:mt-0">{children}</pre>,
  blockquote: ({ children }) => (
    <blockquote className="mt-2 border-l-2 border-current/30 pl-2 italic opacity-90 first:mt-0">
      {children}
    </blockquote>
  ),
  hr: () => <hr className="my-2 border-current/20" />,
  table: ({ children }) => (
    <div className="mt-2 overflow-x-auto first:mt-0">
      <table className="border-collapse text-xs">{children}</table>
    </div>
  ),
  th: ({ children }) => <th className="border border-current/20 px-1.5 py-1 text-left font-semibold">{children}</th>,
  td: ({ children }) => <td className="border border-current/20 px-1.5 py-1">{children}</td>,
}

export function ChatMarkdown({ content }: { content: string }) {
  return (
    <div className="[&>*:first-child]:mt-0">
      <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
        {content}
      </ReactMarkdown>
    </div>
  )
}
