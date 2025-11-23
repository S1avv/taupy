import uuid

class Component:
    _id_counter = 0

    def __init__(self, **kwargs):
        self.props = kwargs
        self.children = self.props.pop("children", []) or []

        provided_id = self.props.pop("id", None)
        if provided_id is not None:
            self.id = provided_id
        else:
            Component._id_counter += 1
            self.id = f"tau_{Component._id_counter}_{uuid.uuid4().hex[:6]}"

    def render(self):
        rendered_children = "".join(
            child.render() if isinstance(child, Component) else str(child)
            for child in self.children
        )
        return rendered_children

    def __repr__(self):
        return f"<{self.__class__.__name__} id={self.id}>"
