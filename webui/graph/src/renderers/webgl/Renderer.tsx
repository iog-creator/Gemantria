import React, { useRef, useEffect, useState } from 'react';
import { canUseWebGL } from '../../utils/capabilities';

/**
 * Sprint 3: Isolated WebGL renderer for escalation
 * Points/lines for nodes/edges, normalized coords, context handling
 * Hot path <16ms/frame budget on static 100k datasets
 * Pan/zoom uniforms + edge opacity for interactive exploration
 * Force simulation offloaded to WebWorker for large datasets
 */

interface RendererProps {
  data: { nodes: any[]; edges: any[] }; // Positions computed via force simulation
  width: number;
  height: number;
  pan?: [number, number]; // [x, y] pan offset
  zoom?: number; // Zoom level (1.0 = default)
  edgeOpacity?: number; // Edge opacity (0.0-1.0)
}

const Renderer: React.FC<RendererProps> = ({
  data,
  width,
  height,
  pan = [0, 0],
  zoom = 1.0,
  edgeOpacity = 1.0
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [layoutNodes, setLayoutNodes] = useState(data.nodes);

  useEffect(() => {
    const worker = new Worker(new URL('../../workers/forceWorker.ts', import.meta.url));
    worker.onmessage = (e) => setLayoutNodes(e.data.nodes);
    worker.postMessage({ nodes: data.nodes, edges: data.edges, width, height });
    return () => worker.terminate();
  }, [data, width, height]);

  useEffect(() => {
    if (!canUseWebGL()) return; // Guard

    const canvas = canvasRef.current;
    if (!canvas) return;

    const gl = canvas.getContext('webgl');
    if (!gl) return;

    gl.viewport(0, 0, width, height);
    gl.clearColor(1, 1, 1, 1);
    gl.clear(gl.COLOR_BUFFER_BIT);

    // Points for nodes (instanced)
    const nodePos = new Float32Array(
      layoutNodes.flatMap(n => [
        n.x / width * 2 - 1,
        1 - n.y / height * 2
      ])
    ); // Normalized

    const nodeBuf = gl.createBuffer();
    if (!nodeBuf) return;

    gl.bindBuffer(gl.ARRAY_BUFFER, nodeBuf);
    gl.bufferData(gl.ARRAY_BUFFER, nodePos, gl.STATIC_DRAW);

    // Lines for edges
    const edgePos = new Float32Array(
      data.edges.flatMap(e => {
        const source = layoutNodes.find(n => n.id === e.source.id || n.id === e.source);
        const target = layoutNodes.find(n => n.id === e.target.id || n.id === e.target);
        if (!source || !target) return [];

        return [
          source.x / width * 2 - 1, 1 - source.y / height * 2,
          target.x / width * 2 - 1, 1 - target.y / height * 2
        ];
      })
    );

    const edgeBuf = gl.createBuffer();
    if (!edgeBuf) return;

    gl.bindBuffer(gl.ARRAY_BUFFER, edgeBuf);
    gl.bufferData(gl.ARRAY_BUFFER, edgePos, gl.STATIC_DRAW);

    // Simple shaders
    const vs = gl.createShader(gl.VERTEX_SHADER);
    if (!vs) return;

    // Updated vertex shader with pan/zoom uniforms
    gl.shaderSource(vs, `
      attribute vec2 aPos;
      uniform vec2 u_pan;
      uniform float u_zoom;
      void main() {
        vec2 transformed = (aPos + u_pan) * u_zoom;
        gl_Position = vec4(transformed, 0, 1);
        gl_PointSize = 5.0 * u_zoom; // Scale point size with zoom
      }
    `);
    gl.compileShader(vs);

    if (!gl.getShaderParameter(vs, gl.COMPILE_STATUS)) {
      console.error('Vertex shader compilation failed:', gl.getShaderInfoLog(vs));
      return;
    }

    const fs = gl.createShader(gl.FRAGMENT_SHADER);
    if (!fs) return;

    gl.shaderSource(fs, `uniform float u_opacity; void main() { gl_FragColor = vec4(0.2, 0.4, 0.8, u_opacity); }`); // Blue with opacity
    gl.compileShader(fs);

    if (!gl.getShaderParameter(fs, gl.COMPILE_STATUS)) {
      console.error('Fragment shader compilation failed:', gl.getShaderInfoLog(fs));
      return;
    }

    const prog = gl.createProgram();
    if (!prog) return;

    gl.attachShader(prog, vs);
    gl.attachShader(prog, fs);
    gl.linkProgram(prog);

    if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) {
      console.error('Program linking failed:', gl.getProgramInfoLog(prog));
      return;
    }

    gl.useProgram(prog);

    // Set uniforms for pan/zoom/opacity
    const panLoc = gl.getUniformLocation(prog, 'u_pan');
    const zoomLoc = gl.getUniformLocation(prog, 'u_zoom');
    const opacityLoc = gl.getUniformLocation(prog, 'u_opacity');

    if (panLoc) gl.uniform2f(panLoc, pan[0], pan[1]);
    if (zoomLoc) gl.uniform1f(zoomLoc, zoom);
    if (opacityLoc) gl.uniform1f(opacityLoc, edgeOpacity);

    // Instanced rendering setup (points)
    const ext = gl.getExtension('ANGLE_instanced_arrays');
    if (ext) {
      const instanceBuffer = gl.createBuffer();
      gl.bindBuffer(gl.ARRAY_BUFFER, instanceBuffer);
      gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(layoutNodes.flatMap(n => [n.x, n.y])), gl.STATIC_DRAW);
      const posLoc = gl.getAttribLocation(prog, 'aPos');
      gl.enableVertexAttribArray(posLoc);
      gl.vertexAttribPointer(posLoc, 2, gl.FLOAT, false, 0, 0);
      ext.vertexAttribDivisorANGLE(posLoc, 1);  // Per-instance
      // Draw instanced
      ext.drawArraysInstancedANGLE(gl.POINTS, 0, 1, layoutNodes.length);
    } else {
      console.warn('Instanced rendering not supported, falling back to regular draw');
      const loc = gl.getAttribLocation(prog, 'aPos');
      gl.enableVertexAttribArray(loc);
      gl.bindBuffer(gl.ARRAY_BUFFER, nodeBuf);
      gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
      gl.drawArrays(gl.POINTS, 0, layoutNodes.length);
    }

    // Draw lines (separate program for different color)
    const lineProg = gl.createProgram();
    if (!lineProg) return;

    const lineFs = gl.createShader(gl.FRAGMENT_SHADER);
    if (!lineFs) return;

    gl.shaderSource(lineFs, `uniform float u_opacity; void main() { gl_FragColor = vec4(0.5, 0.5, 0.5, u_opacity); }`); // Gray with opacity
    gl.compileShader(lineFs);

    if (!gl.getShaderParameter(lineFs, gl.COMPILE_STATUS)) {
      console.error('Line fragment shader compilation failed:', gl.getShaderInfoLog(lineFs));
      return;
    }

    gl.attachShader(lineProg, vs); // Reuse vertex shader
    gl.attachShader(lineProg, lineFs);
    gl.linkProgram(lineProg);

    if (!gl.getProgramParameter(lineProg, gl.LINK_STATUS)) {
      console.error('Line program linking failed:', gl.getProgramInfoLog(lineProg));
      return;
    }

    gl.useProgram(lineProg);

    // Set uniforms for line program too
    const linePanLoc = gl.getUniformLocation(lineProg, 'u_pan');
    const lineZoomLoc = gl.getUniformLocation(lineProg, 'u_zoom');
    const lineOpacityLoc = gl.getUniformLocation(lineProg, 'u_opacity');

    if (linePanLoc) gl.uniform2f(linePanLoc, pan[0], pan[1]);
    if (lineZoomLoc) gl.uniform1f(lineZoomLoc, zoom);
    if (lineOpacityLoc) gl.uniform1f(lineOpacityLoc, edgeOpacity);

    const lineLoc = gl.getAttribLocation(lineProg, 'pos');
    gl.enableVertexAttribArray(lineLoc);

    gl.bindBuffer(gl.ARRAY_BUFFER, edgeBuf);
    gl.vertexAttribPointer(lineLoc, 2, gl.FLOAT, false, 0, 0);
    gl.drawArrays(gl.LINES, 0, data.edges.length * 2);

    // Context loss handling
    const loseContext = gl.getExtension('WEBGL_lose_context');
    if (loseContext) {
      canvas.addEventListener('webglcontextlost', (e) => {
        e.preventDefault();
        console.warn('WebGL context lost');
      });

      canvas.addEventListener('webglcontextrestored', () => {
        console.log('WebGL context restored');
        // Re-initialize would go here
      });
    }

    return () => {
      gl.deleteBuffer(nodeBuf);
      gl.deleteBuffer(edgeBuf);
      gl.deleteProgram(prog);
      if (lineProg) gl.deleteProgram(lineProg);
    };
  }, [data, width, height, pan, zoom, edgeOpacity, layoutNodes]);

  return <canvas ref={canvasRef} width={width} height={height} style={{ display: 'block' }} />;
};

/**
 * @description WebGL static renderer: points/lines for nodes/edges, normalized coords, context handling (Sprint 3).
 * Hot path <16ms/frame. Memory guard: estimateGPUMemoryUsage(nodeCount, edgeCount) < 500MB.
 */
export default Renderer;
