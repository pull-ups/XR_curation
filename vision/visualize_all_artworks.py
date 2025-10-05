import json
from skimage import measure
import numpy as np
import os
from PIL import Image, ImageDraw, ImageFont
import colorsys

def get_color_for_mask(mask_id):
    """마스크 ID에 따라 색상을 반환합니다."""
    base_colors = [
        "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7",
        "#DDA0DD", "#98D8C8", "#F7DC6F", "#BB8FCE", "#85C1E9",
        "#F8C471", "#FF8C94", "#6C5CE7", "#74B9FF", "#00B894",
        "#FDCB6E", "#E17055", "#FD79A8", "#A29BFE", "#55A3FF"
    ]
    
    if mask_id <= len(base_colors):
        return base_colors[mask_id - 1]
    else:
        # HSV 색상으로 동적 생성
        hue = ((mask_id - 1) * 137.5) % 360
        saturation = 0.7 + (mask_id % 3) * 0.1
        value = 0.8 + (mask_id % 2) * 0.2
        
        rgb = colorsys.hsv_to_rgb(hue/360, saturation, value)
        hex_color = "#{:02x}{:02x}{:02x}".format(
            int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255)
        )
        return hex_color

def hex_to_rgb(hex_color):
    """헥스 색상 코드를 RGB 튜플로 변환합니다."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def visualize_artwork(artwork_name, output_dir="./visualizations"):
    """특정 작품의 segmentation과 객체명을 시각화하고 저장합니다."""
    
    print(f"\n처리 중: {artwork_name}")
    
    # JSON 파일에서 마스크 정보 로드
    try:
        json_path = f"./mask_annotation/{artwork_name}.json"
        with open(json_path, 'r', encoding='utf-8') as f:
            mask_info = json.load(f)
        mask_names = {int(k): v for k, v in mask_info["mask_names"].items()}
        print(f"  - {len(mask_names)}개의 마스크 정보 로드 완료")
    except Exception as e:
        print(f"  - JSON 파일 로드 실패: {e}")
        return
    
    # 배경 이미지 로드
    try:
        img = Image.open(f"./artwork_images/{artwork_name}.jpg")
        print(f"  - 이미지 크기: {img.size}")
    except Exception as e:
        print(f"  - 이미지 로드 실패: {e}")
        return
    
    # 이미지에 그리기 위한 객체 생성
    draw = ImageDraw.Draw(img, 'RGBA')
    
    # 폰트 설정 (한글 지원)
    try:
        # macOS의 기본 한글 폰트 사용
        font_size = max(20, min(img.size) // 30)  # 이미지 크기에 비례한 폰트 크기
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/AppleGothic.ttf", font_size)
        small_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/AppleGothic.ttf", font_size - 5)
    except:
        print("  - 폰트 로드 실패, 기본 폰트 사용")
        font = ImageFont.load_default()
        small_font = font
    
    # 마스크 디렉토리 확인
    mask_dir = f"./masks/{artwork_name}/array"
    if not os.path.exists(mask_dir):
        print(f"  - 마스크 디렉토리를 찾을 수 없습니다: {mask_dir}")
        return
    
    # 마스크 파일 개수 확인
    mask_files = sorted([f for f in os.listdir(mask_dir) if f.endswith('.npy')])
    print(f"  - {len(mask_files)}개의 마스크 파일 발견")
    
    # 각 마스크 처리
    for i in range(1, len(mask_files) + 1):
        idx = f"{i:04d}"
        try:
            # 마스크 배열 로드
            segmentation_array = np.load(f"{mask_dir}/{artwork_name}_sam_mask_{idx}.npy")
            
            # 컨투어 찾기
            contours = measure.find_contours(segmentation_array, 0.5)
            
            if len(contours) > 0:
                main_contour = max(contours, key=len)
                
                # PIL 형식으로 좌표 변환 (row, col -> x, y)
                polygon_points = [(point[1], point[0]) for point in main_contour]
                
                # 색상 가져오기
                color_hex = get_color_for_mask(i)
                color_rgb = hex_to_rgb(color_hex)
                
                # 반투명 채우기
                fill_color = color_rgb + (80,)  # 알파 80
                draw.polygon(polygon_points, fill=fill_color, outline=None)
                
                # 경계선 그리기
                outline_color = color_rgb + (255,)  # 완전 불투명
                draw.line(polygon_points + [polygon_points[0]], fill=outline_color, width=3)
                
                # 객체명 표시 (중심점에)
                mask_name = mask_names.get(i, f'Mask {i}')
                
                # 중심점 계산
                contour_array = np.array(polygon_points)
                center_x = int(np.mean(contour_array[:, 0]))
                center_y = int(np.mean(contour_array[:, 1]))
                
                # 텍스트 배경 상자 그리기
                try:
                    bbox = draw.textbbox((center_x, center_y), f"{i}. {mask_name}", font=font, anchor="mm")
                    # 배경 상자를 약간 더 크게
                    padding = 5
                    bbox = (bbox[0] - padding, bbox[1] - padding, bbox[2] + padding, bbox[3] + padding)
                    draw.rectangle(bbox, fill=(255, 255, 255, 200))
                except:
                    pass
                
                # 텍스트 그리기
                draw.text((center_x, center_y), f"{i}. {mask_name}", 
                         fill=(0, 0, 0, 255), font=font, anchor="mm")
                
                print(f"  - 마스크 {i} ({mask_name}): 완료")
                
        except Exception as e:
            print(f"  - 마스크 {i} 처리 실패: {e}")
    
    # 출력 디렉토리 생성
    os.makedirs(output_dir, exist_ok=True)
    
    # 이미지 저장
    output_path = f"{output_dir}/{artwork_name}_visualization.jpg"
    # RGBA를 RGB로 변환하여 저장
    if img.mode == 'RGBA':
        background = Image.new('RGB', img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[3])  # 알파 채널을 마스크로 사용
        background.save(output_path, 'JPEG', quality=95)
    else:
        img.save(output_path, 'JPEG', quality=95)
    
    print(f"  ✓ 저장 완료: {output_path}")

def main():
    """모든 작품을 처리합니다."""
    
    print("=" * 60)
    print("예술 작품 Segmentation 시각화 시작")
    print("=" * 60)
    
    # mask_annotation 폴더에서 작품 목록 가져오기
    annotation_dir = "./mask_annotation"
    artwork_files = [f for f in os.listdir(annotation_dir) if f.endswith('.json')]
    
    # .json 확장자 제거하여 작품명 추출
    artworks = [f.replace('.json', '') for f in artwork_files]
    
    print(f"\n총 {len(artworks)}개의 작품을 처리합니다:")
    for artwork in artworks:
        print(f"  - {artwork}")
    
    # 각 작품 처리
    for artwork in artworks:
        visualize_artwork(artwork)
    
    print("\n" + "=" * 60)
    print("모든 작품 처리 완료!")
    print("=" * 60)

if __name__ == "__main__":
    main()
