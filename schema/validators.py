import re
from typing import Optional
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


def validate_color_format(color: Optional[str]) -> Optional[str]:
    if color is None:
        return None
    if is_hex_color(color):
        return color
    try:
        return rgba_to_hex(color)
    except ValueError:
        pass
    try:
        return cmyk_to_hex(color)
    except ValueError:
        pass
    raise ValueError(f"無法辨識或轉換 color: {color}")


def validate_font_family(font: Optional[str]) -> Optional[str]:
    if font is None:
        return None
    
    # 如果指定的是 .ttf 檔案，檢查 fonts 資料夾中是否存在
    if font.endswith('.ttf'):
        font_path = Path("fonts") / font
        if not font_path.exists():
            available_fonts = list(Path("fonts").glob("*.ttf")) if Path("fonts").exists() else []
            available_names = [f.name for f in available_fonts]
            raise ValueError(f"字體檔案不存在: {font_path}，可用字體: {available_names}")
        return font
    
    # 原有的系統字體檢查邏輯
    font_names = {f.name for f in fm.fontManager.ttflist}
    if font not in font_names:
        raise ValueError(f"系統未安裝字體 '{font}'，請確認拼字或安裝字體")
    return font
