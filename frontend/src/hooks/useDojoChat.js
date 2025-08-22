import { useState, useCallback } from 'react';

export const useDojoChat = () => {
    const [messages, setMessages] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [isStreaming, setIsStreaming] = useState(false);

    const sendMessage = useCallback(async (content) => {
        const userMessage = { sender: 'user', content };
        const aiMessagePlaceholder = { 
            sender: 'ai', 
            content: '', 
            type: 'answer',
            id: Date.now() // Unique ID for tracking
        };
        
        setMessages(prev => [...prev, userMessage, aiMessagePlaceholder]);
        setIsLoading(true);
        setIsStreaming(true);

        try {
            // Użyj streamingowego endpointu
            const response = await fetch('/api/v1/dojo/chat/stream', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'text/event-stream',
                },
                body: JSON.stringify({ content })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                
                // Keep the last partial line in buffer
                buffer = lines.pop() || '';

                for (const line of lines) {
                    if (line.trim() === '') continue;
                    
                    if (line.startsWith('data: ')) {
                        try {
                            const jsonData = line.substring(6); // Remove 'data: '
                            const data = JSON.parse(jsonData);
                            
                            if (data.type === 'token' && data.token) {
                                // Append token to the last AI message
                                setMessages(prev => prev.map((msg, index) => 
                                    index === prev.length - 1 && msg.sender === 'ai' 
                                        ? { ...msg, content: msg.content + data.token }
                                        : msg
                                ));
                            } else if (data.type === 'stream_end') {
                                // Stream completed, we have full content
                                console.log('Stream completed, full content length:', data.total_length);
                            } else if (data.type === 'metadata') {
                                // Update message with metadata if needed
                                const metadata = data.metadata;
                                setMessages(prev => prev.map((msg, index) => 
                                    index === prev.length - 1 && msg.sender === 'ai'
                                        ? { 
                                            ...msg, 
                                            type: metadata.quick_response ? 'answer' : msg.type,
                                            confidence: metadata.confidence_level,
                                            metadata: metadata
                                        }
                                        : msg
                                ));
                            } else if (data.type === 'error') {
                                // Handle error
                                setMessages(prev => prev.map((msg, index) => 
                                    index === prev.length - 1 && msg.sender === 'ai'
                                        ? { 
                                            ...msg, 
                                            content: 'Wystąpił błąd podczas analizy AI.',
                                            type: 'error' 
                                        }
                                        : msg
                                ));
                                console.error('AI Error:', data.error, data.details);
                                break;
                            } else if (data.type === 'fallback') {
                                // Handle fallback response
                                setMessages(prev => prev.map((msg, index) => 
                                    index === prev.length - 1 && msg.sender === 'ai'
                                        ? { 
                                            ...msg, 
                                            content: data.content || 'Używam zapasowej odpowiedzi.',
                                            type: 'answer',
                                            isFallback: true
                                        }
                                        : msg
                                ));
                                break;
                            }
                            
                        } catch (parseError) {
                            console.warn('Error parsing SSE data:', parseError, 'Raw data:', line);
                            continue;
                        }
                    }
                }
            }

        } catch (error) {
            console.error('Streaming error:', error);
            
            // Update the last AI message with error
            setMessages(prev => prev.map((msg, index) => 
                index === prev.length - 1 && msg.sender === 'ai'
                    ? { 
                        ...msg, 
                        content: 'Wystąpił błąd komunikacji z AI.',
                        type: 'error'
                    }
                    : msg
            ));
        } finally {
            setIsLoading(false);
            setIsStreaming(false);
        }
    }, []);

    const clearMessages = useCallback(() => {
        setMessages([]);
    }, []);

    return { 
        messages, 
        isLoading, 
        isStreaming, 
        sendMessage, 
        clearMessages 
    };
};
