import os
from libs.id_card_process import load_template, add_text_to_template, add_code_to_template, add_photo_to_template
from PIL import Image, ImageDraw, ImageFont
import logging

# 獲取logger
logger = logging.getLogger(__name__)

NAME_POSITION = (62.355, 273.821)
NAME_EN_POSITION = (61.800, 323.034)
ID_POSITION = (60.968, 514.840)
PHOTO_POSITION = (772.822, 188.555)

# 測試
def generate(
    name: str,
    name_en: str,
    id_number: str,
    photo_path: str,
    template_path: str = "./templates/正面_模板.png"
) -> tuple:
    template = load_template(template_path)

    # 添加姓名
    template = add_text_to_template(template, name, NAME_POSITION, 35)

    name_en = name_en.upper()
    template = add_code_to_template(template, name_en, NAME_EN_POSITION, 24)

    # 添加身分證字號
    template = add_code_to_template(template, id_number, ID_POSITION, 18)

    try:
        # 添加身分證照片
        photo = Image.open(photo_path)
        template = add_photo_to_template(template, photo, PHOTO_POSITION)
        logger.info(f"成功添加照片: {photo_path}")
    except Exception as e:
        logger.error(f"添加照片失敗: {e}")
        raise ValueError(f"無法添加照片: {photo_path}")
    return template

def main():
    # 確保輸出資料夾存在
    output_dir = "./output"
    os.makedirs(output_dir, exist_ok=True)
    
    # 儲存結果
    template = generate(
        name="林晴恩",
        name_en="Ching,An Lin",
        id_number="A100000003",
        photo_path="./photos/v2-cb85aae46a50b62ed003cf5788d682a5_720w_waifu2x_art_noise3_scale.png"
    )
    output_path = "./output/id_card.png"
    template.save(output_path)
    logger.info(f"身分證已儲存至 {output_path}")
    print(f"身分證已儲存至 {output_path}")

if __name__ == "__main__":
    main()