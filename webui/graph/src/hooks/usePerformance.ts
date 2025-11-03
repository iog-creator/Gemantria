import { useState, useEffect, useRef, useCallback } from 'react';

export interface PerformanceMetrics {
  /** Time to first render in milliseconds */
  tti: number;
  /** Frames per second during interactions */
  fps: number;
  /** Memory usage in MB */
  memoryUsage?: number;
  /** Number of DOM nodes rendered */
  domNodes: number;
  /** Render time in milliseconds */
  renderTime: number;
  /** Timestamp of last measurement */
  timestamp: number;
}

export interface PerformanceConfig {
  /** Enable FPS monitoring */
  enableFPS?: boolean;
  /** Enable memory monitoring */
  enableMemory?: boolean;
  /** Enable DOM node counting */
  enableDOMCount?: boolean;
  /** Performance thresholds */
  thresholds?: {
    tti: number; // ms
    fps: number; // minimum FPS
    memory: number; // MB
    renderTime: number; // ms
  };
}

export interface PerformanceRecommendation {
  /** Recommendation type */
  type: 'webgl' | 'virtualization' | 'simplification' | 'optimization';
  /** Human-readable message */
  message: string;
  /** Priority level */
  priority: 'low' | 'medium' | 'high';
  /** Actionable steps */
  actions: string[];
}

const DEFAULT_CONFIG: PerformanceConfig = {
  enableFPS: true,
  enableMemory: false, // Disabled by default for privacy
  enableDOMCount: true,
  thresholds: {
    tti: 500, // 500ms TTI threshold
    fps: 30, // Minimum 30 FPS
    memory: 100, // 100MB memory threshold
    renderTime: 16, // 16ms for 60fps
  },
};

export function usePerformance(config: PerformanceConfig = {}) {
  const mergedConfig = { ...DEFAULT_CONFIG, ...config };
  const [metrics, setMetrics] = useState<PerformanceMetrics>({
    tti: 0,
    fps: 0,
    memoryUsage: undefined,
    domNodes: 0,
    renderTime: 0,
    timestamp: Date.now(),
  });

  const [recommendations, setRecommendations] = useState<PerformanceRecommendation[]>([]);

  // Refs for performance tracking
  const startTimeRef = useRef<number>(0);
  const fpsIntervalRef = useRef<number | null>(null);
  const containerRef = useRef<HTMLElement | null>(null);

  // Measure Time to Interactive (TTI)
  const measureTTI = useCallback(() => {
    if (startTimeRef.current === 0) {
      startTimeRef.current = performance.now();
    }
    const tti = performance.now() - startTimeRef.current;
    setMetrics(prev => ({ ...prev, tti, timestamp: Date.now() }));
  }, []);

  // Measure FPS during interactions
  const startFPSMonitoring = useCallback(() => {
    if (!mergedConfig.enableFPS || fpsIntervalRef.current) return;

    let frameCount = 0;
    let lastTime = performance.now();

    const measureFPS = () => {
      const now = performance.now();
      frameCount++;

      if (now - lastTime >= 1000) { // Update every second
        const fps = Math.round((frameCount * 1000) / (now - lastTime));
        setMetrics(prev => ({ ...prev, fps, timestamp: Date.now() }));
        frameCount = 0;
        lastTime = now;
      }

      fpsIntervalRef.current = requestAnimationFrame(measureFPS);
    };

    fpsIntervalRef.current = requestAnimationFrame(measureFPS);
  }, [mergedConfig.enableFPS]);

  // Measure render time
  const measureRenderTime = useCallback((startTime: number) => {
    const renderTime = performance.now() - startTime;
    setMetrics(prev => ({ ...prev, renderTime, timestamp: Date.now() }));
    return renderTime;
  }, []);

  // Count DOM nodes
  const countDOMNodes = useCallback(() => {
    if (!mergedConfig.enableDOMCount || !containerRef.current) return;

    const count = containerRef.current.querySelectorAll('*').length;
    setMetrics(prev => ({ ...prev, domNodes: count, timestamp: Date.now() }));
  }, [mergedConfig.enableDOMCount]);

  // Measure memory usage (if available and enabled)
  const measureMemory = useCallback(() => {
    if (!mergedConfig.enableMemory || !(performance as any).memory) return;

    const memoryMB = (performance as any).memory.usedJSHeapSize / (1024 * 1024);
    setMetrics(prev => ({
      ...prev,
      memoryUsage: Math.round(memoryMB),
      timestamp: Date.now()
    }));
  }, [mergedConfig.enableMemory]);

  // Generate performance recommendations
  const generateRecommendations = useCallback((currentMetrics: PerformanceMetrics) => {
    const recs: PerformanceRecommendation[] = [];
    const thresholds = mergedConfig.thresholds!;

    // TTI recommendations
    if (currentMetrics.tti > thresholds.tti) {
      recs.push({
        type: 'webgl',
        message: `Slow initial load (${currentMetrics.tti.toFixed(0)}ms TTI)`,
        priority: currentMetrics.tti > thresholds.tti * 2 ? 'high' : 'medium',
        actions: [
          'Consider enabling WebGL renderer for hardware acceleration',
          'Implement virtual scrolling for large datasets',
          'Use progressive loading for initial render'
        ]
      });
    }

    // FPS recommendations
    if (currentMetrics.fps > 0 && currentMetrics.fps < thresholds.fps) {
      recs.push({
        type: 'optimization',
        message: `Low FPS (${currentMetrics.fps}) during interactions`,
        priority: currentMetrics.fps < 15 ? 'high' : 'medium',
        actions: [
          'Enable viewport culling for large graphs',
          'Reduce node/edge detail in overview mode',
          'Implement level-of-detail rendering'
        ]
      });
    }

    // Memory recommendations
    if (currentMetrics.memoryUsage && currentMetrics.memoryUsage > thresholds.memory) {
      recs.push({
        type: 'virtualization',
        message: `High memory usage (${currentMetrics.memoryUsage}MB)`,
        priority: 'medium',
        actions: [
          'Implement virtual scrolling',
          'Use pagination for large datasets',
          'Clear cached data when not in use'
        ]
      });
    }

    // DOM node recommendations
    if (currentMetrics.domNodes > 10000) {
      recs.push({
        type: 'simplification',
        message: `High DOM node count (${currentMetrics.domNodes})`,
        priority: 'medium',
        actions: [
          'Use canvas/WebGL instead of SVG',
          'Implement virtualization for large lists',
          'Reduce visual complexity for overview mode'
        ]
      });
    }

    setRecommendations(recs);
  }, [mergedConfig.thresholds]);

  // Auto-generate recommendations when metrics change
  useEffect(() => {
    generateRecommendations(metrics);
  }, [metrics, generateRecommendations]);

  // Cleanup
  useEffect(() => {
    return () => {
      if (fpsIntervalRef.current) {
        cancelAnimationFrame(fpsIntervalRef.current);
      }
    };
  }, []);

  // Export hook API
  return {
    metrics,
    recommendations,
    measureTTI,
    startFPSMonitoring,
    measureRenderTime,
    countDOMNodes,
    measureMemory,
    setContainerRef: (ref: HTMLElement | null) => { containerRef.current = ref; },
    isSlow: metrics.tti > (mergedConfig.thresholds?.tti || 500),
    needsWebGL: recommendations.some(r => r.type === 'webgl' && r.priority === 'high'),
    needsVirtualization: recommendations.some(r => r.type === 'virtualization'),
  };
}
