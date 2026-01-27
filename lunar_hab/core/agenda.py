__all__ = ["Agenda"]


from typing import Callable
from collections import deque as Queue
from sortedcontainers import SortedDict


class Agenda(object):
    """
    An agenda object.
    """

    def __init__(self):
        self._todo = SortedDict()

    @property
    def current_time(self) -> float:
        """Get the current time.

        Precondition: The todo is not empty.
        """
        return next(iter(self.todo.keys()))

    @property
    def todo(self) -> dict:
        """Get the todo dictionary."""
        return self._todo

    def empty(self) -> bool:
        """Check if the todo is empty."""
        return not self.todo

    def make_new_todo(self, time):
        """Makes a new todo item for time `time`.

        Precondition: There isn't such an item yet.
        """
        self.todo[time] = Queue()

    def add(self, time : float, event : Callable):
        if time not in self.todo:
            self.make_new_todo(time)
        self.todo[time].appendleft(event)

    def forward(self):
        """Run all events in the current timestep."""
        ct = self.current_time
        # current_events = next(iter(self.todo.values()))
        current_events: Queue = self.todo[ct]
        while current_events:
            event = current_events.pop()
            event()
        del self.todo[ct]
