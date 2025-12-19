from __future__ import annotations

from typing import Any
from .component import Component


def _props_to_str(props: dict[str, Any]) -> str:
    return " ".join(f'{k}="{v}"' for k, v in props.items())


class HStack(Component):
    """
    A horizontal layout container that arranges child components in a row.

    Tailwind:
        flex flex-row gap-2
    """

    def __init__(self, *children: Component, **props: Any) -> None:
        props.setdefault("class", "flex flex-row gap-2")
        super().__init__(children=list(children), **props)

    def render(self) -> str:
        children_html = super().render()
        props = _props_to_str(self.props)
        id_attr = f'id="{self.id}"' if self.id else ""
        data_attr = f'data-component-id="{self.id}"' if self.id else ""
        return f"<div {id_attr} {props} {data_attr}>{children_html}</div>"


class VStack(Component):
    """
    A vertical layout container that arranges child components in a column.

    Tailwind:
        flex flex-col gap-2
    """

    def __init__(self, *children: Component, **props: Any) -> None:
        props.setdefault("class", "flex flex-col gap-2")
        super().__init__(children=list(children), **props)

    def render(self) -> str:
        children_html = super().render()
        props = _props_to_str(self.props)
        id_attr = f'id="{self.id}"' if self.id else ""
        data_attr = f'data-component-id="{self.id}"' if self.id else ""
        return f"<div {id_attr} {props} {data_attr}>{children_html}</div>"


class Center(Component):
    """
    A layout container that centers its content both vertically and horizontally.

    Tailwind:
        flex justify-center items-center
    """

    def __init__(self, *children: Component, **props: Any) -> None:
        props.setdefault("class", "flex justify-center items-center")
        super().__init__(children=list(children), **props)

    def render(self) -> str:
        children_html = super().render()
        props = _props_to_str(self.props)
        id_attr = f'id="{self.id}"' if self.id else ""
        return f'<div {id_attr} {props} data-component-id="{self.id}">{children_html}</div>'


class Container(Component):
    """
    A padded container used for page sections or structured blocks.

    Tailwind:
        p-4
    """

    def __init__(self, *children: Component, **props: Any) -> None:
        props.setdefault("class", "p-4")
        super().__init__(children=list(children), **props)

    def render(self) -> str:
        children_html = super().render()
        props = _props_to_str(self.props)
        id_attr = f'id="{self.id}"' if self.id else ""
        return f'<div {id_attr} {props} data-component-id="{self.id}">{children_html}</div>'


class Scroll(Component):
    """
    A scrollable container with a max height constraint.

    Tailwind:
        overflow-auto max-h-full
    """

    def __init__(self, *children: Component, **props: Any) -> None:
        props.setdefault("class", "overflow-auto max-h-full")
        super().__init__(children=list(children), **props)

    def render(self) -> str:
        children_html = super().render()
        props = _props_to_str(self.props)
        id_attr = f'id="{self.id}"' if self.id else ""
        return f'<div {id_attr} {props} data-component-id="{self.id}">{children_html}</div>'


class Spacer(Component):
    """
    A flexible layout element that expands to fill available space.

    Tailwind:
        flex-grow
    """

    def __init__(self, **props: Any) -> None:
        props.setdefault("class", "flex-grow")
        super().__init__(children=[], **props)

    def render(self) -> str:
        props = _props_to_str(self.props)
        id_attr = f'id="{self.id}"' if self.id else ""
        data_attr = f'data-component-id="{self.id}"' if self.id else ""
        return f"<div {id_attr} {props} {data_attr}></div>"
