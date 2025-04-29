const form = document.getElementById("chat-form");
const input = document.getElementById("chat-input");
const windowEl = document.getElementById("chat-window");
let thinkingIndicator = null;

function createMessageContainer() {
  const container = document.createElement("div");
  container.className = "message-container";
  windowEl.appendChild(container);
  return container;
}

function appendMessage(text, sender) {
  // Remove thinking indicator if it exists
  if (thinkingIndicator) {
    thinkingIndicator.remove();
    thinkingIndicator = null;
  }

  const container = createMessageContainer();
  const div = document.createElement("div");
  div.className = "message " + sender;
  div.textContent = text;
  container.appendChild(div);
  windowEl.scrollTop = windowEl.scrollHeight;
}

function showThinking() {
  const container = createMessageContainer();
  const thinking = document.createElement("div");
  thinking.className = "thinking";

  const dots = document.createElement("div");
  dots.className = "dot-typing";

  for (let i = 0; i < 3; i++) {
    const dot = document.createElement("div");
    dot.className = "dot";
    dots.appendChild(dot);
  }

  thinking.appendChild(dots);
  container.appendChild(thinking);
  thinkingIndicator = container;
  windowEl.scrollTop = windowEl.scrollHeight;
}

form.addEventListener("submit", e => {
  e.preventDefault();
  const msg = input.value.trim();
  if (!msg) return;

  // Disable input while processing
  input.disabled = true;
  const submitBtn = form.querySelector("button");
  submitBtn.disabled = true;

  // Add user message
  appendMessage(msg, "user");
  input.value = "";

  // Show thinking animation
  showThinking();

  // Send request to server
  fetch("/chat", {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({message: msg})
  })
  .then(r => r.json())
  .then(data => {
    // Remove thinking indicator and show response
    appendMessage(data.answer, "bot");
  })
  .catch(err => {
    appendMessage("Error: " + err, "bot");
  })
  .finally(() => {
    // Re-enable input
    input.disabled = false;
    submitBtn.disabled = false;
    input.focus();
  });
});

// Add welcome message and focus input on page load
window.addEventListener("load", () => {
  // Add welcome message from the bot
  appendMessage("Welcome to G.D. Goenka Public School, Vasant Kunj! I'm your virtual assistant. How can I help you today? Feel free to ask me anything about our school, programs, facilities, or admissions.", "bot");
  input.focus();
});
