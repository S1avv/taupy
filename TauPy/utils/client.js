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
    });
    window._tauInputPatched = true;
}
