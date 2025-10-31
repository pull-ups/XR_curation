"""
클릭 좌표 JSON 파일을 읽어서 각 좌표에 대해 터치 인식을 수행하는 스크립트
"""

import json
import os
import sys
from typing import Dict, List
from touch_recognition import TouchRecognition


def load_click_data(json_path: str) -> Dict:
    """
    클릭 좌표 JSON 파일을 로드합니다.
    
    :param json_path: JSON 파일 경로
    :return: JSON 데이터 딕셔너리
    """
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"❌ 파일을 찾을 수 없습니다: {json_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ JSON 파싱 오류: {e}")
        sys.exit(1)


def process_clicks(json_path: str, output_path: str = None) -> List[Dict]:
    """
    클릭 좌표 JSON 파일을 읽어서 각 좌표에 대해 터치 인식을 수행합니다.
    
    :param json_path: 클릭 좌표 JSON 파일 경로
    :param output_path: 결과를 저장할 JSON 파일 경로 (None이면 저장하지 않음)
    :return: 처리 결과 리스트
    """
    # JSON 파일 로드
    click_data = load_click_data(json_path)
    
    artwork_name = click_data['artwork_name']
    clicks = click_data['clicks']
    original_size = click_data['original_image_size']
    
    print("=" * 70)
    print(f"작품: {artwork_name}")
    print(f"총 클릭 수: {len(clicks)}")
    print(f"원본 이미지 크기: {original_size['width']}x{original_size['height']}")
    print("=" * 70)
    
    # TouchRecognition 인스턴스 생성
    touch_recognition = TouchRecognition()
    
    # 각 클릭 좌표에 대해 처리
    results = []
    found_count = 0
    not_found_count = 0
    
    for i, click in enumerate(clicks, 1):
        click_number = click['click_number']
        original_coords = click['original_coordinates']
        x = original_coords['x']
        y = original_coords['y']
        timestamp = click.get('timestamp', '')
        
        print(f"\n[{i}/{len(clicks)}] 클릭 #{click_number} 처리 중...")
        print(f"   좌표: ({x:.2f}, {y:.2f})")
        print(f"   시간: {timestamp}")
        
        # 픽셀 좌표로 객체 찾기
        result = touch_recognition.find_object_at_position(
            art_name=artwork_name,
            x=x,
            y=y,
            coordinate_type="pixel"  # 픽셀 좌표 사용
        )
        
        # 결과 저장
        click_result = {
            "click_number": click_number,
            "coordinates": {
                "x": x,
                "y": y
            },
            "timestamp": timestamp,
            "object_found": result is not None,
            "object_info": result if result else None
        }
        
        results.append(click_result)
        
        if result:
            found_count += 1
            print(f"   ✅ 객체 발견!")
            print(f"      - 마스크 ID: {result['mask_id']}")
            print(f"      - 이름: {result['name']}")
            print(f"      - 설명: {result['description'][:50]}...")
        else:
            not_found_count += 1
            print(f"   ❌ 해당 위치에 객체가 없습니다.")
    
    # 요약 출력
    print("\n" + "=" * 70)
    print("처리 완료 요약:")
    print(f"   총 클릭 수: {len(clicks)}")
    print(f"   객체 발견: {found_count}개")
    print(f"   객체 미발견: {not_found_count}개")
    print("=" * 70)
    
    # 결과를 JSON으로 저장
    output_data = {
        "artwork_name": artwork_name,
        "original_image_size": original_size,
        "total_clicks": len(clicks),
        "found_objects": found_count,
        "not_found": not_found_count,
        "results": results
    }
    
    if output_path:
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            print(f"\n✅ 결과가 저장되었습니다: {output_path}")
        except Exception as e:
            print(f"\n❌ 결과 저장 실패: {e}")
    
    return results


def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description="클릭 좌표 JSON 파일을 처리하여 터치 인식을 수행합니다.")
    parser.add_argument(
        "json_path",
        type=str,
        help="처리할 클릭 좌표 JSON 파일 경로"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="결과를 저장할 JSON 파일 경로 (지정하지 않으면 저장하지 않음)"
    )
    
    args = parser.parse_args()
    
    # 출력 경로가 지정되지 않았으면 자동 생성
    if args.output is None:
        base_name = os.path.splitext(os.path.basename(args.json_path))[0]
        output_dir = os.path.dirname(args.json_path) or "."
        args.output = os.path.join(output_dir, f"result/{base_name}.json")
    
    # 처리 실행
    process_clicks(args.json_path, args.output)


if __name__ == "__main__":
    main()

