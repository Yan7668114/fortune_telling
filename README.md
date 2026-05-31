## 📖 關於專案 / About The Project

本專案將擁有三千年歷史的《易經》（I-Ching / Book of Changes）數位化，採用最正統的「大衍筮法」演算法進行虛擬起卦，並嚴格遵循南宋理學家朱熹的解卦法則來提取關鍵爻辭。

為了橋接現代科技，系統內建了**「AI 大師提示詞引擎」**，能自動將使用者的問題、占卜結果與解卦指引打包成完美的 Prompt，讓使用者可以直接貼給 ChatGPT、Claude 等大語言模型，獲取極具深度與現代視角的白話解析。

This project digitizes the 3,000-year-old *I-Ching* (Book of Changes). It utilizes the authentic "Yarrow Stalk" algorithm for virtual casting and strictly follows the divination rules established by the Song dynasty philosopher Zhu Xi to extract key moving lines.

To bridge ancient wisdom with modern tech, the system features an **AI Master Prompt Engine**. It automatically packages the user's question, the divination result, and Zhu Xi's guidance into a highly optimized prompt. Users can paste this into LLMs like ChatGPT or Claude for profound, modern interpretations.

## ✨ 核心功能 / Key Features

*   **☯️ 大衍筮法演算法 (Yarrow Stalk Algorithm)**：忠實還原傳統 49 根蓍草的機率分佈，每次起卦皆與天地共振。
*   **📜 完整雙語資料庫 (Bilingual Database)**：內建 64 卦、384 爻的完整中英雙語 JSON 資料庫，包含卦名、卦辭與精準翻譯。
*   **💡 朱熹解卦指引 (Zhu Xi's Rule Integration)**：系統會自動判斷 0 到 6 個動爻的變化，精準提示使用者該閱讀哪一段卦辭或爻辭。
*   **🌐 國際化無縫切換 (i18n UI)**：一鍵切換繁體中文與全英文介面，排版精美，適應各種螢幕尺寸。
*   **🤖 AI 提示詞生成 (AI Prompt Generation)**：動態生成結合占卜狀態的專屬 Prompt，讓 AI 成為你的私人解卦師。

## 🚀 快速開始 / Quick Start

### 1. 體驗線上版本 / Live Demo
點擊上方 Streamlit 徽章或[此處](https://your-streamlit-app-url.com)直接體驗線上服務。

### 2. 本地端執行 / Run Locally

**環境要求 (Prerequisites)**
* Python 3.9+

**安裝步驟 (Installation)**
```bash
# 1. 複製專案 (Clone the repo)
git clone [https://github.com/Yan7668114/fortune_telling.git](https://github.com/Yan7668114/fortune_telling.git)

# 2. 進入專案資料夾 (Navigate to directory)
cd fortune_telling

# 3. 安裝相依套件 (Install dependencies)
pip install streamlit

# 4. 啟動應用程式 (Run the app)
streamlit run app.py
