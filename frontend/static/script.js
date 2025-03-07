document.addEventListener("DOMContentLoaded", function () {
    const chatBox = document.getElementById("chat-box");
    const userInput = document.getElementById("user-input");
    const sendBtn = document.getElementById("send-btn");

    appendMessage("Bot: Welcome! Please provide a Google Doc link to get started.", "bot");

    sendBtn.addEventListener("click", sendMessage);
    userInput.addEventListener("keypress", function (event) {
        if (event.key === "Enter") {
            sendMessage();
        }
    });

    function sendMessage() {
        const userMessage = userInput.value.trim();
        if (!userMessage) return;

        appendMessage("You: " + userMessage, "user");
        userInput.value = "";

        fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ user_id: "test_user", message: userMessage }),
        })
        .then(response => response.json())
        .then(data => {
            appendMessage("Bot: " + data.response, "bot");
            if (data.menu) {
                appendMenuOptions(data.menu);
            }
            if (data.reset) {
            setTimeout(resetChat, 2000);
            }
        })
        .catch(error => console.error("Error:", error));
    }

    function appendMessage(message, sender) {
        const messageDiv = document.createElement("div");
        messageDiv.classList.add(sender);
        messageDiv.innerHTML = message;
        chatBox.appendChild(messageDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    function appendMenuOptions(options) {
    const menuDiv = document.createElement("div");
    menuDiv.classList.add("menu-options");

    options.forEach(option => {
        const button = document.createElement("button");
        button.textContent = option;

        button.addEventListener("click", function () {
            userInput.value = option;
            sendMessage();
        });

        menuDiv.appendChild(button);
    });

    chatBox.appendChild(menuDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
    }

    function resetChat() {
    location.reload();
    }
});
