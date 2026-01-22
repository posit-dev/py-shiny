"""Tests for shiny._datastructures module."""

from shiny._datastructures import PriorityQueueFIFO


class TestPriorityQueueFIFO:
    """Tests for PriorityQueueFIFO class."""

    def test_empty_queue(self) -> None:
        """Test empty queue is empty."""
        queue: PriorityQueueFIFO[str] = PriorityQueueFIFO()
        assert queue.empty() is True

    def test_put_and_get_single(self) -> None:
        """Test putting and getting a single item."""
        queue: PriorityQueueFIFO[str] = PriorityQueueFIFO()
        queue.put(1, "item1")
        assert queue.empty() is False
        result = queue.get()
        assert result == "item1"

    def test_priority_order(self) -> None:
        """Test items are returned in priority order (higher first)."""
        queue: PriorityQueueFIFO[str] = PriorityQueueFIFO()
        queue.put(1, "low")
        queue.put(10, "high")
        queue.put(5, "medium")

        assert queue.get() == "high"
        assert queue.get() == "medium"
        assert queue.get() == "low"

    def test_fifo_same_priority(self) -> None:
        """Test FIFO order for same priority items."""
        queue: PriorityQueueFIFO[str] = PriorityQueueFIFO()
        queue.put(1, "first")
        queue.put(1, "second")
        queue.put(1, "third")

        assert queue.get() == "first"
        assert queue.get() == "second"
        assert queue.get() == "third"

    def test_mixed_priorities_fifo(self) -> None:
        """Test mixed priorities with FIFO for same priority."""
        queue: PriorityQueueFIFO[str] = PriorityQueueFIFO()
        queue.put(2, "p2_first")
        queue.put(1, "p1_first")
        queue.put(2, "p2_second")
        queue.put(1, "p1_second")

        assert queue.get() == "p2_first"
        assert queue.get() == "p2_second"
        assert queue.get() == "p1_first"
        assert queue.get() == "p1_second"

    def test_negative_priority(self) -> None:
        """Test negative priority values."""
        queue: PriorityQueueFIFO[str] = PriorityQueueFIFO()
        queue.put(0, "zero")
        queue.put(10, "high")
        queue.put(-10, "negative")

        assert queue.get() == "high"
        assert queue.get() == "zero"
        assert queue.get() == "negative"

    def test_different_types(self) -> None:
        """Test queue with different value types."""
        queue: PriorityQueueFIFO[int] = PriorityQueueFIFO()
        queue.put(2, 42)
        queue.put(1, 100)

        assert queue.get() == 42
        assert queue.get() == 100

    def test_queue_reuse(self) -> None:
        """Test queue can be reused after emptying."""
        queue: PriorityQueueFIFO[str] = PriorityQueueFIFO()
        queue.put(1, "first")
        queue.get()
        assert queue.empty() is True

        queue.put(1, "second")
        assert queue.empty() is False
        assert queue.get() == "second"

    def test_large_number_of_items(self) -> None:
        """Test queue with many items."""
        queue: PriorityQueueFIFO[int] = PriorityQueueFIFO()
        for i in range(100):
            queue.put(i, i)

        # Items should come out in order 99, 98, 97, ... (highest priority first)
        for i in range(100):
            assert queue.get() == 99 - i

    def test_empty_method(self) -> None:
        """Test empty method returns correct values."""
        queue: PriorityQueueFIFO[str] = PriorityQueueFIFO()
        assert queue.empty() is True

        queue.put(1, "item")
        assert queue.empty() is False

        queue.get()
        assert queue.empty() is True

    def test_zero_priority(self) -> None:
        """Test zero priority value."""
        queue: PriorityQueueFIFO[str] = PriorityQueueFIFO()
        queue.put(0, "zero")
        queue.put(1, "positive")
        queue.put(-1, "negative")

        assert queue.get() == "positive"
        assert queue.get() == "zero"
        assert queue.get() == "negative"

    def test_list_as_item(self) -> None:
        """Test queue with list items."""
        queue: PriorityQueueFIFO[list[int]] = PriorityQueueFIFO()
        queue.put(1, [1, 2, 3])
        queue.put(2, [4, 5, 6])

        assert queue.get() == [4, 5, 6]
        assert queue.get() == [1, 2, 3]

    def test_none_as_item(self) -> None:
        """Test queue with None items."""
        queue: PriorityQueueFIFO[None] = PriorityQueueFIFO()
        queue.put(1, None)
        assert queue.get() is None
