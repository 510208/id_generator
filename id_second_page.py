import os
from libs.id_card_process import load_template, add_text_to_template_tps, add_code_to_template, add_photo_to_template
from PIL import Image, ImageDraw, ImageFont
from barcode import Code128
from barcode.writer import ImageWriter
import time
import io
from libs.constraits import *
import logging

# 獲取logger
logger = logging.getLogger(__name__)

# 日期Tuple
BIRTH_DATE_POSITION = [(62.701, 90.692), (167.646, 90.692), (234.157, 90.692)]
IDENTITY_POSITION = (324.907, 95.950)
GENDER_POSITION = (631.723, 95.950)
AUTHORITY_POSITION = (62.701, 197.023)
DOMICILE_POSITION = (62.701, 297.953)
ISSUANCE_TYPE_POSITION = (631.029, 197.023)
DATE_OF_ISSUE_POSITION = [(632.555, 290.953), (737.499, 290.953), (803.456, 290.953)]
DATE_OF_EXPIRY_POSITION = [(632.555, 392.140), (737.499, 392.140), (803.456, 392.140)]

ISSUE_NUMBER_POSITION = (770.345, 525.730)
BARCODE_POSITION = (61.765, 500.003)
BARCODE_SIZE = (181.232, 49.839)

# 測試
def generate_id_card_2_content(
    birth_date: tuple,
    identity: str,
    gender: str,
    authority: str,
    domicile: str,
    issue_type: str,
    date_of_issue: tuple,
    date_of_expiry: tuple,
    issue_number: str,
    photo: Image.Image,
    template_path: str = "./templates/反面_模板.png"
) -> tuple:
    """
    生成身分證反面模板內容部分

    :param birth_date: 出生日期
    :param identity: 身分別
    :param gender: 性別
    :param authority: 發證機關
    :param domicile: 戶籍
    :param issue_type: 證件類型
    :param date_of_issue: 發證日期
    :param date_of_expiry: 到期日期
    :param issue_number: 證件編號
    :param photo: 護照照片
    :return: 更新後的圖片範本
    """
    logger.info(f"開始生成身分證反面內容，證件編號: {issue_number}")
    
    try:
        template = load_template(template_path)
        logger.debug("載入模板成功")

        # 添加出生日期
        for i, date in enumerate(birth_date):
            template = add_code_to_template(template, str(date), BIRTH_DATE_POSITION[i], 26)
        logger.debug("添加出生日期成功")

        # 添加身分別
        template = add_text_to_template_tps(template, identity, IDENTITY_POSITION, 26)
        logger.debug("添加身分別成功")

        # 添加性別
        template = add_text_to_template_tps(template, gender, GENDER_POSITION, 26)
        logger.debug("添加性別成功")

        # 添加發證機關
        template = add_text_to_template_tps(template, authority, AUTHORITY_POSITION, 26)
        logger.debug("添加發證機關成功")

        # 添加戶籍
        template = add_text_to_template_tps(template, domicile, DOMICILE_POSITION, 26)
        logger.debug("添加戶籍成功")

        # 添加核發類型
        template = add_text_to_template_tps(template, issue_type, ISSUANCE_TYPE_POSITION, 26)
        logger.debug("添加核發類型成功")

        # 添加發證日期
        for i, date in enumerate(date_of_issue):
            template = add_code_to_template(template, str(date), DATE_OF_ISSUE_POSITION[i], 26)
        logger.debug("添加發證日期成功")

        # 添加到期日期
        for i, date in enumerate(date_of_expiry):
            template = add_code_to_template(template, str(date), DATE_OF_EXPIRY_POSITION[i], 26)
        logger.debug("添加到期日期成功")

        # 添加證件編號
        template = add_code_to_template(template, issue_number, ISSUE_NUMBER_POSITION, 16)
        logger.debug("添加證件編號成功")

        logger.info("身分證反面內容生成完成")
        return template
        
    except Exception as e:
        logger.error(f"生成身分證反面內容失敗: {str(e)}")
        raise

def generate_barcode(issue_number: str) -> Image.Image:
    """
    生成身分證條碼

    :param issue_number: 證件編號
    :return: 條碼圖片
    """
    logger.info(f"開始生成條碼，證件編號: {issue_number}")
    
    try:
        # 確保 temp/barcode 資料夾存在
        temp_dir = "./temp/barcode"
        os.makedirs(temp_dir, exist_ok=True)
        logger.debug(f"確保條碼暫存目錄存在: {temp_dir}")
        
        # 使用 ImageWriter 直接生成 PNG 格式的條碼
        barcode = Code128(issue_number, writer=ImageWriter())
        png_path = os.path.join(temp_dir, f"{issue_number}")
        barcode.save(png_path, options={'module_width': 0.4, 'module_height': 20})
        logger.debug(f"條碼已儲存至: {png_path}.png")
        
        # 讀取 PNG 檔案
        barcode_image = Image.open(png_path + ".png")
        logger.debug(f"條碼圖片載入成功，原始尺寸: {barcode_image.size}")
        
        # 目標大小
        target_width = int(BARCODE_SIZE[0])
        target_height = int(BARCODE_SIZE[1])
        logger.debug(f"目標尺寸: {target_width}x{target_height}")
        
        # 按寬度比例調整大小，確保完整寬度
        original_width, original_height = barcode_image.size
        scale = target_width / original_width
        new_width = target_width
        new_height = int(original_height * scale)
        
        # 調整條碼大小
        barcode_image = barcode_image.resize((new_width, new_height), Image.LANCZOS)
        logger.debug(f"條碼調整大小完成: {new_width}x{new_height}")
        
        # 如果高度超過目標高度，從中間裁剪
        if new_height > target_height:
            top = (new_height - target_height) // 2
            bottom = top + target_height
            barcode_image = barcode_image.crop((0, top, new_width, bottom))
            logger.debug(f"條碼裁剪完成，最終尺寸: {barcode_image.size}")
        
        logger.info("條碼生成完成")
        return barcode_image
        
    except Exception as e:
        logger.error(f"生成條碼失敗: {str(e)}")
        raise

def add_barcode_to_template(template: tuple, barcode: Image.Image, position: tuple) -> tuple:
    """
    將條碼添加到模板中

    :param template: 模板圖片
    :param barcode: 條碼圖片
    :param position: 條碼位置
    :return: 更新後的模板圖片
    """
    logger.debug(f"開始將條碼添加到模板，位置: {position}")
    
    try:
        # 將位置轉換為整數並將條碼貼到模板上
        position = (int(position[0]), int(position[1]))
        template.paste(barcode, position)
        logger.debug("條碼添加到模板成功")
        return template
        
    except Exception as e:
        logger.error(f"添加條碼到模板失敗: {str(e)}")
        raise

def generate(
    birth_date: tuple,
    identity: str,
    gender: str,
    authority: str,
    domicile: str,
    issue_type: str,
    date_of_issue: tuple,
    date_of_expiry: tuple,
    issue_number: str,
    barcode: Image.Image,
    template_path: str = "./templates/反面_模板.png"
) -> tuple:
    """
    生成身分證反面模板並添加條碼

    :param birth_date: 出生日期
    :param identity: 身分別
    :param gender: 性別
    :param authority: 發證機關
    :param domicile: 戶籍
    :param issue_type: 證件類型
    :param date_of_issue: 發證日期
    :param date_of_expiry: 到期日期
    :param issue_number: 證件編號
    :param barcode: 條碼圖片
    :return: 更新後的圖片範本
    """
    logger.info(f"開始生成完整的身分證反面，證件編號: {issue_number}")
    
    try:
        template = generate_id_card_2_content(
            birth_date,
            identity,
            gender,
            authority,
            domicile,
            issue_type,
            date_of_issue,
            date_of_expiry,
            issue_number,
            template_path
        )
        template = add_barcode_to_template(template, barcode, BARCODE_POSITION)
        logger.info("完整的身分證反面生成成功")
        print(template)
        return template
        
    except Exception as e:
        logger.error(f"生成完整的身分證反面失敗: {str(e)}")
        raise

def main():
    logger.info("開始執行身分證反面生成程序")
    
    try:
        # 確保輸出資料夾存在
        output_dir = "./output"
        os.makedirs(output_dir, exist_ok=True)
        logger.debug(f"確保輸出目錄存在: {output_dir}")

        # 儲存結果
        template = generate(
            birth_date=(2000, 6, 16),
            identity=IDENTITY_CONTENT[0],  # 本國國民
            gender=GENDER_CONTENT[1],  # 女
            authority="諾瓦雷克斯帝國內政戶政部",
            domicile=DOMICILE_CONTENT[0],  # 西康堡市
            issue_type=ISSUANCE_TYPE_CONTENT[0],  # 初發
            date_of_issue=time.localtime()[:3],  # 當前日期
            date_of_expiry=(2030, 1, 1),
            issue_number="010020250003-FR",
            barcode=generate_barcode("A100000003"),
            template_path="./templates/反面_模板.png"
        )

        output_path = "./output/id_card_back.png"
        template.save(output_path)
        logger.info(f"身分證已儲存至 {output_path}")
        print(f"身分證已儲存至 {output_path}")
        
    except Exception as e:
        logger.error(f"程序執行失敗: {str(e)}")
        raise

if __name__ == "__main__":
    main()