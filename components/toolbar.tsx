"use client"

import React from "react"

interface ToolbarProps {
  onLoadFile: (file?: File) => void
  loading: boolean
}

export function Toolbar({ onLoadFile, loading }: ToolbarProps) {
  const fileInputRef = React.useRef<HTMLInputElement>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      onLoadFile(file)
    }
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    e.currentTarget.classList.add("bg-accent/10")
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.currentTarget.classList.remove("bg-accent/10")
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.currentTarget.classList.remove("bg-accent/10")
    const file = e.dataTransfer.files?.[0]
    if (file) {
      onLoadFile(file)
    }
  }

  return (
    <div className="border-b border-border p-4 bg-card flex gap-3 items-center">
      <button
        onClick={() => fileInputRef.current?.click()}
        disabled={loading}
        className="px-4 py-2 bg-primary text-primary-foreground rounded hover:opacity-90 disabled:opacity-50 font-medium text-sm"
      >
        {loading ? "Loading..." : "Upload Envelope"}
      </button>

      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className="flex-1 border-2 border-dashed border-border rounded p-3 text-center text-sm text-muted-foreground transition-colors cursor-pointer hover:border-primary hover:bg-primary/5"
      >
        Or drag and drop JSON file here
      </div>

      <input ref={fileInputRef} type="file" accept=".json" onChange={handleFileChange} className="hidden" />
    </div>
  )
}
