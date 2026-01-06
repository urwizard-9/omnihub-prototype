import functions_framework
from google.cloud import storage
import vertexai
from vertexai.generative_models import GenerativeModel, Part

# 1. 초기화
vertexai.init(project="jnu-rise-edu-150", location="asia-northeast3")
model = GenerativeModel("gemini-1.5-flash")

@functions_framework.http
def analyze_with_gemini(request):
    """HTTP Cloud Function to analyze files using Gemini."""
    
    # 1. 요청에서 데이터 추출 (JSON)
    request_json = request.get_json(silent=True)
    if not request_json:
        return "JSON payload required", 400
        
    bucket_name = request_json.get("bucket")
    file_name = request_json.get("name")
    
    if not bucket_name or not file_name:
        return "Missing bucket or name parameters", 400
    
    print(f"새 분석 요청: {file_name} (버킷: {bucket_name})")

    try:
        # 2. Gemini에게 보낼 데이터 준비
        file_uri = f"gs://{bucket_name}/{file_name}"
        file_part = Part.from_uri(mime_type="application/pdf", uri=file_uri)
        
        # 3. 분석 요청
        prompt = "이 파일의 핵심 내용을 요약하고 인사이트를 추출해줘."
        response = model.generate_content([file_part, prompt])
        
        # 4. 결과 반환 (HTTP Response)
        print(f"Gemini 분석 성공")
        return response.text, 200
        
    except Exception as e:
        print(f"오류 발생: {e}")
        return f"Internal Server Error: {str(e)}", 500
