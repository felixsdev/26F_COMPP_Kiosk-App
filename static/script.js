// ====================
// SEND MESSAGE (triggered by buttons)

async function sendMessage(text) {
    // clear the options to prevent doubleclicks
    document.getElementById("options-area").innerHTML = "";
    // get personality
    const personality = document.getElementById("personality-select").value;
    // append the clicked option to the chat except when its the start button
    if (text !== "Start") {
        appendMessage("You", text, "user");
    }
    // 
    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ 
                message: text, 
                personality: personality
            })
        });
        // get response & check if result or question
        const data = await response.json();
        if (data.product_id && data.product_name) {
            appendMessage("AI", `Perfect! Based on your answers, I recommend: <strong>${data.product_name}</strong>`, "ai");
        } else {
            appendMessage("AI", data.message, "ai");
            renderOptions(data.options);
        }
    } catch (error) {
        console.error("Chat error:", error);
    }
}

// ====================
// RESET SESSION & INITIALIZE

document.addEventListener("DOMContentLoaded", resetSession);
async function resetSession() {
    try {
        const response = await fetch('/reset', {
            method: 'POST',
        });
        const data = await response.json();
        // render the start button
        if (data.status === "success") {
            document.getElementById("chat-box").innerHTML = "";
            document.getElementById("options-area").innerHTML = `
                <button class="option-btn start-btn" onclick="sendMessage('Start')">Start Session</button>
            `;
        }
    } catch (error) {
        console.error("failed to reset", error);
    }
}

// ====================
// RENDER DYNAMIC BUTTONS

function renderOptions(optionsArray) {
    const optionsArea = document.getElementById("options-area");
    optionsArea.innerHTML = "";
    if (!optionsArray || optionsArray.length === 0) return;
    optionsArray.forEach(optText => {
        const btn = document.createElement("button");
        btn.innerText = optText;
        btn.className = "option-btn";
        btn.onclick = () => sendMessage(optText);
        optionsArea.appendChild(btn);
    });
}

// ====================
// APPEND TO CHAT HISTORY

function appendMessage(senderName, message, cssClass) {
    const box = document.getElementById("chat-box");
    const div = document.createElement("div");
    div.className = `msg msg-${cssClass}`;
    div.innerHTML = `<strong>${senderName}:</strong> ${message}`;
    box.appendChild(div);
}