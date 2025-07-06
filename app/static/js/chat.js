const form = document.getElementById('gemini-form');
const questionInput = document.getElementById('question-input');
const chatContainer = document.getElementById('chat-container');
const submitButton = document.getElementById('submit-button');
const newChatButton = document.getElementById('new-chat-button');
const HISTORY_KEY = 'geminiChatHistory';

let conversationHistory = [];

questionInput.addEventListener('keydown', (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        form.dispatchEvent(new Event('submit'));
    }
});

// Auto-resize textarea
questionInput.addEventListener('input', () => {
    questionInput.style.height = 'auto';
    questionInput.style.height = (questionInput.scrollHeight) + 'px';
});

newChatButton.addEventListener('click', () => {
    if (confirm('Czy na pewno chcesz rozpocząć nowy czat? Obecna historia zostanie usunięta.')) {
        conversationHistory = [];
        localStorage.removeItem(HISTORY_KEY);
        chatContainer.innerHTML = '';
        questionInput.focus();
    }
});

form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const question = questionInput.value.trim();
    if (!question) return;

    displayMessage(question, 'user');
    conversationHistory.push({ role: 'user', parts: [question] });
    questionInput.value = '';
    questionInput.style.height = 'auto'; // Reset height after sending
    
    submitButton.disabled = true;

    const modelMessageElement = displayMessage('', 'model');
    let fullModelResponse = '';
    let firstChunkReceived = false;

    try {
        // Używamy ścieżki względnej. Przeglądarka automatycznie
        // użyje tej samej domeny i portu, z której serwowana jest strona.
        // To najlepsza praktyka, która działa zarówno lokalnie, jak i w Cloud Shell.
        const response = await fetch('/gemini/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question, history: conversationHistory }),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value, { stream: true });
            if (!firstChunkReceived && chunk) {
                firstChunkReceived = true;
                modelMessageElement.innerHTML = ''; // Clear the typing indicator
            }

            fullModelResponse += chunk;
            renderModelMessage(fullModelResponse, modelMessageElement);
            chatContainer.scrollTop = chatContainer.scrollHeight; // Scroll after render
        }
    } catch (error) {
        modelMessageElement.textContent = `Wystąpił błąd: ${error.message}`;
        console.error('Fetch error:', error);
    } finally {
        if (fullModelResponse) {
            conversationHistory.push({ role: 'model', parts: [fullModelResponse] });
            saveHistory();
        }
        submitButton.disabled = false;
        questionInput.focus();
    }
});

function displayMessage(text, type) {
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', `${type}-message`);
    if (type === 'user') {
        messageElement.textContent = text;
    } else {
        // For model messages, show a typing indicator
        messageElement.innerHTML = `
            <div class="typing-indicator">
                <span></span><span></span><span></span>
            </div>
        `;
    }
    chatContainer.appendChild(messageElement);
    chatContainer.scrollTop = chatContainer.scrollHeight;
    return messageElement;
}

function renderModelMessage(text, element) {
    // Parse Markdown and sanitize the HTML for security before displaying
    const dirtyHtml = marked.parse(text);
    element.innerHTML = DOMPurify.sanitize(dirtyHtml);
    // After rendering, enhance the code blocks with highlighting and copy buttons
    enhanceCodeBlocks(element);
}

function enhanceCodeBlocks(element) {
    const codeBlocks = element.querySelectorAll('pre');
    codeBlocks.forEach(pre => {
        const code = pre.querySelector('code');
        if (code) {
            // Apply syntax highlighting
            hljs.highlightElement(code);
        }

        // Create and add the copy button
        const copyButton = document.createElement('button');
        copyButton.textContent = 'Kopiuj';
        copyButton.className = 'copy-code-button';

        copyButton.addEventListener('click', () => {
            const codeToCopy = code ? code.innerText : pre.innerText;
            navigator.clipboard.writeText(codeToCopy).then(() => {
                copyButton.textContent = 'Skopiowano!';
                setTimeout(() => {
                    copyButton.textContent = 'Kopiuj';
                }, 2000);
            }).catch(err => console.error('Błąd kopiowania:', err));
        });

        pre.appendChild(copyButton);
    });
}

function saveHistory() {
    localStorage.setItem(HISTORY_KEY, JSON.stringify(conversationHistory));
}

function loadHistory() {
    const savedHistory = localStorage.getItem(HISTORY_KEY);
    if (savedHistory) {
        try {
            conversationHistory = JSON.parse(savedHistory);
            chatContainer.innerHTML = '';
            conversationHistory.forEach(message => {
                const messageElement = document.createElement('div');
                messageElement.classList.add('message', `${message.role}-message`);
                if (message.role === 'user') {
                    messageElement.textContent = message.parts[0];
                } else { // 'model'
                    renderModelMessage(message.parts[0], messageElement);
                }
                chatContainer.appendChild(messageElement);
            });
            chatContainer.scrollTop = chatContainer.scrollHeight;
        } catch (e) {
            console.error("Błąd podczas wczytywania historii czatu:", e);
            localStorage.removeItem(HISTORY_KEY); // Clear corrupted history
        }
    }
}

// Load history on page start
loadHistory();