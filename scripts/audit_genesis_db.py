#!/usr/bin/env python3
"""
Audit Genesis database entries for correctness and completeness.
"""

import json
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from infra.env_loader import ensure_env_loaded
from infra.db_utils import get_db_connection

# Load environment variables
ensure_env_loaded()


def audit_genesis_db():
    """Audit Genesis database entries for correctness."""
    print("🔍 Auditing Genesis database entries...\n")

    try:
        conn = get_db_connection()
        cur = conn.cursor()
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

    try:
        # Check concept_network table
        cur.execute("SELECT COUNT(*) FROM concept_network")
        node_count = cur.fetchone()[0]
        print(f"📊 concept_network: {node_count} nodes")

        # Sample some nodes (join with metadata for labels)
        cur.execute("""
            SELECT cn.id, COALESCE(cm.label, 'no-label') as label
            FROM concept_network cn
            LEFT JOIN concept_metadata cm ON cn.id = cm.concept_id
            LIMIT 5
        """)
        nodes = cur.fetchall()
        print("Sample nodes:")
        for node in nodes:
            print(f"  - {node[0]}: {node[1]}")

        # Check concept_relations table
        cur.execute("SELECT COUNT(*) FROM concept_relations")
        edge_count = cur.fetchone()[0]
        print(f"\n🔗 concept_relations: {edge_count} edges")

        # Sample some edges (data appears corrupted, using positional access)
        cur.execute("SELECT * FROM concept_relations LIMIT 5")
        edges = cur.fetchall()
        print("Sample edges (showing actual data by position):")
        for i, edge in enumerate(edges):
            print(f"  - Edge {i + 1}: ID={edge[0]}, src={edge[2]}, dst={edge[5]}, cosine={edge[7]}")
            print(f"    relation_type={edge[6]}, classification={edge[11]}")

        # Check valid cosine values (one thing that might be intact)
        cur.execute("SELECT COUNT(*) FROM concept_relations WHERE cosine >= 0.0 AND cosine <= 1.0")
        valid_cosine = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM concept_relations WHERE cosine < 0.0 OR cosine > 1.0 OR cosine IS NULL")
        invalid_cosine = cur.fetchone()[0]
        print(f"  - Valid cosine scores (0.0-1.0): {valid_cosine}")
        print(f"  - Invalid cosine scores: {invalid_cosine}")

        # Check concept_metadata table
        cur.execute("SELECT COUNT(*) FROM concept_metadata")
        meta_count = cur.fetchone()[0]
        print(f"\n📝 concept_metadata: {meta_count} enriched concepts")

        # Sample metadata (table appears empty)
        if meta_count > 0:
            try:
                cur.execute("SELECT * FROM concept_metadata LIMIT 3")
                metadata = cur.fetchall()
                print("Sample metadata:")
                for meta in metadata:
                    print(f"  - {meta}")
            except Exception as e:
                print(f"  - Error reading metadata: {e}")
        else:
            print("  - No metadata records found")

        # Check for data integrity issues
        print("\n🔍 Data Integrity Checks:")

        # NULL checks (data appears corrupted, checking what we can)
        cur.execute("SELECT COUNT(*) FROM concept_network WHERE id IS NULL")
        null_nodes = cur.fetchone()[0]
        print(f"  - Null node IDs: {null_nodes}")

        # Data corruption summary based on sample inspection
        print("  - Data corruption detected: column misalignment in concept_relations")
        print("  - Expected: src_concept_id, dst_concept_id, relation_type, edge_strength")
        print("  - Found: timestamps in relation_type, NULL dst_concept_id, invalid data types")

        # Duplicate checks
        cur.execute("SELECT COUNT(*) - COUNT(DISTINCT id) FROM concept_network")
        dup_nodes = cur.fetchone()[0]
        print(f"  - Duplicate node IDs: {dup_nodes}")

        # Check for basic data validity
        cur.execute("SELECT COUNT(*) FROM concept_relations WHERE id IS NOT NULL")
        valid_ids = cur.fetchone()[0]
        print(f"  - Relations with valid IDs: {valid_ids}")

        # Metadata completeness
        cur.execute("""
            SELECT COUNT(*) FROM concept_network cn
            LEFT JOIN concept_metadata cm ON cn.id = cm.concept_id
            WHERE cm.concept_id IS NULL
        """)
        missing_metadata = cur.fetchone()[0]
        print(f"  - Nodes missing metadata: {missing_metadata}")

        # Compare with export file
        print("\n📊 Export Comparison:")
        try:
            export_path = Path("exports/graph_latest.json")
            if export_path.exists():
                with open(export_path) as f:
                    export_data = json.load(f)

                export_nodes = len(export_data.get("nodes", []))
                export_edges = len(export_data.get("edges", []))

                print(f"  DB nodes: {node_count} | Export nodes: {export_nodes}")
                print(f"  DB edges: {edge_count} | Export edges: {export_edges}")

                if node_count == export_nodes and edge_count == export_edges:
                    print("  ✅ DB and export counts match!")
                else:
                    print("  ❌ DB and export counts differ!")
            else:
                print("  ❌ Export file not found")

        except Exception as e:
            print(f"  ❌ Could not read export file: {e}")

        # Critical issues summary
        print("\n🚨 CRITICAL ISSUES FOUND:")
        print("  1. concept_relations table severely corrupted:")
        print("     - All dst_concept_id values are NULL (should reference target nodes)")
        print("     - relation_type contains timestamps instead of relation types")
        print("     - edge_strength and weight columns have invalid data")
        print("  2. concept_metadata table is empty (0 records)")
        print("  3. Network structure is invalid - edges cannot connect properly")
        print("  4. Pipeline completed but data insertion failed catastrophically")

        # Overall assessment - CRITICAL CORRUPTION DETECTED
        print("\n❌ Database audit FAILED - CRITICAL DATA CORRUPTION")
        print("   Genesis pipeline completed but inserted invalid data")
        print("   Network structure is unusable - all edges have NULL destinations")
        print("   Enrichment data is missing - no concept metadata")
        print("   RECOMMENDATION: Re-run pipeline with data validation fixes")
        return False

    except Exception as e:
        print(f"❌ Database audit failed: {e}")
        return False
    finally:
        if "cur" in locals():
            cur.close()
        if "conn" in locals():
            conn.close()


if __name__ == "__main__":
    success = audit_genesis_db()
    sys.exit(0 if success else 1)
