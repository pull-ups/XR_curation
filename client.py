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


def print_result(test_name: str, response: dict):
    """테스트 결과를 보기 좋게 출력"""
    print(f"🎨 {test_name}")
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
    
    # 테스트 케이스 1-1: 첫 작품 설명
    response = call_curation_api(
        curation_type=1,
        art_name="시녀들"
    )
    print_result("타입 1-1: 시녀들 - 첫 설명", response)
    
    # 테스트 케이스 1-2: memory가 있는 경우
    response = call_curation_api(
        curation_type=1,
        art_name="시녀들",
        memory="이 작품은 벨라스케스의 걸작으로 스페인 왕실의 일상을 담았습니다."
    )
    print_result("타입 1-2: 시녀들 - memory가 있는 경우", response)
    
    # 테스트 케이스 1-3: 다른 작품들
    for artwork in ["프리마베라", "최후의 만찬", "야경"]:
        response = call_curation_api(
            curation_type=1,
            art_name=artwork
        )
        print_result(f"타입 1-3: {artwork} - 첫 설명", response)
        time.sleep(1)  # API 호출 간격


def test_type_2():
    """타입 2 테스트: 간단한 정보제공 (질문 필요)"""
    print("\n" + "🟢" * 50)
    print("타입 2 테스트: 간단한 정보제공 (최대 3문장)")
    print("🟢" * 50)
    
    # 테스트 케이스 2-1: 작가 관련 질문
    response = call_curation_api(
        curation_type=2,
        art_name="최후의 만찬",
        question="이 작품을 그린 화가는 누구인가요?"
    )
    print_result("타입 2-1: 최후의 만찬 - 작가 질문", response)
    
    # 테스트 케이스 2-2: 인물 관련 질문
    response = call_curation_api(
        curation_type=2,
        art_name="시녀들",
        question="그림 가운데 있는 소녀는 누구인가요?"
    )
    print_result("타입 2-2: 시녀들 - 인물 질문", response)
    
    # 테스트 케이스 2-3: 시대 배경 질문
    response = call_curation_api(
        curation_type=2,
        art_name="아테네 학당",
        question="이 작품은 언제 그려졌나요?"
    )
    print_result("타입 2-3: 아테네 학당 - 시대 질문", response)
    
    # 테스트 케이스 2-4: 기법 관련 질문
    response = call_curation_api(
        curation_type=2,
        art_name="야경",
        question="이 작품에서 사용된 특별한 기법이 있나요?"
    )
    print_result("타입 2-4: 야경 - 기법 질문", response)
    
    # 테스트 케이스 2-5: memory가 있는 경우
    response = call_curation_api(
        curation_type=2,
        art_name="비너스의 탄생",
        question="비너스는 어떻게 탄생했나요?",
        memory="이 작품은 보티첼리의 대표작으로 르네상스 시대에 그려졌습니다."
    )
    print_result("타입 2-5: 비너스의 탄생 - memory가 있는 경우", response)


def test_type_3():
    """타입 3 테스트: 간단한 비교제공 (연관 작품 필요)"""
    print("\n" + "🟡" * 50)
    print("타입 3 테스트: 간단한 비교제공")
    print("🟡" * 50)
    
    # 테스트 케이스 3-1: 프리마베라 vs 비너스의 탄생
    response = call_curation_api(
        curation_type=3,
        art_name="프리마베라",
        related_artwork="비너스의 탄생"
    )
    print_result("타입 3-1: 프리마베라 vs 비너스의 탄생", response)
    
    # 테스트 케이스 3-2: 최후의 만찬 vs 아담의 창조
    response = call_curation_api(
        curation_type=3,
        art_name="최후의 만찬",
        related_artwork="아담의 창조"
    )
    print_result("타입 3-2: 최후의 만찬 vs 아담의 창조", response)
    
    # 테스트 케이스 3-3: 아테네 학당 vs 회화의 기술
    response = call_curation_api(
        curation_type=3,
        art_name="아테네 학당",
        related_artwork="회화의 기술"
    )
    print_result("타입 3-3: 아테네 학당 vs 회화의 기술", response)
    
    # 테스트 케이스 3-4: 시녀들 vs 야경
    response = call_curation_api(
        curation_type=3,
        art_name="시녀들",
        related_artwork="야경"
    )
    print_result("타입 3-4: 시녀들 vs 야경", response)
    
    # 테스트 케이스 3-5: memory가 있는 경우
    response = call_curation_api(
        curation_type=3,
        art_name="파리스의 심판",
        related_artwork="비너스의 탄생",
        memory="두 작품 모두 그리스 신화를 주제로 합니다."
    )
    print_result("타입 3-5: 파리스의 심판 vs 비너스의 탄생 - memory가 있는 경우", response)


def test_type_4():
    """타입 4 테스트: 작품 배경지식 제공 (3문장)"""
    print("\n" + "🟣" * 50)
    print("타입 4 테스트: 작품 배경지식 제공 (정확히 3문장)")
    print("🟣" * 50)
    
    # 테스트 케이스 4-1: 아담의 창조
    response = call_curation_api(
        curation_type=4,
        art_name="아담의 창조"
    )
    print_result("타입 4-1: 아담의 창조 - 배경지식", response)
    
    # 테스트 케이스 4-2: 성 마태를 부르심
    response = call_curation_api(
        curation_type=4,
        art_name="성 마태를 부르심"
    )
    print_result("타입 4-2: 성 마태를 부르심 - 배경지식", response)
    
    # 테스트 케이스 4-3: memory가 있는 경우
    response = call_curation_api(
        curation_type=4,
        art_name="프리마베라",
        memory="이 작품은 보티첼리의 작품으로 봄의 여신을 그렸습니다."
    )
    print_result("타입 4-3: 프리마베라 - memory가 있는 경우", response)
    
    # 테스트 케이스 4-4: 다른 작품들
    for artwork in ["회화의 기술", "파리스의 심판"]:
        response = call_curation_api(
            curation_type=4,
            art_name=artwork
        )
        print_result(f"타입 4-4: {artwork} - 배경지식", response)
        time.sleep(1)


def test_type_5():
    """타입 5 테스트: 배경지식 + 관람자 느낌 묻기 (4문장)"""
    print("\n" + "🔴" * 50)
    print("타입 5 테스트: 배경지식 + 관람자 느낌 묻기 (정확히 4문장)")
    print("🔴" * 50)
    
    # 테스트 케이스 5-1: 야경
    response = call_curation_api(
        curation_type=5,
        art_name="야경"
    )
    print_result("타입 5-1: 야경 - 배경지식 + 질문", response)
    
    # 테스트 케이스 5-2: 시녀들
    response = call_curation_api(
        curation_type=5,
        art_name="시녀들"
    )
    print_result("타입 5-2: 시녀들 - 배경지식 + 질문", response)
    
    # 테스트 케이스 5-3: memory가 있는 경우
    response = call_curation_api(
        curation_type=5,
        art_name="비너스의 탄생",
        memory="비너스는 바다의 거품에서 탄생했습니다."
    )
    print_result("타입 5-3: 비너스의 탄생 - memory가 있는 경우", response)
    
    # 테스트 케이스 5-4: 다른 작품들
    for artwork in ["최후의 만찬", "아테네 학당"]:
        response = call_curation_api(
            curation_type=5,
            art_name=artwork
        )
        print_result(f"타입 5-4: {artwork} - 배경지식 + 질문", response)
        time.sleep(1)


def test_type_6():
    """타입 6 테스트: 조형요소 + 타인의견 + 관계짓기 (4문장)"""
    print("\n" + "🟤" * 50)
    print("타입 6 테스트: 조형요소 + 타인의견 + 관계짓기 (정확히 4문장)")
    print("🟤" * 50)
    
    # 테스트 케이스 6-1: 연관 작품 있음
    response = call_curation_api(
        curation_type=6,
        art_name="프리마베라",
        related_artwork="비너스의 탄생",
        viewed_artworks=["비너스의 탄생"]
    )
    print_result("타입 6-1: 프리마베라 - 연관 작품 있음", response)
    
    # 테스트 케이스 6-2: 연관 작품 없음
    response = call_curation_api(
        curation_type=6,
        art_name="야경"
    )
    print_result("타입 6-2: 야경 - 연관 작품 없음", response)
    
    # 테스트 케이스 6-3: viewed_artworks만 있는 경우 (자동으로 마지막 작품과 비교)
    response = call_curation_api(
        curation_type=6,
        art_name="아테네 학당",
        viewed_artworks=["프리마베라", "최후의 만찬"]
    )
    print_result("타입 6-3: 아테네 학당 - viewed_artworks 자동 선택", response)
    
    # 테스트 케이스 6-4: memory가 있는 경우
    response = call_curation_api(
        curation_type=6,
        art_name="시녀들",
        related_artwork="회화의 기술",
        memory="이 작품은 바로크 시대의 걸작입니다."
    )
    print_result("타입 6-4: 시녀들 vs 회화의 기술 - memory가 있는 경우", response)
    
    # 테스트 케이스 6-5: 다양한 조합
    pairs = [
        ("성 마태를 부르심", "아담의 창조"),
        ("파리스의 심판", "최후의 만찬"),
    ]
    
    for art, related in pairs:
        response = call_curation_api(
            curation_type=6,
            art_name=art,
            related_artwork=related
        )
        print_result(f"타입 6-5: {art} vs {related}", response)
        time.sleep(1)


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
    """실제 관람 시나리오 테스트"""
    print("\n" + "🎭" * 50)
    print("실제 관람 시나리오 테스트")
    print("🎭" * 50)
    
    viewed = []
    
    # 1. 첫 작품 - 타입 1로 설명
    print("\n📍 첫 작품 관람: 프리마베라")
    response = call_curation_api(
        curation_type=1,
        art_name="프리마베라"
    )
    print_result("1단계: 프리마베라 핵심 설명", response)
    viewed.append("프리마베라")
    time.sleep(1)
    
    # 2. 두 번째 작품 - 타입 3으로 비교
    print("\n📍 두 번째 작품 관람: 비너스의 탄생")
    response = call_curation_api(
        curation_type=3,
        art_name="비너스의 탄생",
        related_artwork="프리마베라",
        viewed_artworks=viewed
    )
    print_result("2단계: 비너스의 탄생 vs 프리마베라 비교", response)
    viewed.append("비너스의 탄생")
    time.sleep(1)
    
    # 3. 질문하기 - 타입 2
    print("\n📍 질문: 비너스의 탄생에 대해")
    response = call_curation_api(
        curation_type=2,
        art_name="비너스의 탄생",
        question="조개껍데기가 어떤 의미인가요?",
        viewed_artworks=viewed
    )
    print_result("3단계: 질문에 답변", response)
    time.sleep(1)
    
    # 4. 배경지식 듣기 - 타입 4
    print("\n📍 배경지식 듣기: 최후의 만찬")
    response = call_curation_api(
        curation_type=4,
        art_name="최후의 만찬",
        viewed_artworks=viewed
    )
    print_result("4단계: 최후의 만찬 배경지식", response)
    viewed.append("최후의 만찬")
    time.sleep(1)
    
    # 5. 느낌 묻기 - 타입 5
    print("\n📍 느낌 공유하기: 야경")
    response = call_curation_api(
        curation_type=5,
        art_name="야경",
        viewed_artworks=viewed
    )
    print_result("5단계: 야경 배경지식 + 느낌 묻기", response)
    viewed.append("야경")
    time.sleep(1)
    
    # 6. 관계짓기 - 타입 6
    print("\n📍 마지막 작품 관람: 시녀들")
    response = call_curation_api(
        curation_type=6,
        art_name="시녀들",
        viewed_artworks=viewed
    )
    print_result("6단계: 시녀들 - 타인의견 + 관계짓기", response)


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
    
    # # 각 타입별 테스트 실행
    # test_type_1()
    # test_type_2()
    # test_type_3()
    # test_type_4()
    # test_type_5()
    # test_type_6()
    
    # 터치 기반 객체 인식 테스트
    # test_touch_recognition()
    
    # 모든 작품의 모든 객체 box 중점 테스트
    test_all_box_centers()
    
    # # 실제 시나리오 테스트
    # test_workflow_scenario()
    
    print("\n" + "🎉" * 50)
    print("모든 테스트가 완료되었습니다!")
    print("🎉" * 50)


if __name__ == "__main__":
    main()

