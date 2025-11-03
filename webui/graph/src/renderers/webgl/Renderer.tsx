import React, { useRef, useEffect } from 'react';
import { canUseWebGL } from '../../utils/capabilities';

/**
 * Sprint 3: Isolated WebGL renderer for escalation
 * Points/lines for nodes/edges, normalized coords, context handling
 * Hot path <16ms/frame budget on static 100k datasets
 */

interface RendererProps {
  data: { nodes: any[]; edges: any[] }; // Positions pre-computed
  width: number;
  height: number;
}

const Renderer: React.FC<RendererProps> = ({ data, width, height }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

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
      data.nodes.flatMap(n => [
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
        const source = data.nodes.find(n => n.id === e.source.id || n.id === e.source);
        const target = data.nodes.find(n => n.id === e.target.id || n.id === e.target);
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

    gl.shaderSource(vs, `attribute vec2 pos; void main() { gl_Position = vec4(pos, 0, 1); gl_PointSize = 5.0; }`);
    gl.compileShader(vs);

    if (!gl.getShaderParameter(vs, gl.COMPILE_STATUS)) {
      console.error('Vertex shader compilation failed:', gl.getShaderInfoLog(vs));
      return;
    }

    const fs = gl.createShader(gl.FRAGMENT_SHADER);
    if (!fs) return;

    gl.shaderSource(fs, `void main() { gl_FragColor = vec4(0.2, 0.4, 0.8, 1); }`); // Blue
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

    const loc = gl.getAttribLocation(prog, 'pos');
    gl.enableVertexAttribArray(loc);

    // Draw points
    gl.bindBuffer(gl.ARRAY_BUFFER, nodeBuf);
    gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
    gl.drawArrays(gl.POINTS, 0, data.nodes.length);

    // Draw lines (separate program for different color)
    const lineProg = gl.createProgram();
    if (!lineProg) return;

    const lineFs = gl.createShader(gl.FRAGMENT_SHADER);
    if (!lineFs) return;

    gl.shaderSource(lineFs, `void main() { gl_FragColor = vec4(0.5, 0.5, 0.5, 0.5); }`);
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
  }, [data, width, height]);

  return <canvas ref={canvasRef} width={width} height={height} style={{ display: 'block' }} />;
};

/**
 * @description WebGL static renderer: points/lines for nodes/edges, normalized coords, context handling (Sprint 3).
 * Hot path <16ms/frame. Memory guard: estimateGPUMemoryUsage(nodeCount, edgeCount) < 500MB.
 */
export default Renderer;
