import React from 'react';
import { Card, CardContent, Typography, Box, Chip, Divider } from '@mui/material';
import LightbulbIcon from '@mui/icons-material/Lightbulb';

const languageData = {
    // Uproszczone mapowanie Big Five na DISC do celów demonstracyjnych
    // Conscientiousness -> C, Extraversion -> I, Agreeableness -> S, Openness -> D
    C: {
        keywords: ['dane', 'analiza', 'dowód', 'specyfikacja', 'jakość', 'precyzja'],
        phrase: 'Pozwoli Pan, że przedstawię szczegółową analizę danych, która to potwierdza.'
    },
    I: {
        keywords: ['niesamowite', 'rewolucja', 'społeczność', 'wyjątkowy', 'przyszłość'],
        phrase: 'Proszę sobie wyobrazić, jakie wrażenie zrobi to na Pana znajomych!'
    },
    S: {
        keywords: ['bezpieczeństwo', 'gwarancja', 'stabilność', 'wsparcie', 'rodzina'],
        phrase: 'To sprawdzona i niezawodna technologia z 8-letnią gwarancją, której zaufały tysiące rodzin.'
    },
    D: { // Używamy Openness jako przybliżenia dla Dominant
        keywords: ['efektywność', 'wynik', 'przewaga', 'lider', 'innowacja', 'moc'],
        phrase: 'To rozwiązanie zapewni Panu przewagę konkurencyjną i maksymalny zwrot z inwestycji.'
    }
};

const LanguageAdvisor = ({ dominantDiscType }) => {
    const advice = languageData[dominantDiscType];

    if (!advice) {
        return null; // Nie renderuj nic, jeśli typ nie jest określony
    }

    return (
        <Card>
            <CardContent>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                    <LightbulbIcon sx={{ mr: 1, color: 'warning.main' }} /> Doradca Językowy
                </Typography>
                <Divider sx={{ my: 1 }} />
                <Typography variant="subtitle2" color="text.secondary">Słowa-Klucze do użycia:</Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, my: 1 }}>
                    {advice.keywords.map(kw => <Chip key={kw} label={kw} size="small" />)}
                </Box>
                <Typography variant="subtitle2" color="text.secondary" sx={{ mt: 2 }}>Złota Fraza:</Typography>
                <Typography variant="body2" fontStyle="italic">"{advice.phrase}"</Typography>
            </CardContent>
        </Card>
    );
};

export default LanguageAdvisor;
