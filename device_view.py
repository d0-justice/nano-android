import flet as ft
from typing import Optional, Callable
import threading
import sys
import os
import time
import numpy as np
import cv2
import base64
import math

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
        
        # 使用GestureDetector来处理手势事件，使用Container包装来处理鼠标事件
        self.gesture_detector = ft.GestureDetector(
            content=self.device_image,
            on_scroll=self._on_scroll,  # 滚轮事件监听
            on_tap_down=self.on_tap_down,  # 鼠标按下事件
            on_tap_up=self.on_tap_up,  # 鼠标释放事件
            on_tap=self.on_tap,  # 点击事件
            on_double_tap=self.on_double_tap,  # 双击事件
            on_secondary_tap=self.on_secondary_tap,  # 右键点击事件
            on_secondary_tap_down=self.on_secondary_tap_down,  # 右键按下事件
            on_secondary_tap_up=self.on_secondary_tap_up,  # 右键释放事件
            on_pan_start=self.on_pan_start,  # 拖拽开始事件
            on_pan_update=self.on_pan_update,  # 拖拽更新事件
            on_pan_end=self.on_pan_end,  # 拖拽结束事件
            on_enter=self.on_mouse_enter,  # 鼠标进入事件
            on_exit=self.on_mouse_exit,  # 鼠标离开事件
            on_hover=self.on_mouse_hover,  # 鼠标悬停事件
        )
        
        # 创建简化的设备屏幕显示界面 - 移除按钮
        device_content = ft.Column([
            # 设备屏幕图像 - 占满整个容器，使用mouse_container包装
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
        """创建占位符图像 - 使用OpenCV替代PIL"""
        # 创建一个简单的占位符图像 (280x350, 灰色背景)
        img = np.full((350, 280, 3), 192, dtype=np.uint8)  # 浅灰色背景
        
        # 添加边框
        cv2.rectangle(img, (5, 5), (275, 345), (128, 128, 128), 2)  # 深灰色边框
        
        # 添加文本 (OpenCV的文本功能比较基础，但性能更好)
        cv2.putText(img, "Android Device", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
        cv2.putText(img, "Waiting for connection...", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (128, 128, 128), 1)
        
        # 转换为base64
        _, buffer = cv2.imencode('.png', img)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return img_base64
    
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
        """处理从scrcpy接收到的帧数据 - 优化版本"""
        if frame is not None and frame.size > 0:
            try:
                self.rlock.acquire()
                # 存储当前帧
                self.current_frame = frame
                
                if not hasattr(self, 'frame_count'):
                    self.frame_count = 0
                    self.last_frame_info_time = time.time()
                
                self.frame_count += 1
                
                # 优化：减少不必要的shape访问
                # 减少日志输出频率
                current_time = time.time()
                if current_time - self.last_frame_info_time > 2.0:  # 增加到2秒减少日志频率
                    image_height, image_width = frame.shape[:2]
                    print(f"收到帧: {image_width}x{image_height}, FPS: {self.frame_count/2:.1f}")
                    self.frame_count = 0
                    self.last_frame_info_time = current_time
                
                # 将OpenCV图像转换为base64格式并更新UI
                self._update_ui_with_frame(frame, 0, 0)  # 不需要传递宽高参数
                        
            except Exception as e:
                print(f"帧处理错误: {e}")
            finally:
                self.rlock.release()
    
    def _update_ui_with_frame(self, display_frame, image_width, image_height):
        """更新UI显示帧数据 - 优化版本"""
        # 检查UI是否仍然活跃
        if not self.is_ui_active:
            return
            
        if self.device_image_ref.current:
            try:
                # 确保数据类型为uint8
                if display_frame.dtype != np.uint8:
                    display_frame = display_frame.astype(np.uint8)
                
                # 优化：使用更高效的JPEG编码参数
                encode_params = [cv2.IMWRITE_JPEG_QUALITY, 85]  # 降低质量以提升性能
                _, buffer = cv2.imencode('.jpg', display_frame, encode_params)
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
        """显示错误占位符图像 - 使用OpenCV替代PIL"""
        # 创建错误占位符图像 (280x350, 浅红色背景)
        img = np.full((350, 280, 3), (240, 128, 128), dtype=np.uint8)  # 浅红色背景 (BGR格式)
        
        # 添加错误信息文本
        cv2.putText(img, "Connection Error", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 139), 1)  # 深红色
        cv2.putText(img, "Failed to update image", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)  # 红色
        
        # 转换为base64
        _, buffer = cv2.imencode('.png', img)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        
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
        
        # 清理滚轮定时器
        if hasattr(self, 'scroll_timer') and self.scroll_timer:
            self.scroll_timer.cancel()
            self.scroll_timer = None
    
    def _on_scroll(self, e):
        """处理滚轮事件，直接使用delta值进行滚动"""
        if not self.client or not self.client.control:
            return
        
        delta_x = getattr(e, 'scroll_delta_x', 0)
        delta_y = getattr(e, 'scroll_delta_y', 0)
        
        # 获取设备分辨率
        try:
            device_width = self.client.resolution[0] if hasattr(self.client, 'resolution') and self.client.resolution else 800
            device_height = self.client.resolution[1] if hasattr(self.client, 'resolution') and self.client.resolution else 600
        except:
            device_width, device_height = 800, 600
        
        # 固定使用屏幕中心点作为滚动坐标
        device_x = device_width // 2
        device_y = device_height // 2
        
        try:
            # 直接使用delta值进行滚动
            # scrcpy的滚动方向与常规相反，所以需要取负值
            scroll_x = int(-delta_x)
            scroll_y = int(-delta_y)
            self.client.control.scroll(device_x, device_y, scroll_x/2, scroll_y/2)
            time.sleep(0.1)
            self.client.control.scroll(device_x, device_y, scroll_x/2, scroll_y/2)
                
        except Exception as ex:
            print(f"❌ 滚动操作失败: {ex}")
   

    # 新的GestureDetector事件处理方法
    def on_tap_down(self, e):
        """鼠标按下事件 - 使用GestureDetector的on_tap_down"""
        if not self.client or not self.client.alive:
            return
        
        x = int(getattr(e, 'local_x', 0))
        y = int(getattr(e, 'local_y', 0))
        
        print(f"GestureDetector - 鼠标按下: x={x}, y={y}")
        
        try:
            self.mouse_left_down = True
            self.ori_x = x
            self.ori_y = y
            self.client.control.touch(x, y, const.ACTION_DOWN)
        except Exception as ex:
            print(f"触摸按下事件发送失败: {ex}")
    
    def on_tap_up(self, e):
        """鼠标释放事件 - 使用GestureDetector的on_tap_up"""
        if not self.client or not self.client.alive:
            return
        
        x = int(getattr(e, 'local_x', 0))
        y = int(getattr(e, 'local_y', 0))
        
        print(f"GestureDetector - 鼠标释放: x={x}, y={y}")
        
        try:
            self.mouse_left_down = False
            self.client.control.touch(x, y, const.ACTION_UP)
        except Exception as ex:
            print(f"触摸释放事件发送失败: {ex}")
    
    def on_tap(self, e):
        """点击事件 - 使用GestureDetector的on_tap"""
        x = int(getattr(e, 'local_x', 0))
        y = int(getattr(e, 'local_y', 0))
        print(f"GestureDetector - 点击: x={x}, y={y}")
    
    def on_double_tap(self, e):
        """双击事件 - 使用GestureDetector的on_double_tap"""
        x = int(getattr(e, 'local_x', 0))
        y = int(getattr(e, 'local_y', 0))
        print(f"GestureDetector - 双击: x={x}, y={y}")
    
    def on_secondary_tap(self, e):
        """右键点击事件 - 使用GestureDetector的on_secondary_tap"""
        x = int(getattr(e, 'local_x', 0))
        y = int(getattr(e, 'local_y', 0))
        print(f"GestureDetector - 右键点击: x={x}, y={y}")
    
    def on_secondary_tap_down(self, e):
        """右键按下事件 - 使用GestureDetector的on_secondary_tap_down"""
        if not self.client or not self.client.alive:
            return
        
        x = int(getattr(e, 'local_x', 0))
        y = int(getattr(e, 'local_y', 0))
        
        print(f"GestureDetector - 右键按下: x={x}, y={y}")
        
        try:
            self.mouse_right_down = True
            self.ori_x = x
            self.ori_y = y
            # 右键可以用于特殊操作，这里暂时使用相同的触摸操作
            self.client.control.touch(x, y, const.ACTION_DOWN)
        except Exception as ex:
            print(f"右键按下事件发送失败: {ex}")
    
    def on_secondary_tap_up(self, e):
        """右键释放事件 - 使用GestureDetector的on_secondary_tap_up"""
        if not self.client or not self.client.alive:
            return
        
        x = int(getattr(e, 'local_x', 0))
        y = int(getattr(e, 'local_y', 0))
        
        print(f"GestureDetector - 右键释放: x={x}, y={y}")
        
        try:
            self.mouse_right_down = False
            self.client.control.touch(x, y, const.ACTION_UP)
        except Exception as ex:
            print(f"右键释放事件发送失败: {ex}")
    
    def on_pan_start(self, e):
        """拖拽开始事件 - 使用GestureDetector的on_pan_start"""
        if not self.client or not self.client.alive:
            return
            
        x = int(getattr(e, 'local_x', 0))
        y = int(getattr(e, 'local_y', 0))
        
        print(f"GestureDetector - 拖拽开始: x={x}, y={y}")
        
        try:
            # 拖拽开始时发送触摸按下事件
            self.mouse_left_down = True
            self.ori_x = x
            self.ori_y = y
            self.client.control.touch(x, y, const.ACTION_DOWN)
        except Exception as ex:
            print(f"拖拽开始事件发送失败: {ex}")
    
    def on_pan_update(self, e):
        """拖拽更新事件 - 使用GestureDetector的on_pan_update"""
        if not self.client or not self.client.alive:
            return
        
        x = int(getattr(e, 'local_x', 0))
        y = int(getattr(e, 'local_y', 0))
        
        print(f"GestureDetector - 拖拽更新: x={x}, y={y}")
        
        try:
            # 拖拽时发送移动事件
            self.client.control.touch(x, y, const.ACTION_MOVE)
        except Exception as ex:
            print(f"拖拽更新事件发送失败: {ex}")
    
    def on_pan_end(self, e):
        """拖拽结束事件 - 使用GestureDetector的on_pan_end"""
        if not self.client or not self.client.alive:
            return
            
        x = int(getattr(e, 'local_x', 0))
        y = int(getattr(e, 'local_y', 0))
        
        print(f"GestureDetector - 拖拽结束: x={x}, y={y}")
        
        try:
            # 拖拽结束时发送触摸释放事件
            self.mouse_left_down = False
            self.client.control.touch(x, y, const.ACTION_UP)
        except Exception as ex:
            print(f"拖拽结束事件发送失败: {ex}")
    
    def on_mouse_enter(self, e):
        """鼠标进入事件 - 使用GestureDetector的on_enter"""
        print("GestureDetector - 鼠标进入设备屏幕区域")
    
    def on_mouse_exit(self, e):
        """鼠标离开事件 - 使用GestureDetector的on_exit"""
        print("GestureDetector - 鼠标离开设备屏幕区域")
    
    def on_mouse_hover(self, e):
        """鼠标悬停事件 - 使用GestureDetector的on_hover"""
        x = int(getattr(e, 'local_x', 0))
        y = int(getattr(e, 'local_y', 0))
        # 不打印悬停事件，避免日志过多
        # print(f"GestureDetector - 鼠标悬停: x={x}, y={y}")
