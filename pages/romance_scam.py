import streamlit as st
import time

st.set_page_config(page_title="Truth Lens - 로맨스 스캠", layout="centered")

# 세션 초기화
if 'step_a' not in st.session_state:
    st.session_state.step_a = 1
if 'verification_status' not in st.session_state:
    st.session_state.verification_status = "NONE" # NONE, FAIL, SUCCESS, FINAL_WARNING

st.header("📱 인스타그램 DM (시뮬레이션)")
st.caption("시나리오: 친밀감 형성 후 투자 사기 유도")

# --- 채팅 화면 ---
chat_container = st.container(border=True)
with chat_container:
    if st.session_state.step_a >= 1:
        st.chat_message("상대방", avatar="👩").write("자기야, 오늘 하루도 고생 많았어! 보고 싶다 ㅠㅠ")
    if st.session_state.step_a >= 2:
        st.chat_message("나", avatar="😊").write("나도.. 주말에 얼른 보고 싶네.")
    if st.session_state.step_a >= 3:
        st.chat_message("상대방", avatar="👩").write("참, 내가 저번에 말한 투자 건 말이야. 오늘 마감이라 지금 넣어야 해. 이 링크로 500만원만 보내줘. (http://bit.ly/fake-invest)")

# --- Truth Lens 개입 ---
if st.session_state.step_a == 3:
    st.divider()
    nudge_container = st.container(border=True)
    with nudge_container:
        st.error("🚨 Truth Lens: 고위험 송금 감지!")
        st.write("로맨스 스캠 패턴 일치율 **92%**. 잠시 멈추세요.")

        st.warning("🧠 잠깐! 퀴즈입니다.")
        st.write("Q: 상대방을 실제로 만난 적이 있나요?")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("예, 만났어요"):
                st.error("❌ 거짓말입니다. 당신은 한 번도 만난 적이 없습니다.")
        with col2:
            if st.button("아니요, 없어요"):
                st.success("✅ 정답! 그런데 왜 돈을 보내려고 하시나요?")
        
        # [변경점 1] 따라써야 할 문구를 가장 위로 배치하고 강조
        target_sentence = "나는 실제로 만난 적 없는 사람에게 돈을 보낸다"
        st.warning(f"**[현실 자각 퀴즈]** 송금을 진행하려면 아래 문장을 띄어쓰기 포함 정확히 입력하세요.")
        st.markdown(f"### 🗣️ \"{target_sentence}\"") # 크고 명확하게 표시
        
        user_input = st.text_input("위 문장을 그대로 따라 쓰세요:", key="input_a")

        # 검증 버튼
        if st.button("확인 및 송금 진행"):
            if user_input.strip() == target_sentence:
                st.session_state.verification_status = "SUCCESS"
            else:
                st.session_state.verification_status = "FAIL"

        # [변경점 2] 틀렸을 경우 다른 문구(에러 메시지)로 재작성 유도
        if st.session_state.verification_status == "FAIL":
            st.toast("❌ 문장이 일치하지 않습니다.", icon="🚫")
            st.error("⚠️ 틀렸습니다. 토씨 하나 틀리지 않고 정확하게 다시 작성하십시오. 당신의 소중한 자산을 지키기 위함입니다.")

        # [변경점 3] 맞게 썼을 때 1차 성공 -> 송금 버튼 노출
        if st.session_state.verification_status == "SUCCESS":
            st.success("✅ 문장 확인 완료. 버튼이 활성화되었습니다.")
            
            # 송금 버튼을 누르면 바로 넘어가는 게 아니라 '이중 경고' 단계로 진입
            if st.button("💸 500만원 송금하기", type="primary"):
                st.session_state.verification_status = "FINAL_WARNING"
                st.rerun()

        # [변경점 4] 송금 버튼을 눌렀을 때 뜨는 '최종 경고(Last Warning)'
        if st.session_state.verification_status == "FINAL_WARNING":
            st.markdown("---")
            st.error("🛑 **잠깐! 마지막 경고입니다.**")
            st.write("상대방의 얼굴을 영상통화로 확인하셨나요? 이 버튼을 누르면 다시는 돈을 돌려받을 수 없습니다.")
            st.write("**정말로 이체를 실행하시겠습니까?**")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("아니요, 취소합니다 (추천)"):
                     st.session_state.step_a = 4
                     st.rerun()
            with col2:
                if st.button("네, 사기여도 책임지겠습니다"):
                     st.session_state.verification_status = "REAL_END"
                     st.rerun()

        # 송금 취소 버튼 (항시 노출)
        if st.session_state.verification_status != "FINAL_WARNING":
            if st.button("송금 취소 및 차단"):
                st.session_state.step_a = 4
                st.rerun()

# --- 진행 컨트롤 ---
if st.session_state.step_a < 3:
    if st.button("다음 대화 ➡️"):
        st.session_state.step_a += 1
        st.rerun()

# --- 결말 ---
if st.session_state.step_a == 4:
    st.balloons()
    st.success("🛡️ 방어 성공! 이성적인 판단으로 사기를 예방했습니다.")
    if st.button("처음으로"):
        st.session_state.step_a = 1
        st.session_state.verification_status = "NONE"
        st.rerun()
elif st.session_state.verification_status == "REAL_END":
    st.error("💸 송금이 완료되었습니다... (피해 발생 시뮬레이션 종료)")