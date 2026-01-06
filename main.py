import streamlit as st
import google.generativeai as genai
import PyPDF2
from io import BytesIO

# 1. Gemini API 설정 (발급받은 API 키를 입력하세요)
# 실제 서비스 시에는 st.secrets 등으로 보안 관리 권장
API_KEY = "AIzaSyCSj-2mIlaGqXb_udwimX-Yo2QclM3QX-s" 
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# 페이지 설정
st.set_page_config(page_title="태평중앙교회 교육위원회", page_icon="⛪")

st.title("⛪ 다음 세대 교육지원 관리 시스템")
st.info("비전: 하나님 나라의 지경을 넓히는 교회 (역대상 4:10)")

# 사이드바: 부서 선택
departments = ["영아부", "유치부", "유초등부", "청소년부", "청년부"]
selected_dept = st.sidebar.selectbox("대상 부서를 선택하세요", departments)

# 메인 영역
st.write(f"### 📁 {selected_dept} 행사 계획서 분석 및 관리")

uploaded_file = st.file_uploader("계획서 파일 업로드 (PDF 권장)", type=['pdf', 'docx', 'txt'])

if uploaded_file is not None:
    # 1. 파일 읽기 및 텍스트 추출
    file_content = ""
    if uploaded_file.type == "application/pdf":
        file_content = extract_text_from_pdf(uploaded_file)
    else:
        file_content = uploaded_file.read().decode("utf-8", errors="ignore")

    st.success(f"✅ '{uploaded_file.name}' 업로드 완료")
    
    # 2. 화면 분할 (코멘트 영역)
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("💬 코멘트 1 (위원 의견)")
        user_comment = st.text_area("장로님/위원님의 의견을 남겨주세요.", height=200)
        if st.button("위원 코멘트 저장"):
            st.success("의견이 성공적으로 저장되었습니다.")

    with col2:
        st.subheader("🤖 코멘트 AI (Gemini 분석)")
        if st.button("AI 분석 실행"):
            with st.spinner('태평중앙교회 AI 비서가 계획서를 읽고 있습니다...'):
                try:
                    # AI에게 줄 프롬프트 설정
                    prompt = f"""
                    너는 태평중앙교회 교육위원회의 AI 비서야. 
                    다음은 {selected_dept}에서 제출한 행사 계획서 내용이야:
                    ---
                    {file_content[:3000]} 
                    ---
                    위 내용을 읽고 '하나님 나라의 지경을 넓히는 비전'과 '다음 세대 교육' 관점에서 
                    격려의 말과 함께 보완하면 좋을 실무적 제언을 300자 내외로 작성해줘.
                    """
                    response = model.generate_content(prompt)
                    st.markdown(f"**[AI 분석 결과]**\n\n{response.text}")
                except Exception as e:
                    st.error(f"AI 분석 중 오류가 발생했습니다: {e}")

# 하단 히스토리 (예시)
st.divider()
st.caption("© 2026 대한예수교장로회 태평중앙교회 교육위원회")
