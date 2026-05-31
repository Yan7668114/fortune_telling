import streamlit as st
import json
import random
import time
import hashlib
from datetime import datetime

# ==========================================
# 網頁基本設定與樣式
# ==========================================
st.set_page_config(page_title="易經數位占卜 | I-Ching Oracle", page_icon="☯️", layout="centered")

st.markdown("""
    <style>
    .hex-line { font-size: 24px; font-weight: bold; letter-spacing: 2px; line-height: 1.2; }
    .gua-title { font-size: 28px; font-weight: bold; color: #b76e22; }
    .strategy-box { 
        background-color: #262730; 
        padding: 20px; 
        border-radius: 10px; 
        border-left: 5px solid #b76e22; 
        margin-top: 20px; 
        margin-bottom: 20px; 
    }
    .strategy-box h4 { color: #b76e22 !important; margin-top: 0px; }
    .strategy-box p { color: #FAFAFA !important; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 核心邏輯
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
            st.error("找不到資料庫檔案 iching_db.json / Database not found!")
            return {}

    def get_hexagram(self, binary_key: str) -> dict:
        # 為了相容雙語，預設值也改為雙語格式
        default_hex = {
            "name_cn": "未知卦象", "name_en": "Unknown Hexagram",
            "description_cn": "找不到對應的卦辭", "description_en": "Description not found"
        }
        return self.data.get(binary_key, default_hex)

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

    def get_zhuxi_strategy(self, lang="繁體中文") -> str:
        count = len(self.moving_lines)
        is_cn = (lang == "繁體中文")
        
        if count == 0: 
            return "【無動爻】：以本卦卦辭為主，評估大環境現狀。" if is_cn else "[No Moving Lines]: Focus on the base hexagram's judgment to assess the current situation."
        elif count == 1: 
            return f"【一爻動】：請查閱本卦第 {self.moving_lines[0] + 1} 爻的爻辭作為核心解答。" if is_cn else f"[1 Moving Line]: Read line {self.moving_lines[0] + 1} of the base hexagram as the core answer."
        elif count == 2: 
            return f"【二爻動】：看本卦變動的兩爻爻辭，並以上方的第 {self.moving_lines[1] + 1} 爻為主。" if is_cn else f"[2 Moving Lines]: Read the two moving lines of the base hexagram, focusing primarily on the upper one (line {self.moving_lines[1] + 1})."
        elif count == 3: 
            return "【三爻動】：本卦與變卦的卦辭都要看，以本卦為主、變卦為輔。" if is_cn else "[3 Moving Lines]: Read the judgments of both the base and transformed hexagrams. Base is primary, transformed is secondary."
        elif count == 4:
            static_lines = [i for i, num in enumerate(self.numbers) if num not in (6, 9)]
            return f"【四爻動】：請看『變卦』中沒有變動的兩爻，並以下方的第 {static_lines[0] + 1} 爻為主。" if is_cn else f"[4 Moving Lines]: Read the two static (non-moving) lines in the transformed hexagram, focusing primarily on the lower one (line {static_lines[0] + 1})."
        elif count == 5:
            static_line = [i for i, num in enumerate(self.numbers) if num not in (6, 9)][0]
            return f"【五爻動】：請看『變卦』中唯一沒有變動的第 {static_line + 1} 爻爻辭。" if is_cn else f"[5 Moving Lines]: Read the single static (non-moving) line in the transformed hexagram (line {static_line + 1})."
        elif count == 6:
            if self.base_key == "111111": 
                return "【六爻全動】：乾卦全變，請查閱『用九：見群龍無首，吉。』" if is_cn else "[All 6 Lines Moving]: All lines of Qian change. Refer to 'Use of Nines: To see a flight of dragons without a head. Good fortune.'"
            elif self.base_key == "000000": 
                return "【六爻全動】：坤卦全變，請查閱『用六：利永貞。』" if is_cn else "[All 6 Lines Moving]: All lines of Kun change. Refer to 'Use of Sixes: Lasting perseverance furthers.'"
            else: 
                return "【六爻全動】：以『變卦』的整體卦辭為解答。" if is_cn else "[All 6 Lines Moving]: Use the overall judgment of the transformed hexagram as the answer."

    def get_key_lines_text(self, lang="繁體中文") -> list:
        count = len(self.moving_lines)
        if count == 0: return []
        
        suffix = "_cn" if lang == "繁體中文" else "_en"
        base_lines = self.base_hex.get(f"lines{suffix}", [])
        trans_lines = self.trans_hex.get(f"lines{suffix}", []) if self.trans_hex else []
        
        if not base_lines:
            return ["*(提醒：爻辭資料庫尚未擴充 / Warning: Lines database not expanded yet)*"]

        # 雙語前綴設定
        p_base = "【本卦動爻】" if lang == "繁體中文" else "[Base Moving Line]"
        p_sub = "【次要參考】" if lang == "繁體中文" else "[Secondary Ref]"
        p_main = "【主要核心】" if lang == "繁體中文" else "[Primary Core]"
        p_trans = "變卦之 " if lang == "繁體中文" else "Transformed: "
        
        result = []
        if count == 1:
            result.append(f"{p_base} {base_lines[self.moving_lines[0]]}")
        elif count == 2:
            result.append(f"{p_sub} {base_lines[self.moving_lines[0]]}")
            result.append(f"{p_main} {base_lines[self.moving_lines[1]]}")
        elif count == 3:
            for idx in self.moving_lines:
                result.append(f"{p_base} {base_lines[idx]}")
        elif count == 4:
            static_lines = [i for i, num in enumerate(self.numbers) if num not in (6, 9)]
            if trans_lines:
                result.append(f"{p_sub} {p_trans}{trans_lines[static_lines[1]]}")
                result.append(f"{p_main} {p_trans}{trans_lines[static_lines[0]]}")
        elif count == 5:
            static_line = [i for i, num in enumerate(self.numbers) if num not in (6, 9)][0]
            if trans_lines:
                result.append(f"{p_main} {p_trans}{trans_lines[static_line]}")
        elif count == 6:
            if self.base_key == "111111":
                result.append("【用九】見群龍無首，吉。" if lang == "繁體中文" else "[Use of Nines] To see a flight of dragons without a head. Good fortune.")
            elif self.base_key == "000000":
                result.append("【用六】利永貞。" if lang == "繁體中文" else "[Use of Sixes] Lasting perseverance furthers.")
            else:
                result.append("【六爻全變】請直接參考下方「變卦」的整體卦辭。" if lang == "繁體中文" else "[All 6 Lines Change] Please refer to the Transformed Hexagram below.")
        return result

# ==========================================
# 視覺化輔助函式
# ==========================================
def draw_hexagram_lines(numbers: list[int], is_transformed: bool = False, lang="繁體中文"):
    visuals = []
    
    # 定義雙語標籤
    l_old_yang = "(老陽 ◯)" if lang == "繁體中文" else "(Old Yang ◯)"
    l_young_yin = "(少陰)" if lang == "繁體中文" else "(Young Yin)"
    l_young_yang = "(少陽)" if lang == "繁體中文" else "(Young Yang)"
    l_old_yin = "(老陰 ✕)" if lang == "繁體中文" else "(Old Yin ✕)"
    l_yin = "(陰)" if lang == "繁體中文" else "(Yin)"
    l_yang = "(陽)" if lang == "繁體中文" else "(Yang)"

    for i, num in enumerate(reversed(numbers)):
        if not is_transformed:
            if num == 9: line = f"███████ {l_old_yang}"
            elif num == 8: line = f"███　███ {l_young_yin}"
            elif num == 7: line = f"███████ {l_young_yang}"
            elif num == 6: line = f"███　███ {l_old_yin}"
        else:
            if num in (9, 7): line = f"███　███ {l_yin}" if num == 9 else f"███████ {l_yang}"
            else: line = f"███████ {l_yang}" if num == 6 else f"███　███ {l_yin}"
        
        visuals.append(f"<div class='hex-line'>{line}</div>")
    return "".join(visuals)

# ==========================================
# UI 介面構建 & 雙語字典
# ==========================================

# 1. 先建立頂部排版的兩大容器（4:1 的寬度比例）
col_title, col_lang = st.columns([4, 1])

# 2. 先執行右側欄位，取得使用者的語系選擇 (lang)
with col_lang:
    st.markdown("<br>", unsafe_allow_html=True) 
    lang = st.selectbox(
        "Language", 
        options=["繁體中文", "English"],
        label_visibility="collapsed"
    )

# 3. 取得 lang 變數後，再回到左側欄位渲染對應的動態標題
with col_title:
    if lang == "繁體中文":
        st.title("✧ 大衍筮法占卜 ✧")
    else:
        st.title("✧ I-Ching Oracle ✧")

# UI 字典對照表
ui = {
    "繁體中文": {
        "subtitle": "閉上眼睛，在心中默想您的問題。心誠則靈，無徵不信。",
        "input_label": "請簡單描述您的問題：",
        "input_placeholder": "例如：我該如何推進接下來的專案？",
        "button": "☯️ 與天地共振，開始起卦",
        "warning": "請先輸入您想詢問的問題，為占卜注入意念。",
        "progress_1": "正在注入意念晶種...",
        "progress_2": "大衍之數，第 {} 變分撥蓍草...",
        "success": "成卦！",
        "strategy_title": "💡 朱熹解卦指引",
        "key_lines_title": "### 📜 關鍵爻辭解析",
        "base_hex": "【本卦】",
        "trans_hex": "【變卦】",
        "no_trans": "無變卦",
        "no_trans_desc": "**說明：** 本次占卜無動爻，請專注於本卦之啟示。",
        "ai_title": "### 🤖 讓 AI 成為您的解卦師",
        "ai_desc": "點擊下方代碼塊右上角的 **「複製」圖示**，將這段專屬 Prompt 貼給您慣用的 AI 模型，獲取深度解析。",
        "disclaimer_title": "⚠️ 免責聲明",
        "disclaimer_text": "本數位占卜系統與 AI 提示詞生成的結果僅供參考與娛樂用途，不構成任何醫療、法律、財務或心理諮商之專業建議。使用者應自行評估風險，開發者對基於本系統結果所作出的任何決策概不負責。"
    },
    "English": {
        "subtitle": "Close your eyes and focus on your question. Sincerity brings clarity.",
        "input_label": "Please describe your question briefly:",
        "input_placeholder": "e.g., How should I proceed with my next project?",
        "button": "☯️ Resonate with Heaven and Earth to Cast",
        "warning": "Please enter your question first to infuse your intention.",
        "progress_1": "Infusing intention seed...",
        "progress_2": "Yarrow stalk sorting, variation {}...",
        "success": "Hexagram Cast Successfully!",
        "strategy_title": "💡 Zhu Xi's Divination Guide",
        "key_lines_title": "### 📜 Key Lines Analysis",
        "base_hex": "[Base]",
        "trans_hex": "[Transformed]",
        "no_trans": "No Transformed Hexagram",
        "no_trans_desc": "**Note:** No moving lines in this casting. Please focus on the base hexagram.",
        "ai_title": "### 🤖 Let AI Be Your Divination Master",
        "ai_desc": "Click the **'Copy' icon** at the top right of the code block below and paste this prompt to your preferred AI model for a deep analysis.",
        "disclaimer_title": "⚠️ Disclaimer",
        "disclaimer_text": "The divination results and AI-generated prompts provided by this system are for entertainment and reference purposes only. They do not constitute professional medical, legal, financial, or psychological advice.Users assume full responsibility for any decisions made based on this tool, and the developer assumes no liability."
    }
}

t = ui[lang]
suffix = "_cn" if lang == "繁體中文" else "_en"

st.markdown(t["subtitle"])

# ==========================================
# 使用 st.form 將輸入框與按鈕綁定
# ==========================================
with st.form(key="divination_form", border=False):
    question = st.text_input(t["input_label"], placeholder=t["input_placeholder"])
    # 表單內的按鈕必須使用 st.form_submit_button
    submit_button = st.form_submit_button(t["button"], use_container_width=True)

# 將原本的 if st.button(...) 改為判定表單是否送出
if submit_button:
    if not question.strip():
        st.warning(t["warning"])
    else:
        # ==========================================
        # 以下保留你原本的起卦邏輯，完全不用動
        # ==========================================
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text(t["progress_1"])
        time.sleep(0.5)
        
        for i in range(1, 4):
            progress_bar.progress(i * 33)
            status_text.text(t["progress_2"].format(i))
            time.sleep(0.6)
            
        status_text.empty()
        progress_bar.empty()
        st.success(t["success"])
        
        db = IChingDB()
        cast_numbers = YarrowDiviner.cast(question)
        hex_cast = HexagramCast(numbers=cast_numbers, db=db)
        
        # 顯示解卦策略
        st.markdown(f"""
        <div class="strategy-box">
            <h4>{t['strategy_title']}</h4>
            <p style="font-size: 18px;">{hex_cast.get_zhuxi_strategy(lang)}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 顯示關鍵爻辭
        key_lines = hex_cast.get_key_lines_text(lang)
        if key_lines:
            st.markdown(t["key_lines_title"])
            for line_text in key_lines:
                st.info(line_text) 
        
        st.divider()
        
      # 5. 雙欄排版顯示卦象 (分層對齊與動態標籤)
        
        # 動態設定卦辭的標籤
        desc_label = "**卦辭：**" if lang == "繁體中文" else "**Desc:**"
        
        # 建立一個小函式來美化標題排版 (解決英文過長與非預期換行的問題)
        def format_gua_title(label, name, is_en):
            if is_en and " (" in name:
                # 將 "Dui (The Joyous / Lake)" 切割，主動讓括號內容換行並套用副標題樣式
                main_title, sub_title = name.split(" (", 1)
                return f"<div class='gua-title' style='line-height: 1.3;'>{label} {main_title}<br><span style='font-size: 18px; opacity: 0.85;'>({sub_title}</span></div>"
            else:
                return f"<div class='gua-title'>{label} {name}</div>"

        # 第一層雙欄：專門顯示標題與卦辭
        col1_top, col2_top = st.columns(2)
        
        is_en = (lang == "English")
        
        with col1_top:
            st.markdown(format_gua_title(t['base_hex'], hex_cast.base_hex['name' + suffix], is_en), unsafe_allow_html=True)
            st.markdown(f"{desc_label} {hex_cast.base_hex['description' + suffix]}")
            
        with col2_top:
            if hex_cast.trans_hex:
                st.markdown(format_gua_title(t['trans_hex'], hex_cast.trans_hex['name' + suffix], is_en), unsafe_allow_html=True)
                st.markdown(f"{desc_label} {hex_cast.trans_hex['description' + suffix]}")
            else:
                st.markdown(f"<div class='gua-title'>{t['no_trans']}</div>", unsafe_allow_html=True)
                st.markdown(t["no_trans_desc"])

        st.markdown("<br>", unsafe_allow_html=True) 
        
        # 第二層雙欄：專門顯示視覺化爻象圖，確保左右絕對水平對齊
        col1_bot, col2_bot = st.columns(2)
        
        with col1_bot:
            st.markdown(draw_hexagram_lines(hex_cast.numbers, is_transformed=False, lang=lang), unsafe_allow_html=True)
            
        with col2_bot:
            if hex_cast.trans_hex:
                st.markdown(draw_hexagram_lines(hex_cast.numbers, is_transformed=True, lang=lang), unsafe_allow_html=True)

        # ==========================================
        # AI 解卦 Prompt 生成器
        # ==========================================
        st.divider()
        st.markdown(t["ai_title"])
        st.markdown(t["ai_desc"])
        
        if lang == "繁體中文":
            trans_info = f"變卦：{hex_cast.trans_hex['name_cn']} ({hex_cast.trans_hex['description_cn']})" if hex_cast.trans_hex else "變卦：無 (代表局勢平穩，專注本卦即可)"
            moving_info = f"{[f'第 {i+1} 爻' for i in hex_cast.moving_lines]}" if hex_cast.moving_lines else "無動爻"
            
            llm_prompt = f"""你現在是一位精通《易經》的解卦大師，能將深奧的古文結合現代人的情境進行白話解析。
請根據以下我擲出的占卜結果與朱熹的解卦法則，為我的問題提供深入、客觀且具建設性的分析。

【我的問題】
{question}

【占卜結果】
- 本卦：{hex_cast.base_hex['name_cn']} ({hex_cast.base_hex['description_cn']})
- {trans_info}
- 動爻位置：{moving_info}

【解卦指引（朱熹法則）】
{hex_cast.get_zhuxi_strategy(lang)}

【請依照以下架構回覆我】
1. 卦象總覽：這支卦反映了我目前問題的大環境與隱藏狀態是什麼？
2. 核心建議：請嚴格遵循上述提供的「解卦指引（朱熹法則）」，告訴我下一步該怎麼做。
3. 決策金句：用一句話總結我該抱持的心態或具體行動。"""

        else:
            trans_info = f"Transformed: {hex_cast.trans_hex['name_en']} ({hex_cast.trans_hex['description_en']})" if hex_cast.trans_hex else "Transformed: None (Indicates a stable situation, focus on the base hexagram)"
            moving_info = f"{[f'Line {i+1}' for i in hex_cast.moving_lines]}" if hex_cast.moving_lines else "No moving lines"
            
            llm_prompt = f"""You are an I-Ching master who can translate deep ancient texts into modern contexts. Based on the divination result and Zhu Xi's rules, provide an objective and constructive analysis for my question.

[My Question]
{question}

[Divination Result]
- Base Hexagram: {hex_cast.base_hex['name_en']} ({hex_cast.base_hex['description_en']})
- {trans_info}
- Moving Lines: {moving_info}

[Divination Guide (Zhu Xi's Rule)]
{hex_cast.get_zhuxi_strategy(lang)}

[Please respond using the following structure]
1. Overall Hexagram: What is the current environment and hidden state of my problem?
2. Core Advice: Strictly follow Zhu Xi's guide above and tell me what to do next.
3. Golden Quote: Summarize the mindset or action I should take in one sentence.

Please act as an I-Ching master and respond to my entire query strictly in English."""

        st.code(llm_prompt, language="markdown")

st.divider() # 加上一條淺色分隔線
st.markdown(f"""
<div style="max-width: 650px; margin: 0 auto; color: rgba(250, 250, 250, 0.45); font-size: 13px; line-height: 1.6;">
    <p style="text-align: center; font-weight: bold; margin-bottom: 6px; color: rgba(250, 250, 250, 0.6);">{t['disclaimer_title']}</p>
    <p style="text-align: justify; text-align-last: center; margin-top: 0;">{t['disclaimer_text']}</p>
</div>
""", unsafe_allow_html=True)