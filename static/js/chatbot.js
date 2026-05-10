import { api } from "./api.js";

let mounted = false;

function mount() {
  const host = document.getElementById("chatbot-container");
  if (!host || mounted) return;
  mounted = true;
  host.innerHTML = `
    <button class="chatbot-fab" id="chatbot-fab" type="button" title="Ask SUMS AI">🤖</button>
    <div class="chatbot-window hidden" id="chatbot-window">
      <div class="chatbot-header">
        <div class="chatbot-avatar">🤖</div>
        <div class="chatbot-header-info">
          <h4>SUMS AI</h4>
          <p>Your university assistant</p>
        </div>
        <button class="chatbot-close" id="chatbot-close" type="button" aria-label="Close">✕</button>
      </div>
      <div class="chatbot-messages" id="chatbot-messages">
        <div class="chat-msg bot"><div class="chat-msg-bubble">👋 Hi! I'm SUMS AI. Ask me anything about courses, attendance, grades, or academic policies.</div></div>
      </div>
      <div class="chatbot-input">
        <input type="text" id="chatbot-input-field" placeholder="Type your question…" autocomplete="off" />
        <button class="chat-send-btn" id="chatbot-send" type="button">➤</button>
      </div>
    </div>
  `;

  const fab = document.getElementById("chatbot-fab");
  const win = document.getElementById("chatbot-window");
  const close = document.getElementById("chatbot-close");
  const send = document.getElementById("chatbot-send");
  const input = document.getElementById("chatbot-input-field");

  const toggle = () => {
    win.classList.toggle("hidden");
    if (!win.classList.contains("hidden")) input.focus();
  };

  fab.addEventListener("click", toggle);
  close.addEventListener("click", toggle);
  send.addEventListener("click", () => sendMsg());
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") sendMsg();
  });
}

function append(role, text) {
  const msgEl = document.getElementById("chatbot-messages");
  if (!msgEl) return;
  const el = document.createElement("div");
  el.className = `chat-msg ${role}`;
  el.innerHTML = `<div class="chat-msg-bubble">${text}</div>`;
  msgEl.appendChild(el);
  msgEl.scrollTop = msgEl.scrollHeight;
}

function typing() {
  const id = `typing-${Date.now()}`;
  const msgEl = document.getElementById("chatbot-messages");
  const el = document.createElement("div");
  el.className = "chat-msg bot";
  el.id = id;
  el.innerHTML = `<div class="chat-msg-bubble chat-typing"><span class="spinner spinner-sm"></span><span class="chat-typing-text">Thinking…</span></div>`;
  msgEl.appendChild(el);
  msgEl.scrollTop = msgEl.scrollHeight;
  return id;
}

function removeTyping(id) {
  document.getElementById(id)?.remove();
}

async function sendMsg() {
  const input = document.getElementById("chatbot-input-field");
  const text = input.value.trim();
  if (!text) return;
  input.value = "";
  append("user", text);
  const t = typing();
  try {
    const res = await api.ai.chatbot(text);
    removeTyping(t);
    append("bot", res.response || res.answer || "Got it.");
  } catch {
    removeTyping(t);
    append("bot", "⚠️ Unable to connect to SUMS AI. Please try again.");
  }
}

if (window.location.pathname !== "/login/" && window.location.pathname !== "/register/") {
  mount();
}

