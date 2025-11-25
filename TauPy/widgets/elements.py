from __future__ import annotations
from typing import Any, Callable, List, Optional
from .component import Component
import shutil
import os
import asyncio

def _normalize_props(props: dict[str, Any]) -> dict[str, Any]:
    """Convert class_ → class and drop Nones."""
    out = {}
    for k, v in props.items():
        if v is None:
            continue
        if k == "class_":
            out["class"] = v
        else:
            out[k] = v
    return out


def _props_to_str(props: dict[str, Any]) -> str:
    out = []
    for k, v in props.items():
        if v is None:
            continue

        if k.startswith("data_"):
            k = "data-" + k[5:]

        out.append(f'{k}="{v}"')

    return " ".join(out)

class Modal_(Component):
    """
    DaisyUI modal. Controlled via State[bool].
    """

    def __init__(
        self,
        open_state,
        *,
        id: Optional[str] = None,
        title: Optional[str] = None,
        content: Optional[List[Component]] = None,
        actions: Optional[List[Component]] = None,
        **props
    ):
        super().__init__(id=id, **props)

        self.state = open_state
        self.title = title
        self.content = content or []
        self.actions = actions or []

        def on_state_change(_):
            asyncio.create_task(self.update())

        self.state.subscribe(on_state_change)

    def render(self) -> str:
        is_open = bool(self.state())

        checked_attr = "checked" if is_open else ""
        props_str = _props_to_str(self.props)

        content_html = "".join(c.render() for c in self.content)
        actions_html = "".join(c.render() for c in self.actions)

        title_html = (
            f'<h3 class="text-lg font-bold">{self.title}</h3>'
            if self.title else ""
        )

        return f"""
<input type="checkbox" id="{self.id}" class="modal-toggle" {checked_attr} />

<div class="modal">
  <div class="modal-box" {props_str}>
    {title_html}
    <div class="py-4">
      {content_html}
    </div>
    <div class="modal-action">
      {actions_html}
      <label for="{self.id}" class="btn">Close</label>
    </div>
  </div>
</div>
"""

class Div_(Component):
    def render(self) -> str:
        props_str = _props_to_str(self.props)
        children = super().render()
        return f'<div id="{self.id}" {props_str} data-component-id="{self.id}">{children}</div>'


class Button_(Component):
    def __init__(self, text: str, **props):
        super().__init__(**props)
        self.text = text
        

    def render(self) -> str:
        props_str = _props_to_str(self.props)
        return (
            f'<button id="{self.id}" class="btn" {props_str} '
            f'data-component-id="{self.id}">{self.text}</button>'
        )


class Input_(Component):
    def __init__(self, value="", placeholder="", on_input=None, **props):
        super().__init__(**props)
        self.value = value
        self.placeholder = placeholder
        self.on_input = on_input

    def render(self) -> str:
        v = self.value() if callable(self.value) else self.value
        props_str = _props_to_str(self.props)

        return (
            f'<input id="{self.id}" value="{v}" placeholder="{self.placeholder}" '
            f'class="input" {props_str} data-component-id="{self.id}" />'
        )


class Text_(Component):
    def __init__(self, value, **props):
        super().__init__(**props)
        self.value = value

    def render(self) -> str:
        text = self.value() if callable(self.value) else self.value
        props_str = _props_to_str(self.props)

        return (
            f'<span id="{self.id}" {props_str} data-component-id="{self.id}">{text}</span>'
        )


class Table_(Component):
    def __init__(self, head=None, rows=None, **props):
        super().__init__(**props)
        self.head = head or []
        self.rows = rows or []

    def render(self) -> str:
        props_str = _props_to_str(self.props)

        thead = ""
        if self.head:
            ths = "".join(f"<th>{c}</th>" for c in self.head)
            thead = f"<thead><tr><th></th>{ths}</tr></thead>"

        rows_html = []
        for i, row in enumerate(self.rows, start=1):
            tds = "".join(f"<td>{c}</td>" for c in row)
            rows_html.append(f"<tr><th>{i}</th>{tds}</tr>")
        tbody = "<tbody>" + "".join(rows_html) + "</tbody>"

        return (
            f'<div class="overflow-x-auto">'
            f'  <table id="{self.id}" {props_str} class="table" data-component-id="{self.id}">'
            f'    {thead}'
            f'    {tbody}'
            f'  </table>'
            f'</div>'
        )


class Image_(Component):
    def __init__(self, src, alt="", width=None, height=None, **props):
        super().__init__(**props)

        if os.path.isfile(src):
            os.makedirs("dist/public", exist_ok=True)
            name = os.path.basename(src)
            shutil.copy(src, f"dist/public/{name}")
            self.src = f"dist/public/{name}"
        else:
            self.src = src

        self.alt = alt
        self.width = width
        self.height = height

    def render(self) -> str:
        props_str = _props_to_str(self.props)

        attrs = [
            f'src="{self.src}"',
            f'alt="{self.alt}"'
        ]
        if self.width: attrs.append(f'width="{self.width}"')
        if self.height: attrs.append(f'height="{self.height}"')

        attrs = " ".join(attrs)

        return (
            f'<img id="{self.id}" {attrs} {props_str} data-component-id="{self.id}" />'
        )


def Div(*children, style: str | None = None, **props):
    return Div_(children=list(children), style=style, **props)

def Button(text: str, style: str | None = None, **props):
    return Button_(text, style=style, **props)

def Text(value, style: str | None = None, **props):
    return Text_(value, style=style, **props)

def Input(value="", placeholder="", style: str | None = None, **props):
    return Input_(value, placeholder=placeholder, style=style, **props)

def Table(head=None, rows=None, style: str | None = None, **props):
    return Table_(head=head, rows=rows, style=style, **props)

def Image(src, style: str | None = None, **props):
    return Image_(src, style=style, **props)

def Modal(open_state, style: str | None = None, **props):
    return Modal_(open_state=open_state, style=style, **props)