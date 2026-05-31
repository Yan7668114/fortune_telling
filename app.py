import streamlit as st
import json
import random
import time
import hashlib
from datetime import datetime

# ==========================================
# 網頁基本設定與樣式
# ==========================================
st.set_page_config(page_title="易經數位占卜", page_icon="☯️", layout="centered")

# 自訂 CSS 讓字體更優雅、排版更精美，並適應深色模式
st.markdown("""
    <style>
    .hex-line { font-size: 24px; font-weight: bold; letter-spacing: 2px; line-height: 1.2; }
    .gua-title { font-size: 28px; font-weight: bold; color: #b76e22; }
    
    /* 修正後的解卦指引區塊 */
    .strategy-box { 
        background-color: #262730; /* 改用 Streamlit 深色模式的面板底色 */
        padding: 20px; 
        border-radius: 10px; 
        border-left: 5px solid #b76e22; 
        margin-top: 20px; 
        margin-bottom: 20px; 
    }
    .strategy-box h4 {
        color: #b76e22 !important; /* 確保標題維持琥珀金色 */
        margin-top: 0px;
    }
    .strategy-box p {
        color: #FAFAFA !important; /* 強制內文顏色為亮白色，確保對比度 */
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 核心邏輯 (完全沿用你的成功架構)
# ==========================================
class IChingDB:
    def __init__(self, filepath: str = 'iching_db.json'):
        self.filepath = filepath
        self.data = self._load_db()

    def _load_db(self) -> dict:
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            st.error("找不到資料庫檔案 iching_db.json！")
            return {}

    def get_hexagram(self, binary_key: str) -> dict:
        return self.data.get(binary_key, {"name": "未知卦象", "description": "找不到對應的卦辭"})

class YarrowDiviner:
    @staticmethod
    def _single_change(stalks: int) -> int:
        left = random.randint(1, stalks - 2)
        right = stalks - left - 1
        left_rem = left % 4 or 4
        right_rem = right % 4 or 4
        return stalks - (1 + left_rem + right_rem)

    @classmethod
    def _get_yao(cls) -> int:
        stalks = 49
        for _ in range(3):
            stalks = cls._single_change(stalks)
        return stalks // 4

    @classmethod
    def cast(cls, question: str) -> list[int]:
        # 儀式感：注入意念晶種
        timestamp = str(datetime.now().timestamp())
        seed_hash = hashlib.sha256((question + timestamp).encode('utf-8')).hexdigest()
        random.seed(int(seed_hash, 16))
        return [cls._get_yao() for _ in range(6)]

class HexagramCast:
    def __init__(self, numbers: list[int], db: IChingDB):
        self.numbers = numbers
        self.db = db
        self.moving_lines = [i for i, num in enumerate(self.numbers) if num in (6, 9)]
        self.base_key = self._generate_key(is_transformed=False)
        self.trans_key = self._generate_key(is_transformed=True)
        self.base_hex = self.db.get_hexagram(self.base_key)
        self.trans_hex = self.db.get_hexagram(self.trans_key) if self.moving_lines else None

    def _generate_key(self, is_transformed: bool) -> str:
        binary_str = ""
        for num in self.numbers:
            if not is_transformed:
                binary_str += "0" if num in (6, 8) else "1"
            else:
                if num == 6: binary_str += "1"
                elif num == 9: binary_str += "0"
                else: binary_str += "0" if num == 8 else "1"
        return binary_str

    def get_zhuxi_strategy(self) -> str:
        count = len(self.moving_lines)
        if count == 0: return "【無動爻】：以本卦卦辭為主，評估大環境現狀。"
        elif count == 1: return f"【一爻動】：請查閱本卦第 {self.moving_lines[0] + 1} 爻的爻辭作為核心解答。"
        elif count == 2: return f"【二爻動】：看本卦變動的兩爻爻辭，並以上方的第 {self.moving_lines[1] + 1} 爻為主。"
        elif count == 3: return "【三爻動】：本卦與變卦的卦辭都要看，以本卦為主、變卦為輔。"
        elif count == 4:
            static_lines = [i for i, num in enumerate(self.numbers) if num not in (6, 9)]
            return f"【四爻動】：請看『變卦』中沒有變動的兩爻，並以下方的第 {static_lines[0] + 1} 爻為主。"
        elif count == 5:
            static_line = [i for i, num in enumerate(self.numbers) if num not in (6, 9)][0]
            return f"【五爻動】：請看『變卦』中唯一沒有變動的第 {static_line + 1} 爻爻辭。"
        elif count == 6:
            if self.base_key == "111111": return "【六爻全動】：乾卦全變，請查閱『用九：見群龍無首，吉。』"
            elif self.base_key == "000000": return "【六爻全動】：坤卦全變，請查閱『用六：利永貞。』"
            else: return "【六爻全動】：以『變卦』的整體卦辭為解答。"

    def get_key_lines_text(self) -> list:
        """根據朱熹法則，自動提取真正需要閱讀的關鍵爻辭"""
        count = len(self.moving_lines)
        if count == 0: return []
        
        # 安全機制：檢查資料庫是否已經擴充了 lines 陣列
        base_lines = self.base_hex.get("lines", [])
        trans_lines = self.trans_hex.get("lines", []) if self.trans_hex else []
        
        if not base_lines:
            return ["*(提醒：爻辭資料庫尚未擴充，請至 iching_db.json 補齊 `lines` 陣列)*"]

        result = []
        if count == 1:
            result.append(f"【本卦動爻】 {base_lines[self.moving_lines[0]]}")
        elif count == 2:
            result.append(f"【次要參考】 {base_lines[self.moving_lines[0]]}")
            result.append(f"【主要核心】 {base_lines[self.moving_lines[1]]}")
        elif count == 3:
            for idx in self.moving_lines:
                result.append(f"【本卦動爻】 {base_lines[idx]}")
        elif count == 4:
            static_lines = [i for i, num in enumerate(self.numbers) if num not in (6, 9)]
            if trans_lines:
                result.append(f"【次要參考】變卦之 {trans_lines[static_lines[1]]}")
                result.append(f"【主要核心】變卦之 {trans_lines[static_lines[0]]}")
        elif count == 5:
            static_line = [i for i, num in enumerate(self.numbers) if num not in (6, 9)][0]
            if trans_lines:
                result.append(f"【主要核心】變卦之 {trans_lines[static_line]}")
        elif count == 6:
            if self.base_key == "111111":
                result.append("【用九】見群龍無首，吉。")
            elif self.base_key == "000000":
                result.append("【用六】利永貞。")
            else:
                result.append("【六爻全變】請直接參考下方「變卦」的整體卦辭。")
        return result
# ==========================================
# 視覺化輔助函式
# ==========================================
def draw_hexagram_lines(numbers: list[int], is_transformed: bool = False):
    """繪製爻象圖 (由上而下印出，所以陣列要反轉)"""
    visuals = []
    # 易經排卦是由下往上(0->5)，但視覺顯示是由上往下，所以使用 reversed
    for i, num in enumerate(reversed(numbers)):
        actual_index = 6 - i # 第幾爻
        if not is_transformed:
            if num == 9: line = "███████ (老陽 ◯)"
            elif num == 8: line = "███　███ (少陰)"
            elif num == 7: line = "███████ (少陽)"
            elif num == 6: line = "███　███ (老陰 ✕)"
        else:
            # 變卦視覺
            if num in (9, 7): line = "███　███ (陰)" if num == 9 else "███████ (陽)"
            else: line = "███████ (陽)" if num == 6 else "███　███ (陰)"
        
        visuals.append(f"<div class='hex-line'>{line}</div>")
    return "".join(visuals)

# ==========================================
# UI 介面構建
# ==========================================
st.title("✧ 大衍筮法占卜 ✧")
st.markdown("閉上眼睛，在心中默想您的問題。心誠則靈，無徵不信。")

# 1. 意念輸入區
question = st.text_input("請簡單描述您的問題：", placeholder="在這裡輸入")

# 2. 起卦按鈕與儀式動畫
if st.button("☯️ 與天地共振，開始起卦", use_container_width=True):
    if not question.strip():
        st.warning("請先輸入您想詢問的問題，為占卜注入意念。")
    else:
        # 儀式感：進度條與文字動畫
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("正在注入意念晶種...")
        time.sleep(0.5)
        
        for i in range(1, 4):
            progress_bar.progress(i * 33)
            status_text.text(f"大衍之數，第 {i} 變分撥蓍草...")
            time.sleep(0.6)
            
        status_text.empty()
        progress_bar.empty()
        st.success("成卦！")
        
        # 3. 執行底層運算
        db = IChingDB()
        cast_numbers = YarrowDiviner.cast(question)
        hex_cast = HexagramCast(numbers=cast_numbers, db=db)
        
        # 4. 顯示解卦策略 (強調顯示區塊)
        st.markdown(f"""
        <div class="strategy-box">
            <h4>💡 朱熹解卦指引</h4>
            <p style="font-size: 18px;">{hex_cast.get_zhuxi_strategy()}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # ==========================================
        # 新增：動態抽出關鍵爻辭顯示在畫面上
        # ==========================================
        key_lines = hex_cast.get_key_lines_text()
        if key_lines:
            st.markdown("### 📜 關鍵爻辭解析")
            for line_text in key_lines:
                # 使用 Streamlit 內建的 info 區塊來凸顯爻辭
                st.info(line_text) 
        
        st.divider()
        
        # 5. 雙欄排版顯示卦象
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"<div class='gua-title'>【本卦】{hex_cast.base_hex['name']}</div>", unsafe_allow_html=True)
            st.markdown(f"**卦辭：** {hex_cast.base_hex['description']}")
            st.markdown("<br>", unsafe_allow_html=True)
            # 渲染視覺化爻象 (反轉為上至下)
            st.markdown(draw_hexagram_lines(hex_cast.numbers, is_transformed=False), unsafe_allow_html=True)
            
        with col2:
            if hex_cast.trans_hex:
                st.markdown(f"<div class='gua-title'>【變卦】{hex_cast.trans_hex['name']}</div>", unsafe_allow_html=True)
                st.markdown(f"**卦辭：** {hex_cast.trans_hex['description']}")
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(draw_hexagram_lines(hex_cast.numbers, is_transformed=True), unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='gua-title'>無變卦</div>", unsafe_allow_html=True)
                st.markdown("**說明：** 本次占卜無動爻，請專注於本卦之啟示。")

        # ==========================================
        # 6. AI 解卦 Prompt 生成器
        # ==========================================
        st.divider()
        st.markdown("### 🤖 讓 AI 成為您的解卦師")
        st.markdown("點擊下方代碼塊右上角的 **「複製」圖示**，將這段專屬 Prompt 貼給您慣用的 AI 模型，獲取深度解析。")
        
        # 整理變卦資訊 (如果有變卦才顯示)
        trans_info = f"變卦：{hex_cast.trans_hex['name']} ({hex_cast.trans_hex['description']})" if hex_cast.trans_hex else "變卦：無 (代表局勢平穩，專注本卦即可)"
        moving_info = f"{[f'第 {i+1} 爻' for i in hex_cast.moving_lines]}" if hex_cast.moving_lines else "無動爻"
        
        # 組合給 LLM 的超強 Prompt
        llm_prompt = f"""你現在是一位精通《易經》的解卦大師，能將深奧的古文結合現代人的情境進行白話解析。
請根據以下我擲出的占卜結果與朱熹的解卦法則，為我的問題提供深入、客觀且具建設性的分析。

【我的問題】
{question}

【占卜結果】
- 本卦：{hex_cast.base_hex['name']} ({hex_cast.base_hex['description']})
- {trans_info}
- 動爻位置：{moving_info}

【解卦指引（朱熹法則）】
{hex_cast.get_zhuxi_strategy()}

【請依照以下架構回覆我】
1. 卦象總覽：這支卦反映了我目前問題的大環境與隱藏狀態是什麼？
2. 核心建議：請嚴格遵循上述提供的「解卦指引（朱熹法則）」，告訴我下一步該怎麼做。
3. 決策金句：用一句話總結我該抱持的心態或具體行動。
"""

        # 使用 st.code 自動產生帶有複製按鈕的區塊
        st.code(llm_prompt, language="markdown")

        