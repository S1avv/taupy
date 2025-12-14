# Layouts

TauPy ships with a handful of **layout containers** – thin wrappers powered by TailwindCSS utility classes and inspired by Flexbox. They let you compose both simple and sophisticated interfaces without touching CSS.

> **Quick reference**  
> • **`VStack`** – vertical stack  
> • **`HStack`** – horizontal stack  
> • **`Center`** – centers its children  
> • **`Container`** – padding & max-width wrapper  
> • **`Scroll`** – scrollable area  
> • **`Spacer`** – flexible filler

---

## 1. `VStack` – vertical stack

```python
from taupy.widgets.layout import VStack, Text, Button

ui = VStack(
    Text("Heading"),
    Button("OK"),
    spacing=4  # optional gap (Tailwind: gap-4)
)
```

`VSTACK` renders to `<div class="flex flex-col gap-2">…</div>`. Override the default classes with `class_="…"` or pass any additional HTML props (`id`, `style`, etc.).

---

## 2. `HStack` – horizontal stack

```python
from taupy.widgets.layout import HStack, Text, Button, Spacer

HStack(
    Text("Left"),
    Spacer(),
    Button("Right"),
)
```

By default `HStack` uses `flex flex-row gap-2`. Adding a `Spacer()` eats up the remaining horizontal space, pushing sibling widgets apart.

---

## 3. `Center` – absolute center

```python
from taupy.widgets.layout import Center, Text

Center(
    Text("Perfectly centered!"),
    class_="h-full"  # stretch container to fill the window height
)
```

`Center` applies `flex justify-center items-center`, aligning its children both horizontally and vertically.

---

## 4. `Container` – padding & fixed width

Use `Container` to wrap content with inner padding and limit its max width.

```python
from taupy.widgets.layout import Container, VStack, Text

Container(
    VStack(
        Text("Content card"),
        Text("More text…"),
    ),
    class_="max-w-xl mx-auto",  # center and constrain width
)
```

---

## 5. `Scroll` – scrollable area

`Scroll` adds `overflow-auto` and `max-h-full`, turning its children into a scrollable region.

```python
from taupy.widgets.layout import Scroll, Text

Scroll(
    *[Text(f"Line {i}") for i in range(100)]
)
```

---

## 6. `Spacer` – flexible filler

`Spacer()` consumes all remaining space along the main axis (`flex-grow`). Handy for separating widgets.

```python
HStack(
    Button("Back"),
    Spacer(),
    Button("Next"),
)
```

---

## 7. Combining containers

Layout containers are fully composable, allowing you to build elaborate structures:

```python
from taupy.widgets.layout import VStack, HStack, Container, Text, Button, Spacer, Scroll

ui = Container(
    VStack(
        Text("Page title", class_="text-2xl font-bold"),
        HStack(
            Button("Add"),
            Spacer(),
            Button("Save"),
        ),
        Scroll(
            *[Text(f"Item {i}") for i in range(50)]
        ),
    ),
    class_="max-w-2xl mx-auto p-6",
)
```

---

## 8. Tweaking spacing & styles

Every container accepts arbitrary HTML attributes. To add your own Tailwind classes, pass them via `class_` (note the trailing underscore—`class` is a reserved Python keyword):

```python
VStack(
    Text("Custom gap & bg"),
    class_="gap-8 bg-base-200 p-4 rounded-lg"
)
```

---

### See also
* [Widgets Overview](./overview.md)
* [State management](./state.md)
