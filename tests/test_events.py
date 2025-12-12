from taupy.events.events import Click, Input, Resize

def test_click_event():
    evt = Click("btn1")
    assert evt.type == "click"
    assert evt.widget_id == "btn1"

def test_input_event():
    evt = Input("inp", "abc")
    assert evt.type == "input"
    assert evt.value == "abc"

def test_resize_event():
    evt = Resize(800, 600)
    assert evt.type == "resize"
    assert evt.width == 800
    assert evt.height == 600
