import flet as ft
import random
import math
import threading
import time
# from scrcpy.device import MyWin
# from scrcpy.image_provider import ImageProvider
from device_view import DeviceView
from device_screenshot import DeviceScreenshot


# 配置常量
class Config:
    # 窗口配置
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800
    
    # 容器配置
    HEADER_HEIGHT = 40
    LEFT_CONTAINER_WIDTH = 800
    BOTTOM_PADDING = 5
    
    # 滚动配置
    SCROLL_DURATION = 150
    SCROLL_CURVE = ft.AnimationCurve.EASE_OUT
    
    # 节点配置
    NODE_SIZE = 80
    NODE_RADIUS = 40
    
    # 颜色配置
    HEADER_COLOR = ft.Colors.BLUE_400
    LEFT_BG_COLOR = ft.Colors.RED_100
    RIGHT_BG_COLOR = ft.Colors.BLUE_100

def main(page: ft.Page):
    print("程序开始启动...")
    # 设置页面属性
    page.title = "Flet 应用"
    page.window.width = Config.WINDOW_WIDTH
    page.window.height = Config.WINDOW_HEIGHT
    
    page.window.center()
    page.padding = 0
    print("页面配置完成...")
    
    # 存储DeviceView实例以便清理
    # 全局变量存储设备视图和截图组件实例
    device_views = []
    device_screenshots = []
    
    # 页面关闭事件处理
    def on_window_event(e):
        if e.data == "close":
            print("窗口正在关闭，清理资源...")
            # 清理所有DeviceView实例
            for device_view in device_views:
                if hasattr(device_view, 'cleanup'):
                    device_view.cleanup()
            print("资源清理完成")
    
    page.on_window_event = on_window_event
    
    
    # 添加头部
    header = ft.Container(
        height=Config.HEADER_HEIGHT,
        bgcolor=Config.HEADER_COLOR,
        width=float('inf')
    )
    
    # 滚动位置配置
    SCROLL_POSITIONS = {
        "F1": 0,
        "F2": 390,
        "F3": 780,
        "F4": 1170
    }
    
    def scroll_to_position(key: str):
        """滚动到指定位置"""
        if hasattr(page, 'horizontal_listview_ref') and page.horizontal_listview_ref.current:
            if key in SCROLL_POSITIONS:
                page.horizontal_listview_ref.current.content.scroll_to(
                    offset=SCROLL_POSITIONS[key],
                    duration=Config.SCROLL_DURATION,
                    curve=Config.SCROLL_CURVE
                )
                page.update()
    
    # 键盘事件处理函数
    def on_keyboard(e: ft.KeyboardEvent):
        """处理F1-F4快捷键滚动、`键截图和设备键盘事件"""
        print(f"键盘事件: {e.key}, shift: {e.shift}, ctrl: {e.ctrl}, alt: {e.alt}")  # 调试日志
        
        # 优先检查`键截图功能
        if e.key == "`":
            print("检测到`键，开始截图...")  # 调试日志
            print(f"device_views列表长度: {len(device_views)}")
            print(f"device_screenshots列表长度: {len(device_screenshots)}")
            
            # `键触发截图功能
            screenshot_count = 0
            for i, device_view in enumerate(device_views):
                print(f"检查device_view[{i}]: {type(device_view)}")
                print(f"  - 有client属性: {hasattr(device_view, 'client')}")
                if hasattr(device_view, 'client'):
                    print(f"  - client存在: {device_view.client is not None}")
                    if device_view.client:
                        print(f"  - client.alive: {device_view.client.alive}")
                
                if hasattr(device_view, 'client') and device_view.client and device_view.client.alive:
                    print(f"找到活跃设备视图，current_frame存在: {hasattr(device_view, 'current_frame') and device_view.current_frame is not None}")
                    # 获取当前帧数据
                    if hasattr(device_view, 'current_frame') and device_view.current_frame is not None:
                        print(f"当前帧形状: {device_view.current_frame.shape}")
                        # 查找DeviceScreenshot实例并更新截图
                        for j, screenshot_view in enumerate(device_screenshots):
                            print(f"更新screenshot_view[{j}]")
                            screenshot_view.update_screenshot(device_view.current_frame)
                            screenshot_count += 1
                        print(f"截图已更新到 {screenshot_count} 个DeviceScreenshot组件")
                    else:
                        print("没有可用的帧数据进行截图")
                    break
            if screenshot_count == 0:
                print("没有找到DeviceScreenshot组件或活跃设备")
        elif e.key in SCROLL_POSITIONS:
            scroll_to_position(e.key)
        else:
            # 将键盘事件转发给当前活跃的设备视图
            for device_view in device_views:
                if hasattr(device_view, 'client') and device_view.client and device_view.client.alive:
                    # 直接传递键盘事件，不区分按下和释放
                    device_view.keyPressEvent(e)
                    break  # 只处理第一个活跃的设备
    
    page.on_keyboard_event = on_keyboard
    
    # UI组件创建函数
    def create_ui_components():
        """创建基础UI组件"""
        title = ft.Text(
            "欢迎使用 Flet!",
            size=32,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.BLUE_600
        )
        
        description = ft.Text(
            "这是一个基础的 Flet 窗口应用",
            size=16,
            color=ft.Colors.GREY_600
        )
        
        def button_clicked(e):
            page.add(ft.Text("按钮被点击了!", color=ft.Colors.GREEN))
        
        button = ft.ElevatedButton(
            "点击我",
            on_click=button_clicked,
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.BLUE_600
        )
        
        return title, description, button
    
    
    # 创建带抽屉翻页效果的ListView项目
    def create_list_item(index):
        # 定义特定的项目名称和快捷键
        item_names = [
            ("Realtime(F1)", "实时图"),
            ("Screenshot(F2)", "抓取的截图"),
            ("Element(F3)", "页面元素属性"),
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
            # 将DeviceView实例添加到列表中以便清理
            device_views.append(content_area)
        elif index == 1:  # 第二个item使用DeviceScreenshot
            content_area = DeviceScreenshot(bgcolor=ft.Colors.with_opacity(0.9, random_color))
            # 将DeviceScreenshot实例添加到列表中
            device_screenshots.append(content_area)
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
            width=375,  # 减少5个像素，每个item宽度为375px
            expand=True,  # 高度填满整个容器
            bgcolor=ft.Colors.TRANSPARENT,  # 完全透明背景
            content=ft.Column([
                title_bar,
                content_area
            ], spacing=5),  # 5像素间距，减少5px
            margin=ft.margin.all(5)  # 5像素边距
        )
    
    # 创建横向ListView
    def create_horizontal_listview():
        # 创建所有项目
        def get_all_items():
            return [create_list_item(i) for i in range(5)]  # 5个特定项目
        
        # 创建主要的ListView容器，只显示两个项目，其他项目通过滚动显示
        page_container = ft.Container(
            ref=page.horizontal_listview_ref if hasattr(page, 'horizontal_listview_ref') else setattr(page, 'horizontal_listview_ref', ft.Ref()) or page.horizontal_listview_ref,
            content=ft.Row(
                get_all_items(),
                spacing=5,  # 项目间距改为5px
                alignment=ft.MainAxisAlignment.START,
                expand=True,  # 确保 Row 也填满高度
                scroll=ft.ScrollMode.AUTO  # 启用自动滚动
            ),
            expand=True,
            padding=ft.padding.symmetric(horizontal=10, vertical=5),
            width=800  # 固定宽度以限制显示的项目数量
        )
        
        # 返回ListView组件（没有分页指示器）
        return page_container
        
    horizontal_listview = create_horizontal_listview()
    
    # 添加左右两个容器
    left_container = ft.Container(
        bgcolor=Config.LEFT_BG_COLOR,
        width=Config.LEFT_CONTAINER_WIDTH,
        content=ft.Column([horizontal_listview]),
        padding=ft.padding.only(bottom=Config.BOTTOM_PADDING)
    )
    
    # 创建层次结构树数据
    def create_tree_data():
        # 创建更紧凑的树结构数据
        departments = [
            {"name": "Engineering", "icon": ft.Icons.ENGINEERING, "teams": [
                {"name": "Frontend Team", "lead": "Alice Chen", "members": ["Bob Li", "Carol Wang"]},
                {"name": "Backend Team", "lead": "David Zhang", "members": ["Eve Liu", "Frank Wu"]}
            ]},
            {"name": "Marketing", "icon": ft.Icons.CAMPAIGN, "teams": [
                {"name": "Digital Marketing", "lead": "Grace Yang", "members": ["Henry Zhou", "Ivy Xu"]},
                {"name": "Content Team", "lead": "Jack Ma", "members": ["Kate Lin"]}
            ]},
            {"name": "Sales", "icon": ft.Icons.TRENDING_UP, "teams": [
                {"name": "Enterprise Sales", "lead": "Leo Chen", "members": ["Mary Zhao", "Nick Sun"]}
            ]}
        ]
        
        tree_items = []
        for i, dept in enumerate(departments):
            # 创建部门节点 - 紧凑样式
            team_controls = []
            for team in dept["teams"]:
                # 团队负责人
                team_lead = ft.Container(
                    content=ft.Row([
                        ft.Container(width=20),  # 缩进
                        ft.Icon(ft.Icons.KEYBOARD_ARROW_RIGHT, size=12, color=ft.Colors.GREY_600),
                        ft.Icon(ft.Icons.PERSON, size=16, color=ft.Colors.BLUE_600),
                        ft.Text(f"{team['name']} - {team['lead']}", size=13, weight=ft.FontWeight.W_500)
                    ], spacing=5),
                    padding=ft.padding.symmetric(vertical=2, horizontal=5),
                    bgcolor=ft.Colors.BLUE_50,
                    border_radius=4
                )
                team_controls.append(team_lead)
                
                # 团队成员
                for member in team["members"]:
                    member_item = ft.Container(
                        content=ft.Row([
                            ft.Container(width=40),  # 更深缩进
                            ft.Icon(ft.Icons.CIRCLE, size=6, color=ft.Colors.GREY_400),
                            ft.Icon(ft.Icons.PERSON_OUTLINE, size=14, color=ft.Colors.GREY_600),
                            ft.Text(member, size=12, color=ft.Colors.GREY_700)
                        ], spacing=5),
                        padding=ft.padding.symmetric(vertical=1, horizontal=5)
                    )
                    team_controls.append(member_item)
            
            dept_node = ft.ExpansionTile(
                title=ft.Row([
                    ft.Icon(dept["icon"], size=18, color=ft.Colors.INDIGO_600),
                    ft.Text(dept["name"], size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.INDIGO_800)
                ], spacing=8),
                subtitle=ft.Text(f"{len(dept['teams'])} teams", size=11, color=ft.Colors.GREY_500),
                initially_expanded=i == 0,  # 第一个部门默认展开
                controls=team_controls,
                bgcolor=ft.Colors.GREY_50,
                collapsed_bgcolor=ft.Colors.WHITE,
                text_color=ft.Colors.INDIGO_800,
                icon_color=ft.Colors.INDIGO_600,
                tile_padding=ft.padding.symmetric(horizontal=8, vertical=4),
                controls_padding=ft.padding.only(left=10, right=8, bottom=8)
            )
            tree_items.append(dept_node)
        
        return tree_items
    
    # 创建图形节点和连接的简化版本
    def create_graph_canvas():
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
    
    
    # 结束调整大小
    def end_resize(e):
        # 清理resize相关的变量
        if hasattr(page, 'resize_start_x'):
            delattr(page, 'resize_start_x')
        if hasattr(page, 'resize_start_width'):
            delattr(page, 'resize_start_width')
    
    # Create right tab interface
    # Flow functionality variables
    flow_nodes = []
    flow_connections = []
    selected_node = None
    
    # Function to create a flow node
    def create_flow_node(x, y, title="New Node"):
        node_id = len(flow_nodes)
        
        def on_node_click(e):
            nonlocal selected_node
            # Deselect previous node
            if selected_node:
                selected_node.border = ft.border.all(1, ft.Colors.GREY_400)
                selected_node.update()
            
            # Select this node
            e.control.border = ft.border.all(2, ft.Colors.BLUE_600)
            selected_node = e.control
            e.control.update()
        
        def on_delete_click(e):
            # Remove node from flow_nodes list if it exists
            if e.control in flow_nodes:
                flow_nodes.remove(e.control)
            # Remove connections associated with this node
            # This would need more complex logic in a full implementation
            e.control.page.remove(e.control)
        
        node = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(title, size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ft.IconButton(
                        icon=ft.Icons.CLOSE,
                        icon_size=12,
                        on_click=on_delete_click,
                        icon_color=ft.Colors.WHITE
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(
                    content=ft.Text("Task details here...", size=10, color=ft.Colors.WHITE70),
                    padding=ft.padding.all(5)
                )
            ], spacing=2),
            width=120,
            height=80,
            bgcolor=ft.Colors.BLUE_400,
            border=ft.border.all(1, ft.Colors.GREY_400),
            border_radius=8,
            padding=8,
            left=x,
            top=y,
            on_click=on_node_click,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=5,
                color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK)
            )
        )
        
        flow_nodes.append(node)
        return node
    
    # Function to add a flow node
    def add_flow_node(e):
        # Add a new node at a random position (in a real app, this might be at the center or mouse position)
        import random
        x = random.randint(50, 300)
        y = random.randint(50, 200)
        node = create_flow_node(x, y, f"Node {len(flow_nodes) + 1}")
        flow_canvas_ref.current.content.controls.append(node)
        page.update()
    
    # Function to clear flow canvas
    def clear_flow_canvas(e):
        nonlocal selected_node
        flow_nodes.clear()
        flow_connections.clear()
        selected_node = None
        flow_canvas_ref.current.content.controls = [ft.Container(
            content=None,
            width=float('inf'),
            height=float('inf'),
            bgcolor=ft.Colors.GREY_50
        )]
        page.update()
    
    # Function to save flow
    def save_flow(e):
        page.add(ft.Text(f"Flow saved with {len(flow_nodes)} nodes and {len(flow_connections)} connections"))
        page.update()
    
    # Create flow canvas reference
    flow_canvas_ref = ft.Ref()
    
    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(
                text="Graph",
                content=ft.Container(
                    content=ft.Stack([
                        # Main content - graph canvas
                        ft.Container(
                            content=ft.Column([
                                create_graph_canvas()
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
            ),
            ft.Tab(
                text="Code",
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Code Page", size=24, weight=ft.FontWeight.BOLD),
                        ft.Text("Code content would be displayed here", size=16)
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    padding=20
                )
            ),
            ft.Tab(
                text="Chat",
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Chat Interface", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800),
                        ft.Text("Communication and messaging interface", size=14, color=ft.Colors.GREY_600),
                        ft.Container(
                            content=ft.Text("Chat functionality will be implemented here", 
                                          size=16, color=ft.Colors.GREY_500),
                            expand=True,
                            alignment=ft.alignment.center
                        )
                    ]),
                    padding=20,
                    expand=True
                )
            ),
            ft.Tab(
                text="Flow",
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Workflow Flow", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800),
                        ft.Text("Interactive flow diagram for visualizing processes", size=14, color=ft.Colors.GREY_600),
                        ft.Container(
                            content=ft.Row([
                                ft.ElevatedButton(
                                    "Add Node",
                                    icon=ft.Icons.ADD,
                                    on_click=add_flow_node
                                ),
                                ft.ElevatedButton(
                                    "Clear Canvas",
                                    icon=ft.Icons.CLEAR,
                                    on_click=clear_flow_canvas
                                ),
                                ft.ElevatedButton(
                                    "Save Flow",
                                    icon=ft.Icons.SAVE,
                                    on_click=save_flow
                                )
                            ], spacing=10),
                            padding=ft.padding.symmetric(vertical=10)
                        ),
                        # Flow canvas area
                        ft.Container(
                            ref=flow_canvas_ref,
                            content=ft.Stack([
                                # Background grid
                                ft.Container(
                                    content=None,
                                    width=float('inf'),
                                    height=float('inf'),
                                    bgcolor=ft.Colors.GREY_50
                                ),
                                # Initial node will be added here
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
            )
        ],
        expand=True
    )
    
    # Add initial node after tabs are created
    def add_initial_node():
        if flow_canvas_ref.current:
            initial_node = create_flow_node(100, 100, "Start")
            flow_canvas_ref.current.content.controls.append(initial_node)
    
    # Call this after the page is loaded
    page.add_initial_node = add_initial_node
    
    right_container = ft.Container(
        bgcolor=ft.Colors.BLUE_100,  # Light blue background
        expand=True,  # Dynamically fill remaining width
        content=tabs,
        padding=ft.padding.only(bottom=10)  # 底部增加10px间距
    )
    
    # Create main content row
    main_content = ft.Row([
        left_container,
        right_container
    ], 
    expand=True,  # Fill height
    spacing=0)  # Remove spacing
    
    # Add controls to page
    page.add(
        ft.Column([
            header,  # Add header
            main_content  # Main content area
        ], 
        spacing=0,  # Remove default spacing
        expand=True)  # Fill entire page height
    )
    
    # Add initial node to flow canvas
    page.update()
    if flow_canvas_ref.current and len(flow_canvas_ref.current.content.controls) == 1:
        # Only the background container exists, add initial node
        initial_node = create_flow_node(100, 100, "Start")
        flow_canvas_ref.current.content.controls.append(initial_node)
        page.update()

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8550)
    # ft.app(target=main)
