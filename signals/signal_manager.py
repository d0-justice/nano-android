"""
信号管理�?- 基于blinker的应用级信号系统

提供统一的信号注册、发送和接收机制，用于解耦组件间的通信
"""

from blinker import signal
from typing import Any, Callable, Dict, Optional
import threading
from dataclasses import dataclass
from enum import Enum


class SignalType(Enum):
    """信号类型枚举"""
    # 设备相关信号
    DEVICE_CONNECTED = "device.connected"
    DEVICE_DISCONNECTED = "device.disconnected"
    DEVICE_FRAME_UPDATED = "device.frame_updated"
    DEVICE_SCREENSHOT_CAPTURED = "device.screenshot_captured"
    
    # UI层次结构相关信号
    HIERARCHY_UPDATED = "hierarchy.updated"
    HIERARCHY_ELEMENT_SELECTED = "hierarchy.element_selected"
    HIERARCHY_CAPTURE_REQUESTED = "hierarchy.capture_requested"
    
    # 元素检查器相关信号
    ELEMENT_INSPECTED = "element.inspected"
    ELEMENT_HIGHLIGHTED = "element.highlighted"
    ELEMENT_PROPERTIES_UPDATED = "element.properties_updated"
    
    # 流程图相关信�?   FLOW_NODE_CREATED = "flow.node_created"
    FLOW_NODE_DELETED = "flow.node_deleted"
    FLOW_NODE_SELECTED = "flow.node_selected"
    FLOW_CANVAS_CLEARED = "flow.canvas_cleared"
    FLOW_SAVED = "flow.saved"
    
    # 界面导航相关信号
    TAB_SWITCHED = "ui.tab_switched"
    PAGE_SCROLLED = "ui.page_scrolled"
    KEYBOARD_SHORTCUT = "ui.keyboard_shortcut"
    
    # 应用状态相关信�?   APP_CLOSING = "app.closing"
    APP_ERROR = "app.error"
    APP_STATUS_CHANGED = "app.status_changed"


@dataclass
class SignalData:
    """信号数据包装
    sender: Any
    data: Any
    timestamp: float
    signal_type: SignalType
    """

class SignalManager:
    """
    信号管理
    单例模式
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._signals: Dict[str, signal] = {}
            self._receivers: Dict[str, list] = {}
            self._lock = threading.RLock()
            self._initialized = True
            self._setup_signals()
    
    def _setup_signals(self):
        """
        初始化所有信
        """
        for signal_type in SignalType:
            self._signals[signal_type.value] = signal(signal_type.value)
            self._receivers[signal_type.value] = []
    
    def connect(self, signal_type: SignalType, receiver: Callable, sender: Any = None) -> None:
        """
        连接信号接收        
        Args:
            signal_type: 信号类型
            receiver: 接收器函            
            sender: 可选的发送者过    
        """
        with self._lock:
            signal_obj = self._signals.get(signal_type.value)
            if signal_obj:
                if sender:
                    signal_obj.connect(receiver, sender=sender)
                else:
                    signal_obj.connect(receiver)
                
                self._receivers[signal_type.value].append({
                    'receiver': receiver,
                    'sender': sender
                })
                print(f"�?信号连接成功: {signal_type.value} -> {receiver.__name__}")
            else:
                print(f"�?信号类型不存�?{signal_type.value}")
    
    def disconnect(self, signal_type: SignalType, receiver: Callable, sender: Any = None) -> None:
        """
        断开信号接收�?       
        Args:
            signal_type: 信号类型
            receiver: 接收器函�?           sender: 可选的发送者过滤器        """
        with self._lock:
            signal_obj = self._signals.get(signal_type.value)
            if signal_obj:
                if sender:
                    signal_obj.disconnect(receiver, sender=sender)
                else:
                    signal_obj.disconnect(receiver)
                
                # 从接收器列表中移�?               receivers_list = self._receivers[signal_type.value]
                self._receivers[signal_type.value] = [
                    r for r in receivers_list 
                    if not (r['receiver'] == receiver and r['sender'] == sender)
                ]
                print(f"�?信号断开成功: {signal_type.value} -> {receiver.__name__}")
    
    def send(self, signal_type: SignalType, sender: Any, data: Any = None) -> list:
        """
        发送信�?       
        Args:
            signal_type: 信号类型
            sender: 发送�?           data: 信号数据
            
        Returns:
            接收器返回值列�?       """
        with self._lock:
            signal_obj = self._signals.get(signal_type.value)
            if signal_obj:
                import time
                signal_data = SignalData(
                    sender=sender,
                    data=data,
                    timestamp=time.time(),
                    signal_type=signal_type
                )
                
                print(f"📡 发送信�?{signal_type.value} from {sender.__class__.__name__}")
                results = signal_obj.send(sender, signal_data=signal_data)
                return [result[1] for result in results]  # 返回接收器的返回�?           else:
                print(f"�?信号类型不存�?{signal_type.value}")
                return []
    
    def send_async(self, signal_type: SignalType, sender: Any, data: Any = None):
        """
        异步发送信号（在新线程中）
        
        Args:
            signal_type: 信号类型
            sender: 发送�?           data: 信号数据
        """
        def _async_send():
            self.send(signal_type, sender, data)
        
        thread = threading.Thread(target=_async_send, daemon=True)
        thread.start()
    
    def get_receivers_count(self, signal_type: SignalType) -> int:
        """获取指定信号的接收器数量"""
        with self._lock:
            return len(self._receivers.get(signal_type.value, []))
    
    def list_signals(self) -> Dict[str, int]:
        """列出所有信号及其接收器数量"""
        with self._lock:
            return {
                signal_name: len(receivers)
                for signal_name, receivers in self._receivers.items()
            }
    
    def clear_all_connections(self):
        """清除所有信号连接（主要用于测试和清理）"""
        with self._lock:
            for signal_obj in self._signals.values():
                signal_obj.receivers.clear()
            for receivers_list in self._receivers.values():
                receivers_list.clear()
            print("🧹 所有信号连接已清除")


# 全局信号管理器实例signal_manager = SignalManager()


# 便捷函数
def connect_signal(signal_type: SignalType, receiver: Callable, sender: Any = None):
    """连接信号的便捷函"""
    signal_manager.connect(signal_type, receiver, sender)


def disconnect_signal(signal_type: SignalType, receiver: Callable, sender: Any = None):
    """断开信号的便捷函"""
    signal_manager.disconnect(signal_type, receiver, sender)


def send_signal(signal_type: SignalType, sender: Any, data: Any = None):
    """发送信号的便捷函数"""
    return signal_manager.send(signal_type, sender, data)


def send_signal_async(signal_type: SignalType, sender: Any, data: Any = None):
    """异步发送信号的便捷函数"""
    signal_manager.send_async(signal_type, sender, data)


# 装饰器支持def signal_receiver(signal_type: SignalType, sender: Any = None):
    """
    信号接收器装饰器
    
    Usage:
        @signal_receiver(SignalType.DEVICE_CONNECTED)
        def on_device_connected(sender, signal_data):
            print(f"Device connected: {signal_data.data}")
    """
    def decorator(func: Callable):
        # 如果是类方法，延迟连接到实例化时
        if hasattr(func, '__self__'):
            # 已绑定的方法，直接连            
            connect_signal(signal_type, func, sender)
        else:
            # 未绑定的方法，标记为需要延迟连           
            if not hasattr(func, '_signal_connections'):
                func._signal_connections = []
            func._signal_connections.append({
                'signal_type': signal_type,
                'sender': sender
            })
        return func
    return decorator


class SignalMixin:
    """信号混入类，为类提供自动信号连接管理"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._connected_signals = []
        self._setup_signal_connections()
    
    def _setup_signal_connections(self):
        """自动设置类中所有带有信号装饰器的方"""
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if callable(attr) and hasattr(attr, '_signal_connections'):
                for connection in attr._signal_connections:
                    signal_type = connection['signal_type']
                    sender = connection['sender']
                    connect_signal(signal_type, attr, sender)
                    self._connected_signals.append({
                        'signal_type': signal_type,
                        'receiver': attr,
                        'sender': sender
                    })
                    print(f"?自动信号连接: {signal_type.value} -> {attr.__name__}")
    
    def cleanup_signals(self):
        """清理所有信号连"""
        for connection in self._connected_signals:
            try:
                disconnect_signal(
                    connection['signal_type'],
                    connection['receiver'],
                    connection['sender']
                )
                print(f"🔌 信号断开: {connection['signal_type'].value} -> {connection['receiver'].__name__}")
            except Exception as e:
                print(f"�?信号断开失败: {e}")
        self._connected_signals.clear()


def signal_handler(*signal_types):
    """
    类装饰器，为类添加信号处理能�?   
    Usage:
        @signal_handler(SignalType.DEVICE_CONNECTED, SignalType.DEVICE_DISCONNECTED)
        class MyClass:
            @signal_receiver(SignalType.DEVICE_CONNECTED)
            def on_device_connected(self, sender, signal_data):
                pass
    """
    def decorator(cls):
        # 确保类继承自SignalMixin
        if not issubclass(cls, SignalMixin):
            # 动态添加SignalMixin到基类列�?           
            class SignalEnabledClass(SignalMixin, cls):
                pass
            SignalEnabledClass.__name__ = cls.__name__
            SignalEnabledClass.__qualname__ = cls.__qualname__
            return SignalEnabledClass
        return cls
    return decorator
