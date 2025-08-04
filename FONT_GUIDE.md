# 字體配置指南

## 字體系統更新

現在系統支援從 `/fonts` 資料夾載入 TTF 字體檔案，提供更精確的字體控制。

## 配置格式

### YAML 配置中的字體設定

```yaml
fields:
  - key: name
    type: text
    position: [62.355, 273.821]
    font_size: 35
    font_color: "#000000"
    font_family: NotoSansTC-VariableFont_wght.ttf # 指定 TTF 檔案名
    data_path: name
```

### 支援的字體格式

1. **TTF 檔案** (推薦)

   ```yaml
   font_family: NotoSansTC-VariableFont_wght.ttf
   ```

   - 從 `/fonts` 資料夾載入
   - 確保精確的字體渲染
   - 跨平台一致性

2. **系統字體名稱** (備用)
   ```yaml
   font_family: Arial
   ```
   - 使用系統安裝的字體
   - 可能因系統而異

## 字體檔案放置

將 TTF 字體檔案放在專案的 `/fonts` 資料夾中：

```
fonts/
├── NotoSansTC-VariableFont_wght.ttf     # 中文字體
├── CartographMonoCF-Regular.ttf         # 英文字體
├── OCR-B.ttf                           # 數字字體
└── TaipeiSansTCBeta-Regular.ttf        # 其他字體
```

## 字體驗證

系統會自動驗證：

1. **TTF 檔案存在性**：檢查 `/fonts` 資料夾中是否存在指定的 TTF 檔案
2. **系統字體可用性**：如果不是 TTF 檔案，檢查系統是否安裝該字體
3. **回退機制**：如果指定字體不可用，自動使用預設字體

## 錯誤處理

### 字體檔案不存在

```
ValueError: 字體檔案不存在: fonts/NonExistent.ttf，可用字體: ['NotoSansTC-VariableFont_wght.ttf', 'OCR-B.ttf']
```

### 系統字體不存在

```
ValueError: 系統未安裝字體 'Unknown Font'，請確認拼字或安裝字體
```

## 實際範例

### 身分證正面配置

```yaml
fields:
  - key: name
    type: text
    position: [62.355, 273.821]
    font_size: 35
    font_color: "#000000"
    font_family: NotoSansTC-VariableFont_wght.ttf # 中文名字
    data_path: name

  - key: name_en
    type: text
    position: [61.800, 323.034]
    font_size: 24
    font_color: "#000000"
    font_family: CartographMonoCF-Regular.ttf # 英文名字
    data_path: name_en

  - key: id_number
    type: text
    position: [60.968, 514.840]
    font_size: 18
    font_color: "#000000"
    font_family: OCR-B.ttf # 身分證號碼
    data_path: id_number
```

## 字體載入優先級

1. **指定 TTF 檔案**：如果 `font_family` 以 `.ttf` 結尾，從 `/fonts` 資料夾載入
2. **系統字體**：嘗試載入系統安裝的字體
3. **預設字體**：如果以上都失敗，使用系統預設字體

## 最佳實踐

1. **使用 TTF 檔案**：為了確保跨平台一致性，建議使用 TTF 檔案
2. **字體檔案命名**：使用有意義的檔案名，包含字體類型資訊
3. **備份字體**：準備多個字體檔案以應對不同需求
4. **測試驗證**：在部署前測試所有字體是否正確載入

## 疑難排解

### 問題：字體無法載入

**解決方案**：

1. 檢查 `/fonts` 資料夾是否存在
2. 確認 TTF 檔案名稱拼寫正確
3. 檢查檔案權限

### 問題：中文字體顯示異常

**解決方案**：

1. 確保使用支援中文的字體（如 NotoSansTC）
2. 檢查字體檔案是否完整
3. 嘗試不同的中文字體檔案

### 問題：字體大小不正確

**解決方案**：

1. 調整 `font_size` 參數
2. 確認字體檔案本身的規格
3. 測試不同的字體檔案
