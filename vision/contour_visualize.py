import json
from skimage import measure
import numpy as np
import os
import matplotlib.pyplot as plt
from PIL import Image
import matplotlib.font_manager as fm

# 한국어 폰트 설정
plt.rcParams['font.family'] = 'AppleGothic'  # macOS용 한국어 폰트
plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지


# 배경 이미지 로드
artwork_name = "프리마베라"

background_img = Image.open(f"../assets/artwork_images/{artwork_name}.jpg")
background_array = np.array(background_img)

# 전체 figure 생성
plt.figure(figsize=(15, 10))
plt.imshow(background_array)

# 모든 마스크를 하나의 이미지에 그리기
all_polygon_vertices = {}  # 모든 폴리곤 꼭짓점을 저장할 딕셔너리

mask_num=len(os.listdir(f"./masks/프리마베라/array"))
for i in range(1, mask_num + 1  ):
    idx=f"{i:04d}"
    # segmentation_array = np.load(f"/Users/sngwon/python/xr_npc/vision/masks/Las Meninas/array/Las Meninas_sam_mask_{idx}.npy")
    segmentation_array = np.load(f"./masks/{artwork_name}/array/{artwork_name}_sam_mask_{idx}.npy")

    # 마스크에서 컨투어(테두리) 찾기
    contours = measure.find_contours(segmentation_array, 0.5)

    # 가장 큰 컨투어를 선택 (여러 개가 있을 경우)
    if len(contours) > 0:
        main_contour = max(contours, key=len)
        
        # y좌표 뒤집힘 문제 해결: row, col을 col, row로 변환하고 y좌표를 뒤집기
        # measure.find_contours는 (row, col) 형태로 반환하므로 (x, y)로 변환 필요
        polygon_vertices = []
        for point in main_contour:
            # row(y좌표)는 이미지 높이에서 빼서 뒤집고, col(x좌표)는 그대로 사용
            x = point[1]  # col
            # y = segmentation_array.shape[0] - point[0]  # 높이 - row (y좌표 뒤집기)
            y = point[0]
            polygon_vertices.append([int(x), int(y)])
        
        # 컨투어를 이미지에 그리기 (각 마스크마다 다른 색상 사용)
        colors = plt.cm.tab10(i / 11)  # 서로 다른 색상 생성
        
        # 컨투어 라인 그리기
        contour_x = [p[1] for p in main_contour]  # col coordinates
        # contour_y = [segmentation_array.shape[0] - p[0] for p in main_contour]  # flipped row coordinates
        contour_y = [p[0] for p in main_contour]  # flipped row coordinates
        
        # 컨투어 라인 그리기 (legend용 label 추가)
        
        plt.plot(contour_x, contour_y, color=colors, linewidth=2, label=f'Mask {i}')
        
        # 꼭짓점 표시
        vertices_x = [p[0] for p in polygon_vertices]
        vertices_y = [p[1] for p in polygon_vertices]
        plt.scatter(vertices_x, vertices_y, color=colors, s=20, marker='o', alpha=0.7)
        
        # polygon_vertices 저장
        all_polygon_vertices[idx] = polygon_vertices
        
        # 개별 JSON 파일로도 저장 (기존 방식 유지)
        os.makedirs(f"./masks/{artwork_name}/contour", exist_ok=True)
        with open(f"./masks/{artwork_name}/contour/{idx}.json", "w") as f:
            json.dump({"polygon_vertices": polygon_vertices}, f)
        
        print(f"마스크 {i}: 폴리곤 꼭짓점 수 {len(polygon_vertices)}개")
    else:
        print(f"마스크 {i}에서 컨투어를 찾을 수 없습니다.")

# 최종 시각화 설정
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.axis('equal')
plt.tight_layout()

# 결과 저장
os.makedirs("./polygon", exist_ok=True)
plt.savefig('./polygon/all_masks_visualization.png', dpi=300, bbox_inches='tight')
plt.show()

#
print(f"총 {len(all_polygon_vertices)}개의 마스크가 처리되었습니다.")
