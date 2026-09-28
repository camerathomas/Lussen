"""
DenkKrant — Grafieken als PNG
Gebruikt matplotlib, werkt overal (ook op Streamlit Cloud).
"""

import os
import matplotlib
matplotlib.use("Agg")  # geen scherm nodig
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx


# ---------- Kleuren ----------

KLEUR_MAP = {
    "seconden": "#ef4444",
    "minuten":  "#f97316",
    "dagen":    "#eab308",
    "maanden":  "#22c55e",
    "jaren":    "#3b82f6",
    "decennia": "#8b5cf6",
}

KLEUR_VERSTERKEND = "#ef4444"
KLEUR_VERZWAKKEND = "#3b82f6"


# ---------- Lussengrafiek ----------

def maak_lussen_png(structuur, pad="pdfs/lussen.png"):
    """Maakt een PNG van het lussen-netwerk."""
    lussen = structuur.get("lussen", [])
    terugkoppelingen = structuur.get("terugkoppelingen", [])

    if not lussen:
        return None

    os.makedirs(os.path.dirname(pad), exist_ok=True)

    # Graaf opbouwen
    G = nx.DiGraph()
    for lus in lussen:
        G.add_node(lus["id"], **lus)
    for tb in terugkoppelingen:
        if tb["van"] in G and tb["naar"] in G:
            G.add_edge(
                tb["van"], tb["naar"],
                sterkte=tb.get("sterkte", 1),
                type=tb.get("type", "versterkend"),
                label=tb.get("label", ""),
            )

    pos = nx.spring_layout(G, k=1.2, iterations=200, seed=42)

    fig, ax = plt.subplots(figsize=(10, 8), dpi=150)
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#ffffff")

    # Knopen
    for lus in lussen:
        lid = lus["id"]
        if lid not in pos:
            continue
        x, y = pos[lid]
        kleur = KLEUR_MAP.get(lus.get("tijdschaal", "maanden"), "#94a3b8")
        grootte = lus.get("omvang", 3) * 800

        ax.scatter(
            x, y,
            s=grootte,
            c=kleur,
            edgecolors="white",
            linewidths=2.5,
            zorder=3,
        )
        ax.text(
            x, y,
            lid,
            ha="center", va="center",
            fontsize=14,
            fontweight="bold",
            color="white",
            zorder=4,
        )
        ax.text(
            x, y - 0.18,
            lus.get("naam", ""),
            ha="center", va="top",
            fontsize=9,
            color="#333333",
            zorder=4,
        )

    # Pijlen (terugkoppelingen)
    for tb in terugkoppelingen:
        van = tb["van"]
        naar = tb["naar"]
        if van not in pos or naar not in pos:
            continue

        sterkte = tb.get("sterkte", 1)
        type_ = tb.get("type", "versterkend")
        kleur = KLEUR_VERSTERKEND if type_ == "versterkend" else KLEUR_VERZWAKKEND
        dikte = sterkte * 0.8

        ax.annotate(
            "",
            xy=pos[naar], xytext=pos[van],
            arrowprops=dict(
                arrowstyle="-|>",
                color=kleur,
                lw=dikte,
                shrinkA=18, shrinkB=18,
                connectionstyle="arc3,rad=0.15",
            ),
            zorder=2,
        )

    ax.set_axis_off()
    ax.margins(0.15)

    # Legenda
    legenda_items = [
        mpatches.Patch(color=kleur, label=schaal.capitalize())
        for schaal, kleur in KLEUR_MAP.items()
    ]
    legenda_items.append(
        mpatches.Patch(color=KLEUR_VERSTERKEND, label="Versterkend")
    )
    legenda_items.append(
        mpatches.Patch(color=KLEUR_VERZWAKKEND, label="Verzwakkend")
    )

    ax.legend(
        handles=legenda_items,
        loc="upper left",
        bbox_to_anchor=(1.02, 1.0),
        fontsize=8,
        frameon=False,
        borderaxespad=0,
    )
    fig.tight_layout()
    fig.savefig(pad, bbox_inches="tight", facecolor="#ffffff")
    plt.close(fig)

    return pad


# ---------- Scenariografieken ----------

def maak_scenario_png(structuur, scenario, pad=None):
    """Maakt een PNG van een scenarionetwerk."""
    lussen = {l["id"]: l for l in structuur.get("lussen", [])}
    terugkoppelingen = structuur.get("terugkoppelingen", [])

    dominante = set(scenario.get("dominante_lussen", []))
    kantelpunten = set(scenario.get("kantelpunten", []))
    externe = scenario.get("externe_lussen", [])

    if pad is None:
        os.makedirs("pdfs", exist_ok=True)
        pad = f"pdfs/scenario_{scenario.get('id', 'X')}.png"

    os.makedirs(os.path.dirname(pad), exist_ok=True)

    # Graaf opbouwen
    G = nx.DiGraph()
    for lid in lussen:
        G.add_node(lid)
    for e in externe:
        G.add_node(e["id"], extern=True)
    for tb in terugkoppelingen:
        if tb["van"] in G and tb["naar"] in G:
            G.add_edge(
                tb["van"], tb["naar"],
                sterkte=tb.get("sterkte", 1),
                type=tb.get("type", "versterkend"),
            )

    pos = nx.spring_layout(G, k=1.2, iterations=200, seed=42)

    fig, ax = plt.subplots(figsize=(10, 8), dpi=150)
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#ffffff")

    # Knopen
    for lid in G.nodes():
        if lid not in pos:
            continue
        x, y = pos[lid]

        is_extern = G.nodes[lid].get("extern", False)
        lus = lussen.get(lid)

        if is_extern:
            kleur = "#f472b6"
            grootte = 25 * 40
            naam = next(
                (e.get("naam", "") for e in externe if e["id"] == lid),
                "",
            )
        else:
            kleur = KLEUR_MAP.get(lus.get("tijdschaal", "maanden"), "#94a3b8")
            grootte = lus.get("omvang", 3) * 800
            naam = lus.get("naam", "")

        rand_kleur = "white"
        rand_dikte = 2.5
        if lid in dominante:
            grootte *= 1.4
        if lid in kantelpunten:
            rand_kleur = "#ef4444"
            rand_dikte = 4

        ax.scatter(
            x, y,
            s=grootte,
            c=kleur,
            edgecolors=rand_kleur,
            linewidths=rand_dikte,
            zorder=3,
        )
        ax.text(
            x, y,
            lid,
            ha="center", va="center",
            fontsize=14,
            fontweight="bold",
            color="white",
            zorder=4,
        )
        ax.text(
            x, y - 0.18,
            naam,
            ha="center", va="top",
            fontsize=9,
            color="#333333",
            zorder=4,
        )

    # Pijlen
    for tb in terugkoppelingen:
        van = tb["van"]
        naar = tb["naar"]
        if van not in pos or naar not in pos:
            continue

        sterkte = tb.get("sterkte", 1)
        type_ = tb.get("type", "versterkend")
        kleur = KLEUR_VERSTERKEND if type_ == "versterkend" else KLEUR_VERZWAKKEND
        dikte = sterkte * 0.8

        ax.annotate(
            "",
            xy=pos[naar], xytext=pos[van],
            arrowprops=dict(
                arrowstyle="-|>",
                color=kleur,
                lw=dikte,
                shrinkA=18, shrinkB=18,
                connectionstyle="arc3,rad=0.15",
            ),
            zorder=2,
        )

    ax.set_axis_off()
    ax.margins(0.15)

    ax.set_title(
        f"Scenario {scenario.get('id', '?')}: {scenario.get('naam', '')}",
        fontsize=12,
        fontweight="bold",
        color="#1a1a1a",
        pad=15,
    )

    fig.tight_layout()
    fig.savefig(pad, bbox_inches="tight", facecolor="#ffffff")
    plt.close(fig)

    return pad
