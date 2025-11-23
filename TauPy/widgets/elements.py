from __future__ import annotations
from typing import Any, Callable, Iterable, List, Optional
from .component import Component
import shutil
import os


def _props_to_str(props: dict[str, Any]) -> str:
    return " ".join(f'{k}="{v}"' for k, v in props.items())


class Div_(Component):
    """A generic HTML <div> container."""

    def render(self) -> str:
        children_html = super().render()
        return (
            f'<div id="{self.id}" {_props_to_str(self.props)} '
            f'data-component-id="{self.id}">{children_html}</div>'
        )


class Button_(Component):
    """
    A clickable button component.

    Parameters:
        text (str): Display text on the button.
        id (str, optional): Unique identifier.
        on_click (Callable, optional): Event handler for click.
        children (list[Component], optional): Not used by Button but kept for consistency.
        **props: Additional HTML attributes.
    """

    def __init__(
        self,
        text: str,
        id: Optional[str] = None,
        on_click: Optional[Callable] = None,
        children: Optional[List[Component]] = None,
        **props: Any
    ) -> None:
        super().__init__(id=id, children=children, **props)
        self.text = text
        self.on_click = on_click

    def render(self) -> str:
        return (
            f'<button class="btn" id="{self.id}" '
            f'data-component-id="{self.id}">{self.text}</button>'
        )


class Input_(Component):
    """
    A text input field.

    Parameters:
        value (str | Callable): Initial or reactive value.
        placeholder (str): Placeholder text.
        id (str, optional): Unique ID.
        on_input (Callable, optional): Input handler.
        **props: HTML attributes.
    """

    def __init__(
        self,
        value: str | Callable[[], str] = "",
        placeholder: str = "",
        id: Optional[str] = None,
        on_input: Optional[Callable] = None,
        **props: Any
    ) -> None:
        super().__init__(id=id, **props)
        self.value = value
        self.placeholder = placeholder
        self.on_input = on_input

    def render(self) -> str:
        value_str = self.value() if callable(self.value) else self.value
        props_str = _props_to_str(self.props)

        return (
            f'<input class="input" id="{self.id}" value="{value_str}" '
            f'placeholder="{self.placeholder}" {props_str} '
            f'data-component-id="{self.id}" />'
        )


class Text_(Component):
    """
    Text component. Supports static and reactive content.

    Parameters:
        value (str | Callable): Text or reactive function.
        **kwargs: Additional props.
    """

    def __init__(
        self,
        value: str | Callable[[], str],
        **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self.value = value

    def render(self) -> str:
        display_value = self.value() if callable(self.value) else self.value
        return (
            f'<span class="text" type="text" id="{self.id}" '
            f'{_props_to_str(self.props)} data-component-id="{self.id}">'
            f'{display_value}</span>'
        )


class Table_(Component):
    """
    A table component.

    Parameters:
        head (list[str], optional): Table header labels.
        rows (list[list[str]], optional): Table body rows.
        id (str, optional): Unique ID.
        **props: Additional HTML attributes.
    """

    def __init__(
        self,
        head: Optional[list[str]] = None,
        rows: Optional[list[list[Any]]] = None,
        id: Optional[str] = None,
        **props: Any
    ) -> None:
        super().__init__(id=id, **props)
        self.head = head or []
        self.rows = rows or []

    def render(self) -> str:
        props = _props_to_str(self.props)

        thead_html = ""
        if self.head:
            ths = "".join(f"<th>{col}</th>" for col in self.head)
            thead_html = f"<thead><tr><th></th>{ths}</tr></thead>"

        tbody_rows = []
        for index, row in enumerate(self.rows, start=1):
            cells = "".join(f"<td>{cell}</td>" for cell in row)
            tbody_rows.append(f"<tr><th>{index}</th>{cells}</tr>")
        tbody_html = "<tbody>" + "".join(tbody_rows) + "</tbody>"

        return (
            f'<div class="overflow-x-auto">'
            f'  <table class="table" id="{self.id}" {props} '
            f'data-component-id="{self.id}">'
            f'    {thead_html}'
            f'    {tbody_html}'
            f'  </table>'
            f'</div>'
        )


class Image_(Component):
    """
    An image component.

    Automatically copies local files into `dist/public/`.

    Parameters:
        src (str): Path or URL.
        alt (str): Alternative text.
        id (str, optional): Unique ID.
        width (int | str, optional): Image width.
        height (int | str, optional): Image height.
        **props: Additional HTML attributes.
    """

    def __init__(
        self,
        src: str,
        alt: str = "",
        id: Optional[str] = None,
        width: Optional[int | str] = None,
        height: Optional[int | str] = None,
        **props: Any
    ) -> None:
        super().__init__(id=id, **props)

        if os.path.isfile(src):
            os.makedirs("dist/public", exist_ok=True)
            filename = os.path.basename(src)
            shutil.copy(src, os.path.join("dist/public", filename))
            self.src = f"dist/public/{filename}"
        else:
            self.src = src

        self.alt = alt
        self.width = width
        self.height = height

    def render(self) -> str:
        attrs = [
            f'src="{self.src}"',
            f'alt="{self.alt}"'
        ]

        if self.width:
            attrs.append(f'width="{self.width}"')
        if self.height:
            attrs.append(f'height="{self.height}"')

        for k, v in self.props.items():
            attrs.append(f'{k}="{v}"')

        if self.id:
            attrs.append(f'id="{self.id}"')
            attrs.append(f'data-component-id="{self.id}"')

        return f"<img {' '.join(attrs)} />"

def Div(*children: Component, **kwargs: Any) -> Div_:
    return Div_(children=list(children), **kwargs)


def Button(text: str, **kwargs: Any) -> Button_:
    return Button_(text, **kwargs)


def Text(value: str | Callable[[], str], **kwargs: Any) -> Text_:
    return Text_(value, **kwargs)


def Input(value: str | Callable[[], str] = "", placeholder: str = "", **kwargs: Any) -> Input_:
    return Input_(value, placeholder=placeholder, **kwargs)


def Table(head: Optional[list[str]] = None, rows: Optional[list[list[Any]]] = None, **kwargs: Any) -> Table_:
    return Table_(head=head, rows=rows, **kwargs)


def Image(src: str, **props: Any) -> Image_:
    return Image_(src, **props)
