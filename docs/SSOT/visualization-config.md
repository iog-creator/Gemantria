---
originating_ADR: ADR-015
canonical: true
version: 1.0
---

# SSOT: Visualization Configuration

## Overview

This document defines the configuration parameters and options for the graph visualization interface. This serves as the single source of truth for display settings, interaction behaviors, and customization options.

## Core Configuration Structure

### Default Configuration

```typescript
const DEFAULT_CONFIG = {
  // Layout settings
  layout: {
    algorithm: "force",
    width: 800,
    height: 600,
    centerAt: { x: 400, y: 300 },
  },

  // Node styling
  nodes: {
    radius: {
      min: 5,
      max: 25,
      scale: "degree",
    },
    colors: {
      palette: "categorical",
      count: 11,
      opacity: 1.0,
    },
    labels: {
      show: true,
      maxLength: 10,
      fontSize: 10,
      offset: -5,
    },
  },

  // Edge styling
  edges: {
    width: {
      min: 1,
      max: 5,
      scale: "strength",
    },
    colors: {
      default: "#999",
      opacity: {
        min: 0.1,
        max: 1.0,
      },
    },
    particles: {
      enabled: true,
      speed: 0.005,
      count: 2,
    },
  },

  // Interaction settings
  interaction: {
    selection: {
      enabled: true,
      multiSelect: false,
      highlightColor: "#000",
      hoverColor: "#666",
    },
    zoom: {
      enabled: true,
      minZoom: 0.1,
      maxZoom: 5.0,
      zoomSpeed: 0.1,
    },
    pan: {
      enabled: true,
      dragInertia: 0.3,
    },
  },

  // Force simulation
  simulation: {
    cooldownTicks: 100,
    alpha: {
      initial: 1.0,
      min: 0.001,
    },
    forces: {
      link: {
        distance: 100,
        strength: 0.1,
      },
      charge: {
        strength: -300,
        distanceMin: 10,
        distanceMax: 1000,
      },
      center: {
        strength: 0.1,
      },
    },
  },

  // Performance settings
  performance: {
    maxNodes: 10000,
    batchSize: 1000,
    throttleMs: 16,
  },
};
```

## Configuration Sections

### Layout Configuration

#### Algorithm Settings

- **`algorithm`**: Layout algorithm (`'force'` only currently supported)
- **`width`**: Canvas width in pixels (responsive)
- **`height`**: Canvas height in pixels (responsive)
- **`centerAt`**: Initial center point for force layout

#### Responsive Behavior

- **Auto-resize**: Adapts to container dimensions
- **Aspect ratio**: Maintains proportions on resize
- **Min dimensions**: 400x300 minimum viewport

### Node Configuration

#### Size Mapping

- **`radius.min/max`**: Pixel radius range for nodes
- **`radius.scale`**: Property to scale by (`'degree'`, `'betweenness'`, `'fixed'`)
- **Scaling formula**: `radius = min + (max - min) * normalized_value`

#### Color Mapping

- **`colors.palette`**: Color scheme (`'categorical'`, `'sequential'`, `'diverging'`)
- **`colors.count`**: Number of distinct colors (11 for categorical)
- **`colors.opacity`**: Base opacity for nodes (0.0-1.0)

#### Color Palette (Categorical)

```typescript
const CATEGORICAL_COLORS = [
  "#1f77b4", // Blue
  "#ff7f0e", // Orange
  "#2ca02c", // Green
  "#d62728", // Red
  "#9467bd", // Purple
  "#8c564b", // Brown
  "#e377c2", // Pink
  "#7f7f7f", // Gray
  "#bcbd22", // Olive
  "#17becf", // Cyan
  "#aec7e8", // Light blue
];
```

#### Label Configuration

- **`labels.show`**: Whether to display node labels
- **`labels.maxLength`**: Maximum characters before truncation
- **`labels.fontSize`**: Font size in pixels
- **`labels.offset`**: Vertical offset from node center

### Edge Configuration

#### Width Mapping

- **`width.min/max`**: Pixel width range for edges
- **`width.scale`**: Property to scale by (`'strength'`, `'fixed'`)
- **Scaling formula**: `width = min + (max - min) * value`

#### Visual Styling

- **`colors.default`**: Default edge color (hex)
- **`colors.opacity.min/max`**: Opacity range based on strength

#### Particle Effects

- **`particles.enabled`**: Show directional particles on edges
- **`particles.speed`**: Particle movement speed
- **`particles.count`**: Number of particles per edge

### Interaction Configuration

#### Selection Settings

- **`selection.enabled`**: Allow node selection
- **`selection.multiSelect`**: Allow multiple simultaneous selections
- **`selection.highlightColor`**: Color for selected nodes
- **`selection.hoverColor`**: Color for hovered nodes

#### Zoom Settings

- **`zoom.enabled`**: Allow zoom interactions
- **`zoom.minZoom`**: Minimum zoom level (0.1 = 10% zoom)
- **`zoom.maxZoom`**: Maximum zoom level (5.0 = 500% zoom)
- **`zoom.zoomSpeed`**: Zoom sensitivity

#### Pan Settings

- **`pan.enabled`**: Allow pan interactions
- **`pan.dragInertia`**: Momentum after drag release

### Simulation Configuration

#### General Settings

- **`cooldownTicks`**: Number of simulation iterations
- **`alpha.initial`**: Starting energy level (1.0 = high energy)
- **`alpha.min`**: Minimum energy threshold for stopping

#### Force Settings

##### Link Force (Edges)

- **`forces.link.distance`**: Target distance between connected nodes
- **`forces.link.strength`**: Strength of link constraints

##### Charge Force (Repulsion)

- **`forces.charge.strength`**: Repulsion strength (negative = repel)
- **`forces.charge.distanceMin`**: Minimum distance for charge calculation
- **`forces.charge.distanceMax`**: Maximum distance for charge calculation

##### Center Force

- **`forces.center.strength`**: Strength of centering force

### Performance Configuration

#### Limits

- **`maxNodes`**: Maximum nodes before showing performance warning
- **`batchSize`**: Nodes processed per batch during rendering
- **`throttleMs`**: Minimum milliseconds between updates

#### Optimization Strategies

- **Level of detail**: Reduce detail at high zoom levels
- **Culling**: Hide nodes outside viewport
- **Batching**: Process updates in chunks

## Configuration Overrides

### Environment Variables

```bash
# Node scaling
VISUALIZATION_NODE_SCALE=degree  # degree, betweenness, eigenvector, fixed

# Color scheme
VISUALIZATION_COLOR_PALETTE=categorical  # categorical, sequential, diverging

# Performance tuning
VISUALIZATION_MAX_NODES=5000
VISUALIZATION_BATCH_SIZE=500
```

### URL Parameters

```
/?scale=betweenness&palette=sequential&maxNodes=2000
```

### Runtime Configuration

```typescript
// Override defaults at runtime
const customConfig = {
  ...DEFAULT_CONFIG,
  nodes: {
    ...DEFAULT_CONFIG.nodes,
    radius: { min: 3, max: 15, scale: "betweenness" },
  },
};
```

## Responsive Design

### Breakpoint Configuration

```typescript
const RESPONSIVE_BREAKPOINTS = {
  mobile: { width: 640, height: 400 },
  tablet: { width: 768, height: 500 },
  desktop: { width: 1024, height: 600 },
  large: { width: 1280, height: 720 },
};
```

### Adaptive Behavior

- **Mobile**: Reduced node sizes, simplified interactions
- **Tablet**: Medium fidelity, touch-optimized
- **Desktop**: Full fidelity, mouse and keyboard support

## Accessibility Configuration

### Keyboard Navigation

- **Tab order**: Logical navigation between interactive elements
- **Enter/Space**: Activate node selection
- **Arrow keys**: Navigate between nodes
- **Escape**: Clear selection

### Screen Reader Support

- **ARIA labels**: Descriptive labels for interactive elements
- **Live regions**: Announce dynamic content changes
- **Focus indicators**: Visible focus outlines

### High Contrast Mode

- **Color overrides**: High contrast color palette
- **Stroke weights**: Thicker lines for visibility
- **Font sizes**: Larger, more readable fonts

## Theming and Customization

### Theme Structure

```typescript
interface Theme {
  colors: {
    background: string;
    node: {
      default: string;
      selected: string;
      hovered: string;
    };
    edge: {
      default: string;
      strong: string;
      weak: string;
    };
    text: string;
  };
  fonts: {
    nodeLabel: string;
    ui: string;
  };
  spacing: {
    nodeLabelOffset: number;
    uiPadding: number;
  };
}
```

### Built-in Themes

- **Light**: Clean, professional appearance
- **Dark**: Low-light optimized
- **High Contrast**: Accessibility focused
- **Print**: Optimized for printing/export

## Export and Serialization

### Configuration Export

```typescript
function exportConfig(config: VisualizationConfig): string {
  return JSON.stringify(config, null, 2);
}
```

### Configuration Import

```typescript
function importConfig(jsonString: string): VisualizationConfig {
  const parsed = JSON.parse(jsonString);
  return { ...DEFAULT_CONFIG, ...parsed };
}
```

## Validation and Constraints

### Configuration Validation

```typescript
function validateConfig(config: VisualizationConfig): ValidationResult {
  const errors: string[] = [];

  // Required fields
  if (!config.layout) errors.push("Layout configuration required");

  // Value ranges
  if (config.nodes.radius.min < 1) errors.push("Node radius min must be >= 1");
  if (config.nodes.radius.max > 100)
    errors.push("Node radius max must be <= 100");

  // Logical constraints
  if (config.nodes.radius.min > config.nodes.radius.max) {
    errors.push("Node radius min cannot exceed max");
  }

  return { valid: errors.length === 0, errors };
}
```

### Safe Fallbacks

- **Invalid values**: Fall back to defaults
- **Missing properties**: Merge with defaults
- **Type mismatches**: Attempt conversion or use defaults

## Performance Tuning

### Adaptive Quality

```typescript
function getAdaptiveQuality(nodeCount: number): QualityLevel {
  if (nodeCount < 100) return "high";
  if (nodeCount < 1000) return "medium";
  if (nodeCount < 5000) return "low";
  return "minimal";
}
```

### Quality Levels

- **High**: Full detail, all effects enabled
- **Medium**: Reduced particles, simplified rendering
- **Low**: Basic rendering, essential features only
- **Minimal**: Wireframe mode, maximum performance

## Future Extensions

### Planned Features

- **Custom layouts**: Alternative algorithms (hierarchical, circular)
- **Advanced styling**: Gradients, textures, animations
- **Collaboration**: Shared views, annotations
- **Export formats**: PNG, SVG, PDF export options

### Configuration Extensions

- **User preferences**: Persistent customization
- **Presets**: Named configuration profiles
- **Sharing**: Export/import configuration files

## Related Documentation

- **ADR-015**: JSON-LD & Visualization implementation details
- **WebUI Contract**: Data consumption specification (webui-contract.md)
- **JSON-LD Schema**: Data format specification (jsonld-schema.md)
