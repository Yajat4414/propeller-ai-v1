require('dotenv').config();
const express = require('express');
const cors = require('cors');

const app = express();
const PORT = 3000;

app.use(cors());
app.use(express.json());
app.use(express.static('.'));

console.log('Starting server...');

// REPLACE YOUR OLD app.post('/api/chat', ...) WITH THIS:
app.post('/api/chat', async (req, res) => {
    console.log('\n=== NEW CHAT REQUEST ===');
    console.log('1. Request received');
    console.log('2. Message:', req.body.message);
    console.log('3. Deep Thinking:', req.body.deepThinking);
    console.log('4. Study Learn:', req.body.studyLearn);
    
    try {
        const { message, deepThinking, studyLearn } = req.body;
        
        let systemMessage = 'You are Propeller, a helpful AI assistant.';
        if (deepThinking) systemMessage += ' Use deep analysis and thorough reasoning.';
        if (studyLearn) systemMessage += ' Focus on educational explanations.';
        
        console.log('5. Making API call to OpenRouter...');
        
        const response = await fetch('https://openrouter.ai/api/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${process.env.OPENROUTER_API_KEY}`,
                'Content-Type': 'application/json',
                'HTTP-Referer': 'http://localhost:3000',
                'X-Title': 'Propeller AI'
            },
            body: JSON.stringify({
                model: 'deepseek/deepseek-chat-v3.1:free',
                messages: [
                    { role: 'system', content: systemMessage },
                    { role: 'user', content: message }
                ]
            })
        });

        console.log('6. OpenRouter response status:', response.status);
        
        const data = await response.json();
        console.log('7. OpenRouter response data:', JSON.stringify(data).substring(0, 200));
        
        if (!response.ok) {
            console.error('8. API ERROR:', data);
            throw new Error(data.error?.message || 'API failed');
        }

        console.log('9. Success! Sending response to client');
        res.json({ response: data.choices[0].message.content });

    } catch (error) {
        console.error('10. CAUGHT ERROR:', error.message);
        console.error('11. Full error:', error);
        res.status(500).json({ error: 'Failed to get response', details: error.message });
    }
});

app.listen(PORT, () => {
    console.log(`✅ Server running at http://localhost:${PORT}`);
});