from taupy.widgets.layout import HStack, VStack, Container


def test_hstack_render():
    layout = HStack()
    html = layout.render()
    assert "flex flex-row" in html


def test_vstack_render():
    layout = VStack()
    html = layout.render()
    assert "flex flex-col" in html


def test_container_render():
    html = Container().render()
    assert "p-4" in html
