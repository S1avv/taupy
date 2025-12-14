let socket = new WebSocket("ws://localhost:8765");

socket.onopen = () => {
    console.log("Connected to TauPy backend");
};

socket.onmessage = (event) => {
    const msg = JSON.parse(event.data);

    if (msg.type === "update_text") {
        const el = document.getElementById(msg.id);
        if (el) el.textContent = msg.value;
    }

    if (msg.type === "replace") {
        const el = document.getElementById(msg.id);
        if (el) {
            el.innerHTML = msg.html;
        }
    }

    if (msg.type === "set_theme") {
        document.documentElement.setAttribute("data-theme", msg.theme);
        localStorage.setItem("theme", msg.theme);
    }

    if (msg.type === "hot_reload") {
        location.reload();
    }

    if (msg.type === "update_html") {
        const el = document.getElementById(msg.id);
        if (el) {
            el.outerHTML = msg.html;
        }
    }

};

document.addEventListener("click", evt => {
    const target = evt.target;

    if (target.dataset.componentId) {
        socket.send(JSON.stringify({
            type: "click",
            id: target.dataset.componentId
        }));
    }
});

document.addEventListener("input", evt => {
    const target = evt.target;

    if (target.dataset.componentId) {
        socket.send(JSON.stringify({
            type: "input",
            id: target.dataset.componentId,
            value: target.value
        }));
    }
});

if (!window._tauInputPatched) {
    socket.addEventListener("message", event => {
        const msg = JSON.parse(event.data);
        if (msg.type === "update_input") {
            const el = document.getElementById(msg.id);
            if (el) el.value = msg.value;
        }
        if (msg.type === "window_cmd") {
            if (window.taupyNative && typeof window.taupyNative.send === "function") {
                window.taupyNative.send(msg.command || msg.payload || {});
            }
        }
    });
    window._tauInputPatched = true;
}

if (!window._tauWindowBridgePatched) {
    if (window.taupyNative && typeof window.taupyNative.onEvent === "function") {
        window.taupyNative.onEvent((evt) => {
            socket.send(JSON.stringify({ type: "window_event", name: evt.type, payload: evt }));
        });
    }
    window._tauWindowBridgePatched = true;
}
