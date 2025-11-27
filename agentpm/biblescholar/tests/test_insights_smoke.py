import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from agentpm.biblescholar.insights_flow import InsightsFlow


def test_insights_smoke():
    print("Initializing InsightsFlow...")
    flow = InsightsFlow()
    print(f"DB Status: {flow.db.db_status}")

    verse_id = "1"  # Genesis 1:1
    print(f"Fetching context for verse_id={verse_id}...")

    context = flow.get_verse_context(verse_id)

    print("Context retrieved:")
    print(f"  Verse ID: {context.verse_id}")
    print(f"  Proper Names: {len(context.proper_names)}")
    print(f"  Word Links: {len(context.word_links)}")
    print(f"  Cross Refs: {len(context.cross_references)}")

    if context.proper_names:
        print(f"  Sample Proper Name: {context.proper_names[0]}")

    if context.cross_references:
        print(f"  Sample Cross Ref: {context.cross_references[0]}")

    print("\nGenerating Insight (Placeholder)...")
    insight = flow.generate_insight(verse_id)
    print(f"Insight: {insight}")


if __name__ == "__main__":
    test_insights_smoke()
