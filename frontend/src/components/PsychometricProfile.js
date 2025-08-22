import React from 'react';
import { Card, CardContent, Typography, Box, LinearProgress, Tooltip, Chip } from '@mui/material';
import PsychologyIcon from '@mui/icons-material/Psychology';
import { usePsychometricData } from '../hooks/usePsychometricData';

const TraitBar = ({ label, description, percentage, color }) => (
    <Tooltip title={description} placement="left" arrow>
        <Box mb={2}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={0.5}>
                <Typography variant="body2" component="span">{label}</Typography>
                <Typography variant="body2" component="span" fontWeight="bold">{percentage}%</Typography>
            </Box>
            <LinearProgress variant="determinate" value={percentage} color={color} />
        </Box>
    </Tooltip>
);

const PsychometricProfile = ({ profile }) => {
    const { bigFive, schwartzValues, hasData, topTraits } = usePsychometricData(profile);

    if (!hasData) {
        return (
            <Card>
                <CardContent sx={{ textAlign: 'center', color: 'text.secondary' }}>
                    <PsychologyIcon sx={{ fontSize: 40, mb: 1 }}/>
                    <Typography variant="h6">Profil Psychometryczny</Typography>
                    <Typography variant="body2">Oczekiwanie na dane do analizy...</Typography>
                </CardContent>
            </Card>
        );
    }

    return (
        <Card>
            <CardContent>
                <Typography variant="h6" gutterBottom>Profil Psychometryczny</Typography>
                 <Box mb={2}>
                    <Typography variant="subtitle2" color="text.secondary" gutterBottom>Dominujące Cechy:</Typography>
                    <Box display="flex" flexWrap="wrap" gap={1}>
                        {topTraits.map(trait => <Chip key={trait.key} label={trait.label} size="small" color={trait.color} />)}
                    </Box>
                </Box>

                {bigFive.length > 0 && (
                    <Box mt={2}>
                        <Typography variant="subtitle1" gutterBottom>Wielka Piątka (Big Five)</Typography>
                        {bigFive.map(trait => <TraitBar key={trait.key} {...trait} />)}
                    </Box>
                )}
                {schwartzValues.length > 0 && (
                    <Box mt={3}>
                        <Typography variant="subtitle1" gutterBottom>Teoria Wartości (Schwartz)</Typography>
                        {schwartzValues.map(trait => <TraitBar key={trait.key} {...trait} />)}
                    </Box>
                )}
            </CardContent>
        </Card>
    );
};

export default PsychometricProfile;
