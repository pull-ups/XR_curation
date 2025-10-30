import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import List, Optional

from curation_types import CurationTypes, ARTWORK_NAMES, ARTWORK_NAME_KR_TO_EN
from touch_recognition import TouchRecognition

# --- Pydantic 모델 정의 ---
class CurationRequest(BaseModel):
    """큐레이션 타입 라우팅을 위한 요청 모델"""
    curation_type: int = Field(..., ge=1, le=6, description="큐레이션 타입 (1-6)")
    art_name: str = Field(..., description="작품명")
    memory: str = Field(default="", description="이전 대화 기록")
    viewed_artworks: Optional[List[str]] = Field(default=None, description="이미 본 작품 목록")
    question: Optional[str] = Field(default=None, description="타입 2에서 사용하는 질문")
    related_artwork: Optional[str] = Field(default=None, description="타입 3, 6에서 사용하는 연관 작품명")

class TouchRequest(BaseModel):
    """터치 기반 객체 인식을 위한 요청 모델"""
    art_name: str = Field(..., description="작품명")
    x: float = Field(..., ge=0, le=1, description="x 좌표 (정규화: 0~1)")
    y: float = Field(..., ge=0, le=1, description="y 좌표 (정규화: 0~1)")

class ObjectListRequest(BaseModel):
    """작품의 객체 목록 조회를 위한 요청 모델"""
    art_name: str = Field(..., description="작품명")

# --- FastAPI 앱 생성 ---
app = FastAPI(
    title="Curation Types API",
    description="큐레이션 타입별 나레이션 생성 및 터치 기반 객체 인식 API (Type 1-6 + Touch Recognition)",
    version="2.0.0"
)

# --- CurationTypes 인스턴스 생성 ---
try:
    curation_types = CurationTypes(comparison_data_path='./assets/llm/transformed_pair.json')
    print("✅ CurationTypes 초기화 완료")
except Exception as e:
    print(f"❌ CurationTypes 초기화 중 오류 발생: {e}")
    curation_types = None

# --- TouchRecognition 인스턴스 생성 ---
try:
    touch_recognition = TouchRecognition(vision_base_path='./vision')
    print("✅ TouchRecognition 초기화 완료")
except Exception as e:
    print(f"❌ TouchRecognition 초기화 중 오류 발생: {e}")
    touch_recognition = None

# --- 정적 파일 서빙 설정 ---
import os
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# --- API 엔드포인트 정의 ---

@app.get("/", summary="웹 인터페이스")
def root():
    """
    HTML 웹 인터페이스를 반환합니다.
    """
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    else:
        # 정적 파일이 없으면 API 정보 반환
        return {
            "name": "Curation Types API",
            "version": "2.0.0",
            "description": "큐레이션 타입별 나레이션 생성 및 터치 기반 객체 인식 API",
            "endpoints": {
                "GET /": "웹 인터페이스",
                "GET /ping": "서버 상태 확인",
                "GET /artworks": "사용 가능한 작품 목록",
                "POST /curation": "큐레이션 나레이션 생성 (Type 1-6)",
                "POST /touch": "터치 좌표로 객체 인식 및 LLM 설명 생성",
                "POST /objects": "작품의 모든 객체 목록 조회"
            },
            "features": {
                "curation_types": [
                    "Type 1: 작품 핵심 맥락 (120~170자)",
                    "Type 2: 간단한 정보제공 (질문 기반)",
                    "Type 3: 작품 비교제공",
                    "Type 4: 배경지식 제공 (3문장)",
                    "Type 5: 배경지식 + 느낌 묻기 (4문장)",
                    "Type 6: 조형요소 + 타인의견 + 관계짓기 (4문장)"
                ],
                "touch_recognition": "작품 터치 시 객체 인식 → LLM 설명 생성"
            }
        }

@app.get("/api/info", summary="API 정보")
def api_info():
    """
    API 기본 정보를 반환합니다.
    """
    return {
        "name": "Curation Types API",
        "version": "2.0.0",
        "description": "큐레이션 타입별 나레이션 생성 및 터치 기반 객체 인식 API",
        "endpoints": {
            "GET /": "웹 인터페이스",
            "GET /api/info": "API 정보",
            "GET /ping": "서버 상태 확인",
            "GET /artworks": "사용 가능한 작품 목록",
            "POST /curation": "큐레이션 나레이션 생성 (Type 1-6)",
            "POST /touch": "터치 좌표로 객체 인식 및 LLM 설명 생성",
            "POST /objects": "작품의 모든 객체 목록 조회"
        },
        "features": {
            "curation_types": [
                "Type 1: 작품 핵심 맥락 (120~170자)",
                "Type 2: 간단한 정보제공 (질문 기반)",
                "Type 3: 작품 비교제공",
                "Type 4: 배경지식 제공 (3문장)",
                "Type 5: 배경지식 + 느낌 묻기 (4문장)",
                "Type 6: 조형요소 + 타인의견 + 관계짓기 (4문장)"
            ],
            "touch_recognition": "작품 터치 시 객체 인식 → LLM 설명 생성"
        }
    }

@app.get("/ping", summary="서버 상태 확인")
def ping():
    """
    서버가 정상적으로 작동하는지 확인하는 간단한 핑 테스트입니다.
    """
    return {
        "message": "pong",
        "status": "healthy",
        "curation_types_loaded": curation_types is not None,
        "touch_recognition_loaded": touch_recognition is not None
    }

@app.post("/curation", summary="큐레이션 타입별 나레이션 생성")
def route_curation_endpoint(request: CurationRequest):
    """
    큐레이션 타입(1-6)에 따라 적절한 나레이션을 생성합니다.
    
    - **Type 1**: 작품 설명의 핵심 맥락 제공 (120~170자)
    - **Type 2**: 간단한 정보제공 (질문 선택적 - 질문이 있으면 먼저 간단히 답변 후 원래 응답)
    - **Type 3**: 간단한 비교제공 (연관 작품 필요, 질문 선택적)
    - **Type 4**: 작품 배경지식 제공 (3문장, 질문 선택적)
    - **Type 5**: 배경지식 + 관람자 느낌 묻기 (4문장, 질문 선택적)
    - **Type 6**: 조형요소 + 타인의견 + 관계짓기 (4문장, 질문 선택적)
    
    모든 타입에서 question 파라미터를 선택적으로 전달할 수 있으며, 
    질문이 있으면 먼저 간단히 답변한 후 원래 설계대로 응답합니다.
    """
    if not curation_types:
        raise HTTPException(status_code=500, detail="CurationTypes 초기화에 실패했습니다.")
    
    # 작품명 검증
    if request.art_name not in ARTWORK_NAMES:
        raise HTTPException(
            status_code=400, 
            detail=f"유효하지 않은 작품명입니다. 가능한 작품: {', '.join(ARTWORK_NAMES)}"
        )
    
    # 타입별 필수 파라미터 검증
    if request.curation_type == 3 and not request.related_artwork:
        raise HTTPException(status_code=400, detail="타입 3은 'related_artwork' 파라미터가 필요합니다.")
    
    # 연관 작품명 검증 (있는 경우)
    if request.related_artwork and request.related_artwork not in ARTWORK_NAMES:
        raise HTTPException(
            status_code=400,
            detail=f"유효하지 않은 연관 작품명입니다. 가능한 작품: {', '.join(ARTWORK_NAMES)}"
        )
    
    try:
        # route_curation 호출
        kwargs = {}
        if request.question:
            kwargs['question'] = request.question
        if request.related_artwork:
            kwargs['related_artwork'] = request.related_artwork
        
        response = curation_types.route_curation(
            curation_type=request.curation_type,
            art_name=request.art_name,
            memory=request.memory,
            viewed_artworks=request.viewed_artworks,
            **kwargs
        )
        
        return {
            "response": response
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"큐레이션 생성 중 오류 발생: {str(e)}")

@app.get("/artworks", summary="사용 가능한 작품 목록 조회")
def get_artwork_list():
    """
    시스템에서 사용 가능한 모든 작품 목록을 반환합니다.
    """
    return {"artworks": ARTWORK_NAMES}

@app.post("/touch", summary="터치 좌표로 객체 인식 및 설명 생성")
def touch_object_recognition(request: TouchRequest):
    """
    작품에서 사용자가 터치한 좌표(x, y)를 기반으로 해당 위치의 객체를 인식하고 
    LLM을 통해 객체에 대한 설명을 생성합니다.
    
    - **art_name**: 작품명 (한글)
    - **x**: x 좌표 (0~1 사이의 정규화된 값, 0=왼쪽, 1=오른쪽)
    - **y**: y 좌표 (0~1 사이의 정규화된 값, 0=위, 1=아래)
    
    반환값:
    - **found**: 객체를 찾았는지 여부
    - **object_name**: 객체 이름
    - **description**: LLM이 생성한 객체 설명
    """
    if not touch_recognition:
        raise HTTPException(status_code=500, detail="TouchRecognition 초기화에 실패했습니다.")
    
    if not curation_types:
        raise HTTPException(status_code=500, detail="CurationTypes 초기화에 실패했습니다.")
    
    # 작품명 검증
    if request.art_name not in ARTWORK_NAMES:
        raise HTTPException(
            status_code=400,
            detail=f"유효하지 않은 작품명입니다. 가능한 작품: {', '.join(ARTWORK_NAMES)}"
        )
    
    try:
        # 객체 인식
        print(f"🔍 객체 인식 시작: 작품={request.art_name}, 좌표=({request.x}, {request.y})")
        result = touch_recognition.find_object_at_position(
            art_name=request.art_name,
            x=request.x,
            y=request.y,
            coordinate_type="normalized"
        )
        
        if not result:
            print(f"❌ 객체를 찾을 수 없음")
            return {
                "found": False,
                "message": "해당 위치에 인식된 객체가 없습니다."
            }
        
        # 객체를 찾았으면 LLM으로 설명 생성
        mask_id = result['mask_id']
        object_name = result['name']
        object_description = result['description']
        art_name_en = ARTWORK_NAME_KR_TO_EN.get(request.art_name, request.art_name)
        print(f"✅ 객체 발견: ID={mask_id}, {object_name}")
        
        # LLM 프롬프트 생성
        prompt = f"""당신은 미술관 큐레이터입니다.

작품명: {art_name_en} (한국어 작품명: {request.art_name})
객체명: {object_name}
객체 정보: {object_description}

관람객이 작품에서 "{object_name}"을(를) 터치했습니다.
이 객체에 대해 간결하게 설명해주세요.

**분량 제약: 정확히 1문장**
- 반드시 한 문장으로만 작성하세요
- 객체의 핵심 의미와 역할을 간결하게 설명하세요
- "이 작품에서 <객체명>은" 형식으로 시작하세요

**중요: TTS(음성 합성)를 위한 출력 형식**
- 자연스러운 구어체로 작성하세요
- 따옴표, 괄호, 특수기호 등은 사용하지 마세요
- 음성으로 읽었을 때 자연스럽게 들리도록 작성하세요
- 문장의 종결어미는 반드시 "~니다" 체를 사용하세요 (예: ~합니다, ~입니다, ~습니다)
- 작품명을 언급할 때는 반드시 한국어 작품명 '{request.art_name}'을(를) 사용하고 따옴표 없이 자연스럽게 말하세요
- 객체명을 언급할 때도 따옴표 없이 자연스럽게 말하세요

예시: "이 작품에서 마르가리타 공주는 이 작품의 중심 인물로 당시 스페인 왕실의 공주이며 화가가 중앙에 배치하여 그녀의 중요성을 강조했습니다."
"""
        
        # LLM 호출
        print(f"🤖 LLM 설명 생성 시작...")
        llm_description = curation_types._get_llm_response(prompt)
        print(f"✅ LLM 설명 생성 완료: {llm_description[:50]}...")
        
        return {
            "found": True,
            "mask_id": mask_id,
            "object_name": object_name,
            "object_info": object_description,
            "description": llm_description,
            "art_name": request.art_name,
            "art_name_en": art_name_en
        }
    
    except Exception as e:
        print(f"❌ 에러 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"객체 인식 및 설명 생성 중 오류 발생: {str(e)}")

@app.post("/objects", summary="작품의 모든 객체 목록 조회")
def get_all_objects(request: ObjectListRequest):
    """
    특정 작품에 포함된 모든 객체의 목록을 반환합니다.
    
    - **art_name**: 작품명 (한글)
    
    반환값:
    - **art_name**: 작품명 (한글)
    - **art_name_en**: 작품명 (영어)
    - **object_count**: 객체 개수
    - **objects**: 객체 리스트 (mask_id, name, description)
    """
    if not touch_recognition:
        raise HTTPException(status_code=500, detail="TouchRecognition 초기화에 실패했습니다.")
    
    # 작품명 검증
    if request.art_name not in ARTWORK_NAMES:
        raise HTTPException(
            status_code=400,
            detail=f"유효하지 않은 작품명입니다. 가능한 작품: {', '.join(ARTWORK_NAMES)}"
        )
    
    try:
        # 모든 객체 가져오기
        objects = touch_recognition.get_all_objects(request.art_name)
        
        return {
            "art_name": request.art_name,
            "art_name_en": objects[0]["art_name_en"] if objects else "",
            "object_count": len(objects),
            "objects": objects
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"객체 목록 조회 중 오류 발생: {str(e)}")

# --- API 서버 실행 ---
if __name__ == "__main__":
    print("\n" + "🎨" * 30)
    print("Curation Types API 서버 시작")
    print("🎨" * 30)
    print(f"\n📍 서버 주소: http://localhost:14723")
    print(f"📍 웹 인터페이스: http://localhost:14723/")
    print(f"📍 API 문서: http://localhost:14723/docs")
    print(f"📍 ReDoc: http://localhost:14723/redoc\n")
    
    uvicorn.run(app, host="0.0.0.0", port=14723)