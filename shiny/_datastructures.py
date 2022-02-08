from typing import TypeVar, Generic
from queue import PriorityQueue


T = TypeVar("T")


class PriorityQueueFIFO(Generic[T]):
    """
    Similar to queue.PriorityQueue, except that if two elements have the same
    priority, they are returned in the order they were inserted. Also, the item
    is kept separate from the priority value (with PriorityQueue, the priority
    is part of the item).
    """

    def __init__(self) -> None:
        self._pq: PriorityQueue[tuple[int, int, T]] = PriorityQueue()
        self._counter: int = 0

    def put(self, priority: int, item: T) -> None:
        """
        Add an item to the queue.

        Parameters:
           priority (int): The priority of the item. Higher priority items will
                           come out of the queue before lower priority items.
           item (T): The item to put in the queue.
        """
        self._counter += 1
        self._pq.put((-priority, self._counter, item))

    def get(self) -> T:
        return self._pq.get()[2]

    def empty(self) -> bool:
        return self._pq.empty()
