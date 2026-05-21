# ARCHETYPY

Agentyczna diagnostyka męskiej jaźni w modelu **King, Warrior, Magician, Lover** (Moore & Gillette) — 100 pytań behawioralnych, zapis lokalny, raport archetypowy w Cursorze (lub innym IDE z agentem).

## Szybki start (Cursor)

1. **Sklonuj** repozytorium i otwórz folder jako workspace.
2. Upewnij się, że plik **`diagnoza_surowe_dane.json`** istnieje w katalogu głównym — w repo jest już **pusty** (`[]`). Agent dopisuje tu odpowiedzi w trakcie ankiety.
3. W czacie napisz np.: *„Rozpocznij mapowanie archetypów”* lub *„Kontynuuj diagnostykę”*.
4. Agent korzysta z reguł `.cursor/rules/`, skilla **archetypal-mapping** i pliku **`PROMPT_SYSTEMOWY.md`**.

Nie musisz nic konfigurować poza otwarciem projektu — stan ankiety to zawsze ten jeden plik JSON.

## Jak to działa

| Faza | Warunek | Co się dzieje |
|------|---------|----------------|
| **1 — Diagnostyka** | Mniej niż 100 wpisów w JSON | Agent zadaje 1–3 pytania na turę (bez ujawniania nazw archetypów), zapisuje odpowiedzi |
| **2 — Analiza** | Dokładnie 100 wpisów | Profil kwadrantów, cienie, raport w `diagnoza_raport.md` |

Źródło pytań: `dane/raport.md`. Klucz punktowy (tylko Faza 2): `.cursor/skills/archetypal-mapping/reference-klucz.md`.

## Pliki stanu

| Plik | W repo | Opis |
|------|--------|------|
| `diagnoza_surowe_dane.json` | Tak (pusty `[]`) | Twoje odpowiedzi — **nie wrzucaj na GitHub z wypełnioną treścią** |
| `diagnoza_raport.md` | Nie (`.gitignore`) | Raport końcowy — generowany lokalnie |
| `diagnoza_wyniki.json` | Nie (`.gitignore`) | Opcjonalne metryki Fazy 2 |
| `diagnoza_surowe_dane.local.json` | Nie (`.gitignore`) | Kopia zapasowa postępu (tworzona przy końcu sesji) |

### Format wpisu w JSON

```json
{
  "id": 1,
  "pytanie": "Treść pytania z raportu…",
  "odpowiedz": "Twoja odpowiedź behawioralna…"
}
```

Zapis z terminala:

```bash
python scripts/zapisz_odpowiedz.py 1 "Treść pytania" "Twoja odpowiedź"
```

## Koniec pracy na dziś (backup)

Ankieta **nie musi** być skończona w jednej sesji — możesz odpowiedzieć np. tylko na 3 pytania i wrócić jutro. Gdy kończysz na dziś, napisz agentowi wprost, np. *„na dziś tyle”*, *„dobranoc”*, *„wrócę jutro”*.

Agent **automatycznie** zrobi kopię zapasową:

```bash
python scripts/backup_diagnoza.py
```

→ zapis do `diagnoza_surowe_dane.local.json` (poza Gitem). Przy następnym starcie kontynuujesz od pierwszego brakującego pytania w `diagnoza_surowe_dane.json`.

Backup możesz też odpalić ręcznie w każdej chwili (np. przed aktualizacją systemu).

## MCP (opcjonalnie, zalecane)

- **claude-context** — semantyczne wyszukiwanie w `dane/` (pytania, teoria) zamiast wczytywania całych plików.
- **claude-mem** — pamięć między sesjami (`project="ARCHETYPY"`). Stan ankiety i tak ma pierwszeństwo w **`diagnoza_surowe_dane.json`**.

## Folder `dane/`

| Plik | Zawartość |
|------|-----------|
| `raport.md` | 100 pytań + materiał do Fazy 2 (framework diagnostyczny) |
| `transkrypcja_film.md` | Transkrypcja filmu poniżej — kontekst do ilustracji w Fazie 2 |
| `*.pdf` | **Nie w repozytorium** — kup / dodaj własną kopię książki lokalnie |

## Źródła i atrybucja

Diagnostyka opiera się na modelu **King, Warrior, Magician, Lover** (Robert Moore, Douglas Gillette).

| Materiał | Autor / wydawca | Gdzie w projekcie |
|----------|-----------------|-------------------|
| Książka *King, Warrior, Magician, Lover* | Moore & Gillette — [Empik](https://www.empik.com/king-warrior-magician-lover-moore-robert-gillette-douglas,1470284,ksiazka-p) | PDF **nie** w repo; opcjonalnie własna kopia w `dane/` |
| Film „jak KURDE być Mężczyzną w XXI w.” | **Mosak Marcin** — [YouTube](https://www.youtube.com/watch?v=5nn9Ex3wTIg) | Transkrypcja: `dane/transkrypcja_film.md` |
| Raport diagnostyczny (100 pytań) | — | `dane/raport.md` |

**Film:** materiał jest publiczny na YouTube; w repozytorium jest transkrypcja, żeby agent mógł z niej korzystać w Fazie 2 (kontekst, przykłady). Autor, tytuł i link do oryginału są w nagłówku `transkrypcja_film.md` — to uzupełnienie modelu z książki, nie zamiennik.

**Książka:** bez PDF w repo; po sklonowaniu dodajesz legalną kopię lokalnie, jeśli chcesz cytować tekst Moore & Gillette w agencie.

## Prywatność

- Repozytorium publiczne zawiera **wyłącznie szablon** ankiety, nie cudze odpowiedzi.
- Przed `git push` sprawdź: `git diff diagnoza_surowe_dane.json` — powinien być pusty lub niecommitowany.
- Własny postęp możesz trzymać w `diagnoza_surowe_dane.local.json` (ignorowany przez Git).

## Struktura projektu

```
ARCHETYPY/
├── PROMPT_SYSTEMOWY.md      # Kanoniczna instrukcja agenta
├── diagnoza_surowe_dane.json # Stan ankiety (start: [])
├── scripts/zapisz_odpowiedz.py
├── scripts/backup_diagnoza.py
├── dane/
├── .cursor/
│   ├── rules/               # Fazy 1 i 2, źródła
│   ├── skills/archetypal-mapping/
│   └── agents/archetypal-analyst.md
└── README.md
```

## Autor repozytorium

Projekt pod agentyczne IDE (Cursor). Issues i PR mile widziane — bez udostępniania osobistych odpowiedzi w issue/PR.
