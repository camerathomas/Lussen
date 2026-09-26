"""
DenkKrant — PDF-export
Zet de analyse-uitkomsten om in een net opgemaakte PDF.
"""

import os
import re
from datetime import datetime

from weasyprint import HTML, CSS


# ---------- Hulpfuncties ----------

def _esc(tekst):
    """Simpele HTML-escape. Voorkomt dat < of > de layout breken."""
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
    """Haalt het JSON-blok uit de AI-tekst."""
    if not tekst:
        return ""
    return re.sub(
        r"={2,}\s*JSON\s*={2,}.*?={2,}\s*EINDE\s*JSON\s*={2,}",
        "",
        tekst,
        flags=re.DOTALL | re.IGNORECASE,
    ).strip()


def _alineas(tekst):
    """Zet platte tekst om in <p>-blokken."""
    if not tekst:
        return ""
    blokken = re.split(r"\n\s*\n", tekst.strip())
    return "".join(f"<p>{_esc(b).replace(chr(10), '<br>')}</p>" for b in blokken)


# ---------- Secties ----------

def _cover(titel, bron, datum):
    return f"""
    <div class="cover">
        <div class="merk">DenkKrant</div>
        <h1>Universele Analyse</h1>
        <div class="subtitel">{_esc(titel)}</div>
        <div class="accentlijn"></div>
        <div class="meta">
            {_esc(bron)}<br>
            {_esc(datum)}
        </div>
    </div>
    """


def _hoofdstuk(nummer, titel, inhoud_html):
    return f"""
    <section class="hoofdstuk">
        <div class="hoofdstuk-nummer">{_esc(nummer)}</div>
        <h2>{_esc(titel)}</h2>
        <div class="hoofdstuk-lijn"></div>
        <div class="sectie">{inhoud_html}</div>
    </section>
    """


def _scenario_blok(sc):
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
    """


# ---------- Hoofdfunctie ----------

def maak_pdf(
    *,
    titel,
    bron,
    analyse_tekst,
    narratief_tekst,
    toekomst_tekst,
    toekomst_structuur,
    algemeen_tekst,
    persoonlijk_tekst,
    uitvoerpad=None,
):
    """Bouwt de HTML en schrijft de PDF."""

    datum = datetime.now().strftime("%d %B %Y").lstrip("0")

    if uitvoerpad is None:
        os.makedirs("pdfs", exist_ok=True)
        stempel = datetime.now().strftime("%Y%m%d_%H%M%S")
        uitvoerpad = f"pdfs/denkkrant_{stempel}.pdf"

    # --- HTML opbouwen ---
    delen = []

    # 1. Analyse
    analyse_schoon = _ontdoe_json(analyse_tekst)
    delen.append(_hoofdstuk("1", "De analyse", _alineas(analyse_schoon)))

    # 2. Narratief
    if narratief_tekst:
        delen.append(
            _hoofdstuk("2", "Het verhaal", _alineas(_ontdoe_json(narratief_tekst)))
        )

    # 3. Toekomstscenario's
    if toekomst_structuur and toekomst_structuur.get("scenarios"):
        scenarios_html = "".join(
            _scenario_blok(sc) for sc in toekomst_structuur["scenarios"]
        )
        delen.append(
            _hoofdstuk("3", "Toekomstscenario's", scenarios_html)
        )

    # 4. Algemene handelingsanalyse
    if algemeen_tekst:
        delen.append(
            _hoofdstuk("4", "Wat kan iemand doen?", _alineas(algemeen_tekst))
        )

    # 5. Persoonlijke analyse
    if persoonlijk_tekst:
        delen.append(
            _hoofdstuk("5", "Jouw positie", _alineas(persoonlijk_tekst))
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
{body}
</body>
</html>
    """

    # --- CSS laden ---
    hier = os.path.dirname(os.path.abspath(__file__))
    css_pad = os.path.join(hier, "pdf_stijl.css")

    if os.path.exists(css_pad):
        stylesheets = [CSS(filename=css_pad)]
    else:
        stylesheets = []

    # --- Renderen ---
    HTML(string=html, base_url=hier).write_pdf(
        uitvoerpad, stylesheets=stylesheets
    )

    return uitvoerpad
