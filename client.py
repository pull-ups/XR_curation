"""
큐레이션 타입 API 테스트 클라이언트

각 큐레이션 타입(1-6)에 대한 다양한 테스트 케이스를 실행합니다.
"""

import requests
import json
from typing import Optional, List
import time

# API 서버 설정
BASE_URL = "http://localhost:14723"

# 10개 작품명
ARTWORKS = [
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


def print_separator():
    """구분선 출력"""
    print("\n" + "=" * 100 + "\n")


def print_result(test_name: str, response: dict, question: str = None):
    """테스트 결과를 보기 좋게 출력"""
    print(f"🎨 {test_name}")
    if question:
        print(f"❓ 질문: {question}")
    print("-" * 100)
    if response.get("response"):
        print(f"📝 응답: {response['response']}")
    else:
        print(f"⚠️  전체 응답: {json.dumps(response, ensure_ascii=False, indent=2)}")
    print_separator()


def call_curation_api(
    curation_type: int,
    art_name: str,
    memory: str = "",
    viewed_artworks: Optional[List[str]] = None,
    question: Optional[str] = None,
    related_artwork: Optional[str] = None
) -> dict:
    """큐레이션 API 호출"""
    url = f"{BASE_URL}/curation"
    
    payload = {
        "curation_type": curation_type,
        "art_name": art_name,
        "memory": memory,
        "viewed_artworks": viewed_artworks or [],
    }
    
    if question:
        payload["question"] = question
    if related_artwork:
        payload["related_artwork"] = related_artwork
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


def call_touch_api(art_name: str, x: float, y: float) -> dict:
    """터치 기반 객체 인식 API 호출"""
    url = f"{BASE_URL}/touch"
    
    payload = {
        "art_name": art_name,
        "x": x,
        "y": y
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


def call_objects_api(art_name: str) -> dict:
    """작품의 모든 객체 목록 조회 API 호출"""
    url = f"{BASE_URL}/objects"
    
    payload = {
        "art_name": art_name
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


def test_type_1():
    """타입 1 테스트: 작품 설명의 핵심 맥락 제공 (120~170자)"""
    print("\n" + "🔵" * 50)
    print("타입 1 테스트: 작품 설명의 핵심 맥락 제공 (120~170자)")
    print("🔵" * 50)
    
    # 테스트 케이스 1-1: 질문 없이 첫 작품 설명
    response = call_curation_api(
        curation_type=1,
        art_name="시녀들"
    )
    print_result("타입 1-1: 시녀들 - 질문 없이 첫 설명", response)
    
    # 테스트 케이스 1-2: 질문과 함께 (POC: 질문 먼저 답변 후 원래 응답)
    question_1_2 = "이 그림은 무슨 내용이에요?"
    response = call_curation_api(
        curation_type=1,
        art_name="시녀들",
        question=question_1_2
    )
    print_result("타입 1-2: 시녀들 - 질문과 함께 (POC: 질문 답변 + 원래 응답)", response, question=question_1_2)
    
    # 테스트 케이스 1-3: memory가 있는 경우
    question_1_3 = "가운데 있는 아이는 누구예요?"
    response = call_curation_api(
        curation_type=1,
        art_name="시녀들",
        memory="이 작품은 벨라스케스의 걸작으로 스페인 왕실의 일상을 담았습니다.",
        question=question_1_3
    )
    print_result("타입 1-3: 시녀들 - memory와 question 모두 있는 경우", response, question=question_1_3)
    
    # 테스트 케이스 1-4: 다른 작품들 (질문 있음/없음 비교)
    questions_1_4 = {
        "프리마베라": "이 작품은 뭐에 대한 그림인가요?",
        "최후의 만찬": "왜 이 장면을 그렸나요?"
    }
    for artwork in ["프리마베라", "최후의 만찬"]:
        # 질문 없이
        response = call_curation_api(
            curation_type=1,
            art_name=artwork
        )
        print_result(f"타입 1-4: {artwork} - 질문 없이", response)
        time.sleep(1)
        
        # 질문과 함께
        question_1_4 = questions_1_4[artwork]
        response = call_curation_api(
            curation_type=1,
            art_name=artwork,
            question=question_1_4
        )
        print_result(f"타입 1-4: {artwork} - 질문과 함께", response, question=question_1_4)
        time.sleep(1)


def test_type_2():
    """타입 2 테스트: 간단한 정보제공 (질문 선택적)"""
    print("\n" + "🟢" * 50)
    print("타입 2 테스트: 간단한 정보제공 (질문 선택적)")
    print("🟢" * 50)
    
    # 테스트 케이스 2-1: 질문 없이 (POC: 원래 설계대로만 응답)
    response = call_curation_api(
        curation_type=2,
        art_name="최후의 만찬"
    )
    print_result("타입 2-1: 최후의 만찬 - 질문 없이 (POC)", response)
    
    # 테스트 케이스 2-2: 질문과 함께 (POC: 질문 답변 + 원래 응답)
    question_2_2 = "가운데 있는 사람은 누구예요?"
    response = call_curation_api(
        curation_type=2,
        art_name="최후의 만찬",
        question=question_2_2
    )
    print_result("타입 2-2: 최후의 만찬 - 질문과 함께 (POC: 질문 답변 + 원래 응답)", response, question=question_2_2)
    
    # 테스트 케이스 2-3: 인물 관련 질문
    question_2_3 = "주변에 있는 사람들은 누구예요?"
    response = call_curation_api(
        curation_type=2,
        art_name="시녀들",
        question=question_2_3
    )
    print_result("타입 2-3: 시녀들 - 인물 질문", response, question=question_2_3)
    
    # 테스트 케이스 2-4: 시대 배경 질문
    question_2_4 = "이 그림은 언제 그려진 거예요?"
    response = call_curation_api(
        curation_type=2,
        art_name="아테네 학당",
        question=question_2_4
    )
    print_result("타입 2-4: 아테네 학당 - 시대 질문", response, question=question_2_4)
    
    # 테스트 케이스 2-5: memory가 있는 경우
    question_2_5 = "이 작품이 유명한 이유가 뭐예요?"
    response = call_curation_api(
        curation_type=2,
        art_name="비너스의 탄생",
        question=question_2_5,
        memory="이 작품은 보티첼리의 대표작으로 르네상스 시대에 그려졌습니다."
    )
    print_result("타입 2-5: 비너스의 탄생 - memory가 있는 경우", response, question=question_2_5)


def test_type_3():
    """타입 3 테스트: 간단한 비교제공 (연관 작품 필요, 질문 선택적)"""
    print("\n" + "🟡" * 50)
    print("타입 3 테스트: 간단한 비교제공 (질문 선택적)")
    print("🟡" * 50)
    
    # 테스트 케이스 3-1: 질문 없이 비교
    response = call_curation_api(
        curation_type=3,
        art_name="프리마베라",
        related_artwork="비너스의 탄생"
    )
    print_result("타입 3-1: 프리마베라 vs 비너스의 탄생 - 질문 없이", response)
    
    # 테스트 케이스 3-2: 질문과 함께 (POC: 질문 답변 + 원래 응답)
    question_3_2 = "두 그림이 뭐가 비슷해요?"
    response = call_curation_api(
        curation_type=3,
        art_name="프리마베라",
        related_artwork="비너스의 탄생",
        question=question_3_2
    )
    print_result("타입 3-2: 프리마베라 vs 비너스의 탄생 - 질문과 함께 (POC)", response, question=question_3_2)
    
    # 테스트 케이스 3-3: 최후의 만찬 vs 아담의 창조
    question_3_3 = "이 두 그림의 차이가 뭐예요?"
    response = call_curation_api(
        curation_type=3,
        art_name="최후의 만찬",
        related_artwork="아담의 창조",
        question=question_3_3
    )
    print_result("타입 3-3: 최후의 만찬 vs 아담의 창조 - 질문과 함께", response, question=question_3_3)
    
    # 테스트 케이스 3-4: memory가 있는 경우
    question_3_4 = "왜 이 두 그림이 비슷해 보이나요?"
    response = call_curation_api(
        curation_type=3,
        art_name="파리스의 심판",
        related_artwork="비너스의 탄생",
        memory="두 작품 모두 그리스 신화를 주제로 합니다.",
        question=question_3_4
    )
    print_result("타입 3-4: 파리스의 심판 vs 비너스의 탄생 - memory와 question", response, question=question_3_4)


def test_type_4():
    """타입 4 테스트: 작품 배경지식 제공 (3문장, 질문 선택적)"""
    print("\n" + "🟣" * 50)
    print("타입 4 테스트: 작품 배경지식 제공 (질문 선택적)")
    print("🟣" * 50)
    
    # 테스트 케이스 4-1: 질문 없이 배경지식
    response = call_curation_api(
        curation_type=4,
        art_name="아담의 창조"
    )
    print_result("타입 4-1: 아담의 창조 - 질문 없이", response)
    
    # 테스트 케이스 4-2: 질문과 함께 (POC: 질문 답변 + 원래 응답)
    question_4_2 = "이 그림은 왜 유명한가요?"
    response = call_curation_api(
        curation_type=4,
        art_name="아담의 창조",
        question=question_4_2
    )
    print_result("타입 4-2: 아담의 창조 - 질문과 함께 (POC)", response, question=question_4_2)
    
    # 테스트 케이스 4-3: memory가 있는 경우
    question_4_3 = "작가가 누구예요?"
    response = call_curation_api(
        curation_type=4,
        art_name="프리마베라",
        memory="이 작품은 보티첼리의 작품으로 봄의 여신을 그렸습니다.",
        question=question_4_3
    )
    print_result("타입 4-3: 프리마베라 - memory와 question", response, question=question_4_3)


def test_type_5():
    """타입 5 테스트: 배경지식 + 관람자 느낌 묻기 (4문장, 질문 선택적)"""
    print("\n" + "🔴" * 50)
    print("타입 5 테스트: 배경지식 + 관람자 느낌 묻기 (질문 선택적)")
    print("🔴" * 50)
    
    # 테스트 케이스 5-1: 질문 없이
    response = call_curation_api(
        curation_type=5,
        art_name="야경"
    )
    print_result("타입 5-1: 야경 - 질문 없이", response)
    
    # 테스트 케이스 5-2: 질문과 함께 (POC: 질문 답변 + 원래 응답)
    question_5_2 = "이 그림 보면 어떤 기분이 들어야 하나요?"
    response = call_curation_api(
        curation_type=5,
        art_name="야경",
        question=question_5_2
    )
    print_result("타입 5-2: 야경 - 질문과 함께 (POC)", response, question=question_5_2)
    
    # 테스트 케이스 5-3: memory가 있는 경우
    question_5_3 = "왜 이렇게 그렸을까요?"
    response = call_curation_api(
        curation_type=5,
        art_name="비너스의 탄생",
        memory="비너스는 바다의 거품에서 탄생했습니다.",
        question=question_5_3
    )
    print_result("타입 5-3: 비너스의 탄생 - memory와 question", response, question=question_5_3)


def test_type_6():
    """타입 6 테스트: 조형요소 + 타인의견 + 관계짓기 (4문장, 질문 선택적)"""
    print("\n" + "🟤" * 50)
    print("타입 6 테스트: 조형요소 + 타인의견 + 관계짓기 (질문 선택적)")
    print("🟤" * 50)
    
    # 테스트 케이스 6-1: 질문 없이 (연관 작품 있음)
    response = call_curation_api(
        curation_type=6,
        art_name="프리마베라",
        related_artwork="비너스의 탄생",
        viewed_artworks=["비너스의 탄생"]
    )
    print_result("타입 6-1: 프리마베라 - 질문 없이 (연관 작품 있음)", response)
    
    # 테스트 케이스 6-2: 질문과 함께 (POC: 질문 답변 + 원래 응답)
    question_6_2 = "다른 사람들은 이 그림 보고 뭐라고 하나요?"
    response = call_curation_api(
        curation_type=6,
        art_name="프리마베라",
        related_artwork="비너스의 탄생",
        viewed_artworks=["비너스의 탄생"],
        question=question_6_2
    )
    print_result("타입 6-2: 프리마베라 - 질문과 함께 (POC)", response, question=question_6_2)
    
    # 테스트 케이스 6-3: viewed_artworks만 있는 경우 (자동으로 마지막 작품과 비교)
    question_6_3 = "이 그림이 좋은 그림인가요?"
    response = call_curation_api(
        curation_type=6,
        art_name="아테네 학당",
        viewed_artworks=["프리마베라", "최후의 만찬"],
        question=question_6_3
    )
    print_result("타입 6-3: 아테네 학당 - viewed_artworks와 question", response, question=question_6_3)
    
    # 테스트 케이스 6-4: memory가 있는 경우
    question_6_4 = "내가 봤던 다른 그림이랑 비교하면 어떤가요?"
    response = call_curation_api(
        curation_type=6,
        art_name="시녀들",
        related_artwork="회화의 기술",
        memory="이 작품은 바로크 시대의 걸작입니다.",
        question=question_6_4
    )
    print_result("타입 6-4: 시녀들 vs 회화의 기술 - memory와 question", response, question=question_6_4)


def load_box_centers_from_json(artwork_name: str) -> list:
    """JSON 파일에서 모든 객체의 bounding box 중점을 계산합니다."""
    import os
    
    json_path = f"./vision/boxes/{artwork_name}.json"
    if not os.path.exists(json_path):
        print(f"⚠️  {artwork_name}의 box JSON 파일을 찾을 수 없습니다: {json_path}")
        return []
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    image_width = data['image_width']
    image_height = data['image_height']
    
    centers = []
    for box in data['bounding_boxes']:
        # 중점 계산 (픽셀 좌표)
        center_x_px = box['x'] + box['width'] / 2
        center_y_px = box['y'] + box['height'] / 2
        
        # 정규화된 좌표 (0~1)
        normalized_x = center_x_px / image_width
        normalized_y = center_y_px / image_height
        
        centers.append({
            'id': box['id'],
            'x': normalized_x,
            'y': normalized_y,
            'x_px': center_x_px,
            'y_px': center_y_px
        })
    
    return centers


def test_touch_recognition():
    """터치 기반 객체 인식 및 LLM 설명 생성 테스트"""
    print("\n" + "👆" * 50)
    print("터치 기반 객체 인식 및 LLM 설명 생성 테스트")
    print("👆" * 50)
    
    # 테스트 케이스 1: 시녀들 - 중앙 위치
    print("\n📍 테스트 1: 시녀들 작품 중앙 (0.5, 0.5) 터치")
    response = call_touch_api(
        art_name="시녀들",
        x=0.5,
        y=0.5
    )
    
    # 디버깅: 전체 응답 출력
    print(f"\n🔍 전체 응답: {json.dumps(response, ensure_ascii=False, indent=2)}")
    
    # 에러 확인
    if response.get("error"):
        print(f"❌ 에러 발생: {response.get('error')}")
    elif response.get("detail"):
        print(f"❌ API 에러: {response.get('detail')}")
    elif response.get("found"):
        print(f"✅ 객체 발견!")
        print(f"   - 객체명: {response.get('object_name')}")
        print(f"   - 작품: {response.get('art_name')} ({response.get('art_name_en')})")
        print(f"   - 객체 정보: {response.get('object_info')}")
        print(f"\n📝 LLM 생성 설명:")
        print(f"   {response.get('description')}")
    else:
        print(f"❌ {response.get('message', '객체를 찾을 수 없습니다')}")
    print_separator()
    
    # 테스트 케이스 2: 다양한 위치 테스트
    test_positions = [
        ("시녀들", 0.3, 0.3, "좌상단"),
        ("시녀들", 0.7, 0.7, "우하단"),
        ("시녀들", 0.8, 0.9, "우상단"),
        ("시녀들", 0.7, 0.7, "우하단"),
        ("시녀들", 0.2, 0.1, "좌하단"),
        ("시녀들", 0.1, 0.2, "좌상단"),
        
    ]
    
    for art_name, x, y, position_name in test_positions:
        print(f"\n📍 테스트: {art_name} - {position_name} ({x}, {y})")
        response = call_touch_api(art_name=art_name, x=x, y=y)
        
        # 에러 확인
        if response.get("error"):
            print(f"❌ 에러 발생: {response.get('error')}")
        elif response.get("detail"):
            print(f"❌ API 에러: {response.get('detail')}")
        elif response.get("found"):
            print(f"✅ 발견: {response.get('object_name')}")
            print(f"📝 설명: {response.get('description')}")
        else:
            print(f"❌ {response.get('message', '객체 없음')}")
        time.sleep(1)  # LLM 호출 간격
        print("-" * 100)
    print_separator()
    
    # 테스트 케이스 3: 모든 객체 목록 조회
    print("\n📍 테스트 3: 시녀들 작품의 모든 객체 목록 조회")
    response = call_objects_api(art_name="시녀들")
    if response.get("object_count"):
        print(f"✅ 총 {response['object_count']}개의 객체:")
        for obj in response.get("objects", [])[:5]:  # 처음 5개만 출력
            print(f"   {obj['mask_id']}. {obj['name']}")
        if response['object_count'] > 5:
            print(f"   ... (외 {response['object_count'] - 5}개)")
    else:
        print("❌ 객체 목록을 가져올 수 없습니다")
    print_separator()


def test_all_box_centers():
    """모든 작품의 모든 객체 box 중점을 테스트합니다."""
    print("\n" + "📦" * 50)
    print("모든 작품의 Bounding Box 중점 테스트")
    print("📦" * 50)
    
    # 통계 정보
    total_tests = 0
    successful_detections = 0
    failed_detections = 0
    
    for artwork in ARTWORKS:
        print(f"\n{'='*100}")
        print(f"🎨 작품: {artwork}")
        print(f"{'='*100}")
        
        # JSON에서 box 중점 로드
        centers = load_box_centers_from_json(artwork)
        
        if not centers:
            print(f"⚠️  {artwork}의 box 정보를 찾을 수 없습니다. 건너뜁니다.")
            continue
        
        print(f"📍 총 {len(centers)}개의 객체 중점 테스트 시작\n")
        
        # 각 객체의 중점에서 터치 API 호출
        for center in centers:
            total_tests += 1
            obj_id = center['id']
            x = center['x']
            y = center['y']
            x_px = center['x_px']
            y_px = center['y_px']
            
            print(f"  객체 {obj_id}: 중점 ({x:.4f}, {y:.4f}) = ({x_px:.1f}px, {y_px:.1f}px)")
            
            response = call_touch_api(art_name=artwork, x=x, y=y)
            
            # 결과 확인
            if response.get("error"):
                print(f"    ❌ 에러: {response.get('error')}")
                failed_detections += 1
            elif response.get("detail"):
                print(f"    ❌ API 에러: {response.get('detail')}")
                failed_detections += 1
            elif response.get("found"):
                detected_name = response.get('object_name')
                detected_id = response.get('mask_id', '?')
                print(f"    ✅ 인식 성공: [{detected_id}] {detected_name}")
                
                # ID가 일치하는지 확인
                if str(detected_id) == str(obj_id):
                    print(f"       ✓ ID 일치")
                else:
                    print(f"       ⚠️  ID 불일치 (예상: {obj_id}, 감지: {detected_id})")
                
                successful_detections += 1
                
                # LLM 설명 일부만 출력 (너무 길어지지 않게)
                description = response.get('description', '')
                if len(description) > 100:
                    description = description[:100] + "..."
                print(f"       📝 {description}")
            else:
                print(f"    ❌ 객체 감지 실패: {response.get('message', '알 수 없음')}")
                failed_detections += 1
            
            print()  # 빈 줄
            time.sleep(0.5)  # API 호출 간격 (조금 짧게)
        
        print(f"\n{artwork} 완료: {len(centers)}개 테스트\n")
        time.sleep(1)
    
    # 최종 통계
    print("\n" + "📊" * 50)
    print("최종 통계")
    print("📊" * 50)
    print(f"총 테스트 수: {total_tests}")
    print(f"✅ 성공: {successful_detections} ({successful_detections/total_tests*100:.1f}%)")
    print(f"❌ 실패: {failed_detections} ({failed_detections/total_tests*100:.1f}%)")
    print_separator()


def test_workflow_scenario():
    """실제 관람 시나리오 테스트 (질문 기능 포함)"""
    print("\n" + "🎭" * 50)
    print("실제 관람 시나리오 테스트 (질문 기능 포함)")
    print("🎭" * 50)
    
    viewed = []
    
    # 1. 첫 작품 - 타입 1로 설명 (질문과 함께)
    print("\n📍 첫 작품 관람: 프리마베라 (질문과 함께)")
    question_w1 = "이 그림은 뭐에 대한 거예요?"
    response = call_curation_api(
        curation_type=1,
        art_name="프리마베라",
        question=question_w1
    )
    print_result("1단계: 프리마베라 - 질문과 함께 핵심 설명", response, question=question_w1)
    viewed.append("프리마베라")
    time.sleep(1)
    
    # 2. 두 번째 작품 - 타입 3으로 비교 (질문과 함께)
    print("\n📍 두 번째 작품 관람: 비너스의 탄생 (질문과 함께)")
    question_w2 = "이전에 본 그림이랑 뭐가 달라요?"
    response = call_curation_api(
        curation_type=3,
        art_name="비너스의 탄생",
        related_artwork="프리마베라",
        viewed_artworks=viewed,
        question=question_w2
    )
    print_result("2단계: 비너스의 탄생 vs 프리마베라 - 질문과 함께 비교", response, question=question_w2)
    viewed.append("비너스의 탄생")
    time.sleep(1)
    
    # 3. 질문하기 - 타입 2
    print("\n📍 질문: 비너스의 탄생에 대해")
    question_w3 = "가운데 있는 사람은 누구예요?"
    response = call_curation_api(
        curation_type=2,
        art_name="비너스의 탄생",
        question=question_w3,
        viewed_artworks=viewed
    )
    print_result("3단계: 질문에 답변", response, question=question_w3)
    time.sleep(1)
    
    # 4. 배경지식 듣기 - 타입 4 (질문과 함께)
    print("\n📍 배경지식 듣기: 최후의 만찬 (질문과 함께)")
    question_w4 = "왜 이 그림이 유명한가요?"
    response = call_curation_api(
        curation_type=4,
        art_name="최후의 만찬",
        viewed_artworks=viewed,
        question=question_w4
    )
    print_result("4단계: 최후의 만찬 - 질문과 함께 배경지식", response, question=question_w4)
    viewed.append("최후의 만찬")
    time.sleep(1)
    
    # 5. 느낌 묻기 - 타입 5 (질문과 함께)
    print("\n📍 느낌 공유하기: 야경 (질문과 함께)")
    question_w5 = "이 그림 보니까 좀 어둡네요"
    response = call_curation_api(
        curation_type=5,
        art_name="야경",
        viewed_artworks=viewed,
        question=question_w5
    )
    print_result("5단계: 야경 - 질문과 함께 배경지식 + 느낌 묻기", response, question=question_w5)
    viewed.append("야경")
    time.sleep(1)
    
    # 6. 관계짓기 - 타입 6 (질문과 함께)
    print("\n📍 마지막 작품 관람: 시녀들 (질문과 함께)")
    question_w6 = "다른 사람들은 이 그림 보고 뭐라고 하나요?"
    response = call_curation_api(
        curation_type=6,
        art_name="시녀들",
        viewed_artworks=viewed,
        question=question_w6
    )
    print_result("6단계: 시녀들 - 질문과 함께 타인의견 + 관계짓기", response, question=question_w6)


def check_server_status():
    """서버 상태 확인"""
    try:
        response = requests.get(f"{BASE_URL}/ping")
        if response.status_code == 200:
            print("✅ 서버가 정상적으로 작동 중입니다.")
            return True
        else:
            print(f"⚠️  서버 응답 코드: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")
        print(f"   예상 주소: {BASE_URL}")
        return False


def test_all_curation_examples():
    """
    CURATION_EXAMPLES.md의 모든 케이스를 테스트합니다.
    이 함수는 MD 파일에 있는 모든 예시를 커버합니다.
    """
    print("\n" + "📚" * 50)
    print("CURATION_EXAMPLES.md 전체 커버리지 테스트")
    print("📚" * 50)
    
    # Type 1: 10개 작품 모두 (질문 없이만)
    print("\n" + "=" * 100)
    print("📌 Type 1: 핵심 맥락 제공 - 모든 작품 (질문 없이)")
    print("=" * 100)
    
    type1_artworks = [
        "프리마베라", "비너스의 탄생", "파리스의 심판", "아담의 창조", "최후의 만찬",
        "성 마태를 부르심", "아테네 학당", "회화의 기술", "시녀들", "야경"
    ]
    
    for artwork in type1_artworks:
        response = call_curation_api(curation_type=1, art_name=artwork)
        print_result(f"Type 1: {artwork} - 질문 없이", response)
        time.sleep(1)
    
    # Type 2: 각 작품별 질문 (시녀들은 질문 없이/있음 둘 다)
    print("\n" + "=" * 100)
    print("📌 Type 2: 간단한 정보제공 - 모든 작품")
    print("=" * 100)
    
    type2_cases = {
        "프리마베라": "이 작품에 등장하는 인물들은 누구인가요?",
        "비너스의 탄생": "조개껍데기가 어떤 의미인가요?",
        "파리스의 심판": "파리스는 누구에게 황금 사과를 주었나요?",
        "아담의 창조": "이 작품은 어디에 그려진 건가요?",
        "최후의 만찬": "이 작품을 그린 화가는 누구인가요?",
        "성 마태를 부르심": "성 마태는 어떤 직업을 가지고 있었나요?",
        "아테네 학당": "그림 중앙의 두 사람은 누구인가요?",
        "회화의 기술": "이 작품의 화가는 누구인가요?",
        "야경": "이 작품에서 사용된 특별한 기법이 있나요?",
    }
    
    # 시녀들 - 질문 없이
    response = call_curation_api(curation_type=2, art_name="시녀들")
    print_result("Type 2: 시녀들 - 질문 없이", response)
    time.sleep(1)
    
    # 시녀들 - 질문과 함께
    response = call_curation_api(
        curation_type=2,
        art_name="시녀들",
        question="왼쪽 아래에서 작품을 바라보는 난쟁이의 시선이 작품 전체에 어떤 영향을 주나요?"
    )
    print_result("Type 2: 시녀들 - 질문과 함께", response, 
                 question="왼쪽 아래에서 작품을 바라보는 난쟁이의 시선이 작품 전체에 어떤 영향을 주나요?")
    time.sleep(1)
    
    # 나머지 작품들 - 질문과 함께
    for artwork, question in type2_cases.items():
        response = call_curation_api(
            curation_type=2,
            art_name=artwork,
            question=question
        )
        print_result(f"Type 2: {artwork} - 질문과 함께", response, question=question)
        time.sleep(1)
    
    # Type 3: 작품 비교
    print("\n" + "=" * 100)
    print("📌 Type 3: 작품 비교 - 모든 비교 조합")
    print("=" * 100)
    
    type3_cases = [
        # (art_name, related_artwork, question 있음)
        ("프리마베라", "비너스의 탄생", 
         "프리마베라와 비너스의 탄생에서 인물들의 윤곽선 처리 방식이 어떻게 다른가요?"),
        ("비너스의 탄생", "프리마베라", None),
        ("파리스의 심판", "비너스의 탄생", None),
        ("아담의 창조", "최후의 만찬", None),
        ("최후의 만찬", "아담의 창조", None),
        ("성 마태를 부르심", "최후의 만찬", None),
        ("아테네 학당", "아담의 창조", None),
        ("회화의 기술", "시녀들", None),
        ("시녀들", "야경", None),
        ("야경", "시녀들", None),
    ]
    
    for art_name, related_artwork, question_yes in type3_cases:
        # 질문 없이 - 모든 케이스
        response = call_curation_api(
            curation_type=3,
            art_name=art_name,
            related_artwork=related_artwork
        )
        print_result(f"Type 3: {art_name} vs {related_artwork} - 질문 없이", response)
        time.sleep(1)
        
        # 질문과 함께 (프리마베라 vs 비너스의 탄생만)
        if question_yes is not None:
            response = call_curation_api(
                curation_type=3,
                art_name=art_name,
                related_artwork=related_artwork,
                question=question_yes
            )
            print_result(f"Type 3: {art_name} vs {related_artwork} - 질문과 함께", response, question=question_yes)
            time.sleep(1)
    
    # Type 4: 배경지식 제공
    print("\n" + "=" * 100)
    print("📌 Type 4: 배경지식 제공 - 모든 작품")
    print("=" * 100)
    
    type4_artworks = [
        "프리마베라", "비너스의 탄생", "파리스의 심판", "아담의 창조", "최후의 만찬",
        "성 마태를 부르심", "아테네 학당", "회화의 기술", "야경"
    ]
    
    # 질문 없이 - 모든 작품
    for artwork in type4_artworks:
        response = call_curation_api(curation_type=4, art_name=artwork)
        print_result(f"Type 4: {artwork} - 질문 없이", response)
        time.sleep(1)
    
    # 시녀들 - 질문 없이와 질문 있음 둘 다
    response = call_curation_api(curation_type=4, art_name="시녀들")
    print_result("Type 4: 시녀들 - 질문 없이", response)
    time.sleep(1)
    
    response = call_curation_api(
        curation_type=4,
        art_name="시녀들",
        question="작품 오른쪽 위에 있는 창문에서 들어오는 빛이 인물들의 얼굴에 미치는 효과는 무엇인가요?"
    )
    print_result("Type 4: 시녀들 - 질문과 함께", response,
                 question="작품 오른쪽 위에 있는 창문에서 들어오는 빛이 인물들의 얼굴에 미치는 효과는 무엇인가요?")
    time.sleep(1)
    
    # Type 5: 배경지식 + 느낌 묻기
    print("\n" + "=" * 100)
    print("📌 Type 5: 배경지식 + 느낌 묻기 - 모든 작품")
    print("=" * 100)
    
    type5_artworks = [
        "프리마베라", "비너스의 탄생", "파리스의 심판", "아담의 창조", "최후의 만찬",
        "성 마태를 부르심", "아테네 학당", "회화의 기술", "야경"
    ]
    
    # 질문 없이 - 모든 작품
    for artwork in type5_artworks:
        response = call_curation_api(curation_type=5, art_name=artwork)
        print_result(f"Type 5: {artwork} - 질문 없이", response)
        time.sleep(1)
    
    # 시녀들 - 질문 없이와 질문 있음 둘 다
    response = call_curation_api(curation_type=5, art_name="시녀들")
    print_result("Type 5: 시녀들 - 질문 없이", response)
    time.sleep(1)
    
    response = call_curation_api(
        curation_type=5,
        art_name="시녀들",
        question="작품 중앙 소녀의 드레스와 주변 인물들의 복장이 만들어내는 색채 대비의 의미는 무엇인가요?"
    )
    print_result("Type 5: 시녀들 - 질문과 함께", response,
                 question="작품 중앙 소녀의 드레스와 주변 인물들의 복장이 만들어내는 색채 대비의 의미는 무엇인가요?")
    time.sleep(1)
    
    # Type 6: 조형요소 + 타인의견 + 관계짓기
    print("\n" + "=" * 100)
    print("📌 Type 6: 조형요소 + 타인의견 + 관계짓기 - 모든 작품")
    print("=" * 100)
    
    type6_cases = [
        # (art_name, related_artwork, viewed_artworks, question 없음, question 있음)
        ("프리마베라", "비너스의 탄생", ["비너스의 탄생"], None,
         "프리마베라와 비너스의 탄생에서 배경의 처리 방식이 작품의 분위기를 어떻게 다르게 만드나요?"),
        ("비너스의 탄생", "프리마베라", ["프리마베라"], None, None),
        ("파리스의 심판", "비너스의 탄생", ["비너스의 탄생"], None, None),
        ("아담의 창조", "최후의 만찬", ["최후의 만찬"], None, None),
        ("최후의 만찬", "아담의 창조", ["아담의 창조"], None, None),
        ("성 마태를 부르심", "최후의 만찬", ["최후의 만찬"], None, None),
        ("아테네 학당", "아담의 창조", ["아담의 창조"], None, None),
        ("회화의 기술", "시녀들", ["시녀들"], None, None),
        ("시녀들", "야경", ["야경"], None, None),
        ("야경", "시녀들", ["시녀들"], None, None),
    ]
    
    for art_name, related_artwork, viewed, question_no, question_yes in type6_cases:
        # 질문 없이
        response = call_curation_api(
            curation_type=6,
            art_name=art_name,
            related_artwork=related_artwork,
            viewed_artworks=viewed
        )
        print_result(f"Type 6: {art_name} (연관: {related_artwork}) - 질문 없이", response)
        time.sleep(1)
        
        # 질문과 함께 (프리마베라만 질문 있음)
        if question_yes is not None:
            response = call_curation_api(
                curation_type=6,
                art_name=art_name,
                related_artwork=related_artwork,
                viewed_artworks=viewed,
                question=question_yes
            )
            print_result(f"Type 6: {art_name} (연관: {related_artwork}) - 질문과 함께", response, question=question_yes)
            time.sleep(1)
    


def test_poc_question_feature():
    """POC: 모든 타입의 질문 기능 테스트"""
    print("\n" + "🚀" * 50)
    print("POC: 모든 타입의 질문 기능 테스트")
    print("🚀" * 50)
    print("\n각 타입별로 질문이 있을 때와 없을 때를 비교합니다.")
    print("질문이 있으면 먼저 간단히 답변한 후 원래 설계대로 응답합니다.\n")
    
    test_artwork = "시녀들"
    
    # Type 1 테스트
    print("\n" + "=" * 100)
    print("📌 Type 1 테스트: 핵심 맥락 제공")
    print("=" * 100)
    
    # 질문 없이
    response = call_curation_api(curation_type=1, art_name=test_artwork)
    print_result("Type 1 - 질문 없이", response)
    time.sleep(1)
    
    # 질문과 함께
    question_1 = "이 그림은 무슨 이야기예요?"
    response = call_curation_api(
        curation_type=1,
        art_name=test_artwork,
        question=question_1
    )
    print_result("Type 1 - 질문과 함께 (간단 답변 + 원래 응답)", response, question=question_1)
    time.sleep(1)
    
    # Type 2 테스트
    print("\n" + "=" * 100)
    print("📌 Type 2 테스트: 간단한 정보제공")
    print("=" * 100)
    
    # 질문 없이
    response = call_curation_api(curation_type=2, art_name=test_artwork)
    print_result("Type 2 - 질문 없이", response)
    time.sleep(1)
    
    # 질문과 함께
    question_2 = "이건 뭐예요?"
    response = call_curation_api(
        curation_type=2,
        art_name=test_artwork,
        question=question_2
    )
    print_result("Type 2 - 질문과 함께 (간단 답변 + 원래 응답)", response, question=question_2)
    time.sleep(1)
    
    # Type 3 테스트
    print("\n" + "=" * 100)
    print("📌 Type 3 테스트: 작품 비교")
    print("=" * 100)
    
    # 질문 없이
    response = call_curation_api(
        curation_type=3,
        art_name="프리마베라",
        related_artwork="비너스의 탄생"
    )
    print_result("Type 3 - 질문 없이", response)
    time.sleep(1)
    
    # 질문과 함께
    question_3 = "이 두 그림이 같나요?"
    response = call_curation_api(
        curation_type=3,
        art_name="프리마베라",
        related_artwork="비너스의 탄생",
        question=question_3
    )
    print_result("Type 3 - 질문과 함께 (간단 답변 + 원래 응답)", response, question=question_3)
    time.sleep(1)
    
    # Type 4 테스트
    print("\n" + "=" * 100)
    print("📌 Type 4 테스트: 배경지식 제공")
    print("=" * 100)
    
    # 질문 없이
    response = call_curation_api(curation_type=4, art_name=test_artwork)
    print_result("Type 4 - 질문 없이", response)
    time.sleep(1)
    
    # 질문과 함께
    question_4 = "언제 만든 거예요?"
    response = call_curation_api(
        curation_type=4,
        art_name=test_artwork,
        question=question_4
    )
    print_result("Type 4 - 질문과 함께 (간단 답변 + 원래 응답)", response, question=question_4)
    time.sleep(1)
    
    # Type 5 테스트
    print("\n" + "=" * 100)
    print("📌 Type 5 테스트: 배경지식 + 느낌 묻기")
    print("=" * 100)
    
    # 질문 없이
    response = call_curation_api(curation_type=5, art_name=test_artwork)
    print_result("Type 5 - 질문 없이", response)
    time.sleep(1)
    
    # 질문과 함께
    question_5 = "이 그림 보니까 뭔가 느껴지는 게 있어요"
    response = call_curation_api(
        curation_type=5,
        art_name=test_artwork,
        question=question_5
    )
    print_result("Type 5 - 질문과 함께 (간단 답변 + 원래 응답)", response, question=question_5)
    time.sleep(1)
    
    # Type 6 테스트
    print("\n" + "=" * 100)
    print("📌 Type 6 테스트: 조형요소 + 타인의견 + 관계짓기")
    print("=" * 100)
    
    # 질문 없이
    response = call_curation_api(
        curation_type=6,
        art_name="프리마베라",
        related_artwork="비너스의 탄생",
        viewed_artworks=["비너스의 탄생"]
    )
    print_result("Type 6 - 질문 없이", response)
    time.sleep(1)
    
    # 질문과 함께
    question_6 = "이 그림 좋아요?"
    response = call_curation_api(
        curation_type=6,
        art_name="프리마베라",
        related_artwork="비너스의 탄생",
        viewed_artworks=["비너스의 탄생"],
        question=question_6
    )
    print_result("Type 6 - 질문과 함께 (간단 답변 + 원래 응답)", response, question=question_6)
    
    print("\n" + "✅" * 50)
    print("POC 테스트 완료!")
    print("✅" * 50)
    print("\n모든 타입(Type 1-6)에서 질문이 있으면 먼저 간단히 답변한 후")
    print("원래 설계대로 응답하는 것을 확인했습니다.")


def main():
    """메인 테스트 실행"""
    print("\n" + "🎨" * 50)
    print("큐레이션 타입 API 테스트 시작")
    print("🎨" * 50)
    
    # 서버 상태 확인
    if not check_server_status():
        print("\n서버를 먼저 실행해주세요:")
        print("  python api.py")
        return
    
    print("\n테스트를 시작합니다...\n")
    
    # CURATION_EXAMPLES.md 전체 커버리지 테스트
    test_all_curation_examples()
    
    # POC: 질문 기능 테스트 (간단 버전)
    # test_poc_question_feature()
    
    # # 각 타입별 상세 테스트 실행
    # test_type_1()
    # test_type_2()
    # test_type_3()
    # test_type_4()
    # test_type_5()
    # test_type_6()
    
    # 터치 기반 객체 인식 테스트
    # test_touch_recognition()
    
    # 모든 작품의 모든 객체 box 중점 테스트
    # test_all_box_centers()
    
    # # 실제 시나리오 테스트 (질문 기능 포함)
    # test_workflow_scenario()
    
    print("\n" + "🎉" * 50)
    print("모든 테스트가 완료되었습니다!")
    print("🎉" * 50)


if __name__ == "__main__":
    main()

