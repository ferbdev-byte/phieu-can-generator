import json
from datetime import datetime

import pytest
from pypdf import PdfReader

from phieucan import Company, Line, Slip, doc_so, render_pdf, so_tien_bang_chu
from phieucan.cli import main


@pytest.mark.parametrize(
    "n, text",
    [
        (0, "không"),
        (5, "năm"),
        (10, "mười"),
        (15, "mười lăm"),
        (21, "hai mươi mốt"),
        (24, "hai mươi tư"),
        (14, "mười bốn"),
        (105, "một trăm lẻ năm"),
        (1001, "một nghìn không trăm lẻ một"),
        (1015, "một nghìn không trăm mười lăm"),
        (1_250_000, "một triệu hai trăm năm mươi nghìn"),
        (119_480_000, "một trăm mười chín triệu bốn trăm tám mươi nghìn"),
        (1_000_000_000_000, "một nghìn tỷ"),
        (-35, "âm ba mươi lăm"),
    ],
)
def test_doc_so(n, text):
    assert doc_so(n) == text


def test_so_tien_bang_chu():
    assert so_tien_bang_chu(1_500_000) == "Một triệu năm trăm nghìn đồng chẵn."


def test_line_math_and_swap():
    x = Line("Sắt vụn", 9_120, 24_360, impurity_pct=2, unit_price=8_000)  # nhập ngược tổng/bì
    assert (x.gross_kg, x.tare_kg, x.net_kg, x.deduction_kg, x.payable_kg) == (24360, 9120, 15240, 305, 14935)
    assert x.amount == 119_480_000


def test_bad_impurity():
    with pytest.raises(ValueError):
        Line("x", 10, 5, impurity_pct=120)


def slip():
    return Slip(
        "PC261123-001", "PHIẾU THU MUA PHẾ LIỆU", "Công ty TNHH Mẫu", "0900 000 000", "51C-123.45", "Nguyễn Văn A",
        datetime(2026, 11, 23, 8, 15), datetime(2026, 11, 23, 8, 31),
        [Line("Sắt vụn loại 2", 24_360, 9_120, 2, 8_000), Line("Đồng cáp", 620, 0, 0, 175_000)],
        note="Dữ liệu mẫu", weigher="Trần Thị B",
    )


def test_render_pdf_has_vietnamese_text(tmp_path):
    out = render_pdf(slip(), Company("CÔNG TY MẪU", "Số 1, đường Mẫu", "0900 000 000"), tmp_path / "p.pdf")
    text = PdfReader(out).pages[0].extract_text()
    assert "PHIẾU THU MUA PHẾ LIỆU" in text
    assert "51C-123.45" in text
    assert "227.980.000" in text  # 119.480.000 + 108.500.000
    assert "Hai trăm hai mươi bảy triệu chín trăm tám mươi nghìn đồng chẵn." in text.replace("\n", " ")


def test_from_weighbridge_record():
    rec = {"plate": "60H-678.90", "material": "Nhôm", "gross_kg": 15880, "tare_kg": 7040, "impurity_pct": 1,
           "unit_price": 48000, "times": {"lan_1": "2026-11-23T09:00:00", "lan_2": "2026-11-23T09:20:00"}}
    s = Slip.from_dict(rec)
    assert s.plate == "60H-678.90" and s.lines[0].net_kg == 8840 and s.time_out.minute == 20


def test_cli_batch(tmp_path, capsys):
    jl = tmp_path / "phieu.jsonl"
    rows = [{"plate": f"51C-00{i}.00", "gross_kg": 10000 + i, "tare_kg": 5000, "unit_price": 8000} for i in range(3)]
    jl.write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")
    co = tmp_path / "co.json"
    co.write_text(json.dumps({"name": "CÔNG TY MẪU", "phone": "0900"}), encoding="utf-8")
    assert main([str(jl), "-c", str(co), "-o", str(tmp_path / "out")]) == 0
    assert len(list((tmp_path / "out").glob("*.pdf"))) == 3
