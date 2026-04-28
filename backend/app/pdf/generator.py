"""
ReportLab PDF generator for PowerOn TCO Reports.
"""
import io
from itertools import accumulate
from datetime import datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT

from app.schemas.inputs import TCOInputs
from app.schemas.outputs import TCOResult
from app.config import LOGO_PATH

# PowerOn brand colors
POWERON_GREEN = colors.HexColor("#2E7D32")
POWERON_LIGHT = colors.HexColor("#E8F5E9")
DARK_TEXT = colors.HexColor("#1A1A1A")
GRAY = colors.HexColor("#757575")
WHITE = colors.white

SCENARIO_COLORS = ["#1565C0", "#2E7D32", "#6A1B9A", "#E65100"]
EV_COLOR = "#2E7D32"
ICE_COLOR = "#C62828"


def _fmt_cad(val: float) -> str:
    return f"${val:,.0f}"


def _fmt_km(val: float) -> str:
    return f"${val:.3f}/km"


def _make_chart_png(fig) -> io.BytesIO:
    buf = io.BytesIO()
    fig.savefig(buf, format="PNG", dpi=150, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf


def build_cumulative_chart(result: TCOResult) -> io.BytesIO:
    fig, ax = plt.subplots(figsize=(9, 4))
    for i, s in enumerate(result.scenarios):
        ev_cum = list(accumulate(y.total for y in s.ev_yearly))
        ice_cum = list(accumulate(y.total for y in s.ice_yearly))
        years = list(range(1, len(ev_cum) + 1))
        ax.plot(years, [v / 1e6 for v in ev_cum], color=SCENARIO_COLORS[i], linewidth=2,
                label=f"EV – {s.scenario_name}")
        ax.plot(years, [v / 1e6 for v in ice_cum], color=SCENARIO_COLORS[i], linewidth=2,
                linestyle="--", alpha=0.6, label=f"ICE – {s.scenario_name}")
    ax.set_xlabel("Year", fontsize=10)
    ax.set_ylabel("Cumulative Cost ($M CAD)", fontsize=10)
    ax.set_title("10-Year Cumulative Fleet Cost", fontsize=12, fontweight="bold")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:.1f}M"))
    ax.set_xticks(range(1, 11))
    ax.legend(fontsize=7, ncol=2)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return _make_chart_png(fig)


def build_breakdown_chart(result: TCOResult) -> io.BytesIO:
    s = result.scenarios[0]  # Cash scenario for breakdown
    years = [y.year for y in s.ev_yearly]
    components = {
        "Vehicle": [y.vehicle_cost for y in s.ev_yearly],
        "Electricity": [y.fuel_or_electricity for y in s.ev_yearly],
        "Maintenance": [y.maintenance for y in s.ev_yearly],
        "Charger": [y.charger_cost for y in s.ev_yearly],
        "Insurance": [y.insurance for y in s.ev_yearly],
        "Rebates": [-y.rebates for y in s.ev_yearly],
    }
    comp_colors = ["#1565C0", "#2E7D32", "#FF8F00", "#6A1B9A", "#00838F", "#C62828"]

    fig, ax = plt.subplots(figsize=(9, 4))
    bottom_pos = [0.0] * len(years)
    bottom_neg = [0.0] * len(years)
    for (name, vals), color in zip(components.items(), comp_colors):
        pos_vals = [max(v, 0) for v in vals]
        neg_vals = [min(v, 0) for v in vals]
        ax.bar(years, [v / 1e3 for v in pos_vals], bottom=[b / 1e3 for b in bottom_pos],
               label=name, color=color, alpha=0.85)
        ax.bar(years, [v / 1e3 for v in neg_vals], bottom=[b / 1e3 for b in bottom_neg],
               color=color, alpha=0.85)
        bottom_pos = [a + b for a, b in zip(bottom_pos, pos_vals)]
        bottom_neg = [a + b for a, b in zip(bottom_neg, neg_vals)]
    ax.set_xlabel("Year", fontsize=10)
    ax.set_ylabel("Cost ($K CAD)", fontsize=10)
    ax.set_title("EV Fleet Annual Cost Breakdown (Cash Scenario)", fontsize=12, fontweight="bold")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:.0f}K"))
    ax.legend(fontsize=8, ncol=3)
    ax.grid(True, alpha=0.3, axis="y")
    fig.tight_layout()
    return _make_chart_png(fig)


def build_comparison_bar(result: TCOResult) -> io.BytesIO:
    names = [s.scenario_name for s in result.scenarios]
    ev_totals = [s.ev_total_tco / 1e6 for s in result.scenarios]
    ice_totals = [s.ice_total_tco / 1e6 for s in result.scenarios]
    x = range(len(names))
    width = 0.35

    fig, ax = plt.subplots(figsize=(8, 4))
    bars1 = ax.bar([xi - width / 2 for xi in x], ev_totals, width, label="EV Fleet", color=EV_COLOR, alpha=0.85)
    bars2 = ax.bar([xi + width / 2 for xi in x], ice_totals, width, label="ICE Fleet", color=ICE_COLOR, alpha=0.85)
    ax.set_xticks(list(x))
    ax.set_xticklabels(names, fontsize=10)
    ax.set_ylabel("10-Year Total Cost ($M CAD)", fontsize=10)
    ax.set_title("Fleet TCO by Financing Scenario", fontsize=12, fontweight="bold")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:.1f}M"))
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3, axis="y")
    for bar in bars1:
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02,
                f"${bar.get_height():.1f}M", ha="center", va="bottom", fontsize=8)
    for bar in bars2:
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02,
                f"${bar.get_height():.1f}M", ha="center", va="bottom", fontsize=8)
    fig.tight_layout()
    return _make_chart_png(fig)


def generate_pdf(inputs: TCOInputs, result: TCOResult) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("title", parent=styles["Title"], textColor=POWERON_GREEN,
                                  fontSize=20, spaceAfter=6)
    h1 = ParagraphStyle("h1", parent=styles["Heading1"], textColor=POWERON_GREEN, fontSize=13,
                         spaceBefore=12, spaceAfter=4)
    h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontSize=11, spaceBefore=8, spaceAfter=4)
    body = ParagraphStyle("body", parent=styles["Normal"], fontSize=9, spaceAfter=3)
    small = ParagraphStyle("small", parent=styles["Normal"], fontSize=8, textColor=GRAY)

    story = []

    # Cover page
    if LOGO_PATH.exists():
        story.append(Image(str(LOGO_PATH), width=1.5 * inch, height=0.6 * inch))
        story.append(Spacer(1, 0.2 * inch))

    story.append(Paragraph("PowerOn Energy", title_style))
    story.append(Paragraph("Fleet TCO Analysis Report", styles["Heading2"]))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y')}", small))
    story.append(Spacer(1, 0.2 * inch))

    # Inputs summary table
    story.append(Paragraph("Analysis Parameters", h1))
    input_data = [
        ["Parameter", "Value"],
        ["Province", inputs.fleet.province],
        ["Vehicle Category", inputs.duty_cycle.vehicle_category],
        ["Daily Distance Required", f"{inputs.duty_cycle.daily_distance_km:,.0f} km"],
        ["EV Fleet Size", f"{inputs.fleet.ev_fleet_size} vehicles"],
        ["ICE Fleet Size", f"{inputs.fleet.ice_fleet_size} vehicles"],
        ["Annual KM per Vehicle", f"{inputs.fleet.annual_km_per_vehicle:,.0f} km"],
        ["Depot Charging %", f"{inputs.fleet.depot_charging_pct * 100:.0f}%"],
        ["Recommended EV", result.recommended_ev.display_name],
        ["EV MSRP", _fmt_cad(result.recommended_ev.msrp_cad)],
        ["Recommended ICE", result.recommended_ice.display_name],
        ["ICE MSRP", _fmt_cad(result.recommended_ice.msrp_cad)],
        ["Chargers Required", str(result.charger_count)],
        ["Charger Capital Cost", _fmt_cad(result.charger_total_cost)],
        ["Discount Rate", f"{inputs.discount_rate * 100:.1f}%"],
    ]
    input_table = Table(input_data, colWidths=[2.5 * inch, 4.5 * inch])
    input_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), POWERON_GREEN),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [POWERON_LIGHT, WHITE]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(input_table)
    story.append(Spacer(1, 0.2 * inch))

    # Scenario comparison table
    story.append(Paragraph("10-Year TCO Comparison by Financing Scenario", h1))
    headers = ["Metric"] + [s.scenario_name for s in result.scenarios]
    rows = [
        headers,
        ["EV Total TCO"] + [_fmt_cad(s.ev_total_tco) for s in result.scenarios],
        ["ICE Total TCO"] + [_fmt_cad(s.ice_total_tco) for s in result.scenarios],
        ["EV NPV"] + [_fmt_cad(s.ev_npv) for s in result.scenarios],
        ["ICE NPV"] + [_fmt_cad(s.ice_npv) for s in result.scenarios],
        ["EV Cost/km"] + [_fmt_km(s.ev_cost_per_km) for s in result.scenarios],
        ["ICE Cost/km"] + [_fmt_km(s.ice_cost_per_km) for s in result.scenarios],
        ["10yr Savings"] + [_fmt_cad(s.savings_vs_ice) for s in result.scenarios],
        ["Break-even Year"] + [f"Year {s.break_even_year}" if s.break_even_year else ">10 yrs" for s in result.scenarios],
    ]
    col_w = [2.0 * inch] + [1.5 * inch] * len(result.scenarios)
    comp_table = Table(rows, colWidths=col_w)
    comp_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), POWERON_GREEN),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [POWERON_LIGHT, WHITE]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(comp_table)
    story.append(PageBreak())

    # Cumulative cost chart
    story.append(Paragraph("Cumulative Fleet Cost Over 10 Years", h1))
    cum_png = build_cumulative_chart(result)
    story.append(Image(cum_png, width=7 * inch, height=3.2 * inch))
    story.append(Spacer(1, 0.2 * inch))

    # Annual breakdown chart
    story.append(Paragraph("EV Annual Cost Breakdown (Cash Scenario)", h1))
    breakdown_png = build_breakdown_chart(result)
    story.append(Image(breakdown_png, width=7 * inch, height=3.2 * inch))
    story.append(PageBreak())

    # Scenario comparison bar chart
    story.append(Paragraph("TCO by Financing Scenario", h1))
    bar_png = build_comparison_bar(result)
    story.append(Image(bar_png, width=6.5 * inch, height=3.2 * inch))
    story.append(Spacer(1, 0.3 * inch))

    # 10-year yearly table (Cash scenario)
    story.append(Paragraph("10-Year EV Cost Breakdown — Cash Scenario", h1))
    cash = result.scenarios[0]
    yr_headers = ["Year", "Vehicle", "Electricity", "Maintenance", "Tires", "Insurance", "Charger", "Rebates", "Salvage", "Total"]
    yr_rows = [yr_headers]
    for y in cash.ev_yearly:
        yr_rows.append([
            str(y.year),
            _fmt_cad(y.vehicle_cost),
            _fmt_cad(y.fuel_or_electricity),
            _fmt_cad(y.maintenance),
            _fmt_cad(y.tires),
            _fmt_cad(y.insurance),
            _fmt_cad(y.charger_cost),
            f"-{_fmt_cad(y.rebates)}" if y.rebates else "-",
            f"-{_fmt_cad(abs(y.salvage))}" if y.salvage else "-",
            _fmt_cad(y.total),
        ])
    col_widths_yr = [0.4 * inch] + [0.77 * inch] * 9
    yr_table = Table(yr_rows, colWidths=col_widths_yr)
    yr_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), POWERON_GREEN),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [POWERON_LIGHT, WHITE]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.lightgrey),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(yr_table)

    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph(
        "Prepared by PowerOn Energy. This analysis uses current-year pricing with projected escalation. "
        "All figures in Canadian dollars.",
        small,
    ))

    doc.build(story)
    return buffer.getvalue()
