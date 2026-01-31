import streamlit as st

st.set_page_config(
    page_title="Truth Lens - 사기 방어 시뮬레이터",
    page_icon="🔍",
    layout="centered"
)

# 메인 헤더
st.title("🔍 Truth Lens")
st.subheader("AI 기반 실시간 사기 방어 시뮬레이터")

st.markdown("---")

# 소개 섹션
st.markdown("""
### 💡 Truth Lens란?

**감정을 마비시키는 순간, 이성을 깨우는 기술**

Truth Lens는 사기범들이 사용하는 심리 조작 기법을 실시간으로 감지하고,  
피해자가 **스스로 현실을 자각**하도록 돕는 AI 넛지(Nudge) 시스템입니다.

#### 🎯 핵심 기능
- 🚨 **실시간 위험 탐지**: 로맨스 스캠, 사칭 사기 등 패턴 자동 인식
- 🧠 **인지 개입**: 감정적 판단을 멈추고 이성적 사고 유도
- ✍️ **타이핑 검증**: 위험 행동 전 현실 자각 문장 직접 입력
- 🛡️ **다단계 방어**: 최종 경고까지 여러 차례 방어 기회 제공
""")

st.markdown("---")

# 시나리오 선택
st.markdown("### 📱 체험해보기")
st.write("실제 사기 상황을 시뮬레이션으로 체험하고, Truth Lens가 어떻게 당신을 보호하는지 확인하세요.")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    #### 💔 로맨스 스캠
    
    친밀감을 형성한 후  
    투자 명목으로 금전 요구
    
    - 인스타그램/SNS DM
    - 감정적 유대감 형성
    - 급한 송금 요청
    """)
    if st.button("🎭 로맨스 스캠 시작하기", use_container_width=True):
        st.switch_page("pages/romance_scam.py")

with col2:
    st.markdown("""
    #### ⚖️ 검찰/경찰 사칭
     
    공공기관을 사칭하여  
    악성 앱 설치 유도
    
    - 문자/카카오톡
    - 긴급성/공포감 조성
    - 앱 설치 강요
    """)
    if st.button("🚔 검찰 사칭 시작하기", use_container_width=True):
        st.switch_page("pages/impersonation_scam.py")

st.markdown("---")

# 통계 섹션
st.markdown("### 📊 왜 Truth Lens가 필요한가?")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="2023년 보이스피싱 피해액",
        value="8,577억원",
        delta="+12.3% (전년 대비)"
    )

with col2:
    st.metric(
        label="로맨스 스캠 피해 건수",
        value="1,247건",
        delta="+34% (증가 추세)"
    )

with col3:
    st.metric(
        label="평균 피해 금액",
        value="638만원",
        delta="1인당"
    )

st.markdown("---")

# 작동 원리
with st.expander("🔬 Truth Lens는 어떻게 작동하나요?"):
    st.markdown("""
    ### 3단계 방어 시스템
    
    **1단계: 패턴 인식**
    - AI가 대화/문자 내용을 실시간 분석
    - 사기 패턴(긴급성, 공포, 친밀감 등) 감지
    
    **2단계: 현실 자각 유도**
    - 감정적 판단을 멈추는 "타이핑 검증"
    - 사실을 직접 입력하며 상황 인지
    
    **3단계: 최종 경고**
    - 위험 행동 실행 직전 마지막 확인
    - 명확한 선택지 제공 (취소/진행)
    """)

# 푸터
st.markdown("---")
st.caption("⚠️ 본 서비스는 교육 목적의 시뮬레이션입니다. 실제 사기 피해 시 112 또는 금융감독원(1332)에 신고하세요.")
st.caption("© 2024 Truth Lens Project. 모두가 안전한 디지털 환경을 만듭니다.")