import sys
import json
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QFileDialog, QMessageBox, QHBoxLayout
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QPoint


class ImageBoundingBoxApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("이미지 Bounding Box 선택기")
        self.setGeometry(100, 100, 1000, 800)
        
        # 상태 변수들
        self.image_path = None
        self.original_pixmap = None
        self.click_points = []  # 현재 클릭한 두 점을 저장
        self.bounding_boxes = []  # 완성된 바운딩 박스들을 저장
        
        self.init_ui()
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        # 버튼 레이아웃
        button_layout = QHBoxLayout()
        
        # 이미지 로드 버튼
        self.load_button = QPushButton("이미지 열기")
        self.load_button.clicked.connect(self.load_image)
        button_layout.addWidget(self.load_button)
        
        # 현재 포인트 초기화 버튼
        self.reset_current_button = QPushButton("현재 포인트 초기화")
        self.reset_current_button.clicked.connect(self.reset_current_points)
        button_layout.addWidget(self.reset_current_button)
        
        # 모든 박스 삭제 버튼
        self.clear_all_button = QPushButton("모든 박스 삭제")
        self.clear_all_button.clicked.connect(self.clear_all_boxes)
        button_layout.addWidget(self.clear_all_button)
        
        # 저장 버튼
        self.save_button = QPushButton("모든 박스 저장")
        self.save_button.clicked.connect(self.save_all_boxes)
        button_layout.addWidget(self.save_button)
        
        layout.addLayout(button_layout)
        
        # 이미지 표시 라벨
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("border: 1px solid black; background-color: white;")
        self.image_label.setMinimumSize(800, 600)
        self.image_label.mousePressEvent = self.on_image_click
        layout.addWidget(self.image_label)
        
        # 상태 표시 라벨
        self.status_label = QLabel("이미지를 로드하고 두 점을 클릭하여 바운딩 박스를 만드세요.")
        layout.addWidget(self.status_label)
        
        # 박스 개수 표시 라벨
        self.count_label = QLabel("생성된 바운딩 박스: 0개")
        layout.addWidget(self.count_label)
        
        central_widget.setLayout(layout)
        
    def load_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "이미지 파일 선택", 
            "images/", 
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        
        if file_path:
            self.image_path = file_path
            self.original_pixmap = QPixmap(file_path)
            
            # 이미지 크기를 라벨에 맞게 조정
            scaled_pixmap = self.original_pixmap.scaled(
                self.image_label.size(), 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)
            
            # 상태 초기화
            self.click_points = []
            self.bounding_boxes = []
            self.update_status()
            
    def on_image_click(self, event):
        if self.original_pixmap is None:
            QMessageBox.warning(self, "경고", "먼저 이미지를 로드해주세요.")
            return
            
        if len(self.click_points) >= 2:
            QMessageBox.information(self, "정보", "이미 두 점이 선택되었습니다. '현재 포인트 초기화'를 눌러 다시 시작하거나 새로운 박스를 만드세요.")
            return
            
        # 클릭한 위치의 실제 이미지 좌표 계산
        click_pos = event.pos()
        image_pos = self.convert_to_image_coordinates(click_pos)
        
        if image_pos:
            self.click_points.append(image_pos)
            
            # 두 점이 모두 선택되면 바운딩 박스 생성
            if len(self.click_points) == 2:
                self.create_bounding_box()
            
            self.update_status()
            # 이미지 업데이트 (점과 박스 그리기)
            self.update_image_display()
                
    def convert_to_image_coordinates(self, label_pos):
        """라벨 좌표를 실제 이미지 좌표로 변환"""
        if self.original_pixmap is None:
            return None
            
        label_size = self.image_label.size()
        pixmap_size = self.image_label.pixmap().size()
        
        # 이미지가 라벨 내에서 중앙 정렬되어 있으므로 오프셋 계산
        x_offset = (label_size.width() - pixmap_size.width()) // 2
        y_offset = (label_size.height() - pixmap_size.height()) // 2
        
        # 라벨 좌표에서 이미지 좌표로 변환
        image_x = label_pos.x() - x_offset
        image_y = label_pos.y() - y_offset
        
        # 이미지 영역 내의 클릭인지 확인
        if 0 <= image_x < pixmap_size.width() and 0 <= image_y < pixmap_size.height():
            # 스케일된 이미지 좌표를 원본 이미지 좌표로 변환
            scale_x = self.original_pixmap.width() / pixmap_size.width()
            scale_y = self.original_pixmap.height() / pixmap_size.height()
            
            original_x = int(image_x * scale_x)
            original_y = int(image_y * scale_y)
            
            return QPoint(original_x, original_y)
        
        return None
    
    def create_bounding_box(self):
        """두 점으로부터 바운딩 박스 생성하고 리스트에 추가"""
        if len(self.click_points) != 2:
            return
            
        p1, p2 = self.click_points
        
        # 좌상단 좌표 계산
        left = min(p1.x(), p2.x())
        top = min(p1.y(), p2.y())
        
        # 가로, 세로 크기 계산
        width = abs(p2.x() - p1.x())
        height = abs(p2.y() - p1.y())
        
        # 바운딩 박스 정보 생성
        bbox_info = {
            "id": len(self.bounding_boxes) + 1,
            "x": left,
            "y": top,
            "width": width,
            "height": height
        }
        
        # 리스트에 추가
        self.bounding_boxes.append(bbox_info)
        
        # 현재 클릭 포인트 초기화 (새로운 박스를 만들 수 있도록)
        self.click_points = []
        
        # 카운트 업데이트
        self.count_label.setText(f"생성된 바운딩 박스: {len(self.bounding_boxes)}개")
        
    def update_image_display(self):
        """이미지에 모든 바운딩 박스들과 현재 클릭한 점들을 그려서 표시"""
        if self.original_pixmap is None:
            return
            
        # 스케일된 이미지 복사본 생성
        scaled_pixmap = self.original_pixmap.scaled(
            self.image_label.size(), 
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        )
        
        # QPainter로 점과 박스 그리기
        painter = QPainter(scaled_pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 원본 이미지 좌표를 스케일된 이미지 좌표로 변환하는 비율
        scale_x = scaled_pixmap.width() / self.original_pixmap.width()
        scale_y = scaled_pixmap.height() / self.original_pixmap.height()
        
        # 완성된 바운딩 박스들 그리기 (녹색)
        painter.setPen(QPen(QColor(0, 255, 0), 2))
        for i, bbox in enumerate(self.bounding_boxes):
            x = bbox["x"] * scale_x
            y = bbox["y"] * scale_y
            w = bbox["width"] * scale_x
            h = bbox["height"] * scale_y
            painter.drawRect(int(x), int(y), int(w), int(h))
            
            # 박스 번호 표시
            painter.setPen(QPen(QColor(255, 255, 0), 1))
            painter.drawText(int(x + 5), int(y + 15), f"#{bbox['id']}")
            painter.setPen(QPen(QColor(0, 255, 0), 2))
        
        # 현재 클릭한 점들 그리기 (빨간색)
        painter.setPen(QPen(QColor(255, 0, 0), 4))
        for point in self.click_points:
            scaled_x = int(point.x() * scale_x)
            scaled_y = int(point.y() * scale_y)
            painter.drawEllipse(scaled_x - 3, scaled_y - 3, 6, 6)
            
        # 현재 진행 중인 바운딩 박스 그리기 (파란색 점선)
        if len(self.click_points) == 2:
            painter.setPen(QPen(QColor(0, 0, 255), 2, Qt.DashLine))
            
            p1, p2 = self.click_points
            x1, y1 = p1.x() * scale_x, p1.y() * scale_y
            x2, y2 = p2.x() * scale_x, p2.y() * scale_y
            
            # 좌상단과 우하단 계산
            left = min(x1, x2)
            top = min(y1, y2)
            width = abs(x2 - x1)
            height = abs(y2 - y1)
            
            painter.drawRect(int(left), int(top), int(width), int(height))
            
        painter.end()
        self.image_label.setPixmap(scaled_pixmap)
    
    def update_status(self):
        """상태 메시지 업데이트"""
        if len(self.click_points) == 0:
            self.status_label.setText(f"새로운 바운딩 박스를 만들려면 첫 번째 점을 클릭하세요. (현재 {len(self.bounding_boxes)}개 박스)")
        elif len(self.click_points) == 1:
            point = self.click_points[0]
            self.status_label.setText(f"첫 번째 점 선택됨: ({point.x()}, {point.y()}) - 두 번째 점을 클릭하세요.")
        elif len(self.click_points) == 2:
            self.status_label.setText(f"바운딩 박스가 생성되었습니다! 새로운 박스를 만들려면 다시 클릭하세요.")
        
    def reset_current_points(self):
        """현재 선택한 점들만 초기화"""
        self.click_points = []
        self.update_status()
        self.update_image_display()
        
    def clear_all_boxes(self):
        """모든 바운딩 박스 삭제"""
        if not self.bounding_boxes and not self.click_points:
            QMessageBox.information(self, "정보", "삭제할 바운딩 박스가 없습니다.")
            return
            
        reply = QMessageBox.question(
            self, 
            "확인", 
            f"모든 바운딩 박스({len(self.bounding_boxes)}개)와 현재 포인트를 삭제하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.bounding_boxes = []
            self.click_points = []
            self.count_label.setText("생성된 바운딩 박스: 0개")
            self.update_status()
            self.update_image_display()
        
    def save_all_boxes(self):
        """모든 바운딩 박스 정보를 JSON 파일로 저장"""
        if not self.bounding_boxes:
            QMessageBox.warning(self, "경고", "저장할 바운딩 박스가 없습니다.")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "바운딩 박스 정보 저장", 
            "bounding_boxes.json", 
            "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                # 저장할 데이터 구성
                save_data = {
                    "image_path": self.image_path,
                    "image_width": self.original_pixmap.width(),
                    "image_height": self.original_pixmap.height(),
                    "total_boxes": len(self.bounding_boxes),
                    "bounding_boxes": self.bounding_boxes
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(save_data, f, indent=2, ensure_ascii=False)
                    
                QMessageBox.information(
                    self, 
                    "저장 완료", 
                    f"{len(self.bounding_boxes)}개의 바운딩 박스 정보가 저장되었습니다:\n{file_path}"
                )
                print(f"저장된 바운딩 박스 정보:")
                for bbox in self.bounding_boxes:
                    print(f"  박스 #{bbox['id']}: 좌상단({bbox['x']}, {bbox['y']}), 크기({bbox['width']} x {bbox['height']})")
                    
            except Exception as e:
                QMessageBox.critical(self, "저장 실패", f"파일 저장 중 오류가 발생했습니다:\n{str(e)}")


def main():
    app = QApplication(sys.argv)
    window = ImageBoundingBoxApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
