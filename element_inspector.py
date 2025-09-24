import flet as ft
from typing import Dict, List, Any, Optional
import json


class ElementInspector(ft.Container):
    """元素检查器 - 负责显示元素属性信息"""
    
    def __init__(self, page: ft.Page, **kwargs):
        super().__init__(**kwargs)
        self.page = page
        self.selected_element = None  # 当前选中的元素
        self.property_table_ref = ft.Ref()  # 属性表格的引用
        self.device_controller = None  # 设备控制器引用
        self.create_inspector_ui()
        
    def set_device_controller(self, device_controller):
        """设置设备控制器"""
        self.device_controller = device_controller
        
    def create_inspector_ui(self):
        """创建元素检查器的UI界面"""
        self.content = self._create_property_panel()
        self.padding = ft.padding.all(10)
        self.expand = True
        self.border_radius = 10
        self.shadow = ft.BoxShadow(
            spread_radius=1,
            blur_radius=15,
            color=ft.Colors.with_opacity(0.3, ft.Colors.GREY_400),
            offset=ft.Offset(0, 4)
        )
    
    def _create_property_panel(self) -> ft.Container:
        """创建属性面板（使用DataTable）"""
        return ft.Container(
            content=ft.Column(
                controls=[
                    # 标题栏
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Text("元素属性", size=16, weight=ft.FontWeight.BOLD),
                                ft.IconButton(
                                    icon=ft.Icons.REFRESH,
                                    tooltip="刷新属性",
                                    on_click=self._refresh_properties
                                )
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        padding=ft.padding.all(10),
                        bgcolor=ft.Colors.GREEN_50,
                        border_radius=8,
                        shadow=ft.BoxShadow(
                            spread_radius=0,
                            blur_radius=8,
                            color=ft.Colors.with_opacity(0.2, ft.Colors.GREEN_300),
                            offset=ft.Offset(0, 2)
                        )
                    ),
                    # 属性DataTable
                    ft.Container(
                        content=self._create_property_data_table(),
                        expand=True,
                        border=ft.border.all(1, ft.Colors.GREY_300),
                        border_radius=8,
                        bgcolor=ft.Colors.WHITE,
                        shadow=ft.BoxShadow(
                            spread_radius=0,
                            blur_radius=5,
                            color=ft.Colors.with_opacity(0.1, ft.Colors.GREY_500),
                            offset=ft.Offset(0, 2)
                        )
                    )
                ],
                spacing=10,
                expand=True
            ),
            expand=True,
            bgcolor=ft.Colors.GREY_50,
            border_radius=8
        )
    
    def _create_property_data_table(self) -> ft.DataTable:
        """创建属性DataTable"""
        return ft.DataTable(
            ref=self.property_table_ref,
            columns=[
                ft.DataColumn(ft.Text("属性名", size=12, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("属性值", size=12, weight=ft.FontWeight.BOLD)),
            ],
            rows=self._create_property_data_rows(),
            border=ft.border.all(1, ft.Colors.GREY_200),
            border_radius=8,
            show_checkbox_column=False,
            column_spacing=20,
            data_row_min_height=35,
            data_row_max_height=50,
            heading_row_height=35,
            horizontal_margin=10,
            show_bottom_border=True,
            bgcolor=ft.Colors.WHITE
        )

    def _create_property_data_rows(self) -> list:
        """创建属性数据行"""
        rows = []
        if not self.selected_element:
            # 显示提示信息
            rows.append(ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text("提示", size=11, weight=ft.FontWeight.W_500, color=ft.Colors.GREY_600)),
                    ft.DataCell(ft.Text("请从页面元素树中选择一个元素", size=11, color=ft.Colors.GREY_600)),
                ]
            ))
            return rows
        
        # 定义要显示的属性及其显示名称
        property_mapping = {
            'class': '类名',
            'text': '文本内容',
            'content-desc': '内容描述',
            'resource-id': '资源ID',
            'package': '包名',
            'bounds': '边界坐标',
            'clickable': '可点击',
            'enabled': '已启用',
            'focusable': '可聚焦',
            'focused': '已聚焦',
            'scrollable': '可滚动',
            'long-clickable': '可长按',
            'password': '密码字段',
            'selected': '已选中',
            'checkable': '可选择',
            'checked': '已选择'
        }
        
        for key, display_name in property_mapping.items():
            value = self.selected_element.get(key, '')
            if value or key in ['clickable', 'enabled', 'focusable', 'focused', 'scrollable', 'long-clickable', 'password', 'selected', 'checkable', 'checked']:
                # 对布尔值进行特殊处理
                if key in ['clickable', 'enabled', 'focusable', 'focused', 'scrollable', 'long-clickable', 'password', 'selected', 'checkable', 'checked']:
                    display_value = "是" if value == "true" else "否"
                else:
                    display_value = str(value) if value else "无"
                
                row = ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(display_name, size=11, weight=ft.FontWeight.W_500)),
                        ft.DataCell(ft.Text(display_value, size=11, max_lines=2)),
                    ]
                )
                rows.append(row)
        
        return rows

    def _refresh_properties(self, e):
        """刷新属性面板"""
        if self.property_table_ref.current:
            self.property_table_ref.current.rows = self._create_property_data_rows()
            self.property_table_ref.current.update()

    def set_selected_element(self, element: Dict[str, Any]):
        """设置选中的元素（供外部调用）"""
        self.selected_element = element
        
        # 更新属性面板
        if self.property_table_ref.current:
            self.property_table_ref.current.rows = self._create_property_data_rows()
            self.property_table_ref.current.update()

    def clear_selection(self):
        """清空选择"""
        self.selected_element = None
        # 清空属性面板
        if self.property_table_ref.current:
            self.property_table_ref.current.rows = self._create_property_data_rows()
            self.property_table_ref.current.update()

    def get_selected_element(self) -> Optional[Dict[str, Any]]:
        """获取当前选中的元素"""
        return self.selected_element