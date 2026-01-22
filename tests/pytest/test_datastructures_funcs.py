"""Tests for shiny._datastructures module."""

from shiny._datastructures import PriorityQueueFIFO


class TestPriorityQueueFIFO:
    """Tests for PriorityQueueFIFO class."""

    def test_priority_queue_basic(self) -> None:
        """Test basic put and get operations."""
        pq: PriorityQueueFIFO[str] = PriorityQueueFIFO()
        pq.put(1, "low")
        pq.put(2, "high")
        # Higher priority comes first
        assert pq.get() == "high"
        assert pq.get() == "low"

    def test_priority_queue_empty(self) -> None:
        """Test empty queue."""
        pq: PriorityQueueFIFO[str] = PriorityQueueFIFO()
        assert pq.empty() is True

    def test_priority_queue_not_empty(self) -> None:
        """Test non-empty queue."""
        pq: PriorityQueueFIFO[str] = PriorityQueueFIFO()
        pq.put(1, "item")
        assert pq.empty() is False

    def test_priority_queue_fifo_same_priority(self) -> None:
        """Test FIFO order for same priority items."""
        pq: PriorityQueueFIFO[str] = PriorityQueueFIFO()
        pq.put(1, "first")
        pq.put(1, "second")
        pq.put(1, "third")
        # Same priority, should come out in insertion order
        assert pq.get() == "first"
        assert pq.get() == "second"
        assert pq.get() == "third"

    def test_priority_queue_mixed_priorities(self) -> None:
        """Test mixed priorities."""
        pq: PriorityQueueFIFO[str] = PriorityQueueFIFO()
        pq.put(1, "low1")
        pq.put(3, "high")
        pq.put(1, "low2")
        pq.put(2, "medium")
        # Should come out: high, medium, low1, low2
        assert pq.get() == "high"
        assert pq.get() == "medium"
        assert pq.get() == "low1"
        assert pq.get() == "low2"

    def test_priority_queue_with_integers(self) -> None:
        """Test queue with integer items."""
        pq: PriorityQueueFIFO[int] = PriorityQueueFIFO()
        pq.put(1, 100)
        pq.put(2, 200)
        pq.put(1, 150)
        assert pq.get() == 200
        assert pq.get() == 100
        assert pq.get() == 150

    def test_priority_queue_becomes_empty(self) -> None:
        """Test queue becomes empty after getting all items."""
        pq: PriorityQueueFIFO[str] = PriorityQueueFIFO()
        pq.put(1, "a")
        pq.put(2, "b")
        assert pq.empty() is False
        pq.get()
        assert pq.empty() is False
        pq.get()
        assert pq.empty() is True

    def test_priority_queue_large_priorities(self) -> None:
        """Test with large priority values."""
        pq: PriorityQueueFIFO[str] = PriorityQueueFIFO()
        pq.put(1000000, "very_high")
        pq.put(1, "low")
        pq.put(500000, "medium")
        assert pq.get() == "very_high"
        assert pq.get() == "medium"
        assert pq.get() == "low"

    def test_priority_queue_negative_priorities(self) -> None:
        """Test with negative priority values."""
        pq: PriorityQueueFIFO[str] = PriorityQueueFIFO()
        pq.put(-1, "negative")
        pq.put(0, "zero")
        pq.put(1, "positive")
        # Higher value = higher priority
        assert pq.get() == "positive"
        assert pq.get() == "zero"
        assert pq.get() == "negative"
