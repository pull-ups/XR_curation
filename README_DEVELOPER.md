# 큐레이션 타입 API - 개발자 문서

## 목차
- [개요](#개요)
- [API 엔드포인트](#api-엔드포인트)
- [데이터 모델](#데이터-모델)
- [큐레이션 타입별 API 명세](#큐레이션-타입별-api-명세)
  - [타입 1: 핵심설명](#타입-1-핵심설명)
  - [타입 2: 질문응답 flat-1 (정보제공)](#타입-2-질문응답-flat-1-정보제공)
  - [타입 3: 질문응답 flat-2 (단순비교)](#타입-3-질문응답-flat-2-단순비교)
  - [타입 4: 질문응답 deep-0 (정보제공 심화)](#타입-4-질문응답-deep-0-정보제공-심화)
  - [타입 5: 질문응답 deep-1 (정보제공 및 인상 나누기)](#타입-5-질문응답-deep-1-정보제공-및-인상-나누기)
  - [타입 6: 질문응답 deep-2 (연관작품 읽기 및 나만의 작품읽기)](#타입-6-질문응답-deep-2-연관작품-읽기-및-나만의-작품읽기)
- [터치 기반 객체 인식 API](#터치-기반-객체-인식-api)
  - [POST /touch: 객체 인식 및 설명 생성](#post-touch-객체-인식-및-설명-생성)
  - [POST /objects: 객체 목록 조회](#post-objects-객체-목록-조회)
- [에러 처리](#에러-처리)
- [사용 예시](#사용-예시)

---

## 개요

큐레이션 타입 API는 미술관 NPC의 6가지 발화 타입을 제공하는 RESTful API입니다.

### 기술 스택
- **Framework**: FastAPI
- **LLM**: OpenAI GPT-4o-mini
- **Language**: Python 3.10+

### 서버 정보
- **Base URL**: `http://localhost:14723`
- **API Docs**: `http://localhost:14723/docs`
- **ReDoc**: `http://localhost:14723/redoc`

---

## API 엔드포인트

### 기본 엔드포인트

#### `GET /`
API 정보 조회

**Response**:
```json
{
  "name": "Curation Types API",
  "version": "1.0.0",
  "description": "큐레이션 타입별 나레이션 생성 API",
  "endpoints": { ... }
}
```

#### `GET /ping`
서버 상태 확인

**Response**:
```json
{
  "message": "pong",
  "status": "healthy",
  "curation_types_loaded": true
}
```

#### `GET /artworks`
사용 가능한 작품 목록 조회

**Response**:
```json
{
  "artworks": [
    "프리마베라",
    "비너스의 탄생",
    "파리스의 심판",
    "아담의 창조",
    "최후의 만찬",
    "성 마태를 부르심",
    "아테네 학당",
    "회화의 기술",
    "시녀들",
    "야경"
  ]
}
```

#### `POST /curation`
큐레이션 나레이션 생성 (메인 엔드포인트)

---

## 데이터 모델

### Request Model: `CurationRequest`

```python
class CurationRequest(BaseModel):
    curation_type: int  # 1-6, required
    art_name: str  # required
    memory: str = ""  # optional, default=""
    viewed_artworks: Optional[List[str]] = None  # optional
    question: Optional[str] = None  # 타입 2 전용
    related_artwork: Optional[str] = None  # 타입 3, 6 전용
```

#### 필드 설명

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `curation_type` | `int` | ✅ | 큐레이션 타입 (1-6) |
| `art_name` | `str` | ✅ | 작품명 (10개 중 하나) |
| `memory` | `str` | ❌ | 이전 대화 기록 (중복 방지용) |
| `viewed_artworks` | `List[str]` | ❌ | 관람한 작품 목록 |
| `question` | `str` | 조건부 | 타입 2에서 필수 |
| `related_artwork` | `str` | 조건부 | 타입 3에서 필수, 타입 6에서 선택 |

### Response Model

```python
{
  "response": str  # LLM 생성 텍스트
}
```

### Error Response

```python
{
  "detail": str  # 에러 메시지
}
```

---

## 큐레이션 타입별 API 명세

### 타입 1: 핵심설명

**목적**: 작품의 핵심 주제와 맥락을 간결하게 설명

#### API Request

```python
POST /curation
{
  "curation_type": 1,
  "art_name": "시녀들",
  "memory": "",  # optional
  "viewed_artworks": []  # optional
}
```

#### Response Format
- **타입**: `string`
- **길이**: 120~170자
- **구조**: 조형적 특징 + 작품 의미

#### 필수 파라미터
- `curation_type`: `1`
- `art_name`: 유효한 작품명

#### 선택 파라미터
- `memory`: 이전 설명 (중복 방지)
- `viewed_artworks`: 관람 이력

#### Example Response
```json
{
  "response": "시녀들은 관찰자와 피관찰자 간의 시선의 교차를 탐구합니다. 복잡한 구도로 인물들이 상호작용하며, 색채에서 고요한 톤과 대비를 통해 깊이감을 표현합니다..."
}
```

#### Python 클라이언트 예시
```python
import requests

response = requests.post(
    "http://localhost:14723/curation",
    json={
        "curation_type": 1,
        "art_name": "시녀들"
    }
)
print(response.json()["response"])
```

---

### 타입 2: 질문응답 flat-1 (정보제공)

**목적**: 사용자 질문에 답하고 추가 선택지 제공

#### API Request

```python
POST /curation
{
  "curation_type": 2,
  "art_name": "최후의 만찬",
  "question": "이 작품을 그린 화가는 누구인가요?",  # required
  "memory": "",  # optional
  "viewed_artworks": []  # optional
}
```

#### Response Format
- **타입**: `string`
- **구조**: 질문 확인 1문장 + 답변 1-2문장 + 선택지 1문장
- **최대**: 3문장

#### 필수 파라미터
- `curation_type`: `2`
- `art_name`: 유효한 작품명
- `question`: 사용자 질문 문자열

#### 선택 파라미터
- `memory`: 이전 설명
- `viewed_artworks`: 관람 이력

#### Example Response
```json
{
  "response": "작가가 궁금하시군요. 이 작품은 레오나르도 다 빈치가 그렸습니다. 작품의 배경에 대해 더 듣고 싶으신가요, 아니면 인물들의 의미를 알고 싶으신가요?"
}
```

#### Validation
- `question` 없이 타입 2 호출 시 → `400 Bad Request`

---

### 타입 3: 질문응답 flat-2 (단순비교)

**목적**: 두 작품의 공통점과 차이점 비교

#### API Request

```python
POST /curation
{
  "curation_type": 3,
  "art_name": "프리마베라",
  "related_artwork": "비너스의 탄생",  # required
  "memory": "",  # optional
  "viewed_artworks": ["비너스의 탄생"]  # optional
}
```

#### Response Format
- **타입**: `string`
- **구조**: 공통점 1구 + 차이점 1구 (1문장) + 선택지 1문장
- **총**: 2문장

#### 필수 파라미터
- `curation_type`: `3`
- `art_name`: 유효한 작품명
- `related_artwork`: 비교할 작품명

#### 선택 파라미터
- `memory`: 이전 설명
- `viewed_artworks`: 관람 이력

#### Data Source
- 작품 비교 데이터: `assets/llm/transformed_pair.json`
- 키 형식: `"{작품1}-{작품2}"` 또는 `"{작품2}-{작품1}"`

#### Example Response
```json
{
  "response": "프리마베라와 비너스의 탄생은 모두 보티첼리가 그린 신화 주제 작품이지만, 프리마베라는 여러 인물이 복잡하게 구성된 반면 비너스의 탄생은 중심 인물에 집중합니다. 더 자세히 알아보시겠습니까?"
}
```

#### Validation
- `related_artwork` 없이 타입 3 호출 시 → `400 Bad Request`
- 유효하지 않은 작품명 → `400 Bad Request`

---

### 타입 4: 질문응답 deep-0 (정보제공 심화)

**목적**: 작품의 시대적 배경, 사조, 작가 정보 제공

#### API Request

```python
POST /curation
{
  "curation_type": 4,
  "art_name": "아담의 창조",
  "memory": "",  # optional
  "viewed_artworks": []  # optional
}
```

#### Response Format
- **타입**: `string`
- **구조**: 정확히 3문장
- **내용**: 제작 시기, 예술 사조, 작가 정보, 시대적/철학적 컨텍스트

#### 필수 파라미터
- `curation_type`: `4`
- `art_name`: 유효한 작품명

#### 선택 파라미터
- `memory`: 이전 설명
- `viewed_artworks`: 관람 이력

#### Example Response
```json
{
  "response": "이 작품은 1508년부터 1512년 사이에 미켈란젤로에 의해 바티칸 시스티나 성당 천장에 그려졌습니다. 르네상스 시대를 대표하는 걸작으로, 인간 중심의 세계관과 신의 창조를 동시에 표현합니다. 당시 교황 율리오 2세의 의뢰로 제작되었으며, 성서의 창세기를 시각화한 대규모 프레스코화의 일부입니다."
}
```

---

### 타입 5: 질문응답 deep-1 (정보제공 및 인상 나누기)

**목적**: 배경지식 제공 후 관람자의 느낌 유도

#### API Request

```python
POST /curation
{
  "curation_type": 5,
  "art_name": "야경",
  "memory": "",  # optional
  "viewed_artworks": []  # optional
}
```

#### Response Format
- **타입**: `string`
- **구조**: 정확히 4문장
  - 배경지식 3문장
  - 느낌 묻는 질문 1문장

#### 필수 파라미터
- `curation_type`: `5`
- `art_name`: 유효한 작품명

#### 선택 파라미터
- `memory`: 이전 설명
- `viewed_artworks`: 관람 이력

#### Example Response
```json
{
  "response": "야경은 1642년 렘브란트가 그린 작품으로 네덜란드 바로크 시대를 대표합니다. 암스테르담 시민 방위대의 모습을 담았으며, 극적인 명암 대비 기법인 키아로스쿠로를 사용했습니다. 당시 네덜란드는 황금시대로 불리며 경제적 번영과 문화적 발전을 이루었습니다. 이 작품의 역동적인 구도와 빛의 사용이 당신에게는 어떤 느낌을 줍니까?"
}
```

---

### 타입 6: 질문응답 deep-2 (연관작품 읽기 및 나만의 작품읽기)

**목적**: 타인의견, 조형요소, 연관작품 비교 후 관람자 경험 연결 유도

#### API Request

```python
POST /curation
{
  "curation_type": 6,
  "art_name": "프리마베라",
  "related_artwork": "비너스의 탄생",  # optional
  "memory": "",  # optional
  "viewed_artworks": ["비너스의 탄생"]  # optional
}
```

#### Response Format
- **타입**: `string`
- **구조**: 정확히 4문장
  - 타인의견/일반 해석 1문장
  - 조형 특징 + (있으면) 연관작품 비교
  - 관람자 경험 연결 질문 1문장

#### 필수 파라미터
- `curation_type`: `6`
- `art_name`: 유효한 작품명

#### 선택 파라미터
- `related_artwork`: 비교할 작품 (없으면 `viewed_artworks`에서 자동 선택)
- `memory`: 이전 설명
- `viewed_artworks`: 관람 이력

#### Auto-selection Logic
```python
if not related_artwork and viewed_artworks:
    previous_works = [art for art in viewed_artworks if art != art_name]
    related_artwork = previous_works[-1] if previous_works else None
```

#### Data Source
- 작품 비교 데이터: `assets/llm/transformed_pair.json` (있으면 사용)

#### Example Response
```json
{
  "response": "많은 관람객들이 프리마베라의 화려한 색채와 섬세한 인물 표현에서 봄의 생명력을 느낀다고 말합니다. 비너스의 탄생과 비교하면 두 작품 모두 신화를 다루지만 프리마베라는 더 복잡한 구성과 풍부한 상징을 담고 있습니다. 당신은 이러한 생명력이 당신의 경험이나 가치관과도 연결된다고 느끼십니까?"
}
```

---

## 터치 기반 객체 인식 API

### POST /touch: 객체 인식 및 설명 생성

**목적**: 작품의 특정 좌표를 터치하면 해당 위치의 객체를 인식하고 LLM이 생성한 설명을 제공

#### API Request

```python
POST /touch
{
  "art_name": "시녀들",
  "x": 0.5,  # required, 0~1 사이의 정규화된 x 좌표
  "y": 0.5   # required, 0~1 사이의 정규화된 y 좌표
}
```

#### 좌표 시스템

- **정규화된 좌표 (0~1)**: 화면 크기에 독립적
  - `x`: 0 (왼쪽) ~ 1 (오른쪽)
  - `y`: 0 (위) ~ 1 (아래)

#### Response Format (객체 발견)

```json
{
  "found": true,
  "object_name": "마르가리타 공주",
  "object_info": "작품 중앙의 주인공으로 당시 스페인 왕실의 공주입니다.",
  "description": "마르가리타 공주는 이 작품의 중심 인물로 당시 스페인 왕실의 공주이며 화가가 중앙에 배치하여 그녀의 중요성을 강조했습니다.",
  "art_name": "시녀들",
  "art_name_en": "Las Meninas"
}
```

#### Response Format (객체 없음)

```json
{
  "found": false,
  "message": "해당 위치에 인식된 객체가 없습니다."
}
```

#### 필수 파라미터
- `art_name`: 유효한 작품명
- `x`: 0~1 사이의 float 값
- `y`: 0~1 사이의 float 값

#### LLM 설명 생성 규칙
- **분량**: 정확히 1문장
- **내용**: 객체의 핵심 의미와 역할
- **톤**: 구어체, ~니다 체
- **TTS 최적화**: 따옴표, 괄호, 특수기호 제외

#### Data Source
- 마스크 데이터: `vision/masks/{작품명}/array/*.npy`
- 객체 정보: `vision/mask_annotation/{작품명}.json`

#### Python 클라이언트 예시

```python
import requests

response = requests.post(
    "http://localhost:14723/touch",
    json={
        "art_name": "시녀들",
        "x": 0.5,  # 중앙
        "y": 0.5
    }
)

result = response.json()
if result["found"]:
    print(f"객체: {result['object_name']}")
    print(f"설명: {result['description']}")
else:
    print(result["message"])
```

#### Validation
- 유효하지 않은 작품명 → `400 Bad Request`
- x, y 범위 초과 (0~1 벗어남) → `422 Unprocessable Entity`
- 객체 인식 실패 → `found: false` 반환 (에러 아님)

---

### POST /objects: 객체 목록 조회

**목적**: 작품에 포함된 모든 객체의 목록을 조회

#### API Request

```python
POST /objects
{
  "art_name": "시녀들"
}
```

#### Response Format

```json
{
  "art_name": "시녀들",
  "art_name_en": "Las Meninas",
  "object_count": 11,
  "objects": [
    {
      "mask_id": 1,
      "name": "마르가리타 공주",
      "description": "작품 중앙의 주인공...",
      "art_name": "시녀들",
      "art_name_en": "Las Meninas"
    },
    {
      "mask_id": 2,
      "name": "시녀 1",
      "description": "...",
      "art_name": "시녀들",
      "art_name_en": "Las Meninas"
    }
    // ... 더 많은 객체
  ]
}
```

#### 필수 파라미터
- `art_name`: 유효한 작품명

#### 사용 시나리오
1. 작품의 모든 객체 미리보기
2. 터치 가능한 영역 확인
3. 객체 목록 UI 구성

#### Python 클라이언트 예시

```python
import requests

response = requests.post(
    "http://localhost:14723/objects",
    json={"art_name": "시녀들"}
)

result = response.json()
print(f"총 {result['object_count']}개의 객체:")
for obj in result['objects']:
    print(f"  {obj['mask_id']}. {obj['name']}")
```

---

## 에러 처리

### HTTP Status Codes

| Code | 상황 | 설명 |
|------|------|------|
| `200` | Success | 정상 처리 |
| `400` | Bad Request | 잘못된 파라미터 (작품명, 필수값 누락 등) |
| `500` | Internal Server Error | 서버 오류 (LLM API 오류 등) |

### Error Examples

#### 유효하지 않은 작품명
```json
{
  "detail": "유효하지 않은 작품명입니다. 가능한 작품: 프리마베라, 비너스의 탄생, ..."
}
```

#### 필수 파라미터 누락 (타입 2)
```json
{
  "detail": "타입 2는 'question' 파라미터가 필요합니다."
}
```

#### 필수 파라미터 누락 (타입 3)
```json
{
  "detail": "타입 3은 'related_artwork' 파라미터가 필요합니다."
}
```

#### CurationTypes 초기화 실패
```json
{
  "detail": "CurationTypes 초기화에 실패했습니다."
}
```

---

## 사용 예시

### Python (requests)

```python
import requests

BASE_URL = "http://localhost:14723"

# 타입 1: 핵심 맥락
response = requests.post(
    f"{BASE_URL}/curation",
    json={
        "curation_type": 1,
        "art_name": "시녀들"
    }
)
print(response.json()["response"])

# 타입 2: 질문 답변
response = requests.post(
    f"{BASE_URL}/curation",
    json={
        "curation_type": 2,
        "art_name": "최후의 만찬",
        "question": "이 작품을 그린 화가는 누구인가요?"
    }
)
print(response.json()["response"])

# 타입 3: 비교
response = requests.post(
    f"{BASE_URL}/curation",
    json={
        "curation_type": 3,
        "art_name": "프리마베라",
        "related_artwork": "비너스의 탄생"
    }
)
print(response.json()["response"])
```

### cURL

```bash
# 타입 1
curl -X POST "http://localhost:14723/curation" \
  -H "Content-Type: application/json" \
  -d '{
    "curation_type": 1,
    "art_name": "시녀들"
  }'

# 타입 2
curl -X POST "http://localhost:14723/curation" \
  -H "Content-Type: application/json" \
  -d '{
    "curation_type": 2,
    "art_name": "최후의 만찬",
    "question": "이 작품을 그린 화가는 누구인가요?"
  }'
```

### JavaScript (fetch)

```javascript
// 타입 1
fetch('http://localhost:14723/curation', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    curation_type: 1,
    art_name: '시녀들'
  })
})
.then(response => response.json())
.then(data => console.log(data.response));

// 타입 6 (연관작품 자동 선택)
fetch('http://localhost:14723/curation', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    curation_type: 6,
    art_name: '프리마베라',
    viewed_artworks: ['비너스의 탄생', '파리스의 심판']
  })
})
.then(response => response.json())
.then(data => console.log(data.response));
```

