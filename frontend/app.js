const API_BASE_URL = 'http://localhost:8000';
let sessionId = null;

const messagesContainer = document.getElementById('messages');
const queryInput = document.getElementById('query-input');
const sendBtn = document.getElementById('send-btn');
const traceContent = document.getElementById('trace-content');
const tracePanel = document.getElementById('trace-panel');
const toggleTraceBtn = document.getElementById('toggle-trace');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    queryInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    sendBtn.addEventListener('click', sendMessage);
    toggleTraceBtn.addEventListener('click', toggleTrace);

    // Example query click handlers
    document.querySelectorAll('.example-queries li').forEach(li => {
        li.addEventListener('click', () => {
            queryInput.value = li.textContent.replace(/[""]/g, '"');
            queryInput.focus();
        });
    });
});

function toggleTrace() {
    const isHidden = tracePanel.style.display === 'none';
    tracePanel.style.display = isHidden ? 'block' : 'none';
    toggleTraceBtn.textContent = isHidden ? 'Hide' : 'Show';
}

async function sendMessage() {
    const query = queryInput.value.trim();
    if (!query) return;

    // Disable input
    queryInput.disabled = true;
    sendBtn.disabled = true;

    // Add user message
    addMessage('user', query);
    queryInput.value = '';

    // Add loading indicator
    const loadingId = addMessage('assistant', '<div class="loading"></div>');

    // Add trace step
    addTraceStep('Analyzing query...');

    try {
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query,
                session_id: sessionId
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        // Update session ID
        if (data.session_id) {
            sessionId = data.session_id;
        }

        // Remove loading message
        removeMessage(loadingId);

        // Add assistant response
        let content = data.answer;

        if (data.visualization) {
            content += `<div class="visualization">
                <img src="data:image/png;base64,${data.visualization}" alt="Visualization">
            </div>`;
        }

        if (data.error) {
            content += `<div class="error-message">Error: ${data.error}</div>`;
        }

        addMessage('assistant', content);

        // Update trace
        if (data.sql_query) {
            addTraceStep(`SQL: ${data.sql_query}`);
        }
        addTraceStep('Response generated');

    } catch (error) {
        removeMessage(loadingId);
        addMessage('assistant', `<div class="error-message">Failed to process query: ${error.message}</div>`);
        addTraceStep(`Error: ${error.message}`);
    } finally {
        // Re-enable input
        queryInput.disabled = false;
        sendBtn.disabled = false;
        queryInput.focus();
    }
}

function addMessage(role, content) {
    const messageId = `msg-${Date.now()}`;
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    messageDiv.id = messageId;

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = role === 'user' ? 'U' : 'AI';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = content;

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(contentDiv);

    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    return messageId;
}

function removeMessage(messageId) {
    const messageElement = document.getElementById(messageId);
    if (messageElement) {
        messageElement.remove();
    }
}

function addTraceStep(step) {
    const stepDiv = document.createElement('div');
    stepDiv.className = 'trace-step';
    stepDiv.textContent = `[${new Date().toLocaleTimeString()}] ${step}`;
    traceContent.appendChild(stepDiv);
    traceContent.scrollTop = traceContent.scrollHeight;
}
