// Replace the existing callAPI function in your HTML with this:
async function callAPI(message) {
    try {
        // Call your Flask backend instead of external APIs directly
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Server request failed');
        }
        
        const data = await response.json();
        hideTypingIndicator();
        displayTypingResponse(data.reply);
        
    } catch (error) {
        hideTypingIndicator();
        finishGeneration();
        showNotification(`Error: ${error.message}`, 'error');
        console.error('API Error:', error);
    }
}

// Also remove or comment out these functions since you won't need them:
// - callOpenAI()
// - callAnthropic() 
// - callGoogle()
// - callCustomAPI()

// Simplify the sendMessage function - remove API settings check:
function sendMessage() {
    const input = document.getElementById('messageInput');
    const message = input.value.trim();
    
    if (message && !isGenerating) {
        addMessage(message, true);
        input.value = '';
        input.style.height = 'auto';
        updateCharCount();
        
        // Add to chat history
        if (!chatHistory.find(chat => chat.id === currentChatId)) {
            const chatItem = {
                id: currentChatId,
                title: message.substring(0, 30) + (message.length > 30 ? '...' : ''),
                timestamp: new Date().toLocaleString(),
                messageCount: 1
            };
            chatHistory.unshift(chatItem);
            updateChatHistoryUI();
        }
        
        // Show typing indicator and generate response
        isGenerating = true;
        document.getElementById('sendBtn').classList.add('hidden');
        document.getElementById('stopBtn').classList.remove('hidden');
        showTypingIndicator();
        
        // Call your Flask API
        callAPI(message);
    }
}