# Vision 모듈

예술품 이미지에서 비전인식 기술 관련 설명입니다.

## 워크플로우
0. SAM 모델 다운로드하여 (링크: https://github.com/facebookresearch/segment-anything?tab=readme-ov-file#model-checkpoints:~:text=or%20vit_h%3A-,ViT%2DH%20SAM%20model.,-vit_l%3A%20ViT), segment-anything 디렉토리에 넣기

1. **`get_box.py`**: "설명할 거리가 있는" 객체들에 대한 bounding box를 직접 annotation합니다.

   ```bash
   #  수작업
   ```

2. **`box_to_seg.py`**: SAM input으로 bounding box를 전달하여 객체들에 대한 segmentation mask를 얻습니다.
   ```bash
   python -m box_to_seg --artwork_name 시녀들
   ```

3. **`contour_visualize.py`**: segmentation mask를 segmentation 테두리(contour)로 변환합니다. 
   - segmentation mask는 이미지 width × height 만큼의 사이즈를 가져 용량이 크지만, contour만 저장하면 용량을 절약할 수 있습니다.

   ```bash
   python -m contour_visualize --artwork_name 시녀들
   ```

4. **Mask Annotation**: `mask_annotation` 폴더에 `[작품명].json`을 생성하여 mask_names와 mask_annotation 정보를 저장합니다.
   - mask_names는 직접 지정하는 것이 편함.
   - mask_names 지정 후 각 mask에 대한 설명 생성은 챗지피티한테 생성해달라고 하면 됨.

   ```bash
   #  수작업
   ```

5. **`contour_gui.py`**: 시뮬레이션을 통해 결과를 확인할 수 있습니다. 

   ```bash
   python -m contour_gui --artwork_name 시녀들
   ```
