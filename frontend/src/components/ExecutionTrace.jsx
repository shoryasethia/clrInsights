import { X, Terminal, ChevronDown, ChevronRight } from 'lucide-react'
import { useState } from 'react'

export default function ExecutionTrace({ steps, onClose }) {
  const [expandedSteps, setExpandedSteps] = useState(new Set())

  const toggleStep = (index) => {
    const newExpanded = new Set(expandedSteps)
    if (newExpanded.has(index)) {
      newExpanded.delete(index)
    } else {
      newExpanded.add(index)
    }
    setExpandedSteps(newExpanded)
  }

  return (
    <div className="w-96 bg-white dark:bg-[#181818] rounded-lg border border-gray-200 dark:border-gray-900 flex flex-col max-h-full shadow-xl">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-900">
        <div className="flex items-center gap-2">
          <Terminal className="w-5 h-5 text-gray-600 dark:text-gray-400" />
          <h3 className="font-semibold text-gray-900 dark:text-white">Execution Trace</h3>
        </div>
        <button
          onClick={onClose}
          className="btn-icon p-1"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Steps */}
      <div className="flex-1 overflow-y-auto p-4 space-y-2">
        {steps.length === 0 ? (
          <div className="text-sm text-gray-500 dark:text-gray-400 text-center py-8">
            No trace data yet
          </div>
        ) : (
          steps.map((step, index) => (
            <div 
              key={index}
              className="bg-gray-50 dark:bg-[#0f0f0f] rounded border border-gray-200 dark:border-gray-900 overflow-hidden"
            >
              {/* Step Header */}
              <div
                onClick={() => step.prompt && toggleStep(index)}
                className={`p-3 flex items-start gap-2 ${step.prompt ? 'cursor-pointer hover:bg-gray-100 dark:hover:bg-[#181818]' : ''}`}
              >
                {step.prompt && (
                  expandedSteps.has(index) 
                    ? <ChevronDown className="w-4 h-4 text-gray-500 mt-0.5 flex-shrink-0" />
                    : <ChevronRight className="w-4 h-4 text-gray-500 mt-0.5 flex-shrink-0" />
                )}
                <div className="flex-1 min-w-0">
                  <div className="text-xs text-gray-400 dark:text-gray-500 mb-1">
                    {step.timestamp}
                  </div>
                  <div className="text-sm text-gray-700 dark:text-gray-300 font-medium">
                    {step.text}
                  </div>
                  {step.type && (
                    <div className="mt-1">
                      <span className={`inline-block px-2 py-0.5 rounded text-xs ${
                        step.type === 'prompt' ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400' :
                        step.type === 'response' ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400' :
                        step.type === 'sql' ? 'bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400' :
                        step.type === 'error' ? 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400' :
                        'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-400'
                      }`}>
                        {step.type}
                      </span>
                    </div>
                  )}
                </div>
              </div>

              {/* Expanded Details */}
              {expandedSteps.has(index) && step.prompt && (
                <div className="border-t border-gray-200 dark:border-gray-700 p-3 space-y-3">
                  {/* Prompt */}
                  <div>
                    <div className="text-xs font-semibold text-gray-500 dark:text-gray-400 mb-1">
                      PROMPT:
                    </div>
                    <div className="text-xs font-mono bg-white dark:bg-gray-950 p-2 rounded border border-gray-200 dark:border-gray-700 max-h-32 overflow-y-auto whitespace-pre-wrap text-gray-800 dark:text-gray-300">
                      {step.prompt}
                    </div>
                  </div>

                  {/* Response */}
                  {step.response && (
                    <div>
                      <div className="text-xs font-semibold text-gray-500 dark:text-gray-400 mb-1">
                        RESPONSE:
                      </div>
                      <div className="text-xs font-mono bg-white dark:bg-gray-950 p-2 rounded border border-gray-200 dark:border-gray-700 max-h-32 overflow-y-auto whitespace-pre-wrap text-gray-800 dark:text-gray-300">
                        {step.response}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  )
}
