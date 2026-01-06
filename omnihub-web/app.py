import streamlit as st
from google.cloud import storage
import os

# 설정 정보
PROJECT_ID = "jnu-rise-edu-150"
# 실제 생성하신 GCS 버킷 이름을 입력하세요. (예: omnipulse-storage-150)
BUCKET_NAME = "omnihub-raw-data" 

def upload_to_gcs(uploaded_file, bucket_name):
    """파일을 GCS 버킷으로 업로드하는 함수"""
    try:
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(uploaded_file.name)
        blob.upload_from_file(uploaded_file, content_type=uploaded_file.type)
        return True
    except Exception as e:
        st.error(f"GCS 업로드 중 오류 발생: {e}")
        return False

# UI 구성
st.set_page_config(page_title="OmniPulse Upload", layout="centered")
st.title("� OmniHub Chat")

# 세션 상태 초기화 (대화 기록)
if "messages" not in st.session_state:
    st.session_state.messages = []

# 이전 대화 기록 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사이드바: 파일 업로드
with st.sidebar:
    st.header("📂 파일 업로드")
    uploaded_file = st.file_uploader("분석할 파일을 선택하세요", type=["pdf", "png", "jpg", "docx"])
    
    upload_clicked = st.button("🚀 업로드 및 분석 요청")

# 메인 로직
if uploaded_file is not None and upload_clicked:
    # 1. 사용자 메시지 추가 및 표시
    user_msg = f"파일 분석 요청: **{uploaded_file.name}**"
    st.session_state.messages.append({"role": "user", "content": user_msg})
    
    with st.chat_message("user"):
        st.markdown(user_msg)

    # 2. 파일 업로드 및 분석 대기
    with st.chat_message("assistant"):
        with st.status("파일 처리 중...", expanded=True) as status:
            st.write("GCS로 파일 전송 중...")
            if upload_to_gcs(uploaded_file, BUCKET_NAME):
                st.write("전송 완료! Gemini 분석 요청 중...")
                
                # HTTP 요청 로직
                import requests
                
                # [중요] 배포 후 생성된 Cloud Functions의 Trigger URL을 여기에 입력하세요.
                # 예: "https://asia-northeast3-jnu-rise-edu-150.cloudfunctions.net/analyze_with_gemini"
                FUNCTION_URL = "YOUR_CLOUD_FUNCTION_TRIGGER_URL_HERE" 
                
                payload = {
                    "bucket": BUCKET_NAME,
                    "name": uploaded_file.name
                }
                
                try:
                    response = requests.post(FUNCTION_URL, json=payload, timeout=300) # 5분 타임아웃
                    
                    if response.status_code == 200:
                        result_text = response.text
                        status.update(label="분석 완료!", state="complete", expanded=False)
                        
                        st.markdown("### 📝 Gemini 분석 리포트")
                        st.write(result_text)
                        
                        # 대화 기록에 저장
                        st.session_state.messages.append({"role": "assistant", "content": result_text})
                    else:
                        status.update(label="분석 실패", state="error")
                        st.error(f"오류: {response.status_code} - {response.text}")
                        
                except Exception as e:
                    status.update(label="요청 오류", state="error")
                    st.error(f"요청 중 오류 발생: {e}")

            else:
                status.update(label="업로드 실패", state="error")
