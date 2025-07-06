document.addEventListener('DOMContentLoaded', () => {
    // --- Elementy DOM ---
    const form = document.getElementById('gemini-form');
    const questionInput = document.getElementById('question-input');
    const chatContainer = document.getElementById('chat-container');
    const newChatButton = document.getElementById('new-chat-button');
    const submitButton = document.getElementById('submit-button');

    // --- Stan aplikacji ---
    let chatHistory = [];

    // --- Główny Event Listener dla formularza ---
    form.addEventListener('submit', async (event) => {
        // Zapobiegaj domyślnemu przeładowaniu strony przez formularz
        event.preventDefault();

        const question = questionInput.value.trim();
        if (!question) {
            return; // Nie wysyłaj pustych pytań
        }

        // Zablokuj interfejs na czas przetwarzania
        setFormState(true);

        // Dodaj wiadomość użytkownika do UI i historii
        addUserMessageToUI(question);
        chatHistory.push({ role: 'user', parts: [{ text: question }] });

        // Wyczyść pole wprowadzania
        questionInput.value = '';
        questionInput.style.height = 'auto'; // Zresetuj wysokość textarea

        // Utwórz kontener na odpowiedź modelu
        const modelResponseDiv = addModelMessageToUI('');

        try {
            const response = await fetch('/gemini/ask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    question: question,
                    history: chatHistory,
                }),
            });

            if (!response.ok) {
                throw new Error(`Błąd serwera: ${response.status}`);
            }

            // Przetwarzaj odpowiedź strumieniową
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let modelResponseText = '';

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;
                const chunk = decoder.decode(value, { stream: true });
                modelResponseText += chunk;
                // Użyj DOMPurify do oczyszczenia i marked do renderowania Markdown
                modelResponseDiv.innerHTML = DOMPurify.sanitize(marked.parse(modelResponseText));
                // Podświetl składnię w blokach kodu
                modelResponseDiv.querySelectorAll('pre code').forEach(hljs.highlightElement);
                scrollToBottom();
            }

            // Zaktualizuj historię ostateczną odpowiedzią modelu
            chatHistory.push({ role: 'model', parts: [{ text: modelResponseText }] });

        } catch (error) {
            console.error('Błąd podczas komunikacji z API:', error);
            modelResponseDiv.innerHTML = `<p class="error">Wystąpił błąd. Spróbuj ponownie.</p>`;
        } finally {
            // Odblokuj interfejs po otrzymaniu odpowiedzi (nawet jeśli wystąpił błąd)
            setFormState(false);
        }
    });

    // --- Dodatkowe Event Listenery ---
    newChatButton.addEventListener('click', () => {
        chatContainer.innerHTML = '';
        chatHistory = [];
        questionInput.value = '';
        questionInput.focus();
    });

    questionInput.addEventListener('input', () => {
        questionInput.style.height = 'auto';
        questionInput.style.height = `${questionInput.scrollHeight}px`;
    });

    // --- Funkcje pomocnicze ---
    function setFormState(isSubmitting) {
        questionInput.disabled = isSubmitting;
        submitButton.disabled = isSubmitting;
        submitButton.textContent = isSubmitting ? 'Czekaj...' : 'Wyślij';
    }

    function addUserMessageToUI(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message user-message';
        // Zawsze oczyszczaj dane wejściowe przed wyświetleniem
        messageDiv.innerHTML = DOMPurify.sanitize(marked.parse(message));
        chatContainer.appendChild(messageDiv);
        scrollToBottom();
    }

    function addModelMessageToUI(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message model-message';
        messageDiv.innerHTML = message; // Początkowo puste, będzie wypełniane strumieniem
        chatContainer.appendChild(messageDiv);
        scrollToBottom();
        return messageDiv; // Zwróć element, aby można go było aktualizować
    }

    function scrollToBottom() {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
});