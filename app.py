import streamlit as st
from groq import Groq
import json
import re
import streamlit.components.v1 as components

# ==========================================
# 系統設定 (Groq Llama-3 高速推理引擎)
# ==========================================
# 從 Streamlit Secrets 讀取 Groq 金鑰
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=GROQ_API_KEY)

# 強制鎖定最新版 Llama-3.3-70B 旗艦模型 (邏輯更強、速度極快)
if "model_name" not in st.session_state:
    st.session_state.model_name = "llama-3.3-70b-versatile"
    print(f"🌟 [系統提示] 已成功載入阿卡夏底層大腦：{st.session_state.model_name}")

# ==========================================
# 📚 劇本資料庫 (新增劇本都在這裡設定)
# ==========================================
SCENARIOS = {
    "新手教學：基礎法則": {
        "title": "🚪 新手教學：基礎法則驗證",
        "caption": "🌌 阿卡夏守門人 ── 系統沙盒",
        "init_stats": {
            "HP (生命)": 100,
            "Sanity (理智)": 100,
            "Inventory": ["裝滿清水的鐵桶", "純棉大被子", "長約兩公尺的木棍"],
            "Scene_State": "Puzzle"
        },
        "init_msg": "*「系統啟動。進入基礎邏輯與物理法則驗證程序。」*\n\n你身處在一個毫無裝飾的灰色水泥房間裡。房間唯一的出口是一扇鐵門，但鐵門前方正燃燒著一堆**【猛烈的營火】**，火勢很大，無法直接跨越，且濃煙正逐漸填滿房間。\n\n在房間的角落，散落著三樣尋常的物品，這也是你目前擁有的資源。\n\n> 💡 **【系統提示：遊戲機制指南】**\n> 請觀察環境與物品的物理特性，並詳細描述你要**如何使用或組合**手邊的物品來解決眼前的危機。",
        
        # 👇 替換這裡的 dm_rule 👇
        "dm_rule": "【極嚴格煞車機制】：這是一個密室逃脫的新手測驗。玩家的唯一終極目標是「成功跨越營火並打開鐵門」。\n若玩家成功打開門，你的 `story_text` 必須立刻以「推開沉重的鐵門後，刺眼的白光吞噬了你的視線...」作結，【絕對禁止】描寫門外的風景、走廊、聲音或任何後續發展！\n同時，請在 `settlement_text` 輸出：「🎉 新手教程通關！請從左側選單切換至『第一層劇本』」。"
    },
    "第一層：阿卡夏起源之井": {
        "title": "🌌 阿卡夏守門人：起源之井",
        "caption": "🌌 核心主線 ── 第一層",
        "init_stats": {
            "HP (生命)": 100,
            "Sanity (理智)": 100,
            "Inventory": ["歸源折疊提燈", "透徹之羽"],
            "Scene_State": "Explore"
        },
        "init_msg": "你已抵達阿卡夏書庫第七層「冥想迴廊」。周圍懸浮著無數散發微光的書卷，寂靜得只能聽到你自己的心跳聲。\n\n前方不遠處，一具古老的**刻印寶箱**正散發著不穩定的幾何波紋，似乎內藏著某種空間陷阱。\n\n> 💡 **【你可以嘗試的行動】：**\n> 1. 靠近觀察寶箱的幾何波紋規律。\n> 2. 舉起「歸源折疊提燈」照亮周圍的書卷。\n> 3. 對著空曠的迴廊呼喊，測試是否有回音。",
        "dm_rule": "【世界觀與推進】：這是一個充滿星靈與代碼法則的宇宙奇幻世界。玩家解決眼前的危機後，請在環境中安插神秘線索（如亂碼日誌、未知星塵），引導玩家發掘更深層的陰謀，採用「碎片化敘事」，不要一次給出所有答案。"
    }
}

# ==========================================
# 狀態初始化與劇本切換邏輯
# ==========================================
if "current_scenario" not in st.session_state:
    st.session_state.current_scenario = "新手教學：基礎法則"
    
def load_scenario(scenario_name):
    # 清空記憶並載入新劇本
    st.session_state.current_scenario = scenario_name
    st.session_state.player_stats = SCENARIOS[scenario_name]["init_stats"].copy()
    st.session_state.messages = [{
        "role": "assistant", 
        "content": SCENARIOS[scenario_name]["init_msg"],
        "settlement": "🔻 劇本已載入。準備開始探索。"
    }]

# 初次載入
if "messages" not in st.session_state:
    load_scenario(st.session_state.current_scenario)

# 輔助函式：安全解析 AI JSON
def parse_ai_response(response_text):
    try:
        # 使用正則表達式，暴力抓取第一個 '{' 到最後一個 '}' 之間的所有內容
        match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if match:
            clean_text = match.group(0)
            return json.loads(clean_text)
        else:
            raise ValueError("找不到 JSON 括號")
    except Exception:
        return {
            "story_text": response_text + "\n\n*(系統警告：AI 思考迴路產生波動，未依格式輸出)*",
            "settlement_text": "⚠️ 法則文字解析異常，維持當前狀態。",
            "updated_stats": st.session_state.player_stats
        }

# ==========================================
# UI 渲染：深空風格與側邊欄
# ==========================================
st.set_page_config(page_title="阿卡夏守門人", page_icon="🌌", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #0B0F19 !important; }
    [data-testid="stSidebar"] { background-color: #111827 !important; }
    .stApp p, .stApp h1, .stApp h2, .stApp h3, .stApp span, .stApp li, .stApp label { color: #F8FAFC !important; }
    [data-testid="stMetricValue"] { color: #38BDF8 !important; }
    .settlement-box {
        background-color: #1E293B !important;
        border-left: 5px solid #38BDF8 !important;
        padding: 12px !important;
        border-radius: 4px !important;
        margin-top: 10px !important; margin-bottom: 20px !important;
        color: #F8FAFC !important; font-family: monospace !important;
    }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("🗂️ 系統終端機")
    
    # 劇本選擇下拉選單
    selected_scenario = st.selectbox(
        "切換劇本：", 
        list(SCENARIOS.keys()), 
        index=list(SCENARIOS.keys()).index(st.session_state.current_scenario)
    )
    
    # 偵測是否切換，若切換則重新載入並重啟網頁
    if selected_scenario != st.session_state.current_scenario:
        load_scenario(selected_scenario)
        st.rerun()

    st.markdown("---")
    st.header("📊 守門人狀態")
    st.metric(label="生命值 (HP)", value=st.session_state.player_stats.get("HP (生命)", 100))
    st.metric(label="理智值 (Sanity)", value=st.session_state.player_stats.get("Sanity (理智)", 100))
    
    st.markdown("---")
    state_mapping = {
        "Explore": {"label": "🎵 【未知探索】星空 Ambient Lo-Fi", "url": "https://cdn.pixabay.com/download/audio/2022/05/27/audio_1808fbf07a.mp3"},
        "Puzzle": {"label": "🎵 【智慧解謎】專注 Clockwork Lo-Fi", "url": "https://cdn.pixabay.com/download/audio/2022/03/15/audio_c8b828ef0f.mp3"},
        "Combat": {"label": "💥 【危機戰鬥】緊湊 Phonk Lo-Fi", "url": "https://cdn.pixabay.com/download/audio/2022/10/14/audio_9939f790cb.mp3"},
        "Rest": {"label": "🔥 【安全重整】溫暖柴火 Jazz Lo-Fi", "url": "https://cdn.pixabay.com/download/audio/2021/09/06/audio_907bb33671.mp3"},
        "Epic": {"label": "🌌 【史詩揭秘】慢速交響 Lo-Fi", "url": "https://cdn.pixabay.com/download/audio/2023/04/07/audio_50b4ec2b2e.mp3"}
    }
    
    current_state = st.session_state.player_stats.get("Scene_State", "Explore")
    bgm_info = state_mapping.get(current_state, state_mapping["Explore"])
    st.info(f"當前情境：{bgm_info['label']}")
    
    audio_js = f"""
    <script>
        const audioUrl = "{bgm_info['url']}";
        const doc = window.parent.document;
        let audioEl = doc.getElementById("bgm-player");
        if (!audioEl) {{
            audioEl = doc.createElement("audio");
            audioEl.id = "bgm-player";
            audioEl.loop = true; audioEl.autoplay = true; audioEl.volume = 0.4;
            doc.body.appendChild(audioEl);
        }}
        if (audioEl.src !== audioUrl) {{
            audioEl.src = audioUrl;
            audioEl.play().catch(e => console.log("等待使用者點擊"));
        }}
    </script>
    """
    components.html(audio_js, height=0, width=0)
    
    st.markdown("---")
    st.write("🎒 **持有物品**:")
    for item in st.session_state.player_stats.get("Inventory", []):
        st.write(f"- {item}")

# 動態主標題
current_scenario_data = SCENARIOS[st.session_state.current_scenario]
st.title(current_scenario_data["title"])
st.caption(current_scenario_data["caption"])
# 👇 新增這行：給手機版玩家的 UI 提示
st.info("📱 **系統提示**：手機版玩家請點擊畫面左上角的 **「 ＞ 」** 符號，展開系統面板來查看血量、道具，或切換劇本。")
st.markdown("---")

# 渲染對話歷史
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "settlement" in msg and msg["settlement"]:
            st.markdown(f'<div class="settlement-box"><b>⚙️ 系統結算：</b><br>{msg["settlement"]}</div>', unsafe_allow_html=True)

# ==========================================
# 遊戲核心引擎 (AI DM 判定中心)
# ==========================================
if user_input := st.chat_input("輸入你的行動... (描述越具體越好)"):
    st.session_state.messages.append({"role": "user", "content": user_input, "settlement": ""})
    with st.chat_message("user"):
        st.markdown(user_input)

    history_context = ""
    for msg in st.session_state.messages[-5:]:
        role_name = "DM系統" if msg["role"] == "assistant" else "玩家"
        history_context += f"[{role_name}]: {msg['content']}\n"

    # 動態寫入該劇本的專屬指令
    scenario_rule = current_scenario_data["dm_rule"]

    system_prompt = f"""
    你是一個高質感的文字冒險遊戲 DM。目前進行的劇本是：「{st.session_state.current_scenario}」。
    玩家狀態：{json.dumps(st.session_state.player_stats, ensure_ascii=False)}

    【本劇本專屬守則】
    {scenario_rule}

    【核心判定守則】
    1. 物理法則優先：根據玩家描述的邏輯進行嚴格判定。不合理的行為給予重度扣血懲罰。
    2. 向前失敗 (Fail Forward)：【絕對禁止死胡同】。如果玩家毀了關鍵道具，不要卡關。讓他們付出沉重代價（如大扣血），但同時引發連鎖反應，開啟另一條更痛苦但能推進劇情的路。
    3. 狀態死亡：如果玩家 HP 或 Sanity 降至 0 或以下，請宣布「Game Over」，並給出一段史詩的死亡敘述。

    【排版與輸出守則】
    1. 故事文字 (story_text)：必須具沉浸感，但不能過度堆砌詞藻。善用 `*斜體*` 描寫聲音與內心，`**粗體**` 強調物件。
    ★ 關鍵引導：在 story_text 的最後一段，你【必須】主動提供 2~3 個明確的「行動建議」或「互動選項」（例如：「💡 接下來你可以選擇：1. 調查牆上的壁畫... 2. 試著用木棍撬開...」），絕對不要讓玩家陷入不知道能做什麼的窘境。
    2. 音樂情境 (Scene_State)：根據當前局勢，更新為 Explore, Puzzle, Combat, Rest, 或 Epic。
    3. 結算文字 (settlement_text)：【必須絕對直白】，只條列 HP/理智 變化、獲得/失去什麼物品。不准有文學修飾。

    你【必須】嚴格以下列 JSON 格式回覆：
    {{
        "story_text": "（沉浸感劇情）",
        "settlement_text": "（直白的系統結算，例如：HP -5 / 獲得：物品A）",
        "updated_stats": {{
            "HP (生命)": (數字),
            "Sanity (理智)": (數字),
            "Inventory": ["物品A", "物品B"],
            "Scene_State": "(五種情境之一)" 
        }}
    }}
    
    【近期劇情】
    {history_context}
    """

    with st.chat_message("assistant"):
        with st.spinner('法則運算中...'):
            try:
                # 呼叫 Groq API (支援原生 JSON 鎖定)
                chat_completion = client.chat.completions.create(
                    messages=[
                        {
                            "role": "system",
                            "content": system_prompt
                        },
                        {
                            "role": "user",
                            "content": "【玩家最新行動】：" + user_input
                        }
                    ],
                    model=st.session_state.model_name,
                    temperature=0.6,
                    response_format={"type": "json_object"} 
                )
                
                # 提取 Groq 的回覆文字
                response_text = chat_completion.choices[0].message.content
                
                # 解析 JSON (保留正則表達式作為雙重保險)
                parsed_data = parse_ai_response(response_text)
                
                # 更新畫面與狀態
                st.markdown(parsed_data.get("story_text", "系統無回應"))
                if parsed_data.get("settlement_text"):
                    st.markdown(f'<div class="settlement-box"><b>⚙️ 系統結算：</b><br>{parsed_data["settlement_text"]}</div>', unsafe_allow_html=True)
                
                st.session_state.player_stats = parsed_data.get("updated_stats", st.session_state.player_stats)
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": parsed_data.get("story_text", ""),
                    "settlement": parsed_data.get("settlement_text", "")
                })
                
            except Exception as e:
                # 攔截錯誤
                error_msg = str(e)
                if "429" in error_msg or "rate limit" in error_msg.lower():
                    sys_reply = "🛑 **[系統提示] API 請求頻率限制 (Error 429)**\n\n由於目前連接的是免費版 AI 伺服器，您的動作太快已觸發流量保護機制。\n\n💡 **請注意：這並非遊戲內的謎題或懲罰。**請暫停操作，等待約 1 分鐘後再重新送出您的指令即可繼續遊玩。"
                else:
                    sys_reply = f"⚠️ **[系統報錯] 伺服器異常**\n\n遊戲引擎發生未知錯誤，這與您的遊玩決策無關。請稍後再試。({error_msg})"
                
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": sys_reply,
                    "settlement": "🛑 系統中斷：狀態未變更"
                })
                
    st.rerun()
