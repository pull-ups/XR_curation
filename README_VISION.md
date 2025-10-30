## Vision 모듈

예술 작품 이미지에 대해 객체 단위 인식 및 상호작용을 지원하기 위한 비전 파이프라인을 제공합니다. Bounding box 수작업 어노테이션을 기반으로 SAM(Segment Anything)으로 세그멘테이션 마스크를 생성하고, 경량화를 위해 컨투어로 변환·관리합니다.

### 사전 준비 사항
- **모델 가중치**: SAM 체크포인트(예: ViT-H)를 다운로드하여 로컬 `segment-anything` 디렉터리에 배치하세요. 다운로드는 [Segment Anything - Model Checkpoints](https://github.com/facebookresearch/segment-anything?tab=readme-ov-file#model-checkpoints) 문서를 참고하세요.
- **작업 디렉터리**: 아래 명령으로 `vision` 디렉터리에서 작업합니다.
  ```bash
  cd vision
  ```

### 워크플로우 개요
1. Bounding box 어노테이션 (`get_box.py`)
2. SAM 기반 마스크 생성 (`box_to_seg.py`)
3. 마스크 → 컨투어 변환 및 시각화 (`contour_visualize.py`)
4. 마스크 메타데이터 어노테이션 작성 (`mask_annotation/[작품명].json`)
5. GUI 시뮬레이션으로 결과 확인 (`contour_gui.py`)

---

### 1) Bounding Box 어노테이션: `get_box.py`
설명 가치가 있는 객체(인물, 사물 등)에 대해 수작업으로 박스를 지정합니다. 입력 이미지는 `vision/artwork_images`를 사용하고, 결과는 `vision/boxes` 하위에 `[작품명].json`으로 저장됩니다.

```bash
python get_box.py
```

참고: 마우스 인터랙션으로 박스를 지정하면 파일이 자동 저장됩니다.

### 2) SAM 마스크 생성: `box_to_seg.py`
1)에서 생성한 bounding box를 SAM에 입력하여 객체 세그멘테이션 마스크를 생성합니다. 결과 마스크는 작품별 디렉터리(`vision/masks/[작품명]/array`)에 `.npy`로 저장됩니다.

```bash
python -m box_to_seg --artwork_name "시녀들"
```

### 3) 컨투어 변환 및 시각화: `contour_visualize.py`
세그멘테이션 마스크는 원본 이미지 크기(`width × height`)와 동일하여 용량이 큽니다. 컨투어(폴리라인)로 변환하여 `vision/masks/[작품명]/contour`에 `.json`으로 저장하면 용량을 크게 절약할 수 있습니다. 시각화 이미지는 `vision/visualizations`에 저장됩니다.

```bash
python -m contour_visualize --artwork_name "최후의 만찬"
```

### 4) 마스크 메타데이터 어노테이션: `mask_annotation/[작품명].json`
작품별로 `mask_names`와 각 마스크에 대한 설명(`mask_annotation`)을 정리합니다. `mask_names`는 사람이 이해하기 쉬운 이름으로 직접 지정하는 것을 권장합니다.

```bash
# 수작업으로 JSON 작성 (예: mask 이름, 설명 추가)
```

작성 팁: 초기 초안은 LLM을 활용해 생성한 뒤, 도메인 검수로 품질을 보완하는 방식을 추천합니다.

### 5) GUI 시뮬레이션: `contour_gui.py`
생성된 컨투어와 어노테이션을 바탕으로 인터랙션 시뮬레이션을 수행합니다.

```bash
python -m contour_gui --artwork_name "프리마베라"
```

---

### 디렉터리 구조(요약)
- `artwork_images/`: 원본 작품 이미지
- `boxes/`: 수작업 bounding box JSON
- `masks/[작품명]/array`: SAM 생성 마스크(`.npy`)
- `masks/[작품명]/contour`: 컨투어(`.json`)
- `mask_annotation/`: 작품별 마스크 메타데이터 JSON
- `visualizations/`: 컨투어 시각화 결과 이미지

### 참고
- SAM 모델 사용법과 체크포인트는 상기 링크 문서를 참고하세요.
