# 基於模板描述檔的證件生成引擎
# Template-based Document Generation Engine

from datetime import datetime
import os
import csv
from pathlib import Path
from typing import Dict, Any, List, Tuple, Union
from PIL import Image, ImageDraw, ImageFont
import logging

from schema import load_config, DocumentConfig
from barcode import Code128
from barcode.writer import ImageWriter
import io

logger = logging.getLogger(__name__)

class DocumentGenerator:
    """基於模板描述檔的證件生成器"""
    
    def __init__(self, template_config_path: str):
        """
        初始化證件生成器
        
        :param template_config_path: 模板描述檔路徑
        """
        self.config = load_config(template_config_path)
        self.template_dir = Path("templates")
        self.output_dir = Path("output")
        
        # 載入背景圖片
        self.background_image = self._load_background()
        
    def _load_background(self) -> Image.Image:
        """載入背景圖片"""
        bg_path = self.template_dir / self.config.background.image
        if not bg_path.exists():
            raise FileNotFoundError(f"背景圖片不存在: {bg_path}")
        
        return Image.open(bg_path).convert("RGBA")
    
    def _get_font(self, font_family: str, font_size: int) -> ImageFont.FreeTypeFont:
        """取得字體物件"""
        try:
            # 如果指定的是 .ttf 檔案，從 fonts 資料夾載入
            if font_family.endswith('.ttf'):
                font_path = Path("fonts") / font_family
                if font_path.exists():
                    return ImageFont.truetype(str(font_path), font_size)
                else:
                    logger.warning(f"字體檔案不存在: {font_path}，使用預設字體")
                    return ImageFont.load_default()
            
            # 嘗試直接使用系統字體名稱
            return ImageFont.truetype(font_family, font_size)
        except OSError:
            try:
                # 嘗試預設字體
                return ImageFont.truetype("arial.ttf", font_size)
            except OSError:
                # 最後回到預設字體
                logger.warning(f"無法載入字體 {font_family}，使用預設字體")
                return ImageFont.load_default()
    
    def _generate_barcode(self, data: str) -> Image.Image:
        """生成條碼圖片"""
        try:
            # 創建條碼
            code128 = Code128(data, writer=ImageWriter())
            
            # 將條碼渲染到記憶體
            buffer = io.BytesIO()
            code128.write(buffer)
            buffer.seek(0)
            
            # 載入圖片並轉換格式
            barcode_img = Image.open(buffer).convert("RGBA")

            return barcode_img
            
        except Exception as e:
            logger.error(f"條碼生成失敗: {e}")
            # 如果條碼生成失敗，返回一個空白圖片
            return Image.new("RGBA", (200, 50), (255, 255, 255, 0))
    
    def _resize_photo_cover(self, photo: Image.Image, size: Union[Tuple[int, int], None] = None) -> Image.Image:
        """
        以 cover 方式縮放照片（類似 CSS background-size: cover）
        縮放照片以填滿目標區域，保持比例並從中心裁切
        """
        # 目標大小
        if size is None:
            size = self.config.photo.size
        target_width = int(size[0] or self.config.photo.size[0])
        target_height = int(size[1] or self.config.photo.size[1])
        logger.debug(f"照片目標尺寸: {target_width}x{target_height}")
        
        # 計算裁切比例，選擇較大的比例以填滿目標區域
        original_width, original_height = photo.size
        logger.debug(f"原始照片尺寸: {original_width}x{original_height}")
        
        scale_w = target_width / original_width
        scale_h = target_height / original_height
        scale = max(scale_w, scale_h)  # 使用較大的比例確保填滿
        logger.debug(f"縮放比例: {scale}")
        
        # 按比例縮放照片
        new_width = int(original_width * scale)
        new_height = int(original_height * scale)
        photo = photo.resize((new_width, new_height), Image.Resampling.LANCZOS)
        logger.debug(f"縮放後照片尺寸: {new_width}x{new_height}")
        
        # 計算裁切位置（從中心裁切）
        left = (new_width - target_width) // 2
        top = (new_height - target_height) // 2
        right = left + target_width
        bottom = top + target_height
        
        # 裁切照片
        photo = photo.crop((left, top, right, bottom))
        logger.debug(f"照片裁切完成，裁切區域: ({left}, {top}, {right}, {bottom})")

        # 創建圓角遮罩
        mask = Image.new('L', (target_width, target_height), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle([0, 0, target_width, target_height], self.config.photo.border_radius, fill=255)
        logger.debug("圓角遮罩創建完成")

        # 創建帶圓角的照片
        rounded_photo = Image.new('RGBA', (target_width, target_height), (255, 255, 255, 0))
        rounded_photo.paste(photo, (0, 0))
        rounded_photo.putalpha(mask)
        logger.debug("圓角照片創建完成")
        
        return rounded_photo
    
    def _sanitize_filename(self, filename: str) -> str:
        """清理檔案名稱，移除不合法的字符"""
        import re
        # 移除不合法的檔案名稱字符
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # 移除多餘的空格
        filename = filename.strip()
        return filename
    
    def _load_photo(self, csv_row: Dict[str, str]) -> Image.Image:
        """載入個人照片"""
        photo_dir = Path(self.config.photo.folder)
        
        # 嘗試不同的照片檔名格式
        possible_names = [
            f"{csv_row.get('name', '')}.png",
            f"{csv_row.get('name', '')}.jpg", 
            f"{csv_row.get('name', '')}.jpeg",
            f"{csv_row.get('id_number', '')}.png",
            f"{csv_row.get('id_number', '')}.jpg",
            f"{csv_row.get('id_number', '')}.jpeg",
        ]
        
        for name in possible_names:
            photo_path = photo_dir / name
            if photo_path.exists():
                photo = Image.open(photo_path).convert("RGBA")
                return self._resize_photo_cover(photo)
        
        # 如果找不到照片，創建一個預設的佔位圖
        logger.warning(f"找不到照片: {csv_row.get('name', '')}, 使用預設佔位圖")
        size = (int(self.config.photo.size[0]), int(self.config.photo.size[1]))
        placeholder = Image.new("RGBA", size, (200, 200, 200, 255))
        draw = ImageDraw.Draw(placeholder)
        draw.text(
            (size[0]//2, size[1]//2),
            "無照片",
            fill=(100, 100, 100, 255),
            anchor="mm"
        )
        return placeholder
    
    def generate_document(self, csv_row: Dict[str, str]) -> Image.Image:
        """
        根據模板配置生成證件
        
        :param csv_row: CSV 資料行
        :return: 生成的證件圖片
        """
        # 複製背景圖片
        document = self.background_image.copy()
        draw = ImageDraw.Draw(document)
        
        # 加入照片 - 位置可以使用浮點數
        if self.config.photo.enabled: 
            photo = self._load_photo(csv_row)
            document.paste(photo, self.config.photo.position, photo)
        
        # 處理每個欄位
        for field in self.config.fields:
            try:
                self._render_field(document, draw, field, csv_row)
            except Exception as e:
                logger.error(f"渲染欄位失敗 {field.key}: {e}")
                continue
        
        return document
    
    def _render_field(self, document: Image.Image, draw: ImageDraw.Draw, field, data_dict: Dict[str, Any]):
        """渲染單個欄位"""
        # 取得資料值
        data_value = data_dict.get(field.data_path, "")
        if not data_value:
            logger.warning(f"欄位 {field.key} 的資料路徑 {field.data_path} 沒有對應的值")
            return
        
        if field.type == "barcode":
            self._render_barcode(document, field, str(data_value))
        elif field.type == "date":
            self._render_date(document, draw, field, data_value)
        else:
            self._render_text(draw, field, str(data_value))
    
    def _render_text(self, draw: ImageDraw.Draw, field, text: str):
        """渲染文字欄位"""
        # 取得字體
        font_size = field.font_size or 16
        font_family = field.font_family or "arial"
        font = self._get_font(font_family, font_size)
        
        # 取得顏色
        color = field.font_color or "#000000"

        # 格式化字串
        # 如果text裡面有任何以大括號包裹的字串，就視為格式化字串
        # 將字串中的大括號視為CSV欄位名，並替換為對應的資料
        if "{" in text and "}" in text:
            try:
                text = text.format(**field.data_dict)
            except KeyError as e:
                logger.error(f"格式化字串失敗: {text}，缺少欄位 {e}")
                return

        # 直接使用浮點數位置 - PIL 支援浮點數位置
        draw.text(
            field.position,
            text,
            fill=color,
            font=font
        )

    def _render_barcode(self, document: Image.Image, field, data: str):
        """渲染條碼欄位"""
        # 生成條碼圖片
        barcode_img = self._generate_barcode(data)
        
        # 如果有指定大小，調整條碼大小 - 這裡需要整數
        if field.size:
            # 只有大小需要轉換為整數
            logging.debug(f"圖片大小：{int(field.size[0])}, {int(field.size[1])}")
            size = (int(field.size[0]), int(field.size[1]))
            barcode_img = barcode_img.resize(size, Image.Resampling.LANCZOS)
            barcode_img = self._resize_photo_cover(barcode_img, size)

        # 將位置元組轉換成整數
        int_pos = (int(field.position[0]), int(field.position[1]))
        
        # 位置可以使用浮點數
        document.paste(barcode_img, int_pos, barcode_img)

    def _render_date(self, document: Image.Image, draw: ImageDraw.Draw, field, date_str: str):
        """渲染日期欄位"""
        # 解析日期字串
        try:
            date_obj = datetime.strptime(date_str, "%Y/%m/%d")
            formatted_date = date_obj.strftime(field.date_format or "%Y/%m/%d")
        except ValueError:
            logger.error(f"無法解析日期: {date_str}，請確保來源的日期格式正確（YYYY/MM/DD）")
            formatted_date = date_str

        # 將日期字串分割成含有年月日的陣列
        date_arr = formatted_date.split('/')

        # 處理字體
        font_size = field.font_size or 16
        font_family = field.font_family or "arial"
        font = self._get_font(font_family, font_size)

        # 依照field.position渲染日期，field.position將為一個List，前三項分別為年月日的位置
        if isinstance(field.position, list) and len(field.position) == 3:
            for i, part in zip(field.position, date_arr):
                # 渲染日期的每個部分
                if not isinstance(i, tuple) or len(i) != 2:
                    logger.error(f"日期欄位 {field.key} 的 position 格式錯誤，應為三個座標 (年、月、日)，目前為 {i}")
                    return
                
                draw.text(i, part, fill=field.font_color or "#000000", font=font)
        else:
            logger.error(f"日期欄位 {field.key} 的 position 格式錯誤，應為三個座標")
            return

    def save_document(self, document: Image.Image, csv_row: Dict[str, str]) -> str:
        """
        儲存證件檔案
        
        :param document: 證件圖片
        :param csv_row: CSV 資料行
        :return: 儲存的檔案路徑
        """
        # 建立輸出目錄
        output_path = self.output_dir / self.config.output.save_to.format(**csv_row)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 建立檔案名稱
        filename = self.config.output.output_file_format.format(**csv_row)
        filename = self._sanitize_filename(filename)
        
        # 檢查檔案副檔名
        if not any(filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']):
            # 如果沒有副檔名，預設使用 .png
            filename += '.png'
            logger.warning(f"檔案名稱沒有副檔名，自動添加 .png: {filename}")
        
        file_path = output_path / filename
        
        try:
            # 根據副檔名決定儲存格式
            if filename.lower().endswith('.png'):
                document.save(file_path, 'PNG', dpi=(self.config.output.dpi, self.config.output.dpi))
            elif filename.lower().endswith(('.jpg', '.jpeg')):
                # JPEG 不支援透明度，需要轉換為 RGB
                rgb_document = Image.new('RGB', document.size, (255, 255, 255))
                rgb_document.paste(document, mask=document.split()[-1] if document.mode == 'RGBA' else None)
                rgb_document.save(file_path, 'JPEG', dpi=(self.config.output.dpi, self.config.output.dpi), quality=95)
            else:
                # 其他格式使用預設方式
                document.save(file_path, dpi=(self.config.output.dpi, self.config.output.dpi))
            
            logger.info(f"證件已儲存: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"儲存檔案失敗 {file_path}: {e}")
            # 嘗試用 PNG 格式儲存
            fallback_path = file_path.with_suffix('.png')
            document.save(fallback_path, 'PNG', dpi=(self.config.output.dpi, self.config.output.dpi))
            logger.info(f"使用 PNG 格式儲存: {fallback_path}")
            return str(fallback_path)
    
    def process_batch(self, csv_data: List[Dict[str, str]]) -> List[Tuple[str, bool, str]]:
        """
        批次處理多個人員資料
        
        :param csv_data: CSV 資料列表
        :return: 處理結果列表 [(id_number, success, error_message), ...]
        """
        results = []
        
        for row in csv_data:
            try:
                # 生成證件
                document = self.generate_document(row)
                
                # 儲存證件
                file_path = self.save_document(document, row)
                
                results.append((row.get('id_number', 'unknown'), True, ""))
                
            except Exception as e:
                error_msg = f"處理失敗: {str(e)}"
                logger.error(f"處理 {row.get('id_number', 'unknown')} 時發生錯誤: {error_msg}")
                logger.debug(f"錯誤詳細資訊: {e}", exc_info=True)
                results.append((row.get('id_number', 'unknown'), False, error_msg))
        
        return results

def load_csv_data(csv_path: str) -> List[Dict[str, str]]:
    """
    載入 CSV 資料
    
    :param csv_path: CSV 檔案路徑
    :return: CSV 資料列表
    """
    data = []
    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append(dict(row))
    return data