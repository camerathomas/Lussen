"""
DenkKrant — PDF-export (v4)
Met automatische titel, inhoudsopgave, ankers, grafieken
en optionele AI-HTML-invoer.
"""

import os
import re
from datetime import datetime

from weasyprint import HTML, CSS


# ---------- Constanten ----------

DISCLAIMER = (
    "Deze tekstuele analyse is gemaakt op basis van de theorie van "
    "gelaagde en in elkaar grijpende processen (lussen). Andere analyses, "
    "met andere aannames of modellen, kunnen tot andere uitkomsten komen."
)


# ---------- Hulpfuncties ----------

def _esc(tekst):
    if tekst is None:
        return ""
    tekst = str(tekst)
    return (
        tekst.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;")
    )


def _status_class(status):
    status = (status or "").lower().strip()
    if status == "gefundeerd":
        return "gefundeerd"
    if status == "speculatief":
        return "speculatief"
    return ""


def _status_label(status):
    status = (status or "").lower().strip()
    if status == "gefundeerd":
        return "🟢 Gefundeerd"
    if status == "speculatief":
        return "🟡 Speculatief"
    return _esc(status).capitalize()


def _ontdoe_json(tekst):
    if not tekst:
        return ""
    return re.sub(
        r"={2,}\s*JSON\s*={2,}.*?={2,}\s*EINDE\s*JSON\s*={2,}",
        "",
        tekst,
        flags=re.DOTALL | re.IGNORECASE,
    ).strip()


def _alineas(tekst):
    if not tekst:
        return ""
    blokken = re.split(r"\n\s*\n", tekst.strip())
    return "".join(
        f"<p>{_esc(b).replace(chr(10), '<br>')}</p>" for b in blokken
    )


# ---------- Secties ----------

def _cover(titel, bron, datum):
    return f"""
    <div class="cover">
        <div class="merk">DenkKrant</div>
        <h1>{_esc(titel)}</h1>
        <div class="subtitel">Universele Analyse</div>
        <div class="accentlijn"></div>
        <div class="meta">
            {_esc(bron)}<br>
            {_esc(datum)}
        </div>
        <div class="disclaimer">
            {_esc(DISCLAIMER)}
        </div>
    </div>
    """


def _inhoudsopgave(hoofdstukken):
    items = "".join(
        f'<li>'
        f'<a href="#{anker}">'
        f'<span class="inhoud-nummer">{_esc(nummer)}</span>'
        f'{_esc(titel)}'
        f'</a>'
        f'</li>'
        for nummer, titel, anker in hoofdstukken
    )
    return f"""
    <section class="inhoud">
        <h2>Inhoud</h2>
        <div class="hoofdstuk-lijn"></div>
        <ul>{items}</ul>
    </section>
    """


def _hoofdstuk(nummer, titel, inhoud_html, kleurklasse="h1", anker=None):
    if anker is None:
        anker = f"h{nummer}"
    return f"""
    <section class="hoofdstuk {kleurklasse}" id="{anker}">
        <div class="terug-naar-inhoud">
            <a href="#inhoud">↑ Inhoud</a>
        </div>
        <div class="hoofdstuk-nummer">{_esc(nummer)}</div>
        <h2>{_esc(titel)}</h2>
        <div class="hoofdstuk-lijn"></div>
        <div class="sectie">{inhoud_html}</div>
    </section>
    """


def _grafiek_html(pad, bijschrift=""):
    if not pad or not os.path.exists(pad):
        return ""
    return f"""
    <div class="grafiek">
        <img src="{_esc(pad)}" alt="grafiek">
        {f'<div class="bijschrift">{_esc(bijschrift)}</div>' if bijschrift else ''}
    </div>
    """


def _scenario_blok(sc, grafiek_pad=None):
    status_cls = _status_class(sc.get("status"))
    naam = _esc(sc.get("naam", ""))
    conditie = _esc(sc.get("conditie", ""))
    tijdschaal = _esc(sc.get("tijdschaal", "?"))
    kans = _esc((sc.get("kans") or "?").capitalize())

    dominante = ", ".join(sc.get("dominante_lussen", [])) or "—"
    kantel = ", ".join(sc.get("kantelpunten", [])) or "—"

    externe_html = ""
    if sc.get("externe_lussen"):
        items = "".join(
            f"<li><strong>{_esc(e.get('id', '?'))}</strong> — "
            f"{_esc(e.get('naam', ''))}: {_esc(e.get('beschrijving', ''))}</li>"
            for e in sc["externe_lussen"]
        )
        externe_html = f"<h4>Externe lussen</h4><ul>{items}</ul>"

    return f"""
    <div class="statusblok {status_cls}">
        <div class="status-label">{_status_label(sc.get("status"))}</div>
        <div class="scenario-naam">{naam}</div>
        <div class="scenario-meta">
            <span>⏳ {tijdschaal}</span>
            <span>📊 {kans}</span>
        </div>
    </div>

    <div class="conditie">
        <span class="label">Conditie</span>
        {conditie}
    </div>

    <table class="velden">
        <tr><td>Dominante lussen</td><td>{_esc(dominante)}</td></tr>
        <tr><td>Kantelende lussen</td><td>{_esc(kantel)}</td></tr>
    </table>

    {externe_html}
    {_grafiek_html(grafiek_pad, f"Netwerk van scenario {_esc(sc.get('id', '?'))}")}
    """


# ---------- Hoofdfunctie ----------

def maak_pdf(
    *,
    titel=None,
    bron="Bron onbekend",
    analyse_tekst,
    analyse_html=None,
    lussen_grafiek_pad=None,
    narratief_tekst,
    narratief_html=None,
    toekomst_tekst,
    toekomst_structuur,
    scenario_grafiek_paden=None,
    algemeen_tekst,
    algemeen_html=None,
    persoonlijk_tekst,
    persoonlijk_html=None,
    uitvoerpad=None,
):
    datum = datetime.now().strftime("%d %B %Y").lstrip("0")

    if uitvoerpad is None:
        os.makedirs("pdfs", exist_ok=True)
        stempel = datetime.now().strftime("%Y%m%d_%H%M%S")
        uitvoerpad = f"pdfs/denkkrant_{stempel}.pdf"

    if not titel or not titel.strip():
        titel = "Universele Analyse"

    # ---- Inhoudsopgave voorbereiden ----
    hoofdstuk_defs = []

    if analyse_tekst:
        hoofdstuk_defs.append(("1", "De analyse", "h1"))
    if narratief_tekst:
        hoofdstuk_defs.append(("2", "Het verhaal", "h2"))
    if toekomst_structuur and toekomst_structuur.get("scenarios"):
        hoofdstuk_defs.append(("3", "Toekomstscenario's", "h3"))
    if algemeen_tekst:
        hoofdstuk_defs.append(("4", "Wat kan iemand doen?", "h4"))
    if persoonlijk_tekst:
        hoofdstuk_defs.append(("5", "Jouw positie", "h5"))

    inhoudsopgave_html = _inhoudsopgave(hoofdstuk_defs)

    # ---- Helper: kies HTML of platte tekst ----
    def _kies_inhoud(plat, html):
        if html and html.strip():
            return html
        return _alineas(_ontdoe_json(plat))

    # ---- Hoofdstukken opbouwen ----
    delen = []

    if analyse_tekst:
        analyse_inhoud = _kies_inhoud(analyse_tekst, analyse_html)
        analyse_inhoud += _grafiek_html(lussen_grafiek_pad, "Lussen-netwerk")
        delen.append(_hoofdstuk("1", "De analyse", analyse_inhoud, "h1"))

    if narratief_tekst:
        delen.append(
            _hoofdstuk(
                "2", "Het verhaal",
                _kies_inhoud(narratief_tekst, narratief_html),
                "h2",
            )
        )

    if toekomst_structuur and toekomst_structuur.get("scenarios"):
        scenario_paden = scenario_grafiek_paden or {}
        scenarios_html = ""
        for sc in toekomst_structuur["scenarios"]:
            pad = scenario_paden.get(sc.get("id"))
            scenarios_html += _scenario_blok(sc, pad)
        delen.append(
            _hoofdstuk("3", "Toekomstscenario's", scenarios_html, "h3")
        )

    if algemeen_tekst:
        delen.append(
            _hoofdstuk(
                "4", "Wat kan iemand doen?",
                _kies_inhoud(algemeen_tekst, algemeen_html),
                "h4",
            )
        )

    if persoonlijk_tekst:
        delen.append(
            _hoofdstuk(
                "5", "Jouw positie",
                _kies_inhoud(persoonlijk_tekst, persoonlijk_html),
                "h5",
            )
        )

    body = "\n".join(delen)

    html = f"""<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="utf-8">
<title>DenkKrant — Universele Analyse</title>
</head>
<body>
{_cover(titel, bron, datum)}
<span id="inhoud"></span>
{inhoudsopgave_html}
{body}
</body>
</html>
    """

    hier = os.path.dirname(os.path.abspath(__file__))
    css_pad = os.path.join(hier, "pdf_stijl.css")

    if os.path.exists(css_pad):
        stylesheets = [CSS(filename=css_pad)]
    else:
        stylesheets = []

    HTML(string=html, base_url=hier).write_pdf(
        uitvoerpad, stylesheets=stylesheets
    )

    return uitvoerpad
