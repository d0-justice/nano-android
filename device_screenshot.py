
import flet as ft
import base64
import io
from PIL import Image, ImageDraw
from datetime import datetime
from typing import Optional


class DeviceScreenshot(ft.Container):
    """设备截图显示组件，与DeviceView保持相同的布局和样式"""
    
    def __init__(self, bgcolor=None, **kwargs):
        # 创建图像引用
        self.device_image_ref = ft.Ref[ft.Image]()
        
        # 创建设备屏幕图像控件 - 与DeviceView完全相同的配置
        placeholder_image = self._create_placeholder_image()
        self.device_image = ft.Image(
            src_base64=placeholder_image,
            width=None,  # 宽度自适应容器
            height=None,  # 高度自适应容器
            fit=ft.ImageFit.CONTAIN,
            border_radius=8,
            ref=self.device_image_ref,
            gapless_playback=True,
            repeat=ft.ImageRepeat.NO_REPEAT,
            visible=True
        )
        
        # 创建与DeviceView相同的布局结构 - 只包含图像，不显示时间戳
        device_content = ft.Column([
            # 设备屏幕图像 - 占满整个容器
            self.device_image
        ], spacing=0, alignment=ft.MainAxisAlignment.CENTER, expand=True)
        
        # 调用父类构造函数 - 与DeviceView完全相同的样式
        super().__init__(
            content=device_content,
            expand=True,
            padding=ft.padding.all(5),  # 添加内边距
            alignment=ft.alignment.center,
            bgcolor=bgcolor if bgcolor is not None else ft.Colors.WHITE,  # 使用传入的背景色或默认白色
            border_radius=8,  # 圆角
            border=ft.border.all(1, ft.Colors.with_opacity(0.2, ft.Colors.GREY)),  # 灰色边框
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=8,
                color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK),
                offset=ft.Offset(1, 2)  # 右下方向
            ),
            **kwargs
        )
    
    def _create_placeholder_image(self) -> str:
        """创建占位符图像，与DeviceView保持一致"""
        img = Image.new('RGB', (280, 350), color='lightgray')
        draw = ImageDraw.Draw(img)
        
        # 添加占位符文本
        draw.text((10, 10), "Screenshot", fill='gray')
        draw.text((10, 40), "Press F2 to capture", fill='darkgray')
        
        # 转换为base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    def update_screenshot(self, current_frame):
        """更新截图显示 - 直接复制DeviceView的图像数据"""
        try:
            # 直接使用OpenCV帧数据转换为base64
            if current_frame is not None:
                import cv2
                
                # 将OpenCV图像转换为PIL图像
                frame_rgb = cv2.cvtColor(current_frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(frame_rgb)
                
                # 转换为base64
                buffer = io.BytesIO()
                pil_image.save(buffer, format='PNG')
                img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                
                # 更新图像显示 - 使用与DeviceView相同的逻辑
                if self.device_image_ref.current:
                    self.device_image_ref.current.src_base64 = img_base64
                    self.device_image_ref.current.src = None
                    self.device_image_ref.current.update()
                    
                print(f"截图已更新")
                
        except Exception as e:
            print(f"更新截图失败: {e}")
    
    def clear_screenshot(self):
        """清除截图，显示占位符"""
        placeholder_image = self._create_placeholder_image()
        if self.device_image_ref.current:
            self.device_image_ref.current.src_base64 = placeholder_image
            self.device_image_ref.current.src = None
            self.device_image_ref.current.update()
    
    def get_screenshot_data(self) -> Optional[str]:
        """获取当前截图的base64数据"""
        if self.device_image_ref.current:
            return self.device_image_ref.current.src_base64
        return None