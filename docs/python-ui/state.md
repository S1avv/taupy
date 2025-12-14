# State Management

TauPy ships with a tiny but powerful reactive core inspired by hooks in React and signals in Solid JS. This page dives into the two main primitives-`State` and `DerivedState`-and shows patterns for structuring state in real-world apps.

---

## 1. `State` – the mutable atom

```python
from taupy.state import State

count = State(0)          # create reactive value

count.value += 1          # mutate → schedules re-render for dependants
print(count.value)        # 1
```

* `State(initial)` wraps any Python value.
* Reading `.value` **subscribes** the calling widget/effect to updates.
* Assigning to `.value` marks the state as changed and triggers a re-render of any widget that accessed it during the last layout pass.

### When to use
• Local component data (input contents, toggles)  
• Transient UI flags (modals, dropdown open/closed)  
• Data frequently updated by user events

---

## 2. `DerivedState` – computed values

`DerivedState` derives its value from other states. It memoises the result and only recomputes when dependencies change.

```python
from taupy.state import State, DerivedState

net = State(100)
vat = 0.2

gross = DerivedState(lambda: net.value * (1 + vat), deps=[net])
```

`gross.value` automatically stays in sync with `net.value` and causes no extra renders when unchanged.

---

## 3. Subscribing to state changes

TauPy's current API lets you subscribe any callback to a `State` object. The callback fires every time the value changes.

```python
from taupy.state import State

query = State("")

# Attach side-effect

def on_query_change(value):
    if value:
        print("Searching for", value)

query.subscribe(on_query_change)

# Somewhere else in your code
query.set("hello")  # -> prints "Searching for hello"
```

> **Note**  
> A first-class `@effect` decorator is on the roadmap, but for now you can use `state.subscribe()` to run side effects when data changes.

---

## 4. Async state updates

Changing `State` **never blocks** the UI thread. For async work, mark the handler as `async def` and await your coroutines:

```python
results = State([])

async def reload():
    data = await fetch_data()
    results.value = data
```

TauPy schedules the coroutine and updates the UI when it finishes.

---

## 5. Lifting state up

When multiple components need to share data, lift the `State` creation to their closest common parent and pass it down:

```python
total = State(0)

# parent.py
VStack(
    CartList(total_state=total),
    CheckoutButton(total_state=total),
)
```

---

## 6. Contexts (coming soon)

For global app-level data (theme, user session) TauPy will ship `create_context()` in the near future. Until then, keep such objects in a top-level module and import them where needed.

---

## 7. Tips & gotchas
1. Avoid expensive computations inside render functions-move them to `DerivedState`.  
2. Never mutate nested objects in-place (`state.value.append(x)`)-instead assign a new list (`state.value = state.value + [x]`).  
3. For large collections, store data in plain Python lists/sets and expose only the required aggregated info via `DerivedState`.  
4. Batch multiple updates in one tick by mutating several states within the same handler; TauPy coalesces renders.

---

### Further reading
* [Python UI Overview](./overview.md)
* [API Reference](./api.md)
