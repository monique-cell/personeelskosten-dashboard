# 📊 Personeelskosten Dashboard

Interactief dashboard voor inzicht in loonkosten, FTE-ontwikkeling en omzet vs. personeelskosten.

---

## 🚀 Lokaal draaien

### 1. Vereisten installeren

```bash
pip install -r requirements.txt
```

### 2. Dashboard starten

```bash
streamlit run app.py
```

Het dashboard opent automatisch in je browser op `http://localhost:8501`.

---

## 📁 Projectstructuur

```
personeelskosten_dashboard/
├── app.py              # Hoofdapplicatie (Streamlit)
├── requirements.txt    # Python-afhankelijkheden
└── README.md           # Deze uitleg
```

---

## 🧩 Functionaliteit

| Feature | Beschrijving |
|---|---|
| **KPI kaarten** | Loonkosten, gem. maandkosten, FTE, loonkosten/omzet ratio |
| **Loonkosten per maand** | Staafgrafiek met historische ontwikkeling |
| **Loonkosten per afdeling** | Gestapelde staafgrafiek |
| **FTE-ontwikkeling** | Lijndiagram per afdeling |
| **Omzet vs. loonkosten** | Combinatiegrafiek |
| **Vacatures simuleren** | Voeg vacatures toe via de sidebar; toggle aan/uit |
| **Mutaties** | Salarisverhogingen, uren-aanpassingen en uitdienst worden correct verwerkt |

---

## 📊 Eigen data toevoegen

De functies `laad_demo_medewerkers()`, `laad_demo_mutaties()` en `laad_demo_omzet()` 
in `app.py` retourneren demo DataFrames. Vervang deze door je eigen data:

```python
# Optie 1: CSV inladen
medewerkers = pd.read_csv("medewerkers.csv")

# Optie 2: Excel inladen
medewerkers = pd.read_excel("medewerkers.xlsx")

# Optie 3: Database (bijv. PostgreSQL)
import sqlalchemy
engine = sqlalchemy.create_engine("postgresql://...")
medewerkers = pd.read_sql("SELECT * FROM medewerkers", engine)
```

### Vereiste kolommen per tabel

**Medewerkers:**
- `naam`, `afdeling`, `uren_per_week`, `fte`, `bruto_maandsalaris`, `startdatum`, `einddatum`

**Mutaties:**
- `datum`, `medewerker`, `type` (`salaris_wijziging` / `uren_wijziging` / `uitdienst`), `nieuwe_waarde`

**Omzet:**
- `maand` (eerste dag van de maand), `omzet`

---

## 🔧 Uitbreidingsideeën

- Werkgeverslasten toevoegen (bijv. 30% opslag)
- Export naar Excel of PDF
- Meerdere scenario's vergelijken
- Koppelingen met HR-systemen (AFAS, Exact, etc.)
- Alerting bij overschrijden loonkostenbudget
