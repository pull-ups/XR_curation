## 변수 설명
### 1. 작품명
```
["비너스의 탄생", "성 마태를 부르심", "시녀들", "아담의 창조", "아테네 학당", "야경", "최후의 만찬", "파리스의 심판", "프리마베라", "회화의 기술"]
```
### 2. 작품 이미지 파일 경로: `assets/artwork_images`
### 3. 작품 이미지 좌표계: `(0,0): left-top`
### 4. 작품 이미지 크기
```
1: 파리스의 심판.jpg, max_width: 5707, max_height: 4226
2: 최후의 만찬.jpg, max_width: 960, max_height: 480
3: 아담의 창조.jpg, max_width: 3572, max_height: 1663
4: 아테네 학당.jpg, max_width: 1000, max_height: 666
5: 시녀들.jpg, max_width: 600, max_height: 691
6: 프리마베라.jpg, max_width: 770, max_height: 504
7: 비너스의 탄생.jpg, max_width: 1200, max_height: 754
8: 야경.jpg, max_width: 1200, max_height: 976
9: 성 마태를 부르심.jpg, max_width: 625, max_height: 599
10: 회화의 기술.jpg, max_width: 6209, max_height: 7377
```



## API Description

### 1. 섹션 안내 나레이션 생성

현재 섹션에 대한 안내 메시지를 생성합니다. 이전 감상 작품이 있는 경우, 해당 작품을 언급하며 다음 섹션을 자연스럽게 안내합니다.

-   **URL:** `/section-narration`
-   **Method:** `POST`
-   **Query Parameters:**

    **Request Body:**
    ```json
    {
      "current_section": 1,
      "viewed_artworks": ["아테네 학당"]
    }
    ```

---

### 2. 작품 흥미 유발 나레이션 생성

현재 섹션에서 아직 관람하지 않은 작품에 대한 흥미를 유발하는 질문을 생성합니다.

-   **URL:** `/artwork-attraction`
-   **Method:** `POST`
-   **Request Body:**
    ```json
    {
      "current_section": 1,
      "viewed_artworks": ["아테네 학당"]
    }
    ```

---

### 3. 작품 설명 나레이션 생성

특정 작품에 대한 설명을 생성합니다. 현재 작품에 대해 이미 생성된 NPC 발화(`memory`)나 이전에 본 작품 목록(`viewed_artworks`)을 바탕으로 개인화된 또는 비교 설명을 제공할 수 있습니다.

-   **URL:** `/artwork-narration`
-   **Method:** `POST`
-   **Request Body:**
    ```json
    # 1. 해당 작품에 대해 이미 생성된 설명이 없을 경우 (첫 상호작용)
    {
      "art_name": "비너스의 탄생",
      "memory": "",
      "viewed_artworks": ["아테네 학당", "최후의 만찬"]
    }


    # 2. 해당 작품에 대해 이미 생성된 설명이 있을 경우(첫 상호작용 이후)
    {
      "art_name": "비너스의 탄생",
      "memory": "비너스의 탄생은 이탈리아의 화가 산드로 보티첼리의 대표작으로 1484년에서 1486년 사이에 제작되었습니다. ... 이 그림은 오늘날에도 많은 사람들에게 사랑받고 있으며, 미술사에서 중요한 위치를 차지하고 있습니다.",
      "viewed_artworks": ["아테네 학당", "최후의 만찬"]
    }
    ```

---

### 4. RAG 기반 질의응답

작품에 대한 사용자의 질문에 RAG(Retrieval-Augmented Generation) 기술을 사용하여 답변합니다.

-   **URL:** `/rag-question`
-   **Method:** `POST`
-   **Request Body:**
    ```json
    {
      "question": "이 그림에 있는 가운데 사람은 누구야?",
      "art_name": "아테네 학당"
    }
    ```



