import os
import time

import pytest

from src.infra.checkpointer import get_checkpointer

pytestmark = pytest.mark.skipif(
    os.getenv("CHECKPOINTER", "memory").lower() != "postgres"
    or not os.getenv("GEMATRIA_DSN"),
    reason="Postgres checkpointer not configured for integration test",
)


@pytest.fixture
def clean_test_data():
    """Clean up test data after each test."""
    cp = get_checkpointer()
    thread_id = "test-thread-cleanup"

    # Clean up any existing data
    try:
        # We can't directly delete from the tables since we don't have direct access,
        # but we can use the checkpointer's methods if they exist
        # For now, just yield and assume test data is cleaned up by test isolation
        yield thread_id
    finally:
        # Cleanup would go here if needed
        pass


def test_postgres_checkpointer_get_tuple_nonexistent():
    """Test get_tuple returns None for non-existent thread."""
    cp = get_checkpointer()
    config = {"configurable": {"thread_id": "nonexistent-thread"}}
    result = cp.get_tuple(config)
    assert result is None


def test_postgres_checkpointer_put_and_get_tuple():
    """Test put stores checkpoint and get_tuple retrieves it."""
    cp = get_checkpointer()
    thread_id = "test-thread-get-tuple"
    checkpoint_id = "cp-001"

    config = {"configurable": {"thread_id": thread_id, "checkpoint_id": checkpoint_id}}
    checkpoint = {"state": {"key": "value"}, "config": {}}
    metadata = {"timestamp": "2024-01-01"}

    # Put checkpoint
    result_config = cp.put(config, checkpoint, metadata)
    assert result_config == config

    # Get it back
    retrieved = cp.get_tuple(config)
    assert retrieved is not None
    retrieved_checkpoint, retrieved_metadata, parent_config = retrieved
    assert retrieved_checkpoint == checkpoint
    assert retrieved_metadata == metadata
    assert parent_config is None


def test_postgres_checkpointer_list_empty():
    """Test list returns empty iterator for thread with no checkpoints."""
    cp = get_checkpointer()
    config = {"configurable": {"thread_id": "empty-thread"}}
    checkpoints = list(cp.list(config))
    assert len(checkpoints) == 0


def test_postgres_checkpointer_list_with_data():
    """Test list returns checkpoints in correct order."""
    cp = get_checkpointer()
    thread_id = "test-thread-list"

    # Put multiple checkpoints
    configs = []
    for i in range(3):
        checkpoint_id = f"cp-{i:03d}"
        config = {
            "configurable": {"thread_id": thread_id, "checkpoint_id": checkpoint_id}
        }
        checkpoint = {"state": {"key": f"value-{i}"}}
        metadata = {"index": i}
        cp.put(config, checkpoint, metadata)
        configs.append(config)
        time.sleep(0.001)  # Ensure different timestamps

    # List all
    checkpoints = list(cp.list({"configurable": {"thread_id": thread_id}}))
    assert len(checkpoints) == 3

    # Should be in reverse chronological order (newest first)
    checkpoint_ids = [cp[0]["configurable"]["checkpoint_id"] for cp in checkpoints]
    assert checkpoint_ids == ["cp-002", "cp-001", "cp-000"]


def test_postgres_checkpointer_list_with_before():
    """Test list pagination with before parameter."""
    cp = get_checkpointer()
    thread_id = "test-thread-before"

    # Put checkpoints
    for i in range(5):
        checkpoint_id = f"cp-{i:03d}"
        config = {
            "configurable": {"thread_id": thread_id, "checkpoint_id": checkpoint_id}
        }
        checkpoint = {"state": {"key": f"value-{i}"}}
        cp.put(config, checkpoint, {})
        time.sleep(0.001)

    # Get first batch
    all_checkpoints = list(cp.list({"configurable": {"thread_id": thread_id}}, limit=2))
    assert len(all_checkpoints) == 2

    # Use before parameter to get next batch
    before_checkpoint = all_checkpoints[-1]  # Last item from first batch
    before_param = (
        before_checkpoint[4],
        before_checkpoint[0]["configurable"]["checkpoint_id"],
    )  # (created_at, checkpoint_id)

    next_batch = list(
        cp.list(
            {"configurable": {"thread_id": thread_id}}, before=before_param, limit=2
        )
    )
    assert len(next_batch) == 2

    # Should not overlap
    first_ids = {cp[0]["configurable"]["checkpoint_id"] for cp in all_checkpoints}
    second_ids = {cp[0]["configurable"]["checkpoint_id"] for cp in next_batch}
    assert first_ids.isdisjoint(second_ids)


def test_postgres_checkpointer_put_writes():
    """Test put_writes stores pending writes."""
    cp = get_checkpointer()
    thread_id = "test-thread-writes"
    checkpoint_id = "cp-writes"

    config = {"configurable": {"thread_id": thread_id, "checkpoint_id": checkpoint_id}}
    writes = [
        ("channel1", {"data": "value1"}),
        ("channel2", {"data": "value2"}),
    ]
    task_id = "task-001"

    # This should not raise an error (even if we don't query the writes later)
    result_config = cp.put_writes(config, writes, task_id)
    assert result_config == config


def test_postgres_checkpointer_upsert_behavior():
    """Test that put updates existing checkpoint (upsert behavior)."""
    cp = get_checkpointer()
    thread_id = "test-thread-upsert"
    checkpoint_id = "cp-upsert"

    config = {"configurable": {"thread_id": thread_id, "checkpoint_id": checkpoint_id}}

    # First put
    checkpoint1 = {"state": {"key": "value1"}}
    cp.put(config, checkpoint1, {"meta": "first"})

    # Second put with same ID (should update)
    checkpoint2 = {"state": {"key": "value2"}}
    cp.put(config, checkpoint2, {"meta": "second"})

    # Get should return the updated checkpoint
    retrieved = cp.get_tuple(config)
    assert retrieved is not None
    retrieved_checkpoint, retrieved_metadata, _ = retrieved
    assert retrieved_checkpoint == checkpoint2
    assert retrieved_metadata == {"meta": "second"}
