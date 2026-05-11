// ====================
// SEND MESSAGE (triggered by buttons)

async function sendMessage(text) {
    // clear the options to prevent doubleclicks and show loading
    const optionsArea = document.getElementById("options-area");
    optionsArea.innerHTML = `<div class="loading-indicator">thinking...</div>`;

    // get personality
    const personality = document.getElementById("ai-persona").value;
    // append the clicked option to the chat except when its the start
    if (text !== "start") {
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
            appendMessage("AI", `<strong>${data.product_name}</strong><br>${data.message} `, "ai");
            const optionsArea = document.getElementById("options-area");
            optionsArea.innerHTML = `
                <button class="chat-option-btn is-green" onclick="checkout('${data.product_id}')">Perfect!</button>
                <button class="chat-option-btn is-red" onclick="declineProduct('${data.product_id}')">I need something else...</button>
            `;
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
        // start chat automatically
        if (data.status === "success") {
            document.getElementById("chat-box").innerHTML = "";
            document.getElementById("options-area").innerHTML = "";
            sendMessage('start');
        }
    } catch (error) {
        console.error("failed to reset", error);
    }
}

// ====================
// CHECKOUT

async function checkout(productId) {
    try {
        await fetch('/increment_sold', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ product_id: productId })
        });
    } catch (error) {
        console.error("Failed to increment sold count", error);
    }
    window.location.href = `/checkout.html?item_id=${productId}`;
}

// ====================
// DECLINE PRODUCT

async function declineProduct(productId) {
    try {
        await fetch('/increment_declined', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ product_id: productId })
        });
    } catch (error) {
        console.error("Failed to increment declined count", error);
    }
    sendMessage('Declined');
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
        btn.className = "chat-option-btn";
        btn.onclick = () => sendMessage(optText);
        optionsArea.appendChild(btn);
    });
    scrollToBottom();
}

// ====================
// APPEND TO CHAT HISTORY

function appendMessage(senderName, message, cssClass) {
    const box = document.getElementById("chat-box");
    const div = document.createElement("div");
    div.className = `chat-message chat-message--${cssClass}`;
    div.innerHTML = `<strong>${senderName}:</strong> ${message}`;
    box.appendChild(div);
    scrollToBottom();
}

// ====================
// SCROLL TO BOTTOM

function scrollToBottom() {
    const chatBox = document.getElementById("chat-box");
    chatBox.scrollTop = chatBox.scrollHeight;
}