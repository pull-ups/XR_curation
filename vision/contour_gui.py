import json
from skimage import measure
import numpy as np
import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw
import math
from openai import OpenAI
from dataclasses import dataclass
import tyro

@dataclass
class Config:
    artwork_name: str


client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)
def get_response(prompt):
    response = client.responses.create(
        model="gpt-4o-mini",
        input=prompt,
        temperature=0.0
    )
    return response.output_text

class TkinterSegmentationViewer:
    def __init__(self, root, artwork_name: str):
        self.root = root
        self.root.title("Las Meninas - Interactive Segmentation Viewer")
        self.root.geometry("1600x1000")
        
        # JSON 파일에서 마스크 정보 로드
        self.load_mask_info()
        self.artwork_name = artwork_name
        
        # 색상 팔레트
        self.colors = [
            "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7",
            "#DDA0DD", "#98D8C8", "#F7DC6F", "#BB8FCE", "#85C1E9",
            "#F8C471"
        ]
        
        # 데이터 초기화
        self.masks_data = {}
        self.polygon_items = {}  # Canvas에 그려진 폴리곤 아이템들
        self.current_hover_mask = None
        self.current_search_masks = []
        self.search_text = ""
        
        # GUI 구성
        self.setup_gui()
        
        # 마스크 데이터 로드
        self.load_mask_data()
        
        # 초기 마스크 그리기
        self.draw_all_masks()
    
    def load_mask_info(self):
        """JSON 파일에서 마스크 이름과 설명을 로드합니다."""
        try:

            json_path = "./mask_annotation/시녀들.json"
            
            with open(json_path, 'r', encoding='utf-8') as f:
                mask_info = json.load(f)
            
            # JSON의 문자열 키를 정수로 변환
            self.mask_names = {int(k): v for k, v in mask_info["mask_names"].items()}
            self.mask_descriptions = {int(k): v for k, v in mask_info["mask_descriptions"].items()}
            
            print("마스크 정보를 JSON 파일에서 성공적으로 로드했습니다.")
            
        except Exception as e:
            print(f"JSON 파일 로드 실패: {e}")
            # 기본값으로 설정
            self.mask_names = {}
            self.mask_descriptions = {}
        
    def setup_gui(self):
        """GUI 구성요소를 설정합니다."""
        # 메인 프레임 (수평 분할)
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 왼쪽 패널 (이미지 뷰어)
        left_panel = ttk.Frame(main_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # 오른쪽 패널 (설명 및 제어)
        right_panel = ttk.Frame(main_frame, width=400)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y)
        right_panel.pack_propagate(False)  # 고정 너비 유지
        
        # === 왼쪽 패널 구성 ===
        # 상단 제어 패널
        control_frame = ttk.Frame(left_panel)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 검색 입력
        ttk.Label(control_frame, text="마스크 검색:", font=('AppleGothic', 12)).pack(side=tk.LEFT, padx=(0, 5))
        
        self.search_var = tk.StringVar()
        # 검색어 변경 추적 제거
        # self.search_var.trace('w', self.on_search_change)
        self.search_entry = ttk.Entry(control_frame, textvariable=self.search_var, 
                                    font=('AppleGothic', 12), width=20)
        self.search_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        # 검색 버튼 추가
        ttk.Button(control_frame, text="검색", command=self.perform_search).pack(side=tk.LEFT, padx=(0, 10))
        
        # 초기화 버튼
        ttk.Button(control_frame, text="초기화", command=self.clear_search).pack(side=tk.LEFT, padx=(0, 10))
        
        # 엔터키 바인딩
        self.search_entry.bind('<Return>', lambda e: self.perform_search())
        
        # 상태 표시
        self.status_var = tk.StringVar(value="준비 완료 - 마우스를 마스크 위에 올리거나 검색어를 입력하세요")
        self.status_label = ttk.Label(control_frame, textvariable=self.status_var, 
                                    font=('AppleGothic', 10), foreground='blue')
        self.status_label.pack(side=tk.LEFT, padx=(20, 0))
        
        # 캔버스 프레임
        canvas_frame = ttk.Frame(left_panel)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        # 스크롤바가 있는 캔버스
        self.canvas = tk.Canvas(canvas_frame, bg='white')
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        
        self.canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # 그리드 배치
        self.canvas.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)
        
        # === 오른쪽 패널 구성 ===
        # 현재 선택된 마스크 정보
        info_frame = ttk.LabelFrame(right_panel, text="선택된 마스크 정보", padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 마스크 이름
        self.selected_name_var = tk.StringVar(value="마스크를 선택하세요")
        selected_name_label = ttk.Label(info_frame, textvariable=self.selected_name_var, 
                                      font=('AppleGothic', 14, 'bold'), foreground='darkblue')
        selected_name_label.pack(anchor=tk.W)
        
        # 구분선
        ttk.Separator(info_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=(10, 15))
        
        # 마스크 설명
        description_frame = ttk.Frame(info_frame)
        description_frame.pack(fill=tk.BOTH, expand=True)
        
        # 스크롤 가능한 텍스트 위젯
        self.description_text = tk.Text(description_frame, wrap=tk.WORD, height=12, 
                                      font=('AppleGothic', 11), bg='#f8f9fa', 
                                      relief=tk.FLAT, padx=10, pady=10)
        desc_scrollbar = ttk.Scrollbar(description_frame, orient=tk.VERTICAL, 
                                     command=self.description_text.yview)
        self.description_text.configure(yscrollcommand=desc_scrollbar.set)
        
        self.description_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        desc_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 초기 설명 텍스트
        self.description_text.insert(tk.END, "마우스를 마스크 위에 올리거나 검색을 통해 마스크를 선택하면 여기에 자세한 설명이 표시됩니다.")
        self.description_text.config(state=tk.DISABLED)
        
        # 마스크 목록
        list_frame = ttk.LabelFrame(right_panel, text="전체 마스크 목록", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # 리스트박스
        listbox_frame = ttk.Frame(list_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True)
        
        self.mask_listbox = tk.Listbox(listbox_frame, font=('AppleGothic', 10), height=8)
        list_scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, 
                                     command=self.mask_listbox.yview)
        self.mask_listbox.configure(yscrollcommand=list_scrollbar.set)
        
        self.mask_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 리스트박스 이벤트 바인딩
        self.mask_listbox.bind('<<ListboxSelect>>', self.on_listbox_select)
        
        # 마스크 목록 채우기
        for mask_id in range(1, 12):
            if mask_id in self.mask_names:
                self.mask_listbox.insert(tk.END, f"{mask_id}. {self.mask_names[mask_id]}")
        
        # 배경 이미지 로드 및 표시
        self.load_background_image()
        
        # 마우스 이벤트 바인딩
        self.canvas.bind('<Motion>', self.on_mouse_move)
        self.canvas.bind('<Button-1>', self.on_mouse_click)
        
    def load_background_image(self):
        """배경 이미지를 로드하고 캔버스에 표시합니다."""
        try:
            # 이미지 로드
            self.background_img = Image.open(f"./artwork_images/{self.artwork_name}.jpg")
            
            # 이미지 크기 조정 (너무 크면 축소)
            max_width, max_height = 1000, 700
            img_width, img_height = self.background_img.size
            
            if img_width > max_width or img_height > max_height:
                ratio = min(max_width/img_width, max_height/img_height)
                new_width = int(img_width * ratio)
                new_height = int(img_height * ratio)
                self.background_img = self.background_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # tkinter 이미지로 변환
            self.bg_photo = ImageTk.PhotoImage(self.background_img)
            
            # 캔버스에 이미지 배치
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.bg_photo)
            
            # 캔버스 스크롤 영역 설정
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            
            self.img_width = self.background_img.size[0]
            self.img_height = self.background_img.size[1]
            
        except Exception as e:
            print(f"배경 이미지 로드 실패: {e}")
            self.status_var.set(f"오류: 배경 이미지를 로드할 수 없습니다 - {e}")
            
    def load_mask_data(self):
        """모든 마스크 데이터를 로드합니다."""
        print("마스크 데이터를 로드중...")
        
        # 이미지 크기 비율 계산 (원본 대비 현재 표시 크기)
        original_img = Image.open(f"./artwork_images/{self.artwork_name}.jpg")
        original_width, original_height = original_img.size
        
        scale_x = self.img_width / original_width
        scale_y = self.img_height / original_height
        
        for i in range(1, 12):
            idx = f"{i:04d}"
            try:
                # 마스크 배열 로드
                segmentation_array = np.load(f"./masks/{self.artwork_name}/array/{self.artwork_name}_sam_mask_{idx}.npy")
                
                # 컨투어 찾기
                contours = measure.find_contours(segmentation_array, 0.5)
                
                if len(contours) > 0:
                    main_contour = max(contours, key=len)
                    
                    # 폴리곤 꼭짓점 계산 (크기 조정 적용)
                    contour_points = []
                    
                    for point in main_contour:
                        x = point[1] * scale_x  # col * scale
                        y = point[0] * scale_y  # row * scale
                        contour_points.extend([x, y])  # tkinter polygon 형식
                    
                    # 마스크 데이터 저장
                    self.masks_data[i] = {
                        'name': self.mask_names.get(i, f'Mask {i}'),
                        'description': self.mask_descriptions.get(i, '설명이 없습니다.'),
                        'contour_points': contour_points,
                        'color': self.colors[(i-1) % len(self.colors)],
                        'original_contour': main_contour  # 원본 컨투어도 저장
                    }
                    
                    print(f"마스크 {i} ({self.mask_names.get(i, f'Mask {i}')}): 로드 완료")
                    
            except Exception as e:
                print(f"마스크 {i} 로드 실패: {e}")
    
    def update_description_panel(self, mask_id):
        """설명 패널을 업데이트합니다."""
        if mask_id and mask_id in self.masks_data:
            mask_data = self.masks_data[mask_id]
            self.selected_name_var.set(f"{mask_id}. {mask_data['name']}")
            
            # 설명 텍스트 업데이트
            self.description_text.config(state=tk.NORMAL)
            self.description_text.delete(1.0, tk.END)
            self.description_text.insert(tk.END, mask_data['description'])
            self.description_text.config(state=tk.DISABLED)
            
            # 리스트박스에서 해당 항목 선택
            self.mask_listbox.selection_clear(0, tk.END)
            self.mask_listbox.selection_set(mask_id - 1)
            self.mask_listbox.see(mask_id - 1)
            
        else:
            self.selected_name_var.set("마스크를 선택하세요")
            self.description_text.config(state=tk.NORMAL)
            self.description_text.delete(1.0, tk.END)
            self.description_text.insert(tk.END, "마우스를 마스크 위에 올리거나 검색을 통해 마스크를 선택하면 여기에 자세한 설명이 표시됩니다.")
            self.description_text.config(state=tk.DISABLED)
            self.mask_listbox.selection_clear(0, tk.END)

    def on_listbox_select(self, event):
        """리스트박스 선택 이벤트를 처리합니다."""
        selection = self.mask_listbox.curselection()
        if selection:
            mask_id = selection[0] + 1  # 리스트 인덱스를 mask_id로 변환
            if mask_id in self.masks_data:
                # 해당 마스크를 하이라이트
                self.current_hover_mask = mask_id
                highlighted_masks = [mask_id]
                if self.current_search_masks:
                    highlighted_masks.extend(self.current_search_masks)
                
                self.draw_all_masks(highlight_mode=True, highlighted_masks=highlighted_masks)
                self.update_description_panel(mask_id)
                self.status_var.set(f"선택: {self.masks_data[mask_id]['name']}")

    # ... (기존 메서드들: draw_all_masks, point_in_polygon, find_mask_at_point, search_masks_by_name)

    def draw_all_masks(self, highlight_mode=False, highlighted_masks=None):
        """모든 마스크를 그립니다."""
        # 기존 폴리곤들 제거
        for item in self.polygon_items.values():
            self.canvas.delete(item)
        self.polygon_items.clear()
        
        for mask_id, mask_data in self.masks_data.items():
            is_highlighted = highlighted_masks and mask_id in highlighted_masks
            
            if len(mask_data['contour_points']) < 6:  # 최소 3개 점 필요
                continue
                
            if highlight_mode and not is_highlighted:
                # 하이라이트되지 않은 마스크는 매우 연하게
                outline_color = mask_data['color']
                fill_color = mask_data['color']
                stipple = 'gray12'  # 점선 패턴
                width = 1
                alpha_fill = ''  # 투명
            elif is_highlighted:
                # 하이라이트된 마스크는 진하게
                outline_color = mask_data['color']
                fill_color = mask_data['color']
                stipple = ''
                width = 3
                alpha_fill = mask_data['color']
            else:
                # 기본 상태에서는 연하게
                outline_color = mask_data['color']
                fill_color = mask_data['color']
                stipple = 'gray25'
                width = 2
                alpha_fill = ''
            
            # 폴리곤 그리기
            polygon_item = self.canvas.create_polygon(
                mask_data['contour_points'],
                outline=outline_color,
                fill=alpha_fill,
                stipple=stipple,
                width=width,
                tags=f"mask_{mask_id}"
            )
            
            self.polygon_items[mask_id] = polygon_item
    
    def point_in_polygon(self, x, y, polygon_points):
        """점이 폴리곤 내부에 있는지 확인합니다."""
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
    
    def find_mask_at_point(self, x, y):
        """주어진 좌표에서 마스크를 찾습니다."""
        for mask_id, mask_data in self.masks_data.items():
            if self.point_in_polygon(x, y, mask_data['contour_points']):
                return mask_id
        return None
    
    def search_masks_by_name(self, search_term):
        """이름으로 마스크를 검색합니다."""
        if not search_term.strip():
            return []
            
        matching_masks = []
        search_term_lower = search_term.lower()
        
        # 직접 매칭 시도
        for mask_id, mask_data in self.masks_data.items():
            mask_name_lower = mask_data['name'].lower()
            if search_term_lower in mask_name_lower:
                matching_masks.append(mask_id)
        
        # 직접 매칭된 결과가 없으면 ChatGPT로 의미적 검색 시도
        if not matching_masks:
            try:
                # 시스템 메시지 구성 - 객체 리스트와 함께
                objects_list = "\n".join([f"{mask_id}. {mask_data['name']}" for mask_id, mask_data in self.masks_data.items()])
                system_message = f"""당신은 사용자의 질문에서 물어보고 있는 대상을 분석하여 아래 목록 중에서 가장 관련있는 객체의 번호를 찾아주는 AI 입니다.
질문: {search_term}
객체 목록:
{objects_list}

규칙:
1. 사용자의 질문에서 물어보고 있는 대상과 가장 의미적으로 관련있는 객체의 번호만 반환하세요.
2. 여러 객체가 관련있다면 쉼표로 구분하여 모든 번호를 반환하세요.
3. 관련된 객체가 없다면 "none"을 반환하세요.
4. 번호만 반환하고 다른 설명은 하지 마세요.

예시:
- 입력: "왕실" -> "1,4" (왕녀와 거울 속 왕과 왕비가 관련)
- 입력: "동물" -> "2" (개가 관련)
- 입력: "하늘" -> "none" (관련 객체 없음)"""

                # 사용자 검색어로 ChatGPT 호출
                print(system_message)
                result = get_response(system_message)
                print(result)
                
                # ChatGPT 응답 처리
                
                if result != "none":
                    # 쉼표로 구분된 번호들을 리스트로 변환
                    matching_masks = [int(num.strip()) for num in result.split(",")]
                    
            except Exception as e:
                print(f"ChatGPT 검색 중 오류 발생: {e}")
                
        return matching_masks
    
    def on_mouse_move(self, event):
        """마우스 이동 이벤트를 처리합니다."""
        # 캔버스 좌표로 변환
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        # 현재 마우스 위치에서 마스크 찾기
        mask_id = self.find_mask_at_point(canvas_x, canvas_y)
        
        if mask_id != self.current_hover_mask:
            self.current_hover_mask = mask_id
            
            if mask_id:
                # 호버된 마스크가 있으면 하이라이트
                highlighted_masks = [mask_id]
                if self.current_search_masks:
                    highlighted_masks.extend(self.current_search_masks)
                
                self.draw_all_masks(highlight_mode=True, highlighted_masks=highlighted_masks)
                self.update_description_panel(mask_id)
                self.status_var.set(f"선택: {self.masks_data[mask_id]['name']}")
            else:
                # 호버된 마스크가 없으면 검색 결과만 하이라이트
                if self.current_search_masks:
                    self.draw_all_masks(highlight_mode=True, highlighted_masks=self.current_search_masks)
                    if len(self.current_search_masks) == 1:
                        self.update_description_panel(self.current_search_masks[0])
                    else:
                        self.update_description_panel(None)
                    mask_names = [self.masks_data[mid]['name'] for mid in self.current_search_masks]
                    self.status_var.set(f"검색 결과: {', '.join(mask_names)}")
                else:
                    self.draw_all_masks(highlight_mode=False)
                    self.update_description_panel(None)
                    self.status_var.set("마우스를 마스크 위에 올리거나 검색어를 입력하세요")
    
    def on_mouse_click(self, event):
        """마우스 클릭 이벤트를 처리합니다."""
        # 캔버스 좌표로 변환
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        # 클릭한 위치의 마스크 찾기
        mask_id = self.find_mask_at_point(canvas_x, canvas_y)
        
        if mask_id:
            mask_name = self.masks_data[mask_id]['name']
            self.status_var.set(f"클릭: {mask_name}")
            self.update_description_panel(mask_id)
            print(f"마스크 {mask_id} '{mask_name}' 클릭됨")
    
    def on_search_change(self, *args):
        """검색어 변경 시 호출됩니다."""
        self.search_text = self.search_var.get()
        self.current_search_masks = self.search_masks_by_name(self.search_text)
        
        # 화면 업데이트
        if self.current_search_masks:
            highlighted_masks = self.current_search_masks[:]
            if self.current_hover_mask and self.current_hover_mask not in highlighted_masks:
                highlighted_masks.append(self.current_hover_mask)
            
            self.draw_all_masks(highlight_mode=True, highlighted_masks=highlighted_masks)
            
            # 검색 결과가 하나면 설명 표시
            if len(self.current_search_masks) == 1:
                self.update_description_panel(self.current_search_masks[0])
            else:
                self.update_description_panel(None)
            
            # 찾은 마스크 정보 표시
            mask_names = [self.masks_data[mid]['name'] for mid in self.current_search_masks]
            self.status_var.set(f"검색 결과: {', '.join(mask_names)}")
        else:
            if self.search_text.strip():
                self.status_var.set(f"'{self.search_text}'에 해당하는 마스크가 없습니다")
                self.draw_all_masks(highlight_mode=False)
                self.update_description_panel(None)
            else:
                self.status_var.set("마우스를 마스크 위에 올리거나 검색어를 입력하세요")
                self.draw_all_masks(highlight_mode=False)
                self.update_description_panel(None)
    
    def perform_search(self):
        """검색을 실행합니다."""
        self.search_text = self.search_var.get()
        self.current_search_masks = self.search_masks_by_name(self.search_text)
        
        # 화면 업데이트
        if self.current_search_masks:
            highlighted_masks = self.current_search_masks[:]
            if self.current_hover_mask and self.current_hover_mask not in highlighted_masks:
                highlighted_masks.append(self.current_hover_mask)
            
            self.draw_all_masks(highlight_mode=True, highlighted_masks=highlighted_masks)
            
            # 검색 결과가 하나면 설명 표시
            if len(self.current_search_masks) == 1:
                self.update_description_panel(self.current_search_masks[0])
            else:
                self.update_description_panel(None)
            
            # 찾은 마스크 정보 표시
            mask_names = [self.masks_data[mid]['name'] for mid in self.current_search_masks]
            self.status_var.set(f"검색 결과: {', '.join(mask_names)}")
            if not any(self.search_text.lower() in name.lower() for name in mask_names):
                self.status_var.set(f"AI 검색 결과: {', '.join(mask_names)}")
        else:
            if self.search_text.strip():
                self.status_var.set(f"'{self.search_text}'에 해당하는 마스크를 찾을 수 없습니다")
                self.draw_all_masks(highlight_mode=False)
                self.update_description_panel(None)
            else:
                self.status_var.set("마우스를 마스크 위에 올리거나 검색어를 입력하세요")
                self.draw_all_masks(highlight_mode=False)
                self.update_description_panel(None)
    
    def clear_search(self):
        """검색어를 지웁니다."""
        self.search_var.set("")
        self.current_search_masks = []
        self.draw_all_masks(highlight_mode=False)
        self.update_description_panel(None)
        self.status_var.set("검색이 초기화되었습니다")
        self.search_entry.focus()

def main(artwork_name: str):
    root = tk.Tk()
    app = TkinterSegmentationViewer(root, artwork_name=artwork_name)
    
    print("=== Tkinter Interactive Segmentation Viewer with Descriptions ===")
    print("사용법:")
    print("1. 마우스를 마스크 위에 올리면 해당 마스크가 하이라이트되고 설명이 표시됩니다")
    print("2. 검색창에 '소녀', '그림', '여자' 등을 입력하면 해당 마스크들이 하이라이트됩니다")
    print("3. 오른쪽 마스크 목록에서 클릭해도 해당 마스크를 선택할 수 있습니다")
    print("4. 마스크를 클릭하면 해당 마스크의 정보가 고정됩니다")
    print("5. '초기화' 버튼으로 검색을 초기화할 수 있습니다")
    print("================================================================")
    
    root.mainloop()

if __name__ == "__main__":
    args = tyro.cli(Config)
    main(artwork_name=args.artwork_name)
    
"""
python -m contour_gui --artwork_name "Las Meninas"
"""