import asyncio
from taupy import App, AppMode, VStack, Text, Button
from taupy.events import Click

app = App("New TauPy App", 800, 600, mode=AppMode.GENERATE_HTML)


@app.route("/")
def home():
    return VStack(
        Text("Hello from TauPy!"),
        Button("Click me", id="btn"),
        id="main",
    )


@app.dispatcher.on_click("btn")
async def click_btn(_: Click):
    print("clicked!")


async def main():
    root = VStack(id="root")
    await app.run(root)


if __name__ == "__main__":
    asyncio.run(main())
