#!/usr/bin/env python3
"""
信号系统测试脚本

测试基于blinker的信号管理器功能，验证组件间通信是否正常工作
"""

import time
import threading
from utils.signal_manager import SignalManager, SignalType, send_signal, connect_signal, disconnect_signal


class MockDeviceView:
    """模拟设备视图类"""
    
    def __init__(self, device_name):
        self.device_name = device_name
        self.client = None
        self.is_connected = False
        
        # 连接信号
        connect_signal(SignalType.KEYBOARD_SHORTCUT, self.on_keyboard_signal)
        print(f"✅ MockDeviceView {device_name} 已连接键盘信号")
    
    def on_keyboard_signal(self, sender, signal_data):
        """处理键盘信号"""
        if signal_data and signal_data.data:
            key_event = signal_data.data
            print(f"📱 {self.device_name} 收到键盘事件: {key_event.get('type')} - {key_event.get('key', 'unknown')}")
    
    def connect_device(self):
        """模拟设备连接"""
        self.is_connected = True
        self.client = "mock_client"
        
        # 发送设备连接信号
        send_signal(SignalType.DEVICE_CONNECTED, self, {
            'device_name': self.device_name,
            'client': self.client
        })
        print(f"📱 {self.device_name} 设备连接信号已发送")
    
    def disconnect_device(self):
        """模拟设备断开"""
        self.is_connected = False
        device_name = self.device_name
        self.client = None
        
        # 发送设备断开信号
        send_signal(SignalType.DEVICE_DISCONNECTED, self, {
            'device_name': device_name
        })
        print(f"📱 {device_name} 设备断开信号已发送")


class MockHierarchy:
    """模拟层次结构类"""
    
    def __init__(self, device_id):
        self.device_id = device_id
        self.elements = []
        
        # 连接信号
        connect_signal(SignalType.HIERARCHY_CAPTURE_REQUESTED, self.on_hierarchy_capture_requested)
        print(f"✅ MockHierarchy {device_id} 已连接层次结构捕获信号")
    
    def on_hierarchy_capture_requested(self, sender, signal_data):
        """处理层次结构捕获请求"""
        print(f"🌳 {self.device_id} 收到层次结构捕获请求")
        self.refresh_hierarchy()
    
    def refresh_hierarchy(self):
        """模拟刷新层次结构"""
        # 模拟获取元素数据
        self.elements = [
            {'id': 'btn1', 'type': 'Button', 'text': 'Click Me'},
            {'id': 'txt1', 'type': 'TextView', 'text': 'Hello World'},
            {'id': 'img1', 'type': 'ImageView', 'text': ''}
        ]
        
        # 发送层次结构更新信号
        send_signal(SignalType.HIERARCHY_UPDATED, self, {
            'device_id': self.device_id,
            'elements': self.elements,
            'element_count': len(self.elements)
        })
        print(f"🌳 {self.device_id} 层次结构更新信号已发送，元素数量: {len(self.elements)}")
    
    def select_element(self, element_id):
        """模拟选择元素"""
        element = next((e for e in self.elements if e['id'] == element_id), None)
        if element:
            send_signal(SignalType.HIERARCHY_ELEMENT_SELECTED, self, {
                'device_id': self.device_id,
                'element': element
            })
            print(f"🌳 {self.device_id} 元素选择信号已发送: {element_id}")


class MockMainWindow:
    """模拟主窗口类"""
    
    def __init__(self):
        self.device_view = None
        self.hierarchy = None
        
        # 连接信号
        connect_signal(SignalType.DEVICE_CONNECTED, self.on_device_connected)
        connect_signal(SignalType.DEVICE_DISCONNECTED, self.on_device_disconnected)
        connect_signal(SignalType.HIERARCHY_UPDATED, self.on_hierarchy_updated)
        connect_signal(SignalType.HIERARCHY_ELEMENT_SELECTED, self.on_element_selected)
        connect_signal(SignalType.APP_ERROR, self.on_app_error)
        print("✅ MockMainWindow 已连接所有信号")
    
    def on_device_connected(self, sender, signal_data):
        """处理设备连接信号"""
        if signal_data and signal_data.data:
            device_name = signal_data.data.get('device_name')
            print(f"🏠 主窗口收到设备连接信号: {device_name}")
    
    def on_device_disconnected(self, sender, signal_data):
        """处理设备断开信号"""
        if signal_data and signal_data.data:
            device_name = signal_data.data.get('device_name')
            print(f"🏠 主窗口收到设备断开信号: {device_name}")
    
    def on_hierarchy_updated(self, sender, signal_data):
        """处理层次结构更新信号"""
        if signal_data and signal_data.data:
            device_id = signal_data.data.get('device_id')
            element_count = signal_data.data.get('element_count')
            print(f"🏠 主窗口收到层次结构更新信号: {device_id}, 元素数量: {element_count}")
    
    def on_element_selected(self, sender, signal_data):
        """处理元素选择信号"""
        if signal_data and signal_data.data:
            device_id = signal_data.data.get('device_id')
            element = signal_data.data.get('element')
            print(f"🏠 主窗口收到元素选择信号: {device_id}, 元素: {element.get('id')}")
    
    def on_app_error(self, sender, signal_data):
        """处理应用错误信号"""
        if signal_data and signal_data.data:
            error_type = signal_data.data.get('error_type')
            error = signal_data.data.get('error')
            print(f"🏠 主窗口收到错误信号: {error_type} - {error}")
    
    def send_keyboard_event(self, key):
        """模拟发送键盘事件"""
        send_signal(SignalType.KEYBOARD_SHORTCUT, self, {
            'type': 'key_press',
            'key': key
        })
        print(f"🏠 主窗口发送键盘事件: {key}")
    
    def request_hierarchy_capture(self):
        """模拟请求层次结构捕获"""
        send_signal(SignalType.HIERARCHY_CAPTURE_REQUESTED, self, {
            'timestamp': time.time()
        })
        print("🏠 主窗口发送层次结构捕获请求")


def test_signal_system():
    """测试信号系统"""
    print("🚀 开始测试信号系统...")
    print("=" * 60)
    
    # 创建信号管理器实例
    signal_manager = SignalManager()
    print(f"📊 信号管理器状态: {signal_manager.list_signals()}")
    print()
    
    # 创建模拟组件
    print("📱 创建模拟组件...")
    main_window = MockMainWindow()
    device_view1 = MockDeviceView("device1")
    device_view2 = MockDeviceView("device2")
    hierarchy1 = MockHierarchy("device1")
    hierarchy2 = MockHierarchy("device2")
    print()
    
    # 测试设备连接/断开
    print("🔌 测试设备连接/断开...")
    device_view1.connect_device()
    time.sleep(0.1)
    device_view2.connect_device()
    time.sleep(0.1)
    device_view1.disconnect_device()
    time.sleep(0.1)
    print()
    
    # 测试键盘事件
    print("⌨️ 测试键盘事件...")
    main_window.send_keyboard_event("F1")
    time.sleep(0.1)
    main_window.send_keyboard_event("Enter")
    time.sleep(0.1)
    print()
    
    # 测试层次结构捕获
    print("🌳 测试层次结构捕获...")
    main_window.request_hierarchy_capture()
    time.sleep(0.1)
    print()
    
    # 测试元素选择
    print("🎯 测试元素选择...")
    hierarchy1.select_element("btn1")
    time.sleep(0.1)
    hierarchy2.select_element("txt1")
    time.sleep(0.1)
    print()
    
    # 测试错误信号
    print("❌ 测试错误信号...")
    send_signal(SignalType.APP_ERROR, None, {
        'error_type': 'test_error',
        'error': 'This is a test error'
    })
    time.sleep(0.1)
    print()
    
    # 显示最终状态
    print("📊 最终信号管理器状态:")
    for signal_name, receiver_count in signal_manager.list_signals().items():
        print(f"  {signal_name}: {receiver_count} 个接收器")
    print()
    
    print("✅ 信号系统测试完成!")
    print("=" * 60)


def test_async_signals():
    """测试异步信号"""
    print("🔄 测试异步信号...")
    
    def async_receiver(sender, signal_data):
        print(f"🔄 异步接收器收到信号: {signal_data.signal_type.value}")
        time.sleep(0.5)  # 模拟耗时操作
        print(f"🔄 异步接收器处理完成: {signal_data.signal_type.value}")
    
    # 连接异步接收器
    connect_signal(SignalType.DEVICE_FRAME_UPDATED, async_receiver)
    
    # 发送异步信号
    from utils.signal_manager import send_signal_async
    send_signal_async(SignalType.DEVICE_FRAME_UPDATED, None, {'frame_id': 123})
    print("🔄 异步信号已发送，继续执行其他任务...")
    
    # 等待异步处理完成
    time.sleep(1)
    print("🔄 异步信号测试完成")


if __name__ == "__main__":
    # 运行基本测试
    test_signal_system()
    
    # 运行异步测试
    test_async_signals()
    
    print("\n🎉 所有测试完成！信号系统工作正常。")