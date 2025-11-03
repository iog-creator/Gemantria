/**
 * WebGL Capability Detection
 * Guards against unsupported environments and context loss
 */

export const canUseWebGL = (): boolean => {
  try {
    const canvas = document.createElement('canvas');
    const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
    if (!gl) return false;

    // Check for basic WebGL support
    const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
    if (!debugInfo) return false;

    // Check for required extensions (can be expanded)
    const requiredExtensions = [
      'OES_vertex_array_object',
      'WEBGL_lose_context' // For context loss handling
    ];

    for (const ext of requiredExtensions) {
      if (!gl.getExtension(ext)) {
        console.warn(`WebGL extension ${ext} not supported`);
        return false;
      }
    }

    // Clean up
    gl.getExtension('WEBGL_lose_context')?.loseContext();

    return true;
  } catch (e) {
    console.warn('WebGL not supported:', e);
    return false;
  }
};

/**
 * Memory usage estimation for WebGL escalation decisions
 */
export const estimateGPUMemoryUsage = (nodeCount: number, edgeCount: number): number => {
  // Rough estimation: nodes (position + color + size) + edges (indices)
  const nodeBytes = nodeCount * (2 * 4 + 4 * 4 + 1 * 4); // pos(vec2) + color(vec4) + size(float)
  const edgeBytes = edgeCount * (2 * 4); // indices (2 uint per edge)
  return (nodeBytes + edgeBytes) / (1024 * 1024); // MB
};
