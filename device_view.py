import flet as ft
from typing import Optional, Callable


class DeviceView:
    """设备屏幕显示视图类"""
    
    def __init__(self, on_send_message: Optional[Callable] = None):
        self.on_send_message = on_send_message
        self.device_image_ref = ft.Ref[ft.Image]()
        self.chat_input_ref = ft.Ref[ft.TextField]()
        self.listview_ref = ft.Ref[ft.ListView]()
        
        # 创建设备屏幕图像控件
        self.device_image = ft.Image(
            src="https://via.placeholder.com/300x400/0000FF/FFFFFF?text=Device+Screen",
            width=300,
            height=400,
            fit=ft.ImageFit.CONTAIN,
            border_radius=8,
            ref=self.device_image_ref,
            gapless_playback=True,
            repeat=ft.ImageRepeat.NO_REPEAT,
            visible=True
        )
        
        # 创建聊天输入框
        self.chat_input = ft.TextField(
            hint_text="Type your message here...",
            expand=True,
            multiline=True,
            min_lines=1,
            max_lines=3,
            border_radius=8,
            border_color=ft.Colors.GREY_400,
            ref=self.chat_input_ref
        )
        
        # 创建发送按钮
        self.send_button = ft.ElevatedButton(
            text="Send",
            on_click=self._on_send_click,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.BLUE_600,
                color=ft.Colors.WHITE,
                shape=ft.RoundedRectangleBorder(radius=8)
            )
        )
        
        # 创建 ListView
        self.listview = ft.ListView(
            controls=[
                ft.Container(
                    content=ft.Column([
                        ft.Text("Device Screen", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_600),
                        ft.Container(
                            content=self.device_image,
                            border=ft.border.all(1, ft.Colors.GREY_300),
                            border_radius=8,
                            padding=5
                        )
                    ], spacing=5),
                    padding=ft.padding.all(10),
                    border_radius=8,
                    bgcolor=ft.Colors.BLUE_50
                )
            ],
            expand=True,
            spacing=5,
            padding=ft.padding.all(10),
            auto_scroll=True,
            ref=self.listview_ref
        )
        
        # 创建测试按钮
        self.test_button = ft.ElevatedButton(
            text="Test Update Image",
            on_click=self._on_test_update_click,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.GREEN_600,
                color=ft.Colors.WHITE,
                shape=ft.RoundedRectangleBorder(radius=8)
            )
        )
        
        # 创建完整的聊天界面
        self.content = ft.Container(
            content=ft.Column([
                # Test button area
                ft.Container(
                    content=ft.Row([
                        self.test_button,
                        ft.Text("Click to manually update device image", size=12, color=ft.Colors.GREY_600)
                    ], spacing=10),
                    padding=ft.padding.symmetric(vertical=5),
                    bgcolor=ft.Colors.YELLOW_50,
                    border_radius=8
                ),
                # Chat history area
                ft.Container(
                    content=self.listview,
                    expand=True,
                    border=ft.border.all(1, ft.Colors.GREY_300),
                    border_radius=8,
                    bgcolor=ft.Colors.WHITE
                ),
                # Input area
                ft.Container(
                    content=ft.Row([
                        self.chat_input,
                        self.send_button
                    ], spacing=10),
                    padding=ft.padding.all(10),
                    bgcolor=ft.Colors.GREY_50,
                    border_radius=8
                )
            ], spacing=10),
            expand=True,
            padding=ft.padding.all(10)
        )
    
    def _on_send_click(self, e):
        """发送按钮点击事件"""
        if self.on_send_message and self.chat_input.value.strip():
            self.on_send_message(self.chat_input.value)
            self.chat_input.value = ""
            self.chat_input.update()
    
    def _on_test_update_click(self, e):
        """测试更新图像按钮点击事件"""
        # 生成一个测试图像
        import base64
        import io
        from PIL import Image, ImageDraw
        import time
        
        # 创建一个简单的测试图像
        img = Image.new('RGB', (300, 400), color='lightgreen')
        draw = ImageDraw.Draw(img)
        
        # 添加文本
        draw.text((10, 10), f"Test Image {int(time.time())}", fill='black')
        draw.text((10, 40), "Manual Update", fill='red')
        draw.text((10, 70), "Android Device", fill='blue')
        
        # 添加一些图形
        draw.rectangle([50, 100, 250, 200], outline='red', width=3)
        draw.ellipse([100, 120, 200, 180], outline='blue', width=2)
        
        # 转换为base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        data_uri = f"data:image/png;base64,{img_base64}"
        
        # 更新图像
        self.update_device_image(data_uri)
        print("Manual test image update triggered")
    
    def update_device_image(self, base64_image: str):
        """更新设备屏幕图像"""
        print(f"DEBUG: update_device_image called - base64_image: {bool(base64_image)}, ref: {bool(self.device_image_ref.current)}")
        
        if base64_image and self.device_image_ref.current:
            # 图像提供者已经返回了正确的data URI格式，直接使用
            print(f"DEBUG: Setting image src, length: {len(base64_image)}")
            print(f"DEBUG: Image src starts with: {base64_image[:50]}...")
            
            # 直接更新图像（现在在主线程中调用）
            self.device_image_ref.current.src = base64_image
            self.device_image_ref.current.update()
            
            # 强制刷新ListView以确保图像显示
            if self.listview_ref.current:
                self.listview_ref.current.update()
                print(f"DEBUG: ListView refreshed")
            
            print(f"DEBUG: Image updated successfully")
        else:
            print(f"DEBUG: Cannot update image - base64_image: {bool(base64_image)}, ref: {bool(self.device_image_ref.current)}")
    
    def add_message(self, message: str, is_user: bool = True):
        """添加聊天消息"""
        message_color = ft.Colors.BLUE_600 if is_user else ft.Colors.GREY_700
        bg_color = ft.Colors.BLUE_50 if is_user else ft.Colors.GREY_100
        
        message_container = ft.Container(
            content=ft.Text(
                message,
                color=message_color,
                size=14
            ),
            padding=ft.padding.all(10),
            border_radius=8,
            bgcolor=bg_color,
            margin=ft.margin.symmetric(vertical=2)
        )
        
        if self.listview_ref.current:
            self.listview_ref.current.controls.append(message_container)
            self.listview_ref.current.update()
    
    def clear_messages(self):
        """清空所有消息（保留设备屏幕）"""
        if self.listview_ref.current:
            # 保留第一个设备屏幕控件
            device_screen = self.listview_ref.current.controls[0] if self.listview_ref.current.controls else None
            self.listview_ref.current.controls = [device_screen] if device_screen else []
            self.listview_ref.current.update()
    
    def get_device_image_control(self) -> Optional[ft.Image]:
        """获取设备图像控件引用"""
        return self.device_image_ref.current
    
    def get_listview_control(self) -> Optional[ft.ListView]:
        """获取 ListView 控件引用"""
        return self.listview_ref.current
