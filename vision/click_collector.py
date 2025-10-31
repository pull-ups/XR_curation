"""
각 작품별로 20번의 클릭 좌표를 수집하여 JSON 파일로 저장하는 프로그램
"""

import json
import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from dataclasses import dataclass
import tyro
from datetime import datetime


@dataclass
class Config:
    artwork_name: str


class ClickCollector:
    def __init__(self, root, artwork_name: str):
        self.root = root
        self.root.title(f"{artwork_name} - 클릭 좌표 수집")
        self.root.geometry("1200x800")
        
        self.artwork_name = artwork_name
        self.max_clicks = 20
        self.click_count = 0
        self.click_coordinates = []
        
        # 원본 이미지 경로
        self.image_path = f"./artwork_images/{artwork_name}.jpg"
        
        if not os.path.exists(self.image_path):
            raise FileNotFoundError(f"이미지 파일을 찾을 수 없습니다: {self.image_path}")
        
        # GUI 설정
        self.setup_gui()
        
        # 이미지 로드
        self.load_image()
    
    def setup_gui(self):
        """GUI 구성요소를 설정합니다."""
        # 메인 프레임
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 상단 정보 패널
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 작품명 표시
        title_label = ttk.Label(info_frame, text=f"작품: {self.artwork_name}", 
                               font=('AppleGothic', 14, 'bold'))
        title_label.pack(side=tk.LEFT, padx=(0, 20))
        
        # 클릭 진행 상황 표시
        self.status_var = tk.StringVar(value=f"클릭 진행: 0/{self.max_clicks}")
        status_label = ttk.Label(info_frame, textvariable=self.status_var,
                                font=('AppleGothic', 12), foreground='blue')
        status_label.pack(side=tk.LEFT, padx=(0, 20))
        
        # 저장 경로 표시
        self.save_path_var = tk.StringVar(value="")
        save_path_label = ttk.Label(info_frame, textvariable=self.save_path_var,
                                   font=('AppleGothic', 10), foreground='green')
        save_path_label.pack(side=tk.LEFT)
        
        # 캔버스 프레임
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        # 스크롤바가 있는 캔버스
        self.canvas = tk.Canvas(canvas_frame, bg='lightgray', cursor='crosshair')
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        
        self.canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # 그리드 배치
        self.canvas.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)
        
        # 하단 버튼 프레임
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # 수동 저장 버튼
        save_button = ttk.Button(button_frame, text="수동 저장", command=self.save_click_coordinates)
        save_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 초기화 버튼
        reset_button = ttk.Button(button_frame, text="초기화", command=self.reset_clicks)
        reset_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 사용법 표시
        instruction_label = ttk.Label(button_frame, 
                                      text="이미지를 클릭하면 좌표가 수집됩니다. 20번 클릭하면 자동으로 저장됩니다.",
                                      font=('AppleGothic', 10), foreground='gray')
        instruction_label.pack(side=tk.LEFT, padx=(20, 0))
        
        # 클릭 이벤트 바인딩
        self.canvas.bind('<Button-1>', self.on_click)
        
        # 클릭 위치 표시용 원형 마커
        self.click_markers = []
    
    def load_image(self):
        """이미지를 로드하고 캔버스에 표시합니다."""
        try:
            # 원본 이미지 로드
            self.original_image = Image.open(self.image_path)
            self.original_width, self.original_height = self.original_image.size
            
            # 이미지 크기 조정 (너무 크면 축소)
            max_width, max_height = 1000, 700
            img_width, img_height = self.original_image.size
            
            if img_width > max_width or img_height > max_height:
                ratio = min(max_width / img_width, max_height / img_height)
                new_width = int(img_width * ratio)
                new_height = int(img_height * ratio)
                self.display_image = self.original_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            else:
                self.display_image = self.original_image.copy()
            
            self.display_width, self.display_height = self.display_image.size
            
            # 스케일 비율 계산 (표시 크기 / 원본 크기)
            self.scale_x = self.display_width / self.original_width
            self.scale_y = self.display_height / self.original_height
            
            # tkinter 이미지로 변환
            self.photo = ImageTk.PhotoImage(self.display_image)
            
            # 캔버스에 이미지 배치
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
            
            # 캔버스 스크롤 영역 설정
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            
            print(f"이미지 로드 완료: {self.original_width}x{self.original_height} -> {self.display_width}x{self.display_height}")
            
        except Exception as e:
            print(f"이미지 로드 실패: {e}")
            self.status_var.set(f"오류: 이미지를 로드할 수 없습니다 - {e}")
    
    def on_click(self, event):
        """마우스 클릭 이벤트를 처리합니다."""
        # 20번 클릭을 완료했는지 확인
        if self.click_count >= self.max_clicks:
            print(f"이미 {self.max_clicks}번의 클릭을 완료했습니다.")
            return
        
        # 캔버스 좌표로 변환
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        # 이미지 영역 내인지 확인
        if canvas_x < 0 or canvas_x > self.display_width or canvas_y < 0 or canvas_y > self.display_height:
            print(f"이미지 영역 밖을 클릭했습니다: ({canvas_x}, {canvas_y})")
            return
        
        # 원본 이미지 좌표로 변환
        original_x = canvas_x / self.scale_x
        original_y = canvas_y / self.scale_y
        
        # 클릭 정보 저장
        click_info = {
            "click_number": self.click_count + 1,
            "canvas_coordinates": {
                "x": round(canvas_x, 2),
                "y": round(canvas_y, 2)
            },
            "original_coordinates": {
                "x": round(original_x, 2),
                "y": round(original_y, 2)
            },
            "timestamp": datetime.now().isoformat()
        }
        
        # 클릭 좌표 추가
        self.click_coordinates.append(click_info)
        self.click_count += 1
        
        # 클릭 위치에 마커 표시
        marker = self.canvas.create_oval(
            canvas_x - 5, canvas_y - 5,
            canvas_x + 5, canvas_y + 5,
            fill='red', outline='darkred', width=2,
            tags=f"marker_{self.click_count}"
        )
        self.click_markers.append(marker)
        
        # 클릭 번호 표시
        text = self.canvas.create_text(
            canvas_x, canvas_y - 15,
            text=str(self.click_count),
            fill='red', font=('Arial', 10, 'bold'),
            tags=f"text_{self.click_count}"
        )
        
        # 상태 업데이트
        remaining = self.max_clicks - self.click_count
        if remaining > 0:
            self.status_var.set(f"클릭 진행: {self.click_count}/{self.max_clicks} (남은 클릭: {remaining})")
        else:
            self.status_var.set(f"클릭 완료! {self.click_count}/{self.max_clicks} - 저장 중...")
            self.save_click_coordinates()
        
        print(f"클릭 {self.click_count}/{self.max_clicks}: 캔버스({canvas_x:.2f}, {canvas_y:.2f}) -> 원본({original_x:.2f}, {original_y:.2f})")
    
    def save_click_coordinates(self):
        """클릭 좌표를 JSON 파일로 저장합니다."""
        if self.click_count == 0:
            print("저장할 클릭 좌표가 없습니다.")
            self.status_var.set("저장할 클릭 좌표가 없습니다.")
            return
        
        # 저장 디렉토리 생성
        clicks_dir = "./clicks"
        os.makedirs(clicks_dir, exist_ok=True)
        
        json_path = os.path.join(clicks_dir, f"{self.artwork_name}.json")
        
        # 저장할 데이터 구성
        data = {
            "artwork_name": self.artwork_name,
            "total_clicks": self.click_count,
            "image_path": self.image_path,
            "original_image_size": {
                "width": self.original_width,
                "height": self.original_height
            },
            "display_image_size": {
                "width": self.display_width,
                "height": self.display_height
            },
            "scale_factors": {
                "scale_x": self.scale_x,
                "scale_y": self.scale_y
            },
            "clicks": self.click_coordinates
        }
        
        # JSON 파일로 저장
        try:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 클릭 좌표가 저장되었습니다: {json_path}")
            self.status_var.set(f"✅ 저장 완료! ({self.click_count}/{self.max_clicks})")
            self.save_path_var.set(f"저장 위치: {json_path}")
            
        except Exception as e:
            print(f"❌ 저장 실패: {e}")
            self.status_var.set(f"❌ 저장 실패: {e}")
    
    def reset_clicks(self):
        """클릭 정보를 초기화합니다."""
        self.click_count = 0
        self.click_coordinates = []
        
        # 캔버스에서 마커 제거
        for marker in self.click_markers:
            self.canvas.delete(marker)
        self.click_markers = []
        
        # 텍스트 제거
        for i in range(1, self.max_clicks + 1):
            self.canvas.delete(f"marker_{i}")
            self.canvas.delete(f"text_{i}")
        
        self.status_var.set(f"클릭 진행: 0/{self.max_clicks} (초기화 완료)")
        self.save_path_var.set("")
        print("클릭 정보가 초기화되었습니다.")


def main(artwork_name: str):
    """메인 함수"""
    root = tk.Tk()
    
    try:
        app = ClickCollector(root, artwork_name=artwork_name)
        
        print("=" * 60)
        print(f"작품: {artwork_name}")
        print(f"목표: {app.max_clicks}번의 클릭")
        print("=" * 60)
        print("사용법:")
        print("1. 이미지에서 원하는 위치를 클릭하세요")
        print("2. 클릭할 때마다 빨간 원과 번호가 표시됩니다")
        print("3. 20번 클릭하면 자동으로 JSON 파일로 저장됩니다")
        print("4. '수동 저장' 버튼으로 언제든지 저장 가능합니다")
        print("5. '초기화' 버튼으로 클릭 정보를 초기화할 수 있습니다")
        print("=" * 60)
        
        root.mainloop()
        
    except FileNotFoundError as e:
        print(f"오류: {e}")
        root.destroy()
    except Exception as e:
        print(f"예상치 못한 오류: {e}")
        root.destroy()


if __name__ == "__main__":
    args = tyro.cli(Config)
    main(artwork_name=args.artwork_name)

