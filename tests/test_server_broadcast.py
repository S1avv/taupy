import pytest
from taupy.server import TauServer
from taupy.app import App


@pytest.mark.asyncio
async def test_broadcast_no_clients():
    app = App("Test", 800, 600)
    server = TauServer(app)

    # should not crash with 0 clients
    await server.broadcast({"hello": 123})
