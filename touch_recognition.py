import json
import numpy as np
import os
from typing import Optional, Tuple, Dict
from skimage import measure
from curation_types import ARTWORK_NAMES, ARTWORK_NAME_KR_TO_EN


class TouchRecognition:
    """
    터치 좌표를 기반으로 작품 내 객체를 인식하고 설명을 제공하는 클래스.
    사용자가 작품의 특정 위치를 터치하면 해당 위치의 객체 정보를 반환합니다.
    """
    
    def __init__(self, vision_base_path="./vision"):
        """
        TouchRecognition 클래스를 초기화합니다.
        
        :param vision_base_path: vision 데이터가 저장된 기본 경로
        """
        self.vision_base_path = vision_base_path
        self.masks_cache = {}  # 작품별 마스크 데이터 캐시
        self.mask_info_cache = {}  # 작품별 마스크 정보 캐시
    
    def _load_mask_info(self, art_name: str) -> Tuple[Dict[int, str], Dict[int, str]]:
        """
        JSON 파일에서 마스크 이름과 설명을 로드합니다.
        
        :param art_name: 작품명
        :return: (mask_names, mask_descriptions) 튜플
        """
        if art_name in self.mask_info_cache:
            return self.mask_info_cache[art_name]
        
        try:
            json_path = f"{self.vision_base_path}/mask_annotation/{art_name}.json"
            print(f"🔍 JSON 파일 로드 시도: {json_path}")
            
            with open(json_path, 'r', encoding='utf-8') as f:
                mask_info = json.load(f)
            
            # JSON의 문자열 키를 정수로 변환
            mask_names = {int(k): v for k, v in mask_info["mask_names"].items()}
            mask_descriptions = {int(k): v for k, v in mask_info["mask_descriptions"].items()}
            
            print(f"✅ 마스크 정보 로드 성공: {len(mask_names)}개 이름, {len(mask_descriptions)}개 설명")
            print(f"   마스크 이름 샘플: {list(mask_names.items())[:2]}")
            
            self.mask_info_cache[art_name] = (mask_names, mask_descriptions)
            return mask_names, mask_descriptions
            
        except Exception as e:
            print(f"❌ 마스크 정보 로드 실패 ({art_name}): {e}")
            import traceback
            traceback.print_exc()
            return {}, {}
    
    def _load_masks_data(self, art_name: str) -> Dict[int, Dict]:
        """
        작품의 모든 마스크 데이터를 로드합니다.
        
        :param art_name: 작품명
        :return: 마스크 ID를 키로 하는 마스크 데이터 딕셔너리
        """
        if art_name in self.masks_cache:
            return self.masks_cache[art_name]
        
        masks_data = {}
        
        # 마스크 정보 로드
        mask_names, mask_descriptions = self._load_mask_info(art_name)
        
        # 원본 이미지 크기 가져오기
        try:
            from PIL import Image
            img_path = f"{self.vision_base_path}/artwork_images/{art_name}.jpg"
            img = Image.open(img_path)
            original_width, original_height = img.size
        except Exception as e:
            print(f"이미지 로드 실패 ({art_name}): {e}")
            return {}
        
        # 마스크 디렉토리 확인
        mask_dir = f"{self.vision_base_path}/masks/{art_name}/array"
        if not os.path.exists(mask_dir):
            print(f"마스크 디렉토리를 찾을 수 없습니다: {mask_dir}")
            return {}
        
        # 마스크 파일 개수 동적 감지
        mask_files = [f for f in os.listdir(mask_dir) if f.endswith('.npy')]
        max_mask_num = len(mask_files)
        
        print(f"작품 '{art_name}': {max_mask_num}개 마스크 로드 중...")
        
        for i in range(1, max_mask_num + 1):
            idx = f"{i:04d}"
            try:
                # 마스크 배열 로드
                segmentation_array = np.load(
                    f"{self.vision_base_path}/masks/{art_name}/array/{art_name}_sam_mask_{idx}.npy"
                )
                
                # 컨투어 찾기
                contours = measure.find_contours(segmentation_array, 0.5)
                
                if len(contours) > 0:
                    main_contour = max(contours, key=len)
                    
                    # 원본 이미지 좌표계로 컨투어 저장
                    contour_points = []
                    for point in main_contour:
                        x = point[1]  # col
                        y = point[0]  # row
                        contour_points.extend([x, y])
                    
                    mask_name = mask_names.get(i, f'Mask {i}')
                    mask_desc = mask_descriptions.get(i, '설명이 없습니다.')
                    
                    masks_data[i] = {
                        'name': mask_name,
                        'description': mask_desc,
                        'contour_points': contour_points,
                        'segmentation_array': segmentation_array
                    }
                    
                    print(f"  마스크 {i}: {mask_name} (포인트 {len(contour_points)//2}개)")
                    
            except Exception as e:
                print(f"❌ 마스크 {i} 로드 실패 ({art_name}): {e}")
        
        # 캐시에 저장
        self.masks_cache[art_name] = masks_data
        print(f"작품 '{art_name}': {len(masks_data)}개 마스크 로드 완료")
        
        return masks_data
    
    def _point_in_polygon(self, x: float, y: float, polygon_points: list) -> bool:
        """
        점이 폴리곤 내부에 있는지 확인합니다 (Ray casting algorithm).
        
        :param x: x 좌표
        :param y: y 좌표
        :param polygon_points: 폴리곤 꼭짓점 리스트 [x1, y1, x2, y2, ...]
        :return: 점이 폴리곤 내부에 있으면 True
        """
        if len(polygon_points) < 6:  # 최소 3개 점
            return False
        
        # Ray casting algorithm
        n = len(polygon_points) // 2
        inside = False
        
        p1x, p1y = polygon_points[0], polygon_points[1]
        for i in range(1, n + 1):
            p2x, p2y = polygon_points[(i % n) * 2], polygon_points[(i % n) * 2 + 1]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        
        return inside
    
    def find_object_at_position(
        self, 
        art_name: str, 
        x: float, 
        y: float,
        coordinate_type: str = "normalized"
    ) -> Optional[Dict]:
        """
        주어진 좌표에서 객체를 찾아 정보를 반환합니다.
        
        :param art_name: 작품명
        :param x: x 좌표
        :param y: y 좌표
        :param coordinate_type: 좌표 타입 ("normalized": 0~1 정규화, "pixel": 픽셀 좌표)
        :return: 객체 정보 딕셔너리 또는 None
                {
                    "mask_id": int,
                    "name": str,
                    "description": str,
                    "art_name": str,
                    "art_name_en": str
                }
        """
        # 작품명 유효성 검사
        if art_name not in ARTWORK_NAMES:
            return None
        
        # 마스크 데이터 로드
        masks_data = self._load_masks_data(art_name)
        if not masks_data:
            return None
        
        # 좌표 변환 (정규화된 좌표인 경우)
        if coordinate_type == "normalized":
            from PIL import Image
            img_path = f"{self.vision_base_path}/artwork_images/{art_name}.jpg"
            try:
                img = Image.open(img_path)
                img_width, img_height = img.size
                pixel_x = x * img_width
                pixel_y = y * img_height
            except Exception as e:
                print(f"이미지 크기 확인 실패: {e}")
                return None
        else:
            pixel_x = x
            pixel_y = y
        
        # 각 마스크를 순회하며 해당 위치의 객체 찾기
        print(f"🔍 좌표 ({pixel_x:.1f}, {pixel_y:.1f})에서 객체 검색 중... (총 {len(masks_data)}개 마스크)")
        for mask_id, mask_data in masks_data.items():
            if self._point_in_polygon(pixel_x, pixel_y, mask_data['contour_points']):
                # 객체를 찾았으면 정보 반환
                art_name_en = ARTWORK_NAME_KR_TO_EN.get(art_name, art_name)
                
                result = {
                    "mask_id": mask_id,
                    "name": mask_data['name'],
                    "description": mask_data['description'],
                    "art_name": art_name,
                    "art_name_en": art_name_en
                }
                
                print(f"✅ 객체 찾음: ID={mask_id}, 이름={mask_data['name']}")
                return result
        
        # 해당 위치에 객체가 없음
        print(f"❌ 해당 좌표에서 객체를 찾지 못함")
        return None
    
    def get_all_objects(self, art_name: str) -> list:
        """
        작품의 모든 객체 목록을 반환합니다.
        
        :param art_name: 작품명
        :return: 객체 정보 리스트
        """
        if art_name not in ARTWORK_NAMES:
            return []
        
        masks_data = self._load_masks_data(art_name)
        art_name_en = ARTWORK_NAME_KR_TO_EN.get(art_name, art_name)
        
        objects_list = []
        for mask_id in sorted(masks_data.keys()):
            mask_data = masks_data[mask_id]
            objects_list.append({
                "mask_id": mask_id,
                "name": mask_data['name'],
                "description": mask_data['description'],
                "art_name": art_name,
                "art_name_en": art_name_en
            })
        
        return objects_list


# --- 사용 예시 ---
if __name__ == '__main__':
    # TouchRecognition 인스턴스 생성
    touch_recognition = TouchRecognition()
    
    print("=== 터치 기반 객체 인식 테스트 ===\n")
    
    # 테스트 1: 정규화된 좌표로 객체 찾기
    print("테스트 1: 시녀들 작품에서 중앙 (0.5, 0.5) 위치 객체 찾기")
    result = touch_recognition.find_object_at_position(
        art_name="시녀들",
        x=0.5,
        y=0.5,
        coordinate_type="normalized"
    )
    
    if result:
        print(f"✅ 객체 발견!")
        print(f"   - 마스크 ID: {result['mask_id']}")
        print(f"   - 이름: {result['name']}")
        print(f"   - 설명: {result['description']}")
    else:
        print("❌ 해당 위치에 객체가 없습니다.")
    
    print("\n" + "="*60 + "\n")
    
    # 테스트 2: 모든 객체 목록 가져오기
    print("테스트 2: 시녀들 작품의 모든 객체 목록")
    objects = touch_recognition.get_all_objects("시녀들")
    print(f"총 {len(objects)}개의 객체:")
    for obj in objects[:3]:  # 처음 3개만 출력
        print(f"   {obj['mask_id']}. {obj['name']}")
    print("   ...")
    
    print("\n" + "="*60)
