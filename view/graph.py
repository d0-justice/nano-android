import flet as ft
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.signal_manager import SignalMixin


class Graph(SignalMixin):
    """图形管理类，负责处理图形显示相关的UI和逻辑"""
    
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
    
    def create_graph_canvas(self):
        """创建图形画布"""
        # 使用容器和定位来模拟图形节点
        node_data = [
            {"name": "Node A", "color": ft.Colors.RED_400},
            {"name": "Node B", "color": ft.Colors.BLUE_400},
            {"name": "Node C", "color": ft.Colors.GREEN_400},
            {"name": "Node D", "color": ft.Colors.ORANGE_400},
            {"name": "Node E", "color": ft.Colors.PURPLE_400},
            {"name": "Node F", "color": ft.Colors.CYAN_400}
        ]
        
        # 创建网格布局的节点
        rows = []
        for i in range(0, len(node_data), 3):  # 每行3个节点
            row_nodes = []
            for j in range(3):
                if i + j < len(node_data):
                    node = node_data[i + j]
                    node_container = ft.Container(
                        width=80,
                        height=80,
                        bgcolor=node["color"],
                        border_radius=40,  # 圆形
                        content=ft.Text(
                            node["name"].split()[-1],  # 只显示最后一个字符
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE,
                            text_align=ft.TextAlign.CENTER
                        ),
                        alignment=ft.alignment.center,
                        border=ft.border.all(2, ft.Colors.BLACK26),
                        animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
                        on_hover=lambda e: setattr(e.control, 'scale', 1.1 if e.data == 'true' else 1.0) or e.control.update()
                    )
                    row_nodes.append(node_container)
                else:
                    row_nodes.append(ft.Container())  # 空占位符
            
            rows.append(
                ft.Row(
                    row_nodes,
                    alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                    spacing=30
                )
            )
        
        # 添加连接信息文本
        connection_info = ft.Container(
            content=ft.Column([
                ft.Text("Network Connections:", size=14, weight=ft.FontWeight.BOLD),
                ft.Text("A ↔ B ↔ C", size=12),
                ft.Text("A ↔ E ↔ C", size=12),
                ft.Text("C ↔ D ↔ F", size=12),
                ft.Text("C ↔ F", size=12)
            ]),
            padding=10,
            bgcolor=ft.Colors.GREY_100,
            border_radius=8
        )
        
        return ft.Column([
            ft.Column(rows, spacing=30),
            ft.Container(height=20),
            connection_info
        ], alignment=ft.MainAxisAlignment.CENTER)

    def create_graph_tab_content(self):
        """创建图形标签页内容"""
        return ft.Container(
            content=ft.Stack([
                # Main content - graph canvas
                ft.Container(
                    content=ft.Column([
                        self.create_graph_canvas()
                    ], alignment=ft.MainAxisAlignment.CENTER, scroll=ft.ScrollMode.AUTO),
                    alignment=ft.alignment.center,
                    expand=True,
                    border=ft.border.all(1, ft.Colors.GREY_300),
                    border_radius=8,
                    padding=20
                )
            ]),
            padding=20,
            expand=True
        )