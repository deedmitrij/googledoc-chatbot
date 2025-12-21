document.addEventListener("DOMContentLoaded", function () {
    const chatBox = document.getElementById("chat-box");
    const userInput = document.getElementById("user-input");
    const sendBtn = document.getElementById("send-btn");

    function getUserId() {
        let userId = sessionStorage.getItem("user_id");
        if (!userId) {
            userId = crypto.randomUUID();
            sessionStorage.setItem("user_id", userId);
        }
        return userId;
    }

    const userId = getUserId();

    appendMessage("Bot: Welcome! Please provide a Google Doc link to the specification.", "bot");

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
            body: JSON.stringify({ user_id: userId, message: userMessage }),
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
        messageDiv.classList.add("message", sender);

        const textDiv = document.createElement("div");
        textDiv.classList.add("text");
        textDiv.innerHTML = message;

        messageDiv.appendChild(textDiv);
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
