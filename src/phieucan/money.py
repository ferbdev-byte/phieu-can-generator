"""Đọc số thành chữ tiếng Việt, đúng các quy tắc "lẻ", "mốt", "lăm", "tư", "mươi"."""

from __future__ import annotations

DIGITS = ["không", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"]
UNITS = ["", "nghìn", "triệu", "tỷ", "nghìn tỷ", "triệu tỷ"]


def _ba_chu_so(n: int, full: bool) -> str:
    """Đọc một nhóm 0..999. `full`: nhóm không đứng đầu nên phải đọc cả 'không trăm', 'lẻ'."""
    tram, chuc, dv = n // 100, n // 10 % 10, n % 10
    words: list[str] = []
    if tram or full:
        words += [DIGITS[tram], "trăm"]
    if chuc == 0:
        if dv and (tram or full):
            words.append("lẻ")
    elif chuc == 1:
        words.append("mười")
    else:
        words += [DIGITS[chuc], "mươi"]
    if dv:
        if dv == 1 and chuc > 1:
            words.append("mốt")
        elif dv == 5 and chuc > 0:
            words.append("lăm")
        elif dv == 4 and chuc > 1:
            words.append("tư")
        else:
            words.append(DIGITS[dv])
    return " ".join(words)


def doc_so(n: int) -> str:
    """doc_so(1_250_000) -> 'một triệu hai trăm năm mươi nghìn'."""
    if n < 0:
        return "âm " + doc_so(-n)
    if n == 0:
        return "không"
    groups: list[int] = []
    while n:
        groups.append(n % 1000)
        n //= 1000
    if len(groups) > len(UNITS):
        raise ValueError("số quá lớn")
    top = len(groups) - 1
    parts = [
        f"{_ba_chu_so(g, full=i != top)} {UNITS[i]}".strip()
        for i, g in zip(range(top, -1, -1), reversed(groups), strict=True)
        if g
    ]
    return " ".join(parts)


def so_tien_bang_chu(n: int) -> str:
    """'Một triệu hai trăm năm mươi nghìn đồng chẵn.'"""
    s = doc_so(int(n))
    return s[0].upper() + s[1:] + " đồng chẵn."
