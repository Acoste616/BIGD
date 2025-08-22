import React from 'react';
import { Box, Paper, Typography, Avatar, Chip } from '@mui/material';
import PersonIcon from '@mui/icons-material/Person';
import SmartToyIcon from '@mui/icons-material/SmartToy';

const ChatMessage = ({ message }) => {
    const isUser = message.sender === 'user';
    return (
        <Box sx={{ display: 'flex', justifyContent: isUser ? 'flex-end' : 'flex-start', mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'flex-start', flexDirection: isUser ? 'row-reverse' : 'row', gap: 1 }}>
                <Avatar sx={{ bgcolor: isUser ? 'primary.main' : 'secondary.main' }}>
                    {isUser ? <PersonIcon /> : <SmartToyIcon />}
                </Avatar>
                <Paper
                    variant="outlined"
                    sx={{
                        p: 1.5,
                        bgcolor: isUser ? 'primary.light' : 'background.paper',
                        maxWidth: '70%',
                    }}
                >
                    <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>{message.content}</Typography>
                    {message.type && !isUser && (
                         <Chip label={message.type} size="small" sx={{ mt: 1 }} />
                    )}
                </Paper>
            </Box>
        </Box>
    );
};
export default ChatMessage;
