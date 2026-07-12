// MSME Sahayak - Frontend JavaScript
// Ye file chat functionality handle karti hai
// Messages bhejti hai API ko aur jawab dikhati hai

// DOM elements - ye sab HTML se hain
const messagesDiv = document.getElementById('messages');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');

// Chat history - purane messages yaad rakhne ke liye
// Isse AI ko context milta hai
let chatHistory = [];

// ==========================================
// Message send karo
// ==========================================

async function sendMessage() {
    // Input se message lo
    const message = userInput.value.trim();

    // Agar message empty hai toh kuch mat karo
    if (!message) return;

    // User ka message chat me dikhao
    addMessage(message, 'user');

    // Input box khali karo
    userInput.value = '';
    userInput.style.height = 'auto';

    // Send button disable karo (duplicate send rokne ke liye)
    sendBtn.disabled = true;

    // Loading dikhao
    const loadingMsg = addLoading();

    try {
        // API ko message bhejo
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                context: ''  // Future me context add kar sakte hain
            })
        });

        // Response parse karo
        const data = await response.json();

        // Loading hatao
        loadingMsg.remove();

        // AI ka jawab chat me dikhao
        addMessage(data.reply, 'bot');

        // Chat history me save karo
        chatHistory.push({ role: 'user', content: message });
        chatHistory.push({ role: 'assistant', content: data.reply });

    } catch (error) {
        // Agar API call fail ho jaye
        loadingMsg.remove();
        addMessage('Sorry, kuch gadbad ho gayi. Please try again.', 'bot');
        console.error('Chat error:', error);
    }

    // Send button wapas enable karo
    sendBtn.disabled = false;
    userInput.focus();
}

// ==========================================
// Feature buttons se message bhejo
// ==========================================

function sendFeature(message) {
    // Feature button pe click ho toh automatically message bhej do
    userInput.value = message;
    sendMessage();
}

// ==========================================
// Message chat area me add karo
// ==========================================

function addMessage(content, type) {
    // Naya message div banao
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message`;

    // Content me formatting karo (basic markdown support)
    let formattedContent = content
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')  // **bold**
        .replace(/\*(.*?)\*/g, '<em>$1</em>')              // *italic*
        .replace(/\n/g, '<br>');                             // newline

    // Agar bot hai toh "MSME Sahayak:" prefix lagao
    const prefix = type === 'bot' ? '<strong>MSME Sahayak:</strong> ' : '';

    messageDiv.innerHTML = `
        <div class="message-content">
            ${prefix}${formattedContent}
        </div>
    `;

    // Chat area me add karo
    messagesDiv.appendChild(messageDiv);

    // Neeche scroll karo (naye message pe)
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// ==========================================
// Loading indicator dikhao
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
// Enter key se message bhejo
// ==========================================

function handleKeyDown(event) {
    // Enter press kiya aur Shift nahi dabaaya toh message bhejo
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

// ==========================================
// Textarea auto-resize karo
// ==========================================

userInput.addEventListener('input', function() {
    // Text badhe toh box bhi badhe
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 120) + 'px';
});

// Page load pe input focus karo
userInput.focus();
