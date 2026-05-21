---
name: archetypal-mapping
description: Prowadzi mapowanie męskiej jaźni (Moore-Gillette KWML) — 100 pytań behawioralnych, zapis JSON, analiza kwadrantów i cieni. Użyj przy archetypach, KWML, diagnozie męskości, mapowaniu cienia, diagnoza_surowe_dane.json, raport archetypowy.
---

# Mapowanie archetypów KWML

Pełny system prompt (rola, MCP, boot): **[PROMPT_SYSTEMOWY.md](../../../PROMPT_SYSTEMOWY.md)** w katalogu głównym repo.

## Szybki start

1. Wczytaj `diagnoza_surowe_dane.json`.
2. Jeśli `< 100` wpisów → **Faza 1** (reguły `kwml-faza1-*`, `kwml-core`).
3. Jeśli `= 100` → **Faza 2** (`kwml-faza2-analiza`, [reference-klucz.md](reference-klucz.md)).

## Faza 1 — checklist

```
- [ ] 1–3 pytania z dane/raport.md (kolejne id)
- [ ] Zero nazw archetypów/cieni
- [ ] Zapis: python scripts/zapisz_odpowiedz.py <id> "..." "..."
- [ ] Postęp X–Y / 100
- [ ] Prośba o przykład behawioralny przy ogólnikach
```

Pytania: linie 43–141 w `dane/raport.md` (numeracja 1–100 w tekście raportu).

## Faza 2 — checklist

```
- [ ] Potwierdź 100 unikalnych id
- [ ] Odczytaj reference-klucz.md + teorię z raport.md
- [ ] Profil % (4 kwadranty)
- [ ] Per archetyp: dojrzały / inflacja / deflacja
- [ ] Oscylacja między biegunami
- [ ] Złoty cień
- [ ] Zapisz diagnoza_raport.md (+ opcjonalnie diagnoza_wyniki.json)
```

## Wiedza i pamięć

- **claude-context:** `search_code` na `.../ARCHETYPY/dane` (pytania, klucz, PDF) — przed pełnym odczytem pliku
- **claude-mem:** `search` + `get_observations`, `project="ARCHETYPY"` — tylko historia sesji; stan ankiety z JSON
- Transkrypcja: kontekst w raporcie Fazy 2

## Szablon raportu

```markdown
# Mapa archetypowa — [data]

## Podsumowanie
[2–3 zdania]

## Profil kwadrantów
| Kwadrant | % | Dominanta |
|----------|---|-----------|

## Piramidy (per archetyp)
### Król / Wojownik / Mag / Kochanek
- Szczyt: …
- Cień aktywny: …
- Cień pasywny: …

## Oscylacje
…

## Złoty cień
…

## Kierunki integracji
1. …
```

## Delegacja

Długa sesja ankiety (50+ pytań): subagent `archetypal-analyst` — izoluje kontekst, trzyma zapis JSON.
