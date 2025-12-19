import uuid

class Component:
    _id_counter = 0

    def __init__(self, **kwargs):
        self.props = kwargs
        self.children = self.props.pop("children", []) or []

        self.app = None   

        provided_id = self.props.pop("id", None)
        if provided_id is not None:
            self.id = provided_id
        else:
            Component._id_counter += 1
            self.id = f"tau_{Component._id_counter}_{uuid.uuid4().hex[:6]}"

    async def update(self):
        """
        Re-render this component and send HTML to frontend.
        """
        if not self.app:
            print(f"[WARN] Component {self.id} has no app linked")
            return

        new_html = self.render()

        await self.app.server.broadcast({
            "type": "update_html",
            "id": self.id,
            "html": new_html
        })

    def render(self):
        return "".join(
            child.render() if isinstance(child, Component) else str(child)
            for child in self.children
        )

    def __repr__(self):
        return f"<{self.__class__.__name__} id={self.id}>"
