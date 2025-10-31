import { useEffect, useState } from "react";

// Types for stats data
interface GraphStats {
  nodes: number;
  edges: number;
  clusters: number;
  density: number;
  centrality: {
    avg_degree: number;
    max_degree: number;
    avg_betweenness: number;
    max_betweenness: number;
    avg_eigenvector: number;
    max_eigenvector: number;
  };
  cluster_metrics: {
    avg_cluster_density: number | null;
    avg_cluster_diversity: number | null;
  };
  health: {
    has_nodes: boolean;
    has_edges: boolean;
    has_clusters: boolean;
    density_reasonable: boolean;
  };
}

interface CorrelationStats {
  metadata: {
    total_correlations: number;
    significant_correlations: number;
    correlation_methods: string[];
  };
}

interface CombinedStats {
  graph: GraphStats;
  correlations: CorrelationStats;
  patterns: {
    metadata: {
      total_patterns: number;
      analyzed_books: string[];
    };
  };
}

export default function MetricsPanel() {
  const [stats, setStats] = useState<GraphStats | null>(null);
  const [correlations, setCorrelations] = useState<CorrelationStats | null>(
    null,
  );
  const [patterns, setPatterns] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [statsRes, corrRes, patternsRes] = await Promise.all([
        fetch("/api/v1/stats"),
        fetch("/api/v1/correlations?limit=1"), // Just get metadata
        fetch("/api/v1/patterns?limit=1"), // Just get metadata
      ]);

      if (statsRes.ok) {
        const statsData = await statsRes.json();
        setStats(statsData);
      }

      if (corrRes.ok) {
        const corrData = await corrRes.json();
        setCorrelations(corrData);
      }

      if (patternsRes.ok) {
        const patternsData = await patternsRes.json();
        setPatterns(patternsData);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-48 mb-4"></div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[...Array(8)].map((_, i) => (
              <div key={i} className="h-24 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="text-red-600">
          <h3 className="text-lg font-semibold mb-2">Error Loading Metrics</h3>
          <p>{error}</p>
          <button
            onClick={fetchData}
            className="mt-2 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  // Mock sparkline data (in a real implementation, this would come from historical data)
  const generateSparkline = (baseValue: number, variance: number = 0.1) => {
    return Array.from({ length: 20 }, () => {
      const variation = (Math.random() - 0.5) * variance * baseValue;
      return Math.max(0, baseValue + variation);
    });
  };

  const Sparkline = ({
    data,
    color = "blue",
  }: {
    data: number[];
    color?: string;
  }) => {
    const width = 80;
    const height = 20;
    const max = Math.max(...data);
    const min = Math.min(...data);

    const points = data
      .map((value, index) => {
        const x = (index / (data.length - 1)) * width;
        const y = height - ((value - min) / (max - min)) * height;
        return `${x},${y}`;
      })
      .join(" ");

    return (
      <svg width={width} height={height} className="ml-2">
        <polyline
          fill="none"
          stroke={`rgb(59 130 246)`}
          strokeWidth="1.5"
          points={points}
        />
      </svg>
    );
  };

  const MetricCard = ({
    title,
    value,
    subtitle,
    trend,
    sparklineData,
  }: {
    title: string;
    value: string | number;
    subtitle?: string;
    trend?: "up" | "down" | "neutral";
    sparklineData?: number[];
  }) => (
    <div className="bg-white rounded-lg shadow p-4">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-medium text-gray-600">{title}</h3>
        {sparklineData && <Sparkline data={sparklineData} />}
      </div>
      <div className="text-2xl font-bold mb-1">{value}</div>
      {subtitle && <div className="text-sm text-gray-500">{subtitle}</div>}
      {trend && (
        <div
          className={`text-sm ${trend === "up" ? "text-green-600" : trend === "down" ? "text-red-600" : "text-gray-600"}`}
        >
          {trend === "up" ? "↗" : trend === "down" ? "↘" : "→"} Trending
        </div>
      )}
    </div>
  );

  return (
    <div className="p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold mb-2">Analytics Dashboard</h2>
        <p className="text-gray-600">
          Real-time metrics from semantic network analysis
        </p>
      </div>

      {/* Primary Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <MetricCard
          title="Network Nodes"
          value={stats?.nodes ?? 0}
          subtitle="Total concepts"
          sparklineData={
            stats?.nodes ? generateSparkline(stats.nodes, 0.05) : undefined
          }
        />
        <MetricCard
          title="Network Edges"
          value={stats?.edges ?? 0}
          subtitle="Semantic relationships"
          sparklineData={
            stats?.edges ? generateSparkline(stats.edges, 0.1) : undefined
          }
        />
        <MetricCard
          title="Clusters"
          value={stats?.clusters ?? 0}
          subtitle="Community groups"
          sparklineData={
            stats?.clusters
              ? generateSparkline(stats.clusters, 0.02)
              : undefined
          }
        />
        <MetricCard
          title="Network Density"
          value={stats?.density ? `${(stats.density * 100).toFixed(2)}%` : "0%"}
          subtitle="Connection density"
          trend={stats?.density && stats.density > 0.001 ? "up" : "neutral"}
        />
      </div>

      {/* Centrality Metrics */}
      <div className="mb-8">
        <h3 className="text-lg font-semibold mb-4">Network Centrality</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <MetricCard
            title="Avg Degree"
            value={
              stats?.centrality?.avg_degree
                ? stats.centrality.avg_degree.toFixed(2)
                : "0.00"
            }
            subtitle="Average connections per node"
          />
          <MetricCard
            title="Avg Betweenness"
            value={
              stats?.centrality?.avg_betweenness
                ? stats.centrality.avg_betweenness.toFixed(4)
                : "0.0000"
            }
            subtitle="Bridge node centrality"
          />
          <MetricCard
            title="Avg Eigenvector"
            value={
              stats?.centrality?.avg_eigenvector
                ? stats.centrality.avg_eigenvector.toFixed(4)
                : "0.0000"
            }
            subtitle="Influence centrality"
          />
        </div>
      </div>

      {/* Cluster Metrics */}
      <div className="mb-8">
        <h3 className="text-lg font-semibold mb-4">Cluster Analysis</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <MetricCard
            title="Avg Cluster Density"
            value={
              stats?.cluster_metrics?.avg_cluster_density
                ? stats.cluster_metrics.avg_cluster_density.toFixed(3)
                : "N/A"
            }
            subtitle="Internal cluster connectivity"
          />
          <MetricCard
            title="Avg Cluster Diversity"
            value={
              stats?.cluster_metrics?.avg_cluster_diversity
                ? stats.cluster_metrics.avg_cluster_diversity.toFixed(3)
                : "N/A"
            }
            subtitle="Cluster content variety"
          />
        </div>
      </div>

      {/* Correlation & Pattern Metrics */}
      <div className="mb-8">
        <h3 className="text-lg font-semibold mb-4">Advanced Analytics</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <MetricCard
            title="Total Correlations"
            value={correlations?.metadata?.total_correlations ?? 0}
            subtitle="Concept relationships analyzed"
            sparklineData={
              correlations?.metadata?.total_correlations
                ? generateSparkline(
                    correlations.metadata.total_correlations,
                    0.1,
                  )
                : undefined
            }
          />
          <MetricCard
            title="Significant Correlations"
            value={correlations?.metadata?.significant_correlations ?? 0}
            subtitle="Statistically significant (p<0.05)"
            trend="up"
          />
          <MetricCard
            title="Cross-Book Patterns"
            value={patterns?.metadata?.total_patterns ?? 0}
            subtitle={`Across ${patterns?.metadata?.analyzed_books?.length ?? 0} books`}
            sparklineData={
              patterns?.metadata?.total_patterns
                ? generateSparkline(patterns.metadata.total_patterns, 0.05)
                : undefined
            }
          />
        </div>
      </div>

      {/* Health Status */}
      <div className="mb-8">
        <h3 className="text-lg font-semibold mb-4">System Health</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div
            className={`p-4 rounded-lg ${stats?.health?.has_nodes ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}`}
          >
            <div className="font-medium">Nodes</div>
            <div className="text-sm">
              {stats?.health?.has_nodes ? "✅ Available" : "❌ Missing"}
            </div>
          </div>
          <div
            className={`p-4 rounded-lg ${stats?.health?.has_edges ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}`}
          >
            <div className="font-medium">Edges</div>
            <div className="text-sm">
              {stats?.health?.has_edges ? "✅ Available" : "❌ Missing"}
            </div>
          </div>
          <div
            className={`p-4 rounded-lg ${stats?.health?.has_clusters ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}`}
          >
            <div className="font-medium">Clusters</div>
            <div className="text-sm">
              {stats?.health?.has_clusters ? "✅ Available" : "❌ Missing"}
            </div>
          </div>
          <div
            className={`p-4 rounded-lg ${stats?.health?.density_reasonable ? "bg-green-100 text-green-800" : "bg-yellow-100 text-yellow-800"}`}
          >
            <div className="font-medium">Density</div>
            <div className="text-sm">
              {stats?.health?.density_reasonable ? "✅ Reasonable" : "⚠️ Check"}
            </div>
          </div>
        </div>
      </div>

      {/* Correlation Methods */}
      {correlations?.metadata?.correlation_methods &&
        correlations.metadata.correlation_methods.length > 0 && (
          <div className="mb-8">
            <h3 className="text-lg font-semibold mb-4">
              Correlation Methods Used
            </h3>
            <div className="flex flex-wrap gap-2">
              {correlations.metadata.correlation_methods.map(
                (method, index) => (
                  <span
                    key={index}
                    className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
                  >
                    {method}
                  </span>
                ),
              )}
            </div>
          </div>
        )}

      {/* Refresh Button */}
      <div className="text-center">
        <button
          onClick={fetchData}
          className="px-6 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
        >
          Refresh Metrics
        </button>
      </div>
    </div>
  );
}
