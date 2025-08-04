import os
from libs.id_card_process import add_mrz_to_template, load_template, add_text_to_template_tps, add_code_to_template, add_photo_to_template
from PIL import Image, ImageDraw, ImageFont
from barcode import Code128
from barcode.writer import ImageWriter
import time
import io
from libs.constraits import *
import logging
from libs.mrzgenerater import MRZGenerator
import time

# 獲取logger
logger = logging.getLogger(__name__)

PASSPORT_NUMBER_POSITION = (102.794, 205.324)   # 護照號碼位置
NAME_POSITION = (102.479, 292.787)   # 姓名位置
NAME_EN_POSITION = (102.479, 395.547)   # 外文姓名位置
ID_POSITION = (101.751, 541.424)   # 身分證號碼位置
BIRTH_PLACE_POSITION = (365.955, 618.463)   # 出生地

BIRTH_DATE_POSITION = [(366.459, 541.424), (461.433, 541.424), (521.628, 541.424)]
DATE_OF_ISSUE_POSITION = [(629.872, 541.424), (724.846, 541.424), (784.537, 541.424)]
DATE_OF_EXPIRY_POSITION = [(103.046, 615.989), (198.020, 615.989), (257.711, 615.989)]

BARCODE_POSITION = (110.035, 804.865)
BARCODE_SIZE = (281.738, 66.137)

MRZ_LINE_1_POSITION = (105.268, 1276.998)
MRZ_LINE_2_POSITION = (105.268, 1300.012)

PHOTO_POSITION = (627.667, 100.016)
PHOTO_SIZE = (273.174, 367.081)

# 測試
def generate_passport_content(
    passport_number: str,
    name: str,
    name_en: str,
    id_number: str,
    birth_place: str,
    birth_date: tuple,
    date_of_issue: tuple,
    date_of_expiry: tuple,
    mrz: str,
    photo: Image.Image,
    template_path: str = "./templates/個人資料頁面_模板.png"
) -> tuple:
    """
    生成護照個人資料頁面模板

    :param passport_number: 護照號碼
    :param name: 姓名
    :param name_en: 外文姓名
    :param id_number: 身分證號碼
    :param birth_place: 出生地
    :param birth_date: 出生日期
    :param date_of_issue: 發證日期
    :param date_of_expiry: 到期日期
    :param mrz: 機器可讀區文字內容
    :param photo: 護照照片
    :param template_path: 模板路徑
    :return: 生成的護照個人資料頁面模板
    """

    logger.info(f"開始生成護照內容，證件編號: {id_number}")

    try:
        template = load_template(template_path)
        logger.debug("載入模板成功")

        # 添加護照號碼
        template = add_code_to_template(template, passport_number, PASSPORT_NUMBER_POSITION, 22)
        logger.debug("護照號碼添加成功")

        # 添加姓名
        template = add_text_to_template_tps(template, name, NAME_POSITION, 46)
        logger.debug("姓名添加成功")

        # 添加英文姓名
        template = add_code_to_template(template, name_en.upper(), NAME_EN_POSITION, 24)
        logger.debug("英文姓名添加成功")

        # 添加身分證號碼
        template = add_code_to_template(template, id_number.upper(), ID_POSITION, 22)
        logger.debug("身分證號碼添加成功")

        # 添加出生日期
        for i, pos in enumerate(BIRTH_DATE_POSITION):
            template = add_code_to_template(template, str(birth_date[i]), pos, 22)
        logger.debug("出生日期添加成功")

        # 添加發證日期
        for i, pos in enumerate(DATE_OF_ISSUE_POSITION):
            template = add_code_to_template(template, str(date_of_issue[i]), pos, 22)
        logger.debug("發證日期添加成功")

        # 添加到期日期
        for i, pos in enumerate(DATE_OF_EXPIRY_POSITION):
            template = add_code_to_template(template, str(date_of_expiry[i]), pos, 22)
        logger.debug("到期日期添加成功")

        # 添加條碼
        barcode = generate_barcode(id_number)
        template = add_barcode_to_template(template, barcode, BARCODE_POSITION)
        logger.debug("條碼添加成功")

        # 添加出生地
        template = add_text_to_template_tps(template, birth_place, BIRTH_PLACE_POSITION, 24)
        logger.debug("出生地添加成功")

        # 添加機器可讀區文字
        mrz_lines = mrz.split('\n')
        for i, line in enumerate(mrz_lines):
            template = add_mrz_to_template(
                template,
                line,
                MRZ_LINE_1_POSITION if i == 0 else MRZ_LINE_2_POSITION,
                18
            )
        logger.debug("機器可讀區文字添加成功")

        # 添加護照照片
        if photo:
            template = add_photo_to_template(template, photo, PHOTO_POSITION, 10, target_size=PHOTO_SIZE)
            logger.debug("護照照片添加成功")
        else:
            logger.warning("未提供護照照片，跳過添加照片步驟")

        logger.info("護照內容生成成功")

        logger.info("護照資訊內容生成完成")
        return template
        
    except Exception as e:
        logger.error(f"生成護照資訊內容失敗: {str(e)}")
        raise

def generate_barcode(issue_number: str) -> Image.Image:
    """
    生成護照條碼

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
    name: str,
    name_en: str,
    id_number: str,
    birth_place: str,
    birth_date: tuple,
    date_of_issue: tuple,
    date_of_expiry: tuple,
    photo: Image.Image,
    gender: str = "女",
    template_path: str = "./templates/個人資料頁面_模板.png"
) -> tuple:
    """
    生成護照反面模板並添加條碼

    :param name: 姓名
    :param name_en: 外文姓名
    :param id_number: 身分證號碼
    :param birth_place: 出生地
    :param birth_date: 出生日期 (年, 月, 日)
    :param date_of_issue: 發證日期 (年, 月, 日)
    :param date_of_expiry: 到期日期 (年, 月, 日)
    :param photo: 護照照片
    :param gender: 性別
    :param template_path: 模板路徑
    :return: 生成的護照模板
    """
    logger.info(f"開始生成護照，證件編號: {id_number}")
    
    # 輸出調試信息
    logger.debug(f"birth_date: {birth_date}, type: {type(birth_date)}")
    logger.debug(f"date_of_issue: {date_of_issue}, type: {type(date_of_issue)}")
    logger.debug(f"date_of_expiry: {date_of_expiry}, type: {type(date_of_expiry)}")
    
    try:
        # 確保日期是數字格式
        birth_year = int(birth_date[0])
        birth_month = int(birth_date[1])
        birth_day = int(birth_date[2])
        
        expiry_year = int(date_of_expiry[0])
        expiry_month = int(date_of_expiry[1])
        expiry_day = int(date_of_expiry[2])
        
        dob = f"{birth_year % 100:02d}{birth_month:02d}{birth_day:02d}"  # YYMMDD
        expiry = f"{expiry_year % 100:02d}{expiry_month:02d}{expiry_day:02d}"  # YYMMDD
        
        logger.debug(f"格式化後的日期 - dob: {dob}, expiry: {expiry}")
        
    except (ValueError, TypeError, IndexError) as e:
        logger.error(f"日期格式錯誤: {str(e)}")
        logger.error(f"birth_date: {birth_date}")
        logger.error(f"date_of_expiry: {date_of_expiry}")
        raise ValueError(f"日期格式不正確，請確保日期格式為 (年, 月, 日) 的數字元組")

    # 構建 MRZ
    generator = MRZGenerator()
    mrz = generator.build_mrz_line1(
        country_code="NRE",
        last_name=name,
        first_name=name_en
    ) + "\n" + generator.build_mrz_line2(
        passport_number=f"{id_number[0]}{id_number[2:]}",  # 身份證字號去除第二位，讓他變成九位數
        nationality="NRE",  # 假設國籍為 NRE
        dob=dob,  # 假設出生日期為 990616
        gender=gender,  # 假設性別為 F
        expiry_date=expiry,  # 假設到期日期為 230101
        personal_identifier=""  # 保留
    )

    try:
        template = generate_passport_content(
            passport_number=f"N-{id_number[0]}-{id_number[1:]}F",  # 護照號碼格視為 N-<身分證首字母>-<身分證號碼>F
            name=name,
            name_en=name_en,
            id_number=id_number,
            birth_place=birth_place,
            birth_date=(birth_year, birth_month, birth_day),
            date_of_issue=date_of_issue,
            date_of_expiry=(expiry_year, expiry_month, expiry_day),
            mrz=mrz,
            template_path=template_path,
            photo=photo
        )
        logger.info("完整的護照反面生成成功")
        return template
    except Exception as e:
        logger.error(f"生成完整的護照反面失敗: {str(e)}")
        raise

def main():
    logger.info("開始執行護照反面生成程序")

    try:
        # 確保輸出資料夾存在
        output_dir = "./output"
        os.makedirs(output_dir, exist_ok=True)
        logger.debug(f"確保輸出目錄存在: {output_dir}")

        # 儲存結果
        template = generate(
            name="林晴恩",
            name_en="Ching,An Lin",
            id_number="A100000003",
            birth_place=f"{DOMICILE_CONTENT[0].split('\n')[0]} / {DOMICILE_CONTENT[0].split('\n')[1]}",  # 西康堡市
            birth_date=(2010, 6, 16),
            date_of_issue=time.localtime()[:3],
            date_of_expiry=(time.localtime()[0] + 10, time.localtime()[1], time.localtime()[2]),
            photo=Image.open("./photos/v2-cb85aae46a50b62ed003cf5788d682a5_720w_waifu2x_art_noise3_scale.png"),  # 假設有
        )

        output_path = "./output/passport_infopage.png"
        template.save(output_path)
        logger.info(f"護照已儲存至 {output_path}")
        print(f"護照已儲存至 {output_path}")
        
    except Exception as e:
        logger.error(f"程序執行失敗: {str(e)}")
        raise

if __name__ == "__main__":
    main()