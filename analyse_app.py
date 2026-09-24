import streamlit as st
import re
import json
import math
from bs4 import BeautifulSoup
import plotly.graph_objects as go
import networkx as nx
from google import genai

# === INSTELLINGEN ===
st.set_page_config(page_title="DenkKrant Analyse", layout="wide")

# === MODELLEN (met fallback) ===
MODELLEN = [
    "gemini-3.5-flash-lite",
    "gemini-2.5-flash",
]


def haal_tekst_uit_interaction(interaction):
    """Probeer eerst het gemaksattribuut, anders zelf de stappen doorlopen."""
    tekst = getattr(interaction, "output_text", None)
    if tekst:
        return tekst
    tekst = ""
    for step in getattr(interaction, "steps", []):
        if getattr(step, "type", None) == "model_output":
            for block in getattr(step, "content", []):
                if getattr(block, "type", None) == "text":
                    tekst += block.text
    return tekst


def vraag_ai(client, prompt, modellen=MODELLEN):
    """Probeer modellen één voor één tot er één werkt."""
    laatste_fout = None
    for modelnaam in modellen:
        try:
            interaction = client.interactions.create(
                model=modelnaam,
                input=prompt,
            )
            return haal_tekst_uit_interaction(interaction), modelnaam
        except Exception as e:
            laatste_fout = e
            continue
    raise laatste_fout


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


# === ALGEMENE HANDELINGSANALYSE ===
ALGEMEEN_SLEUTEL = """
Je bent een filosofisch analist die werkt met de universele lussen-sleutel.

Je krijgt zo:
1. De originele tekst.
2. De lussen-analyse.
3. De toekomstscenario's.

JOUW TAAK:
Geef een ALGEMENE handelingsanalyse. Dit is NIET persoonlijk.
Je zegt wat een willekeurig iemand zou kunnen overwegen, gegeven de lussen
en de scenario's. Je weet niet wie de lezer is, dus je blijft breed.

Structuur:

=== WAT KAN IEMAND DOEN? ===

1. Overkoepelende houding
   In 3-5 zinnen: wat is, gegeven deze lussen, een verstandige houding?
   Denk aan: voorbereiden, afwachten, versnellen, vertragen, bondgenoten
   zoeken, loslaten, monitoren.

2. Per scenario: één handelingsrichting
   Voor elk scenario uit de analyse:
   - Naam van het scenario
   - Eén algemene handelingsrichting (1-2 zinnen)
   - Eén concreet voorbeeld van wat iemand zou kunnen doen

3. Vroege signalen
   Noem per scenario 1-2 signalen waaraan je zou merken dat het scenario
   zich daadwerkelijk ontvouwt. Waar moet je op letten?

4. Wat buiten iedereens macht ligt
   Noem 2-3 dingen die niemand kan beheersen, hoe goed voorbereid ook.
   Dit is de filosofische kern: onderscheid wat wel en niet in je macht ligt.

5. Eerlijke conclusie
   Is voorbereiding zinvol, of is dit vooral een beschouwende oefening?
   Wees eerlijk. Als het antwoord "het hangt ervan af" is, zeg dat dan,
   maar leg uit waarvan.

BELANGRIJK:
- Blijf ALGEMEEN. Geen "je moet", maar "iemand zou kunnen".
- Geen therapeutisch, juridisch of financieel advies.
- Geen vage taal ("wees flexibel"). Wees concreet waar het kan.
- Maximaal 500 woorden.
"""


# === VRAGEN VOORSTELLEN ===
VRAGEN_SLEUTEL = """
Je bent een filosofisch gespreksleider die werkt met de universele lussen-sleutel.

Je krijgt zo:
1. De originele tekst.
2. De lussen-analyse.
3. De toekomstscenario's.
4. De algemene handelingsanalyse.

JOUW TAAK:
Stel een korte set persoonlijke vragen voor, toegespitst op DIT artikel
en DEZE analyse. De vragen moeten de gebruiker helpen zijn eigen positie
in de lussen te bepalen, zodat een persoonlijke handelingsanalyse scherp
kan zijn.

REGELS:
- Maximaal 8 vragen.
- Elke vraag is direct relevant voor dit specifieke onderwerp.
- Geen standaardvragen die op elk artikel passen.
- Minimaal één vraag gaat over wat de gebruiker VOELT bij dit onderwerp
  (angst, hoop, woede, berusting, nieuwsgierigheid, walging, iets anders).
- Vragen mogen keuze, schaal (1-5), ja/nee, of vrije tekst zijn.

TUSSENVRAGEN:
Soms zal een antwoord van de gebruiker aanleiding geven tot een extra vraag.
Je mag maximaal 2 zulke tussenvragen voorbereiden. Een tussenvraag is een
vraag die je alleen stelt als een bepaald eerder antwoord daar aanleiding
toe geeft.
- Geef per tussenvraag aan: bij welk(e) antwoord(en) hij gesteld moet worden.
- Tussenvragen zijn optioneel; het is prima als er 0 zijn.
- Een tussenvraag moet ECHT iets toevoegen, niet gewoon een herformulering.

Sluit af met een JSON-blok tussen === JSON === en === EINDE JSON ===:

{
  "vragen": [
    {
      "id": "V1",
      "vraag": "...",
      "type": "keuze|schaal|ja_nee|tekst",
      "opties": ["...", "..."],
      "waarom": "korte uitleg waarom deze vraag relevant is voor dit artikel"
    }
  ],
  "tussenvragen": [
    {
      "id": "T1",
      "vraag": "...",
      "type": "keuze|schaal|ja_nee|tekst",
      "opties": ["...", "..."],
      "trigger": "bij welk antwoord op welke vraag deze tussenvraag gesteld moet worden",
      "waarom": "korte uitleg"
    }
  ]
}

- Bij type "schaal" is "opties" een lijst van 5 labels (1 t/m 5).
- Bij type "ja_nee" en "tekst" is "opties" leeg of afwezig.
- De JSON moet geldig zijn: geen commentaar, geen trailing comma's.
"""


# === PERSOONLIJKE ANALYSE ===
PERSOONLIJK_SLEUTEL = """
Je bent een filosofisch analist die werkt met de universele lussen-sleutel.

Je krijgt zo:
1. De originele tekst.
2. De lussen-analyse.
3. De toekomstscenario's.
4. De algemene handelingsanalyse.
5. De vragen die aan de gebruiker zijn gesteld.
6. De antwoorden van de gebruiker.

JOUW TAAK:
Geef een PERSOONLIJKE handelingsanalyse voor deze specifieke gebruiker.
Baseer je op zijn antwoorden, zijn positie in de lussen, en wat hij voelt.

Structuur:

=== JOUW POSITIE ===
In 3-5 zinnen: waar staat deze gebruiker in de lussen?
Welke rol heeft hij, welke lussen raken hem direct, welke niet.

=== WAT JIJ VOELT ===
Erken de emotie die de gebruiker noemde. Leg uit wat die emotie
betekent in de context van de lussen. Is de emotie terecht?
Wat zegt ze over hoe de gebruiker de situatie waarneemt?

=== WAT JIJ KUNT DOEN ===
Per relevant scenario (sla scenario's over die voor deze gebruiker
niet relevant zijn, en zeg waarom):
- Relevantie voor jou (1-2 zinnen)
- Noodzaak tot voorbereiding: ja / nee / misschien — met onderbouwing
- Concrete handelingen, opgesplitst in:
  * Nu doen
  * Voorbereiden
  * Monitoren
  * Nalaten (wat je vooral NIET moet doen)
- Vroege signalen om op te letten
- Wat buiten jouw macht ligt (en dus losgelaten kan worden)

=== EERLIJK EINDOORDEEL ===
Is voorbereiding voor deze gebruiker zinvol, of is het vooral
beschouwend? Durf te zeggen: "voor jou is dit niet iets om je op
voor te bereiden." Wees eerlijk.

BELANGRIJK:
- Pas de TOON aan op de emotie. Bij angst: rustig en beheerst.
  Bij hoop: warm en uitnodigend. Bij woede: nuchter en richtinggevend.
  Bij berusting: zacht maar eerlijk. Bij nieuwsgierigheid: verkennend.
- Geen "je moet". Wel: "een mogelijke beweging is", "je zou kunnen overwegen".
- Geen therapeutisch, juridisch of financieel advies.
- Blijf dicht bij wat de gebruiker heeft geantwoord. Verzin niets bij.
- Maximaal 600 woorden.
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


# === LUSSEN-GRAFIEK ===
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


# === SCENARIO-GRAFIEK ===
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
for sleutel_naam, begin_waarde in [
    ("analyse_klaar", False),
    ("volledige_tekst", ""),
    ("structuur", None),
    ("schone_tekst", ""),
    ("toekomst_tekst", ""),
    ("toekomst_structuur", None),
    ("algemeen_tekst", ""),
    ("vragen_data", None),
    ("antwoorden", {}),
    ("tussen_antwoorden", {}),
    ("persoonlijk_tekst", ""),
]:
    if sleutel_naam not in st.session_state:
        st.session_state[sleutel_naam] = begin_waarde

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
                client = genai.Client(api_key=api_key)
                prompt = f"{SLEUTEL}\n\n--- TEKST OM TE ANALYSEREN ---\n\n{schone_tekst}"
                volledige_tekst, model_gebruikt = vraag_ai(client, prompt)
                st.caption(f"Analyse gegenereerd met {model_gebruikt}")

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
                # Reset lagere lagen
                st.session_state.toekomst_tekst = ""
                st.session_state.toekomst_structuur = None
                st.session_state.algemeen_tekst = ""
                st.session_state.vragen_data = None
                st.session_state.antwoorden = {}
                st.session_state.tussen_antwoorden = {}
                st.session_state.persoonlijk_tekst = ""

            except Exception as e:
                st.error(f"Fout bij AI-aanroep: {e}")
                st.info("Controleer je API-sleutel en of je internetverbinding werkt.")


# === VANAF HIER: ALLES BINNEN analyse_klaar ===
if st.session_state.analyse_klaar:
    volledige_tekst = st.session_state.volledige_tekst
    structuur = st.session_state.structuur

    # Grafiek 1
    if structuur:
        try:
            fig = teken_lussen_grafiek(structuur)
            if fig:
                st.markdown("### Lussen-netwerk")
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.warning(f"Kon de grafiek niet tekenen: {e}")

    # Tekstuele analyse
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
        st.text(st.session_state.sch
