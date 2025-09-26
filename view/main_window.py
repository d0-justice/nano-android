import flet as ft
import random
import math
import threading
import time

from .device_view import DeviceView
from .device_screenshot import DeviceScreenshot
from .element_inspector import ElementInspector
from .hierarchy import Hierarchy
from .graph import Graph
from .chat import Chat
from .flow import Flow
from .code import Code

# 导入信号管理器
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.signal_manager import SignalType, send_signal, signal_receiver, SignalMixin


class Config:
    # Window configuration
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800
    
    # Layout configuration
    HEADER_HEIGHT = 40
    LEFT_CONTAINER_WIDTH = 800
    BOTTOM_PADDING = 5
    
    # Scroll configuration
    SCROLL_DURATION = 150
    SCROLL_CURVE = ft.AnimationCurve.EASE_OUT
    
    # Node configuration
    NODE_SIZE = 80
    NODE_RADIUS = 40
    
    # Color configuration
    HEADER_COLOR = ft.Colors.BLUE_400
    LEFT_BG_COLOR = ft.Colors.RED_100
    RIGHT_BG_COLOR = ft.Colors.BLUE_100


class MainWindow(SignalMixin):
    def __init__(self, page: ft.Page):
        self.page = page
        # 单个视图实例 - 简化管理
        self.device_view = None
        self.device_screenshot = None
        self.element_inspector = None
        self.hierarchy = None
        self.selected_node = None
        self.flow_canvas_ref = ft.Ref()
        self.horizontal_listview_ref = ft.Ref()  # 新增：横向ListView的引用
        self.listview_page_state = 1  # 新增属性：记录ListView的滚动翻页状态，默认为1
        
        # 调用SignalMixin的初始化，这会自动设置信号连接
        super().__init__()
        
        self._setup_page()
        self._setup_event_handlers()
        self._create_ui()
    
    def _setup_page(self):
        """设置页面属性"""
        print("程序开始启动...")
        self.page.title = "Flet 应用"
        self.page.window.width = Config.WINDOW_WIDTH
        self.page.window.height = Config.WINDOW_HEIGHT
        self.page.window.center()
        self.page.padding = 0
        print("页面配置完成...")
    
    def _setup_event_handlers(self):
        """设置窗口事件处理器，和"""
        self.page.window.on_event = self._on_window_event
        self.page.on_keyboard_event = self._on_keyboard
    

    @signal_receiver(SignalType.DEVICE_CONNECTED)
    def _on_device_connected(self, sender, signal_data):
        """处理设备连接信号"""
        if signal_data and signal_data.data:
            device_name = signal_data.data.get('device_name')
            print(f"📱 主窗口收到设备连接信号: {device_name}")
            # 可以在这里更新UI状态，比如状态栏显示
    
    @signal_receiver(SignalType.DEVICE_DISCONNECTED)
    def _on_device_disconnected(self, sender, signal_data):
        """处理设备断开信号"""
        if signal_data and signal_data.data:
            device_name = signal_data.data.get('device_name')
            print(f"📱 主窗口收到设备断开信号: {device_name}")
            # 可以在这里更新UI状态
    
    @signal_receiver(SignalType.HIERARCHY_UPDATED)
    def _on_hierarchy_updated(self, sender, signal_data):
        """处理层次结构更新信号"""
        if signal_data and signal_data.data:
            device_id = signal_data.data.get('device_id')
            elements_count = len(signal_data.data.get('elements', []))
            print(f"🏠 主窗口收到层次结构更新信号: {device_id}, 元素数量: {elements_count}")
            # 可以在这里处理层次结构更新后的逻辑
    
    @signal_receiver(SignalType.APP_ERROR)
    def _on_app_error(self, sender, signal_data):
        """处理应用错误信号"""
        if signal_data and signal_data.data:
            error_type = signal_data.data.get('error_type')
            error = signal_data.data.get('error')
            print(f"🏠 主窗口收到错误信号: {error_type} - {error}")
            # 可以在这里显示错误提示
    
    @signal_receiver(SignalType.FLOW_NODE_CREATED)
    def _on_flow_node_created(self, sender, signal_data):
        """处理流程节点创建信号"""
        if signal_data and signal_data.data:
            title = signal_data.data.get('title')
            position = signal_data.data.get('position', {})
            print(f"🔷 流程节点已创建: {title} at ({position.get('x', 0)}, {position.get('y', 0)})")
    
    @signal_receiver(SignalType.FLOW_NODE_DELETED)
    def _on_flow_node_deleted(self, sender, signal_data):
        """处理流程节点删除信号"""
        if signal_data and signal_data.data:
            title = signal_data.data.get('title')
            print(f"🗑️ 流程节点已删除: {title}")
    
    @signal_receiver(SignalType.FLOW_NODE_SELECTED)
    def _on_flow_node_selected(self, sender, signal_data):
        """处理流程节点选择信号"""
        if signal_data and signal_data.data:
            title = signal_data.data.get('title')
            position = signal_data.data.get('position', {})
            print(f"🎯 流程节点已选择: {title} at ({position.get('x', 0)}, {position.get('y', 0)})")
    
    @signal_receiver(SignalType.FLOW_CANVAS_CLEARED)
    def _on_flow_canvas_cleared(self, sender, signal_data):
        """处理流程画布清空信号"""
        if signal_data and signal_data.data:
            node_count = signal_data.data.get('node_count', 0)
            print(f"🧹 流程画布已清空，删除了 {node_count} 个节点")
    
    @signal_receiver(SignalType.FLOW_SAVED)
    def _on_flow_saved(self, sender, signal_data):
        """处理流程保存信号"""
        if signal_data and signal_data.data:
            node_count = signal_data.data.get('node_count', 0)
            connection_count = signal_data.data.get('connection_count', 0)
            print(f"💾 流程已保存: {node_count} 个节点, {connection_count} 个连接")
    
    def _on_window_event(self, e):
        """页面关闭事件处理"""
        if e.data == "close":
            print("窗口正在关闭，清理资源...")
            # 清理DeviceView实例
            if self.device_view and hasattr(self.device_view, 'cleanup'):
                self.device_view.cleanup()
            # 清理信号连接
            self.cleanup_signals()
            print("资源清理完成")
    
    
    def _handle_hierarchy_capture(self):
        """处理层次结构捕获请求"""
        try:
            print("开始处理层次结构捕获...")
            
            # 发送层次结构捕获请求信号，让所有相关组件响应
            send_signal(SignalType.HIERARCHY_CAPTURE_REQUESTED, self, {
                'timestamp': time.time()
            })
            
            print("层次结构捕获请求已发送")
            
        except Exception as e:
            print(f"处理层次结构捕获失败: {e}")
            send_signal(SignalType.APP_ERROR, self, {
                'error_type': 'hierarchy_capture_failed',
                'error': str(e)
            })
    

    def _on_keyboard(self, e: ft.KeyboardEvent):
        """处理F1-F4快捷键滚动、`键UI hierarchy获取和设备键盘事件"""
        print(f"键盘事件: {e.key}, shift: {e.shift}, ctrl: {e.ctrl}, alt: {e.alt}")  # 调试日志
        
        # 检查F1-F4键，更新ListView翻页状态和滚动
        if e.key == "F1":
            # F1键被 再次按下，触发截图功能
            if self.listview_page_state == 1:
                # 从第一个view中截屏更新到第二个view
                screenshot = self.device_view.capture_screenshot()
                self.device_screenshot.update_screenshot(screenshot)
                return
            self.listview_page_state = 1
            print(f"ListView翻页状态更新为: {self.listview_page_state}")
            self._scroll_to_position(e.key)

        elif e.key == "F2":
            # F2被 再次按下，触 发获取UI数据
            if self.listview_page_state == 2:
                print("检测到`键，开始获取UI hierarchy...")
                self._handle_hierarchy_capture()
                return  # 直接返回，避免进入其他条件
            self.listview_page_state = 2
            print(f"ListView翻页状态更新为: {self.listview_page_state}")
            self._scroll_to_position(e.key)
        elif e.key == "F3":
            self.listview_page_state = 3
            print(f"ListView翻页状态更新为: {self.listview_page_state}")
            self._scroll_to_position(e.key)
        elif e.key == "F4":
            self.listview_page_state = 4
            print(f"ListView翻页状态更新为: {self.listview_page_state}")
            self._scroll_to_position(e.key)
        else:
            # 使用信号系统转发键盘事件给设备视图
            send_signal(SignalType.KEYBOARD_SHORTCUT, self, {
                'type': 'key_press',
                'event': e
            })
    
    def _create_ui(self):
        """创建用户界面"""
        # 滚动位置配置
        self.SCROLL_POSITIONS = {
            "F1": 0,
            "F2": 390,
            "F3": 780,
            "F4": 1170
        }
        
        # 添加头部
        header = ft.Container(
            height=Config.HEADER_HEIGHT,
            bgcolor=Config.HEADER_COLOR,
            width=float('inf')
        )
        
        # 创建主布局
        main_content = self._create_main_layout()
        
        # 添加控件到页面
        self.page.add(
            ft.Column([
                header,  # Add header
                main_content  # Main content area
            ], 
            spacing=0,  # Remove default spacing
            expand=True)  # Fill entire page height
        )
        
        # 更新页面并添加初始流程节点
        self.page.update()
        self._add_initial_flow_node()
    
    def _scroll_to_position(self, key: str):
        """滚动到指定位置"""
        if self.horizontal_listview_ref.current:
            if key in self.SCROLL_POSITIONS:
                self.horizontal_listview_ref.current.scroll_to(
                    offset=self.SCROLL_POSITIONS[key],
                    duration=Config.SCROLL_DURATION,
                    curve=Config.SCROLL_CURVE
                )
                self.page.update()
                print(f"滚动到位置: {key}, 偏移量: {self.SCROLL_POSITIONS[key]}")  # 调试信息
    
    def _create_list_item(self, index):
        """创建带抽屉翻页效果的ListView项目"""
        # 定义特定的项目名称和快捷键
        item_names = [
            ("Realtime(F1)", "实时图"),
            ("Screenshot(F2)", "抓取的截图"),
            ("Element Inspector(F3)", "页面元素属性"),
            ("Hierarchy(F4)", "页面资源树"),
            ("Workspace", "当前工作区")
        ]
        
        # 随机选择背景颜色
        colors = [
            ft.Colors.RED_200, ft.Colors.BLUE_200, ft.Colors.GREEN_200,
            ft.Colors.YELLOW_200, ft.Colors.PURPLE_200, ft.Colors.ORANGE_200,
            ft.Colors.PINK_200, ft.Colors.CYAN_200, ft.Colors.TEAL_200,
            ft.Colors.INDIGO_200, ft.Colors.LIME_200, ft.Colors.AMBER_200
        ]
        random_color = random.choice(colors)
        
        # 获取项目名称
        if index < len(item_names):
            display_name, description = item_names[index]
        else:
            display_name = f"Item {index + 1}"
            description = "Default item"
        
        # 创建可点击的抽屉项目
        def on_item_click(e):
            # 获取父容器控件（Container）
            current_control = e.control.parent if hasattr(e.control, 'parent') else e.control
            
            # 增强阴影效果 - 统一为右下阴影
            enhanced_shadow = ft.BoxShadow(
                spread_radius=0,
                blur_radius=16,
                color=ft.Colors.with_opacity(0.4, ft.Colors.BLACK),
                offset=ft.Offset(3, 4)  # 右下方向
            )
            
            current_control.shadow = enhanced_shadow
            current_control.update()
            
            # 短暂延迟后恢复原阴影
            import threading
            def restore_shadow():
                normal_shadow = ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=8,
                    color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK),
                    offset=ft.Offset(1, 2)  # 右下方向
                )
                current_control.shadow = normal_shadow
                current_control.update()
            threading.Timer(0.3, restore_shadow).start()
        
        # 创建hover效果
        def on_item_hover(e):
            # 获取父容器控件（Container）
            current_control = e.control.parent if hasattr(e.control, 'parent') else e.control
            
            if e.data == "true":  # 鼠标进入
                # 增强浮动效果 - 统一为右下阴影
                enhanced_shadow = ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=12,
                    color=ft.Colors.with_opacity(0.35, ft.Colors.BLACK),
                    offset=ft.Offset(2, 3)  # 右下方向
                )
                current_control.shadow = enhanced_shadow
            else:  # 鼠标离开
                # 恢复普通浮动效果 - 统一为右下阴影
                normal_shadow = ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=8,
                    color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK),
                    offset=ft.Offset(1, 2)  # 右下方向
                )
                current_control.shadow = normal_shadow
            
            current_control.update()
        
        # 创建独立的标题栏
        title_bar = ft.Container(
            height=60,  # 调整高度到60px
            bgcolor=ft.Colors.with_opacity(0.9, random_color),  # 稍微透明一些
            content=ft.Text(
                display_name, 
                size=12,  # 缩小字体
                text_align=ft.TextAlign.CENTER, 
                color=ft.Colors.WHITE, 
                weight=ft.FontWeight.BOLD
            ),
            alignment=ft.alignment.center,
            border_radius=8,  # 缩小圆角
            margin=ft.margin.only(top=10, bottom=10),  # 顶部和底部间距都设为10px
            padding=ft.padding.symmetric(horizontal=8, vertical=10),  # 增加垂直内边距
            border=ft.border.all(1, ft.Colors.with_opacity(0.2, ft.Colors.WHITE)),  # 更细的边框
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=8,
                color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK),
                offset=ft.Offset(1, 2)  # 右下方向
            ),
            animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT),  # 添加动画效果
            on_click=on_item_click,  # 添加点击事件
            on_hover=on_item_hover,  # 添加hover事件
            ink=True,  # 添加点击涟漪效果
            tooltip=f"标题: {display_name}"  # 添加提示文本
        )
        
        # 创建独立的内容区域
        if index == 0:  # 第一个item使用DeviceView
            content_area = DeviceView("acde74a2", bgcolor=ft.Colors.with_opacity(0.9, random_color))
            # 将DeviceView实例保存为单个实例
            self.device_view = content_area
        elif index == 1:  # 第二个item使用DeviceScreenshot
            content_area = DeviceScreenshot(bgcolor=ft.Colors.with_opacity(0.9, random_color))
            # 将DeviceScreenshot实例保存为单个实例
            self.device_screenshot = content_area
        elif index == 2:  # 第三个item使用ElementInspector
            content_area = ElementInspector(self.page, bgcolor=ft.Colors.with_opacity(0.9, random_color))
            # 将ElementInspector实例保存为单个实例
            self.element_inspector = content_area
        elif index == 3:  # 第四个item使用Hierarchy
            content_area = Hierarchy(self.page, bgcolor=ft.Colors.with_opacity(0.9, random_color))
            
            # 设置元素选择回调，连接到对应的ElementInspector
            if self.element_inspector:
                content_area.set_element_select_callback(self.element_inspector.set_selected_element)
            
            # 将Hierarchy实例保存为单个实例
            self.hierarchy = content_area
        else:  # 其他item使用原来的文本内容
            content_area = ft.Container(
                expand=True,  # 填充剩余空间
                bgcolor=random_color,
                content=ft.Text(
                    description, 
                    size=10,  # 缩小字体
                    text_align=ft.TextAlign.CENTER, 
                    color=ft.Colors.WHITE, 
                    weight=ft.FontWeight.NORMAL
                ),
                alignment=ft.alignment.center,
                border_radius=8,  # 缩小圆角
                padding=ft.padding.all(12),  # 增加内边距
                border=ft.border.all(1, ft.Colors.with_opacity(0.2, ft.Colors.WHITE)),  # 更细的边框
                shadow=ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=8,
                    color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK),
                    offset=ft.Offset(1, 2)  # 右下方向
                ),
                animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT),  # 添加动画效果
                on_click=on_item_click,  # 添加点击事件
                on_hover=on_item_hover,  # 添加hover事件
                ink=True,  # 添加点击涟漪效果
                tooltip=f"内容: {description}"  # 添加提示文本
            )
        
        return ft.Container(
            width=380,  # 恢复原始宽度，每个item宽度为380px
            expand=True,  # 高度填满整个容器
            bgcolor=ft.Colors.TRANSPARENT,  # 完全透明背景
            content=ft.Column([
                title_bar,
                content_area
            ], spacing=10),  # 恢复为10px
            margin=ft.margin.all(10)  # 5像素边距
        )
    
    
    def _create_horizontal_listview(self):
        """创建横向ListView"""
        # 创建5个列表项
        items = [self._create_list_item(i) for i in range(5)]
        
        # 创建横向滚动的Row，并设置ref引用
        horizontal_row = ft.Row(
            controls=items,
            spacing=0,  # 移除间距
            scroll=ft.ScrollMode.AUTO,  # 启用滚动
            alignment=ft.MainAxisAlignment.START,
            ref=self.horizontal_listview_ref  # 设置引用
        )
        
        return ft.Container(
            content=horizontal_row,
            expand=True,  # 填充剩余空间
            padding=ft.padding.all(0)  # 移除内边距
        )
    

    def _create_tabs(self):
        # 创建各个组件实例
        graph_component = Graph(self.page)
        code_component = Code(self.page)
        chat_component = Chat(self.page)
        flow_component = Flow(self.page)
        
        tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(
                    text="Graph",
                    content=graph_component.create_graph_tab_content()
                ),
                ft.Tab(
                    text="Code",
                    content=code_component.create_code_tab_content()
                ),
                ft.Tab(
                    text="Chat",
                    content=chat_component.create_chat_tab_content()
                ),
                ft.Tab(
                    text="Flow",
                    content=flow_component.create_flow_tab_content()
                )
            ],
            expand=True
        )
        return tabs

    def _create_main_layout(self):
        # 创建左侧容器
        horizontal_listview = self._create_horizontal_listview()
        left_container = ft.Container(
            bgcolor=Config.LEFT_BG_COLOR,
            width=Config.LEFT_CONTAINER_WIDTH,
            content=ft.Column([horizontal_listview]),
            padding=ft.padding.only(bottom=Config.BOTTOM_PADDING)
        )
        
        # 创建右侧容器
        tabs = self._create_tabs()
        right_container = ft.Container(
            bgcolor=ft.Colors.BLUE_100,  # Light blue background
            expand=True,  # Dynamically fill remaining width
            content=tabs,
            padding=ft.padding.only(bottom=10)  # 底部增加10px间距
        )
        
        # 创建主内容行
        main_content = ft.Row([
            left_container,
            right_container
        ], 
        expand=True,  # Fill height
        spacing=0)  # Remove spacing
        
        return main_content

    def _add_initial_flow_node(self):
        """添加初始流程节点"""
        # 初始化逻辑已移至Flow组件中
        pass