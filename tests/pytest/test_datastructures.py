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
