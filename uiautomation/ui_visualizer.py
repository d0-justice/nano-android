"""
UI可视化工具

负责UI元素的可视化显示和高亮
"""

import flet as ft
from typing import Dict, List, Any, Optional, Tuple


class UIVisualizer:
    """UI元素可视化工具"""
    
    def __init__(self, page: ft.Page = None):
        self.page = page
        self.overlay_controls = []
        self.highlight_color = ft.Colors.RED
        self.highlight_opacity = 0.3
        self.border_width = 2
    
    def create_element_overlay(self, element: Dict[str, Any], bounds: Dict[str, int]) -> Optional[ft.Container]:
        """为UI元素创建可视化覆盖层"""
        try:
            if not bounds:
                return None
            
            # 创建透明容器作为覆盖层
            overlay = ft.Container(
                left=bounds['left'],
                top=bounds['top'],
                width=bounds['width'],
                height=bounds['height'],
                bgcolor=ft.Colors.with_opacity(self.highlight_opacity, self.highlight_color),
                border=ft.Border.all(self.border_width, self.highlight_color),
                border_radius=2,
                tooltip=self._create_element_tooltip(element),
                on_click=lambda e, elem=element: self._on_element_click(elem)
            )
            
            return overlay
            
        except Exception as e:
            print(f"创建元素覆盖层失败: {e}")
            return None
    
    def _create_element_tooltip(self, element: Dict[str, Any]) -> str:
        """创建元素的提示信息"""
        tooltip_parts = []
        
        # 添加类名
        if element.get('class'):
            tooltip_parts.append(f"类型: {element['class']}")
        
        # 添加文本
        if element.get('text'):
            tooltip_parts.append(f"文本: {element['text']}")
        
        # 添加resource-id
        if element.get('resource-id'):
            tooltip_parts.append(f"ID: {element['resource-id']}")
        
        # 添加描述
        if element.get('content-desc'):
            tooltip_parts.append(f"描述: {element['content-desc']}")
        
        # 添加属性
        attributes = []
        if element.get('clickable') == 'true':
            attributes.append('可点击')
        if element.get('scrollable') == 'true':
            attributes.append('可滚动')
        if element.get('checkable') == 'true':
            attributes.append('可选择')
        if element.get('enabled') == 'false':
            attributes.append('已禁用')
        
        if attributes:
            tooltip_parts.append(f"属性: {', '.join(attributes)}")
        
        return '\n'.join(tooltip_parts)
    
    def _on_element_click(self, element: Dict[str, Any]):
        """处理元素点击事件"""
        print(f"点击了UI元素: {element.get('class', 'Unknown')} - {element.get('text', 'No text')}")
        # 这里可以触发回调或发送信号
    
    def highlight_element(self, element: Dict[str, Any], bounds: Dict[str, int], 
                         color: str = None, opacity: float = None) -> Optional[ft.Container]:
        """高亮显示特定元素"""
        highlight_color = color or self.highlight_color
        highlight_opacity = opacity or self.highlight_opacity
        
        if not bounds:
            return None
        
        highlight_overlay = ft.Container(
            left=bounds['left'],
            top=bounds['top'],
            width=bounds['width'],
            height=bounds['height'],
            bgcolor=ft.Colors.with_opacity(highlight_opacity, highlight_color),
            border=ft.Border.all(self.border_width * 2, highlight_color),
            border_radius=4,
            animate=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT)
        )
        
        return highlight_overlay
    
    def create_element_info_card(self, element: Dict[str, Any]) -> ft.Card:
        """创建元素信息卡片"""
        info_items = []
        
        # 基本信息
        if element.get('class'):
            info_items.append(
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.WIDGETS),
                    title=ft.Text("类型"),
                    subtitle=ft.Text(element['class'])
                )
            )
        
        if element.get('text'):
            info_items.append(
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.TEXT_FIELDS),
                    title=ft.Text("文本"),
                    subtitle=ft.Text(element['text'])
                )
            )
        
        if element.get('resource-id'):
            info_items.append(
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.FINGERPRINT),
                    title=ft.Text("Resource ID"),
                    subtitle=ft.Text(element['resource-id'])
                )
            )
        
        if element.get('content-desc'):
            info_items.append(
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.DESCRIPTION),
                    title=ft.Text("描述"),
                    subtitle=ft.Text(element['content-desc'])
                )
            )
        
        # 位置信息
        if element.get('bounds'):
            info_items.append(
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.CROP_FREE),
                    title=ft.Text("边界"),
                    subtitle=ft.Text(element['bounds'])
                )
            )
        
        # 属性信息
        attributes = []
        if element.get('clickable') == 'true':
            attributes.append("可点击")
        if element.get('scrollable') == 'true':
            attributes.append("可滚动")
        if element.get('checkable') == 'true':
            attributes.append("可选择")
        if element.get('enabled') == 'false':
            attributes.append("已禁用")
        if element.get('focusable') == 'true':
            attributes.append("可聚焦")
        
        if attributes:
            info_items.append(
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.SETTINGS),
                    title=ft.Text("属性"),
                    subtitle=ft.Text(", ".join(attributes))
                )
            )
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column(info_items, spacing=0),
                padding=10
            )
        )
    
    def get_element_color_by_type(self, element_class: str) -> str:
        """根据元素类型获取颜色"""
        color_map = {
            'Button': ft.Colors.BLUE,
            'TextView': ft.Colors.GREEN,
            'EditText': ft.Colors.ORANGE,
            'ImageView': ft.Colors.PURPLE,
            'LinearLayout': ft.Colors.GREY,
            'RelativeLayout': ft.Colors.BROWN,
            'FrameLayout': ft.Colors.PINK,
            'RecyclerView': ft.Colors.CYAN,
            'ListView': ft.Colors.LIME,
            'ScrollView': ft.Colors.INDIGO,
        }
        
        return color_map.get(element_class, ft.Colors.RED)
    
    def create_legend(self) -> ft.Container:
        """创建图例说明"""
        legend_items = [
            ft.Row([
                ft.Container(
                    width=20, height=20,
                    bgcolor=ft.Colors.BLUE,
                    border_radius=2
                ),
                ft.Text("Button", size=12)
            ]),
            ft.Row([
                ft.Container(
                    width=20, height=20,
                    bgcolor=ft.Colors.GREEN,
                    border_radius=2
                ),
                ft.Text("TextView", size=12)
            ]),
            ft.Row([
                ft.Container(
                    width=20, height=20,
                    bgcolor=ft.Colors.ORANGE,
                    border_radius=2
                ),
                ft.Text("EditText", size=12)
            ]),
            ft.Row([
                ft.Container(
                    width=20, height=20,
                    bgcolor=ft.Colors.GREY,
                    border_radius=2
                ),
                ft.Text("Layout", size=12)
            ])
        ]
        
        return ft.Container(
            content=ft.Column(
                [ft.Text("元素类型图例", weight=ft.FontWeight.BOLD)] + legend_items,
                spacing=5
            ),
            padding=10,
            bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
            border_radius=5
        )
    
    def set_highlight_style(self, color: str = None, opacity: float = None, border_width: int = None):
        """设置高亮样式"""
        if color:
            self.highlight_color = color
        if opacity is not None:
            self.highlight_opacity = opacity
        if border_width is not None:
            self.border_width = border_width