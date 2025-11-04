import React, { useRef, useEffect, useState } from 'react';
import { useForceWorker } from './useForceWorker';

interface WebGLRendererProps {
  data: { nodes: any[]; edges: any[] };
  width: number;
  height: number;
  pan?: [number, number];
  zoom?: number;
  edgeOpacity?: number;
  forceWorkerEnabled?: boolean;
  quadTreeWorkerEnabled?: boolean;
}

export const WebGLRenderer: React.FC<WebGLRendererProps> = ({
  data,
  width,
  height,
  pan = [0, 0],
  zoom = 1.0,
  edgeOpacity = 1.0,
  forceWorkerEnabled = false,
  quadTreeWorkerEnabled = false
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [layoutNodes, setLayoutNodes] = useState(data.nodes);
  const [visibleNodes, setVisibleNodes] = useState(data.nodes);
  const worker = useForceWorker(forceWorkerEnabled);

  // 30Hz throttle for worker updates
  useEffect(() => {
    if (!forceWorkerEnabled) return;
    let rafId: number;
    const updateLayout = () => {
      worker.start(data.nodes, data.edges, 10, (result) => {
        setLayoutNodes(result.nodes);
        rafId = requestAnimationFrame(updateLayout);
      });
    };
    updateLayout();
    return () => {
      if (rafId) cancelAnimationFrame(rafId);
      worker.stop();
    };
  }, [data, forceWorkerEnabled, worker]);

  // Quad-tree culling for large datasets
  useEffect(() => {
    if (!quadTreeWorkerEnabled) {
      setVisibleNodes(layoutNodes);
      return;
    }

    const quadWorker = new Worker(new URL('../../workers/quadtree.worker.ts', import.meta.url));
    const viewport = [0, 0, width, height]; // Simple viewport, could be enhanced with pan/zoom

    quadWorker.onmessage = (e) => {
      const quadtree = e.data.quadtree;
      const culledNodes = quadtree.query(viewport);
      setVisibleNodes(culledNodes);
    };

    quadWorker.postMessage({
      nodes: layoutNodes,
      bounds: [0, 0, width, height],
      maxDepth: 8
    });

    return () => quadWorker.terminate();
  }, [layoutNodes, width, height, quadTreeWorkerEnabled]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const gl = canvas.getContext('webgl');
    if (!gl) {
      console.error('WebGL not supported');
      return;
    }

    // Clear canvas
    gl.clearColor(0.0, 0.0, 0.0, 1.0);
    gl.clear(gl.COLOR_BUFFER_BIT);

    // Vertex shader with pan/zoom uniforms
    const vsSource = `
      attribute vec2 aPos;
      uniform float uPointSize;
      uniform vec2 u_pan;
      uniform float u_zoom;
      void main() {
        vec2 p = aPos * u_zoom + u_pan;
        gl_Position = vec4(p, 0.0, 1.0);
        gl_PointSize = uPointSize;
      }
    `;

    // Fragment shader with opacity uniform
    const fsSource = `
      precision mediump float;
      uniform float u_opacity;
      void main() {
        gl_FragColor = vec4(0.20, 0.40, 0.80, u_opacity);
      }
    `;

    // Create shaders
    const vertexShader = gl.createShader(gl.VERTEX_SHADER)!;
    gl.shaderSource(vertexShader, vsSource);
    gl.compileShader(vertexShader);

    const fragmentShader = gl.createShader(gl.FRAGMENT_SHADER)!;
    gl.shaderSource(fragmentShader, fsSource);
    gl.compileShader(fragmentShader);

    // Create program
    const program = gl.createProgram()!;
    gl.attachShader(program, vertexShader);
    gl.attachShader(program, fragmentShader);
    gl.linkProgram(program);
    gl.useProgram(program);

    // Instanced rendering setup (points)
    const ext = gl.getExtension('ANGLE_instanced_arrays');
    if (ext) {
      const instanceBuffer = gl.createBuffer();
      gl.bindBuffer(gl.ARRAY_BUFFER, instanceBuffer);
      gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(
        visibleNodes.flatMap(n => [
          (n.x / width) * 2 - 1,
          1 - (n.y / height) * 2
        ])
      ), gl.STATIC_DRAW);
      const posLoc = gl.getAttribLocation(program, 'aPos');
      gl.enableVertexAttribArray(posLoc);
      gl.vertexAttribPointer(posLoc, 2, gl.FLOAT, false, 0, 0);
      ext.vertexAttribDivisorANGLE(posLoc, 1);  // Per-instance
      // Draw instanced
      ext.drawArraysInstancedANGLE(gl.POINTS, 0, 1, visibleNodes.length);
    } else {
      // Fallback to regular rendering
      const nodeBuffer = gl.createBuffer();
      gl.bindBuffer(gl.ARRAY_BUFFER, nodeBuffer);
      const nodeData = new Float32Array(
        visibleNodes.flatMap(n => [
          (n.x / width) * 2 - 1,
          1 - (n.y / height) * 2
        ])
      );
      gl.bufferData(gl.ARRAY_BUFFER, nodeData, gl.STATIC_DRAW);
      const posLoc = gl.getAttribLocation(program, 'aPos');
      gl.enableVertexAttribArray(posLoc);
      gl.vertexAttribPointer(posLoc, 2, gl.FLOAT, false, 0, 0);
      gl.drawArrays(gl.POINTS, 0, visibleNodes.length);
    }

    // Set uniforms
    gl.uniform1f(gl.getUniformLocation(program, 'uPointSize'), 5.0);
    gl.uniform2fv(gl.getUniformLocation(program, 'u_pan'), new Float32Array(pan));
    gl.uniform1f(gl.getUniformLocation(program, 'u_zoom'), zoom);
    gl.uniform1f(gl.getUniformLocation(program, 'u_opacity'), edgeOpacity);

  }, [data, width, height, pan, zoom, edgeOpacity, visibleNodes]);

  return (
    <canvas
      ref={canvasRef}
      width={width}
      height={height}
      style={{ border: '1px solid #ccc' }}
    />
  );
};
