"""
集中式日誌配置模組
提供彩色日誌輸出和統一的日誌管理
"""

import logging
import colorlog
import os
from datetime import datetime

def setup_logger(name: str = None) -> logging.Logger:
    """
    設定彩色日誌輸出
    
    :param name: logger名稱，如果為None則使用根logger
    :return: 配置好的logger
    """
    logger = logging.getLogger(name)
    
    # 避免重複設定
    if logger.handlers:
        return logger
    
    # 設定日誌等級
    logger.setLevel(logging.DEBUG)
    
    # 創建彩色格式化器
    color_formatter = colorlog.ColoredFormatter(
        "%(blue)s%(asctime)s%(reset)s - %(yellow)s%(name)s%(reset)s - %(log_color)s%(levelname)s%(reset)s - %(message_log_color)s%(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'white,bg_green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        },
        secondary_log_colors={
            'message': {
                'DEBUG': 'white',
                'INFO': 'white',
                'WARNING': 'white',
                'ERROR': 'white',
                'CRITICAL': 'white',
            }
        }
    )
    
    # 創建控制台處理器
    console_handler = colorlog.StreamHandler()
    console_handler.setFormatter(color_formatter)
    logger.addHandler(console_handler)
    
    # 防止日誌向上傳播到根logger
    logger.propagate = False
    
    return logger

def setup_main_logger() -> logging.Logger:
    """
    設定主要的日誌輸出，包含檔案輸出和彩色終端輸出
    
    :return: 配置好的主logger
    """
    # 確保logs目錄存在
    os.makedirs('./logs', exist_ok=True)
    
    # 獲取根logger
    root_logger = logging.getLogger()
    
    # 清除現有的handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 設定日誌等級
    root_logger.setLevel(logging.INFO)
    
    # 創建以當前時間為名的日誌檔案
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"./logs/id_gen_{current_time}.log"
    
    # 創建檔案處理器
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_formatter)
    
    # 創建彩色控制台處理器
    console_handler = colorlog.StreamHandler()
    color_formatter = colorlog.ColoredFormatter(
        "%(blue)s%(asctime)s%(reset)s - %(yellow)s%(name)s%(reset)s - %(log_color)s%(levelname)s%(reset)s - %(message_log_color)s%(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        },
        secondary_log_colors={
            'message': {
                'DEBUG': 'white',
                'INFO': 'white',
                'WARNING': 'white',
                'ERROR': 'white',
                'CRITICAL': 'white',
            }
        }
    )
    console_handler.setFormatter(color_formatter)
    
    # 添加處理器到根logger
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # 記錄日誌檔案路徑
    root_logger.info(f"日誌檔案已創建: {log_filename}")
    
    return root_logger
