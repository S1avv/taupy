import asyncio
from TauPy import App, AppMode

app = App(
    "New TauPy App",
    800,
    600,
    mode=AppMode.RAW_HTML,
    http_port=8000,
    external_http=False,
)


@app.dispatcher.on_click("taupy-sample")
async def handle_test_event(_):
    print("Received test event from frontend")


async def main():
    await app.run()


if __name__ == "__main__":
    asyncio.run(main())
