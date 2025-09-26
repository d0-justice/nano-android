import flet as ft

from typing import Dict, List, Any, Optional

import json

class ElementInspector(ft.Container):

   

    def __init__(self, page: ft.Page, **kwargs):

        super().__init__(**kwargs)

        self.page = page

        self.selected_element = None  

        self.property_table_ref = ft.Ref()  

        self.device_controller = None

        self.create_inspector_ui()

        

    def set_device_controller(self, device_controller):


        self.device_controller = device_controller

    
    def create_inspector_ui(self):


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

    

    def set_selected_element(self, element: Dict[str, Any]):
        """设置选中的元素"""
        self.selected_element = element
        self._update_property_display()
    
    def _update_property_display(self):
        """更新属性显示"""
        if self.property_table_ref.current and self.selected_element:
            # 更新属性表格数据
            self.property_table_ref.current.rows = self._create_property_rows()
            self.property_table_ref.current.update()
    
    def _create_property_panel(self) -> ft.Container:
        """创建属性面板"""
        return ft.Container(
            content=ft.Column([
                ft.Text("元素属性", size=16, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                self._create_property_data_table()
            ]),
            expand=True
        )

    def _create_property_data_table(self) -> ft.DataTable:
        """创建属性数据表格"""
        table = ft.DataTable(
            ref=self.property_table_ref,
            columns=[
                ft.DataColumn(ft.Text("属性")),
                ft.DataColumn(ft.Text("值"))
            ],
            rows=self._create_property_rows()
        )
        return table
    
    def _create_property_rows(self) -> List[ft.DataRow]:
        """创建属性行数据"""
        if not self.selected_element:
            return [ft.DataRow(cells=[
                ft.DataCell(ft.Text("无选中元素")),
                ft.DataCell(ft.Text(""))
            ])]
        
        rows = []
        for key, value in self.selected_element.items():
            if value:  # 只显示有值的属性
                rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(key)),
                    ft.DataCell(ft.Text(str(value)))
                ]))
        
        return rows

