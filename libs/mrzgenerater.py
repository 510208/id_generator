import re

class MRZGenerator:
    """
    用於生成機器可讀取區 (MRZ) 的類別，根據提供的 JavaScript 邏輯進行翻譯。
    這個實現與 ICAO 規範可能存在差異，請注意！
    """

    # --- 組態常數 ---
    CONFIG = {
        "MRZ_LINE_LENGTH": 44,
        "PASSPORT_TYPE": "P",
        "COUNTRY_CODE_LENGTH": 3,
        "PASSPORT_NUMBER_FIELD_LENGTH": 9,
        # 根據圖像範例，此區域(包含<<符號和其自身的校驗碼)佔滿剩餘空間，共15個字元
        "PERSONAL_ID_SECTION_LENGTH": 15,
        "WEIGHTS": [7, 3, 1],
        "FILLER": "<",
    }

    # --- 字元數值對照表 ---
    CHAR_TO_VALUE = {
        "0": 0, "1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9,
        "A": 10, "B": 11, "C": 12, "D": 13, "E": 14, "F": 15, "G": 16, "H": 17, "I": 18, "J": 19,
        "K": 20, "L": 21, "M": 22, "N": 23, "O": 24, "P": 25, "Q": 26, "R": 27, "S": 28, "T": 29,
        "U": 30, "V": 31, "W": 32, "X": 33, "Y": 34, "Z": 35,
        "<": 0,
    }

    def __init__(self):
        pass # 初始化時不需要特別做什麼

    def calculate_check_digit(self, data: str) -> int:
        """
        根據配置中的權重計算資料的校驗碼。
        :param data: 需要計算校驗碼的字串。
        :return: 計算出的校驗碼 (0-9)。
        :raises ValueError: 如果遇到不支援的字元。
        """
        total_sum = 0
        for i, char in enumerate(data):
            value = self.CHAR_TO_VALUE.get(char)
            if value is None:
                raise ValueError(f'不支援的字元 "{char}"，無法計算校驗碼。')
            total_sum += value * self.CONFIG["WEIGHTS"][i % len(self.CONFIG["WEIGHTS"])]
        return total_sum % 10

    def sanitize_and_pad(self, s: str, length: int) -> str:
        """
        清理字串，將非大寫字母、數字或 '<' 的字元替換為填充字元，
        並根據指定長度進行填充或截斷。
        :param s: 輸入字串。
        :param length: 目標長度。如果為 0，則僅清理不填充/截斷。
        :return: 清理並填充後的字串。
        """
        sanitized = re.sub(r'[^A-Z0-9<]', self.CONFIG["FILLER"], s.upper())
        if length == 0:
            return sanitized
        return sanitized.ljust(length, self.CONFIG["FILLER"])[:length]

    def build_mrz_line1(self, country_code: str, last_name: str, first_name: str) -> str:
        """
        根據提供的資訊建立 MRZ 的第一行。
        :param country_code: 國籍代碼。
        :param last_name: 姓氏。
        :param first_name: 名字。
        :return: MRZ 的第一行字串。
        """
        mrz_type = self.CONFIG["PASSPORT_TYPE"]
        country = self.sanitize_and_pad(country_code, self.CONFIG["COUNTRY_CODE_LENGTH"])
        prefix = f"{mrz_type}{self.CONFIG['FILLER']}{country}{self.CONFIG['FILLER']}{self.CONFIG['FILLER']}"

        name_field_content = f"{self.sanitize_and_pad(last_name, 0)}<<{self.sanitize_and_pad(first_name, 0)}"
        name_field = self.sanitize_and_pad(
            name_field_content,
            self.CONFIG["MRZ_LINE_LENGTH"] - len(prefix)
        )

        return prefix + name_field

    def build_mrz_line2(
        self,
        passport_number: str,
        nationality: str,
        dob: str,
        gender: str,
        expiry_date: str,
        personal_identifier: str,
    ) -> str:
        """
        根據提供的資訊建立 MRZ 的第二行。
        :param passport_number: 護照號碼。
        :param nationality: 國籍。
        :param dob: 出生日期 (YYMMDD)。
        :param gender: 性別 (M/F/<)。
        :param expiry_date: 有效期 (YYMMDD)。
        :param personal_identifier: 個人識別碼。
        :return: MRZ 的第二行字串。
        """
        # 1. 護照號碼 + 校驗碼 (10位)
        passport_num_padded = self.sanitize_and_pad(
            passport_number, self.CONFIG["PASSPORT_NUMBER_FIELD_LENGTH"]
        )
        passport_num_cd = self.calculate_check_digit(passport_num_padded)
        part1 = f"{passport_num_padded}{self.CONFIG['FILLER']}{passport_num_cd}" # 這裡跟JS不同，JS那邊多了一個FILLER，Python這邊移除。

        # 2. 國籍 (3位)
        part2 = self.sanitize_and_pad(nationality, self.CONFIG["COUNTRY_CODE_LENGTH"])

        # 3. 出生日期(6位)
        dob_cd = self.calculate_check_digit(dob)
        part3 = f"{dob}"

        # 4. 性別 (1位)
        part4 = self.sanitize_and_pad(gender, 1)

        # 5. 有效期 + 校驗碼 (7位)
        expiry_date_cd = self.calculate_check_digit(expiry_date)
        part5 = f"{expiry_date}{self.CONFIG['FILLER']}{expiry_date_cd}"

        # 6. 個人識別碼部分 (共 15 位)
        # a. 將使用者輸入的個人識別碼，填充或截斷至 14 位，作為計算校驗碼的資料。
        # 你的 JS 程式碼這裡寫的是 `sanitizeAndPad(personalIdentifier, 7)`，
        # 但註解卻是「填充或截斷至 14 位」，這點讓我有點困惑。
        # 根據最終組合總長度為 44，並回推 JS 程式碼的 `buildMrzLine2`
        # 組合方式 `part1}{CONFIG.FILLER}{part2}{CONFIG.FILLER}{part3}{CONFIG.FILLER}{part4}{CONFIG.FILLER}{part5}{CONFIG.FILLER}{CONFIG.FILLER}{personalIdData}{CONFIG.FILLER}{personalIdCD}`
        # 我們來算一下：
        # part1 (護照號碼+校驗碼): 9 + 1 = 10
        # part2 (國籍): 3
        # part3 (出生日期+校驗碼): 6 + 1 = 7
        # part4 (性別): 1
        # part5 (有效期+校驗碼): 6 + 1 = 7
        # 填充字元數量: 1 + 1 + 1 + 1 + 2 + 1 = 7
        # 總計已佔用: 10 + 3 + 7 + 1 + 7 + 7 = 35
        # 剩餘可分配給 personalIdData + personalIdCD 的長度 = 44 - 35 = 9
        # 你的 JS 程式碼 `PERSONAL_ID_SECTION_LENGTH: 15` 但在 `buildMrzLine2` 中，
        # `personalIdData` 是 `sanitizeAndPad(personalIdentifier, 7)`，加上一個校驗碼就是 8 位。
        # 這樣會導致總長度不符。
        # 我會依照你的 JS 程式碼實際運行的邏輯，也就是 `sanitizeAndPad(personalIdentifier, 7)` 來處理 `personalIdData`，
        # 但這會使得最終的 MRZ Line 2 長度是 35 + 7 + 1 = 43 (如果 `personalIdData` 是 7 位，校驗碼 1 位)。
        # 如果要達到 44 位，且 personalIdData 加上校驗碼後是 15 位，那麼 personalIdData 應該是 14 位。
        # 這裡我先按照 JS 程式碼中 `sanitizeAndPad(personalIdentifier, 7)` 這個實際的呼叫來寫，
        # 但建議你檢查一下這個長度是否真的符合你的預期 MRZ 格式，畢竟你說它跟 ICAO 不同嘛！
        personal_id_data = self.sanitize_and_pad(personal_identifier, 7) # 依據 JS 程式碼的呼叫

        # b. 根據這 7 位的資料計算校驗碼。
        personal_id_cd = self.calculate_check_digit(personal_id_data)

        # 7. 組合所有部分。
        # 這裡會依照 JS 程式碼的組合方式，但如果總長度不對，可能需要你重新審視一下。
        mrz_line2 = (
            f"{part1}"  # A12345678<4
            f"{self.CONFIG['FILLER']}"
            f"{part2}"  # NRE
            f"{self.CONFIG['FILLER']}"
            f"{part3}"  # 990616<4
            f"{self.CONFIG['FILLER']}"
            f"{part4}"  # F
            f"{self.CONFIG['FILLER']}"
            f"{part5}"  # 990616<4
            f"{self.CONFIG['FILLER']}"
            f"{self.CONFIG['FILLER']}" # 這裡多了兩個填充符號
            f"{personal_id_data}"
            f"{self.CONFIG['FILLER']}"
            f"{personal_id_cd}"
        )
        return mrz_line2

# 如何在其他檔案中引入和使用這個類別的範例：
if __name__ == "__main__":
    generator = MRZGenerator()

    # 模擬表單資料
    form_data = {
        "country_code": "NRE",
        "last_name": "LIN",
        "first_name": "CHING AN",
        "passport_number": "A12345678",
        "nationality": "NRE",
        "dob": "990616", # YYMMDD，生日
        "gender": "F", # M/F/<
        "expiry_date": "990616", # YYMMDD，有效期
        "personal_identifier": "990616", # 這裡的長度可能需要依照實際需求調整
    }

    try:
        # 驗證輸入格式 (Python 中需要自己實現，這裡簡單模擬)
        if not re.fullmatch(r'\d{6}', form_data["dob"]):
            raise ValueError("出生日期格式不正確，應為 YYMMDD。")
        if not re.fullmatch(r'\d{6}', form_data["expiry_date"]):
            raise ValueError("有效期格式不正確，應為 YYMMDD。")

        mrz1 = generator.build_mrz_line1(
            country_code=form_data["country_code"],
            last_name=form_data["last_name"],
            first_name=form_data["first_name"]
        )
        mrz2 = generator.build_mrz_line2(
            passport_number=form_data["passport_number"],
            nationality=form_data["nationality"],
            dob=form_data["dob"],
            gender=form_data["gender"],
            expiry_date=form_data["expiry_date"],
            personal_identifier=form_data["personal_identifier"]
        )

        print("--- MRZ 已產生 ---")
        print(f"MRZ Line 1: {mrz1}")
        print(f"MRZ Line 2: {mrz2}")
        print(f"Line 1 長度: {len(mrz1)}")
        print(f"Line 2 長度: {len(mrz2)}") # 注意這裡的長度是否為 44！

    except ValueError as e:
        print(f"錯誤: {e}")
    except Exception as e:
        print(f"發生未知錯誤: {e}")