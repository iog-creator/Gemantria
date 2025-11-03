import React from 'react';
import { usePerformance } from '../hooks/usePerformance';
import { theme } from '../styles/theme';

/**
 * Phase 4: Performance Badge
 * Visual indicator showing current performance status
 * Color-coded with hover tooltip and click to open debug panel
 */
interface PerformanceBadgeProps {
  /** Click handler to open debug panel */
  onClick?: () => void;
  /** Show detailed metrics in badge */
  showDetails?: boolean;
  /** Custom size */
  size?: 'sm' | 'md' | 'lg';
}

const PerformanceBadge: React.FC<PerformanceBadgeProps> = ({
  onClick,
  showDetails = true,
  size = 'md'
}) => {
  const { metrics, recommendations, isSlow, needsWebGL } = usePerformance();

  // Determine overall status
  const getOverallStatus = (): { status: 'good' | 'warning' | 'error'; icon: string; message: string } => {
    // Priority: errors > warnings > recommendations
    if (isSlow || needsWebGL) {
      return {
        status: 'error',
        icon: '❌',
        message: 'Performance issues detected'
      };
    }

    const highPriorityRecs = recommendations.filter(r => r.priority === 'high');
    if (highPriorityRecs.length > 0) {
      return {
        status: 'error',
        icon: '🔴',
        message: `${highPriorityRecs.length} critical issue${highPriorityRecs.length > 1 ? 's' : ''}`
      };
    }

    const mediumPriorityRecs = recommendations.filter(r => r.priority === 'medium');
    if (mediumPriorityRecs.length > 0) {
      return {
        status: 'warning',
        icon: '🟡',
        message: `${mediumPriorityRecs.length} performance warning${mediumPriorityRecs.length > 1 ? 's' : ''}`
      };
    }

    // Check key metrics
    if (metrics.tti > 1000 || metrics.fps < 30 || (metrics.memoryUsage && metrics.memoryUsage > 150)) {
      return {
        status: 'warning',
        icon: '⚠️',
        message: 'Performance degradation'
      };
    }

    return {
      status: 'good',
      icon: '✅',
      message: 'Performance optimal'
    };
  };

  const overallStatus = getOverallStatus();
  const statusColor = {
    good: theme.colors.status.success,
    warning: theme.colors.status.warning,
    error: theme.colors.status.error,
  }[overallStatus.status];

  const sizeClasses = {
    sm: 'px-2 py-1 text-xs',
    md: 'px-3 py-1.5 text-sm',
    lg: 'px-4 py-2 text-base'
  };

  return (
    <button
      onClick={onClick}
      className={`inline-flex items-center gap-2 rounded-full font-medium transition-all hover:scale-105 focus:outline-none focus:ring-2 focus:ring-offset-2 ${sizeClasses[size]} ${
        onClick ? 'cursor-pointer' : 'cursor-default'
      }`}
      style={{
        backgroundColor: `${statusColor}15`, // 15% opacity
        border: `1px solid ${statusColor}30`, // 30% opacity
        color: statusColor,
        transition: `all ${theme.animations.duration.fast} ${theme.animations.easing.ease}`,
        boxShadow: overallStatus.status === 'error' ? theme.shadows.md : 'none'
      }}
      title={overallStatus.message}
      aria-label={`Performance status: ${overallStatus.message}`}
      role={onClick ? 'button' : 'status'}
    >
      <span className="text-lg leading-none">{overallStatus.icon}</span>

      {showDetails && (
        <>
          <span>Perf</span>

          {/* Key metrics summary */}
          <div className="flex items-center gap-1 text-xs opacity-75">
            <span>{metrics.tti.toFixed(0)}ms</span>
            <span>•</span>
            <span>{metrics.fps.toFixed(0)} FPS</span>
            {metrics.memoryUsage && (
              <>
                <span>•</span>
                <span>{metrics.memoryUsage}MB</span>
              </>
            )}
          </div>

          {/* Issue count badge */}
          {recommendations.length > 0 && (
            <span
              className="bg-white bg-opacity-80 text-xs px-1.5 py-0.5 rounded-full font-bold"
              style={{ color: statusColor }}
            >
              {recommendations.length}
            </span>
          )}
        </>
      )}
    </button>
  );
};

export default PerformanceBadge;
