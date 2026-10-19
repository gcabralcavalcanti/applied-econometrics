"""Final report of a paper, built from its own outputs: final-reports/<paper>.pdf.

Page 1: question, short result and reading (from the paper README) and the data-check summary.
Then the main tables (parsed from the LaTeX the pipeline wrote) and the main figures (PNG embedded; PDF figures
appended as pages). Running the pipeline again rebuilds the report from the new outputs.

    python -m applied_econometrics.report              # every paper
    python -m applied_econometrics.report 03           # one paper
"""

from __future__ import annotations

import io
import json
import re
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pypdf import PdfReader, PdfWriter  # noqa: E402
from reportlab import rl_config  # noqa: E402
from reportlab.lib import colors  # noqa: E402
from reportlab.lib.pagesizes import A4  # noqa: E402
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet  # noqa: E402
from reportlab.lib.units import cm  # noqa: E402
from reportlab.platypus import (
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,  # noqa: E402
    Table,
    TableStyle,
)

from applied_econometrics import config  # noqa: E402
from applied_econometrics.tables import _clean, _rows  # noqa: E402

rl_config.invariant = 1  # no timestamps or random ids: same outputs -> same PDF

MAIN = {
    "01-phillips-curve": {
        "tables": ["q2_tab_phillips_dinamica", "q2_tab_hac_comparacao", "q2_tab_robustez", "q2_tab_estacionariedade"],
        "figures": ["q2_fig_series.pdf", "q2_fig_phillips_scatter.pdf", "q2_fig_acf_residuos.pdf"],
    },
    "02-crime-panel": {
        "tables": ["q3_tab_fe_condado", "q3_tab_duas_vias", "q3_tab_cluster", "q3_tab_heterocedasticidade"],
        "figures": ["q3_fig_painel_descritivo.png", "q3_fig_dispersao.png", "q3_fig_residuos_scatter.png"],
    },
    "03-religion-and-domestic-violence": {
        "tables": ["tab_principal", "tab_robustez", "tab_poisson", "tab_refino_denominador"],
        "figures": ["fig_evang_vd.png", "fig_proxy_vd.png", "fig_coef_janelas.png"],
    },
    "04-fund-selection": {
        "tables": ["tab_persistence", "tab_transition", "tab_costs", "tab_montecarlo"],
        "figures": ["fig_costs.png", "fig_montecarlo.png"],
    },
}
COURSE = (
    "It extracts the quantitative work of a longer paper I wrote for a UFRJ econometrics course; "
    "the full paper is available on request."
)
ORIGIN = {
    "01-phillips-curve": COURSE,
    "02-crime-panel": COURSE,
    "03-religion-and-domestic-violence": COURSE,
    "04-fund-selection": "This study was built for this portfolio from public CVM data.",
}
TITLES = {  # tables written without a caption
    "tab_principal": "Main models: evangelical density and recorded domestic violence",
    "tab_robustez": "Robustness: evangelical density coefficient across samples and errors",
    "tab_poisson": "Poisson with population offset",
    "tab_refino_denominador": "Refinement: rate over the full 3-year window",
}

ss = getSampleStyleSheet()
H1 = ParagraphStyle("h1", parent=ss["Title"], fontSize=16, leading=20, alignment=0, spaceAfter=6)
H2 = ParagraphStyle("h2", parent=ss["Heading2"], fontSize=11.5, leading=14, spaceBefore=8, spaceAfter=4)
BODY = ParagraphStyle("body", parent=ss["BodyText"], fontSize=9.5, leading=13)
NOTE = ParagraphStyle(
    "note",
    parent=ss["BodyText"],
    fontSize=9,
    leading=12,
    backColor=colors.HexColor("#f2f1ee"),
    borderPadding=6,
    spaceBefore=4,
    spaceAfter=8,
)
SMALL = ParagraphStyle("small", parent=BODY, fontSize=8, leading=10, textColor=colors.HexColor("#52514e"))
CELL = ParagraphStyle("cell", parent=BODY, fontSize=7.5, leading=9)


def _md(text: str) -> str:
    """Minimal Markdown -> reportlab markup (bold, code, escapes)."""
    t = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"`(.+?)`", r"<font face='Courier'>\1</font>", t)
    return t


def _section(readme: str, name: str) -> str:
    m = re.search(rf"^## {name}\s*$(.*?)(?=^## |\Z)", readme, flags=re.M | re.S)
    return m.group(1).strip() if m else ""


def _paragraphs(block: str) -> list:
    out, para = [], []
    for line in block.splitlines():
        if line.startswith("- "):
            out.append(Paragraph("• " + _md(line[2:]), BODY))
        elif not line.strip():
            if para:
                out.append(Paragraph(_md(" ".join(para)), BODY))
                para = []
        else:
            para.append(line.strip())
    if para:
        out.append(Paragraph(_md(" ".join(para)), BODY))
    return out


def _table(tex_path: Path):
    tex = tex_path.read_text(encoding="utf-8")
    cap = re.search(r"\\caption\{(.*?)\}(?:\\label|\s*$)", tex, flags=re.M | re.S)
    title = TITLES.get(tex_path.stem) or (_clean(cap.group(1)) if cap else tex_path.stem)
    rows = [[c for c in r] for r in _rows(tex)]
    width = max(len(r) for r in rows)
    rows = [r + [""] * (width - len(r)) for r in rows]
    data = [[Paragraph(_md(c), CELL) for c in r] for r in rows]
    first = 4.6 * cm if width > 3 else 6 * cm
    other = (A4[0] - 3 * cm - first) / max(width - 1, 1)
    t = Table(data, colWidths=[first] + [other] * (width - 1), repeatRows=1)
    t.setStyle(
        TableStyle(
            [
                ("LINEABOVE", (0, 0), (-1, 0), 0.8, colors.black),
                ("LINEBELOW", (0, 0), (-1, 0), 0.4, colors.black),
                ("LINEBELOW", (0, -1), (-1, -1), 0.8, colors.black),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 1),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
            ]
        )
    )
    return KeepTogether([Paragraph(_md(title), H2), t, Paragraph(f"Source: output/{tex_path.name}", SMALL)])


def build(paper: str) -> Path:
    pdir = config.PAPERS / paper
    readme = (pdir / "README.md").read_text(encoding="utf-8")
    title = readme.splitlines()[0].lstrip("# ").strip()
    checks = json.loads((pdir / "output" / "data_checks.json").read_text(encoding="utf-8"))["summary"]
    story = [
        Paragraph(_md(title), H1),
        Paragraph(
            "This report's text is generated automatically from the code's outputs. The main output is the "
            "quantitative part: data, checks, models and tables. " + ORIGIN[paper],
            NOTE,
        ),
        Paragraph("Question", H2),
        *_paragraphs(_section(readme, "Question")),
        Paragraph("Result", H2),
        *_paragraphs(_section(readme, "Result")),
        Paragraph("Data checks", H2),
        Paragraph(
            f"{checks['pass']} pass, {checks['warn']} warnings, {checks['fail']} fail "
            "(details in output/data_checks.json).",
            BODY,
        ),
        PageBreak(),
        Paragraph("Main tables", H1),
    ]
    files = {p.name: p for p in pdir.glob("output/**/*") if p.is_file()}
    for stem in MAIN[paper]["tables"]:
        story += [_table(files[f"{stem}.tex"]), Spacer(1, 8)]
    pngs = [files[f] for f in MAIN[paper]["figures"] if f.endswith(".png")]
    if pngs:
        story += [PageBreak(), Paragraph("Main figures", H1)]
        for p in pngs:
            img = Image(str(p))
            scale = min((A4[0] - 3 * cm) / img.imageWidth, 9.5 * cm / img.imageHeight)
            img.drawWidth, img.drawHeight = img.imageWidth * scale, img.imageHeight * scale
            story += [
                KeepTogether([img, Paragraph(f"Source: output/{p.relative_to(pdir / 'output').as_posix()}", SMALL)]),
                Spacer(1, 10),
            ]
    buf = io.BytesIO()
    SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
        title=title,
        author="",
        subject="",
        creator="",
        producer="",
    ).build(story)
    writer = PdfWriter()
    writer.append(PdfReader(buf))
    for f in MAIN[paper]["figures"]:  # vector figures (PDF) appended as pages
        if f.endswith(".pdf"):
            writer.append(PdfReader(files[f]))
    writer.add_metadata({"/Title": title})
    out = config.ROOT / "final-reports" / f"{paper}.pdf"
    out.parent.mkdir(exist_ok=True)
    with open(out, "wb") as fh:
        writer.write(fh)
    print(f"[report] {paper}: {len(writer.pages)} pages -> {out.relative_to(config.ROOT)}")
    return out


if __name__ == "__main__":
    keys = sys.argv[1:] or [p[:2] for p in MAIN]
    for paper in MAIN:
        if paper[:2] in keys:
            build(paper)
