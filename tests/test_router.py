from taupy.router import Router


def test_router_register_and_get():
    r = Router()

    def handler():
        return "OK"

    r.register("/", handler)

    assert r.get("/") is handler
    assert r.get("/404") is None
