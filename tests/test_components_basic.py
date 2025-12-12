from taupy.widgets.elements import Text_, Button_, Input_

def test_text_static():
    t = Text_("Hello")
    html = t.render()
    assert "Hello" in html

def test_text_dynamic():
    x = 5
    t = Text_(lambda: f"Val={x}")
    assert "Val=5" in t.render()

def test_button_render():
    b = Button_("Click", id="btn")
    html = b.render()
    assert "Click" in html
    assert 'id="btn"' in html

def test_input_render():
    i = Input_("test", placeholder="Enter")
    html = i.render()
    assert 'value="test"' in html
    assert 'placeholder="Enter"' in html
