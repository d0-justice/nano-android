import flet as ft
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.signal_manager import SignalMixin, SignalType, connect_signal, send_signal
import random


class Flow(SignalMixin):
    """流程图管理类，负责处理流程图相关的UI和逻辑"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.flow_canvas_ref = ft.Ref[ft.Stack]()
        self.selected_node = None
        super().__init__()  # 调用SignalMixin的初始化
    
    def _setup_signal_connections(self):
        """设置信号连接"""
        connect_signal(SignalType.FLOW_NODE_CREATED, self._on_flow_node_created)
        connect_signal(SignalType.FLOW_NODE_DELETED, self._on_flow_node_deleted)
        connect_signal(SignalType.FLOW_NODE_SELECTED, self._on_flow_node_selected)
        connect_signal(SignalType.FLOW_CANVAS_CLEARED, self._on_flow_canvas_cleared)
        connect_signal(SignalType.FLOW_SAVED, self._on_flow_saved)
    
    def _on_flow_node_created(self, sender, signal_data):
        """处理流程节点创建信号"""
        if signal_data and signal_data.data:
            title = signal_data.data.get('title')
            position = signal_data.data.get('position', {})
            print(f"🔷 流程节点已创建: {title} at ({position.get('x', 0)}, {position.get('y', 0)})")
    
    def _on_flow_node_deleted(self, sender, signal_data):
        """处理流程节点删除信号"""
        if signal_data and signal_data.data:
            title = signal_data.data.get('title')
            print(f"🗑️ 流程节点已删除: {title}")
    
    def _on_flow_node_selected(self, sender, signal_data):
        """处理流程节点选择信号"""
        if signal_data and signal_data.data:
            title = signal_data.data.get('title')
            position = signal_data.data.get('position', {})
            print(f"👆 流程节点已选择: {title} at ({position.get('x', 0)}, {position.get('y', 0)})")
    
    def _on_flow_canvas_cleared(self, sender, signal_data):
        """处理流程画布清空信号"""
        if signal_data and signal_data.data:
            node_count = signal_data.data.get('node_count', 0)
            print(f"🧹 流程画布已清空，删除了 {node_count} 个节点")
    
    def _on_flow_saved(self, sender, signal_data):
        """处理流程保存信号"""
        if signal_data and signal_data.data:
            node_count = signal_data.data.get('node_count', 0)
            connection_count = signal_data.data.get('connection_count', 0)
            print(f"💾 流程已保存: {node_count} 个节点, {connection_count} 个连接")
    
    def create_flow_node(self, x, y, title="New Node"):
        """创建流程节点"""
        def on_node_click(e):
            # 取消选择之前的节点
            if self.selected_node:
                self.selected_node.border = ft.border.all(1, ft.Colors.GREY_400)
                self.selected_node.update()
            
            # 选择当前节点
            e.control.border = ft.border.all(2, ft.Colors.BLUE_600)
            self.selected_node = e.control
            e.control.update()
            
            # 发送节点选择信号
            send_signal(SignalType.FLOW_NODE_SELECTED, self, {
                'node': e.control,
                'title': title,
                'position': {'x': x, 'y': y}
            })

        def on_delete_click(e):
            # 发送节点删除信号
            send_signal(SignalType.FLOW_NODE_DELETED, self, {
                'node': e.control,
                'title': title
            })
            
            # 从画布中移除节点
            if self.flow_canvas_ref.current and self.flow_canvas_ref.current.content:
                controls = self.flow_canvas_ref.current.content.controls
                if e.control.parent in controls:
                    controls.remove(e.control.parent)
                    self.flow_canvas_ref.current.update()

        # 创建删除按钮
        delete_button = ft.IconButton(
            icon=ft.Icons.CLOSE,
            icon_size=12,
            tooltip="删除节点",
            on_click=on_delete_click,
            style=ft.ButtonStyle(
                color=ft.Colors.RED_400,
                bgcolor=ft.Colors.WHITE,
                shape=ft.CircleBorder()
            )
        )

        # 创建节点容器
        node = ft.Container(
            width=120,
            height=60,
            bgcolor=ft.Colors.LIGHT_BLUE_100,
            border=ft.border.all(1, ft.Colors.GREY_400),
            border_radius=8,
            content=ft.Stack([
                ft.Container(
                    content=ft.Text(
                        title,
                        size=12,
                        text_align=ft.TextAlign.CENTER,
                        weight=ft.FontWeight.BOLD
                    ),
                    alignment=ft.alignment.center
                ),
                ft.Container(
                    content=delete_button,
                    alignment=ft.alignment.top_right,
                    top=-5,
                    right=-5
                )
            ]),
            left=x,
            top=y,
            on_click=on_node_click,
            animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT)
        )
        
        # 发送节点创建信号
        send_signal(SignalType.FLOW_NODE_CREATED, self, {
            'node': node,
            'title': title,
            'position': {'x': x, 'y': y}
        })
        
        return node
    
    def add_flow_node(self, e):
        """添加新的流程节点"""
        import random
        
        # 随机位置
        x = random.randint(50, 400)
        y = random.randint(50, 300)
        
        # 创建新节点
        new_node = self.create_flow_node(x, y, f"Node {random.randint(1, 100)}")
        
        # 添加到画布
        if self.flow_canvas_ref.current and self.flow_canvas_ref.current.content:
            self.flow_canvas_ref.current.content.controls.append(new_node)
            self.flow_canvas_ref.current.update()

    def clear_flow_canvas(self, e):
        """清空流程画布"""
        # 发送画布清空信号
        node_count = len(self.flow_canvas_ref.current.content.controls) if self.flow_canvas_ref.current and self.flow_canvas_ref.current.content else 0
        send_signal(SignalType.FLOW_CANVAS_CLEARED, self, {
            'node_count': node_count
        })
        
        # 清空画布
        if self.flow_canvas_ref.current and self.flow_canvas_ref.current.content:
            self.flow_canvas_ref.current.content.controls.clear()
            self.flow_canvas_ref.current.update()
        
        # 重置选中节点
        self.selected_node = None

    def save_flow(self, e):
        """保存流程"""
        # 获取当前节点数量
        node_count = len(self.flow_canvas_ref.current.content.controls) if self.flow_canvas_ref.current and self.flow_canvas_ref.current.content else 0
        
        # 发送流程保存信号
        send_signal(SignalType.FLOW_SAVED, self, {
            'node_count': node_count,
            'connection_count': 0  # 暂时设为0，因为连接功能还未实现
        })
        
        print(f"流程已保存: {node_count} 个节点")

    def add_initial_flow_node(self):
        """添加初始流程节点"""
        initial_node = self.create_flow_node(100, 100, "Start")
        
        # 添加到画布
        if self.flow_canvas_ref.current and self.flow_canvas_ref.current.content:
            self.flow_canvas_ref.current.content.controls.append(initial_node)
            self.flow_canvas_ref.current.update()

    def create_flow_tab_content(self):
        """创建流程图标签页内容"""
        return ft.Container(
            content=ft.Column([
                ft.Text("Workflow Flow", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800),
                ft.Text("Interactive flow diagram for visualizing processes", size=14, color=ft.Colors.GREY_600),
                ft.Container(
                    content=ft.Row([
                        ft.ElevatedButton(
                            "Add Node",
                            icon=ft.Icons.ADD_CIRCLE_OUTLINE,
                            on_click=self.add_flow_node,
                            style=ft.ButtonStyle(
                                bgcolor=ft.Colors.BLUE_600,
                                color=ft.Colors.WHITE
                            )
                        ),
                        ft.ElevatedButton(
                            "Clear Canvas",
                            icon=ft.Icons.CLEAR_ALL,
                            on_click=self.clear_flow_canvas,
                            style=ft.ButtonStyle(
                                bgcolor=ft.Colors.RED_600,
                                color=ft.Colors.WHITE
                            )
                        ),
                        ft.ElevatedButton(
                            "Save Flow",
                            icon=ft.Icons.SAVE,
                            on_click=self.save_flow,
                            style=ft.ButtonStyle(
                                bgcolor=ft.Colors.GREEN_600,
                                color=ft.Colors.WHITE
                            )
                        )
                    ], spacing=10),
                    padding=ft.padding.only(bottom=20)
                ),
                ft.Container(
                    ref=self.flow_canvas_ref,
                    content=ft.Stack([
                        # 初始节点将在这里添加
                    ], expand=True),
                    expand=True,
                    border=ft.border.all(1, ft.Colors.GREY_400),
                    border_radius=8,
                    padding=20,
                    bgcolor=ft.Colors.WHITE
                )
            ], expand=True),
            padding=20,
            expand=True
        )