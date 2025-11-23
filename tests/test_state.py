from TauPy.state import State

def test_state_basic():
    s = State(10)
    assert s() == 10

    s.set(20)
    assert s() == 20


def test_state_subscribe():
    s = State(0)
    called = []

    def on_change(val):
        called.append(val)

    s.subscribe(on_change)
    s.set(5)

    assert called == [5]
