import asyncio
from TauPy.app import App
from TauPy.widgets import VStack, Text, Button
from TauPy.events import Click

app = App("New TauPy App", 800, 600)

@app.route("/")
def home():
    return VStack(
        Text("Hello from TauPy!"),
        Button("Click me", id="btn"),
    )

@app.dispatcher.on_click("btn")
async def click_btn(_: Click):
    print("clicked!")

async def main():
    root = VStack(id="main")
    await app.run(root)

if __name__ == "__main__":
    asyncio.run(main())