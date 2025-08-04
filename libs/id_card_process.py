import os
from PIL import Image, ImageDraw, ImageFont
import logging

# 獲取logger
logger = logging.getLogger(__name__)

# 讀取範本
def load_template(template_path = "./templates/正面_模板.png"):
    """讀取圖片範本"""
    logger.info(f"開始載入模板: {template_path}")
    
    try:
        template = Image.open(template_path)
        logger.debug(f"模板載入成功，尺寸: {template.size}")
        return template
    except Exception as e:
        logger.error(f"載入模板失敗: {str(e)}")
        raise

def add_text_to_template(template: tuple, text: str, position: tuple, font_size: int) -> tuple:
    """
    在範本上添加文字

    :param template: 圖片範本
    :param text: 要添加的文字
    :param position: 文字位置 (x, y)
    :param font_size: 字體大小
    :return: 更新後的圖片範本
    """
    logger.debug(f"開始添加文字: '{text}' 到位置 {position}，字體大小: {font_size}")
    
    try:
        draw = ImageDraw.Draw(template)
        font = ImageFont.truetype("./fonts/NotoSansTC-Bold.ttf", font_size)
        draw.text(position, text, font=font, fill="black")
        logger.debug("文字添加成功")
        return template
    except Exception as e:
        logger.error(f"添加文字失敗: {str(e)}")
        raise

def add_text_to_template_tps(template: tuple, text: str, position: tuple, font_size: int) -> tuple:
    """
    在範本上添加文字，但使用台北黑體

    :param template: 圖片範本
    :param text: 要添加的文字
    :param position: 文字位置 (x, y)
    :param font_size: 字體大小
    :return: 更新後的圖片範本
    """
    logger.debug(f"開始添加文字(台北黑體): '{text}' 到位置 {position}，字體大小: {font_size}")
    
    try:
        draw = ImageDraw.Draw(template)
        font = ImageFont.truetype("./fonts/TaipeiSansTCBeta-Regular.ttf", font_size)
        draw.text(position, text, font=font, fill="black")
        logger.debug("文字添加成功")
        return template
    except Exception as e:
        logger.error(f"添加文字失敗: {str(e)}")
        raise

def add_code_to_template(template: tuple, code: str, position: tuple, font_size: int) -> tuple:
    """
    在範本上添加數位內容

    :param template: 圖片範本
    :param code: 要添加的數位內容
    :param position: 文字位置 (x, y)
    :param font_size: 字體大小
    :return: 更新後的圖片範本
    """
    logger.debug(f"開始添加代碼: '{code}' 到位置 {position}，字體大小: {font_size}")
    
    try:
        draw = ImageDraw.Draw(template)
        font = ImageFont.truetype("./fonts/CartographMonoCF-Regular.ttf", font_size)
        draw.text(position, code, font=font, fill="black")
        logger.debug("代碼添加成功")
        return template
    except Exception as e:
        logger.error(f"添加代碼失敗: {str(e)}")
        raise

def add_mrz_to_template(template: tuple, mrz: str, position: tuple, font_size: int) -> tuple:
    """
    在範本上添加機器可讀區文字

    :param template: 圖片範本
    :param mrz: 機器可讀區文字內容
    :param position: 文字位置 (x, y)
    :param font_size: 字體大小
    :return: 更新後的圖片範本
    """
    logger.debug(f"開始添加MRZ: '{mrz}' 到位置 {position}，字體大小: {font_size}")
    
    try:
        draw = ImageDraw.Draw(template)
        font = ImageFont.truetype("./fonts/OCR-B.ttf", font_size)
        draw.text(position, mrz, font=font, fill="black")
        logger.debug("MRZ添加成功")
        return template
    except Exception as e:
        logger.error(f"添加MRZ失敗: {str(e)}")
        raise

def add_photo_to_template(template: tuple, photo: Image.Image, position: tuple, corner_radius: int = 10, target_size: tuple = None) -> tuple:
    """
    在範本上添加身分證照片（帶圓角）
    
    :param template: 圖片範本
    :param photo: 身分證照片
    :param position: 照片位置 (x, y)
    :param corner_radius: 圓角半徑
    :param target_size: 目標大小 (width, height)，如果為 None 則使用預設的 168x226
    :return: 更新後的圖片範本
    """
    logger.debug(f"開始添加照片到位置 {position}，圓角半徑: {corner_radius}")
    
    try:
        # 目標大小
        if target_size is None:
            target_width, target_height = 168, 226
        else:
            target_width, target_height = int(target_size[0]), int(target_size[1])
        logger.debug(f"照片目標尺寸: {target_width}x{target_height}")
        
        # 計算裁切比例，選擇較大的比例以填滿目標區域
        original_width, original_height = photo.size
        logger.debug(f"原始照片尺寸: {original_width}x{original_height}")
        
        scale_w = target_width / original_width
        scale_h = target_height / original_height
        scale = max(scale_w, scale_h)
        logger.debug(f"縮放比例: {scale}")
        
        # 按比例縮放照片
        new_width = int(original_width * scale)
        new_height = int(original_height * scale)
        photo = photo.resize((new_width, new_height), Image.LANCZOS)
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
        mask_draw.rounded_rectangle([0, 0, target_width, target_height], corner_radius, fill=255)
        logger.debug("圓角遮罩創建完成")
        
        # 創建帶圓角的照片
        rounded_photo = Image.new('RGBA', (target_width, target_height), (255, 255, 255, 0))
        rounded_photo.paste(photo, (0, 0))
        rounded_photo.putalpha(mask)
        logger.debug("圓角照片創建完成")
        
        # 將位置轉換為整數並將圓角照片貼到模板上
        int_position = (int(position[0]), int(position[1]))
        template.paste(rounded_photo, int_position, rounded_photo)
        logger.debug("照片添加到模板成功")
        return template
        
    except Exception as e:
        logger.error(f"添加照片失敗: {str(e)}")
        raise