const btn = document.getElementById("send-btn");
const countEl = document.getElementById("sent-count");

let sentCount = 0;

if (btn) {
    btn.addEventListener("click", () => {
        sentCount += 1;
        if (countEl) {
            countEl.textContent = String(sentCount);
        }
    });
}
