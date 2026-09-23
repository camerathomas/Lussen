import streamlit as st
import re
from bs4 import BeautifulSoup
import google.generativeai as genai

# === INSTELLINGEN ===
st.set_page_config(page_title="DenkKrant Analyse", layout="wide")

# === DE SLEUTEL (pas dit aan naar jouw formulering) ===
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

Let op deze soorten: enthymeem, verzwegen waardeoordeel, verzwegen definitie,
verzwegen oorzaak-gevolg relatie, verzwegen autoriteit, verzwegen algemene regel.
Geef maximaal 5 verborgen premissen, geordend op belangrijkheid.

=== DEEL 2.5: UNIVERSELE VERGELIJKING ===

Zoek naar het overheersende patroon in de situatie.
Vergelijk dit patroon met vergelijkbare patronen in andere domeinen.

Kies 3 tot 5 domeinen uit deze lijst:
- Plantenrijk (groei, bloei, verval, seizoenen)
- Dierenrijk (predatie, symbiose, competitie, kuddegedrag)
- Natuurkunde (zwaartekracht, entropie, faseovergangen)
- Kosmos (sterren, planeten, zwarte gaten)
- Maatschappij (politiek, cultuur, instituties)
- Economie (markten, cycli, schaarste)
- Technologie (innovaties, adoptiecurves, netwerkeffecten)
- Menselijk lichaam (immuniteit, metabolisme, zenuwstelsel)
- Spel (strategie, bondgenootschappen, verraad)
- Verhaal (held, schurk, crisis, transformatie)

Voor elk domein:
1. Noem het domein.
2. Beschrijf het vergelijkbare patroon in dat domein.
3. Leg uit waarom het patroon vergelijkbaar is.
4. Geef aan of de vergelijking volledig of gedeeltelijk opgaat.
5. Trek een conclusie: wat leert deze vergelijking ons over de situatie?

Kies domeinen die:
- Voor een breed publiek begrijpelijk zijn.
- Een patroon laten zien dat echt vergelijkbaar is.
- Iets toevoegen aan de analyse dat nog niet genoemd is.

=== DEEL 3: JIP-EN-JANNEKE-VERTALING ===
Vertaal de analyse naar Jip-en-Janneke-taal.
- Maximaal 300 woorden.
- Minimaal één metafoor of beeld.
- Noem de belangrijkste lus en de belangrijkste terugkoppeling.
- Leg uit wat het geheel zwak of sterk maakt.
- Vermijd jargon: geen "emergentie", "terugkoppeling", "selectiecriterium".
- Schrijf alsof je het aan een slimme vriend vertelt die niets van het model weet.

=== DEEL 4: SPREEKWOORDEN ===
Geef 3 tot 5 spreekwoorden, uitdrukkingen of allegorieën die van toepassing zijn.
Voor elk spreekwoord:
- Noem het spreekwoord.
- Leg in één zin uit waarom het past.
- Koppel het aan een specifieke lus of verhouding.
- Geef aan of het de situatie volledig dekt of slechts een deel.

=== DEEL 5: SOCIALE-MEDIA-REACTIES ===
Schrijf drie reacties voor sociale media, één in elke stijl:

STIJL A — COMPASSIE
- Begin met erkenning: "Wat een nare situatie..."
- Benoem het menselijke aspect.
- Sluit af met een warme wens of gedachte.
- Maximaal 100 woorden.

STIJL B — ANALYTISCH
- Begin met: "Wat hier echt speelt is..."
- Benoem de belangrijkste lus en de belangrijkste terugkoppeling.
- Doorprik de oppervlakkige laag: "Ogenschijnlijk gaat het over X, maar eigenlijk..."
- Sluit af met een prikkelende vraag.
- Maximaal 120 woorden.

STIJL C — MENSELIJK
- Begin met herkenning: "Ik kan me voorstellen dat..."
- Vertel een kort, algemeen menselijk voorbeeld.
- Gebruik de ik-vorm.
- Sluit af met een uitnodiging: "Hoe zou jij hiermee omgaan?"
- Maximaal 100 woorden.

=== BELANGRIJK ===
- Wees precies. Verzin niets. Als iets niet in de tekst staat, zeg dat dan.
- Sla geen enkel deel over. Elk deel moet er staan, ook als het kort is.
- Gebruik duidelijke koppen zodat de gebruiker elk deel kan vinden.
"""

# === TEKST OPSCHONEN ===
def schoon_html(html_tekst):
    """Verwijdert HTML-tags en rommel."""
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
    """Verwijdert URLs, e-mails en typische rommel uit platte tekst."""
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

# === UI ===
st.title("DenkKrant — Universele Analyse")
st.markdown("Plak een tekst (artikel, verhaal, verslag) en laat de sleutel zijn werk doen.")

api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    st.error("Geen API-sleutel gevonden. Stel GOOGLE_API_KEY in via de Secrets-instellingen.")

ruwe_tekst = st.text_area("Plak hier je tekst", height=300,
                           placeholder="Plak een artikel van minimaal 800 woorden...")

if st.button("Analyseer", type="primary"):
    if not api_key:
        st.error("Vul eerst je API-sleutel in.")
    elif not ruwe_tekst or len(ruwe_tekst.split()) < 100:
        st.error("De tekst is te kort. Plak een langere tekst (minimaal 800 woorden).")
    else:
        with st.spinner("Tekst opschonen..."):
            schone_tekst = maak_schoon(ruwe_tekst)
            woord_count = len(schone_tekst.split())
            st.info(f"Opgeschoonde tekst: {woord_count} woorden")

        if woord_count < 100:
            st.error("Na opschonen blijft er te weinig tekst over. Controleer je input.")
        else:
            with st.spinner("AI analyseert de tekst met de sleutel..."):
                try:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel("gemini-3.5-flash-lite")
                    prompt = f"{SLEUTEL}\n\n--- TEKST OM TE ANALYSEREN ---\n\n{schone_tekst}"
                    response = model.generate_content(prompt)

                    st.success("Analyse voltooid")
                    st.markdown("---")
                    st.markdown("### Analyse")
                    st.markdown(response.text)

                    with st.expander("Opgeschoonde tekst bekijken"):
                        st.text(schone_tekst)

                except Exception as e:
                    st.error(f"Fout bij AI-aanroep: {e}")
                    st.info("Controleer je API-sleutel en of je internetverbinding werkt.")

st.markdown("---")
st.caption("DenkKrant — universele sleutel prototype v0.1")
