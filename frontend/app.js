const CONFIG = {
  apiBaseUrl:
    window.APP_CONFIG?.API_BASE_URL?.replace(/\/$/, '') || 'http://localhost:8000',
  chatEndpoint: '/api/v1/chat',
  healthEndpoint: '/health',
  storageKey: 'agentic-planner-chat-history',
};

const elements = {
  messageContainer: document.getElementById('message-container'),
  chatForm: document.getElementById('chat-form'),
  chatInput: document.getElementById('chat-input'),
  sendButton: document.getElementById('send-button'),
  resetChat: document.getElementById('reset-chat'),
  healthIndicator: document.getElementById('health-indicator'),
  healthText: document.getElementById('health-text'),
  metaEndpoint: document.getElementById('meta-endpoint'),
  metaModel: document.getElementById('meta-model'),
  metaStatus: document.getElementById('meta-status'),
  messageTemplate: document.getElementById('message-template'),
};

const state = {
  messages: [],
  model: null,
  isSending: false,
  isHealthy: false,
};

function loadMessagesFromStorage() {
  try {
    const raw = window.localStorage.getItem(CONFIG.storageKey);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];
    return parsed.filter((item) => item?.role && item?.content);
  } catch (error) {
    console.warn('Konnte Gesprächsverlauf nicht laden:', error);
    return [];
  }
}

function saveMessagesToStorage(messages) {
  try {
    window.localStorage.setItem(CONFIG.storageKey, JSON.stringify(messages));
  } catch (error) {
    console.warn('Konnte Gesprächsverlauf nicht speichern:', error);
  }
}

function formatTime(date = new Date()) {
  return date.toLocaleTimeString('de-DE', {
    hour: '2-digit',
    minute: '2-digit',
  });
}

function createMessageElement(message) {
  const clone = elements.messageTemplate.content
    .cloneNode(true)
    .querySelector('.message');
  clone.classList.add(message.role);
  clone.querySelector('.message-role').textContent = message.role;
  clone.querySelector('.message-time').textContent =
    message.timestamp || formatTime();
  clone.querySelector('.message-content').textContent = message.content;
  if (message.role === 'error') {
    clone.classList.add('error');
  }
  return clone;
}

function renderMessages() {
  elements.messageContainer.innerHTML = '';
  const fragment = document.createDocumentFragment();

  if (!state.messages.length) {
    elements.messageContainer.classList.add('empty');
  } else {
    elements.messageContainer.classList.remove('empty');
    state.messages.forEach((message) => {
      fragment.appendChild(createMessageElement(message));
    });
  }

  elements.messageContainer.appendChild(fragment);
  scrollChatToBottom();
}

function appendMessage(message) {
  state.messages.push({ ...message, timestamp: message.timestamp || formatTime() });
  saveMessagesToStorage(state.messages);
  renderMessages();
}

function updateLatestAssistantMessage(content) {
  const last = state.messages[state.messages.length - 1];
  if (last && last.role === 'assistant') {
    last.content = content;
    saveMessagesToStorage(state.messages);
    renderMessages();
  }
}

function toggleSending(isSending) {
  state.isSending = isSending;
  elements.sendButton.disabled = isSending;
  elements.sendButton.textContent = isSending ? 'Sendet…' : 'Senden';
}

function scrollChatToBottom() {
  requestAnimationFrame(() => {
    elements.messageContainer.scrollTo({
      top: elements.messageContainer.scrollHeight,
      behavior: 'smooth',
    });
  });
}

async function checkHealth() {
  const healthUrl = `${CONFIG.apiBaseUrl}${CONFIG.healthEndpoint}`;
  elements.metaEndpoint.textContent = `${CONFIG.apiBaseUrl}${CONFIG.chatEndpoint}`;

  try {
    const response = await fetch(healthUrl, { method: 'GET' });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const payload = await response.json();
    state.isHealthy = payload.status === 'healthy';
    state.model = payload.model;

    updateHealthUI();
    return payload;
  } catch (error) {
    state.isHealthy = false;
    state.model = null;
    updateHealthUI(error);
    return null;
  }
}

function updateHealthUI(error) {
  if (state.isHealthy) {
    elements.healthIndicator.classList.add('ready');
    elements.healthIndicator.classList.remove('error');
    elements.healthText.textContent = 'Backend verbunden';
    elements.metaStatus.textContent = 'Healthy';
    elements.metaModel.textContent = state.model ?? 'Unbekannt';
  } else {
    elements.healthIndicator.classList.remove('ready');
    elements.healthIndicator.classList.add('error');
    elements.healthText.textContent = 'Backend nicht erreichbar';
    elements.metaStatus.textContent = 'Error';
    elements.metaModel.textContent = '–';
    if (error) {
      appendSystemMessage(
        `Fehler beim Health-Check (${error.message ?? 'unbekannt'}). Prüfe, ob das Backend auf ${CONFIG.apiBaseUrl} läuft.`,
        'error',
      );
    }
  }
}

function appendSystemMessage(content, role = 'system') {
  appendMessage({ role, content });
}

async function sendMessage(messageText) {
  if (!messageText.trim()) return;

  const userMessage = {
    role: 'user',
    content: messageText.trim(),
  };

  appendMessage(userMessage);
  toggleSending(true);
  elements.chatInput.value = '';
  autoResizeTextarea();

  const payload = {
    message: userMessage.content,
    conversation_history: state.messages
      .filter((msg, index) => index !== state.messages.length - 1)
      .filter((msg) => msg.role === 'user' || msg.role === 'assistant')
      .map((msg) => ({ role: msg.role, content: msg.content })),
  };

  const requestInit = {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  };

  appendMessage({ role: 'assistant', content: '…', timestamp: formatTime() });

  try {
    const response = await fetch(`${CONFIG.apiBaseUrl}${CONFIG.chatEndpoint}`, requestInit);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    updateLatestAssistantMessage(data.result ?? 'Keine Antwort erhalten.');
  } catch (error) {
    updateLatestAssistantMessage('Fehler bei der Verarbeitung.');
    appendSystemMessage(
      `Beim Senden der Nachricht ist ein Fehler aufgetreten: ${error.message ?? error}`,
      'error',
    );
  } finally {
    toggleSending(false);
  }
}

function autoResizeTextarea() {
  const el = elements.chatInput;
  el.style.height = 'auto';
  el.style.height = `${Math.min(el.scrollHeight, 240)}px`;
}

function setupEventListeners() {
  elements.chatForm.addEventListener('submit', (event) => {
    event.preventDefault();
    if (state.isSending) return;
    sendMessage(elements.chatInput.value);
  });

  elements.chatInput.addEventListener('keydown', (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      elements.chatForm.requestSubmit();
    }
  });

  elements.chatInput.addEventListener('input', autoResizeTextarea);

  elements.resetChat.addEventListener('click', () => {
    state.messages = [];
    saveMessagesToStorage([]);
    renderMessages();
    appendSystemMessage('Der Gesprächsverlauf wurde gelöscht.');
  });
}

function hydrateFromStorage() {
  state.messages = loadMessagesFromStorage();
  renderMessages();
}

async function bootstrap() {
  hydrateFromStorage();
  setupEventListeners();
  autoResizeTextarea();

  if (state.messages.length === 0) {
    appendSystemMessage('Hi! Ich plane deine Projekte Schritt für Schritt. Beschreibe dein Ziel.');
  }

  await checkHealth();
}

bootstrap();

