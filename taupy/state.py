from __future__ import annotations
from typing import Any, Callable, List


class State:
    """
    Reactive state container used by TauPy.

    `State` stores a value and automatically notifies all subscribed
    UI bindings whenever the value is updated. It powers the reactive
    update system used by components such as `Text`.

    The state behaves like a callable:
        count = State(0)
        print(count())  # -> 0
    """

    def __init__(self, initial_value: Any) -> None:
        """
        Initialize a new reactive state.

        Parameters:
            initial_value (Any): The initial stored value.
        """
        self._value: Any = initial_value
        self._subscribers: List[Callable[[Any], None]] = []

    def __call__(self) -> Any:
        """
        Return the current state value.

        Returns:
            Any: The stored value.
        """
        return self._value

    def set(self, new_value: Any) -> None:
        """
        Update the stored value and notify subscribers if the value changes.

        Parameters:
            new_value (Any): The new value to store.
        """
        if self._value != new_value:
            self._value = new_value
            self._notify_subscribers()

    def subscribe(self, callback: Callable[[Any], None]) -> None:
        """
        Subscribe a callback to state changes.

        Parameters:
            callback (Callable[[Any], None]):
                A function that will be called with the updated value.
        """
        self._subscribers.append(callback)

    def unsubscribe(self, callback: Callable[[Any], None]) -> None:
        """
        Remove a previously added subscriber.

        Parameters:
            callback (Callable[[Any], None]): The subscriber to remove.
        """
        try:
            self._subscribers.remove(callback)
        except ValueError:
            pass

    def _notify_subscribers(self) -> None:
        """
        Notify all subscribers about the updated value.
        Internal - should not be called manually.
        """
        for callback in list(self._subscribers):
            callback(self._value)
