import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional

# 기존 CuratorNPC 클래스를 가져옵니다.
# curation_npc.py가 동일한 디렉터리 또는 파이썬 경로에 있어야 합니다.
from curation_npc import CuratorNPC

# --- Pydantic 모델 정의 ---
# 요청 본문의 데이터 구조를 정의합니다.

class ArtworkAttractionRequest(BaseModel):
    current_section: int
    viewed_artworks: List[str]

class SectionNarrationRequest(BaseModel):
    current_section: int
    viewed_artworks: Optional[List[str]] = None

class ArtworkNarrationRequest(BaseModel):
    art_name: str
    memory: str = ""
    viewed_artworks: Optional[List[str]] = None

class RagQuestionRequest(BaseModel):
    question: str
    art_name: str

# --- FastAPI 앱 생성 ---
app = FastAPI(
    title="Curator NPC API",
    description="미술관 큐레이터 NPC의 다양한 기능을 API로 제공합니다.",
    version="1.0.0"
)

# --- CuratorNPC 인스턴스 생성 ---
# curation_npc.py의 main 함수에 있던 경로를 사용합니다.
# 실제 환경에 맞게 경로를 수정해야 할 수 있습니다.
try:
    section_data_file = './assets/llm/section_level_data.json'
    prompts_directory = './prompts'
    documents_directory = './assets/llm/document'
    common_and_different_path= './assets/llm/transformed_pair.json'

    curator = CuratorNPC(
        section_data_path=section_data_file, 
        common_and_different_path=common_and_different_path,
        prompts_dir=prompts_directory,
        documents_dir=documents_directory
    )
except FileNotFoundError as e:
    print(f"오류: 초기화에 필요한 파일을 찾을 수 없습니다. 경로를 확인하세요. {e}")
    curator = None
except Exception as e:
    print(f"CuratorNPC 초기화 중 오류 발생: {e}")
    curator = None

# --- API 엔드포인트 정의 ---

@app.get("/ping", summary="서버 상태 확인")
def ping():
    """
    서버가 정상적으로 작동하는지 확인하는 간단한 핑 테스트입니다.
    """
    return {"message": "pong", "status": "healthy"}

@app.post("/section-narration", summary="섹션 안내 나레이션 생성")
def get_section_narration(request: SectionNarrationRequest):
    """
    현재 섹션에 대한 안내 메시지를 생성합니다.
    - **current_section**: 현재 섹션 번호 (1 또는 2)
    - **viewed_artworks**: (선택) 이전에 감상한 작품 목록
    """
    if not curator:
        raise HTTPException(status_code=500, detail="서버 초기화에 실패했습니다.")
    
    previous_work = request.viewed_artworks[-1] if request.viewed_artworks else None
    return {"response": curator.get_section_narration(request.current_section, previous_work)}

@app.post("/artwork-attraction", summary="작품 흥미 유발 나레이션 생성")
def get_artwork_attraction_narration(request: ArtworkAttractionRequest):
    """
    현재 섹션에서 아직 관람하지 않은 작품에 대한 흥미 유발 질문을 생성합니다.
    """
    if not curator:
        raise HTTPException(status_code=500, detail="서버 초기화에 실패했습니다.")
    return {"response": curator.get_artwork_attraction_narration(request.current_section, request.viewed_artworks)}

@app.post("/artwork-narration", summary="작품 설명 나레이션 생성")
def get_artwork_narration(request: ArtworkNarrationRequest):
    """
    작품에 대한 설명을 생성합니다. 이전 감상 작품이 있으면 비교 설명합니다.
    """
    if not curator:
        raise HTTPException(status_code=500, detail="서버 초기화에 실패했습니다.")
    return {"response": curator.get_artwork_narration(request.art_name, request.memory, request.viewed_artworks)}

@app.post("/rag-question", summary="RAG 기반 질의응답")
def answer_question_with_rag(request: RagQuestionRequest):
    """
    작품에 대한 사용자의 질문에 RAG를 사용하여 답변합니다.
    """
    if not curator:
        raise HTTPException(status_code=500, detail="서버 초기화에 실패했습니다.")
    if not curator.rag_chains:
        raise HTTPException(status_code=503, detail="RAG 시스템을 사용할 수 없습니다.")
    
    answer = curator.answer_question_with_rag(request.question, request.art_name)
    return {"response": answer}

# --- API 서버 실행 ---
# 이 파일을 직접 실행할 때 uvicorn 서버를 구동합니다.
if __name__ == "__main__":
    # host="0.0.0.0"으로 설정하면 외부에서도 접속 가능합니다.
    uvicorn.run(app, host="0.0.0.0", port=8000)