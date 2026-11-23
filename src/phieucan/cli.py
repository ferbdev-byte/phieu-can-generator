"""Dòng lệnh: xuất một phiếu từ JSON, hoặc cả lô từ file JSON Lines của weighbridge-reader."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from . import __version__
from .model import Company, Slip, load_company
from .render import render_pdf


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="phieucan", description="Xuất phiếu cân ra PDF.")
    p.add_argument("--version", action="version", version=f"phieucan {__version__}")
    p.add_argument("input", help="file .json (một phiếu) hoặc .jsonl (nhiều phiếu)")
    p.add_argument("-c", "--company", help="file JSON thông tin công ty")
    p.add_argument("-o", "--out", default="phieu", help="thư mục đầu ra")
    p.add_argument("--prefix", default="PC", help="tiền tố số phiếu tự sinh")
    p.add_argument("--kind", help='tiêu đề phiếu, vd. "PHIẾU THU MUA PHẾ LIỆU"')
    args = p.parse_args(argv)

    company = load_company(args.company) if args.company else Company("TÊN CÔNG TY")
    src = Path(args.input)
    text = src.read_text(encoding="utf-8")
    records = [json.loads(x) for x in text.splitlines() if x.strip()] if src.suffix == ".jsonl" else [json.loads(text)]

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%y%m%d")
    for i, rec in enumerate(records, 1):
        slip = Slip.from_dict(rec)
        slip.number = slip.number or f"{args.prefix}{stamp}-{i:03d}"
        if args.kind:
            slip.kind = args.kind
        path = render_pdf(slip, company, out_dir / f"{slip.number}.pdf")
        print(f"{path}  ({len(slip.lines)} dòng, {slip.total_amount:,} đ)".replace(",", "."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
