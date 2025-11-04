#!/usr/bin/env python3
"""
Export quick graph statistics for dashboard consumption.

Provides aggregated metrics about the semantic concept network for UI cards
and monitoring dashboards, focusing on key insights and health indicators.
"""

import os

import numpy as np
import pandas as pd
from src.graph.patterns import build_graph, compute_patterns
from src.infra.db import get_gematria_rw
from src.infra.env_loader import ensure_env_loaded
from src.infra.structured_logger import get_logger, log_json

# Load environment variables from .env file
ensure_env_loaded()

LOG = get_logger("export_stats")


def calculate_graph_stats(db):
    """Calculate comprehensive graph statistics."""

    stats = {}

    # Basic counts (handle missing tables gracefully for CI empty DB)
    try:
        node_result = list(db.execute("SELECT COUNT(*) FROM concept_network"))
        stats["nodes"] = node_result[0][0] if node_result else 0
    except Exception:
        stats["nodes"] = 0  # Table doesn't exist in empty CI DB

    try:
        edge_result = list(db.execute("SELECT COUNT(*) FROM concept_relations"))
        stats["edges"] = edge_result[0][0] if edge_result else 0
    except Exception:
        stats["edges"] = 0  # Table doesn't exist in empty CI DB

    # Cluster statistics
    try:
        cluster_result = list(db.execute("SELECT COUNT(DISTINCT cluster_id) FROM concept_clusters"))
        stats["clusters"] = cluster_result[0][0] if cluster_result else 0
    except Exception:
        stats["clusters"] = 0  # Table doesn't exist in empty CI DB

    # Centrality averages (DB) with optional NetworkX fallback
    try:
        centrality_stats = list(
            db.execute(
                """
                SELECT
                    COALESCE(AVG(degree), 0) as avg_degree,
                    COALESCE(MAX(degree), 0) as max_degree,
                    COALESCE(AVG(betweenness), 0) as avg_betweenness,
                    COALESCE(MAX(betweenness), 0) as max_betweenness,
                    COALESCE(AVG(eigenvector), 0) as avg_eigenvector,
                    COALESCE(MAX(eigenvector), 0) as max_eigenvector
                FROM concept_centrality
                """
            )
        )
    except Exception:
        centrality_stats = [(0, 0, 0, 0, 0, 0)]  # Table doesn't exist in empty CI DB

    def _centrality_from_db_row(row):
        return {
            "avg_degree": float(row[0]),
            "max_degree": float(row[1]),
            "avg_betweenness": float(row[2]),
            "max_betweenness": float(row[3]),
            "avg_eigenvector": float(row[4]),
            "max_eigenvector": float(row[5]),
        }

    stats["centrality"] = (
        _centrality_from_db_row(centrality_stats[0])
        if centrality_stats
        else {
            "avg_degree": 0.0,
            "max_degree": 0.0,
            "avg_betweenness": 0.0,
            "max_betweenness": 0.0,
            "avg_eigenvector": 0.0,
            "max_eigenvector": 0.0,
        }
    )

    # Compute and persist centrality if missing from database
    centrality_missing = not centrality_stats or all(
        row[0] == 0 and row[1] == 0 and row[2] == 0 and row[3] == 0 and row[4] == 0 and row[5] == 0
        for row in centrality_stats
    )

    if centrality_missing:
        try:
            # Build graph and compute centrality
            G = build_graph(db)
            if G.number_of_nodes() > 0:
                _cluster_map, degree, betw, eigen = compute_patterns(G)

                # Persist centrality to database
                centrality_insert_count = 0
                for node in G.nodes():
                    try:
                        db.execute(
                            """
                            INSERT INTO concept_centrality (
                                concept_id, degree, betweenness, eigenvector
                            )
                            VALUES (%s, %s, %s, %s)
                            ON CONFLICT (concept_id) DO UPDATE SET
                                degree = EXCLUDED.degree,
                                betweenness = EXCLUDED.betweenness,
                                eigenvector = EXCLUDED.eigenvector
                            """,
                            (
                                node,
                                degree.get(node, 0),
                                betw.get(node, 0),
                                eigen.get(node, 0),
                            ),
                        )
                        centrality_insert_count += 1
                    except Exception as e:
                        log_json(
                            LOG,
                            40,
                            "centrality_persist_failed",
                            node=node[:8],
                            error=str(e),
                        )

                # Re-query centrality stats after persistence
                centrality_stats = list(
                    db.execute(
                        """
                        SELECT
                            COALESCE(AVG(degree), 0) as avg_degree,
                            COALESCE(MAX(degree), 0) as max_degree,
                            COALESCE(AVG(betweenness), 0) as avg_betweenness,
                            COALESCE(MAX(betweenness), 0) as max_betweenness,
                            COALESCE(AVG(eigenvector), 0) as avg_eigenvector,
                            COALESCE(MAX(eigenvector), 0) as max_eigenvector
                        FROM concept_centrality
                        """
                    )
                )

                log_json(
                    LOG,
                    20,
                    "centrality_computed_and_persisted",
                    nodes_computed=G.number_of_nodes(),
                    centrality_inserts=centrality_insert_count,
                    stats_reloaded=bool(centrality_stats),
                )

        except Exception as e:
            log_json(
                LOG,
                30,
                "centrality_computation_failed",
                error=str(e),
                falling_back_to_zeros=True,
            )
            centrality_stats = None

    # Optional NetworkX fallback if DB table is empty or zeros (legacy behavior)
    use_fallback = os.getenv("STATS_CENTRALITY_FALLBACK", "0").lower() in (
        "1",
        "true",
        "yes",
    )
    if use_fallback:
        try:
            import networkx as nx  # noqa: E402

            # consider "cosine" as edge weight if present
            rows = list(db.execute("SELECT source_id, target_id, COALESCE(cosine, 0.0) FROM concept_relations"))  # noqa: E501
            if rows:
                G = nx.Graph()
                for s, t, w in rows:
                    G.add_edge(s, t, weight=float(w))
                # Degree centrality (normalized to 0-1)
                degrees = dict(G.degree())
                max_possible_degree = len(G.nodes()) - 1
                degree_centrality = (
                    {n: d / max_possible_degree for n, d in degrees.items()} if max_possible_degree > 0 else {}  # noqa: E501
                )

                # Betweenness (weighted by inverse similarity to prefer stronger ties)
                inv_weights = {
                    (u, v): (1.0 - max(0.0, min(1.0, d.get("weight", 0.0)))) + 1e-6
                    for u, v, d in G.edges(data=True)  # noqa: E501
                }
                nx.set_edge_attributes(G, inv_weights, name="invw")
                bet = nx.betweenness_centrality(G, weight="invw", normalized=True) if G.number_of_edges() else {}

                # Eigenvector centrality (use weight, already normalized)
                try:
                    eig = nx.eigenvector_centrality_numpy(G, weight="weight") if G.number_of_edges() else {}
                except Exception:
                    eig = {}

                def _avg(d):
                    return float(sum(d.values()) / len(d)) if d else 0.0

                stats["centrality"] = {
                    "avg_degree": _avg(degree_centrality),
                    "max_degree": (float(max(degree_centrality.values())) if degree_centrality else 0.0),
                    "avg_betweenness": _avg(bet),
                    "max_betweenness": float(max(bet.values())) if bet else 0.0,
                    "avg_eigenvector": _avg(eig),
                    "max_eigenvector": float(max(eig.values())) if eig else 0.0,
                }
                log_json(
                    LOG,
                    20,
                    "centrality_fallback_networkx_applied",
                    node_count=G.number_of_nodes(),
                    edge_count=G.number_of_edges(),
                )
        except ImportError:
            log_json(
                LOG,
                20,
                "centrality_fallback_networkx_skipped",
                reason="networkx_not_installed",
            )

    # Edge strength distribution
    edge_distribution = list(
        db.execute(
            """
        SELECT
            COUNT(*) as total_edges,
            SUM(CASE WHEN cosine >= 0.90 THEN 1 ELSE 0 END) as strong_edges,
            SUM(CASE WHEN cosine >= 0.75 AND cosine < 0.90 THEN 1 ELSE 0 END) as weak_edges,
            SUM(CASE WHEN cosine < 0.75 THEN 1 ELSE 0 END) as very_weak_edges,
            COALESCE(AVG(cosine), 0) as avg_cosine,
            COALESCE(MIN(cosine), 0) as min_cosine,
            COALESCE(MAX(cosine), 0) as max_cosine
        FROM concept_relations
    """
        )
    )

    if edge_distribution and stats["edges"] > 0:
        stats["edge_distribution"] = {
            "strong_edges": edge_distribution[0][1],
            "weak_edges": edge_distribution[0][2],
            "very_weak_edges": edge_distribution[0][3],
            "avg_cosine": float(edge_distribution[0][4]),
            "min_cosine": float(edge_distribution[0][5]),
            "max_cosine": float(edge_distribution[0][6]),
        }

    # Cluster size distribution
    cluster_sizes = list(
        db.execute(
            """
        SELECT cluster_id, COUNT(*) as size
        FROM concept_clusters
        GROUP BY cluster_id
        ORDER BY size DESC
    """
        )
    )

    if cluster_sizes:
        stats["cluster_sizes"] = [{"cluster_id": row[0], "size": row[1]} for row in cluster_sizes]

        # Largest cluster info
        largest_cluster = cluster_sizes[0]
        stats["largest_cluster"] = {
            "id": largest_cluster[0],
            "size": largest_cluster[1],
        }

    # Network density (actual edges / possible edges)
    if stats["nodes"] > 1:
        possible_edges = stats["nodes"] * (stats["nodes"] - 1) / 2
        stats["density"] = stats["edges"] / possible_edges if possible_edges > 0 else 0
    else:
        stats["density"] = 0

    # Cluster metrics (if available)
    metrics_overview = list(db.execute("SELECT * FROM v_metrics_overview"))
    if metrics_overview:
        stats["cluster_metrics"] = {
            "avg_cluster_density": (float(metrics_overview[0][3]) if metrics_overview[0][3] else None),
            "avg_cluster_diversity": (float(metrics_overview[0][4]) if metrics_overview[0][4] else None),
        }

    # Health indicators
    stats["health"] = {
        "has_nodes": stats["nodes"] > 0,
        "has_edges": stats["edges"] > 0,
        "has_clusters": stats["clusters"] > 0,
        "density_reasonable": (0.001 <= stats.get("density", 0) <= 0.1 if "density" in stats else False),
    }

    return stats


def export_correlations(db):
    """Export pattern correlation analysis results."""
    correlations = []
    metadata = {
        "total_correlations": 0,
        "significant_correlations": 0,
        "correlation_methods": [],
        "generated_at": None,
        "run_id": None,
    }

    try:
        # First try: Query concept_correlations view (Phase 5-B database implementation)
        try:
            correlation_rows = list(
                db.execute(
                    """
                SELECT source, target, correlation, p_value, metric,
                       cluster_source, cluster_target, sample_size
                FROM concept_correlations
                ORDER BY ABS(correlation) DESC
                LIMIT 1000  -- Limit to top 1000 correlations for performance
            """
                )
            )

            if correlation_rows:
                for row in correlation_rows:
                    corr_record = {
                        "source": str(row[0]),
                        "target": str(row[1]),
                        "correlation": float(row[2]) if row[2] is not None else 0.0,
                        "p_value": float(row[3]) if row[3] is not None else 1.0,
                        "metric": str(row[4]) if row[4] else "database_view",
                        "cluster_source": int(row[5]) if row[5] is not None else None,
                        "cluster_target": int(row[6]) if row[6] is not None else None,
                    }

                    # Add sample_size if available
                    if len(row) > 7 and row[7] is not None:
                        corr_record["sample_size"] = int(row[7])

                    correlations.append(corr_record)

                LOG.info(f"Loaded {len(correlations)} correlations from database view")

        except Exception as db_error:
            LOG.warning(f"Database correlation view not available ({db_error}), falling back to Python computation")
            correlations = _compute_correlations_python(db)

    except Exception as e:
        LOG.warning(f"Could not retrieve correlations, using Python fallback: {e}")
        correlations = _compute_correlations_python(db)

    # Calculate metadata
    if correlations:
        metadata["total_correlations"] = len(correlations)
        metadata["significant_correlations"] = sum(1 for c in correlations if c.get("p_value", 1.0) < 0.05)
        metadata["correlation_methods"] = list(set(c.get("metric", "unknown") for c in correlations))

    import datetime  # noqa: E402

    metadata["generated_at"] = datetime.datetime.now().isoformat()

    # Try to get run_id from recent pipeline runs
    try:
        run_row = list(db.execute("SELECT run_id FROM metrics_log ORDER BY started_at DESC LIMIT 1"))
        if run_row:
            metadata["run_id"] = str(run_row[0][0])
    except Exception:
        metadata["run_id"] = "unknown"

    return {"correlations": correlations, "metadata": metadata}


def _compute_correlations_python(db):
    """Fallback: Compute correlations using Python/scipy when database view unavailable."""
    try:
        from itertools import combinations  # noqa: E402

        from scipy.stats import pearsonr  # noqa: E402
    except ImportError:
        LOG.error("scipy not available for correlation computation fallback")
        return []

    try:
        # Get concept embeddings from database
        concept_data = list(
            db.execute(
                """
            SELECT cn.concept_id, cn.embedding, cn.cluster_id, c.name
            FROM concept_network cn
            JOIN concepts c ON cn.concept_id = c.id
            WHERE cn.embedding IS NOT NULL
            ORDER BY cn.concept_id
        """
            )
        )

        if len(concept_data) < 2:
            LOG.warning("Insufficient concept data for correlation analysis")
            return []

        correlations = []
        # Process in batches to avoid memory issues with large networks
        batch_size = 100  # Limit combinations per batch

        # Convert embeddings to numpy arrays for efficient computation
        import numpy as np  # noqa: E402

        concept_list = []
        for row in concept_data:
            try:
                # Assuming embedding is stored as vector type, convert to numpy
                embedding = np.array(row[1])  # row[1] is embedding
                concept_list.append(
                    {
                        "id": str(row[0]),  # concept_id
                        "embedding": embedding,
                        "cluster_id": row[2],
                        "name": str(row[3]),
                    }
                )
            except Exception as e:
                LOG.warning(f"Skipping concept {row[0]} due to embedding parsing error: {e}")
                continue

        # Compute correlations between concept pairs
        processed_pairs = 0
        for (_i, concept_a), (_j, concept_b) in combinations(enumerate(concept_list), 2):
            if processed_pairs >= batch_size:
                break  # Limit for performance

            try:
                # Compute Pearson correlation
                r, p_value = pearsonr(concept_a["embedding"], concept_b["embedding"])

                # Skip if correlation is NaN or invalid
                if not np.isfinite(r) or not np.isfinite(p_value):
                    continue

                corr_record = {
                    "source": concept_a["id"],
                    "target": concept_b["id"],
                    "correlation": float(r),
                    "p_value": float(p_value),
                    "metric": "python_pearson",
                    "cluster_source": concept_a["cluster_id"],
                    "cluster_target": concept_b["cluster_id"],
                    "sample_size": len(concept_a["embedding"]),  # embedding dimension
                }

                correlations.append(corr_record)
                processed_pairs += 1

            except Exception as e:
                LOG.warning(f"Error computing correlation for {concept_a['id']} vs {concept_b['id']}: {e}")
                continue

        # Sort by absolute correlation strength
        correlations.sort(key=lambda x: abs(x["correlation"]), reverse=True)

        LOG.info(f"Computed {len(correlations)} correlations using Python fallback")
        return correlations[:500]  # Limit output size

    except Exception as e:
        LOG.error(f"Python correlation computation failed: {e}")
        return []


def export_patterns(db):
    """
    Cross-text pattern correlation analysis.
    - Loads correlation + concept data
    - Groups by book_source/book_target
    - Computes association metrics (support, lift, confidence)
    - Writes exports/graph_patterns.json
    - Validates against graph-patterns.schema.json
    """
    patterns = []
    metadata = {
        "total_patterns": 0,
        "analyzed_books": [],
        "pattern_methods": [],
        "generated_at": None,
        "run_id": None,
        "analysis_parameters": {"min_shared_concepts": 2, "min_pattern_strength": 0.1},
    }

    try:
        # Get concepts with their book associations and cluster information
        concept_data = list(
            db.execute(
                """
            SELECT DISTINCT
                c.id as concept_id,
                c.name as concept_name,
                c.book as book_name,
                cn.cluster_id,
                cn.embedding
            FROM concepts c
            LEFT JOIN concept_network cn ON c.id = cn.concept_id
            WHERE c.book IS NOT NULL
            ORDER BY c.book, c.id
        """
            )
        )

        if not concept_data:
            LOG.warning("No concept data with book associations found")
            return {"patterns": patterns, "metadata": metadata}

        # Group concepts by book
        books_concepts = {}
        for row in concept_data:
            concept_id, concept_name, book_name, cluster_id, embedding = row
            if book_name not in books_concepts:
                books_concepts[book_name] = []
            books_concepts[book_name].append(
                {
                    "id": str(concept_id),
                    "name": concept_name,
                    "cluster_id": cluster_id,
                    "embedding": embedding,
                }
            )

        metadata["analyzed_books"] = list(books_concepts.keys())

        # Analyze cross-book patterns
        book_names = list(books_concepts.keys())
        for i, book_a in enumerate(book_names):
            for j, book_b in enumerate(book_names):
                if i >= j:  # Avoid duplicate pairs and self-comparisons
                    continue

                concepts_a = set(c["id"] for c in books_concepts[book_a])
                concepts_b = set(c["id"] for c in books_concepts[book_b])

                # Find shared concepts
                shared_concepts = concepts_a.intersection(concepts_b)
                if len(shared_concepts) < metadata["analysis_parameters"]["min_shared_concepts"]:
                    continue

                # Calculate association metrics
                total_concepts = len(concepts_a.union(concepts_b))
                support = len(shared_concepts) / total_concepts if total_concepts > 0 else 0

                # Confidence: P(B|A) = |shared| / |A|
                confidence_a_to_b = len(shared_concepts) / len(concepts_a) if concepts_a else 0
                confidence_b_to_a = len(shared_concepts) / len(concepts_b) if concepts_b else 0

                # Lift: P(A,B) / (P(A) * P(B))
                p_a = len(concepts_a) / total_concepts if total_concepts > 0 else 0
                p_b = len(concepts_b) / total_concepts if total_concepts > 0 else 0
                p_a_and_b = len(shared_concepts) / total_concepts if total_concepts > 0 else 0
                lift = p_a_and_b / (p_a * p_b) if (p_a * p_b) > 0 else 0

                # Jaccard similarity
                jaccard = (
                    len(shared_concepts) / len(concepts_a.union(concepts_b)) if concepts_a.union(concepts_b) else 0
                )

                # Pattern strength (weighted combination)
                pattern_strength = jaccard * 0.4 + min(confidence_a_to_b, confidence_b_to_a) * 0.4 + support * 0.2

                if pattern_strength >= metadata["analysis_parameters"]["min_pattern_strength"]:
                    pattern_record = {
                        "book_source": book_a,
                        "book_target": book_b,
                        "shared_concepts": list(shared_concepts),
                        "pattern_strength": float(pattern_strength),
                        "metric": "jaccard",
                        "support": float(support),
                        "lift": float(lift),
                        "confidence": float(max(confidence_a_to_b, confidence_b_to_a)),
                        "jaccard": float(jaccard),
                    }

                    # Add cluster information if available
                    clusters_a = set(c["cluster_id"] for c in books_concepts[book_a] if c["cluster_id"] is not None)
                    clusters_b = set(c["cluster_id"] for c in books_concepts[book_b] if c["cluster_id"] is not None)

                    if clusters_a and clusters_b:
                        pattern_record["source_clusters"] = list(clusters_a)
                        pattern_record["target_clusters"] = list(clusters_b)

                    patterns.append(pattern_record)

        # Sort patterns by strength
        patterns.sort(key=lambda x: x["pattern_strength"], reverse=True)

        # Update metadata
        metadata["total_patterns"] = len(patterns)
        if patterns:
            metadata["pattern_methods"] = list(set(p.get("metric", "unknown") for p in patterns))

        import datetime  # noqa: E402

        metadata["generated_at"] = datetime.datetime.now().isoformat()

        # Try to get run_id from recent pipeline runs
        try:
            run_row = list(db.execute("SELECT run_id FROM metrics_log ORDER BY started_at DESC LIMIT 1"))
            if run_row:
                metadata["run_id"] = str(run_row[0][0])
        except Exception:
            metadata["run_id"] = "unknown"

        LOG.info(f"Generated {len(patterns)} cross-text patterns across {len(metadata['analyzed_books'])} books")

    except Exception as e:
        LOG.warning(f"Could not compute cross-text patterns: {e}")

    return {"patterns": patterns, "metadata": metadata}


# ============================================================================
# Temporal Analysis Engine (ADR-025)
# ============================================================================


def compute_rolling_windows(df, window=5, metrics=None):
    """
    Compute rolling statistics on sequential data.

    Args:
        df: pandas Series or DataFrame with sequential index
        window: Rolling window size
        metrics: List of metrics to compute ('mean', 'std', 'sum', 'min', 'max')

    Returns:
        DataFrame with rolling statistics
    """
    if metrics is None:
        metrics = ["mean", "std"]

    if isinstance(df, pd.Series):
        df = df.to_frame(name="value")
    elif isinstance(df, pd.DataFrame) and len(df.columns) == 1:
        df = df.copy()
    else:
        raise ValueError("df must be a Series or single-column DataFrame")

    rolling = df.rolling(window=window, min_periods=1)
    results = {}
    for metric in metrics:
        if hasattr(rolling, metric):
            results[metric] = getattr(rolling, metric)().iloc[:, 0]
        else:
            LOG.warning(f"Metric '{metric}' not available in rolling window")
    return pd.DataFrame(results)


def naive_forecast(series, horizon=10):
    """
    Naive forecast: repeat last value with prediction intervals (±std).

    Args:
        series: pandas Series with sequential data
        horizon: Number of steps to forecast

    Returns:
        dict with 'forecast' (Series) and 'intervals' (DataFrame with lower/upper)
    """
    if len(series) == 0:
        empty_series = pd.Series([], dtype=float)
        return {"forecast": empty_series, "intervals": pd.DataFrame()}
    last = series.iloc[-1]
    std = series.std()
    forecast_index = pd.RangeIndex(len(series), len(series) + horizon)
    forecast = pd.Series([last] * horizon, index=forecast_index)
    intervals = pd.DataFrame(
        {"lower": forecast - std, "upper": forecast + std}, index=forecast_index
    )
    return {"forecast": forecast, "intervals": intervals}


def sma_forecast(series, window=5, horizon=10):
    """
    Simple Moving Average forecast with intervals.

    Args:
        series: pandas Series with sequential data
        window: Moving average window size
        horizon: Number of steps to forecast

    Returns:
        dict with 'forecast' (Series) and 'intervals' (DataFrame with lower/upper)
    """
    if len(series) == 0:
        empty_series = pd.Series([], dtype=float)
        return {"forecast": empty_series, "intervals": pd.DataFrame()}
    sma = series.rolling(window=window, min_periods=1).mean().iloc[-1]
    rolling_std = series.rolling(window=window).std()
    std = rolling_std.iloc[-1] if not rolling_std.empty else series.std()
    forecast_index = pd.RangeIndex(len(series), len(series) + horizon)
    forecast = pd.Series([sma] * horizon, index=forecast_index)
    intervals = pd.DataFrame(
        {"lower": forecast - std, "upper": forecast + std}, index=forecast_index
    )
    return {"forecast": forecast, "intervals": intervals}


def arima_forecast(series, order=(1, 1, 1), horizon=10):
    """
    ARIMA forecast with prediction intervals.

    Args:
        series: pandas Series with sequential data
        order: ARIMA order tuple (p, d, q)
        horizon: Number of steps to forecast

    Returns:
        dict with 'forecast' (Series) and 'intervals' (DataFrame with lower/upper)
    """
    try:
        from statsmodels.tsa.arima.model import ARIMA

        if len(series) < 3:
            # Fallback to naive if insufficient data
            return naive_forecast(series, horizon)

        model = ARIMA(series, order=order)
        fit = model.fit()
        forecast_obj = fit.get_forecast(steps=horizon)
        forecast = forecast_obj.predicted_mean
        intervals = forecast_obj.conf_int()
        intervals.columns = ["lower", "upper"]
        return {"forecast": forecast, "intervals": intervals}
    except ImportError:
        LOG.warning("statsmodels not available, falling back to SMA forecast")
        return sma_forecast(series, window=5, horizon=horizon)
    except Exception as e:
        LOG.warning(f"ARIMA forecast failed: {e}, falling back to SMA")
        return sma_forecast(series, window=5, horizon=horizon)


def detect_change_points(series, threshold=3.0):
    """
    Z-score based change point detection for textual shifts.

    Args:
        series: pandas Series with sequential data
        threshold: Z-score threshold for change point detection (default: 3.0)

    Returns:
        list of indices where change points are detected
    """
    if len(series) < 2:
        return []

    mean = series.mean()
    std = series.std()

    if std == 0:
        return []

    z_scores = np.abs((series - mean) / std)
    change_points = np.where(z_scores > threshold)[0]
    return change_points.tolist()


def export_temporal_patterns(db):
    """
    Temporal pattern analysis using rolling windows.
    - Analyzes concept/cluster frequency over sequential indices
    - Computes rolling means/sums with configurable windows
    - Detects change points and basic seasonality
    - Writes exports/temporal_patterns.json
    - Validates against temporal-patterns.schema.json
    """
    import statistics  # noqa: E402

    patterns = []
    metadata = {
        "generated_at": None,
        "analysis_parameters": {
            "default_unit": "chapter",
            "default_window": 5,
            "min_series_length": 10,
        },
        "total_series": 0,
        "books_analyzed": [],
    }

    try:
        rows = list(
            db.execute(
                """
            SELECT book, concept_id::text, chapter::int, SUM(count)::int AS ct
            FROM v_concept_occurrences
            GROUP BY book, concept_id, chapter
            ORDER BY book, concept_id, chapter
            """
            )
        )

        if not rows:
            return {"temporal_patterns": [], "metadata": metadata}

        by_key = {}
        max_ch = {}
        for book, cid, chapter, ct in rows:
            key = (book, cid)
            by_key.setdefault(key, {})[int(chapter)] = int(ct)
            max_ch[book] = max(max_ch.get(book, 0), int(chapter))

        for (book, cid), chmap in by_key.items():
            length = max_ch[book]
            values = [chmap.get(i, 0) for i in range(1, length + 1)]
            if len(values) < metadata["analysis_parameters"]["min_series_length"]:
                continue
            window = metadata["analysis_parameters"]["default_window"]
            rolling = [statistics.mean(values[i : i + window]) for i in range(0, len(values) - window + 1)]
            change_points = []
            if len(rolling) > 2:
                st = statistics.pstdev(rolling)
                if st > 0:
                    for i in range(1, len(rolling)):
                        if abs(rolling[i] - rolling[i - 1]) > 2 * st:
                            change_points.append(i)
            patterns.append(
                {
                    "series_id": f"concept_{cid}",
                    "unit": "chapter",
                    "window": window,
                    "start_index": 1,
                    "end_index": length,
                    "metric": "frequency",
                    "values": rolling,
                    "method": "rolling_mean",
                    "book": book,
                    "change_points": change_points[:5],
                    "metadata": {
                        "total_observations": length,
                        "rolling_windows": len(rolling),
                    },
                }
            )

        metadata["total_series"] = len(patterns)
        metadata["books_analyzed"] = sorted({b for (b, _cid) in by_key})
    except Exception as e:
        LOG.warning(f"Could not compute temporal patterns: {e}")
        patterns = []

    return {"temporal_patterns": patterns, "metadata": metadata}


def export_forecast(db):
    """
    Forecast temporal patterns using statistical models.
    - For each temporal series, forecast horizon steps ahead
    - Try ARIMA if statsmodels available, fallback to SMA
    - Computes prediction intervals and error metrics
    - Writes exports/pattern_forecast.json
    - Validates against pattern-forecast.schema.json
    """
    forecasts = []
    metadata = {
        "generated_at": None,
        "forecast_parameters": {
            "default_horizon": 10,
            "default_model": "sma",
            "min_training_length": 5,
        },
        "total_forecasts": 0,
        "books_forecasted": [],
        "model_distribution": {"naive": 0, "sma": 0, "arima": 0},
        "average_metrics": {"rmse": None, "mae": None},
    }

    try:
        # First get temporal patterns (this would normally be from the temporal export)
        temporal_data = export_temporal_patterns(db)
        temporal_patterns = temporal_data.get("temporal_patterns", [])

        metadata["books_forecasted"] = list(set(p["book"] for p in temporal_patterns))

        for pattern in temporal_patterns[:50]:  # Limit to first 50 for performance
            series_id = pattern["series_id"]
            values = pattern["values"]
            book = pattern["book"]

            if len(values) < metadata["forecast_parameters"]["min_training_length"]:
                continue

            horizon = metadata["forecast_parameters"]["default_horizon"]
            default_model = metadata["forecast_parameters"]["default_model"]

            # Convert to pandas Series for temporal engine functions
            series = pd.Series(values)

            # Try forecasts in order: ARIMA (if available), SMA, then naive
            forecast_series = None
            model_used = None
            predictions = []
            prediction_intervals = None

            # Try ARIMA first if requested or as default
            if default_model == "arima" or len(values) >= 10:
                try:
                    forecast_series = arima_forecast(series, order=(1, 1, 1), horizon=horizon)
                    model_used = "arima"
                    predictions = forecast_series.tolist()
                except Exception:
                    # Fall through to SMA
                    pass

            # Try SMA if ARIMA failed or not requested
            if model_used is None:
                try:
                    forecast_series = sma_forecast(series, window=5, horizon=horizon)
                    model_used = "sma"
                    predictions = forecast_series.tolist()
                except Exception:
                    # Fall back to naive
                    pass

            # Naive forecast as final fallback
            if model_used is None:
                forecast_series = naive_forecast(series, horizon=horizon)
                model_used = "naive"
                predictions = forecast_series.tolist()

            metadata["model_distribution"][model_used] += 1

            # Calculate error metrics (simple approximation for now)
            # In production, these would be computed from held-out validation data
            if len(values) > horizon:
                # Use last horizon values as "test" set
                test_values = values[-horizon:]
                rmse = np.sqrt(np.mean([(p - t) ** 2 for p, t in zip(predictions, test_values, strict=True)]))
                mae = np.mean([abs(p - t) for p, t in zip(predictions, test_values, strict=True)])
            else:
                # Estimate based on series variance
                series_std = series.std() if len(series) > 1 else 1.0
                rmse = series_std * 1.5
                mae = series_std * 1.2

            # Simple prediction intervals (1.96 * std for 95% confidence)
            std_estimate = series.std() if len(series) > 1 else 1.0
            prediction_intervals = {
                "lower": [max(0, p - 1.96 * std_estimate) for p in predictions],
                "upper": [p + 1.96 * std_estimate for p in predictions],
                "confidence_level": 0.95,
            }

            forecast_record = {
                "series_id": series_id,
                "horizon": horizon,
                "model": model_used,
                "predictions": predictions,
                "book": book,
                "rmse": float(rmse),
                "mae": float(mae),
                "prediction_intervals": prediction_intervals,
                "metadata": {
                    "training_length": len(values),
                    "forecast_method": model_used,
                },
            }

            forecasts.append(forecast_record)

        metadata["total_forecasts"] = len(forecasts)

        # Calculate average metrics
        if forecasts:
            rmses = [f["rmse"] for f in forecasts if "rmse" in f]
            maes = [f["mae"] for f in forecasts if "mae" in f]
            metadata["average_metrics"]["rmse"] = sum(rmses) / len(rmses) if rmses else None
            metadata["average_metrics"]["mae"] = sum(maes) / len(maes) if maes else None

        LOG.info(f"Generated {len(forecasts)} forecasts across {len(metadata['books_forecasted'])} books")

    except Exception as e:
        LOG.warning(f"Could not compute forecasts: {e}")
        forecasts = []

    return {"forecasts": forecasts, "metadata": metadata}


def main():
    """Main export function."""

    log_json(LOG, 20, "export_stats_start")

    try:
        db = get_gematria_rw()
        stats = calculate_graph_stats(db)

        # Export correlations (Phase 5)
        correlations = export_correlations(db)

        # Export patterns (Phase 6)
        patterns = export_patterns(db)

        # Export temporal patterns (Phase 8)
        temporal_patterns = export_temporal_patterns(db)

        # Export forecasts (Phase 8)
        forecasts = export_forecast(db)

        # Add timestamp
        import datetime  # noqa: E402

        now = datetime.datetime.now().isoformat()

        stats["export_timestamp"] = now
        correlations["metadata"]["generated_at"] = now
        patterns["metadata"]["generated_at"] = now
        temporal_patterns["metadata"]["generated_at"] = now
        forecasts["metadata"]["generated_at"] = now

        # === Rule 021/022 + Rule 030: schema validation (HARD-REQUIRED) ===
        import json  # noqa: E402
        import sys  # noqa: E402
        from pathlib import Path  # noqa: E402

        # Hard requirement: jsonschema must be installed
        try:
            from jsonschema import ValidationError, validate  # noqa: E402
        except ImportError:
            print(
                "[export_stats] CRITICAL: jsonschema not installed (hard requirement)",
                file=sys.stderr,
            )
            print(
                "[export_stats] Install with: pip install -r requirements-dev.txt",
                file=sys.stderr,
            )
            sys.exit(2)

        # Validate stats schema (only if we have meaningful data)
        if stats["nodes"] > 0 or stats["edges"] > 0:
            SCHEMA_PATH = Path("docs/SSOT/graph-stats.schema.json")
            schema = json.loads(SCHEMA_PATH.read_text())
            try:
                validate(instance=stats, schema=schema)
            except ValidationError as e:
                print(
                    f"[export_stats] stats schema validation failed: {e.message}",
                    file=sys.stderr,
                )
                sys.exit(2)

        # Validate correlations schema (if correlations exist)
        CORRELATIONS_SCHEMA_PATH = Path("docs/SSOT/graph-correlations.schema.json")
        if correlations["correlations"]:  # Only validate if we have data
            correlations_schema = json.loads(CORRELATIONS_SCHEMA_PATH.read_text())
            try:
                validate(instance=correlations, schema=correlations_schema)
            except ValidationError as e:
                print(
                    f"[export_stats] correlations schema validation failed: {e.message}",
                    file=sys.stderr,
                )
                sys.exit(2)

        # Validate patterns schema (if patterns exist) - Rule 032
        PATTERNS_SCHEMA_PATH = Path("docs/SSOT/graph-patterns.schema.json")
        if patterns["patterns"]:  # Only validate if we have data
            patterns_schema = json.loads(PATTERNS_SCHEMA_PATH.read_text())
            try:
                validate(instance=patterns, schema=patterns_schema)
            except ValidationError as e:
                print(
                    f"[export_stats] patterns schema validation failed: {e.message}",
                    file=sys.stderr,
                )
                sys.exit(2)

        # Validate temporal patterns schema (if patterns exist) - Rule 034
        TEMPORAL_SCHEMA_PATH = Path("docs/SSOT/temporal-patterns.schema.json")
        if temporal_patterns["temporal_patterns"]:  # Only validate if we have data
            temporal_schema = json.loads(TEMPORAL_SCHEMA_PATH.read_text())
            try:
                validate(instance=temporal_patterns, schema=temporal_schema)
            except ValidationError as e:
                print(
                    f"[export_stats] temporal patterns schema validation failed: {e.message}",
                    file=sys.stderr,
                )
                sys.exit(2)

        # Validate forecast schema (if forecasts exist) - Rule 035
        FORECAST_SCHEMA_PATH = Path("docs/SSOT/pattern-forecast.schema.json")
        if forecasts["forecasts"]:  # Only validate if we have data
            forecast_schema = json.loads(FORECAST_SCHEMA_PATH.read_text())
            try:
                validate(instance=forecasts, schema=forecast_schema)
            except ValidationError as e:
                print(
                    f"[export_stats] forecast schema validation failed: {e.message}",
                    file=sys.stderr,
                )
                sys.exit(2)

        # Output JSON to stdout
        print(json.dumps(stats, indent=2))

        # Also write static files for UI consumption
        out_dir = os.getenv("EXPORT_DIR", "exports")
        os.makedirs(out_dir, exist_ok=True)

        # Write stats
        stats_path = os.path.join(out_dir, "graph_stats.json")
        with open(stats_path, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)

        # Write correlations (Phase 5)
        correlations_path = os.path.join(out_dir, "graph_correlations.json")
        with open(correlations_path, "w", encoding="utf-8") as f:
            json.dump(correlations, f, indent=2, ensure_ascii=False)

        # Write patterns (Phase 6)
        patterns_path = os.path.join(out_dir, "graph_patterns.json")
        with open(patterns_path, "w", encoding="utf-8") as f:
            json.dump(patterns, f, indent=2, ensure_ascii=False)

        # Write temporal patterns (Phase 8)
        temporal_path = os.path.join(out_dir, "temporal_patterns.json")
        with open(temporal_path, "w", encoding="utf-8") as f:
            json.dump(temporal_patterns, f, indent=2, ensure_ascii=False)

        # Write forecasts (Phase 8)
        forecast_path = os.path.join(out_dir, "pattern_forecast.json")
        with open(forecast_path, "w", encoding="utf-8") as f:
            json.dump(forecasts, f, indent=2, ensure_ascii=False)

        log_json(
            LOG,
            20,
            "export_stats_complete",
            **{k: v for k, v in stats.items() if isinstance(v, int | float | bool)},
            correlations_total=correlations["metadata"]["total_correlations"],
            correlations_significant=correlations["metadata"]["significant_correlations"],
            patterns_total=patterns["metadata"]["total_patterns"],
            temporal_patterns_total=temporal_patterns["metadata"]["total_series"],
            forecasts_total=forecasts["metadata"]["total_forecasts"],
        )

    except Exception as e:
        log_json(LOG, 40, "export_stats_failed", error=str(e))
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
# PR-061: Graph centrality computation and persistence
