document.addEventListener("DOMContentLoaded", function () {
    const chatBox = document.getElementById("chat-box");
    const userInput = document.getElementById("user-input");
    const sendBtn = document.getElementById("send-btn");

    function getUserId() {
        let userId = localStorage.getItem("user_id");
        if (!userId) {
            userId = crypto.randomUUID();
            localStorage.setItem("user_id", userId);
        }
        return userId;
    }

    const userId = getUserId();
    let lastSender = null;

    appendMessage("Welcome! Please provide a Google Doc link to the specification.", "bot");

    sendBtn.addEventListener("click", sendMessage);
    userInput.addEventListener("keypress", function (event) {
        if (event.key === "Enter") {
            sendMessage();
        }
    });

    function sendMessage() {
        const userMessage = userInput.value.trim();
        if (!userMessage) return;

        appendMessage(userMessage, "user");
        userInput.value = "";

        fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ user_id: userId, message: userMessage }),
        })
        .then(response => response.json())
        .then(data => {
            appendMessage(data.response, "bot");
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

        if (sender !== lastSender) {
            const senderLabel = document.createElement("div");
            senderLabel.classList.add("sender-label");
            senderLabel.textContent = sender === "bot" ? "Bot" : "You";
            messageDiv.appendChild(senderLabel);
        } else {
            messageDiv.classList.add("consecutive");
        }

        const textDiv = document.createElement("div");
        textDiv.classList.add("text");
        textDiv.innerHTML = linkify(message);

        const timestamp = document.createElement("div");
        timestamp.classList.add("timestamp");
        timestamp.textContent = new Date().toLocaleTimeString();

        messageDiv.appendChild(textDiv);
        messageDiv.appendChild(timestamp);

        chatBox.appendChild(messageDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
        lastSender = sender;
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

    function linkify(text) {
        // This regex looks for URLs starting with http/https or www.
        // It also handles URLs without protocol but containing a domain.
        const urlPattern = /((https?:\/\/|www\.)[\w\-]+(\.[\w\-]+)+[\w\-.,@?^=%&:/~+#]*[\w\-@?^=%&/~+#])|([a-zA-Z0-9.\-]+(?:\.[a-zA-Z]{2,})(?:[\w\-.,@?^=%&:/~+#]*[\w\-@?^=%&/~+#]))/gi;

        return text.replace(urlPattern, url => {
            // Check if the URL already starts with http:// or https://
            let fullUrl = url;
            if (!url.match(/^(https?:\/\/)/i)) {
                // If it starts with www., add http://
                if (url.match(/^www\./i)) {
                    fullUrl = `http://${url}`;
                } else if (url.match(/^[a-zA-Z0-9.\-]+(?:\.[a-zA-Z]{2,})/)) {
                    // For bare domains like example.com, add http://
                    fullUrl = `http://${url}`;
                }
            }
            return `<a href="${fullUrl}" target="_blank" rel="noopener noreferrer">${url}</a>`;
        });
    }
});
