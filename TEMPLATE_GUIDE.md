# 模板驅動證件生成器使用指南

## 概述

此專案已升級為模板驅動的證件生成系統。您可以使用 YAML 格式的模板描述檔來定義證件的外觀和內容，系統會根據模板和 CSV 資料自動生成證件。

## 系統架構

### 1. 核心組件

- **DocumentGenerator**: 主要的證件生成引擎
- **schema**: Pydantic 資料驗證模組
- **template YAML**: 證件模板描述檔

### 2. 資料流程

```
CSV 資料 + YAML 模板 → DocumentGenerator → 證件圖片 + 壓縮檔
```

## 使用方式

### 基本命令

```bash
# 使用指定的模板生成證件
python main.py -t sample-passport.yml -c data/sample_data.csv

# 詳細輸出模式
python main.py -t sample-passport.yml -c data/sample_data.csv -v

# 自訂輸出目錄
python main.py -t sample-passport.yml -c data/sample_data.csv -o ./custom_output
```

### 命令列參數

- `-t, --template-path`: **必需** 模板描述檔路徑 (YAML)
- `-c, --csv-path`: CSV 資料檔案路徑 (預設: `./data/data.csv`)
- `-o, --output-dir`: 輸出資料夾路徑 (預設: `./output`)
- `-p, --photos-dir`: 照片資料夾路徑 (預設: `./photos`)
- `--skip-additional`: 跳過額外檔案複製
- `--skip-zip`: 跳過 ZIP 壓縮
- `-v, --verbose`: 詳細輸出模式
- `-l, --log-level`: 日誌等級

## 模板格式 (YAML)

### 完整範例

```yaml
# 證件基本資訊
id: "passport"
country: "諾瓦雷克斯帝國"
version: "1.0"

# 背景設定
background:
  image: "passport-bg.png" # templates/ 資料夾中的檔案
  color: "#f4f4f4"

# 欄位定義
fields:
  - key: "name"
    type: "text"
    position: [100, 150]
    font_size: 18
    font_color: "#000000"
    font_family: "Noto Sans TC"
    data_path: "name"

  - key: "barcode"
    type: "barcode"
    position: [500, 300]
    size: [200, 50]
    data_path: "id_number"

# 照片設定
photo:
  folder: "./photos"
  position: [50, 50]
  size: [100, 120]
  border_radius: 10

# 輸出設定
output:
  dpi: 300
  save_to: "{id_number}"
  output_file_format: "passport-{id_number}.png"
  other_file:
    - "resources/passport_pages/*.png"
```

### 欄位類型

- **text**: 一般文字
- **number**: 數字
- **date**: 日期
- **barcode**: 條碼

### 資料路徑 (data_path)

指定從 CSV 資料中取得的欄位名稱，例如：

- `name`: 對應 CSV 中的 name 欄位
- `id_number`: 對應 CSV 中的 id_number 欄位

## CSV 資料格式

### 必需欄位

```csv
name,name_en,id_number,birth_date,identity,gender,domicile,issue_type,nationality
林晴恩,Ching-An Lin,A100000003,1990/1/1,單一國籍子民,女,西康堡市,初發,諾瓦雷克斯帝國
```

### 欄位說明

- `name`: 中文姓名
- `name_en`: 英文姓名
- `id_number`: 身分證號碼
- `birth_date`: 出生日期 (格式: YYYY/MM/DD)
- `identity`: 身分別
- `gender`: 性別
- `domicile`: 戶籍地
- `issue_type`: 發證類型
- `nationality`: 國籍

## 檔案結構

```
專案目錄/
├── main.py                    # 主程式
├── document_generator.py      # 證件生成引擎
├── schema/                    # 資料驗證模組
│   ├── __init__.py
│   ├── schema.py
│   ├── loader.py
│   └── validators.py
├── templates/                 # 模板檔案
│   └── passport-bg.png
├── photos/                    # 照片檔案
│   ├── 林晴恩.png
│   └── 張偉明.png
├── data/                      # CSV 資料
│   └── sample_data.csv
├── resources/                 # 額外資源檔案
│   └── passport_pages/
└── output/                    # 輸出結果
    ├── A100000003/
    │   ├── passport-A100000003.png
    │   └── A100000003_documents.zip
    └── A100000004/
```

## 照片檔案

### 命名規則

系統會按以下順序尋找照片檔案：

1. `{姓名}.png`
2. `{姓名}.jpg`
3. `{姓名}.jpeg`
4. `{身分證號碼}.png`
5. `{身分證號碼}.jpg`
6. `{身分證號碼}.jpeg`

### 格式要求

- 支援 PNG、JPG、JPEG 格式
- 系統會自動調整大小至模板指定尺寸
- 如找不到照片會使用預設佔位圖

## 輸出結果

### 檔案結構

每個人員會在輸出目錄中建立獨立資料夾：

```
output/
└── {身分證號碼}/
    ├── {證件檔案}.png
    ├── {其他檔案}
    └── {身分證號碼}_documents.zip
```

### ZIP 壓縮檔

自動建立包含所有相關檔案的壓縮檔，方便分發。

## 錯誤處理

### 常見錯誤

1. **模板檔案不存在**: 檢查 `-t` 參數路徑
2. **CSV 檔案不存在**: 檢查 `-c` 參數路徑
3. **背景圖片不存在**: 確保 templates/ 資料夾中有對應檔案
4. **照片不存在**: 系統會使用預設佔位圖
5. **字體不存在**: 系統會回到預設字體

### 除錯技巧

- 使用 `-v` 參數啟用詳細輸出
- 檢查日誌檔案了解詳細錯誤訊息
- 使用 `--log-level debug` 取得更多資訊

## 進階功能

### 自訂模板

1. 複製 `sample-passport.yml` 為新檔案
2. 修改背景圖片、欄位位置、字體等設定
3. 使用 `-t` 參數指定新模板

### 批次處理

系統支援批次處理多筆資料，自動為每個人員建立獨立的輸出資料夾和檔案。

### 條碼生成

系統使用 Code128 格式生成條碼，資料來源可指定任何 CSV 欄位。
