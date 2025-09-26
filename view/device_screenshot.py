
import flet as ft
import base64
import io
from PIL import Image, ImageDraw
from datetime import datetime
from typing import Optional, List, Dict, Any


class DeviceScreenshot(ft.Container):
    """设备截图显示组件，与DeviceView保持相同的布局和样"""
    
    def __init__(self, bgcolor=None, **kwargs):
        # 创建图像引用
        self.device_image_ref = ft.Ref[ft.Image]()
        self.overlay_stack_ref = ft.Ref[ft.Stack]()
        
        # UI可视化相"
        self.ui_elements = []
        self.selected_element_id = None
        self.on_element_select_callback = None
        
        # 创建设备屏幕图像控件 - 与DeviceView完全相同的配"
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
        
        # 创建UI元素覆盖"
        self.overlay_stack = ft.Stack(
            controls=[self.device_image],  # 底层是截图图"
            ref=self.overlay_stack_ref,
            expand=True
        )
        
        # 创建与DeviceView相同的布局结构 - 使用Stack来支持覆盖层
        device_content = ft.Column([
            # 设备屏幕图像和覆盖层 - 占满整个容器
            self.overlay_stack
        ], spacing=0, alignment=ft.MainAxisAlignment.CENTER, expand=True)
        
        # 调用父类构造函"- 与DeviceView完全相同的样"
        super().__init__(
            content=device_content,
            expand=True,
            padding=ft.padding.all(5),  # 添加内边"
            alignment=ft.alignment.center,
            bgcolor=bgcolor if bgcolor is not None else ft.Colors.WHITE,  # 使用传入的背景色或默认白"
            border_radius=8,  # 圆角
            border=ft.border.all(1, ft.Colors.with_opacity(0.2, ft.Colors.GREY)),  # 灰色边框
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=8,
                color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK),
                offset=ft.Offset(1, 2)  # 右下方向阴影
            ),
            animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT),  # 添加动画效果
            **kwargs
        )
    
    def _create_placeholder_image(self) -> str:
        """ 创建占位符图像，与DeviceView保持一"""
        img = Image.new('RGB', (280, 350), color='lightgray')
        draw = ImageDraw.Draw(img)
        
        # 添加占位符文"
        draw.text((10, 10), "Screenshot", fill='gray')
        draw.text((10, 40), "Press F2 to capture", fill='darkgray')
        
        # 转换为base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    def update_screenshot(self, current_frame):
        """更新截图显示 - 直接复制DeviceView的图像数"""
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
                    try:
                        # 检查组件是否已添加到页"
                        if not hasattr(self.device_image_ref.current, 'page') or not self.device_image_ref.current.page:
                            print("DEBUG: Screenshot image control not added to page yet, skipping update")
                            return
                            
                        self.device_image_ref.current.src_base64 = img_base64
                        self.device_image_ref.current.src = None
                        self.device_image_ref.current.update()
                        print(f"截图已更")
                    except Exception as update_error:
                        print(f"UI更新错误: {update_error}")
                else:
                    print("设备图像引用为空，跳过更")
                
        except Exception as e:
            print(f"更新截图失败: {e}")
    
    def get_screenshot_data(self) -> Optional[str]:
        """获取当前截图的base64数据 """
        if self.device_image_ref.current:
            return self.device_image_ref.current.src_base64
        return None
    
    def set_ui_elements(self, elements: List[Dict[str, Any]]):
        """设置UI元素数据并创建可视化覆盖"""
        self.ui_elements = elements
        self._create_ui_overlay()
    
    def set_element_select_callback(self, callback):
        """设置元素选择回调函数"""
        self.on_element_select_callback = callback
    
    def _create_ui_overlay(self):
        """创建UI元素的可视化覆盖"""
        try:
            if not self.overlay_stack_ref.current:
                return
                
            # 清除现有的覆盖层控件（保留底层图像）
            overlay_controls = [self.device_image]
            
            # 为每个UI元素创建透明容器
            for element in self.ui_elements:
                overlay_container = self._create_element_overlay(element)
                if overlay_container:
                    overlay_controls.append(overlay_container)
            
            # 更新Stack的控件列"
            self.overlay_stack_ref.current.controls = overlay_controls
            self.overlay_stack_ref.current.update()
            
            print(f"UI覆盖层已更新，共{len(overlay_controls)-1}个元")
            
        except Exception as e:
            print(f"创建UI覆盖层失败: {e}")
    
    def _create_element_overlay(self, element: Dict[str, Any]) -> Optional[ft.Container]:
        """为单个元素创建透明覆盖容器"""
        try:
            # 获取元素边界信息
            bounds = element.get('bounds', '0,0,0,0')
            if isinstance(bounds, str):
                # 解析bounds字符串，格式通常""left,top,right,bottom"
                coords = bounds.replace('[', '').replace(']', '').split(',')
                if len(coords) >= 4:
                    left, top, right, bottom = map(int, coords[:4])
                else:
                    return None
            else:
                return None
                
            # 计算元素在截图中的相对位置和大小
            element_width = right - left
            element_height = bottom - top
            
            # 如果元素太小，跳"
            if element_width <= 5 or element_height <= 5:
                return None
                
            # 创建透明容器
            element_id = element.get('resource-id', f"element_{left}_{top}")
            is_selected = element_id == self.selected_element_id
            
            # 根据是否选中设置边框颜色
            border_color = ft.Colors.RED if is_selected else ft.Colors.BLUE_400
            border_width = 3 if is_selected else 1
            
            overlay_container = ft.Container(
                width=element_width,
                height=element_height,
                left=left,
                top=top,
                bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.BLUE) if not is_selected else ft.Colors.with_opacity(0.2, ft.Colors.RED),
                border=ft.border.all(border_width, border_color),
                border_radius=2,
                tooltip=f"{element.get('class', 'Unknown')}: {element.get('text', 'No text')}",
                on_click=lambda e, elem=element: self._on_element_click(elem),
                animate=ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT)
            )
            
            return overlay_container
            
        except Exception as e:
            print(f"创建元素覆盖容器失败: {e}")
            return None
    
    def _on_element_click(self, element: Dict[str, Any]):
        """处理元素点击事件"""
        element_id = element.get('resource-id', f"element_{element.get('bounds', '')}")
        self.selected_element_id = element_id
        
        # 重新创建覆盖层以更新选中状"
        self._create_ui_overlay()
        
        # 调用回调函数
        if self.on_element_select_callback:
            self.on_element_select_callback(element)
            
        print(f"选中元素: {element.get('class', 'Unknown')} - {element.get('text', 'No text')}")
    
    def clear_ui_overlay(self):
        """清除UI覆盖"""
        try:
            if self.overlay_stack_ref.current:
                self.overlay_stack_ref.current.controls = [self.device_image]
                self.overlay_stack_ref.current.update()
            self.ui_elements = []
            self.selected_element_id = None
            print("UI覆盖层已清除")
        except Exception as e:
            print(f"清除UI覆盖层失败: {e}")