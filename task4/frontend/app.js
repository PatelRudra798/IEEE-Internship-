// app.js – Handles chat UI interactions and communication with backend

const chatList = document.getElementById('chat-list');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');

// Append a message bubble to the chat list
function addMessage(content, type) {
  const li = document.createElement('li');
  li.className = type === 'user' ? 'user-msg' : 'bot-msg';
  const span = document.createElement('span');
  span.textContent = content;
  li.appendChild(span);
  chatList.appendChild(li);
  // Auto‑scroll to latest message
  chatList.scrollTop = chatList.scrollHeight;
}

// Send user message to backend
async function sendMessage() {
  const message = userInput.value.trim();
  if (!message) return;
  addMessage(message, 'user');
  userInput.value = '';
  userInput.disabled = true;
  sendBtn.disabled = true;

  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message })
    });
    const data = await response.json();
    addMessage(data.response, 'bot');
  } catch (err) {
    console.error(err);
    addMessage('Error: unable to reach the server.', 'bot');
  } finally {
    userInput.disabled = false;
    sendBtn.disabled = false;
    userInput.focus();
  }
}

sendBtn.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

// Auto‑grow textarea
userInput.addEventListener('input', () => {
  userInput.style.height = 'auto';
  userInput.style.height = userInput.scrollHeight + 'px';
});
