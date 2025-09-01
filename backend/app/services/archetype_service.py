"""
ArchetypeService v1.0 - Customer Archetype Detection and Management
Extracted from SessionOrchestratorService monolith - Phase 2C

Single Responsibility: Customer archetype detection and business logic
- Generic interface for industry-agnostic archetype mapping
- Tesla-specific archetype definitions and rules
- Easily replaceable for different industries (e.g., real estate, finance)
- Confidence scoring and psychological alignment algorithms
"""

import logging
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class BaseArchetypeService(ABC):
    """
    🏗️ Abstract base class defining the generic interface for archetype services
    
    This interface ensures that any industry-specific archetype service
    (Tesla, RealEstate, Finance, etc.) implements the same contract,
    making the system easily adaptable to different business domains.
    """
    
    @abstractmethod
    def get_available_archetypes(self) -> Dict[str, Dict]:
        """Return all available archetype definitions for this industry"""
        pass
    
    @abstractmethod
    async def determine_archetype(self, psychology_results: Dict, session_context: Dict = None) -> Dict:
        """Main interface: determine customer archetype based on psychology and context"""
        pass
    
    @abstractmethod
    def calculate_archetype_confidence(self, psychology_scores: Dict, selected_archetype: str) -> int:
        """Calculate confidence score for archetype selection"""
        pass
    
    @abstractmethod
    def get_fallback_archetype(self) -> Dict:
        """Return safe fallback archetype when detection fails"""
        pass

class TeslaArchetypeService(BaseArchetypeService):
    """
    🚗 Tesla-specific customer archetype detection service
    
    Responsible for:
    1. Tesla customer archetype definitions and mapping rules
    2. Psychology-to-archetype algorithm specific to Tesla customers
    3. Confidence scoring based on Tesla customer behavior patterns
    4. Sales strategy recommendations for Tesla sales scenarios
    """
    
    def __init__(self):
        """Initialize Tesla archetype service with predefined archetype definitions"""
        logger.info("🎯 [TESLA ARCHETYPE] Initializing Tesla-specific archetype service")
        
        # GENERAL CUSTOMER ARCHETYPES - Universal baseline archetypes
        self.GENERAL_ARCHETYPES = {
            "analityk": {
                "name": "🔬 Analityk",
                "description": "Wysoka Sumienność, Compliance (DISC), Wartość: Bezpieczeństwo",
                "psychological_profile": {
                    "big_five": {"conscientiousness": "high", "openness": "medium"},
                    "disc": {"compliance": "high", "steadiness": "medium"},
                    "schwartz": ["security", "conformity"]
                },
                "sales_strategy": {
                    "do": ["Dostarczaj twarde dane i statystyki", "Prezentuj TCO i ROI", "Dawaj czas na przemyślenie"],
                    "dont": ["Nie naciskaj na szybką decyzję", "Nie pomijaj szczegółów technicznych", "Nie używaj emocjonalnych argumentów"]
                }
            },
            "wizjoner": {
                "name": "🚀 Wizjoner",
                "description": "Wysoka Otwartość, Dominance + Influence (DISC), Wartość: Osiągnięcia",
                "psychological_profile": {
                    "big_five": {"openness": "high", "extraversion": "high"},
                    "disc": {"dominance": "high", "influence": "high"},
                    "schwartz": ["achievement", "self_direction"]
                },
                "sales_strategy": {
                    "do": ["Podkreślaj innowacyjność i przyszłość", "Mów o statusie i prestiżu", "Prezentuj wizję długoterminową"],
                    "dont": ["Nie skupiaj się tylko na kosztach", "Nie wdawaj w nadmierne szczegóły", "Nie ograniczaj do obecnych potrzeb"]
                }
            },
            "relacyjny_budowniczy": {
                "name": "🤝 Relacyjny Budowniczy",
                "description": "Wysoka Ugodowość, Steadiness (DISC), Wartość: Życzliwość",
                "psychological_profile": {
                    "big_five": {"agreeableness": "high", "conscientiousness": "medium"},
                    "disc": {"steadiness": "high", "influence": "medium"},
                    "schwartz": ["benevolence", "tradition"]
                },
                "sales_strategy": {
                    "do": ["Buduj osobistą relację", "Podkreślaj korzyści dla zespołu/rodziny", "Używaj referencji i opinii"],
                    "dont": ["Nie bądź zbyt agresywny", "Nie ignoruj emocji i relacji", "Nie podejmuj za niego decyzji"]
                }
            },
            "szybki_decydent": {
                "name": "⚡ Szybki Decydent",
                "description": "Wysoka Ekstrawersja, Dominance (DISC), Wartość: Władza",
                "psychological_profile": {
                    "big_five": {"extraversion": "high", "conscientiousness": "low"},
                    "disc": {"dominance": "high", "compliance": "low"},
                    "schwartz": ["power", "achievement"]
                },
                "sales_strategy": {
                    "do": ["Prezentuj kluczowe korzyści szybko", "Podkreślaj przewagę konkurencyjną", "Oferuj natychmiastowe działanie"],
                    "dont": ["Nie przeciągaj prezentacji", "Nie wdawaj się w szczegóły techniczne", "Nie zwlekaj z ofertą"]
                }
            }
        }
        
        # TESLA-SPECIFIC ARCHETYPES - Industry-specific customer segments
        self.TESLA_ARCHETYPES = {
            "zdobywca_statusu": {
                "name": "🏆 Zdobywca Statusu",
                "description": "Percepcja Tesli jako symbolu sukcesu i prestiżu. Klient, który postrzega zakup Tesli jako inwestycję w swój wizerunek i pozycję społeczną.",
                "dominant_traits": ["extraversion", "dominance_disc"],
                "psychological_profile": {
                    "big_five": {"extraversion": "high", "conscientiousness": "medium"},
                    "disc": {"dominance": "high", "influence": "high"},
                    "schwartz": ["achievement", "power"]
                },
                "sales_strategy": {
                    "do": [
                        "Podkreślaj ekskluzywność i prestiż marki Tesla",
                        "Mów o statusie właściciela Tesli w społeczeństwie",
                        "Prezentuj Teslę jako symbol sukcesu i innowacyjności",
                        "Używaj języka sukcesu i przywództwa",
                        "Podkreślaj unikalność - 'nie każdy może mieć Teslę'"
                    ],
                    "dont": [
                        "Nie skupiaj się tylko na aspektach technicznych",
                        "Nie pomniejszaj znaczenia wizerunku i statusu",
                        "Nie używaj argumentów czysto ekonomicznych",
                        "Nie porównuj z konkurencją w kategoriach ceny"
                    ]
                },
                "motivation": "Status społeczny i prestiż",
                "communication_style": "Entuzjastyczny, skoncentrowany na korzyściach wizerunkowych"
            },
            "straznik_rodziny": {
                "name": "👨‍👩‍👧‍👦 Strażnik Rodziny",
                "description": "Priorytetem jest bezpieczeństwo i ochrona najbliższych. Tesla postrzegana jako najbezpieczniejszy wybór dla rodziny.",
                "dominant_traits": ["conscientiousness", "steadiness_disc"],
                "psychological_profile": {
                    "big_five": {"conscientiousness": "high", "agreeableness": "high"},
                    "disc": {"steadiness": "high", "compliance": "high"},
                    "schwartz": ["security", "benevolence"]
                },
                "sales_strategy": {
                    "do": [
                        "Podkreślaj bezpieczeństwo - najwyższe oceny NHTSA",
                        "Mów o ochronie rodziny i dzieci",
                        "Prezentuj technologię Autopilot jako opiekuna",
                        "Używaj języka bezpieczeństwa i zaufania",
                        "Podkreślaj niezawodność i trwałość Tesli"
                    ],
                    "dont": [
                        "Nie ignoruj aspektów bezpieczeństwa",
                        "Nie bagatelizuj obaw o rodzinę",
                        "Nie skupiaj się wyłącznie na osiągach",
                        "Nie używa języka ryzykanckiego"
                    ]
                },
                "motivation": "Bezpieczeństwo i ochrona rodziny",
                "communication_style": "Spokojny, skoncentrowany na bezpieczeństwie"
            },
            "pragmatyczny_analityk": {
                "name": "📊 Pragmatyczny Analityk",
                "description": "Kieruje się danymi, TCO i ROI. Dokładnie analizuje koszty, zasięg, efektywność energetyczną.",
                "dominant_traits": ["conscientiousness", "compliance_disc"],
                "psychological_profile": {
                    "big_five": {"conscientiousness": "high", "openness": "medium"},
                    "disc": {"compliance": "high", "steadiness": "medium"},
                    "schwartz": ["security", "conformity"]
                },
                "sales_strategy": {
                    "do": [
                        "Dostarczaj szczegółowe dane TCO i ROI",
                        "Porównuj koszty z konkurentami (na korzyść Tesli)",
                        "Prezentuj fakty o zasięgu i efektywności",
                        "Używaj wykresów, tabel i konkretnych liczb",
                        "Podkreślaj ekonomiczne korzyści długoterminowe"
                    ],
                    "dont": [
                        "Nie pomijaj aspektów ekonomicznych",
                        "Nie używaj emocjonalnych argumentów",
                        "Nie naciskaj na szybką decyzję",
                        "Nie bagatelizuj kosztów początkowych"
                    ]
                },
                "motivation": "Ekonomiczna efektywność i dane",
                "communication_style": "Faktyczny, analityczny, skoncentrowany na liczbach"
            },
            "wizjoner_przyszlosci": {
                "name": "🔮 Wizjoner Przyszłości",
                "description": "Entuzjasta technologii i innowacji. Widzi w Tesli przyszłość transportu i chce być częścią rewolucji.",
                "dominant_traits": ["openness", "influence_disc"],
                "psychological_profile": {
                    "big_five": {"openness": "high", "extraversion": "high"},
                    "disc": {"influence": "high", "dominance": "medium"},
                    "schwartz": ["self_direction", "universalism"]
                },
                "sales_strategy": {
                    "do": [
                        "Podkreślaj rewolucyjne technologie Tesli",
                        "Mów o wizji przyszłości transportu elektrycznego",
                        "Prezentuj Autopilot, FSD i przyszłe funkcje",
                        "Używaj języka innowacji i przyszłości",
                        "Podkreślaj rolę Tesli w zrównoważonym rozwoju"
                    ],
                    "dont": [
                        "Nie skupiaj się tylko na kosztach",
                        "Nie ignoruj aspektów technologicznych",
                        "Nie używa języka konserwatywnego",
                        "Nie porównuj z tradycyjnymi samochodami"
                    ]
                },
                "motivation": "Innowacja i przyszłość technologii",
                "communication_style": "Entuzjastyczny, wizjonerski, technologiczny"
            },
            "ekologiczny_aktywista": {
                "name": "🌱 Ekologiczny Aktywista",
                "description": "Świadomy ekologicznie klient, który widzi w Tesli narzędzie do walki ze zmianami klimatu.",
                "dominant_traits": ["agreeableness", "openness"],
                "psychological_profile": {
                    "big_five": {"agreeableness": "high", "openness": "high"},
                    "disc": {"steadiness": "high", "influence": "medium"},
                    "schwartz": ["universalism", "benevolence"]
                },
                "sales_strategy": {
                    "do": [
                        "Podkreślaj ekologiczne korzyści Tesli",
                        "Mów o redukcji emisji CO2",
                        "Prezentuj zrównoważony rozwój Gigafactory",
                        "Używaj języka środowiska i przyszłości planety",
                        "Podkreślaj wpływ na przyszłe pokolenia"
                    ],
                    "dont": [
                        "Nie ignoruj aspektów środowiskowych",
                        "Nie używa języka destrukcyjnego",
                        "Nie skupiaj się wyłącznie na osiągach",
                        "Nie porównuj z tradycyjnymi samochodami bez kontekstu ekologicznego"
                    ]
                },
                "motivation": "Środowisko i zrównoważony rozwój",
                "communication_style": "Idealistyczny, skoncentrowany na środowisku"
            },
            "fleet_manager": {
                "name": "🏢 Fleet Manager",
                "description": "Zarządca floty pojazdów, skupia się na efektywności kosztowej, niezawodności i skalowalności.",
                "dominant_traits": ["conscientiousness", "compliance_disc"],
                "psychological_profile": {
                    "big_five": {"conscientiousness": "high", "extraversion": "low"},
                    "disc": {"compliance": "high", "steadiness": "high"},
                    "schwartz": ["security", "conformity"]
                },
                "sales_strategy": {
                    "do": [
                        "Podkreślaj korzyści flotowe (TCO, serwis, zarządzanie)",
                        "Prezentuj skalowalność rozwiązań Tesli",
                        "Mów o niezawodności i minimalizacji przestojów",
                        "Używaj języka biznesowego i efektywności",
                        "Podkreślaj korzyści dla całej organizacji"
                    ],
                    "dont": [
                        "Nie ignoruj aspektów biznesowych",
                        "Nie skupiaj się tylko na indywidualnych korzyściach",
                        "Nie używaj języka emocjonalnego",
                        "Nie pomniejszaj znaczenia kosztów operacyjnych"
                    ]
                },
                "motivation": "Efektywność biznesowa i zarządzanie ryzykiem",
                "communication_style": "Profesjonalny, skoncentrowany na biznesie"
            }
        }
    
    def get_available_archetypes(self) -> Dict[str, Dict]:
        """Return all available Tesla customer archetypes"""
        return self.TESLA_ARCHETYPES
    
    async def determine_archetype(self, psychology_results: Dict, session_context: Dict = None) -> Dict:
        """
        🎯 MAIN PUBLIC INTERFACE - Tesla customer archetype determination
        
        Args:
            psychology_results: Complete psychological analysis results
            session_context: Additional context (interaction count, session metadata)
            
        Returns:
            dict: Complete archetype information with confidence and strategies
        """
        try:
            logger.info("🎯 [TESLA ARCHETYPE] Starting archetype determination")
            
            # Extract psychology scores from results
            cumulative_psychology = psychology_results.get('cumulative_psychology', {})
            interaction_count = session_context.get('interaction_count', 0) if session_context else 0
            
            # Perform Tesla-specific archetype mapping
            archetype_result = await self._map_psychology_to_tesla_archetype(cumulative_psychology)
            
            # Add metadata
            archetype_result.update({
                'determination_timestamp': logger.info.__module__,  # Simple timestamp
                'interaction_count': interaction_count,
                'archetype_source': 'tesla_specific',
                'industry': 'automotive_tesla'
            })
            
            logger.info(f"✅ [TESLA ARCHETYPE] Determined: {archetype_result.get('archetype_name', 'Unknown')} "
                       f"(confidence: {archetype_result.get('confidence', 0)}%)")
            
            return archetype_result
            
        except Exception as e:
            logger.error(f"❌ [TESLA ARCHETYPE] Error during determination: {e}")
            return self.get_fallback_archetype()
    
    async def _map_psychology_to_tesla_archetype(self, cumulative_psychology: dict) -> dict:
        """
        🧠⚡ Tesla-specific psychology-to-archetype mapping algorithm
        
        Extracted and enhanced from SessionOrchestratorService
        """
        try:
            logger.info("🎯 [TESLA MAPPER] Starting psychology-to-archetype mapping")

            # STEP 1: Extract psychological indicators
            big_five = cumulative_psychology.get('big_five', {})
            disc = cumulative_psychology.get('disc', {})

            # Extract scores (default to neutral 5 if missing)
            scores = {
                'extraversion': big_five.get('extraversion', {}).get('score', 5),
                'conscientiousness': big_five.get('conscientiousness', {}).get('score', 5),
                'openness': big_five.get('openness', {}).get('score', 5),
                'agreeableness': big_five.get('agreeableness', {}).get('score', 5),
                'dominance_disc': disc.get('dominance', {}).get('score', 5),
                'influence_disc': disc.get('influence', {}).get('score', 5),
                'steadiness_disc': disc.get('steadiness', {}).get('score', 5),
                'compliance_disc': disc.get('compliance', {}).get('score', 5)
            }

            # STEP 2: Tesla-specific decision algorithm
            selected_archetype = None
            max_score = 0

            # Status Seeker: High extraversion + dominance
            status_score = (scores['extraversion'] + scores['dominance_disc'] + scores['influence_disc']) / 3
            if status_score > max_score:
                max_score = status_score
                selected_archetype = "zdobywca_statusu"

            # Family Guardian: High conscientiousness + steadiness
            family_score = (scores['conscientiousness'] + scores['steadiness_disc'] + scores['compliance_disc']) / 3
            if family_score > max_score:
                max_score = family_score
                selected_archetype = "straznik_rodziny"

            # Pragmatic Analyst: High conscientiousness + compliance
            analyst_score = (scores['conscientiousness'] + scores['compliance_disc']) / 2
            if analyst_score > max_score:
                max_score = analyst_score
                selected_archetype = "pragmatyczny_analityk"

            # Future Visionary: High openness + influence
            visionary_score = (scores['openness'] + scores['influence_disc']) / 2
            if visionary_score > max_score:
                max_score = visionary_score
                selected_archetype = "wizjoner_przyszlosci"

            # Eco Activist: High agreeableness + openness
            eco_score = (scores['agreeableness'] + scores['openness']) / 2
            if eco_score > max_score:
                max_score = eco_score
                selected_archetype = "ekologiczny_aktywista"

            # Fleet Manager: Low extraversion + high compliance (business context)
            if scores['extraversion'] < 4 and scores['compliance_disc'] > 6:
                selected_archetype = "fleet_manager"

            # STEP 3: Fallback if no clear match
            if not selected_archetype:
                selected_archetype = "pragmatyczny_analityk"
                logger.info("⚠️ [TESLA MAPPER] Using fallback archetype: Pragmatyczny Analityk")

            # STEP 4: Get archetype definition
            archetype_data = self.TESLA_ARCHETYPES[selected_archetype].copy()

            # STEP 5: Calculate confidence based on alignment
            confidence = self.calculate_archetype_confidence(scores, selected_archetype)

            # STEP 6: Build complete archetype result
            result = {
                "archetype_key": selected_archetype,
                "archetype_name": archetype_data["name"],
                "description": archetype_data["description"],
                "dominant_traits": archetype_data["dominant_traits"],
                "confidence": confidence,
                "key_traits": archetype_data["dominant_traits"],
                "sales_strategy": archetype_data["sales_strategy"],
                "motivation": archetype_data["motivation"],
                "communication_style": archetype_data["communication_style"],
                "psychological_match": {
                    "big_five_alignment": f"{max_score:.1f}/10",
                    "primary_drivers": archetype_data["dominant_traits"],
                    "secondary_traits": [k for k, v in scores.items() if v >= 7]
                }
            }

            logger.info(f"✅ [TESLA MAPPER] Mapped to: {archetype_data['name']} (confidence: {confidence}%)")
            return result

        except Exception as e:
            logger.error(f"❌ [TESLA MAPPER] Error during mapping: {e}")
            return self.get_fallback_archetype()
    
    def calculate_archetype_confidence(self, psychology_scores: Dict, selected_archetype: str) -> int:
        """
        Calculate confidence score for Tesla archetype selection
        
        Args:
            psychology_scores: Dictionary of psychology scores
            selected_archetype: Selected archetype key
            
        Returns:
            int: Confidence percentage (60-95%)
        """
        try:
            # Get archetype definition
            archetype_data = self.TESLA_ARCHETYPES.get(selected_archetype, {})
            dominant_traits = archetype_data.get('dominant_traits', [])
            
            # Calculate alignment with dominant traits
            alignment_scores = []
            for trait in dominant_traits:
                score = psychology_scores.get(trait, 5)
                alignment_scores.append(score)
            
            # Average alignment score
            if alignment_scores:
                avg_alignment = sum(alignment_scores) / len(alignment_scores)
                # Convert to confidence percentage (60-95% range)
                confidence = min(95, max(60, int(avg_alignment * 10)))
            else:
                confidence = 70  # Default confidence
            
            return confidence
            
        except Exception as e:
            logger.error(f"❌ [CONFIDENCE] Error calculating confidence: {e}")
            return 60  # Minimum confidence on error
    
    def get_fallback_archetype(self) -> Dict:
        """Return safe fallback Tesla archetype when detection fails"""
        return {
            "archetype_key": "pragmatyczny_analityk",
            "archetype_name": "📊 Pragmatyczny Analityk",
            "description": "Fallback - bezpieczny wybór archetypu dla klientów Tesla",
            "confidence": 50,
            "key_traits": ["conscientiousness", "compliance_disc"],
            "sales_strategy": {
                "do": ["Dostarczaj dane i fakty", "Bądź cierpliwy", "Używaj języka profesjonalnego"],
                "dont": ["Nie naciskaj", "Nie używaj emocji", "Nie przyspieszaj decyzji"]
            },
            "motivation": "Bezpieczeństwo decyzji",
            "communication_style": "Profesjonalny i rzeczowy",
            "psychological_match": {
                "big_five_alignment": "5.0/10",
                "primary_drivers": ["conscientiousness", "compliance_disc"],
                "secondary_traits": []
            },
            "archetype_source": "fallback",
            "industry": "automotive_tesla"
        }

# Factory function for future industry adaptability
def create_archetype_service(industry: str = "tesla") -> BaseArchetypeService:
    """
    🏭 Factory function for creating industry-specific archetype services
    
    Args:
        industry: Industry type ("tesla", "real_estate", "finance", etc.)
        
    Returns:
        BaseArchetypeService: Industry-specific archetype service
        
    Future usage example:
        tesla_service = create_archetype_service("tesla")
        real_estate_service = create_archetype_service("real_estate")
    """
    if industry.lower() == "tesla":
        return TeslaArchetypeService()
    # Future implementations:
    # elif industry.lower() == "real_estate":
    #     return RealEstateArchetypeService()
    # elif industry.lower() == "finance":
    #     return FinanceArchetypeService()
    else:
        logger.warning(f"⚠️ Unknown industry '{industry}', defaulting to Tesla")
        return TeslaArchetypeService()

# Create default service instance
archetype_service = create_archetype_service("tesla")