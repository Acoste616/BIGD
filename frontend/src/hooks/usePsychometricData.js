import { useMemo } from 'react';

// Definicje (można je przenieść do osobnego pliku w przyszłości)
const TRAIT_DEFINITIONS = {
    openness: { label: 'Otwartość', description: 'Skłonność do nowych idei, kreatywność, ciekawość.' },
    conscientiousness: { label: 'Sumienność', description: 'Zorganizowanie, odpowiedzialność, dyscyplina.' },
    extraversion: { label: 'Ekstrawersja', description: 'Energia, towarzyskość, asertywność.' },
    agreeableness: { label: 'Ugodowość', description: 'Współczucie, chęć do współpracy, uprzejmość.' },
    neuroticism: { label: 'Neurotyczność', description: 'Podatność na stres i negatywne emocje.' },
    security: { label: 'Bezpieczeństwo', description: 'Ceni stabilność, porządek i pewność.' },
    power: { label: 'Władza', description: 'Dąży do statusu, prestiżu i kontroli.' },
    achievement: { label: 'Osiągnięcia', description: 'Skupiony na sukcesie, kompetencjach i wynikach.' },
    hedonism: { label: 'Hedonizm', description: 'Poszukuje przyjemności i komfortu.' },
    stimulation: { label: 'Stymulacja', description: 'Potrzebuje nowości, wyzwań i ekscytujących doświadczeń.' },
    universalism: { label: 'Uniwersalizm', description: 'Kieruje się troską o dobro ogółu i tolerancją.' },
};

const getScoreColor = (score) => {
    if (score >= 0.7) return 'success';
    if (score >= 0.4) return 'info';
    return 'inherit';
};

export const usePsychometricData = (profile) => {
    const processedData = useMemo(() => {
        if (!profile || (!profile.big_five && !profile.schwartz_values)) {
            return { bigFive: [], schwartzValues: [], topTraits: [], hasData: false };
        }

        const allTraits = [];

        const bigFive = profile.big_five ? Object.entries(profile.big_five).map(([key, value]) => {
             const trait = {
                key,
                value,
                ...TRAIT_DEFINITIONS[key],
                percentage: Math.round(value * 100),
                color: getScoreColor(value),
            };
            allTraits.push(trait);
            return trait;
        }) : [];

        const schwartzValues = profile.schwartz_values ? Object.entries(profile.schwartz_values).map(([key, value]) => {
            const trait = {
                key,
                value,
                ...TRAIT_DEFINITIONS[key],
                percentage: Math.round(value * 100),
                color: getScoreColor(value),
            };
            allTraits.push(trait);
            return trait;
        }) : [];

        const topTraits = allTraits.sort((a, b) => b.value - a.value).slice(0, 3);

        return { bigFive, schwartzValues, topTraits, hasData: allTraits.length > 0 };
    }, [profile]);

    return processedData;
};
