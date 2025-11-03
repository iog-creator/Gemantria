/**
 * Phase 3: UI Beautification Theme
 * Centralized design tokens for colors, typography, spacing, and animations
 * No duplicates, scoped JSX integration, robust scaling
 */

export interface ThemeTokens {
  colors: {
    primary: string;
    secondary: string;
    accent: string;
    background: string;
    surface: string;
    text: {
      primary: string;
      secondary: string;
      muted: string;
    };
    clusters: string[];
    gradients: {
      dashboard: string;
      card: string;
    };
    status: {
      success: string;
      warning: string;
      error: string;
      info: string;
    };
  };
  typography: {
    fontFamily: string;
    fontSize: {
      xs: string;
      sm: string;
      base: string;
      lg: string;
      xl: string;
      '2xl': string;
    };
    fontWeight: {
      normal: string;
      medium: string;
      semibold: string;
      bold: string;
    };
    lineHeight: {
      tight: string;
      normal: string;
      relaxed: string;
    };
  };
  spacing: {
    xs: string;
    sm: string;
    md: string;
    lg: string;
    xl: string;
    '2xl': string;
  };
  borderRadius: {
    none: string;
    sm: string;
    md: string;
    lg: string;
    full: string;
  };
  shadows: {
    sm: string;
    md: string;
    lg: string;
    xl: string;
  };
  animations: {
    duration: {
      fast: string;
      normal: string;
      slow: string;
    };
    easing: {
      ease: string;
      easeIn: string;
      easeOut: string;
      easeInOut: string;
    };
  };
  breakpoints: {
    sm: string;
    md: string;
    lg: string;
    xl: string;
  };
}

/**
 * Pastel color palette for clusters (11 colors, no duplicates)
 */
const clusterColors = [
  '#8dd3c7', // teal
  '#ffffb3', // light yellow
  '#bebada', // lavender
  '#fb8072', // coral
  '#80b1d3', // light blue
  '#fdb462', // orange
  '#b3de69', // light green
  '#fccde5', // pink
  '#d9d9d9', // gray
  '#bc80bd', // purple
  '#ccebc5', // mint
];

/**
 * Main theme tokens - soft blues/grays/gold palette
 */
export const theme: ThemeTokens = {
  colors: {
    primary: '#2563eb', // blue-600
    secondary: '#64748b', // slate-500
    accent: '#f59e0b', // amber-500 (gold)
    background: '#f8fafc', // slate-50
    surface: '#ffffff', // white
    text: {
      primary: '#1e293b', // slate-800
      secondary: '#475569', // slate-600
      muted: '#64748b', // slate-500
    },
    clusters: clusterColors,
    gradients: {
      dashboard: 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)',
      card: 'linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)',
    },
    status: {
      success: '#10b981', // emerald-500
      warning: '#f59e0b', // amber-500
      error: '#ef4444', // red-500
      info: '#3b82f6', // blue-500
    },
  },
  typography: {
    fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    fontSize: {
      xs: '0.75rem',
      sm: '0.875rem',
      base: '1rem',
      lg: '1.125rem',
      xl: '1.25rem',
      '2xl': '1.5rem',
    },
    fontWeight: {
      normal: '400',
      medium: '500',
      semibold: '600',
      bold: '700',
    },
    lineHeight: {
      tight: '1.25',
      normal: '1.5',
      relaxed: '1.75',
    },
  },
  spacing: {
    xs: '0.25rem',
    sm: '0.5rem',
    md: '1rem',
    lg: '1.5rem',
    xl: '2rem',
    '2xl': '3rem',
  },
  borderRadius: {
    none: '0',
    sm: '0.25rem',
    md: '0.375rem',
    lg: '0.5rem',
    full: '9999px',
  },
  shadows: {
    sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
    md: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
    lg: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
    xl: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
  },
  animations: {
    duration: {
      fast: '150ms',
      normal: '200ms',
      slow: '300ms',
    },
    easing: {
      ease: 'cubic-bezier(0.4, 0, 0.2, 1)',
      easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
      easeOut: 'cubic-bezier(0, 0, 0.2, 1)',
      easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
    },
  },
  breakpoints: {
    sm: '640px',
    md: '768px',
    lg: '1024px',
    xl: '1280px',
  },
};

/**
 * Utility functions for theme usage
 */
export const getClusterColor = (index: number): string => {
  return theme.colors.clusters[index % theme.colors.clusters.length];
};

export const getStatusColor = (status: 'success' | 'warning' | 'error' | 'info'): string => {
  return theme.colors.status[status];
};

/**
 * CSS custom properties for runtime theme application
 */
export const themeCSSVariables = {
  '--color-primary': theme.colors.primary,
  '--color-secondary': theme.colors.secondary,
  '--color-accent': theme.colors.accent,
  '--color-background': theme.colors.background,
  '--color-surface': theme.colors.surface,
  '--color-text-primary': theme.colors.text.primary,
  '--color-text-secondary': theme.colors.text.secondary,
  '--color-text-muted': theme.colors.text.muted,
  '--font-family': theme.typography.fontFamily,
  '--animation-duration-normal': theme.animations.duration.normal,
  '--animation-easing': theme.animations.easing.ease,
  '--shadow-md': theme.shadows.md,
  '--border-radius-md': theme.borderRadius.md,
  '--spacing-md': theme.spacing.md,
} as const;
