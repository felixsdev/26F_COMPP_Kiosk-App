/* ====================
CHAT FUNCTION (onclick send button)
==================== */
async function sendMessage() {

    // Get & format text input
    const input = document.getElementById("user-input");
    const message = input.value.trim();
    input.value = "";
    if (!message) return; // Return if empty

    // Append the message to the chat
    appendMessage("You", message, "user");

    // Request on /chat 
    const response = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message })
    });

    // Get response & append it
    const data = await response.json();
    appendMessage("AI", data.reply, "ai");
}

/* ====================
APPEND TO CHAT HISTORY FUNCTION
==================== */
function appendMessage(senderName, message, cssClass) {
    const box = document.getElementById("chat-box");
    const div = document.createElement("div");
    div.className = `msg msg-${cssClass}`;
    div.innerHTML = `<strong>${senderName}:</strong> ${message}`;
    box.appendChild(div);
}