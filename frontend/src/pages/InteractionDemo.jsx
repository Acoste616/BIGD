/**
 * Demo strona dla komponentu InteractionCard
 * Pokazuje quick_response i pełne możliwości komponentu
 */
import React, { useState } from 'react';
import {
  Box,
  Typography,
  Container,
  Paper,
  Switch,
  FormControlLabel,
  Alert,
  Button,
  Stack,
  Divider
} from '@mui/material';
import {
  Psychology as PsychologyIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import MainLayout from '../components/MainLayout';
import InteractionCard from '../components/InteractionCard';

// Przykładowe dane interakcji z prawdziwą strukturą API
const sampleInteractions = [
  {
    id: 1,
    user_input: "Klient pyta o cenę Model Y i czy można dostać rabat. Wydaje się zainteresowany, ale martwi się o koszty eksploatacji.",
    timestamp: "2025-01-16T14:30:22Z",
    confidence_score: 92,
    ai_response_json: {
      main_analysis: "Klient wykazuje silne zainteresowanie Model Y, ale ma obawy finansowe. To typowe zachowanie dla archetypu Pragmatycznego Analityka - potrzebuje konkretnych danych ekonomicznych.",
      client_archetype: "Pragmatyczny Analityk",
      confidence_level: 92,
      suggested_actions: [
        {
          action: "Przedstaw kalkulator TCO (Total Cost of Ownership)",
          reasoning: "Analityk potrzebuje twardych danych o kosztach długoterminowych"
        },
        {
          action: "Porównaj koszty eksploatacji z samochodem spalinowym",
          reasoning: "Konkretne porównanie przekona do oszczędności"
        },
        {
          action: "Omów opcje leasingu i finansowania",
          reasoning: "Może rozłożyć koszty początkowe w czasie"
        },
        {
          action: "Zaproponuj jazdę testową z omówieniem funkcji oszczędzających energię",
          reasoning: "Praktyczne doświadczenie wzmocni argumenty ekonomiczne"
        }
      ],
      buy_signals: ["pytanie o cenę", "zainteresowanie konkretnym modelem", "rozważanie kosztów"],
      risk_signals: ["obawy o koszty", "wahanie cenowe"],
      key_insights: [
        "Klient jest w fazie aktywnego rozważania zakupu",
        "Potrzebuje konkretnych danych finansowych do podjęcia decyzji",
        "Archetyp analityka wymaga logicznej argumentacji"
      ],
      objection_handlers: {
        "za droge": "Pokaż oszczędności długoterminowe i całkowity TCO",
        "koszty eksploatacji": "Przedstaw porównanie z kosztami benzyny i serwisu"
      },
      qualifying_questions: [
        "Ile obecnie wydaje Pan miesięcznie na paliwo?",
        "Jaki jest planowany budżet na nowy samochód?",
        "Czy rozważał Pan leasing jako opcję finansowania?"
      ],
      sentiment_score: 8,
      potential_score: 9,
      urgency_level: "high",
      next_best_action: "Przygotuj szczegółowy kalkulator kosztów TCO",
      follow_up_timing: "W ciągu 24 godzin",
      quick_response: "To świetne pytanie! Model Y rzeczywiście ma doskonałą relację jakości do ceny. Czy mogę pokazać Panu dokładne porównanie kosztów eksploatacji?"
    }
  },
  {
    id: 2,
    user_input: "Klient mówi, że jego żona nie chce samochodu elektrycznego bo boi się, że zabraknie prądu w trasie.",
    timestamp: "2025-01-16T15:15:18Z",
    confidence_score: 85,
    ai_response_json: {
      main_analysis: "Typowe zastrzeżenie dotyczące anxiety o zasięg. Klient ma pozytywne nastawienie, ale potrzebuje przekonać współmałżonkę. To wymaga taktyki edukacyjnej i budowania zaufania.",
      client_archetype: "Strażnik Rodziny",
      confidence_level: 85,
      suggested_actions: [
        {
          action: "Zapytaj o typowe trasy rodzinne",
          reasoning: "Pokażesz, że zasięg Model Y pokrywa ich potrzeby z zapasem"
        },
        {
          action: "Pokaż mapę ładowarek na ich trasach",
          reasoning: "Konkretne lokalizacje zmniejszą obawy"
        },
        {
          action: "Zaoferuj test drive dla obojga",
          reasoning: "Praktyczne doświadczenie przekona bardziej niż teoria"
        },
        {
          action: "Opisz funkcje planowania trasy z ładowarkami",
          reasoning: "Technologia automatycznie rozwiązuje problem planowania"
        }
      ],
      buy_signals: ["rozważanie zakupu", "próba rozwiązania zastrzeżeń"],
      risk_signals: ["opór współmałżonka", "obawy o zasięg"],
      key_insights: [
        "Decyzja wymaga przekonania dwóch osób",
        "Bezpieczeństwo rodziny to priorytet",
        "Potrzeba edukacji o infrastrukturze ładowania"
      ],
      objection_handlers: {
        "zasieg": "Model Y ma zasięg 533 km - to więcej niż większość tras bez tankowania",
        "brak ladowarek": "Supercharger network to ponad 50,000 punktów ładowania na świecie"
      },
      qualifying_questions: [
        "Jakie są najczęstsze trasy, które państwo pokonujecie?",
        "Jak daleko zwykle jeździcie bez postoju?",
        "Czy mają państwo możliwość ładowania w domu?"
      ],
      sentiment_score: 7,
      potential_score: 6,
      urgency_level: "medium",
      next_best_action: "Zaplanuj wspólną prezentację dla obojga partnerów",
      follow_up_timing: "W ciągu 2-3 dni",
      quick_response: "Rozumiem te obawy - to bardzo częste pytanie! Model Y ma zasięg 533 km, a czy mogę zapytać, jak długie trasy zwykle państwo pokonujecie?"
    }
  },
  {
    id: 3,
    user_input: "Klient właśnie wrócił z jazdy testowej i jest bardzo podekscytowany. Pyta kiedy może odebrać auto.",
    timestamp: "2025-01-16T16:02:45Z", 
    confidence_score: 96,
    ai_response_json: {
      main_analysis: "BARDZO POZYTYWNY SYGNAŁ! Klient przeszedł od zainteresowania do emocjonalnego zaangażowania. To idealny moment na zamknięcie sprzedaży z zachowaniem profesjonalizmu.",
      client_archetype: "Entuzjasta Osiągów",
      confidence_level: 96,
      suggested_actions: [
        {
          action: "Przejdź natychmiast do konfiguracji samochodu",
          reasoning: "Strike while the iron is hot - wykorzystaj moment szczytowego zainteresowania"
        },
        {
          action: "Omów dostępne opcje finansowania",
          reasoning: "Ułatwi podjęcie decyzji o zakupie"
        },
        {
          action: "Sprawdź aktualne terminy dostaw", 
          reasoning: "Konkretna data dostawy zmaterializuje zakup"
        },
        {
          action: "Zaproponuj zastrzeżenie konkretnej konfiguracji",
          reasoning: "Commitment przez działanie zwiększa prawdopodobieństwo zakupu"
        }
      ],
      buy_signals: ["emocjonalne zaangażowanie", "pytanie o odbiór", "pozytywna reakcja na test drive"],
      risk_signals: ["możliwa impulsywność", "potrzeba sprawdzenia budżetu"],
      key_insights: [
        "Klient jest gotowy do zakupu TERAZ",
        "Emocje są bardzo pozytywne",
        "To prawdopodobnie ostatnia faza przed decyzją"
      ],
      objection_handlers: {
        "za szybko": "Rozumiem, że to duża decyzja. Możemy zastrzec konfigurację bez zobowiązania",
        "termin dostawy": "Aktualne terminy to X miesięcy, ale możemy sprawdzić dostępność wcześniejszych"
      },
      qualifying_questions: [
        "Która funkcja podczas jazdy testowej zrobiła na Panu największe wrażenie?",
        "Jaka konfiguracja byłaby dla Pana idealna?",
        "Czy jest jakiś konkretny termin, do którego potrzebuje Pan auto?"
      ],
      sentiment_score: 10,
      potential_score: 10, 
      urgency_level: "high",
      next_best_action: "Rozpocznij proces konfiguracji i rezerwacji",
      follow_up_timing: "Natychmiast - nie czekaj!",
      quick_response: "Fantastycznie! Widzę, że jazda zrobiła na Panu wrażenie. Sprawdźmy aktualną dostępność - mogę od razu przygotować konfigurację dla Pana!"
    }
  },
  // Przykład z fallback (AI niedostępny)
  {
    id: 4,
    user_input: "Klient porównuje Tesla z BMW i Audi. Wydaje się niezdecydowany.",
    timestamp: "2025-01-16T16:30:12Z",
    confidence_score: 30,
    ai_response_json: {
      main_analysis: "Analiza automatyczna: 'Klient porównuje Tesla z BMW i Audi...' - AI niedostępny. Postępuj zgodnie z procedurami sprzedażowymi.",
      client_archetype: "Nieznany (błąd AI)",
      confidence_level: 30,
      suggested_actions: [
        {
          action: "Zadawaj pytania otwarte",
          reasoning: "Zbieraj informacje o potrzebach"
        },
        {
          action: "Słuchaj aktywnie", 
          reasoning: "Zbuduj zrozumienie sytuacji"
        },
        {
          action: "Przedstaw korzyści produktu",
          reasoning: "Buduj wartość oferty"
        },
        {
          action: "Zaproponuj następny krok",
          reasoning: "Utrzymaj momentum rozmowy"
        }
      ],
      buy_signals: ["zainteresowanie", "pytania o szczegóły"],
      risk_signals: ["wahanie", "brak konkretów"],
      key_insights: [
        "AI niedostępny - polegaj na doświadczeniu",
        "Skup się na potrzebach klienta", 
        "Zadawaj pytania kwalifikujące"
      ],
      objection_handlers: {
        "cena": "Pokaż wartość długoterminową i TCO",
        "czas": "Zapytaj o konkretne obawy i harmonogram"
      },
      qualifying_questions: [
        "Co jest najważniejsze w Pana nowym samochodzie?",
        "Jaki jest planowany budżet?",
        "Kiedy chciałby Pan podjąć decyzję?"
      ],
      sentiment_score: 5,
      potential_score: 5,
      urgency_level: "medium",
      next_best_action: "Zbierz więcej informacji o potrzebach klienta",
      follow_up_timing: "W ciągu 24-48 godzin",
      quick_response: "Rozumiem. Czy mógłby Pan powiedzieć więcej o swoich potrzebach?",
      // Metadata błędu
      is_fallback: true,
      error_reason: "AI service unavailable",
      model_used: "fallback"
    }
  }
];

const InteractionDemo = () => {
  const [showFullDetails, setShowFullDetails] = useState(true);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [copiedMessage, setCopiedMessage] = useState('');

  const currentInteraction = sampleInteractions[currentIndex];

  const handleCopyQuickResponse = (quickResponse) => {
    setCopiedMessage(`Skopiowano: "${quickResponse}"`);
    setTimeout(() => setCopiedMessage(''), 3000);
  };

  const nextInteraction = () => {
    setCurrentIndex((prev) => (prev + 1) % sampleInteractions.length);
    setCopiedMessage('');
  };

  const prevInteraction = () => {
    setCurrentIndex((prev) => (prev - 1 + sampleInteractions.length) % sampleInteractions.length);
    setCopiedMessage('');
  };

  return (
    <MainLayout title="Demo: Quick Response & Analiza AI">
      <Container maxWidth="md" sx={{ py: 3 }}>
        {/* Header */}
        <Paper sx={{ p: 3, mb: 3, bgcolor: 'primary.main', color: 'white' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
            <PsychologyIcon sx={{ fontSize: '2rem' }} />
            <Box>
              <Typography variant="h4" fontWeight="bold">
                🤖 AI Co-Pilot: Quick Response
              </Typography>
              <Typography variant="subtitle1" sx={{ opacity: 0.9 }}>
                Demo funkcjonalności natychmiastowych odpowiedzi dla sprzedawców
              </Typography>
            </Box>
          </Box>
        </Paper>

        {/* Kontrolki */}
        <Paper sx={{ p: 2, mb: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">
              Interakcja {currentIndex + 1} z {sampleInteractions.length}
            </Typography>
            
            <Stack direction="row" spacing={1}>
              <Button onClick={prevInteraction} variant="outlined" size="small">
                Poprzednia
              </Button>
              <Button onClick={nextInteraction} variant="contained" size="small" startIcon={<RefreshIcon />}>
                Następna
              </Button>
            </Stack>
          </Box>
          
          <FormControlLabel
            control={
              <Switch 
                checked={showFullDetails}
                onChange={(e) => setShowFullDetails(e.target.checked)}
              />
            }
            label="Pokaż pełną analizę AI"
          />
        </Paper>

        {/* Komunikat o kopiowaniu */}
        {copiedMessage && (
          <Alert severity="success" sx={{ mb: 2 }}>
            {copiedMessage}
          </Alert>
        )}

        {/* Informacje o bieżącej interakcji */}
        <Alert severity="info" sx={{ mb: 2 }}>
          <Typography variant="body2">
            <strong>Scenariusz:</strong> {
              currentIndex === 0 ? "Klient pyta o cenę - typowa sytuacja sprzedażowa" :
              currentIndex === 1 ? "Opór współmałżonka - potrzeba edukacji" :
              currentIndex === 2 ? "Po jeździe testowej - moment zamknięcia sprzedaży!" :
              "AI niedostępny - fallback response"
            }
          </Typography>
        </Alert>

        {/* Główny komponent InteractionCard */}
        <InteractionCard 
          interaction={currentInteraction}
          showFullDetails={showFullDetails}
          onCopyQuickResponse={handleCopyQuickResponse}
        />

        {/* Informacje techniczne */}
        <Paper sx={{ p: 3, mt: 3, bgcolor: 'grey.50' }}>
          <Typography variant="h6" gutterBottom>
            💡 Kluczowe funkcje Quick Response:
          </Typography>
          
          <Stack spacing={1}>
            <Typography variant="body2">
              ✅ <strong>Natychmiastowa użyteczność</strong> - sprzedawca może od razu odpowiedzieć klientowi
            </Typography>
            <Typography variant="body2">
              ✅ <strong>Kontekstowa inteligencja</strong> - odpowiedź dopasowana do archetypu i sytuacji
            </Typography>
            <Typography variant="body2">
              ✅ <strong>Kopiowanie jednym klikiem</strong> - szybkie przeniesienie do komunikatora/notatek
            </Typography>
            <Typography variant="body2">
              ✅ <strong>Fallback safety</strong> - działa nawet gdy AI jest niedostępny
            </Typography>
            <Typography variant="body2">
              ✅ <strong>Wyróżnienie wizualne</strong> - błękitna ramka przyciąga uwagę
            </Typography>
          </Stack>

          <Divider sx={{ my: 2 }} />

          <Typography variant="body2" color="text.secondary">
            <strong>Dane techniczne:</strong> Model {currentInteraction.ai_response_json.model_used || 'gpt-oss-120b'} 
            | Pewność: {currentInteraction.confidence_score}% 
            | {currentInteraction.ai_response_json.is_fallback ? "Fallback mode" : "AI aktywny"}
          </Typography>
        </Paper>
      </Container>
    </MainLayout>
  );
};

export default InteractionDemo;
