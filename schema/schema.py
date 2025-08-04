from pathlib import Path
from typing import List, Literal, Optional, Tuple
from pydantic import BaseModel, DirectoryPath, field_validator

from .validators import validate_color_format, validate_font_family

class FieldDefinition(BaseModel):
    """
    欄位定義模型

    :param key: 欄位鍵
    :param type: 欄位類型 (text, number, date, barcode)
    :param position: 欄位位置 (x, y)
    :param font_size: 字體大小
    :param font_color: 字體顏色
    :param font_family: 字體名稱
    :param size: 條碼大小 (寬, 高)
    :param data_path: 資料路徑 (對應 CSV 欄位)
    :raises ValueError: 如果字體顏色格式不正確，則拋出此錯誤
    :raises ValueError: 如果字體名稱不正確，則拋出此錯誤
    """
    key: str
    type: Literal["text", "number", "date", "barcode"]
    position: Tuple[float, float]
    font_size: Optional[int] = None
    font_color: Optional[str] = None
    font_family: Optional[str] = None
    size: Optional[Tuple[int, int]] = None
    data_path: str

    @field_validator("font_color", mode="after")
    @classmethod
    def check_color(cls, v):
        return validate_color_format(v)

    @field_validator("font_family", mode="after")
    @classmethod
    def check_font(cls, v):
        return validate_font_family(v)

# 背景圖格式驗證
class Background(BaseModel):
    """
    背景設定模型

    :param image: 背景圖片路徑
    :param color: 背景顏色
    :raises ValueError: 如果圖片檔案不存在，則拋出此錯誤
    """

    image: str  # 只存檔名，相對於 templates/
    color: str

    @field_validator("image", mode="after")
    @classmethod
    def check_image_file_exists(cls, v: str) -> str:
        path = Path("templates") / v
        if not path.is_file():
            raise ValueError(f"background.image 檔案不存在：{path}")
        return v

class PhotoConfig(BaseModel):
    """
    照片設定模型

    :param folder: 照片資料夾路徑
    :param position: 照片位置 (x, y)
    :param size: 照片大小 (寬, 高)
    :param border_radius: 照片邊框半徑
    :raises ValueError: 如果資料夾為空，則拋出此錯誤
    """
    folder: DirectoryPath  # 路徑若不存在，Invalid
    position: Tuple[int, int]
    size: Tuple[int, int]
    border_radius: Optional[int] = 0

    @field_validator("folder", mode="after")
    @classmethod
    def check_folder_not_empty(cls, v: Path) -> Path:
        if not any(v.iterdir()):
            raise ValueError(f"photo.folder 資料夾存在，但為空：{v}")
        return v

class OutputConfig(BaseModel):
    """
    輸出設定模型

    :param dpi: 圖片解析度
    :param save_to: 儲存路徑格式
    :param output_file_format: 輸出檔案格式
    :param other_file: 其他檔案模式列表
    """
    dpi: int = 300
    save_to: str
    output_file_format: str
    other_file: Optional[List[str]] = []

class DocumentConfig(BaseModel):
    """
    模版描述檔格式的模型

    :param id: 模版 ID
    :param country: 國家或地區
    :param version: 模版版本
    :param background: 背景設定
    :param fields: 欄位定義列表
    :param photo: 照片設定
    :param output: 輸出設定
    """
    id: str
    country: str
    version: str
    background: Background
    fields: List[FieldDefinition]
    photo: PhotoConfig
    output: OutputConfig
