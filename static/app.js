let token = localStorage.getItem("token");
let isAdmin = localStorage.getItem("is_admin") === "true";
const sessionId = localStorage.getItem("session_id") || crypto.randomUUID();
localStorage.setItem("session_id", sessionId);

if (token) showChat();

async function login() {
    const name = document.getElementById("name").value.trim();
    const password = document.getElementById("password").value.trim();

    const res = await fetch("/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, password })
    });

    if (!res.ok) {
        document.getElementById("login-error").style.display = "block";
        return;
    }

    const data = await res.json();
    token = data.token;
    isAdmin = data.is_admin;
    localStorage.setItem("token", token);
    localStorage.setItem("is_admin", isAdmin);
    showChat();
}

async function logout() {
    await fetch("/logout", {
        method: "POST",
        headers: { "Authorization": `Bearer ${token}` }
    });
    localStorage.removeItem("token");
    localStorage.removeItem("is_admin");
    location.reload();
}

function showChat() {
    document.getElementById("login-screen").style.display = "none";
    document.getElementById("chat-screen").style.display = "block";
    document.getElementById("user-label").textContent = isAdmin ? "Administrator" : "Restricted Access";
}

async function sendMessage() {
    const input = document.getElementById("user-input");
    const message = input.value.trim();
    if (!message) return;

    addMessage("User: " + message, "user");
    input.value = "";

    const res = await fetch("/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ message, session_id: sessionId })
    });

    if (res.status === 401) {
        addMessage("Session expired. Please log in again.", "bot");
        localStorage.removeItem("token");
        setTimeout(() => location.reload(), 2000);
        return;
    }

    const data = await res.json();
    addMessage("AI Assistant: " + data.reply, "bot");
}

function addMessage(text, who) {
    const div = document.getElementById("messages");
    div.innerHTML += `<div class="${who}"><span>${text}</span></div>`;
    div.scrollTop = div.scrollHeight;
}

document.getElementById("user-input")?.addEventListener("keydown", e => {
    if (e.key === "Enter") sendMessage();
});

document.getElementById("password")?.addEventListener("keydown", e => {
    if (e.key === "Enter") login();
});