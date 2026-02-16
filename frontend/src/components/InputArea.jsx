import { Send } from 'lucide-react'

export default function InputArea({ input, setInput, loading, onSend, onKeyDown }) {
  return (
    <div className="bg-white dark:bg-[#181818] rounded-lg border border-gray-200 dark:border-gray-900 p-3 flex gap-3">
      <textarea
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={onKeyDown}
        placeholder="Ask a question about your data..."
        rows="2"
        disabled={loading}
        className="flex-1 bg-transparent border-none focus:outline-none resize-none text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500"
      />
      <button
        onClick={onSend}
        disabled={loading || !input.trim()}
        className="btn-primary h-10 px-4 self-end"
      >
        <Send className="w-4 h-4" />
      </button>
    </div>
  )
}
