<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# **Prompt Badawczy \#2: Moduł Scenariuszy Sprzedażowych**

**Cel:** Stworzenie kompletnych, wieloetapowych scenariuszy rozmów, które łączą nasze atomowe "taktyki" w spójne strategie dostosowane do konkretnych archetypów klientów.
**Źródła:** Metodologie sprzedaży (SPIN Selling, The Challenger Sale, MEDDIC), wewnętrzne materiały szkoleniowe firm, blogi i książki o procesach sprzedażowych.
**Zadanie:** Dla **każdego z kluczowych Archetypów** (zacznij od `Pragmatycznego Analityka` i `Strażnika Rodziny`), opracuj kompletny scenariusz sprzedażowy, który obejmuje następujące fazy:
**Faza Otwarcia:** Jakie pytania zadać na początku, aby potwierdzić archetyp?
**Faza Diagnozy Potrzeb:** Jakie taktyki (np. pytania SPIN) zastosować, aby odkryć kluczowe problemy i potrzeby klienta?
**Faza Prezentacji Rozwiązania:** Jak przedstawić Teslę, aby odpowiedzieć na zdiagnozowane potrzeby?
**Faza Obsługi Kluczowych Obiekcji:** Jakie 2-3 obiekcje są najbardziej prawdopodobne dla tego archetypu i jak je zbić?
**Faza Zamknięcia:** Jaka technika zamknięcia sprzedaży będzie najskuteczniejsza?
**Format Wyjściowy:** Twórz "bryłki wiedzy" z nowym `type: "sales_scenario"`. W polu `content` opisz poszczególne fazy. W polu `related_ids` **umieść ID istniejących 'taktyk' i 'faktów'**, które należy wykorzystać w danym scenariuszu.
**Przykład:**
{
"id": "SALES\_SCENARIO\_PRAGMATIC\_ANALYST\_001",
"type": "sales\_scenario",
"title": "Scenariusz rozmowy z Pragmatycznym Analitykiem",
"content": "1. Otwarcie: Potwierdź archetyp pytaniem o proces decyzyjny ('Jakie dane są dla Pana kluczowe przy wyborze auta?'). 2. Diagnoza: Skup się na kosztach obecnego auta (pytania o problem w SPIN). 3. Prezentacja: Pokaż analizę TCO, a nie przyspieszenie. 4. Obiekcje: Bądź gotów na obiekcje dotyczące ceny zakupu. 5. Zamknięcie: Zamknij sprzedaż na podstawie kalkulacji ROI, pokazując, że decyzja jest finansowo optymalna.",
"tags": ["scenariusz", "pragmatyczny\_analityk", "proces\_sprzedazy", "tco", "roi"],
"archetype\_filter": ["pragmatyczny\_analityk"],
"source": "Metodologia sprzedaży konsultacyjnej",
"related\_ids": [
"SALES\_TACTIC\_TCO\_PRESENTATION\_001",
"ACCOUNTING\_TCO\_COMPARISON\_001",
"SALES\_TACTIC\_OBJECTION\_PRICE\_001"
]
}

```json
{
  "id": "SALES_SCENARIO_PRAGMATIC_ANALYST_001",
  "type": "sales_scenario",
  "title": "Scenariusz rozmowy z Pragmatycznym Analitykiem",
  "content": "1. Faza Otwarcia: Rozpocznij od pytania o kryteria decyzyjne oraz zbierania danych. Zapytaj: 'Jakie parametry są dla Pana kluczowe przy wyborze auta? Na co zwraca Pan szczególną uwagę – koszty, gwarancję, technologię, a może TCO?' Pozwala to potwierdzić archetyp analityka i zbudować zaufanie.\n2. Faza Diagnozy Potrzeb: Użyj pytań SPIN. Skup się na kosztach bieżących i ukrytych obecnego auta ('Jakie są największe wyzwania kosztowe przy obecnej flocie? Ile obecnie kosztuje serwis/ubezpieczenie/paliwo rocznie?'). Zadawaj pytania o oczekiwania dotyczące ROI oraz planowanej długości użytkowania auta.\n3. Faza Prezentacji Rozwiązania: Pokaż twarde kalkulacje — porównaj TCO Tesli i referencyjnego auta spalinowego (np. BMW), zaprezentuj arkusz opłacalności, ROI, wyliczenia oszczędności rocznych i wpływ amortyzacji, podkreśl technologiczną przewagę OTA i Superchargera.\n4. Faza Obsługi Kluczowych Obiekcji: Najczęstsze obiekcje: (a) 'Tesla jest za droga' – zbij wyliczeniem TCO z 3 lat oraz wyższą wartością odsprzedaży, (b) 'Obawy o zasięg / ładowanie' – pokaż mapę i parametry Superchargerów, (c) 'Koszt serwisu/ubezpieczenia' – przywołaj niższe koszty serwisu oraz fakt, że OC dla Tesli jest tańsze vs spalinowe premium.\n5. Faza Zamknięcia: Zamknij sprzedaż przez logiczny lead-out w stylu Challenger lub SPIN: 'Porównując bilans, Tesla wychodzi taniej przy niższym ryzyku i wyższej wartości po zakończeniu umowy – kiedy robimy jazdę testową lub pierwszą kalkulację rezerwacji?'",
  "tags": ["scenariusz", "pragmatyczny_analityk", "tco", "spinselling", "challenger", "roi", "supercharger"],
  "archetype_filter": ["pragmatyczny_analityk"],
  "source": "Metodologia sprzedaży konsultacyjnej, SPIN, Challenger Sale",
  "related_ids": [
    "SALES_TACTIC_TCO_PRESENTATION_001",
    "SALES_TACTIC_OBJECTION_PRICE_001",
    "ACCOUNTING_TCO_COMPARISON_001",
    "OBJECTION_RANGE_ANXIETY_001",
    "OBJECTION_PRICE_HIGH_001"
  ]
}
```

```json
{
  "id": "SALES_SCENARIO_FAMILY_GUARDIAN_001",
  "type": "sales_scenario",
  "title": "Scenariusz rozmowy ze Strażnikiem Rodziny",
  "content": "1. Faza Otwarcia: Potwierdź archetyp pytaniami o priorytety rodziny i bezpieczeństwo: 'Jakie są dla Pana najważniejsze kwestie przy wyborze auta rodzinnego? Na co zwraca Pan uwagę w kontekście komfortu i ochrony bliskich?'\n2. Faza Diagnozy Potrzeb: Użyj SPIN, koncentrując się na pytaniach o codzienny komfort i lęki związane z użytkowaniem auta ('Czego najbardziej obawia się Pan na trasie? Jak często podróżuje Pan z dziećmi? Jakie rozwiązania ułatwiają organizację rodzinnej logistyki?').\n3. Faza Prezentacji Rozwiązania: Skup się na bezpieczeństwie (5-gwiazdek NHTSA, statystykach wypadków), realnych funkcjach chroniących rodzinę (HEPA – Bioweapon Defense, Sentry Mode, asysty kierowcy, ochrona dzieci). Podkreśl ponadprzeciętną pojemność bagażnika, praktyczność, niskie koszty eksploatacji, łatwość użytkowania dla całej rodziny.\n4. Faza Obsługi Kluczowych Obiekcji: Typowe obiekcje: (a) 'Co z bezpieczeństwem baterii/aut na prąd?' – zbij statystykami pożarów i argumentem o chemii LFP/HEPA, (b) 'Co jeśli auto odmówi posłuszeństwa w trasie z dziećmi?' – wytłumacz sieć Supercharger i wsparcie 24h/7, (c) 'Czy to wygodne na co dzień?' – podkreśl domowe ładowanie, automatykę, brak tłumika, ochronę zdrowia (HEPA vs smog/palenie).\n5. Faza Zamknięcia: Zamknij sprzedaż narracją bezpieczeństwa oraz opieki: 'Podejmując decyzję, daje Pan rodzinie najbezpieczniejsze auto na rynku i codzienny komfort bez kompromisów – kiedy najlepiej przetestować Model Y całą rodziną?'",
  "tags": ["scenariusz", "straznik_rodziny", "bezpieczenstwo", "hepa", "familycar", "praktycznosc"],
  "archetype_filter": ["straznik_rodziny"],
  "source": "Metodologia SPIN Selling, konsultacje rodzinne, szkolenia EV",
  "related_ids": [
    "TECHNICAL_SAFETY_IMPACT_001",
    "PRODUCT_BIOWEAPON_DEFENSE_TACTIC_001",
    "PRODUCT_SENTRY_MODE_DRAIN_001",
    "TECHNICAL_MODEL3_BAGAZNIK_001",
    "PRODUCT_BIOWEAPON_DEFENSE_001",
    "TECHNICAL_THERMAL_RUNAWAY_TACTIC_001"
  ]
}
```

<div style="text-align: center">⁂</div>

[^1]: Brylki-wiedzy-Wskazniki-psychometryczne-Big-Five.md

[^2]: knowledge_base_pl.json

[^3]: knowledge_base_pl_corrected.json

[^4]: https://jurnal.unived.ac.id/index.php/er/article/view/5509

[^5]: https://www.nature.com/articles/s41586-024-07033-8

[^6]: https://link.aps.org/doi/10.1103/PhysRevLett.128.203201

[^7]: https://advanced.onlinelibrary.wiley.com/doi/10.1002/adma.202415142

[^8]: https://onlinelibrary.wiley.com/doi/10.1002/adfm.202300175

[^9]: https://onlinelibrary.wiley.com/doi/10.1002/lpor.202402051

[^10]: https://link.aps.org/doi/10.1103/PhysRevApplied.22.064081

[^11]: http://www.emerald.com/apjml/article/37/6/1503-1527/1263149

[^12]: https://advanced.onlinelibrary.wiley.com/doi/10.1002/advs.202412688

[^13]: http://www.emerald.com/mbe/article/24/1/69-89/285596

[^14]: http://arxiv.org/pdf/1804.02037.pdf

[^15]: https://arxiv.org/pdf/2502.13334.pdf

[^16]: https://essuir.sumdu.edu.ua/bitstream/123456789/85574/1/Kozludzhova_mmi_3_2021.pdf

[^17]: https://journals.sagepub.com/doi/10.1177/10422587221102110

[^18]: https://dx.plos.org/10.1371/journal.pone.0273124

[^19]: http://www.scielo.cl/pdf/jotmi/v5n3/art04.pdf

[^20]: http://sceco.ub.ro/index.php/SCECO/article/download/348/327

[^21]: https://arxiv.org/pdf/2011.14822.pdf

[^22]: https://pmc.ncbi.nlm.nih.gov/articles/PMC9858020/

[^23]: https://timreview.ca/sites/default/files/article_PDF/GilbertDavies_TIMReview_October2011_1.pdf

[^24]: https://www.highspot.com/blog/spin-selling/

[^25]: https://www.zendesk.com/blog/spin-selling/

[^26]: https://www.lucidchart.com/blog/the-4-steps-to-spin-selling

[^27]: https://rep.ai/blog/spin-selling

[^28]: https://www.salesforce.com/blog/spin-selling/

[^29]: https://challengerinc.com/the-challenger-customer-profiles/

[^30]: https://www.close.com/blog/meddic-sales-methodology

[^31]: https://www.salesenablementcollective.com/spin-sales-methodology/

[^32]: https://www.pipedrive.com/en/blog/challenger-sales-model

[^33]: https://www.atlassian.com/blog/project-management/meddic-sales-methodology

[^34]: https://blog.hubspot.com/sales/spin-selling-the-ultimate-guide

[^35]: https://www.salesforce.com/blog/challenger-sales-methodology/

[^36]: https://www.highspot.com/blog/meddic-sales-methodology/

[^37]: https://www.salesodyssey.com/blog/spin-selling

[^38]: https://www.b2bsell.com/challenger-customer/

[^39]: https://miro.com/process-mapping/meddic-sales-process-explained/

[^40]: https://www.salesforce.com/blog/meddic-sales/

