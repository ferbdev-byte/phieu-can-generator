"""Vẽ phiếu ra PDF khổ A5 ngang bằng reportlab, font DejaVu Sans đủ dấu tiếng Việt."""

from __future__ import annotations

from datetime import datetime
from importlib import resources
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A5, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .model import Company, Slip
from .money import so_tien_bang_chu

_FONTS_READY = False


def _fonts() -> None:
    global _FONTS_READY
    if _FONTS_READY:
        return
    base = resources.files("phieucan")
    pdfmetrics.registerFont(TTFont("VN", str(base / "DejaVuSans.ttf")))
    pdfmetrics.registerFont(TTFont("VN-B", str(base / "DejaVuSans-Bold.ttf")))
    registerFontFamily("VN", normal="VN", bold="VN-B", italic="VN", boldItalic="VN-B")
    _FONTS_READY = True


def n(x: float) -> str:
    return f"{x:,.0f}".replace(",", ".")


def _dt(d: datetime | None) -> str:
    return d.strftime("%H:%M %d/%m/%Y") if d else ""


def render_pdf(slip: Slip, company: Company, out: str | Path) -> Path:
    _fonts()
    out = Path(out)
    s = ParagraphStyle("t", fontName="VN", fontSize=8.5, leading=11)
    b = ParagraphStyle("b", parent=s, fontName="VN-B")
    title = ParagraphStyle("h", fontName="VN-B", fontSize=14, leading=18, alignment=1, spaceAfter=2)
    center = ParagraphStyle("c", parent=s, alignment=1)

    doc = SimpleDocTemplate(str(out), pagesize=landscape(A5), leftMargin=10 * mm, rightMargin=10 * mm,
                            topMargin=8 * mm, bottomMargin=8 * mm, title=f"{slip.kind} {slip.number}",
                            author=company.name)
    story = []

    head = Table(
        [[Paragraph(f"<b>{company.name}</b><br/>{company.address}<br/>ĐT: {company.phone}"
                    + (f" · MST: {company.tax_code}" if company.tax_code else ""), s),
          Paragraph(f"Số: <b>{slip.number}</b>", ParagraphStyle("r", parent=s, alignment=2))]],
        colWidths=[140 * mm, None],
    )
    head.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
    story += [head, Spacer(1, 3 * mm), Paragraph(slip.kind, title)]

    info = [
        [Paragraph(f"Khách hàng: <b>{slip.partner}</b>", s), Paragraph(f"Điện thoại: {slip.partner_phone}", s)],
        [Paragraph(f"Biển số xe: <b>{slip.plate}</b>", s), Paragraph(f"Tài xế: {slip.driver}", s)],
        [Paragraph(f"Giờ cân lần 1: {_dt(slip.time_in)}", s), Paragraph(f"Giờ cân lần 2: {_dt(slip.time_out)}", s)],
    ]
    t = Table(info, colWidths=[95 * mm, None])
    t.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 1)]))
    story += [t, Spacer(1, 3 * mm)]

    header = ["#", "Loại hàng", "Tổng (kg)", "Bì (kg)", "Hàng (kg)", "Trừ tạp", "Tính tiền (kg)", "Đơn giá", "Thành tiền"]
    rows = [[Paragraph(h, ParagraphStyle("th", parent=b, alignment=1, textColor=colors.white)) for h in header]]
    for i, x in enumerate(slip.lines, 1):
        tru = f"{x.impurity_pct:g}".replace(".", ",") + f"% ({n(x.deduction_kg)})" if x.impurity_pct else "—"
        rows.append([str(i), Paragraph(x.material, s), n(x.gross_kg), n(x.tare_kg), n(x.net_kg), tru,
                     n(x.payable_kg), n(x.unit_price), n(x.amount)])
    rows.append(["", Paragraph("<b>Tổng cộng</b>", s), "", "", "", "", n(slip.total_kg), "", n(slip.total_amount)])
    table = Table(rows, colWidths=[9 * mm, 36 * mm, 18 * mm, 16 * mm, 18 * mm, 21 * mm, 22 * mm, 17 * mm, None],
                  repeatRows=1)
    table.setStyle(TableStyle([
        ("FONT", (0, 0), (-1, -1), "VN", 8.5),
        ("FONT", (0, -1), (-1, -1), "VN-B", 8.5),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#f3f4f6")]),
        ("LINEBELOW", (0, -2), (-1, -2), 0.6, colors.HexColor("#1f2937")),
        ("ALIGN", (2, 1), (-1, -1), "RIGHT"),
        ("ALIGN", (0, 1), (0, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#1f2937")),
    ]))
    story += [table, Spacer(1, 2.5 * mm)]
    story.append(Paragraph(f"Số tiền bằng chữ: <b>{so_tien_bang_chu(slip.total_amount)}</b>", s))
    if slip.note:
        story.append(Paragraph(f"Ghi chú: {slip.note}", s))
    story.append(Spacer(1, 4 * mm))

    sign = Table(
        [[Paragraph("<b>Khách hàng</b><br/>(ký, ghi rõ họ tên)", center),
          Paragraph("<b>Người cân</b><br/>(ký, ghi rõ họ tên)", center),
          Paragraph("<b>Thủ kho</b><br/>(ký, ghi rõ họ tên)", center)],
         ["", Paragraph(slip.weigher, center), ""]],
        colWidths=[63 * mm] * 3, rowHeights=[None, 16 * mm],
    )
    sign.setStyle(TableStyle([("VALIGN", (0, 1), (-1, 1), "BOTTOM")]))
    story.append(sign)
    doc.build(story)
    return out
