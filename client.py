import requests
import json

# API 서버의 기본 URL
# BASE_URL = "http://0.0.0.0:8000"
BASE_URL = "http://127.0.0.1:14723"

def print_request_response(title, url, data, response):
    """요청과 응답을 예쁘게 출력하는 함수"""
    print(f"--- {title} ---")
    print(f"요청 URL: {url}")
    print("요청 내용:")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    print()
    
    if response.status_code == 200:
        print("✅ 요청 성공!")
        print("응답 내용:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    else:
        print(f"❌ 오류 발생! (상태 코드: {response.status_code})")
        try:
            print("오류 내용:")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        except json.JSONDecodeError:
            print(response.text)
    print("\n" + "="*50 + "\n")


def test_api():
    """모든 API 엔드포인트를 테스트합니다."""

    # 1. 섹션 안내 나레이션 테스트 (POST /section-narration)
    # 시나리오 1: 첫 입장
    data1 = {"current_section": 1}
    url1 = f"{BASE_URL}/section-narration"
    response1 = requests.post(url1, json=data1)
    print_request_response("1. 초기 섹션 안내", url1, data1, response1)

    # 시나리오 2: 이전 작품 감상 후 섹션 이동
    data2 = {"current_section": 2, "viewed_artworks": ["프리마베라"]}
    url2 = f"{BASE_URL}/section-narration"
    response2 = requests.post(url2, json=data2)
    print_request_response("2. 이전 작품 감상 후 섹션 안내", url2, data2, response2)


    # 2. 작품 흥미 유발 나레이션 테스트 (POST /artwork-attraction)
    payload3 = {
        "current_section": 1,
        "viewed_artworks": ["프리마베라"]
    }
    url3 = f"{BASE_URL}/artwork-attraction"
    response3 = requests.post(url3, json=payload3)
    print_request_response("3. 작품 흥미 유발", url3, payload3, response3)


    # 3. 작품 설명 나레이션 테스트 (POST /artwork-narration)
    # 시나리오 1: 첫 작품, 첫 설명
    payload4_1 = {
        "art_name": "비너스의 탄생",
        "memory": "",
        "viewed_artworks": []
    }
    url4_1 = f"{BASE_URL}/artwork-narration"
    response4_1 = requests.post(url4_1, json=payload4_1)
    print_request_response("4-1. 작품 설명 (첫 작품, 첫 설명)", url4_1, payload4_1, response4_1)

    # 시나리오 2: 다른 작품 감상 후, 첫 설명
    payload4_2 = {
        "art_name": "비너스의 탄생",
        "memory": "",
        "viewed_artworks": ["프리마베라"]
    }
    url4_2 = f"{BASE_URL}/artwork-narration"
    response4_2 = requests.post(url4_2, json=payload4_2)
    print_request_response("4-2. 작품 설명 (이전 감상 이력 있음)", url4_2, payload4_2, response4_2)


    # 4. RAG 기반 질의응답 테스트 (POST /rag-question)
    payload5 = {
        "question": "그림에서 가운데 있는 소녀는 누구야?",
        "art_name": "시녀들"
    }
    url5 = f"{BASE_URL}/rag-question"
    response5 = requests.post(url5, json=payload5)
    print_request_response("5. RAG 질의응답", url5, payload5, response5)


if __name__ == "__main__":
    # API 서버가 실행 중인지 확인
    print("API 서버가 실행 중인지 확인...")
    try:
        requests.get(f"{BASE_URL}/ping")
    except requests.ConnectionError:
        print("오류: API 서버가 실행 중이 아닙니다.")
        print("다른 터미널에서 'python -m api' 명령으로 서버를 먼저 실행해주세요.")
    else:
        test_api()
        
"""
python -m client
"""