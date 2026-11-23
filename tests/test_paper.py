import pytest
from pypdf import PdfReader

from phieucan import Company, Line, Slip, render_pdf


def _slip():
    return Slip("PC-A4", lines=[Line("Sắt vụn", 24360, 9120, 2, 8000)])


@pytest.mark.parametrize("paper, size_mm", [("a5", (210, 148)), ("a4", (210, 297))])
def test_paper_size(tmp_path, paper, size_mm):
    out = render_pdf(_slip(), Company("CÔNG TY MẪU"), tmp_path / f"{paper}.pdf", paper)
    box = PdfReader(out).pages[0].mediabox
    w, h = round(float(box.width) / 72 * 25.4), round(float(box.height) / 72 * 25.4)
    assert (w, h) == size_mm


def test_bad_paper(tmp_path):
    with pytest.raises(ValueError):
        render_pdf(_slip(), Company("X"), tmp_path / "x.pdf", "letter")
