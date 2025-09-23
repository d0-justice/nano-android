import flet as ft
from typing import Optional, Callable
import threading
import sys
import os
import time
import numpy as np
import cv2
import base64

# 添加scrcpy模块路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'scrcpy'))
from scrcpy.core import Client
import scrcpy.const as const


class DeviceView(ft.Container):
    """设备屏幕显示视图类"""
    
    def __init__(self, device_name: str = None, bgcolor=None, **kwargs):
        self.device_name = device_name or "未选择设备"
        self.device_image_ref = ft.Ref[ft.Image]()
        self.rlock = threading.RLock()
        self.current_frame = None
        self.client = None
        self.is_ui_active = True  # 标记UI是否仍然活跃
        
        # 鼠标状态跟踪
        self.mouse_left_down = False
        self.mouse_right_down = False
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        self.key_alt_down = False
        self.key_ctrl_down = False
        self.mouse_x = 0
        self.mouse_y = 0
        self.ori_x = 0
        self.ori_y = 0
        
        # 创建设备屏幕图像控件 - 使用base64格式的占位符图像
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
        
        # 使用GestureDetector来正确处理鼠标事件和获取坐标
        self.gesture_detector = ft.GestureDetector(
            content=self.device_image,
            on_tap_down=self._on_tap_down,
            on_pan_start=self._on_pan_start,
            on_pan_update=self._on_pan_update,
            on_pan_end=self._on_pan_end,
        )
        
        # 创建简化的设备屏幕显示界面 - 移除按钮
        device_content = ft.Column([
            # 设备屏幕图像 - 占满整个容器
            self.gesture_detector
        ], spacing=0, alignment=ft.MainAxisAlignment.CENTER, expand=True)
        
        # 调用父类构造函数
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
                offset=ft.Offset(1, 2)  # 右下方向阴影
            ),
            animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT),  # 添加动画效果
            # 移除这里的事件绑定，因为已经绑定到图像容器上了
            **kwargs
        )
        
        # 如果提供了有效的设备名，则自动连接
        if device_name and device_name != "未选择设备":
            # 使用线程延迟自动连接，避免阻塞UI初始化
            threading.Timer(1.0, self._auto_connect).start()
    
    def _create_placeholder_image(self):
        """创建占位符图像"""
        import base64
        import io
        from PIL import Image, ImageDraw
        
        # 创建一个简单的占位符图像
        img = Image.new('RGB', (280, 350), color='lightgray')
        draw = ImageDraw.Draw(img)
        
        # 添加文本
        draw.text((10, 10), "Android Device", fill='black')
        draw.text((10, 40), "Waiting for connection...", fill='gray')
        
        # 添加一个简单的边框
        draw.rectangle([5, 5, 275, 345], outline='darkgray', width=2)
        
        # 转换为base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return img_base64
    
    def _on_test_update_click(self, e):
        """测试更新图像按钮点击事件"""
        # 生成一个测试图像
        import base64
        import io
        from PIL import Image, ImageDraw
        import time
        
        # 创建一个简单的测试图像
        img = Image.new('RGB', (280, 350), color='lightgreen')
        draw = ImageDraw.Draw(img)
        
        # 添加文本
        draw.text((10, 10), f"Test Image {int(time.time())}", fill='black')
        draw.text((10, 40), "Manual Update", fill='red')
        draw.text((10, 70), "Android Device", fill='blue')
        
        # 添加一些图形
        draw.rectangle([20, 100, 260, 200], outline='red', width=3)
        draw.ellipse([50, 120, 230, 180], outline='blue', width=2)
        
        # 转换为base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        # 更新图像
        self.update_device_image(img_base64)
        print("Manual test image update triggered")
    
    def _on_connect_click(self, e):
        """连接设备按钮点击事件"""
        if self.client is None:
            self._connect_to_device()
        else:
            self._disconnect_device()
    
    def _connect_to_device(self):
        """连接到Android设备"""
        try:
            # 检查设备名是否有效
            if self.device_name == "未选择设备" or not self.device_name:
                print("请先选择有效的设备名")
                return
                
            print(f"正在连接设备: {self.device_name}")
            self.client = Client(device=self.device_name, max_width=800, bitrate=4000000, max_fps=20, connection_timeout=10000)
            print("正在添加帧监听器...")
            self.client.add_listener("frame", self.on_frame)
            print("正在启动客户端...")
            self.client.start(threaded=True)
            print(f"成功连接到设备 {self.device_name}")
                
        except Exception as e:
            print(f"连接设备失败: {e}")
            self.client = None
    
    def _auto_connect(self):
        """自动连接设备的方法"""
        print(f"开始自动连接设备: {self.device_name}")
        self._connect_to_device()
    
    def _disconnect_device(self):
        """断开设备连接"""
        if self.client:
            try:
                self.client.stop()
                self.client = None
                print("设备连接已断开")
                
                # 更新按钮状态
                if self.connect_button:
                    self.connect_button.text = "Connect Device"
                    self.connect_button.style.bgcolor = ft.Colors.BLUE_600
                    self.connect_button.update()
                    
                # 显示占位符图像
                self._show_waiting_placeholder()
                
            except Exception as e:
                print(f"断开连接失败: {e}")
    
    def on_frame(self, frame):
        """处理从scrcpy接收到的帧数据"""
        if frame is not None and frame.size > 0:
            try:
                self.rlock.acquire()
                # 存储当前帧
                self.current_frame = frame
                
                if not hasattr(self, 'frame_count'):
                    self.frame_count = 0
                    self.last_frame_info_time = time.time()
                
                self.frame_count += 1
                image_height, image_width, image_depth = frame.shape
                
                # 减少日志输出频率
                current_time = time.time()
                if current_time - self.last_frame_info_time > 1.0:
                    print(f"收到帧: {image_width}x{image_height}, FPS: {self.frame_count}")
                    self.frame_count = 0
                    self.last_frame_info_time = current_time
                
                # 将OpenCV图像转换为base64格式并更新UI
                self._update_ui_with_frame(frame, image_width, image_height)
                        
            except Exception as e:
                print(f"帧处理错误: {e}")
            finally:
                self.rlock.release()
    
    def _update_ui_with_frame(self, display_frame, image_width, image_height):
        """更新UI显示帧数据"""
        # 检查UI是否仍然活跃
        if not self.is_ui_active:
            return
            
        if self.device_image_ref.current:
            try:
                # 确保数据类型为uint8
                if display_frame.dtype != np.uint8:
                    display_frame = display_frame.astype(np.uint8)
                
                # scrcpy的帧数据通常已经是RGB格式
                rgb_frame = display_frame
                
                # 转换为base64编码
                _, buffer = cv2.imencode('.jpg', rgb_frame)
                img_str = base64.b64encode(buffer).decode('utf-8')
                
                # 更新图像
                self.device_image_ref.current.src_base64 = img_str
                self.device_image_ref.current.src = None
                
                # 安全地更新UI
                try:
                    self.device_image_ref.current.update()
                except Exception as update_error:
                    # 如果更新失败，可能是因为event loop已关闭
                    if "Event loop is closed" in str(update_error):
                        self.is_ui_active = False
                        print("检测到Event loop已关闭，停止UI更新")
                    else:
                        print(f"UI更新错误: {update_error}")
                
            except Exception as e:
                print(f"UI更新错误: {e}")
    
    def update_device_image(self, image_data: str):
        """更新设备屏幕图像"""
        print(f"DEBUG: update_device_image called - image_data: {bool(image_data)}, ref: {bool(self.device_image_ref.current)}")
        
        if image_data and self.device_image_ref.current:
            try:
                # 检查图像数据格式
                if image_data.startswith('data:image/'):
                    # 如果是data URI格式，直接使用
                    print(f"DEBUG: Using data URI format, length: {len(image_data)}")
                    self.device_image_ref.current.src = image_data
                    self.device_image_ref.current.src_base64 = None
                elif image_data.startswith('/9j/') or image_data.startswith('iVBOR'):
                    # 如果是纯base64数据，使用src_base64
                    print(f"DEBUG: Using base64 format, length: {len(image_data)}")
                    self.device_image_ref.current.src_base64 = image_data
                    self.device_image_ref.current.src = None
                else:
                    # 尝试作为base64处理
                    print(f"DEBUG: Treating as base64 data, length: {len(image_data)}")
                    self.device_image_ref.current.src_base64 = image_data
                    self.device_image_ref.current.src = None
                
                # 更新图像控件
                self.device_image_ref.current.update()
                print(f"DEBUG: Image updated successfully")
                
            except Exception as e:
                print(f"DEBUG: Error updating image: {e}")
                # 如果更新失败，显示错误占位符
                self._show_error_placeholder()
        else:
            print(f"DEBUG: Cannot update image - image_data: {bool(image_data)}, ref: {bool(self.device_image_ref.current)}")
            # 显示等待占位符
            self._show_waiting_placeholder()
    
    def _show_waiting_placeholder(self):
        """显示等待占位符图像"""
        if self.device_image_ref.current:
            waiting_image = self._create_placeholder_image()
            self.device_image_ref.current.src_base64 = waiting_image
            self.device_image_ref.current.src = None
            self.device_image_ref.current.update()
    
    def _show_error_placeholder(self):
        """显示错误占位符图像"""
        import base64
        import io
        from PIL import Image, ImageDraw
        
        # 创建错误占位符图像
        img = Image.new('RGB', (280, 350), color='lightcoral')
        draw = ImageDraw.Draw(img)
        
        # 添加错误信息
        draw.text((10, 10), "Connection Error", fill='darkred')
        draw.text((10, 40), "Failed to update image", fill='red')
        
        # 转换为base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        if self.device_image_ref.current:
            self.device_image_ref.current.src_base64 = img_base64
            self.device_image_ref.current.src = None
            self.device_image_ref.current.update()
    
    def get_device_image_control(self) -> Optional[ft.Image]:
        """获取设备图像控件引用"""
        return self.device_image_ref.current
    
    def cleanup(self):
        """清理资源"""
        print(f"开始清理DeviceView资源: {self.device_name}")
        self.is_ui_active = False  # 标记UI不再活跃
        if self.client:
            print(f"正在停止客户端: {self.device_name}")
            self.client.stop()
            self.client = None
            print(f"客户端已停止: {self.device_name}")
        print(f"DeviceView资源清理完成: {self.device_name}")
    
    # Flet事件处理器 - 使用GestureDetector的事件
    def _on_tap_down(self, e):
        """处理点击事件"""
        try:
            # 根据Flet文档，on_tap_down事件应该提供TapDownDetails
            print(f"点击事件类型: {type(e)}")
            print(f"事件对象属性: {dir(e)}")
            
            # 尝试获取坐标
            x = getattr(e, 'local_x', None)
            y = getattr(e, 'local_y', None)
            
            # 如果没有local_x/local_y，尝试其他属性
            if x is None or y is None:
                # 检查是否有global_position或local_position
                global_pos = getattr(e, 'global_position', None)
                local_pos = getattr(e, 'local_position', None)
                
                if local_pos:
                    x = getattr(local_pos, 'dx', 0)
                    y = getattr(local_pos, 'dy', 0)
                elif global_pos:
                    x = getattr(global_pos, 'dx', 0)
                    y = getattr(global_pos, 'dy', 0)
                else:
                    x = 0
                    y = 0
            
            print(f"点击坐标: x={x}, y={y}")
            
            if self.client and self.client.alive:
                print(f"发送点击事件到设备: ({x}, {y})")
                # 更新最后记录的鼠标位置
                self.last_mouse_x = x
                self.last_mouse_y = y
                event_data = {
                    'x': x,
                    'y': y,
                    'button': 'left'  # Tap事件是左键点击
                }
                print(f"点击事件: x={event_data['x']}, y={event_data['y']}, client状态: {self.client.alive if self.client else 'None'}")
                
                # 调用按下事件
                self.mousePressEvent(event_data)
                
                # 短暂延迟后调用释放事件
                import threading
                def release_event():
                    if self.client and self.client.alive:  # 再次检查client状态
                        self.mouseReleaseEvent(event_data)
                threading.Timer(0.1, release_event).start()
            else:
                print("客户端未连接")
                
        except Exception as ex:
            print(f"处理点击事件时出错: {ex}")
            print(f"事件对象: {e}")
            print(f"事件对象属性: {dir(e) if hasattr(e, '__dict__') else 'No attributes'}")
    
    def _on_pan_start(self, e):
        """处理拖拽开始事件（鼠标按下）"""
        if not self.client or not self.client.alive:
            print("Client未连接或不可用，无法处理拖拽开始事件")
            return
            
        # 安全获取坐标
        x = getattr(e, 'local_x', 0)
        y = getattr(e, 'local_y', 0)
        
        # 更新最后记录的鼠标位置
        self.last_mouse_x = x
        self.last_mouse_y = y
        
        event_data = {
            'x': x,
            'y': y,
            'button': 'left'
        }
        print(f"拖拽开始: x={event_data['x']}, y={event_data['y']}")
        self.mousePressEvent(event_data)
    
    def _on_pan_update(self, e):
        """处理拖拽更新事件（鼠标移动）"""
        if not self.client or not self.client.alive:
            return
            
        # 安全获取坐标
        x = getattr(e, 'local_x', 0)
        y = getattr(e, 'local_y', 0)
        
        # 更新最后记录的鼠标位置
        self.last_mouse_x = x
        self.last_mouse_y = y
        
        event_data = {
            'x': x,
            'y': y,
            'button': 'left'
        }
        self.mouseMoveEvent(event_data)
    
    def _on_pan_end(self, e):
        """处理拖拽结束事件（鼠标释放）"""
        if not self.client or not self.client.alive:
            return
            
        # DragEndEvent没有local_x和local_y属性，使用最后记录的鼠标位置
        event_data = {
            'x': self.last_mouse_x,
            'y': self.last_mouse_y,
            'button': 'left'
        }
        print(f"拖拽结束: x={event_data['x']}, y={event_data['y']}")
        self.mouseReleaseEvent(event_data)
    
    def _on_hover(self, e):
        """处理悬停事件"""
        # 检查client是否可用
        if not self.client or not self.client.alive:
            return
            
        # 安全获取坐标
        x = getattr(e, 'local_x', 0)
        y = getattr(e, 'local_y', 0)
        
        event_data = {
            'x': x,
            'y': y
        }
        self.on_image_hover(event_data)
    
    # 鼠标事件处理方法
    def mouseMoveEvent(self, event):
        """鼠标移动事件处理"""
        if not self.client or not self.client.alive:
            return
            
        # 获取鼠标坐标
        x = event.get('x', 0)
        y = event.get('y', 0)
        
        print(f"鼠标移动: x={x}, y={y}, 左键按下={self.mouse_left_down}, 右键按下={self.mouse_right_down}")
        
        # 更新鼠标坐标
        self.mouse_x = x
        self.mouse_y = y
        
        # 如果鼠标左键按下，执行触摸移动
        if self.mouse_left_down:
            self.client.control.touch(x, y, const.ACTION_MOVE)
        # 如果鼠标右键按下，执行触摸移动
        elif self.mouse_right_down:
            self.client.control.touch(x, y, const.ACTION_MOVE)
    
    def mousePressEvent(self, event):
        """鼠标按下事件处理"""
        if not self.client or not self.client.alive:
            print(f"mousePressEvent: Client状态检查失败 - client: {self.client}, alive: {self.client.alive if self.client else 'N/A'}")
            return
            
        # 获取鼠标坐标和按键
        x = event.get('x', 0)
        y = event.get('y', 0)
        button = event.get('button', 'left')
        
        print(f"鼠标按下: x={x}, y={y}, 按键={button}, client.control: {hasattr(self.client, 'control')}")
        
        try:
            # 更新鼠标状态和坐标
            if button == 'left':
                self.mouse_left_down = True
                self.ori_x = x
                self.ori_y = y
                self.client.control.touch(x, y, const.ACTION_DOWN)
                print(f"发送触摸按下命令: ({x}, {y})")
            elif button == 'right':
                self.mouse_right_down = True
                self.ori_x = x
                self.ori_y = y
                self.client.control.touch(x, y, const.ACTION_DOWN)
                print(f"发送触摸按下命令: ({x}, {y})")
        except Exception as e:
            print(f"发送触摸命令失败: {e}")
    
    def mouseDoubleClickEvent(self, event):
        """鼠标双击事件处理"""
        # 双击事件可以根据需要实现特殊逻辑
        # 目前保持简单，不做特殊处理
        print(f"鼠标双击事件: x={event.get('x', 0)}, y={event.get('y', 0)}")
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件处理"""
        if not self.client or not self.client.alive:
            return
            
        # 获取鼠标坐标和按键
        x = event.get('x', 0)
        y = event.get('y', 0)
        button = event.get('button', 'left')
        
        print(f"鼠标释放: x={x}, y={y}, 按键={button}")
        
        # 释放鼠标状态并执行触摸释放
        if button == 'left' and self.mouse_left_down:
            self.mouse_left_down = False
            self.client.control.touch(x, y, const.ACTION_UP)
        elif button == 'right' and self.mouse_right_down:
            self.mouse_right_down = False
            self.client.control.touch(x, y, const.ACTION_UP)
    
    def keyPressEvent(self, event):
        """键盘按下事件处理"""
        if not self.client or not self.client.alive:
            return
            
        # 获取按键信息 - 直接使用KeyboardEvent对象的key属性
        key = event.key
        
        print(f"按键按下: {key}")
        
        # 检查是否是重复按键 - KeyboardEvent对象没有get方法
        # 直接跳过重复按键检查
            
        # 处理Ctrl和Alt键状态
        if key == 'Control Left' or key == 'Control Right':
            self.key_ctrl_down = True
        elif key == 'Alt Left' or key == 'Alt Right':
            self.key_alt_down = True
        
        # 处理特定按键
        if key == 'Space':
            self.client.control.keycode(62)  # KEYCODE_SPACE
        elif key == 'C' and self.key_ctrl_down:
            self.client.control.keycode(31)  # KEYCODE_S
        elif key == '?':
            self.client.control.keycode(76)  # KEYCODE_SLASH with shift
        elif key == '/':
            self.client.control.keycode(76)  # KEYCODE_SLASH
        elif key == '\\':
            self.client.control.keycode(73)  # KEYCODE_BACKSLASH
    
    def keyReleaseEvent(self, event):
        """键盘释放事件处理"""
        if not self.client or not self.client.alive:
            return
            
        # 获取按键信息
        key = getattr(event, 'key', '')
        
        print(f"按键释放: {key}")
        
        # 处理Ctrl和Alt键状态释放
        if key == 'Control Left' or key == 'Control Right':
            self.key_ctrl_down = False
        elif key == 'Alt Left' or key == 'Alt Right':
            self.key_alt_down = False
