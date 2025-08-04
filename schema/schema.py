from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal, Tuple
import re
from pathlib import Path
import matplotlib.font_manager as fm

def is_hex_color(s: str) -> bool:
    return bool(re.fullmatch(r"#([0-9a-fA-F]{6})", s.strip()))

def rgba_to_hex(rgba: str) -> str:
    match = re.fullmatch(r"rgba?\((\d{1,3}), *(\d{1,3}), *(\d{1,3})(, *[\d.]+)?\)", rgba)
    if not match:
        raise ValueError(f"無法解析 color: {rgba}")
    r, g, b = [int(match.group(i)) for i in range(1, 4)]
    return "#{:02x}{:02x}{:02x}".format(r, g, b)

def cmyk_to_hex(cmyk: str) -> str:
    match = re.fullmatch(r"cmyk\((\d{1,3})%, *(\d{1,3})%, *(\d{1,3})%, *(\d{1,3})%\)", cmyk)
    if not match:
        raise ValueError(f"無法解析 color: {cmyk}")
    c, m, y, k = [int(match.group(i)) / 100 for i in range(1, 5)]
    r = 255 * (1 - c) * (1 - k)
    g = 255 * (1 - m) * (1 - k)
    b = 255 * (1 - y) * (1 - k)
    return "#{:02x}{:02x}{:02x}".format(int(r), int(g), int(b))


class FieldDefinition(BaseModel):
    key: str
    type: Literal["text", "number", "date", "barcode"]
    position: Tuple[int, int]
    font_size: Optional[int] = None
    font_color: Optional[str] = None
    font_family: Optional[str] = None
    size: Optional[Tuple[int, int]] = None
    data_path: str

    @field_validator("font_color", mode="after")
    @classmethod
    def validate_color(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if is_hex_color(v):
            return v
        try:
            return rgba_to_hex(v)
        except ValueError:
            pass
        try:
            return cmyk_to_hex(v)
        except ValueError:
            pass
        raise ValueError(f"無法辨識字體顏色格式：{v}")

    @field_validator("font_family", mode="after")
    @classmethod
    def validate_font(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        font_names = {f.name for f in fm.fontManager.ttflist}
        if v not in font_names:
            available = sorted(list(font_names))[:5]
            raise ValueError(f"系統未安裝字體 '{v}'，請確認名稱是否正確，例如：{available}")
        return v
