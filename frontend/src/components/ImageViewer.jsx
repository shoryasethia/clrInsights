import { useState, useRef, useCallback } from 'react'
import { X, ZoomIn, ZoomOut, RotateCcw, Download, Copy, Check } from 'lucide-react'

export default function ImageViewer({ src, alt, onClose }) {
  const [scale, setScale] = useState(1)
  const [position, setPosition] = useState({ x: 0, y: 0 })
  const [dragging, setDragging] = useState(false)
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 })
  const [copied, setCopied] = useState(false)
  const imgRef = useRef(null)

  const zoomIn = () => setScale(s => Math.min(s + 0.25, 5))
  const zoomOut = () => setScale(s => Math.max(s - 0.25, 0.25))
  const resetView = () => { setScale(1); setPosition({ x: 0, y: 0 }) }

  const handleWheel = useCallback((e) => {
    e.preventDefault()
    const delta = e.deltaY > 0 ? -0.1 : 0.1
    setScale(s => Math.min(Math.max(s + delta, 0.25), 5))
  }, [])

  const handleMouseDown = (e) => {
    if (e.button !== 0) return
    setDragging(true)
    setDragStart({ x: e.clientX - position.x, y: e.clientY - position.y })
  }

  const handleMouseMove = (e) => {
    if (!dragging) return
    setPosition({ x: e.clientX - dragStart.x, y: e.clientY - dragStart.y })
  }

  const handleMouseUp = () => setDragging(false)

  const handleDownload = () => {
    const link = document.createElement('a')
    link.href = src
    link.download = `chart-${Date.now()}.png`
    link.click()
  }

  const handleCopy = async () => {
    try {
      const res = await fetch(src)
      const blob = await res.blob()
      await navigator.clipboard.write([
        new ClipboardItem({ 'image/png': blob })
      ])
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      // Fallback: copy as data URL
      try {
        await navigator.clipboard.writeText(src)
        setCopied(true)
        setTimeout(() => setCopied(false), 2000)
      } catch {}
    }
  }

  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget) onClose()
  }

  return (
    <div
      className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center"
      onClick={handleBackdropClick}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
    >
      {/* Toolbar */}
      <div className="absolute top-4 left-1/2 -translate-x-1/2 flex items-center gap-1 bg-[#181818] border border-gray-700 rounded-xl px-2 py-1.5 shadow-2xl z-10">
        <button onClick={zoomIn} className="p-2 hover:bg-gray-700 rounded-lg text-gray-300 hover:text-white transition-colors" title="Zoom in">
          <ZoomIn className="w-5 h-5" />
        </button>
        <button onClick={zoomOut} className="p-2 hover:bg-gray-700 rounded-lg text-gray-300 hover:text-white transition-colors" title="Zoom out">
          <ZoomOut className="w-5 h-5" />
        </button>
        <span className="text-gray-400 text-sm px-2 min-w-[3.5rem] text-center select-none">
          {Math.round(scale * 100)}%
        </span>
        <button onClick={resetView} className="p-2 hover:bg-gray-700 rounded-lg text-gray-300 hover:text-white transition-colors" title="Reset view">
          <RotateCcw className="w-5 h-5" />
        </button>
        <div className="w-px h-6 bg-gray-700 mx-1" />
        <button onClick={handleDownload} className="p-2 hover:bg-gray-700 rounded-lg text-gray-300 hover:text-white transition-colors" title="Save image">
          <Download className="w-5 h-5" />
        </button>
        <button onClick={handleCopy} className="p-2 hover:bg-gray-700 rounded-lg text-gray-300 hover:text-white transition-colors" title="Copy image">
          {copied ? <Check className="w-5 h-5 text-green-400" /> : <Copy className="w-5 h-5" />}
        </button>
        <div className="w-px h-6 bg-gray-700 mx-1" />
        <button onClick={onClose} className="p-2 hover:bg-red-900/50 rounded-lg text-gray-300 hover:text-red-400 transition-colors" title="Close">
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Image */}
      <div
        className="cursor-grab active:cursor-grabbing select-none"
        onMouseDown={handleMouseDown}
        onWheel={handleWheel}
        style={{
          transform: `translate(${position.x}px, ${position.y}px) scale(${scale})`,
          transition: dragging ? 'none' : 'transform 0.15s ease-out'
        }}
      >
        <img
          ref={imgRef}
          src={src}
          alt={alt}
          className="max-w-[90vw] max-h-[85vh] rounded-lg shadow-2xl pointer-events-none"
          draggable={false}
        />
      </div>
    </div>
  )
}
