import unittest
from unittest.mock import MagicMock, patch
import sys

# Mock psycopg before importing the script
sys.modules["psycopg"] = MagicMock()

from agentpm.scripts.docs_dashboard_refresh import (  # noqa: E402
    generate_summary,
    generate_canonical,
    generate_archive_candidates,
    generate_unreviewed_batch,
    main,
)


class TestDocsDashboardRefresh(unittest.TestCase):
    def setUp(self):
        self.mock_conn = MagicMock()
        self.mock_cursor = MagicMock()
        self.mock_conn.cursor.return_value.__enter__.return_value = self.mock_cursor

    @patch("agentpm.scripts.docs_dashboard_refresh.write_json")
    def test_generate_summary(self, mock_write_json):
        # Mock DB results: total, canonical, archive, unreviewed
        self.mock_cursor.fetchone.side_effect = [[100], [50], [20], [10]]

        generate_summary(self.mock_conn)

        self.assertEqual(mock_write_json.call_count, 1)
        args, _ = mock_write_json.call_args
        filename, data = args
        self.assertEqual(filename, "summary.json")
        self.assertEqual(data["total_docs"], 100)
        self.assertEqual(data["canonical_docs"], 50)
        self.assertEqual(data["archive_candidates"], 20)
        self.assertEqual(data["unreviewed_docs"], 10)
        self.assertEqual(data["ssot_ratio"], 0.5)

    @patch("agentpm.scripts.docs_dashboard_refresh.write_json")
    def test_generate_canonical(self, mock_write_json):
        # Mock DB results
        self.mock_cursor.fetchall.return_value = [
            ("docs/file1.md", "Title 1", "canonical", None),
            ("docs/file2.md", "Title 2", "canonical", None),
        ]

        generate_canonical(self.mock_conn)

        self.assertEqual(mock_write_json.call_count, 1)
        args, _ = mock_write_json.call_args
        filename, data = args
        self.assertEqual(filename, "canonical.json")
        self.assertEqual(len(data["items"]), 2)
        self.assertEqual(data["items"][0]["path"], "docs/file1.md")

    @patch("agentpm.scripts.docs_dashboard_refresh.write_json")
    def test_generate_archive_candidates(self, mock_write_json):
        # Mock DB results
        self.mock_cursor.fetchall.return_value = [
            ("docs/old/file1.md",),
            ("docs/old/file2.md",),
            ("docs/old/file3.md",),
            ("docs/other/file4.md",),
        ]

        generate_archive_candidates(self.mock_conn)

        self.assertEqual(mock_write_json.call_count, 1)
        args, _ = mock_write_json.call_args
        filename, data = args
        self.assertEqual(filename, "archive-candidates.json")
        self.assertEqual(len(data["groups"]), 2)

        # Check grouping
        group1 = next(g for g in data["groups"] if g["directory"] == "docs/old")
        self.assertEqual(group1["count"], 3)
        self.assertEqual(len(group1["examples"]), 3)

    @patch("agentpm.scripts.docs_dashboard_refresh.write_json")
    def test_generate_unreviewed_batch(self, mock_write_json):
        # Mock DB results
        self.mock_cursor.fetchall.return_value = [
            ("docs/new1.md", "New Doc 1", None),
        ]

        generate_unreviewed_batch(self.mock_conn)

        self.assertEqual(mock_write_json.call_count, 1)
        args, _ = mock_write_json.call_args
        filename, data = args
        self.assertEqual(filename, "unreviewed-batch.json")
        self.assertEqual(len(data["items"]), 1)
        self.assertEqual(data["items"][0]["path"], "docs/new1.md")

    @patch("agentpm.scripts.docs_dashboard_refresh.get_db_connection")
    @patch("agentpm.scripts.docs_dashboard_refresh.ensure_exports_dir")
    @patch("agentpm.scripts.docs_dashboard_refresh.generate_summary")
    @patch("agentpm.scripts.docs_dashboard_refresh.generate_canonical")
    @patch("agentpm.scripts.docs_dashboard_refresh.generate_archive_candidates")
    @patch("agentpm.scripts.docs_dashboard_refresh.generate_unreviewed_batch")
    @patch("agentpm.scripts.docs_dashboard_refresh.generate_orphans")
    @patch("agentpm.scripts.docs_dashboard_refresh.generate_archive_dryrun")
    def test_main(
        self,
        mock_dryrun,
        mock_orphans,
        mock_unreviewed,
        mock_archive,
        mock_canonical,
        mock_summary,
        mock_ensure,
        mock_get_db,
    ):
        mock_get_db.return_value = self.mock_conn

        main()

        mock_ensure.assert_called_once()
        mock_get_db.assert_called_once()
        mock_summary.assert_called_once()
        mock_canonical.assert_called_once()
        mock_archive.assert_called_once()
        mock_unreviewed.assert_called_once()
        mock_orphans.assert_called_once()
        mock_dryrun.assert_called_once()
        self.mock_conn.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
