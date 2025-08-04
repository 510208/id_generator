# 身分證產生器

import csv
import os
import shutil
from PIL import Image
import click
import id_first_page as fst_page
from id_second_page import generate_barcode
import id_second_page as snd_page
import passport_infopage as passport
from libs.constraits import DOMICILE_DICT, GENDER_DICT, IDENTITY_DICT, ISSUANCE_TYPE_DICT, ISSUANCE_TYPE_CODE_DICT
import datetime
import logging
import pprint
from logger_config import setup_main_logger
from converter import convert_images_to_png

# 新增 tabulate 套件用於表格輸出
from tabulate import tabulate
from termcolor import colored

# 設定主要日誌系統
logger = setup_main_logger()

# 確保 logs 目錄存在
os.makedirs('./logs', exist_ok=True)

info_dict = {
    "name": "林晴恩",
    "name_en": "Ching,An Lin",
    "id_number": "A100000003",
    "photo_path": "./photos/v2-cb85aae46a50b62ed003cf5788d682a5_720w_waifu2x_art_noise3_scale.png",
    "birth_date": (1990, 1, 1),
    "identity": "公民",
    "gender": "女",
    "authority": "諾瓦雷克斯帝國內政戶政部",
    "domicile": "西康堡市",
    "issue_type": "國民身分證",
    "date_of_issue": (2020, 1, 1),
    "date_of_expiry": (2030, 1, 1),
    "issue_number": "A100000003"
}

def generate_both_id_cards(info: dict):
    """
    生成身分證的正面和反面

    :param info: 包含身分證資訊的字典
    :return: (success: bool, error_message: str)
    """
    try:
        # 確保輸出資料夾存在
        id_dir = f"./output/{info['id_number']}/id"
        os.makedirs(id_dir, exist_ok=True)

        # 生成正面身分證
        front_template = fst_page.generate(
            name=info['name'],
            name_en=info['name_en'],
            id_number=info['id_number'],
            photo_path=info['photo_path']
        )
        
        # 儲存正面身分證
        front_output_path = f"./output/{info['id_number']}/id/id_card_front.png"
        front_template.save(front_output_path)
        logger.info(f"身分證正面已儲存至 {front_output_path}")
        
        # 生成反面身分證
        back_template = snd_page.generate(
            birth_date=info['birth_date'],
            identity=info['identity'],
            gender=info['gender'],
            authority=info['authority'],
            domicile=info['domicile'],
            issue_type=info['issue_type'],
            date_of_issue=info['date_of_issue'],
            date_of_expiry=info['date_of_expiry'],
            issue_number=info['issue_number'],
            barcode=generate_barcode(info['id_number']),
        )

        # 儲存反面身分證
        back_output_path = f"./output/{info['id_number']}/id/id_card_back.png"
        back_template.save(back_output_path)
        logger.info(f"身分證反面已儲存至 {back_output_path}")
        
        return True, ""
    except Exception as e:
        error_msg = f"身分證生成失敗: {str(e)}"
        logger.error(error_msg)
        return False, error_msg

def read_data_from_csv(csv_path: str) -> list:
    with open(csv_path, mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        person_info_list = []

        for row in reader:
            person_info = {
                "name": row["name"],  # 中文姓名
                "name_en": row["name_en"],  # 英文姓名
                "id_number": row["id_number"],  # 身分證號碼
                "photo_path": f"./photos/{row['name']}.png",  # 照片路徑
                "birth_date": tuple(map(int, row["birth_date"].split('/'))),  # 出生日期
                "identity": IDENTITY_DICT[row["identity"]],  # 身分別
                "gender": GENDER_DICT[row["gender"]],  # 性別
                "authority": "諾瓦雷克斯帝國數位政務府",  # 發證機關
                "domicile": DOMICILE_DICT[row["domicile"]],  # 戶籍
                "issue_type": ISSUANCE_TYPE_DICT[row["issue_type"]],  # 證件類型
                "date_of_issue": datetime.datetime.now().strftime("%Y-%m-%d").split('-')[:3],  # 發證日期(當前時間)
                "date_of_expiry": (datetime.datetime.now() + datetime.timedelta(days=3650)).strftime("%Y-%m-%d").split('-')[:3],  # 到期日期(當前時間 + 10年)
                # 證件核發編號格式：<本次流水號（兩位數）>00<當前年份（四位數）><名字首字拼音大寫（取前四位）>-<發證類型兩位代碼（FR初發/CR換發或補發）
                "issue_number": f"{row['id_number'][:2]}00{datetime.datetime.now().year}{row['name_en'][:4].upper()}-{ISSUANCE_TYPE_CODE_DICT[row['issue_type']]}"
            }
            person_info_list.append(person_info)
        return person_info_list

def generate_id_card_from_csv(data_list: list, output_dir: str = "./output"):
    """
    從CSV資料生成身分證

    :param data_list: 包含多個身分證資訊的列表
    :param output_dir: 輸出資料夾路徑
    :return: 成功生成的結果列表 [(id_number, success, error_message), ...]
    """
    os.makedirs(output_dir, exist_ok=True)
    results = []
    
    for info in data_list:
        id_number = info['id_number']
        id_dir = os.path.join(output_dir, id_number)
        os.makedirs(id_dir, exist_ok=True)
        
        success, error_msg = generate_both_id_cards(info)
        results.append((id_number, success, error_msg))
        
        if success:
            logger.info(f"已生成身分證: {id_number}")
        else:
            logger.error(f"身分證生成失敗: {id_number} - {error_msg}")
    
    return results

def generate_passport_from_csv(data_list: list, output_dir: str = "./output"):
    """
    從CSV資料生成護照，儲存到指定的輸出資料夾/<身分證字號>/passport/<圖片檔名>

    :param data_list: 包含多個護照資訊的列表
    :param output_dir: 輸出資料夾路徑
    :return: 成功生成的結果列表 [(id_number, success, error_message), ...]
    """
    os.makedirs(output_dir, exist_ok=True)
    results = []
    
    for info in data_list:
        id_number = info['id_number']
        try:
            passport_template = passport.generate(
                name=info['name'],
                name_en=info['name_en'],
                id_number=info['id_number'],
                birth_place=info['domicile'],  # 假設出生地為戶籍地
                birth_date=info['birth_date'],
                date_of_issue=info['date_of_issue'],
                date_of_expiry=info['date_of_expiry'],
                photo=Image.open(info['photo_path']),
                gender=info['gender']
            )

            passport_dir = os.path.join(output_dir, id_number, "passport")
            os.makedirs(passport_dir, exist_ok=True)

            passport_output_path = os.path.join(passport_dir, "個人資料頁面.png")
            passport_template.save(passport_output_path)
            logger.info(f"護照已儲存至 {passport_output_path}")
            
            results.append((id_number, True, ""))
            
        except FileNotFoundError as e:
            error_msg = f"找不到照片檔案 {info['photo_path']}"
            logger.error(f"錯誤：{error_msg} - {e}")
            results.append((id_number, False, error_msg))
        except Exception as e:
            error_msg = f"護照生成失敗: {str(e)}"
            logger.error(f"護照生成錯誤: {id_number} - {error_msg}")
            results.append((id_number, False, error_msg))
    
    return results

def print_summary_table(id_results, passport_results, skip_id, skip_passport):
    """
    輸出批次處理結果總結表格
    """
    # 建立結果字典以便查找
    id_dict = {result[0]: (result[1], result[2]) for result in id_results} if not skip_id else {}
    passport_dict = {result[0]: (result[1], result[2]) for result in passport_results} if not skip_passport else {}
    
    # 取得所有的身分證號碼
    all_ids = set()
    if not skip_id:
        all_ids.update(id_dict.keys())
    if not skip_passport:
        all_ids.update(passport_dict.keys())
    
    # 建立表格資料
    table_data = []
    for id_number in sorted(all_ids):
        row = [id_number]
        
        # 身分證狀態
        if skip_id:
            row.append("已跳過")
        else:
            id_success, id_error = id_dict.get(id_number, (False, "未處理"))
            if id_success:
                row.append(colored("✓ 成功", "green"))
            else:
                row.append(colored(f"✗ 失敗: {id_error}", "red"))
        
        # 護照狀態
        if skip_passport:
            row.append("已跳過")
        else:
            passport_success, passport_error = passport_dict.get(id_number, (False, "未處理"))
            if passport_success:
                row.append(colored("✓ 成功", "green"))
            else:
                row.append(colored(f"✗ 失敗: {passport_error}", "red"))
        
        table_data.append(row)
    
    # 輸出表格
    headers = ["身分證號碼", "身分證", "護照"]
    click.echo("\n" + "="*80)
    click.echo(colored("批次處理結果總結", "yellow", attrs=["bold"]))
    click.echo("="*80)
    
    if table_data:
        click.echo(tabulate(table_data, headers=headers, tablefmt="grid"))
        
        # 統計資訊
        total_count = len(all_ids)
        if not skip_id:
            id_success_count = sum(1 for _, success, _ in id_results if success)
            click.echo(f"\n身分證: {colored(f'{id_success_count}/{total_count}', 'green' if id_success_count == total_count else 'yellow')} 成功")
        
        if not skip_passport:
            passport_success_count = sum(1 for _, success, _ in passport_results if success)
            click.echo(f"護照: {colored(f'{passport_success_count}/{total_count}', 'green' if passport_success_count == total_count else 'yellow')} 成功")
    else:
        click.echo(colored("沒有處理任何資料", "yellow"))
    
    click.echo("="*80)

@click.command()
@click.option('--csv-path', '-c', default='./data/data.csv', help='CSV 資料檔案路徑')
@click.option('--output-dir', '-o', default='./output', help='輸出資料夾路徑')
@click.option('--photos-dir', '-p', default='./photos', help='照片資料夾路徑')
@click.option('--skip-id', is_flag=True, help='跳過身分證生成')
@click.option('--skip-passport', is_flag=True, help='跳過護照生成')
@click.option('--skip-zip', is_flag=True, help='跳過 ZIP 壓縮')
@click.option('--verbose', '-v', is_flag=True, help='詳細輸出模式')
@click.option('--log-level', '-l', default='info', help='日誌等級 (debug, info, warning, error, critical)')
def main(csv_path, output_dir, photos_dir, skip_id, skip_passport, skip_zip, verbose, log_level):
    """
    身分證和護照產生器
    
    從 CSV 檔案讀取資料，生成身分證和護照圖片，並打包成 ZIP 檔案。
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        click.echo("啟用詳細輸出模式")

    if log_level:
        logging.getLogger().setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # 設定日誌等級
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    click.echo(f"日誌等級設定為: {log_level.upper()}")

    # 確保輸出資料夾存在
    os.makedirs(output_dir, exist_ok=True)

    # UTF8 讀入 CSV 資料
    if not os.path.exists(csv_path):
        click.echo(f"錯誤：CSV 檔案不存在 - {csv_path}", err=True)
        return
    
    click.echo(f"正在讀取 CSV 資料: {csv_path}")
    data_list = read_data_from_csv(csv_path)
    
    if verbose:
        click.echo("CSV 資料內容:")
        pprint.pprint(data_list)

    # 轉換照片格式
    if os.path.exists(photos_dir):
        click.echo(f"正在轉換照片格式: {photos_dir}")
        convert_images_to_png(photos_dir)
        logger.info("已轉換照片格式為 PNG")
    else:
        click.echo(f"警告：照片資料夾不存在 - {photos_dir}")
    
    # 初始化結果列表
    id_results = []
    passport_results = []
    
    # 生成身分證
    if not skip_id:
        click.echo("正在生成身分證...")
        id_results = generate_id_card_from_csv(data_list, output_dir)
        click.echo("身分證生成完成")

    # 生成護照
    if not skip_passport:
        click.echo("正在生成護照...")
        passport_results = generate_passport_from_csv(data_list, output_dir)

        # 打包一本完整的護照
        click.echo("正在複製護照頁面...")
        passport_pages_dir = "./resources/passport_pages"
        if os.path.exists(passport_pages_dir):
            for info in data_list:
                id_number = info['id_number']
                passport_dir = os.path.join(output_dir, id_number, "passport")
                os.makedirs(passport_dir, exist_ok=True)

                for filename in os.listdir(passport_pages_dir):
                    if filename.endswith(".png"):
                        src_path = os.path.join(passport_pages_dir, filename)
                        dst_path = os.path.join(passport_dir, filename)
                        shutil.copy(src_path, dst_path)
                        logger.info(f"已複製護照頁面: {filename} 到 {passport_dir}")
                logger.info(f"護照頁面已複製到 {passport_dir}")
        else:
            click.echo(f"警告：護照頁面資料夾不存在 - {passport_pages_dir}")
        
        click.echo("護照生成完成")

    # 壓縮檔案
    if not skip_zip:
        click.echo("正在壓縮檔案...")
        for info in data_list:
            id_number = info['id_number']
            id_dir = os.path.join(output_dir, id_number)
            
            if not skip_id and os.path.exists(os.path.join(id_dir, 'id')):
                # 壓縮身份證
                shutil.make_archive(os.path.join(id_dir, f"id_card_{id_number}"), 'zip', id_dir, 'id')
                logger.info(f"已壓縮身份證: {id_number}")

            if not skip_passport and os.path.exists(os.path.join(id_dir, 'passport')):
                # 壓縮護照
                shutil.make_archive(os.path.join(id_dir, f"passport_{id_number}"), 'zip', os.path.join(id_dir, "passport"))
                logger.info(f"已壓縮護照: {id_number}")
        
        click.echo("檔案壓縮完成")
    
    # 輸出總結表格
    print_summary_table(id_results, passport_results, skip_id, skip_passport)
    
    click.echo(f"所有任務完成！輸出資料夾: {output_dir}")

if __name__ == "__main__":
    main()
