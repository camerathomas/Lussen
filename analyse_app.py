import streamlit as st
import re
import json
import math
from bs4 import BeautifulSoup
import google.generativeai as genai
import plotly.graph_objects as go
import networkx as nx

# === INSTELLINGEN ===
st.set_page_config(page_title="DenkKrant Analyse", layout="wide")

# === DE SLEUTEL ===
SLEUTEL = """
Je bent een analysemachine die werkt met een universele sleutel van processen.

DE SLEUTEL:
1. Alles verandert.
2. Verandering verloopt in lussen: opkomen -> bloeien -> ondergaan -> nieuwe generatie.
3. Elke lus begint met een trigger: een interactie met de omgeving.
4. Triggers kunnen extern, intern of gemengd zijn.
5. Lussen hebben een selectiecriterium: wat overleeft, gaat door.
6. Lussen hebben een snelheid, vorm, plaats en tijd.
7. Lussen zijn ingebed in een omgeving die zelf verandert.
8. Lussen kunnen cumulatief zijn: elke generatie bouwt voort op de vorige.
9. Als een lus niet voltooit, gaat het materiaal door in een andere lus.
10. Het geheel van lussen heeft een eigen dynamiek: emergent, niet reduceerbaar.
11. Vanaf de terugkoppeling ontstaat intentionaliteit.
12. Intentionele lussen kunnen kiezen, leren en doelen stellen.
13. Universele processen sturen het gedrag: zelfhandhaving, voortplanting, groei, herstel, differentiatie.
14. Een lus an sich is niets; hij bestaat alleen in relatie tot andere lussen.
15. De basis van elke verhouding is terugkoppeling: geven en nemen.
16. De krachten die de verhouding bepalen zijn zelf ook lussen.

JOUW TAAK:
Je levert ALTIJD alle onderstaande onderdelen, in deze exacte volgorde, met duidelijke koppen.
Sla geen enkel onderdeel over. Als een onderdeel niet van toepassing is, schrijf je "niet van toepassing" en leg je uit waarom.

=== DEEL 1: LUSSENANALYSE ===
1. Identificeer alle lussen (processen).
2. Identificeer de triggers voor elke lus.
3. Identificeer de terugkoppelingen tussen lussen.
4. Identificeer de tijd, plaats, vorm en snelheid van elke lus.
5. Identificeer de verhoudingen tussen lussen.
6. Identificeer de krachten die de verhoudingen beïnvloeden.
7. Identificeer het selectiecriterium.
8. Identificeer de emergentie van het geheel.
9. Geef expliciet aan welke variabelen ontbreken.
10. Geef een analyse van de actuele situatie en mogelijke ontwikkelingen.

=== DEEL 2: VERBORGEN PREMISSEN ===
Analyseer de tekst op verborgen premissen: aannames die de schrijver niet expliciet maakt,
maar die wel nodig zijn om de conclusies te laten kloppen.

Voor elke verborgen premisse:
1. Citeer de passage waar de premisse impliciet blijft.
2. Formuleer de verborgen premisse in één heldere zin.
3. Leg uit waarom deze premisse nodig is voor de redenering.
4. Geef aan of de premisse aanvaardbaar, twijfelachtig of onjuist is.
5. Als de premisse onjuist is, leg uit welk effect dat heeft op de conclusie.

Let op: enthymeem, verzwegen waardeoordeel, verzwegen definitie,
verzwegen oorzaak-gevolg relatie, verzwegen autoriteit, verzwegen algemene regel.
Geef maximaal 5 verborgen premissen, geordend op belangrijkheid.

=== DEEL 3: EMOTIONELE LUSSEN EN PERSPECTIEVEN ===
Gevoelens zijn zelf lussen. Splits de betrokken partijen uit.

Voor elke groep of persoon in de tekst:
- Wie is het?
- Wat is hun positie? (machtig, machteloos, afhankelijk, neutraal)
- Wat voelen zij waarschijnlijk?
- Met wie identificeren zij zich?
- Wat willen zij?

Geef een tabel:
| Groep | Positie | Mogelijke gevoelens | Wat zij willen |

Geef aan:
- Welke gevoelens tegen elkaar worden opgewogen.
- Welke groepen zich machteloos voelen.
- Wiens gevoelens niet genoemd worden.

=== DEEL 4: JIP-EN-JANNEKE-VERTALING ===
Vertaal de analyse naar Jip-en-Janneke-taal.
- Maximaal 300 woorden.
- Minimaal één metafoor of beeld.
- Noem de belangrijkste lus en de belangrijkste terugkoppeling.
- Leg uit wat het geheel zwak of sterk maakt.
- Vermijd jargon.

=== DEEL 5: SPREEKWOORDEN ===
Geef 3 tot 5 spreekwoorden, uitdrukkingen of allegorieën die van toepassing zijn.
Voor elk spreekwoord:
- Noem het spreekwoord.
- Leg in één zin uit waarom het past.
- Koppel het aan een specifieke lus of verhouding.
- Geef aan of het de situatie volledig dekt of slechts een deel.

=== DEEL 6: UNIVERSELE VERGELIJKING ===
Zoek naar het overheersende patroon en vergelijk het met 3 tot 5 andere domeinen:
plantenrijk, dierenrijk, natuurkunde, kosmos, maatschappij, economie,
technologie, menselijk lichaam, spel, verhaal.

Voor elk domein:
1. Noem het domein.
2. Beschrijf het vergelijkbare patroon.
3. Leg uit waarom het vergelijkbaar is.
4. Geef aan waar de vergelijking NIET opgaat.
5. Trek een conclusie: wat leert deze vergelijking ons?

=== DEEL 7: SOCIALE-MEDIA-REACTIES ===
Schrijf drie reacties voor sociale media:

STIJL A — COMPASSIE (max 100 woorden)
STIJL B — ANALYTISCH (max 120 woorden)
STIJL C — MENSELIJK (max 100 woorden)

=== DEEL 8: GESTRUCTUREERDE OUTPUT VOOR GRAFIEK ===
Geef na de tekstuele analyse een JSON-blok, tussen de markeringen
=== JSON === en === EINDE JSON ===.

{
  "lussen": [
    {"id": "A", "naam": "korte naam", "tijdschaal": "seconden|minuten|dagen|maanden|jaren|decennia", "omvang": 1-5, "domein": "biologisch|maatschappelijk|economisch|politiek|cultureel"}
  ],
  "triggers": [
    {"naar": "A", "label": "korte beschrijving"}
  ],
  "terugkoppelingen": [
    {"van": "A", "naar": "B", "sterkte": 1-5, "type": "versterkend|verzwakkend", "label": "korte beschrijving"}
  ],
  "krachten": [
    {"naam": "korte naam", "op": ["A", "B"]}
  ]
}

BELANGRIJK:
- De lussen komen UIT DE TEKST. Verzin geen lussen die er niet zijn.
- Gebruik alleen letters A, B, C, ... als id's.
- "omvang" en "sterkte" zijn 1 (klein/zwak) tot 5 (groot/sterk).
- De JSON moet geldig zijn: geen commentaar, geen trailing comma's.

=== BELANGRIJK ===
- Wees precies. Verzin niets. Als iets niet in de tekst staat, zeg dat dan.
- Sla geen enkel deel over.
- Gebruik duidelijke koppen.
"""

# === TOEKOMST-SLEUTEL ===
TOEKOMST_SLEUTEL = """
Je bent een toekomstanalysemachine die werkt met de universele lussen-sleutel.

Je krijgt zo:
1. De originele tekst.
2. De volledige lussen-analyse die al is gemaakt.
3. De JSON met lussen, triggers en terugkoppelingen.

JOUW TAAK:
Werk 3 tot 5 toekomstscenario's uit op basis van de interactie tussen de lussen.
Elk scenario heeft deze vorm:

- Naam
- Conditie: ALS [lus/terugkoppeling/trigger verandert op deze manier], DAN ...
- Dominante lussen
- Lussen die overspannen raken of wegvallen
- Kantelende terugkoppelingen (versterkend <-> verzwakkend)
- Tijdschaal
- Kansband: klein / mogelijk / groot — met onderbouwing
- Status: GEFUNDEERD (direct afgeleid uit de analyse) of SPECULATIEF (vereist aanname)

Werk minimaal één scenario uit waarin een NIEUWE lus van buitenaf
de omgeving binnendringt en de bestaande verhoudingen sterk verandert.
Noem die externe lus expliciet en leg uit welke bestaande verhoudingen
erdoor kantelen.

BELANGRIJK: Gebruik exact dezelfde lus-id's (A, B, C, ...) als in de
aangeleverde JSON. Verzin geen nieuwe id's voor bestaande lussen.
Externe lussen krijgen id's als X, Y, Z.

Sluit af met een JSON-blok tussen === JSON === en === EINDE JSON ===:

{
  "scenarios": [
    {
      "id": "S1",
      "naam": "...",
      "conditie": "...",
      "kans": "klein|mogelijk|groot",
      "status": "gefundeerd|speculatief",
      "dominante_lussen": ["A"],
      "kantelpunten": ["B"],
      "externe_lussen": [
        {"id": "X", "naam": "...", "beschrijving": "..."}
      ],
      "tijdschaal": "maanden"
    }
  ]
}

De JSON moet geldig zijn: geen commentaar, geen trailing comma's.
Sla geen enkel onderdeel over.
"""


# === TEKST OPSCHONEN ===
def schoon_html(html_tekst):
    soup = BeautifulSoup(html_tekst, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "aside",
                     "figcaption", "figure", "iframe", "form"]):
        tag.decompose()
    onderdelen = []
    for tag in soup.find_all(["h1", "h2", "h3", "p"]):
        tekst = tag.get_text(strip=True)
        if tekst:
            onderdelen.append(tekst)
    return "\n\n".join(onderdelen)


def schoon_platte_tekst(tekst):
    tekst = re.sub(r'https?://\S+', '', tekst)
    tekst = re.sub(r'\S+@\S+', '', tekst)
    rommel = [
        r'^Lees ook:.*$', r'^Foto:.*$', r'^Beeld:.*$',
        r'^Deel dit artikel.*$', r'^Advertentie.*$', r'^Cookie.*$',
        r'^Accepteer.*$', r'^\s*$',
    ]
    for patroon in rommel:
        tekst = re.sub(patroon, '', tekst, flags=re.MULTILINE | re.IGNORECASE)
    tekst = re.sub(r'\n{3,}', '\n\n', tekst)
    return tekst.strip()


def maak_schoon(ruwe_tekst):
    if "<" in ruwe_tekst and ">" in ruwe_tekst:
        return schoon_html(ruwe_tekst)
    return schoon_platte_tekst(ruwe_tekst)


# === LUSSEN-GRAFIEK (bestaand) ===
def teken_lussen_grafiek(structuur):
    lussen = structuur.get("lussen", [])
    terugkoppelingen = structuur.get("terugkoppelingen", [])
    triggers = structuur.get("triggers", [])

    if not lussen:
        return None

    G = nx.Graph()
    for lus in lussen:
        G.add_node(lus["id"])
    for tb in terugkoppelingen:
        if tb["van"] in G and tb["naar"] in G:
            G.add_edge(tb["van"], tb["naar"], weight=tb.get("sterkte", 1))

    pos = nx.spring_layout(G, k=0.8, iterations=100, seed=42)

    kleur_map = {
        "seconden": "#ef4444", "minuten": "#f97316",
        "dagen": "#eab308", "maanden": "#22c55e",
        "jaren": "#3b82f6", "decennia": "#8b5cf6",
    }

    fig = go.Figure()

    for tb in terugkoppelingen:
        if tb["van"] not in pos or tb["naar"] not in pos:
            continue
        van = pos[tb["van"]]
        naar = pos[tb["naar"]]
        sterkte = tb.get("sterkte", 1)
        kleur = "#ef4444" if tb.get("type") == "versterkend" else "#3b82f6"

        fig.add_trace(go.Scatter(
            x=[van[0], naar[0]], y=[van[1], naar[1]],
            mode="lines",
            line=dict(width=sterkte * 1.5, color=kleur),
            hoverinfo="text",
            text=[tb.get("label", ""), tb.get("label", "")],
            showlegend=False,
        ))

    for lus in lussen:
        if lus["id"] not in pos:
            continue
        x, y = pos[lus["id"]]
        kleur = kleur_map.get(lus.get("tijdschaal", "maanden"), "#94a3b8")
        grootte = lus.get("omvang", 3) * 15

        fig.add_trace(go.Scatter(
            x=[x], y=[y],
            mode="markers+text",
            marker=dict(size=grootte, color=kleur,
                        line=dict(width=2, color="white")),
            text=[f"{lus['id']}: {lus['naam']}"],
            textposition="middle center",
            hoverinfo="text",
            hovertext=f"{lus['naam']}<br>Tijdschaal: {lus.get('tijdschaal', '?')}",
            showlegend=False,
        ))

    for trigger in triggers:
        if trigger["naar"] not in pos:
            continue
        naar = pos[trigger["naar"]]
        hoek = math.atan2(naar[1], naar[0])
        x = naar[0] + 0.2 * math.cos(hoek)
        y = naar[1] + 0.2 * math.sin(hoek)

        fig.add_trace(go.Scatter(
            x=[x], y=[y],
            mode="markers+text",
            marker=dict(size=15, color="#facc15", symbol="star"),
            text=[trigger.get("label", "")],
            textposition="top center",
            hoverinfo="text",
            hovertext=trigger.get("label", ""),
            showlegend=False,
        ))

    fig.update_layout(
        title="Lussen-netwerk",
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor="#0f172a",
        paper_bgcolor="#0f172a",
        font=dict(color="white"),
        height=700,
        margin=dict(l=20, r=20, t=50, b=20),
    )
    return fig


# === SCENARIO-GRAFIEK (nieuw) ===
def teken_scenario_grafiek(structuur, scenario):
    lussen = {l["id"]: l for l in structuur.get("lussen", [])}
    terugkoppelingen = structuur.get("terugkoppelingen", [])

    dominante = set(scenario.get("dominante_lussen", []))
    kantelpunten = set(scenario.get("kantelpunten", []))
    externe = scenario.get("externe_lussen", [])

    alle_ids = set(lussen.keys()) | {e["id"] for e in externe}
    if not alle_ids:
        return None

    G = nx.Graph()
    for nid in alle_ids:
        G.add_node(nid)
    for tb in terugkoppelingen:
        if tb["van"] in G and tb["naar"] in G:
            G.add_edge(tb["van"], tb["naar"], weight=tb.get("sterkte", 1))
    for e in externe:
        if e["id"] not in G:
            G.add_node(e["id"])

    pos = nx.spring_layout(G, k=0.9, iterations=100, seed=42)

    kleur_map = {
        "seconden": "#ef4444", "minuten": "#f97316",
        "dagen": "#eab308", "maanden": "#22c55e",
        "jaren": "#3b82f6", "decennia": "#8b5cf6",
    }

    fig = go.Figure()

    for tb in terugkoppelingen:
        if tb["van"] not in pos or tb["naar"] not in pos:
            continue
        van = pos[tb["van"]]
        naar = pos[tb["naar"]]
        sterkte = tb.get("sterkte", 1)
        kleur = "#ef4444" if tb.get("type") == "versterkend" else "#3b82f6"

        fig.add_trace(go.Scatter(
            x=[van[0], naar[0]], y=[van[1], naar[1]],
            mode="lines",
            line=dict(width=sterkte * 1.5, color=kleur),
            hoverinfo="text",
            text=[tb.get("label", ""), tb.get("label", "")],
            showlegend=False,
        ))

    for lus in lussen.values():
        if lus["id"] not in pos:
            continue
        x, y = pos[lus["id"]]
        kleur = kleur_map.get(lus.get("tijdschaal", "maanden"), "#94a3b8")
        grootte = lus.get("omvang", 3) * 15

        if lus["id"] in dominante:
            grootte *= 1.4
        rand_kleur = "#ef4444" if lus["id"] in kantelpunten else "white"
        rand_breedte = 4 if lus["id"] in kantelpunten else 2

        fig.add_trace(go.Scatter(
            x=[x], y=[y],
            mode="markers+text",
            marker=dict(size=grootte, color=kleur,
                        line=dict(width=rand_breedte, color=rand_kleur)),
            text=[f"{lus['id']}: {lus['naam']}"],
            textposition="middle center",
            hoverinfo="text",
            hovertext=f"{lus['naam']}<br>Tijdschaal: {lus.get('tijdschaal', '?')}",
            showlegend=False,
        ))

    for e in externe:
        if e["id"] not in pos:
            continue
        x, y = pos[e["id"]]
        fig.add_trace(go.Scatter(
            x=[x], y=[y],
            mode="markers+text",
            marker=dict(size=25, color="#f472b6", symbol="diamond",
                        line=dict(width=2, color="white")),
            text=[f"{e['id']}: {e['naam']}"],
            textposition="middle center",
            hoverinfo="text",
            hovertext=f"EXTERN — {e.get('beschrijving', '')}",
            showlegend=False,
        ))

    fig.update_layout(
        title=f"Scenario {scenario.get('id', '?')}: {scenario.get('naam', '')}",
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor="#0f172a",
        paper_bgcolor="#0f172a",
        font=dict(color="white"),
        height=600,
        margin=dict(l=20, r=20, t=50, b=20),
    )
    return fig


# === UI ===
st.title("DenkKrant — Universele Analyse")
st.markdown("Plak een tekst en laat de sleutel zijn werk doen.")

api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    st.error("Geen API-sleutel gevonden. Stel GEMINI_API_KEY in via de Secrets.")

# State initialiseren
if "analyse_klaar" not in st.session_state:
    st.session_state.analyse_klaar = False
if "volledige_tekst" not in st.session_state:
    st.session_state.volledige_tekst = ""
if "structuur" not in st.session_state:
    st.session_state.structuur = None
if "schone_tekst" not in st.session_state:
    st.session_state.schone_tekst = ""
if "toekomst_tekst" not in st.session_state:
    st.session_state.toekomst_tekst = ""
if "toekomst_structuur" not in st.session_state:
    st.session_state.toekomst_structuur = None

ruwe_tekst = st.text_area(
    "Plak hier je tekst",
    height=300,
    placeholder="Plak een artikel van minimaal 800 woorden..."
)

# === KNOP 1: ANALYSE ===
if st.button("Analyseer", type="primary"):
    if not api_key:
        st.error("Geen API-sleutel gevonden.")
    elif not ruwe_tekst or len(ruwe_tekst.split()) < 100:
        st.error("De tekst is te kort.")
    else:
        with st.spinner("Tekst opschonen..."):
            schone_tekst = maak_schoon(ruwe_tekst)
            woord_count = len(schone_tekst.split())
            st.info(f"Opgeschoonde tekst: {woord_count} woorden")

        with st.spinner("AI analyseert de tekst..."):
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("gemini-2.5-flash-lite")
                prompt = f"{SLEUTEL}\n\n--- TEKST OM TE ANALYSEREN ---\n\n{schone_tekst}"
                response = model.generate_content(prompt)
                volledige_tekst = response.text

                structuur = None
                start = volledige_tekst.find("=== JSON ===") + len("=== JSON ===")
                einde = volledige_tekst.find("=== EINDE JSON ===")
                if start > 0 and einde > start:
                    json_tekst = volledige_tekst[start:einde].strip()
                    try:
                        structuur = json.loads(json_tekst)
                    except Exception as e:
                        st.warning(f"Kon JSON niet parsen: {e}")

                st.session_state.volledige_tekst = volledige_tekst
                st.session_state.structuur = structuur
                st.session_state.schone_tekst = schone_tekst
                st.session_state.analyse_klaar = True
                st.session_state.toekomst_tekst = ""
                st.session_state.toekomst_structuur = None

            except Exception as e:
                st.error(f"Fout bij AI-aanroep: {e}")
                st.info("Controleer je API-sleutel en of je internetverbinding werkt.")

# === TOON ANALYSE ===
if st.session_state.analyse_klaar:
    volledige_tekst = st.session_state.volledige_tekst
    structuur = st.session_state.structuur

    if structuur:
        try:
            fig = teken_lussen_grafiek(structuur)
            if fig:
                st.markdown("### Lussen-netwerk")
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.warning(f"Kon de grafiek niet tekenen: {e}")

    st.success("Analyse voltooid")
    st.markdown("---")
    st.markdown("### Analyse")

    start = volledige_tekst.find("=== JSON ===")
    einde = volledige_tekst.find("=== EINDE JSON ===")
    tekst_zonder_json = volledige_tekst
    if start > 0 and einde > start:
        tekst_zonder_json = (
            volledige_tekst[:start] +
            volledige_tekst[einde + len("=== EINDE JSON ==="):]
        )
    st.markdown(tekst_zonder_json)

    with st.expander("Opgeschoonde tekst bekijken"):
        st.text(st.session_state.schone_tekst)

    # === KNOP 2: TOEKOMSTANALYSE ===
    st.markdown("---")
    st.markdown("### Toekomstanalyse")
    st.caption("Laat de lussen-interactie doorwerken in mogelijke scenario's.")

    if st.button("Toekomstanalyse", type="secondary"):
        if not structuur:
            st.error("Geen structuur gevonden om op voort te bouwen.")
        else:
            with st.spinner("AI werkt scenario's uit..."):
                try:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel("gemini-2.0-flash")

                    context = (
                        f"--- ORIGINELE TEKST ---\n{st.session_state.schone_tekst}\n\n"
                        f"--- EERSTE ANALYSE ---\n{st.session_state.volledige_tekst}\n\n"
                        f"--- STRUCTUUR (JSON) ---\n"
                        f"{json.dumps(structuur, ensure_ascii=False)}\n"
                    )
                    prompt = f"{TOEKOMST_SLEUTEL}\n\n{context}"
                    response = model.generate_content(prompt)
                    toekomst_tekst = response.text

                    toekomst_structuur = None
                    s = toekomst_tekst.find("=== JSON ===") + len("=== JSON ===")
                    e = toekomst_tekst.find("=== EINDE JSON ===")
                    if s > 0 and e > s:
                        try:
                            toekomst_structuur = json.loads(
                                toekomst_tekst[s:e].strip()
                            )
                        except Exception as ex:
                            st.warning(f"Kon scenario-JSON niet parsen: {ex}")

                    st.session_state.toekomst_tekst = toekomst_tekst
                    st.session_state.toekomst_structuur = toekomst_structuur

                except Exception as e:
                    st.error(f"Fout bij toekomstanalyse: {e}")

    # === TOON TOEKOMSTANALYSE ===
    if st.session_state.toekomst_tekst:
        toekomst_tekst = st.session_state.toekomst_tekst
        toekomst_structuur = st.session_state.toekomst_structuur

        s = toekomst_tekst.find("=== JSON ===")
        e = toekomst_tekst.find("=== EINDE JSON ===")
        tekst_zonder_json = toekomst_tekst
        if s > 0 and e > s:
            tekst_zonder_json = (
                toekomst_tekst[:s] +
                toekomst_tekst[e + len("=== EINDE JSON ==="):]
            )
        st.markdown(tekst_zonder_json)

        if toekomst_structuur and structuur:
            scenarios = toekomst_structuur.get("scenarios", [])
            if scenarios:
                st.markdown("### Scenario-netwerken")
                tabs = st.tabs([
                    f"{sc.get('id', '?')}: {sc.get('naam', '')}"
                    for sc in scenarios
                ])
                for tab, sc in zip(tabs, scenarios):
                    with tab:
                        st.caption(f"Conditie: {sc.get('conditie', '')}")
                        st.caption(
                            f"Kans: {sc.get('kans', '?')} — "
                            f"status: {sc.get('status', '?')} — "
                            f"tijdschaal: {sc.get('tijdschaal', '?')}"
                        )
                        try:
                            fig = teken_scenario_grafiek(structuur, sc)
                            if fig:
                                st.plotly_chart(fig, use_container_width=True)
                        except Exception as ex:
                            st.warning(f"Kon scenariografiek niet tekenen: {ex}")

st.markdown("---")
st.caption("DenkKrant — universele sleutel prototype v0.3 (met toekomstanalyse)")
