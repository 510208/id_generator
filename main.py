# 身分證產生器 - 模板驅動版本

import csv
import os
import shutil
from PIL import Image
import click
import datetime
import logging
import pprint
from logger_config import setup_main_logger
from converter import convert_images_to_png
from document_generator import DocumentGenerator, load_csv_data
from pathlib import Path

# 新增 tabulate 套件用於表格輸出
from tabulate import tabulate
from termcolor import colored

# 設定主要日誌系統
logger = setup_main_logger()

# 確保 logs 目錄存在
os.makedirs('./logs', exist_ok=True)

def generate_documents_from_template(template_path: str, csv_data: list, output_dir: str = "./output"):
    """
    使用模板描述檔生成證件
    
    :param template_path: 模板描述檔路徑 (YAML)
    :param csv_data: CSV 資料列表
    :param output_dir: 輸出資料夾路徑
    :return: 成功生成的結果列表 [(id_number, success, error_message), ...]
    """
    try:
        # 建立文件生成器
        generator = DocumentGenerator(template_path)
        
        # 處理批次資料
        results = generator.process_batch(csv_data)
        
        return results
        
    except Exception as e:
        error_msg = f"模板載入失敗: {str(e)}"
        logger.error(error_msg)
        # 回傳所有項目都失敗的結果
        return [(row.get('id_number', 'unknown'), False, error_msg) for row in csv_data]

def copy_additional_files(template_path: str, csv_data: list, output_dir: str):
    """
    複製模板中指定的額外檔案
    
    :param template_path: 模板描述檔路徑
    :param csv_data: CSV 資料列表  
    :param output_dir: 輸出資料夾路徑
    """
    try:
        from schema import load_config
        config = load_config(template_path)
        
        if not config.output.other_file:
            return
            
        for row in csv_data:
            id_number = row.get('id_number', '')
            if not id_number:
                continue
                
            person_output_dir = Path(output_dir) / config.output.save_to.format(**row)
            person_output_dir.mkdir(parents=True, exist_ok=True)
            
            for file_pattern in config.output.other_file:
                # 處理檔案模式，例如 "/resources/passport_pages/*.png"
                if file_pattern.startswith('/'):
                    file_pattern = file_pattern[1:]  # 移除開頭的 /
                
                import glob
                matching_files = glob.glob(file_pattern)
                
                for src_file in matching_files:
                    src_path = Path(src_file)
                    if src_path.exists():
                        dst_path = person_output_dir / src_path.name
                        shutil.copy2(src_path, dst_path)
                        logger.info(f"已複製檔案: {src_file} -> {dst_path}")
                        
    except Exception as e:
        logger.error(f"複製額外檔案時發生錯誤: {e}")

def create_archives(csv_data: list, output_dir: str, template_path: str):
    """
    為每個人員建立 ZIP 壓縮檔
    
    :param csv_data: CSV 資料列表
    :param output_dir: 輸出資料夾路徑
    :param template_path: 模板描述檔路徑
    """
    try:
        from schema import load_config
        config = load_config(template_path)
        
        for row in csv_data:
            id_number = row.get('id_number', '')
            if not id_number:
                continue
                
            person_dir = Path(output_dir) / config.output.save_to.format(**row)
            
            if person_dir.exists():
                # 建立壓縮檔
                archive_name = f"{id_number}_documents"
                archive_path = person_dir.parent / archive_name
                
                shutil.make_archive(str(archive_path), 'zip', str(person_dir))
                logger.info(f"已建立壓縮檔: {archive_path}.zip")
                
    except Exception as e:
        logger.error(f"建立壓縮檔時發生錯誤: {e}")

def print_summary_table(results, template_name):
    """
    輸出批次處理結果總結表格
    """
    # 建立表格資料
    table_data = []
    for id_number, success, error_msg in results:
        row = [id_number]
        
        if success:
            row.append(colored("✓ Success", "green"))
        else:
            row.append(colored(f"✗ Failed: {error_msg}", "red"))
        
        table_data.append(row)
    
    # 輸出表格
    headers = ["id_number", f"{template_name} Status"]
    click.echo("\n" + "="*80)
    click.echo(colored(f"{template_name} 批次處理結果總結", "yellow", attrs=["bold"]))
    click.echo("="*80)
    
    if table_data:
        click.echo(tabulate(table_data, headers=headers, tablefmt="grid"))
        
        # 統計資訊
        total_count = len(results)
        success_count = sum(1 for _, success, _ in results if success)
        click.echo(f"\n{template_name}: {colored(f'{success_count}/{total_count}', 'green' if success_count == total_count else 'yellow')} Success")
    else:
        click.echo(colored("No Data was proceed", "yellow"))
    
    click.echo("="*80)

@click.command()
@click.option('--csv-path', '-c', default='./data/data.csv', help='CSV 資料檔案路徑')
@click.option('--template-path', '-t', required=True, help='模板描述檔路徑 (YAML)')
@click.option('--output-dir', '-o', default='./output', help='輸出資料夾路徑')
@click.option('--photos-dir', '-p', default='./photos', help='照片資料夾路徑')
@click.option('--skip-additional', is_flag=True, help='跳過額外檔案複製')
@click.option('--skip-zip', is_flag=True, help='跳過 ZIP 壓縮')
@click.option('--verbose', '-v', is_flag=True, help='詳細輸出模式')
@click.option('--log-level', '-l', default='info', help='日誌等級 (debug, info, warning, error, critical)')
def main(csv_path, template_path, output_dir, photos_dir, skip_additional, skip_zip, verbose, log_level):
    """
    基於模板的證件產生器
    
    從 CSV 檔案讀取資料，依照 YAML 模板描述檔生成證件圖片，並打包成 ZIP 檔案。
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        click.echo("啟用詳細輸出模式")

    if log_level:
        logging.getLogger().setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # 設定日誌等級
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    click.echo(f"日誌等級設定為: {log_level.upper()}")

    # 檢查檔案是否存在
    if not os.path.exists(csv_path):
        click.echo(f"錯誤：CSV 檔案不存在 - {csv_path}", err=True)
        return
        
    if not os.path.exists(template_path):
        click.echo(f"錯誤：模板檔案不存在 - {template_path}", err=True)
        return

    # 確保輸出資料夾存在
    os.makedirs(output_dir, exist_ok=True)

    # 讀取 CSV 資料
    click.echo(f"正在讀取 CSV 資料: {csv_path}")
    csv_data = load_csv_data(csv_path)
    
    if verbose:
        click.echo("CSV 資料內容:")
        pprint.pprint(csv_data)

    # 轉換照片格式
    if os.path.exists(photos_dir):
        click.echo(f"正在轉換照片格式: {photos_dir}")
        convert_images_to_png(photos_dir)
        logger.info("已轉換照片格式為 PNG")
    else:
        click.echo(f"警告：照片資料夾不存在 - {photos_dir}")
    
    # 獲取模板名稱
    template_name = Path(template_path).stem
    
    # 使用模板生成證件
    click.echo(f"正在使用模板 {template_name} 生成證件...")
    results = generate_documents_from_template(template_path, csv_data, output_dir)
    click.echo("證件生成完成")

    # 複製額外檔案
    if not skip_additional:
        click.echo("正在複製額外檔案...")
        copy_additional_files(template_path, csv_data, output_dir)
        click.echo("額外檔案複製完成")

    # 壓縮檔案
    if not skip_zip:
        click.echo("正在建立壓縮檔...")
        create_archives(csv_data, output_dir, template_path)
        click.echo("壓縮檔建立完成")
    
    # 輸出總結表格
    print_summary_table(results, template_name)
    
    click.echo(f"所有任務完成！輸出資料夾: {output_dir}")

if __name__ == "__main__":
    main()
