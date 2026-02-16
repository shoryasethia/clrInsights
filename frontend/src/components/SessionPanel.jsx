import { MessageSquare, Trash2, Edit2, Check, X } from 'lucide-react'
import { useState } from 'react'

export default function SessionPanel({ sessions, currentSessionId, onSelectSession, onDeleteSession, onRenameSession, onNewSession, onClose }) {
  const [editingId, setEditingId] = useState(null)
  const [editTitle, setEditTitle] = useState('')

  const startEdit = (session) => {
    setEditingId(session.id)
    setEditTitle(session.title)
  }

  const saveEdit = () => {
    if (editTitle.trim()) {
      onRenameSession(editingId, editTitle.trim())
    }
    setEditingId(null)
  }

  const cancelEdit = () => {
    setEditingId(null)
    setEditTitle('')
  }

  return (
    <div className="w-64 bg-white dark:bg-[#181818] border-r border-gray-200 dark:border-gray-900 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-900 flex items-center justify-between">
        <button
          onClick={onNewSession}
          className="flex-1 btn-primary flex items-center justify-center gap-2"
        >
          <MessageSquare className="w-4 h-4" />
          New Chat
        </button>
        <button
          onClick={onClose}
          className="btn-icon ml-2 p-1"
          title="Close sidebar"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Sessions List */}
      <div className="flex-1 overflow-y-auto scrollbar-hidden p-2 space-y-1">
        {sessions.length === 0 ? (
          <div className="text-center text-gray-500 dark:text-gray-400 text-sm py-8">
            No sessions yet
          </div>
        ) : (
          sessions.map((session) => (
            <div
              key={session.id}
              className={`group relative p-3 rounded-lg cursor-pointer transition-colors ${
                currentSessionId === session.id
                  ? 'bg-primary-100 dark:bg-[#222] border border-primary-200 dark:border-gray-800'
                  : 'hover:bg-gray-50 dark:hover:bg-[#202020]'
              }`}
              onClick={() => onSelectSession(session.id)}
            >
              {editingId === session.id ? (
                <div className="flex items-center gap-1" onClick={(e) => e.stopPropagation()}>
                  <input
                    type="text"
                    value={editTitle}
                    onChange={(e) => setEditTitle(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') saveEdit()
                      if (e.key === 'Escape') cancelEdit()
                    }}
                    className="flex-1 px-2 py-1 text-sm bg-white dark:bg-[#0f0f0f] border border-gray-300 dark:border-gray-800 rounded text-gray-900 dark:text-gray-100"
                    autoFocus
                  />
                  <button onClick={saveEdit} className="p-1 text-green-600 hover:bg-green-50 dark:hover:bg-green-900/20 rounded">
                    <Check className="w-4 h-4" />
                  </button>
                  <button onClick={cancelEdit} className="p-1 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded">
                    <X className="w-4 h-4" />
                  </button>
                </div>
              ) : (
                <>
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium text-gray-900 dark:text-white truncate">
                        {session.title}
                      </div>
                      <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                        {new Date(session.created_at).toLocaleDateString()}
                      </div>
                    </div>
                    <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          startEdit(session)
                        }}
                        className="p-1 hover:bg-gray-200 dark:hover:bg-gray-600 rounded"
                      >
                        <Edit2 className="w-3 h-3" />
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          onDeleteSession(session.id)
                        }}
                        className="p-1 hover:bg-red-100 dark:hover:bg-red-900/20 text-red-600 rounded"
                      >
                        <Trash2 className="w-3 h-3" />
                      </button>
                    </div>
                  </div>
                </>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  )
}
