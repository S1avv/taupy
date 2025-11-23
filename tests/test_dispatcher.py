import pytest
from TauPy.dispatcher import Dispatcher
from TauPy.events.events import Click, Input

@pytest.mark.asyncio
async def test_dispatch_click():
    dp = Dispatcher()
    clicked = []

    @dp.on_click("btn")
    async def handler(evt):
        clicked.append(evt.widget_id)

    await dp.dispatch_click("btn")

    assert clicked == ["btn"]


@pytest.mark.asyncio
async def test_dispatch_input():
    dp = Dispatcher()
    results = []

    @dp.on_input("field")
    async def handler(evt):
        results.append(evt.value)

    await dp.dispatch_input("field", "hello")

    assert results == ["hello"]
