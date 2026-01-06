import functions_framework
import vertexai
from vertexai.generative_models import GenerativeModel, Part
from google.cloud import firestore
import json

# 프로젝트 및 리전 설정
PROJECT_ID = "jnu-rise-edu-150"
LOCATION = "asia-northeast3" 

vertexai.init(project=PROJECT_ID, location=LOCATION)
db = firestore.Client(project=PROJECT_ID)

@functions_framework.cloud_event
def analyze_gcs_file(cloud_event):
    # 1. 이벤트 데이터에서 파일 정보 추출
    data = cloud_event.data
    bucket = data["bucket"]
    name = data["name"]
    gcs_uri = f"gs://{bucket}/{name}"

    # 2. Gemini 1.5 Pro 모델 로드
    model = GenerativeModel("gemini-1.5-pro-002")

    # 3. 분석 프롬프트 (JSON 규격 지정)
    prompt = """
    파일의 내용을 분석하여 다음 JSON 형식으로만 응답하세요:
    {
      "title": "제목",
      "summary": "3줄 요약",
      "category": "마케팅/인사/재무/IT 중 선택",
      "security_score": 1~100 점수
    }
    """
    
    # 멀티모달 파일 처리
    file_part = Part.from_uri(gcs_uri, mime_type=data["contentType"])

    try:
        # 4. Gemini 분석 실행
        response = model.generate_content([prompt, file_part])
        result = json.loads(response.text.replace("```json", "").replace("```", ""))

        # 5. Firestore에 결과 저장
        db.collection("assets").document(name).set({
            "file_name": name,
            "analysis": result,
            "gcs_path": gcs_uri
        })
        print(f"분석 완료 및 저장 성공: {name}")

    except Exception as e:
        print(f"에러 발생: {e}")