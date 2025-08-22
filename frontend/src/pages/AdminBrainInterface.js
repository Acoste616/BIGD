import React, { useState, useRef, useEffect } from 'react';
import { Box, TextField, Button, Paper, Typography, CircularProgress } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import MainLayout from '../components/MainLayout';
import ChatMessage from '../components/ChatMessage';
import { useDojoChat } from '../hooks/useDojoChat';

const AdminBrainInterface = () => {
    const { messages, isLoading, sendMessage } = useDojoChat();
    const [input, setInput] = useState('');
    const chatEndRef = useRef(null);

    useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const handleSend = () => {
        if (input.trim()) {
            sendMessage(input.trim());
            setInput('');
        }
    };

    return (
        <MainLayout>
            <Paper sx={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 120px)' }}>
                <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
                    <Typography variant="h5">AI Dojo - Trening Interaktywny</Typography>
                </Box>
                <Box sx={{ flexGrow: 1, overflowY: 'auto', p: 2 }}>
                    {messages.map((msg, index) => <ChatMessage key={index} message={msg} />)}
                    {isLoading && <Typography>AI pisze...</Typography>}
                    <div ref={chatEndRef} />
                </Box>
                <Box component="form" sx={{ p: 2, borderTop: 1, borderColor: 'divider', display: 'flex', gap: 1 }}
                    onSubmit={(e) => { e.preventDefault(); handleSend(); }}>
                    <TextField
                        fullWidth
                        variant="outlined"
                        placeholder="Wpisz polecenie lub pytanie do AI..."
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        disabled={isLoading}
                    />
                    <Button type="submit" variant="contained" endIcon={<SendIcon />} disabled={isLoading}>
                        Wyślij
                    </Button>
                </Box>
            </Paper>
        </MainLayout>
    );
};
export default AdminBrainInterface;
