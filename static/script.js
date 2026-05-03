/* ====================
CHAT (onclick send button)
==================== */
async function sendMessage() {

    // Get & format text input
    const input = document.getElementById("user-input");
    const message = input.value.trim();
    input.value = "";
    if (!message) return; // Return if empty

    // Get the selected personality
    const personality = document.getElementById("personality-select").value;

    // Append the message to the chat
    appendMessage("You", message, "user");

    // Request on /chat 
    const response = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: message, personality: personality })
    });

    // Get response & append it
    const data = await response.json();
    appendMessage("AI", data.reply, "ai");
}

/* ====================
APPEND TO CHAT HISTORY
==================== */
function appendMessage(senderName, message, cssClass) {
    const box = document.getElementById("chat-box");
    const div = document.createElement("div");
    div.className = `msg msg-${cssClass}`;
    div.innerHTML = `<strong>${senderName}:</strong> ${message}`;
    box.appendChild(div);
}

/* ====================
RESET SESSION
==================== */

document.addEventListener("DOMContentLoaded", resetSession);
async function resetSession() {
    try {
        // Call the backend reset route
        const response = await fetch('/reset', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();

        if (data.status === "success") {
            // Clear the chat box UI
            document.getElementById("chat-box").innerHTML = "";
            console.log("Session cleared successfully.");
        } else {
            console.error("Failed to clear session.");
        }
    } catch (error) {
        console.error("Error connecting to reset route:", error);
    }
}