"""Dữ liệu một phiếu: công ty, đối tác, xe, các dòng hàng."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass
class Company:
    name: str
    address: str = ""
    phone: str = ""
    tax_code: str = ""


@dataclass
class Line:
    material: str
    gross_kg: int          # tổng (xe + hàng)
    tare_kg: int           # bì (xe không)
    impurity_pct: float = 0.0
    unit_price: int = 0    # đồng/kg

    def __post_init__(self):
        if self.gross_kg < self.tare_kg:
            self.gross_kg, self.tare_kg = self.tare_kg, self.gross_kg
        if not 0 <= self.impurity_pct < 100:
            raise ValueError("% tạp chất phải trong khoảng 0–100")

    @property
    def net_kg(self) -> int:
        return self.gross_kg - self.tare_kg

    @property
    def deduction_kg(self) -> int:
        return round(self.net_kg * self.impurity_pct / 100)

    @property
    def payable_kg(self) -> int:
        return self.net_kg - self.deduction_kg

    @property
    def amount(self) -> int:
        return self.payable_kg * self.unit_price


@dataclass
class Slip:
    number: str
    kind: str = "PHIẾU CÂN HÀNG"   # hoặc "PHIẾU THU MUA PHẾ LIỆU"
    partner: str = ""
    partner_phone: str = ""
    plate: str = ""
    driver: str = ""
    time_in: datetime | None = None
    time_out: datetime | None = None
    lines: list[Line] = field(default_factory=list)
    note: str = ""
    weigher: str = ""

    @property
    def total_kg(self) -> int:
        return sum(x.payable_kg for x in self.lines)

    @property
    def total_amount(self) -> int:
        return sum(x.amount for x in self.lines)

    @classmethod
    def from_dict(cls, d: dict) -> Slip:
        """Nhận cả định dạng riêng lẫn một dòng phiếu của weighbridge-reader."""
        if "gross_kg" in d and "lines" not in d:  # bản ghi weighbridge-reader
            times = d.get("times", {})
            return cls(
                number=d.get("number", ""),
                plate=d.get("plate", ""),
                time_in=datetime.fromisoformat(times["lan_1"]) if "lan_1" in times else None,
                time_out=datetime.fromisoformat(times["lan_2"]) if "lan_2" in times else None,
                lines=[Line(d.get("material") or "Hàng", d["gross_kg"], d["tare_kg"],
                            d.get("impurity_pct", 0.0), d.get("unit_price", 0))],
            )
        d = dict(d)
        d["lines"] = [Line(**x) for x in d.get("lines", [])]
        for k in ("time_in", "time_out"):
            if d.get(k):
                d[k] = datetime.fromisoformat(d[k])
        return cls(**d)


def load_company(path: str | Path) -> Company:
    return Company(**json.loads(Path(path).read_text(encoding="utf-8")))
