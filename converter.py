import os
from PIL import Image
import glob

def convert_images_to_png(photos_dir="./photos"):
    """
    將 ./photos 目錄中的所有圖片轉換為 PNG 格式
    支援的格式：webp, jpeg, jpg, bmp, gif 等
    """
    # 確保 photos 目錄存在
    if not os.path.exists(photos_dir):
        print(f"目錄 {photos_dir} 不存在")
        return
    
    # 支援的圖片格式
    supported_formats = ['*.webp', '*.jpeg', '*.jpg', '*.bmp', '*.gif', '*.tiff', '*.tif']
    
    converted_count = 0
    
    for format_pattern in supported_formats:
        # 搜尋指定格式的檔案
        file_pattern = os.path.join(photos_dir, format_pattern)
        files = glob.glob(file_pattern, recursive=False)
        
        # 也搜尋大寫副檔名
        file_pattern_upper = os.path.join(photos_dir, format_pattern.upper())
        files.extend(glob.glob(file_pattern_upper, recursive=False))
        
        for file_path in files:
            try:
                # 取得檔案名稱（不含副檔名）
                file_name = os.path.splitext(os.path.basename(file_path))[0]
                output_path = os.path.join(photos_dir, f"{file_name}.png")
                
                # 如果目標 PNG 檔案已存在，跳過
                if os.path.exists(output_path):
                    print(f"跳過 {file_path} - PNG 檔案已存在")
                    continue
                
                # 開啟並轉換圖片
                with Image.open(file_path) as img:
                    # 如果是 RGBA 模式，直接儲存
                    # 如果是其他模式，轉換為 RGB
                    if img.mode in ('RGBA', 'LA'):
                        img.save(output_path, 'PNG')
                    else:
                        # 轉換為 RGB 模式以確保相容性
                        rgb_img = img.convert('RGB')
                        rgb_img.save(output_path, 'PNG')
                
                print(f"轉換完成: {file_path} -> {output_path}")
                converted_count += 1
                
            except Exception as e:
                print(f"轉換失敗 {file_path}: {str(e)}")
    
    print(f"\n轉換完成！共轉換了 {converted_count} 個檔案")

if __name__ == "__main__":
    convert_images_to_png()
