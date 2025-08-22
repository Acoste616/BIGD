import apiClient from './api';

export const sendDojoMessage = async (content) => {
    const response = await apiClient.post('/dojo/chat', { content });
    return response.data;
};

export const getDojoHealth = async () => {
    const response = await apiClient.get('/dojo/health');
    return response.data;
};
