from __future__ import annotations

from typing import Optional


class Event:
    """
    Base class for all UI events in TauPy.

    Parameters:
        type (str): Logical event type (e.g., "click", "input", "resize").
        widget_id (Optional[str]): ID of the component that triggered the event.
    """

    def __init__(self, type: str, widget_id: Optional[str] = None) -> None:
        self.type = type
        self.widget_id = widget_id


class Click(Event):
    """
    Event triggered when a component is clicked.

    Parameters:
        widget_id (str): ID of the clicked component.
    """

    def __init__(self, widget_id: str) -> None:
        super().__init__("click", widget_id)


class Input(Event):
    """
    Event triggered when an <Input> component changes text.

    Parameters:
        widget_id (str): ID of the input component.
        value (str): The new value entered by the user.
    """

    def __init__(self, widget_id: str, value: str) -> None:
        super().__init__("input", widget_id)
        self.value = value


class Resize(Event):
    """
    Event triggered when the window changes dimensions.

    Parameters:
        width (int): New window width in pixels.
        height (int): New window height in pixels.
    """

    def __init__(self, width: int, height: int) -> None:
        super().__init__("resize")
        self.width = width
        self.height = height
