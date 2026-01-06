import streamlit as st
import google.generativeai as genai
import PyPDF2
from io import BytesIO
import pandas as pd
from datetime import datetime

# ==========================================
# 1. API 키 보안 설정 (배포 환경용)
# ==========================================
# Streamlit Cloud의 Settings -> Secrets에 설정된 GEMINI_API_KEY를 가져옵니다.
if "GEMINI_API_KEY" in st.secrets:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("⚠️ 설정 오류: Streamlit Cloud의 Secrets 메뉴에서 'GEMINI_API_KEY'를 등록해주세요.")
    st.stop() # 키가 없으면 실행 중단

# ==========================================
# 2. 유틸리티 함수 (PDF 텍스트 추출)
# ==========================================
def extract_text_from_pdf(file):
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            content = page.extract_text()
            if content:
                text += content
        return text
    except Exception as e:
        return f"파일 읽기 오류: {e}"

# ==========================================
# 3. 웹 페이지 UI 구성
# ==========================================
st.set_page_config(page_title="태평중앙교회 교육위원회", page_icon="⛪", layout="wide")

# 헤더
st.title("⛪ 다음 세대 교육지원 관리 시스템")
st.markdown("#### **\"하나님 나라의 지경을 넓히는 교회 (역대상 4:10)\"**")
st.divider()

# 사이드바: 부서 선택
departments = ["영아부", "유치부", "유초등부", "청소년부", "청년부"]
selected_dept = st.sidebar.selectbox("📂 대상 부서를 선택하세요", departments)
st.sidebar.divider()
st.sidebar.info("💡 계획서를 업로드하면 AI가 교육 비전에 맞춰 분석해 드립니다.")

# 메인 섹션
st.write(f"### 📋 {selected_dept} 행사 계획서 검토")

uploaded_file = st.file_uploader("계획서 파일 업로드 (PDF 권장)", type=['pdf', 'docx', 'txt'])

if uploaded_file is not None:
    # 파일 처리 로딩
    with st.spinner('문서를 분석 준비 중입니다...'):
        if uploaded_file.type == "application/pdf":
            file_text = extract_text_from_pdf(uploaded_file)
        else:
            file_text = uploaded_file.read().decode("utf-8", errors="ignore")

    st.success(f"✅ '{uploaded_file.name}' 업로드 성공")
    
    # 2단 화면 구성
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("💬 코멘트 1 (위원 의견)")
        comment_1 = st.text_area("장로님 또는 교육위원의 의견을 기록하세요.", height=250)
        if st.button("의견 저장하기"):
            st.toast("위원님의 의견이 정상적으로 기록되었습니다.")

    with col2:
        st.subheader("🤖 코멘트 AI (Gemini 분석)")
        if st.button("AI 분석 시작"):
            with st.spinner('태평중앙교회 AI 비서가 검토 중입니다...'):
                try:
                    prompt = f"""
                    너는 태평중앙교회 교육위원회의 사역을 돕는 지능형 비서야. 
                    다음은 {selected_dept}에서 제출한 계획서 내용의 일부야:
                    ---
                    {file_text[:3500]} 
                    ---
                    위 내용을 읽고 다음 세대 신앙 교육의 관점에서 세 가지 피드백을 줘:
                    1. [격려] 계획의 훌륭한 점과 담당자의 수고에 대한 감사
                    2. [비전] '하나님 나라의 지경을 넓히는가'에 대한 영적 조언
                    3. [실무] 예산, 안전, 구체성 등에서 보완할 점
                    답변은 정중하고 따뜻한 톤으로 300자 내외로 작성해줘.
                    """
                    response = model.generate_content(prompt)
                    st.info(response.text)
                    st.caption("※ 본 제언은 인공지능에 의해 생성된 참고용 데이터입니다.")
                except Exception as e:
                    st.error(f"분석 중 오류가 발생했습니다. (API 설정 확인 필요): {e}")

# 하단 히스토리
st.divider()
st.write("### 📜 최근 관리 내역")
history_data = {
    "날짜": [datetime.now().strftime("%Y-%m-%d")],
    "부서": [selected_dept],
    "파일명": [uploaded_file.name if uploaded_file else "대기 중"],
    "상태": ["진행 중" if uploaded_file else "미등록"]
}
st.table(pd.DataFrame(history_data))

st.divider()
st.caption("© 2026 대한예수교장로회 태평중앙교회 교육위원회")
