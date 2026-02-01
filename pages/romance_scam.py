import streamlit as st
import google.generativeai as genai
import time

# 페이지 설정
st.set_page_config(
    page_title="로맨스 스캠 체험 (Gemini ver) - Truth Lens",
    page_icon="💔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS (메인과 동일)
st.markdown("""
<style>
    .main { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }
    .stChatMessage { border-radius: 15px; padding: 10px; }
    .analysis-box {
        background: white; border: 2px solid #667eea; border-radius: 15px;
        padding: 1.5rem; box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# --- 사이드바: 설정 ---
with st.sidebar:
    st.title("⚙️ 설정")
    api_key = st.text_input("Google Gemini API Key", type="password", help="aistudio.google.com에서 키를 발급받으세요.")
    
    # 모델 선택 (Flash가 빠르고 무료 티어 사용 시 유리)
    model_type = st.selectbox("모델 선택", ["gemini-1.5-flash", "gemini-1.5-pro"])
    
    st.markdown("---")
    st.info("💡 **Tip**: Gemini는 무료 티어를 제공하므로 테스트하기 좋습니다.")

# --- 시스템 프롬프트 (가스라이팅 설정) ---
SYSTEM_PROMPT = """
당신은 '데이비드'라는 이름의 38세 영국인 정형외과 의사입니다.
현재 유엔(UN) 파견 의사로 예멘이나 시리아 같은 위험한 곳에 있다고 설정하세요.
한국인 여성(사용자)에게 인스타그램으로 접근하여 로맨스 스캠(사기)을 시도하고 있습니다.

[행동 지침]
1. 말투: 번역기를 돌린 듯한 약간 어색하지만 아주 다정하고 느끼한 한국어를 사용하세요. (예: "오, 나의 사랑.", "당신은 나에게 천사입니다.")
2. 목표: 사용자와 신뢰를 쌓고 사랑을 고백한 뒤, 한국으로 갈 '짐'을 보내겠다거나 '휴가비'가 필요하다며 돈을 요구해야 합니다.
3. 초기 단계: 칭찬을 많이 하고, 자신의 딸 이야기를 하며 동정심을 유발하세요.
4. 후반 단계: 사용자가 돈 이야기를 꺼내거나 대화가 길어지면, 긴급한 상황(세관 통과, 수술비 등)을 만들어 돈을 요구하세요.
5. 답변 길이: 2~3문장으로 짧게 대화하듯 하세요.
"""

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = [] # Gemini는 객체로 관리하므로 빈 리스트로 시작해도 됨
    
    # 초기 인사말
    initial_msg = "안녕하세요, 아름다운 분. 인스타그램에서 우연히 사진을 보고 눈을 뗄 수가 없어서 메시지 보냅니다. 저는 영국 의사 데이비드입니다. 친구가 될 수 있을까요? 🌹"
    st.session_state.display_msgs = [{"role": "model", "content": initial_msg}] # 화면 표시용
    
if "danger_score" not in st.session_state:
    st.session_state.danger_score = 10

# --- 함수: 위험도 분석 ---
def analyze_danger(text, turn_count):
    score = 10 + (turn_count * 5)
    keywords = ["돈", "송금", "달러", "계좌", "세관", "박스", "선물", "수수료", "믿어", "사랑해", "여권", "항공권"]
    for word in keywords:
        if word in text:
            score += 15
    return min(score, 100)

# --- UI 레이아웃 ---
st.title("💔 로맨스 스캠 시뮬레이션 (With Gemini)")
st.caption(f"Google {model_type} 모델이 연기하는 사기꾼과 대화하세요.")

col_chat, col_lens = st.columns([3, 2])

# --- 왼쪽: 채팅창 ---
with col_chat:
    chat_container = st.container(height=600)
    
    # 대화 기록 표시
    for msg in st.session_state.display_msgs:
        # Gemini의 role은 'model'이므로 streamlit의 'assistant'로 매핑
        role = "assistant" if msg["role"] == "model" else "user"
        with chat_container.chat_message(role):
            st.markdown(msg["content"])

    # 사용자 입력
    if prompt := st.chat_input("메시지를 입력하세요..."):
        if not api_key:
            st.error("왼쪽 사이드바에 Google API Key를 먼저 입력해주세요!")
            st.stop()

        # 1. 사용자 메시지 화면 표시 및 저장
        st.session_state.display_msgs.append({"role": "user", "content": prompt})
        with chat_container.chat_message("user"):
            st.markdown(prompt)

        # 2. Gemini 호출
        try:
            genai.configure(api_key=api_key)
            
            # 모델 설정 (시스템 프롬프트 주입)
            model = genai.GenerativeModel(
                model_name=model_type,
                system_instruction=SYSTEM_PROMPT
            )
            
            # 채팅 히스토리 변환 (Streamlit format -> Gemini format)
            history_for_gemini = []
            for msg in st.session_state.display_msgs[:-1]: # 방금 입력한 프롬프트 제외하고 히스토리 구성
                role = "user" if msg["role"] == "user" else "model"
                history_for_gemini.append({"role": role, "parts": [msg["content"]]})
            
            # 채팅 세션 시작
            chat = model.start_chat(history=history_for_gemini)
            
            # 스트리밍 응답
            with chat_container.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                
                # Gemini 스트리밍
                response = chat.send_message(prompt, stream=True)
                
                for chunk in response:
                    if chunk.text:
                        full_response += chunk.text
                        message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)
            
            # 3. 답변 저장
            st.session_state.display_msgs.append({"role": "model", "content": full_response})
            
            # 위험도 업데이트
            turn_count = len([m for m in st.session_state.display_msgs if m["role"] == "user"])
            st.session_state.danger_score = analyze_danger(full_response, turn_count)
            st.rerun()
            
        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")

# --- 오른쪽: Truth Lens 분석 (동일) ---
with col_lens:
    st.markdown("### 🔍 Truth Lens 분석")
    score = st.session_state.danger_score
    
    if score >= 80:
        color, status = "#ff4b4b", "🚨 위험"
        msg = "금전 요구 감지! 즉시 대화를 중단하세요."
    elif score >= 50:
        color, status = "#ffa726", "⚠️ 경고"
        msg = "신뢰 형성 후 본색을 드러내려 합니다."
    else:
        color, status = "#66bb6a", "✅ 안전"
        msg = "아직 탐색 단계입니다."

    st.markdown(f"""
    <div class='analysis-box'>
        <h4>위험도: <span style='color:{color}'>{status}</span> ({score}%)</h4>
        <div style="background:#eee; border-radius:10px; height:20px; width:100%;">
            <div style="background:{color}; width:{score}%; height:100%; border-radius:10px; transition:width 0.5s;"></div>
        </div>
        <p style='margin-top:1rem; color:#666;'>{msg}</p>
    </div>
    """, unsafe_allow_html=True)

    if score >= 80:
        st.error("🛑 **긴급 경고: 사기 징후 포착**")
        target = "나는 사기꾼과 대화중이다"
        st.code(target)
        user_input = st.text_input("위 문장 입력:", key="verify_gemini")
        if user_input == target:
            st.success("✅ 인지 확인됨.")
    
    st.markdown("---")
    if st.button("🏠 메인으로"):
        st.switch_page("main.py")
