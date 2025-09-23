# -*- coding: utf-8 -*-

# Android设备屏幕镜像应用 - 使用Flet框架
# 支持实时显示Android设备屏幕，鼠标键盘控制，以及公共画布功能

import flet as ft
import threading
import sys
import os
import time
import numpy as np
import cv2
import base64
import queue

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from scrcpy.core import Client
import scrcpy.const as const

class AndroidMirrorApp:

    def __init__(self, ch_name):
        self.device_name = ch_name
        self.rlock = threading.RLock()
        
        # 鼠标和键盘状态
        self.mouse_left_down = False
        self.mouse_right_down = False
        self.mouse_x1_down = False
        self.key_alt_down = False
        self.key_ctrl_down = False
        self.win_moving = False
        self.ori_x = 0
        self.ori_y = 0
        
        # 鼠标交互相关
        self.mouse_x = 0
        self.mouse_y = 0
        self.current_frame = None  # 存储当前帧以便坐标转换
        
        # 公共画布支持 - 供其他模块绘制UI元素边框
        self.public_canvas = None  # 公共画布，其他模块可以在此绘制
        self.canvas_lock = threading.RLock()  # 画布线程锁
        
        # Flet UI 组件
        self.image_widget = None
        self.page = None
        
        # 检查是否为模拟设备模式
        if ch_name == "simulator":
            print("启动模拟设备模式...")
            self.client = None
            self.simulator_mode = True
            self.start_simulator()
        else:
            try:
                print(f"正在初始化客户端，设备: {ch_name}")
                self.client = Client(device=ch_name, max_width=800, bitrate=4000000, max_fps=20, connection_timeout=10000)
                print("正在添加帧监听器...")
                self.client.add_listener("frame", self.on_frame)
                print("正在启动客户端...")
                self.client.start(threaded=True)
                print(f"成功连接到设备 {ch_name}")
                self.simulator_mode = False
            except Exception as e:
                print(f"连接设备失败: {e}")
                print("请确保:")
                print("1. Android 设备已连接并启用 USB 调试")
                print("2. 运行 'adb devices' 确认设备可见")
                print("3. 运行 'adb push scrcpy-server.jar /data/local/tmp/' 推送服务器文件")
                print("4. 在设备上允许屏幕录制权限")
                print("启动模拟设备模式...")
                self.client = None
                self.simulator_mode = True
                self.start_simulator()
    
    def main(self, page: ft.Page):
        """Flet 主函数"""
        self.page = page
        page.title = f"Android镜像 - {self.device_name}"
        page.window_width = 400
        page.window_height = 800
        page.window_resizable = True
        
        # 创建图像显示组件
        self.image_widget = ft.Image(
            src="",
            width=400,
            height=800,
            fit=ft.ImageFit.CONTAIN,
        )
        
        # 创建主容器
        main_container = ft.Container(
            content=self.image_widget,
            width=400,
            height=800,
            on_click=self.on_image_click,
            on_hover=self.on_image_hover,
        )
        
        page.add(main_container)
        
        # 设置键盘事件监听
        page.on_keyboard_event = self.on_keyboard_event
        
        # 初始化图像数据队列
        self.image_queue = queue.Queue()
        
        # 启动UI更新定时器
        def ui_update_timer():
            while True:
                try:
                    if not self.image_queue.empty():
                        image_data = self.image_queue.get_nowait()
                        if self.image_widget and self.page:
                            # 直接更新UI组件，让Flet处理线程安全
                            try:
                                self.image_widget.src = image_data['src']
                                self.image_widget.width = image_data['width']
                                self.image_widget.height = image_data['height']
                                # 不调用page.update()，让Flet自动处理
                            except Exception as e:
                                print(f"UI更新错误: {e}")
                except queue.Empty:
                    pass
                except Exception as e:
                    print(f"UI更新定时器错误: {e}")
                time.sleep(0.05)  # 50ms间隔
        
        ui_timer_thread = threading.Thread(target=ui_update_timer, daemon=True)
        ui_timer_thread.start()
        
        # 显示帮助信息
        self.show_help()
    
    def start_simulator(self):
        """启动模拟设备模式"""
        def simulator_loop():
            while self.simulator_mode:
                # 创建模拟帧
                frame = np.zeros((800, 400, 3), dtype=np.uint8)
                frame[:] = (50, 50, 50)  # 深灰色背景
                
                # 添加一些模拟内容
                cv2.putText(frame, "Simulator Mode", (50, 100), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                cv2.putText(frame, "No Android Device", (50, 150), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)
                cv2.putText(frame, "Connected", (50, 200), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)
                
                self.on_frame(frame)
                time.sleep(0.1)  # 10 FPS
        
        simulator_thread = threading.Thread(target=simulator_loop, daemon=True)
        simulator_thread.start()

    def on_frame(self, frame):
        if frame is not None and frame.size > 0:
            try:
                self.rlock.acquire()
                # 存储当前帧以便坐标转换和UI分析
                self.current_frame = frame
                                
                if not hasattr(self, 'frame_count'):
                    self.frame_count = 0
                    self.last_frame_info_time = 0
                
                self.frame_count += 1
                image_height, image_width, image_depth = frame.shape
                
                # 减少日志输出频率，每30帧（约1秒）打印一次
                current_time = time.time()
                if current_time - self.last_frame_info_time > 1.0:
                    print(f"收到帧: {image_width}x{image_height}, FPS: {self.frame_count}/{current_time - self.last_frame_info_time:.1f}")
                    self.frame_count = 0
                    self.last_frame_info_time = current_time
                                
                # 动态调整窗口大小以匹配图像大小
                if not hasattr(self, 'window_resized') or not self.window_resized:
                    if self.page:
                        try:
                            self.page.window_width = image_width
                            self.page.window_height = image_height
                            # 不调用page.update()，让Flet自动处理
                        except Exception as e:
                            print(f"窗口调整错误: {e}")
                    self.window_resized = True
                    print(f"窗口大小已调整为: {image_width}x{image_height}")
                
                # 处理公共画布渲染 - 将UI元素边框叠加到frame上
                display_frame = frame.copy()
                with self.canvas_lock:
                    if self.public_canvas is not None:
                        try:
                            # 确保画布尺寸与frame匹配
                            if self.public_canvas.shape[:2] == (image_height, image_width):
                                # 将画布内容叠加到frame上
                                # 使用加权混合，让原图可见，画布内容作为覆盖层
                                alpha = 0.6  # 原图透明度
                                beta = 0.4   # 画布透明度 - 提高边框可见性
                                display_frame = cv2.addWeighted(display_frame, alpha, self.public_canvas, beta, 0)
                            else:
                                # 如果尺寸不匹配，重置画布
                                print(f"画布尺寸不匹配，重置: 期望{(image_height, image_width)}, 实际{self.public_canvas.shape[:2]}")
                                self.public_canvas = None
                        except Exception as e:
                            print(f"画布渲染错误: {e}")
                            self.public_canvas = None
                
                # 将OpenCV图像转换为Flet可显示的base64格式
                if self.image_widget and self.page:
                    try:
                        # 确保数据类型为uint8，避免不必要的类型转换
                        if display_frame.dtype != np.uint8:
                            display_frame = display_frame.astype(np.uint8)
                        
                        # 直接使用OpenCV的imencode编码BGR数据，避免任何通道转换
                        # 这是最高效的方法：直接编码原始BGR数据
                        success, encoded_img = cv2.imencode('.png', display_frame)
                        if success:
                            # 直接使用NumPy的tobytes()方法，避免额外的内存拷贝
                            # 这比PIL + BytesIO的组合更高效
                            img_str = base64.b64encode(encoded_img.tobytes()).decode()
                            
                            # 将图像数据放入队列，由UI更新定时器处理
                            try:
                                image_data = {
                                    'src': f"data:image/png;base64,{img_str}",
                                    'width': image_width,
                                    'height': image_height
                                }
                                # 清空队列中的旧数据，只保留最新的
                                while not self.image_queue.empty():
                                    try:
                                        self.image_queue.get_nowait()
                                    except queue.Empty:
                                        break
                                self.image_queue.put(image_data)
                            except Exception as e:
                                print(f"队列操作错误: {e}")
                        else:
                            print("图像编码失败")
                        
                    except Exception as e:
                        print(f"图像转换错误: {e}")
                        
            except Exception as e:
                print("线程出错%s"%(e))
            finally:
                self.rlock.release()
        else:
            pass
            # print("收到空帧或无效帧")

    def set_public_canvas(self, canvas):
        """设置公共画布，供其他模块绘制UI元素边框
        
        Args:
            canvas: OpenCV格式的画布(numpy array)，或None清空画布
        """
        with self.canvas_lock:
            self.public_canvas = canvas
    
    def get_frame_size(self):
        """获取当前帧的尺寸，供其他模块创建匹配的画布
        
        Returns:
            tuple: (height, width) 或 None如果未接收到帧
        """
        if hasattr(self, 'current_frame') and self.current_frame is not None:
            return self.current_frame.shape[:2]
        return None
    
    def create_empty_canvas(self):
        """创建与当前帧尺寸匹配的空画布
        
        Returns:
            numpy.ndarray: 空的BGR画布，或None如果无法创建
        """
        frame_size = self.get_frame_size()
        if frame_size is not None:
            height, width = frame_size
            return np.zeros((height, width, 3), dtype=np.uint8)
        return None




    def show_help(self):
        """显示快捷键帮助信息"""
        print("\n" + "="*50)
        print("🎮 Android分析器 - 快捷键帮助")
        print("="*50)
        print("💡 提示:")
        print("  • 基础scrcpy屏幕镜像功能")
        print("  • 支持公共画布用于外部UI绘制")
        print("="*50)


    def on_image_click(self, e: ft.ControlEvent):
        """处理图像点击事件"""
        if self.client is None:
            return
        
        x = e.local_x
        y = e.local_y
        
        # 更新鼠标位置
        self.mouse_x = x
        self.mouse_y = y
        
        # 在Flet中，我们需要通过其他方式检测鼠标按钮
        # 这里简化为左键点击
        self.mouse_left_down = True
        self.client.control.touch(x, y, const.ACTION_DOWN, 2)

    def on_image_hover(self, e: ft.ControlEvent):
        """处理鼠标悬停事件"""
        if self.client is None:
            return
        
        x = e.local_x
        y = e.local_y
        
        # 更新鼠标位置
        self.mouse_x = x
        self.mouse_y = y
        
        if self.mouse_left_down:
            self.client.control.touch(x, y, const.ACTION_MOVE, 2)

    def on_keyboard_event(self, e: ft.KeyboardEvent):
        """处理键盘事件"""
        print(f"🔑 按键事件: {e.key}, 字符: {e.character}")  # 添加调试信息
        
        if e.event_type == ft.KeyboardEventType.KEY_DOWN:
            if e.key == "Alt":
                self.key_alt_down = True
            elif e.key == "Control":
                self.key_ctrl_down = True
            elif e.key == " ":
                if self.win_moving:
                    self.win_moving = False
            elif e.key == "C":
                pass
            elif e.key == "?" or e.key == "/":
                self.show_help()
            elif e.key == "\\":
                print('生成技能图形指纹完成')
                
        elif e.event_type == ft.KeyboardEventType.KEY_UP:
            if e.key == "Alt":
                self.key_alt_down = False
            elif e.key == "Control":
                self.key_ctrl_down = False





    def cleanup(self):
        """清理资源"""
        if self.client:
            try:
                self.client.stop()
            except:
                pass


def get_device_id():
    """获取可用的设备ID"""
    try:
        import subprocess
        result = subprocess.run(['adb', 'devices'], capture_output=True, text=True, timeout=5)
        lines = result.stdout.strip().split('\n')[1:]  # 跳过第一行标题
        devices = []
        for line in lines:
            if line.strip() and 'device' in line:
                device_id = line.split()[0]
                devices.append(device_id)
        
        if not devices:
            print("❌ 没有找到连接的Android设备")
            print("请确保：")
            print("1. 设备已连接并开启USB调试")
            print("2. ADB驱动已正确安装") 
            print("3. 在设备上允许USB调试授权")
            return "simulator"
        
        # 使用第一个可用设备
        device_id = devices[0]
        print(f"✅ 发现设备: {device_id}")
        return device_id
        
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"❌ ADB命令执行失败: {e}")
        print("请确保ADB已安装并在PATH环境变量中")
        print("⚠️  启动模拟设备模式...")
        return "simulator"


if __name__ == '__main__':
    # 获取设备ID
    device_id = get_device_id()
    
    # 创建应用实例
    app = AndroidMirrorApp(device_id)
    
    # 启动Flet应用
    ft.app(target=app.main)