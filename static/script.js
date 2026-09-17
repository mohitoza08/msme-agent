// MSME Sahayak - Frontend JavaScript
// Handles all chat interactions: sends messages to the API,
// renders replies and manages the plan for the server.
// DOM elements - references to the HTML controls
const messagesDiv = document.getElementById('messages');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const apiKeyInput = document.getElementById('apiKeyInput');
const keyStatus = document.getElementById('keyStatus');

// Chat history - keeps prior messages so the AI has context
let chatHistory = [];

// Selected response language - affects the AI's replies
let appLanguage = 'hinglish';  // 'hinglish' or 'english'

// ==========================================
// Language selection (modal + storage)
// ==========================================

function setLanguage(lang) {
    appLanguage = (lang === 'english') ? 'english' : 'hinglish';
    localStorage.setItem('msme_language', appLanguage);
}

function chooseLanguage(lang) {
    setLanguage(lang);
    const modal = document.getElementById('langModal');
    if (modal) modal.classList.remove('active');
}

// Load the saved language (if any) but always show the chooser popup
(function initLanguage() {
    const savedLang = localStorage.getItem('msme_language');
    if (savedLang === 'english' || savedLang === 'hinglish') {
        appLanguage = savedLang;
    }
    const modal = document.getElementById('langModal');
    if (modal) modal.classList.add('active');
})();

// ==========================================
// BYOK user-provided Groq API key
// ==========================================

// Load a previously saved key from localStorage when the page loads
(function loadSavedKey() {
    const saved = localStorage.getItem('msme_api_key') || '';
    if (apiKeyInput && saved) {
        apiKeyInput.value = saved;
        setKeyStatus('Key saved (unused)');
    }
})();

function getApiKey() {
    // Use the key from the input field, falling back to localStorage
    if (apiKeyInput && apiKeyInput.value.trim()) return apiKeyInput.value.trim();
    return localStorage.getItem('msme_api_key') || null;
}

function saveApiKey() {
    const key = apiKeyInput ? apiKeyInput.value.trim() : '';
    if (!key) {
        localStorage.removeItem('msme_api_key');
        setKeyStatus('Key removed');
        return;
    }
    if (!/^gsk_/.test(key)) {
        setKeyStatus('Invalid key - gsk_ se shuru hona chahiye', true);
        return;
    }
    localStorage.setItem('msme_api_key', key);
    setKeyStatus('Key saved');
}

function setKeyStatus(text, isError) {
    if (!keyStatus) return;
    keyStatus.textContent = text;
    keyStatus.style.color = isError ? '#f87171' : '#4ade80';
}

// ==========================================
// Send a message
// ==========================================

async function sendMessage() {
    // Read the message from the input
    const message = userInput.value.trim();

    // Do nothing if the message is empty
    if (!message) return;

    // Show the user's message in the chat
    addMessage(message, 'user');

    // Clear the input field
    userInput.value = '';
    userInput.style.height = 'auto';

    // Disable the send button to prevent duplicate submissions
    sendBtn.disabled = true;

    // Show the loading indicator
    const loadingMsg = addLoading();

    try {
        // Send the message to the API
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                context: '',  // Reserved for future context injection
                language: appLanguage,  // Response language: Hinglish or English
                api_key: getApiKey()  // BYOK - the user's own key
            })
        });

        // Parse the JSON response
        const data = await response.json();

        // Remove the loading indicator
        loadingMsg.remove();

        // Show the AI's reply in the chat
        addMessage(data.reply, 'bot');

        // Save this exchange to the chat history
        chatHistory.push({ role: 'user', content: message });
        chatHistory.push({ role: 'assistant', content: data.reply });

    } catch (error) {
        // Handle a failed API call
        loadingMsg.remove();
        addMessage('Sorry, kuch gadbad ho gayi. Please try again.', 'bot');
        console.error('Chat error:', error);
    }

    // Re-enable the send button
    sendBtn.disabled = false;
    userInput.focus();
}

// ==========================================
// Send a message from a feature button
// ==========================================

function sendFeature(message) {
    // Fill the input and trigger a send when a feature button is clicked
    userInput.value = message;
    sendMessage();
}

// ==========================================
// Add a message to the chat area
// ==========================================

function addMessage(content, type) {
    // Create a new message element
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message`;

    // Render Markdown to HTML with marked.js, then sanitize with DOMPurify
    let rendered = content;
    if (typeof marked !== 'undefined' && typeof marked.parse === 'function'
        && typeof DOMPurify !== 'undefined') {
        rendered = DOMPurify.sanitize(marked.parse(content));
    }

    // Prefix bot messages with the assistant name
    const prefix = type === 'bot' ? '<span class="bot-prefix">MSME Sahayak</span>' : '';

    messageDiv.innerHTML = `
        <div class="message-content">
            ${prefix}${rendered}
        </div>
    `;

    // Append the message to the chat area
    messagesDiv.appendChild(messageDiv);

    // Scroll to the bottom so the newest message is visible
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// ==========================================
// Show the loading indicator
// ==========================================

function addLoading() {
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message bot-message loading active';
    loadingDiv.innerHTML = '<div class="message-content">Thinking...</div>';
    messagesDiv.appendChild(loadingDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
    return loadingDiv;
}

// ==========================================
// Send a message with the Enter key
// ==========================================

function handleKeyDown(event) {
    // Enter pressed without Shift sends the message
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

// ==========================================
// Auto-resize the textarea
// ==========================================

userInput.addEventListener('input', function() {
    // Grow the box as the text grows
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 120) + 'px';
});

// Focus the input on page load
userInput.focus();
