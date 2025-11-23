from __future__ import annotations

from uuid import uuid4
from typing import Any, Dict, Type
from .component import Component as BaseComponent


def Component(template: str) -> Type[BaseComponent]:
    """
    Factory function that creates a custom template-based UI component.

    This allows users to define reusable widgets using plain HTML templates.
    The template may contain placeholders such as ``{prop}`` and a
    ``<children />`` or ``<slot />`` marker where child components will be injected.

    Example:
        >>> Card = Component(\"\"\"
        ...     <div class='card'>
        ...         <h2>{title}</h2>
        ...         <p>{subtitle}</p>
        ...         <children />
        ...     </div>
        ... \"\"\")
        >>> card = Card(title="Hello", subtitle="World")

    Parameters:
        template (str): HTML template string used to render the component.

    Returns:
        Type[BaseComponent]: A dynamically created subclass of ``Component``.
    """

    class TemplateComponent(BaseComponent):
        """Dynamically generated UI component based on a template."""

        def __init__(self, *children: BaseComponent, id: str | None = None, **props: Any) -> None:
            super().__init__(id=id, children=list(children), **props)

            self.template_props: Dict[str, Any] = props

            if self.id is None:
                self.id = f"cmp_{uuid4().hex[:8]}"

        def render(self) -> str:
            """
            Renders the component by injecting props and child components into the template.

            Returns:
                str: Rendered HTML string.
            """
            children_html = "".join(child.render() for child in self.children)

            html = template.format(**self.template_props)

            html = html.replace("<children />", children_html)
            html = html.replace("<slot />", children_html)

            return f"""
<div id="{self.id}" data-component-id="{self.id}">
    {html}
</div>
"""

    return TemplateComponent
