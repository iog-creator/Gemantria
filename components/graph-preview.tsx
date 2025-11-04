"use client"

import type React from "react"
import { useRef, useEffect, useState } from "react"
import type { Envelope, SelectedItems } from "@/lib/types"

interface GraphPreviewProps {
  envelope: Envelope | null
  selection: SelectedItems
  onSelectionChange: (nodeIds: Set<string>, edgeIds: Set<string>) => void
}

interface NodePosition {
  id: string
  x: number
  y: number
  label: string
  type?: string
}

export function GraphPreview({ envelope, selection, onSelectionChange }: GraphPreviewProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [nodePositions, setNodePositions] = useState<Map<string, NodePosition>>(new Map())
  const [hoveredNode, setHoveredNode] = useState<string | null>(null)
  const [pan, setPan] = useState({ x: 0, y: 0 })
  const [zoom, setZoom] = useState(1)

  useEffect(() => {
    if (!envelope || envelope.nodes.length === 0) return

    const angleSlice = (2 * Math.PI) / envelope.nodes.length
    const radius = Math.min(300, 50 + 100 * Math.log(envelope.nodes.length + 1))

    const positions = new Map<string, NodePosition>()
    envelope.nodes.forEach((node, idx) => {
      const angle = angleSlice * idx
      const x = radius * Math.cos(angle)
      const y = radius * Math.sin(angle)
      positions.set(node.id, {
        id: node.id,
        x,
        y,
        label: node.label,
        type: node.type,
      })
    })

    setNodePositions(positions)
  }, [envelope])

  const typeColorMap: Record<string, string> = {
    untyped: "#8b5cf6",
    input: "#3b82f6",
    output: "#10b981",
    process: "#f59e0b",
  }

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas || !envelope) return

    const ctx = canvas.getContext("2d")
    if (!ctx) return

    // Set canvas size
    canvas.width = canvas.offsetWidth
    canvas.height = canvas.offsetHeight

    // Clear canvas
    ctx.fillStyle = "#ffffff"
    ctx.fillRect(0, 0, canvas.width, canvas.height)

    const centerX = canvas.width / 2
    const centerY = canvas.height / 2

    // Draw edges
    ctx.strokeStyle = "#d1d5db"
    ctx.lineWidth = 1
    envelope.edges.forEach((edge) => {
      const src = nodePositions.get(edge.src)
      const dst = nodePositions.get(edge.dst)

      if (src && dst) {
        const x1 = centerX + (src.x * zoom + pan.x)
        const y1 = centerY + (src.y * zoom + pan.y)
        const x2 = centerX + (dst.x * zoom + pan.x)
        const y2 = centerY + (dst.y * zoom + pan.y)

        // Highlight selected edges
        if (selection.edgeIds.has(`${edge.src}-${edge.dst}`)) {
          ctx.strokeStyle = "#fbbf24"
          ctx.lineWidth = 3
        } else {
          ctx.strokeStyle = "#d1d5db"
          ctx.lineWidth = edge.weight ? 1 + edge.weight : 1
        }

        ctx.beginPath()
        ctx.moveTo(x1, y1)
        ctx.lineTo(x2, y2)
        ctx.stroke()

        // Draw edge label
        if (edge.rel_type) {
          const midX = (x1 + x2) / 2
          const midY = (y1 + y2) / 2
          ctx.fillStyle = "#666666"
          ctx.font = "10px sans-serif"
          ctx.textAlign = "center"
          ctx.fillText(edge.rel_type, midX, midY - 5)
        }
      }
    })

    // Draw nodes
    nodePositions.forEach((node) => {
      const x = centerX + (node.x * zoom + pan.x)
      const y = centerY + (node.y * zoom + pan.y)
      const radius = 24
      const isSelected = selection.nodeIds.has(node.id)
      const isHovered = hoveredNode === node.id

      // Draw node circle
      const color = typeColorMap[node.type || "untyped"] || "#6b7280"
      ctx.fillStyle = isHovered ? "#fbbf24" : color
      ctx.beginPath()
      ctx.arc(x, y, radius, 0, 2 * Math.PI)
      ctx.fill()

      // Draw border
      ctx.strokeStyle = isSelected ? "#fbbf24" : "rgba(255,255,255,0.3)"
      ctx.lineWidth = isSelected ? 3 : 2
      ctx.stroke()

      // Draw label
      ctx.fillStyle = "#ffffff"
      ctx.font = "bold 11px sans-serif"
      ctx.textAlign = "center"
      ctx.textBaseline = "middle"

      const maxLength = 10
      const truncatedLabel = node.label.length > maxLength ? node.label.slice(0, maxLength - 1) + "…" : node.label

      ctx.fillText(truncatedLabel, x, y)
    })
  }, [envelope, nodePositions, selection, pan, zoom, hoveredNode])

  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current
    if (!canvas) return

    const rect = canvas.getBoundingClientRect()
    const mouseX = e.clientX - rect.left
    const mouseY = e.clientY - rect.top

    const centerX = canvas.width / 2
    const centerY = canvas.height / 2

    let foundNode: string | null = null
    nodePositions.forEach((node) => {
      const x = centerX + (node.x * zoom + pan.x)
      const y = centerY + (node.y * zoom + pan.y)
      const distance = Math.sqrt((mouseX - x) ** 2 + (mouseY - y) ** 2)

      if (distance < 24) {
        foundNode = node.id
      }
    })

    setHoveredNode(foundNode)
    canvas.style.cursor = foundNode ? "pointer" : "grab"
  }

  const handleMouseClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current
    if (!canvas) return

    const rect = canvas.getBoundingClientRect()
    const mouseX = e.clientX - rect.left
    const mouseY = e.clientY - rect.top

    const centerX = canvas.width / 2
    const centerY = canvas.height / 2

    let clickedNode: string | null = null
    nodePositions.forEach((node) => {
      const x = centerX + (node.x * zoom + pan.x)
      const y = centerY + (node.y * zoom + pan.y)
      const distance = Math.sqrt((mouseX - x) ** 2 + (mouseY - y) ** 2)

      if (distance < 24) {
        clickedNode = node.id
      }
    })

    if (clickedNode) {
      const newSelection = new Set(selection.nodeIds)
      if (newSelection.has(clickedNode)) {
        newSelection.delete(clickedNode)
      } else {
        newSelection.add(clickedNode)
      }
      onSelectionChange(newSelection, new Set())
    }
  }

  const handleWheel = (e: React.WheelEvent<HTMLCanvasElement>) => {
    e.preventDefault()
    const zoomSpeed = 0.1
    const newZoom = Math.max(0.5, Math.min(3, zoom + (e.deltaY > 0 ? -zoomSpeed : zoomSpeed)))
    setZoom(newZoom)
  }

  if (!envelope || envelope.nodes.length === 0) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-card text-muted-foreground">
        No nodes to display. Upload an envelope to get started.
      </div>
    )
  }

  return (
    <div className="w-full h-full relative bg-white overflow-hidden">
      <canvas
        ref={canvasRef}
        className="w-full h-full"
        onMouseMove={handleMouseMove}
        onClick={handleMouseClick}
        onWheel={handleWheel}
      />
      <div className="absolute bottom-4 right-4 bg-black/50 text-white text-xs px-3 py-2 rounded">
        <div>Zoom: {zoom.toFixed(2)}x</div>
        <div>Nodes: {envelope.nodes.length}</div>
        <div>Edges: {envelope.edges.length}</div>
      </div>
    </div>
  )
}
