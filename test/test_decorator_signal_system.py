#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试装饰器信号系统
验证新的装饰器信号系统是否正常工作
"""

import asyncio
import time
from utils.signal_manager import SignalManager, SignalType, send_signal, signal_receiver, SignalMixin


class MockMainWindow(SignalMixin):
    """模拟MainWindow类"""
    
    def __init__(self):
        super().__init__()
        self.device_connected_count = 0
        self.device_disconnected_count = 0
        self.hierarchy_updated_count = 0
        self.app_error_count = 0
        print("✅ MockMainWindow 初始化完成")
    
    @signal_receiver(SignalType.DEVICE_CONNECTED)
    def _on_device_connected(self, sender, signal_data):
        """处理设备连接信号"""
        self.device_connected_count += 1
        device_id = signal_data.data.get('device_id', 'unknown')
        print(f"📱 MockMainWindow 收到设备连接信号: {device_id}")
    
    @signal_receiver(SignalType.DEVICE_DISCONNECTED)
    def _on_device_disconnected(self, sender, signal_data):
        """处理设备断开信号"""
        self.device_disconnected_count += 1
        device_id = signal_data.data.get('device_id', 'unknown')
        print(f"📱 MockMainWindow 收到设备断开信号: {device_id}")
    
    @signal_receiver(SignalType.HIERARCHY_UPDATED)
    def _on_hierarchy_updated(self, sender, signal_data):
        """处理层次结构更新信号"""
        self.hierarchy_updated_count += 1
        device_id = signal_data.data.get('device_id', 'unknown')
        print(f"🌳 MockMainWindow 收到层次结构更新信号: {device_id}")
    
    @signal_receiver(SignalType.APP_ERROR)
    def _on_app_error(self, sender, signal_data):
        """处理应用错误信号"""
        self.app_error_count += 1
        error = signal_data.data.get('error', 'unknown error')
        print(f"❌ MockMainWindow 收到应用错误信号: {error}")


class MockDeviceView(SignalMixin):
    """模拟DeviceView类"""
    
    def __init__(self, device_name: str):
        super().__init__()
        self.device_name = device_name
        self.keyboard_signal_count = 0
        print(f"✅ MockDeviceView {device_name} 初始化完成")
    
    @signal_receiver(SignalType.KEYBOARD_SHORTCUT)
    def _on_keyboard_signal(self, sender, signal_data):
        """处理键盘快捷键信号"""
        self.keyboard_signal_count += 1
        key = signal_data.data.get('key', 'unknown')
        print(f"⌨️ MockDeviceView {self.device_name} 收到键盘信号: {key}")


class MockHierarchy(SignalMixin):
    """模拟Hierarchy类"""
    
    def __init__(self, device_id: str):
        super().__init__()
        self.device_id = device_id
        self.capture_requested_count = 0
        print(f"✅ MockHierarchy {device_id} 初始化完成")
    
    @signal_receiver(SignalType.HIERARCHY_CAPTURE_REQUESTED)
    def _on_hierarchy_capture_requested(self, sender, signal_data):
        """处理层次结构捕获请求信号"""
        self.capture_requested_count += 1
        print(f"🌳 MockHierarchy {self.device_id} 收到层次结构捕获请求信号")


def test_decorator_signal_system():
    """测试装饰器信号系统"""
    print("🚀 开始测试装饰器信号系统...")
    
    # 创建模拟组件
    main_window = MockMainWindow()
    device_view = MockDeviceView("test_device")
    hierarchy = MockHierarchy("test_device")
    
    print("\n📡 测试信号发送和接收...")
    
    # 测试设备连接信号
    send_signal(SignalType.DEVICE_CONNECTED, sender=main_window, data={'device_id': 'test_device'})
    time.sleep(0.1)  # 等待信号处理
    
    # 测试设备断开信号
    send_signal(SignalType.DEVICE_DISCONNECTED, sender=main_window, data={'device_id': 'test_device'})
    time.sleep(0.1)
    
    # 测试层次结构更新信号
    send_signal(SignalType.HIERARCHY_UPDATED, sender=hierarchy, data={'device_id': 'test_device', 'elements': []})
    time.sleep(0.1)
    
    # 测试键盘快捷键信号
    send_signal(SignalType.KEYBOARD_SHORTCUT, sender=device_view, data={'key': 'Ctrl+R'})
    time.sleep(0.1)
    
    # 测试层次结构捕获请求信号
    send_signal(SignalType.HIERARCHY_CAPTURE_REQUESTED, sender=main_window, data={'device_id': 'test_device'})
    time.sleep(0.1)
    
    # 测试应用错误信号
    send_signal(SignalType.APP_ERROR, sender=main_window, data={'error': 'Test error message'})
    time.sleep(0.1)
    
    print("\n📊 验证信号接收结果...")
    
    # 验证MainWindow信号接收
    assert main_window.device_connected_count == 1, f"设备连接信号接收失败: {main_window.device_connected_count}"
    assert main_window.device_disconnected_count == 1, f"设备断开信号接收失败: {main_window.device_disconnected_count}"
    assert main_window.hierarchy_updated_count == 1, f"层次结构更新信号接收失败: {main_window.hierarchy_updated_count}"
    assert main_window.app_error_count == 1, f"应用错误信号接收失败: {main_window.app_error_count}"
    
    # 验证DeviceView信号接收
    assert device_view.keyboard_signal_count == 1, f"键盘信号接收失败: {device_view.keyboard_signal_count}"
    
    # 验证Hierarchy信号接收
    assert hierarchy.capture_requested_count == 1, f"层次结构捕获请求信号接收失败: {hierarchy.capture_requested_count}"
    
    print("✅ 所有信号接收验证通过!")
    
    # 测试信号清理
    print("\n🧹 测试信号清理...")
    main_window.cleanup_signals()
    device_view.cleanup_signals()
    hierarchy.cleanup_signals()
    
    # 再次发送信号，应该不会被接收
    old_counts = {
        'device_connected': main_window.device_connected_count,
        'keyboard': device_view.keyboard_signal_count,
        'capture_requested': hierarchy.capture_requested_count
    }
    
    send_signal(SignalType.DEVICE_CONNECTED, sender=main_window, data={'device_id': 'test_device'})
    send_signal(SignalType.KEYBOARD_SHORTCUT, sender=device_view, data={'key': 'Ctrl+T'})
    send_signal(SignalType.HIERARCHY_CAPTURE_REQUESTED, sender=main_window, data={'device_id': 'test_device'})
    time.sleep(0.1)
    
    # 验证信号清理后不再接收
    assert main_window.device_connected_count == old_counts['device_connected'], "信号清理失败，仍在接收信号"
    assert device_view.keyboard_signal_count == old_counts['keyboard'], "信号清理失败，仍在接收信号"
    assert hierarchy.capture_requested_count == old_counts['capture_requested'], "信号清理失败，仍在接收信号"
    
    print("✅ 信号清理验证通过!")
    
    print("\n🎉 装饰器信号系统测试完成，所有测试通过!")


async def test_async_signals():
    """测试异步信号处理"""
    print("\n🔄 测试异步信号处理...")
    
    class AsyncSignalReceiver(SignalMixin):
        def __init__(self):
            super().__init__()
            self.async_signal_count = 0
        
        @signal_receiver(SignalType.DEVICE_CONNECTED)
        def _on_async_device_connected(self, sender, signal_data):
            """同步处理设备连接信号（异步信号处理需要特殊处理）"""
            self.async_signal_count += 1
            print(f"🔄 处理设备连接信号完成")
    
    receiver = AsyncSignalReceiver()
    
    # 发送信号
    send_signal(SignalType.DEVICE_CONNECTED, sender=receiver, data={'device_id': 'async_test'})
    await asyncio.sleep(0.1)  # 等待处理完成
    
    # 验证信号处理
    assert receiver.async_signal_count == 1, f"信号处理失败: {receiver.async_signal_count}"
    print("✅ 异步环境下信号处理验证通过!")
    
    # 清理
    receiver.cleanup_signals()


if __name__ == "__main__":
    # 运行同步测试
    test_decorator_signal_system()
    
    # 运行异步测试
    asyncio.run(test_async_signals())
    
    print("\n🏆 所有装饰器信号系统测试完成!")