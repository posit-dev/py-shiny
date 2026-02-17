"""Tests for `shiny.datastructures`."""

from shiny._datastructures import PriorityQueueFIFO


def test_priority_queue_fifo():
    q: PriorityQueueFIFO[str] = PriorityQueueFIFO()

    # The random-seeming items are here to ensure that the value of the items
    # do not affect the order that they go into the queue.
    q.put(1, "9")
    q.put(1, "8")
    q.put(2, "6")
    q.put(2, "7")

    assert q.get() == "6"
    assert q.get() == "7"
    assert q.get() == "9"
    assert q.get() == "8"


class TestPriorityQueueFIFO:
    """Extended tests for the PriorityQueueFIFO class."""

    def test_empty_queue(self):
        """Test that a new queue is empty."""
        pq = PriorityQueueFIFO[int]()
        assert pq.empty() is True

    def test_put_single_item(self):
        """Test adding a single item to the queue."""
        pq = PriorityQueueFIFO[str]()
        pq.put(1, "item1")
        assert pq.empty() is False

    def test_get_single_item(self):
        """Test getting a single item from the queue."""
        pq = PriorityQueueFIFO[str]()
        pq.put(1, "item1")
        result = pq.get()
        assert result == "item1"
        assert pq.empty() is True

    def test_priority_order(self):
        """Test that higher priority items come out first."""
        pq = PriorityQueueFIFO[str]()
        pq.put(1, "low")
        pq.put(5, "high")
        pq.put(3, "medium")

        assert pq.get() == "high"
        assert pq.get() == "medium"
        assert pq.get() == "low"
        assert pq.empty() is True

    def test_fifo_order_same_priority(self):
        """Test that items with the same priority come out in FIFO order."""
        pq = PriorityQueueFIFO[str]()
        pq.put(1, "first")
        pq.put(1, "second")
        pq.put(1, "third")

        assert pq.get() == "first"
        assert pq.get() == "second"
        assert pq.get() == "third"
        assert pq.empty() is True

    def test_negative_priority(self):
        """Test that negative priorities work correctly."""
        pq = PriorityQueueFIFO[str]()
        pq.put(-5, "very_low")
        pq.put(0, "zero")
        pq.put(5, "high")

        assert pq.get() == "high"
        assert pq.get() == "zero"
        assert pq.get() == "very_low"

    def test_different_types(self):
        """Test queue with different value types."""
        # Test with integers
        pq_int = PriorityQueueFIFO[int]()
        pq_int.put(1, 42)
        assert pq_int.get() == 42

        # Test with lists
        pq_list = PriorityQueueFIFO[list[int]]()
        test_list: list[int] = [1, 2, 3]
        pq_list.put(1, test_list)
        assert pq_list.get() == test_list

        # Test with None values
        pq_none = PriorityQueueFIFO[None]()
        pq_none.put(1, None)
        assert pq_none.get() is None

    def test_put_after_get(self):
        """Test that we can add items after getting some."""
        pq = PriorityQueueFIFO[str]()
        pq.put(1, "first")
        assert pq.get() == "first"

        pq.put(1, "second")
        assert pq.get() == "second"

        assert pq.empty() is True

    def test_large_number_of_items(self):
        """Test adding many items to the queue maintains order."""
        pq = PriorityQueueFIFO[int]()

        # Add 50 items, all same priority
        for i in range(50):
            pq.put(0, i)

        # They should come out in insertion order (FIFO)
        for i in range(50):
            assert pq.get() == i

        assert pq.empty() is True
