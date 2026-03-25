"""
Personeelskosten Dashboard
==========================
Een interactief dashboard voor inzicht in loonkosten, FTE-ontwikkeling en omzet.

Lokaal draaien:
    1. pip install streamlit pandas plotly
    2. streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import calendar

# ─────────────────────────────────────────────
# PAGINA CONFIGURATIE
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Personeelskosten Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# WACHTWOORDBEVEILIGING
# ─────────────────────────────────────────────
def check_wachtwoord() -> bool:
    """
    Toont een inlogscherm. Wachtwoord staat in Streamlit Secrets:
      [auth]
      wachtwoord = "jouw-wachtwoord"
    Lokaal: maak .streamlit/secrets.toml aan met bovenstaande inhoud.
    """
    # Haal wachtwoord op uit secrets (of gebruik fallback voor lokaal testen)
    try:
        correct_wachtwoord = st.secrets["auth"]["wachtwoord"]
    except Exception:
        correct_wachtwoord = "demo1234"  # Lokale fallback

    if "ingelogd" not in st.session_state:
        st.session_state.ingelogd = False

    if st.session_state.ingelogd:
        return True

    # Inlogscherm
    st.markdown("## 🔐 Inloggen")
    st.markdown("Dit dashboard is beveiligd. Voer het wachtwoord in om verder te gaan.")
    wachtwoord_input = st.text_input("Wachtwoord", type="password", placeholder="Voer wachtwoord in")

    if st.button("Inloggen", use_container_width=False):
        if wachtwoord_input == correct_wachtwoord:
            st.session_state.ingelogd = True
            st.rerun()
        else:
            st.error("❌ Onjuist wachtwoord. Probeer opnieuw.")

    st.stop()  # Voorkomt dat de rest van de app laadt
    return False

check_wachtwoord()

# ─────────────────────────────────────────────
# STYLING
# ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }
    h1, h2, h3 {
        font-family: 'DM Mono', monospace;
        letter-spacing: -0.5px;
    }
    .stMetric {
        background: #F8F9FA;
        border: 1px solid #E9ECEF;
        border-radius: 8px;
        padding: 16px !important;
    }
    .stMetric label {
        font-family: 'DM Mono', monospace !important;
        font-size: 11px !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #6C757D !important;
    }
    .block-container {
        padding-top: 2rem;
    }
    .vacature-box {
        background: #FFF8E1;
        border-left: 4px solid #FFC107;
        padding: 12px 16px;
        border-radius: 4px;
        margin: 8px 0;
    }
    div[data-testid="stSidebar"] {
        background: #1A1A2E;
    }
    div[data-testid="stSidebar"] * {
        color: #E8E8F0 !important;
    }
    div[data-testid="stSidebar"] .stSelectbox label,
    div[data-testid="stSidebar"] .stNumberInput label,
    div[data-testid="stSidebar"] .stDateInput label,
    div[data-testid="stSidebar"] .stTextInput label {
        color: #A0A0C0 !important;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    div[data-testid="stSidebar"] h2, 
    div[data-testid="stSidebar"] h3 {
        color: #FFFFFF !important;
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# DEMO DATA
# ─────────────────────────────────────────────
def laad_demo_medewerkers() -> pd.DataFrame:
    """Retourneert een DataFrame met voorbeeldmedewerkers."""
    return pd.DataFrame([
        {"naam": "Developer-01",       "afdeling": "Tech",       "uren_per_week": 40, "fte": 1.0, "bruto_maandsalaris": 5200, "startdatum": "2022-01-01", "einddatum": None},
        {"naam": "Developer-02",       "afdeling": "Tech",       "uren_per_week": 32, "fte": 0.8, "bruto_maandsalaris": 4100, "startdatum": "2022-03-01", "einddatum": None},
        {"naam": "Accountmanager-01",  "afdeling": "Sales",      "uren_per_week": 40, "fte": 1.0, "bruto_maandsalaris": 4500, "startdatum": "2021-06-01", "einddatum": None},
        {"naam": "Accountmanager-02",  "afdeling": "Sales",      "uren_per_week": 40, "fte": 1.0, "bruto_maandsalaris": 4800, "startdatum": "2022-09-01", "einddatum": None},
        {"naam": "HR-medewerker-01",   "afdeling": "HR",         "uren_per_week": 24, "fte": 0.6, "bruto_maandsalaris": 2700, "startdatum": "2023-01-01", "einddatum": None},
        {"naam": "Controller-01",      "afdeling": "Finance",    "uren_per_week": 40, "fte": 1.0, "bruto_maandsalaris": 5500, "startdatum": "2021-01-01", "einddatum": None},
        {"naam": "Developer-03",       "afdeling": "Tech",       "uren_per_week": 40, "fte": 1.0, "bruto_maandsalaris": 5800, "startdatum": "2023-04-01", "einddatum": None},
        {"naam": "Accountmanager-03",  "afdeling": "Sales",      "uren_per_week": 40, "fte": 1.0, "bruto_maandsalaris": 4200, "startdatum": "2023-07-01", "einddatum": "2024-06-30"},
        {"naam": "Marketeer-01",       "afdeling": "Marketing",  "uren_per_week": 40, "fte": 1.0, "bruto_maandsalaris": 4600, "startdatum": "2022-11-01", "einddatum": None},
        {"naam": "Marketeer-02",       "afdeling": "Marketing",  "uren_per_week": 32, "fte": 0.8, "bruto_maandsalaris": 3600, "startdatum": "2024-01-01", "einddatum": None},
    ])


def laad_demo_mutaties() -> pd.DataFrame:
    """Retourneert mutaties (salarisverhogingen, uren-wijzigingen, uitdienst)."""
    return pd.DataFrame([
        {"datum": "2024-01-01", "medewerker": "Developer-01",      "type": "salaris_wijziging", "nieuwe_waarde": 5500},
        {"datum": "2024-04-01", "medewerker": "Developer-02",      "type": "uren_wijziging",    "nieuwe_waarde": 40},
        {"datum": "2024-04-01", "medewerker": "Developer-02",      "type": "salaris_wijziging", "nieuwe_waarde": 5000},
        {"datum": "2024-07-01", "medewerker": "Accountmanager-01", "type": "salaris_wijziging", "nieuwe_waarde": 4800},
        {"datum": "2024-06-30", "medewerker": "Accountmanager-03", "type": "uitdienst",         "nieuwe_waarde": 0},
    ])


def laad_demo_omzet() -> pd.DataFrame:
    """Retourneert maandelijkse omzetcijfers."""
    maanden = pd.date_range("2024-01-01", periods=12, freq="MS")
    omzet = [95000, 102000, 110000, 108000, 115000, 125000,
             118000, 130000, 135000, 128000, 142000, 155000]
    return pd.DataFrame({"maand": maanden, "omzet": omzet})


# ─────────────────────────────────────────────
# BEREKENINGEN
# ─────────────────────────────────────────────
def bereken_maandelijkse_kosten(
    medewerkers: pd.DataFrame,
    mutaties: pd.DataFrame,
    maanden: list[date],
    vacatures: list[dict] | None = None,
    include_vacatures: bool = True,
) -> pd.DataFrame:
    """
    Berekent per maand de loonkosten en FTE per afdeling,
    inclusief mutaties en (optioneel) vacatures.
    """
    medewerkers = medewerkers.copy()
    mutaties = mutaties.copy()

    # Datums omzetten
    medewerkers["startdatum"] = pd.to_datetime(medewerkers["startdatum"])
    medewerkers["einddatum"] = pd.to_datetime(medewerkers["einddatum"])
    mutaties["datum"] = pd.to_datetime(mutaties["datum"])

    resultaten = []

    for maand in maanden:
        maand_start = pd.Timestamp(maand)
        maand_eind = maand_start + pd.offsets.MonthEnd(0)

        for _, mw in medewerkers.iterrows():
            # Is medewerker actief in deze maand?
            if mw["startdatum"] > maand_eind:
                continue
            if pd.notna(mw["einddatum"]) and mw["einddatum"] < maand_start:
                continue

            # Pas mutaties toe (chronologisch, tot en met einde maand)
            salaris = mw["bruto_maandsalaris"]
            uren = mw["uren_per_week"]

            relevante_mutaties = mutaties[
                (mutaties["medewerker"] == mw["naam"]) &
                (mutaties["datum"] <= maand_eind)
            ].sort_values("datum")

            for _, mut in relevante_mutaties.iterrows():
                if mut["type"] == "salaris_wijziging":
                    salaris = mut["nieuwe_waarde"]
                elif mut["type"] == "uren_wijziging":
                    uren = mut["nieuwe_waarde"]
                elif mut["type"] == "uitdienst":
                    salaris = 0  # Telt niet mee

            fte = uren / 40

            resultaten.append({
                "maand": maand_start,
                "naam": mw["naam"],
                "afdeling": mw["afdeling"],
                "salaris": salaris,
                "fte": fte,
                "type": "medewerker",
            })

        # Vacatures toevoegen
        if include_vacatures and vacatures:
            for vac in vacatures:
                vac_start = pd.Timestamp(vac["startdatum"])
                if vac_start <= maand_eind:
                    resultaten.append({
                        "maand": maand_start,
                        "naam": f"🔍 Vacature ({vac['afdeling']})",
                        "afdeling": vac["afdeling"],
                        "salaris": vac["salaris"],
                        "fte": vac["uren"] / 40,
                        "type": "vacature",
                    })

    return pd.DataFrame(resultaten)


def aggregeer_per_maand(df: pd.DataFrame) -> pd.DataFrame:
    """Groepeert op maand en berekent totale kosten + FTE."""
    return df.groupby("maand").agg(
        loonkosten=("salaris", "sum"),
        fte=("fte", "sum"),
    ).reset_index()


def aggregeer_per_afdeling_maand(df: pd.DataFrame) -> pd.DataFrame:
    """Groepeert op maand + afdeling."""
    return df.groupby(["maand", "afdeling"]).agg(
        loonkosten=("salaris", "sum"),
        fte=("fte", "sum"),
    ).reset_index()


# ─────────────────────────────────────────────
# PLOTLY STIJL HELPER
# ─────────────────────────────────────────────
KLEUREN = ["#2D6A4F", "#52B788", "#95D5B2", "#1B4332", "#74C69D",
           "#E76F51", "#F4A261", "#264653", "#2A9D8F", "#E9C46A"]

def fig_layout(fig, titel: str) -> go.Figure:
    """Past een consistente layout toe op alle grafieken."""
    fig.update_layout(
        title=dict(text=titel, font=dict(family="DM Mono", size=14), x=0),
        font=dict(family="DM Sans", size=12),
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="left", x=0),
        hovermode="x unified",
    )
    fig.update_xaxes(showgrid=False, linecolor="#DEE2E6")
    fig.update_yaxes(gridcolor="#F1F3F5", linecolor="#DEE2E6")
    return fig


# ─────────────────────────────────────────────
# SESSIE STATE INITIALISATIE
# ─────────────────────────────────────────────
if "medewerkers" not in st.session_state:
    st.session_state.medewerkers = laad_demo_medewerkers()
if "mutaties" not in st.session_state:
    st.session_state.mutaties = laad_demo_mutaties()
if "omzet" not in st.session_state:
    st.session_state.omzet = laad_demo_omzet()
if "vacatures" not in st.session_state:
    st.session_state.vacatures = []


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Instellingen")
    st.markdown("---")

    # Periode
    st.markdown("### 📅 Periode")
    col1, col2 = st.columns(2)
    with col1:
        start_jaar = st.selectbox("Van", [2023, 2024, 2025], index=1)
        start_maand = st.selectbox("Maand", range(1, 13), index=0, format_func=lambda m: calendar.month_abbr[m])
    with col2:
        eind_jaar = st.selectbox("Tot", [2024, 2025, 2026], index=0)
        eind_maand = st.selectbox("Maand ", range(1, 13), index=11, format_func=lambda m: calendar.month_abbr[m])

    # Vacatures toggle
    st.markdown("---")
    st.markdown("### 🔍 Vacatures")
    include_vacatures = st.toggle("Inclusief vacatures", value=True)

    # Vacature toevoegen
    with st.expander("➕ Vacature toevoegen"):
        afdelingen = list(st.session_state.medewerkers["afdeling"].unique())
        vac_afdeling = st.selectbox("Afdeling", afdelingen)
        vac_salaris = st.number_input("Bruto maandsalaris (€)", min_value=2000, max_value=15000, value=4500, step=100)
        vac_uren = st.number_input("Uren per week", min_value=8, max_value=40, value=40, step=4)
        vac_start = st.date_input("Verwachte startdatum", value=date.today())

        if st.button("Vacature toevoegen", use_container_width=True):
            st.session_state.vacatures.append({
                "afdeling": vac_afdeling,
                "salaris": vac_salaris,
                "uren": vac_uren,
                "startdatum": str(vac_start),
            })
            st.success(f"Vacature toegevoegd voor {vac_afdeling}")

    # Actieve vacatures tonen
    if st.session_state.vacatures:
        st.markdown("**Actieve vacatures:**")
        for i, vac in enumerate(st.session_state.vacatures):
            col_vac, col_del = st.columns([4, 1])
            with col_vac:
                st.markdown(f"<div class='vacature-box'>🔍 {vac['afdeling']}<br/>€{vac['salaris']:,} · {vac['uren']}u · vanaf {vac['startdatum']}</div>", unsafe_allow_html=True)
            with col_del:
                if st.button("✕", key=f"del_{i}"):
                    st.session_state.vacatures.pop(i)
                    st.rerun()


# ─────────────────────────────────────────────
# MAANDEN GENEREREN
# ─────────────────────────────────────────────
start_datum = date(start_jaar, start_maand, 1)
eind_datum = date(eind_jaar, eind_maand, 1)

maanden = []
d = start_datum
while d <= eind_datum:
    maanden.append(d)
    d = (d.replace(day=1) + timedelta(days=32)).replace(day=1)


# ─────────────────────────────────────────────
# BEREKENINGEN UITVOEREN
# ─────────────────────────────────────────────
df_detail = bereken_maandelijkse_kosten(
    st.session_state.medewerkers,
    st.session_state.mutaties,
    maanden,
    st.session_state.vacatures,
    include_vacatures,
)

df_maand = aggregeer_per_maand(df_detail)
df_afd = aggregeer_per_afdeling_maand(df_detail)

# Omzet koppelen
omzet = st.session_state.omzet.copy()
omzet["maand"] = pd.to_datetime(omzet["maand"])
df_omzet = df_maand.merge(omzet, on="maand", how="left")


# ─────────────────────────────────────────────
# DASHBOARD HEADER
# ─────────────────────────────────────────────
st.markdown("# 📊 Personeelskosten Dashboard")
st.markdown(f"*Periode: {calendar.month_name[start_maand]} {start_jaar} – {calendar.month_name[eind_maand]} {eind_jaar}*")

if include_vacatures and st.session_state.vacatures:
    st.info(f"ℹ️ {len(st.session_state.vacatures)} vacature(s) meegenomen in berekeningen.")

st.markdown("---")


# ─────────────────────────────────────────────
# KPI KAARTEN
# ─────────────────────────────────────────────
laatste_maand = df_maand.iloc[-1] if not df_maand.empty else None
eerste_maand = df_maand.iloc[0] if not df_maand.empty else None

if laatste_maand is not None:
    col1, col2, col3, col4 = st.columns(4)

    met_col1 = col1.metric(
        "💰 Loonkosten (laatste maand)",
        f"€ {laatste_maand['loonkosten']:,.0f}",
        delta=f"€ {laatste_maand['loonkosten'] - eerste_maand['loonkosten']:,.0f} vs start" if eerste_maand is not None else None,
    )

    gem_loonkosten = df_maand["loonkosten"].mean()
    col2.metric("📈 Gem. maandloonkosten", f"€ {gem_loonkosten:,.0f}")

    col3.metric("👥 FTE (laatste maand)", f"{laatste_maand['fte']:.1f} FTE")

    if not df_omzet.empty and df_omzet["omzet"].notna().any():
        laatste_omzet = df_omzet.dropna(subset=["omzet"]).iloc[-1]
        ratio = (laatste_omzet["loonkosten"] / laatste_omzet["omzet"]) * 100
        col4.metric("⚖️ Loonkosten / Omzet", f"{ratio:.1f}%")
    else:
        col4.metric("⚖️ Loonkosten / Omzet", "–")


st.markdown("---")


# ─────────────────────────────────────────────
# GRAFIEKEN
# ─────────────────────────────────────────────

# 1. Loonkosten per maand
col_g1, col_g2 = st.columns(2)

with col_g1:
    fig1 = go.Figure()
    fig1.add_trace(go.Bar(
        x=df_maand["maand"],
        y=df_maand["loonkosten"],
        marker_color=KLEUREN[0],
        name="Loonkosten",
        hovertemplate="€%{y:,.0f}<extra></extra>",
    ))
    fig_layout(fig1, "Loonkosten per maand")
    fig1.update_yaxes(tickprefix="€ ", tickformat=",.0f")
    st.plotly_chart(fig1, use_container_width=True)

# 2. Loonkosten per afdeling (gestapeld)
with col_g2:
    fig2 = go.Figure()
    afdelingen = df_afd["afdeling"].unique()
    for i, afd in enumerate(afdelingen):
        subset = df_afd[df_afd["afdeling"] == afd]
        fig2.add_trace(go.Bar(
            x=subset["maand"],
            y=subset["loonkosten"],
            name=afd,
            marker_color=KLEUREN[i % len(KLEUREN)],
            hovertemplate=f"{afd}: €%{{y:,.0f}}<extra></extra>",
        ))
    fig2.update_layout(barmode="stack")
    fig_layout(fig2, "Loonkosten per afdeling")
    fig2.update_yaxes(tickprefix="€ ", tickformat=",.0f")
    st.plotly_chart(fig2, use_container_width=True)


col_g3, col_g4 = st.columns(2)

# 3. FTE-ontwikkeling
with col_g3:
    fig3 = go.Figure()
    for i, afd in enumerate(afdelingen):
        subset = df_afd[df_afd["afdeling"] == afd]
        fig3.add_trace(go.Scatter(
            x=subset["maand"],
            y=subset["fte"],
            name=afd,
            mode="lines+markers",
            line=dict(color=KLEUREN[i % len(KLEUREN)], width=2),
            hovertemplate=f"{afd}: %{{y:.1f}} FTE<extra></extra>",
        ))
    fig_layout(fig3, "FTE-ontwikkeling per afdeling")
    fig3.update_yaxes(title_text="FTE")
    st.plotly_chart(fig3, use_container_width=True)

# 4. Omzet vs. loonkosten
with col_g4:
    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(
        x=df_omzet["maand"],
        y=df_omzet["omzet"],
        name="Omzet",
        mode="lines+markers",
        line=dict(color=KLEUREN[0], width=2),
        hovertemplate="Omzet: €%{y:,.0f}<extra></extra>",
    ))
    fig4.add_trace(go.Scatter(
        x=df_omzet["maand"],
        y=df_omzet["loonkosten"],
        name="Loonkosten",
        mode="lines+markers",
        line=dict(color=KLEUREN[5], width=2, dash="dash"),
        hovertemplate="Loonkosten: €%{y:,.0f}<extra></extra>",
    ))
    fig_layout(fig4, "Omzet vs. loonkosten")
    fig4.update_yaxes(tickprefix="€ ", tickformat=",.0f")
    st.plotly_chart(fig4, use_container_width=True)


# ─────────────────────────────────────────────
# DETAIL TABEL
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown("### 📋 Medewerkersoverzicht")

with st.expander("Bekijk medewerkers en mutaties"):
    tab1, tab2 = st.tabs(["Medewerkers", "Mutaties"])

    with tab1:
        st.dataframe(
            st.session_state.medewerkers.style.format({"bruto_maandsalaris": "€ {:,.0f}"}),
            use_container_width=True,
            hide_index=True,
        )

    with tab2:
        st.dataframe(st.session_state.mutaties, use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────
# VOET
# ─────────────────────────────────────────────
st.markdown("---")
st.caption("Personeelskosten Dashboard · Demo versie · Data wordt niet opgeslagen")
