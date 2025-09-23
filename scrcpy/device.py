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

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from scrcpy.core import Client
from scrcpy import const

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
        
        # 图像显示相关
        
        # Flet UI 组件
        self.image_widget = None
        self.page = None
        
        # 直接连接设备
        try:
            print(f"正在初始化客户端，设备: {ch_name}")
            self.client = Client(device=ch_name, max_width=800, bitrate=4000000, max_fps=20, connection_timeout=10000)
            print("正在添加帧监听器...")
            self.client.add_listener("frame", self.on_frame)
            print("正在启动客户端...")
            self.client.start(threaded=True)
            print(f"成功连接到设备 {ch_name}")
        except Exception as e:
            print(f"连接设备失败: {e}")
            print("请确保:")
            print("1. Android 设备已连接并启用 USB 调试")
            print("2. 运行 'adb devices' 确认设备可见")
            print("3. 运行 'adb push scrcpy-server.jar /data/local/tmp/' 推送服务器文件")
            print("4. 在设备上允许屏幕录制权限")
            # 直接抛出异常，不启动模拟器模式
            raise
    
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
        
        # 创建状态文本
        self.status_text = ft.Text("等待图像...", color="white")
        
        # 创建主容器
        main_container = ft.Container(
            content=ft.Column([
                self.image_widget,
                self.status_text
            ]),
            width=400,
            height=800,
            on_click=self.on_image_click,
            on_hover=self.on_image_hover,
            bgcolor="black",
        )
        
        # 立即更新UI
        page.add(main_container)
        page.update()
        
        # 设置键盘事件监听
        page.on_keyboard_event = self.on_keyboard_event
        
        # 显示帮助信息
        self.show_help()
    


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
                
                # 直接使用原始帧，不进行画布叠加
                display_frame = frame
                
                # 将OpenCV图像转换为Flet可显示的base64格式并直接更新UI
                self.update_ui_with_frame(display_frame, image_width, image_height)
                        
            except Exception as e:
                print("线程出错%s"%(e))
            finally:
                self.rlock.release()
        else:
            pass
            # print("收到空帧或无效帧")
            
    def update_ui_with_frame(self, display_frame, image_width, image_height):
        """直接更新UI，不使用队列和定时器"""
        if self.image_widget and self.page:
            try:
                # 确保数据类型为uint8，避免不必要的类型转换
                if display_frame.dtype != np.uint8:
                    display_frame = display_frame.astype(np.uint8)
                
                # scrcpy的帧数据通常已经是RGB格式，不需要转换
                # 如果颜色不对，可能需要BGR到RGB的转换
                # rgb_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
                rgb_frame = display_frame
                
                # 转换为base64编码，避免文件缓存问题
                _, buffer = cv2.imencode('.jpg', rgb_frame)
                img_str = base64.b64encode(buffer).decode('utf-8')
                
                # 使用base64编码直接更新图像
                self.image_widget.src_base64 = img_str
                self.image_widget.width = image_width
                self.image_widget.height = image_height
                
                # 更新状态文本
                if hasattr(self, 'status_text') and self.status_text:
                    if not hasattr(self, 'update_count'):
                        self.update_count = 0
                    self.update_count += 1
                    self.status_text.value = f"已更新 {self.update_count} 帧 - {image_width}x{image_height}"
                
                try:
                    # 显式调用page.update()来确保UI更新
                    self.page.update()
                    print(f"UI已直接更新: {image_width}x{image_height}")
                except Exception as e:
                    # 忽略UI更新错误，可能是UI已关闭
                    pass
            except Exception as e:
                print(f"线程出错{e}")





    def show_help(self):
        """显示快捷键帮助信息"""
        print("\n" + "="*50)
        print("🎮 Android分析器 - 快捷键帮助")
        print("="*50)
        print("💡 提示:")
        print("  • 基础scrcpy屏幕镜像功能")
        print("  • 支持鼠标点击和键盘控制")
        print("="*50)


    def on_image_click(self, e: ft.ControlEvent):
        """处理图像点击事件"""
        if self.client is None:
            return
        
        # 安全获取坐标
        x = getattr(e, 'local_x', 0)
        y = getattr(e, 'local_y', 0)
        
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
        
        # 使用正确的属性名
        x = getattr(e, 'local_x', 0)
        y = getattr(e, 'local_y', 0)
        
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
    
    try:
        # 启动Flet应用，指定端口
        ft.app(target=app.main, port=8550)
    except Exception as e:
        print(f"主程序异常: {e}")
        import traceback
        traceback.print_exc()