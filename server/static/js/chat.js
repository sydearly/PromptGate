document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("chat-form");
    const textarea = document.getElementById("prompt");
    const output = document.getElementById("output");
    const logList = document.getElementById("log-list");

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const prompt = textarea.value.trim();
        if (!prompt) return;

        // Show user message
        const userMsg = document.createElement("div");
        userMsg.className = "pg-msg pg-msg--user";
        userMsg.textContent = prompt;
        output.appendChild(userMsg);
        output.scrollTop = output.scrollHeight;
        textarea.value = "";

        const startTime = Date.now();
        try {
            const res = await fetch("/api/chat", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({prompt}),
            });

            const elapsed = Date.now() - startTime;
            const li = document.createElement("li");
            li.innerHTML = `<time>${new Date().toLocaleTimeString()}</time> ${res.status} /api/chat ${elapsed}ms`;

            // Highlight rate limit hits
            if (res.status === 429) {
                li.style.color = "red";
                  li.innerHTML = `<time>${new Date().toLocaleTimeString()}</time> ${res.status} Rate limit reached — please wait a few seconds before sending another message. /api/chat ${elapsed}ms`;
            } else {
                li.style.color = "black";
            }
            logList.prepend(li);

            const data = await res.json();

            if (res.status === 429) {
                li.style.color = "red";

                const rateMsg = document.createElement("div");
                rateMsg.className = "pg-msg pg-msg--ai";
                rateMsg.style.color = "red";
                rateMsg.textContent =
                    data.error || "Rate limit reached — please wait a few seconds before sending another message.";

                output.appendChild(rateMsg);
                output.scrollTop = output.scrollHeight;
            }

            if (!res.ok) {
                const errMsg = document.createElement("div");
                errMsg.className = "pg-msg pg-msg--ai";
                errMsg.style.color = "red";
                errMsg.textContent = data.error || "An error occurred.";
                output.appendChild(errMsg);
                output.scrollTop = output.scrollHeight;
                return;
            }

            // Normal AI response
            const aiMsg = document.createElement("div");
            aiMsg.className = "pg-msg pg-msg--ai";
            aiMsg.textContent = data.response;
            output.appendChild(aiMsg);
            output.scrollTop = output.scrollHeight;
        } catch (err) {
            console.error(err);
        }
    });
});
