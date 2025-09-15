import React from 'react';
import { Box, Typography } from '@mui/material';

const PromptSandbox = () => {
    return (
        <Box>
            <Typography variant="h6" gutterBottom>
                Piaskownica Promptów (w budowie)
            </Typography>
            <Typography variant="body1">
                W tym miejscu pojawi się interfejs do edycji, testowania A/B
                i wdrażania nowych wersji promptów systemowych.
            </Typography>
            {/* TODO: Implementacja listy promptów, edytora i mechanizmu testowania */}
        </Box>
    );
};

export default PromptSandbox;