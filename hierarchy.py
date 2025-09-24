

import flet as ft
from typing import Dict, List, Any, Optional


class Hierarchy(ft.Container):
    """页面元素层次结构管理器 - 负责页面元素树的显示和管理"""
    
    def __init__(self, page: ft.Page, **kwargs):
        super().__init__(**kwargs)
        self.page = page
        self.current_elements = []  # 当前页面的元素列表
        self.selected_element = None  # 当前选中的元素
        self.element_tree_ref = ft.Ref()  # 元素树的引用
        self.device_controller = None  # 设备控制器引用
        self.on_element_select_callback = None  # 元素选择回调
        self.create_element_tree_panel()
        
    def set_device_controller(self, device_controller):
        """设置设备控制器"""
        self.device_controller = device_controller
    
    def create_element_tree_panel(self):
        """创建元素树面板（使用DataTable）"""
        self.content = ft.Column(
            controls=[
                # 标题栏
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text("页面元素树", size=16, weight=ft.FontWeight.BOLD),
                            ft.IconButton(
                                icon=ft.Icons.REFRESH,
                                tooltip="刷新元素树",
                                on_click=self.refresh_element_tree
                            )
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    padding=ft.padding.all(10),
                    bgcolor=ft.Colors.BLUE_50,
                    border_radius=5
                ),
                # 元素树DataTable
                ft.Container(
                    content=self.create_element_data_table(),
                    expand=True,
                    border=ft.border.all(1, ft.Colors.GREY_300),
                    border_radius=5
                )
            ],
            spacing=10,
            expand=True
        )
        self.width = 400
        self.expand = True
        self.border_radius = 10
        self.shadow = ft.BoxShadow(
            spread_radius=1,
            blur_radius=15,
            color=ft.Colors.with_opacity(0.3, ft.Colors.GREY_400),
            offset=ft.Offset(0, 4)
        )

    def create_element_data_table(self) -> ft.DataTable:
        """创建元素树DataTable"""
        return ft.DataTable(
            ref=self.element_tree_ref,
            columns=[
                ft.DataColumn(ft.Text("图标", size=12, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("类型", size=12, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("文本", size=12, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("ID", size=12, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("位置", size=12, weight=ft.FontWeight.BOLD)),
            ],
            rows=self.create_element_data_rows(),
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=5,
            show_checkbox_column=False,
            column_spacing=10,
            data_row_min_height=40,
            data_row_max_height=60,
            heading_row_height=35,
            horizontal_margin=10,
            show_bottom_border=True
        )

    def create_element_data_rows(self) -> list:
        """创建元素数据行"""
        rows = []
        if not self.current_elements:
            return rows
        
        for element in self.current_elements:
            # 获取元素信息
            element_type = element.get('class', '未知')
            text = element.get('text', '')
            resource_id = element.get('resource-id', '')
            bounds = element.get('bounds', '')
            
            # 创建数据行
            row = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Icon(self.get_element_icon(element_type), size=16)),
                    ft.DataCell(ft.Text(element_type, size=11, max_lines=1)),
                    ft.DataCell(ft.Text(text[:20] + "..." if len(text) > 20 else text, size=11, max_lines=1)),
                    ft.DataCell(ft.Text(resource_id.split('/')[-1] if resource_id else '', size=11, max_lines=1)),
                    ft.DataCell(ft.Text(bounds, size=10, max_lines=1)),
                ],
                on_select_changed=lambda e, elem=element: self.on_element_selected(elem)
            )
            rows.append(row)
        
        return rows

    def get_element_icon(self, element_type: str) -> str:
        """根据元素类型获取对应的图标"""
        # 99个常用元素图标映射
        icon_map = {
            # 基础UI组件
            'View': ft.Icons.CROP_SQUARE,
            'ViewGroup': ft.Icons.DASHBOARD,
            'LinearLayout': ft.Icons.VIEW_AGENDA,
            'RelativeLayout': ft.Icons.GRID_VIEW,
            'FrameLayout': ft.Icons.LAYERS,
            'ConstraintLayout': ft.Icons.GRID_ON,
            'ScrollView': ft.Icons.SCROLL,
            'HorizontalScrollView': ft.Icons.SWAP_HORIZ,
            'RecyclerView': ft.Icons.LIST,
            'ListView': ft.Icons.FORMAT_LIST_BULLETED,
            'GridView': ft.Icons.GRID_VIEW,
            
            # 文本相关
            'TextView': ft.Icons.TEXT_FIELDS,
            'EditText': ft.Icons.EDIT,
            'AutoCompleteTextView': ft.Icons.SEARCH,
            'MultiAutoCompleteTextView': ft.Icons.SEARCH,
            
            # 按钮相关
            'Button': ft.Icons.SMART_BUTTON,
            'ImageButton': ft.Icons.IMAGE,
            'ToggleButton': ft.Icons.TOGGLE_ON,
            'Switch': ft.Icons.TOGGLE_OFF,
            'CheckBox': ft.Icons.CHECK_BOX,
            'RadioButton': ft.Icons.RADIO_BUTTON_CHECKED,
            'CompoundButton': ft.Icons.RADIO_BUTTON_UNCHECKED,
            
            # 图像相关
            'ImageView': ft.Icons.IMAGE,
            'VideoView': ft.Icons.VIDEOCAM,
            'WebView': ft.Icons.WEB,
            
            # 进度相关
            'ProgressBar': ft.Icons.PROGRESS_ACTIVITY,
            'SeekBar': ft.Icons.TUNE,
            'RatingBar': ft.Icons.STAR_RATE,
            
            # 选择器相关
            'Spinner': ft.Icons.ARROW_DROP_DOWN,
            'DatePicker': ft.Icons.DATE_RANGE,
            'TimePicker': ft.Icons.ACCESS_TIME,
            'NumberPicker': ft.Icons.LOOKS_ONE,
            
            # 导航相关
            'TabHost': ft.Icons.TAB,
            'TabWidget': ft.Icons.TAB_UNSELECTED,
            'ViewPager': ft.Icons.SWIPE,
            'NavigationView': ft.Icons.MENU,
            'BottomNavigationView': ft.Icons.NAVIGATION,
            'Toolbar': ft.Icons.BUILD,
            'ActionBar': ft.Icons.MENU,
            
            # 容器相关
            'CardView': ft.Icons.CREDIT_CARD,
            'AppBarLayout': ft.Icons.VERTICAL_ALIGN_TOP,
            'CollapsingToolbarLayout': ft.Icons.EXPAND_LESS,
            'CoordinatorLayout': ft.Icons.COORDINATE,
            'DrawerLayout': ft.Icons.MENU_OPEN,
            'SlidingPaneLayout': ft.Icons.VIEW_SIDEBAR,
            
            # 输入相关
            'TextInputLayout': ft.Icons.INPUT,
            'TextInputEditText': ft.Icons.EDIT,
            'Chip': ft.Icons.LABEL,
            'ChipGroup': ft.Icons.LABEL_OUTLINE,
            
            # 对话框相关
            'AlertDialog': ft.Icons.WARNING,
            'Dialog': ft.Icons.CHAT_BUBBLE,
            'PopupWindow': ft.Icons.OPEN_IN_NEW,
            'Toast': ft.Icons.NOTIFICATIONS,
            'Snackbar': ft.Icons.INFO,
            
            # 菜单相关
            'Menu': ft.Icons.MORE_VERT,
            'MenuItem': ft.Icons.MORE_HORIZ,
            'ContextMenu': ft.Icons.MORE_VERT,
            'PopupMenu': ft.Icons.MORE_HORIZ,
            
            # 布局相关
            'TableLayout': ft.Icons.TABLE_CHART,
            'TableRow': ft.Icons.TABLE_ROWS,
            'GridLayout': ft.Icons.GRID_4X4,
            'FlexboxLayout': ft.Icons.VIEW_COLUMN,
            
            # 特殊组件
            'Fragment': ft.Icons.EXTENSION,
            'Activity': ft.Icons.ANDROID,
            'Service': ft.Icons.SETTINGS,
            'BroadcastReceiver': ft.Icons.WIFI,
            'ContentProvider': ft.Icons.STORAGE,
            
            # 媒体相关
            'MediaPlayer': ft.Icons.PLAY_CIRCLE,
            'AudioManager': ft.Icons.VOLUME_UP,
            'Camera': ft.Icons.CAMERA_ALT,
            'SurfaceView': ft.Icons.VIDEOCAM,
            'TextureView': ft.Icons.TEXTURE,
            
            # 传感器相关
            'SensorManager': ft.Icons.SENSORS,
            'LocationManager': ft.Icons.LOCATION_ON,
            'BluetoothAdapter': ft.Icons.BLUETOOTH,
            'WifiManager': ft.Icons.WIFI,
            'TelephonyManager': ft.Icons.PHONE,
            
            # 系统相关
            'NotificationManager': ft.Icons.NOTIFICATIONS,
            'AlarmManager': ft.Icons.ALARM,
            'PowerManager': ft.Icons.POWER,
            'WindowManager': ft.Icons.WINDOW,
            'ActivityManager': ft.Icons.APPS,
            
            # 数据相关
            'SharedPreferences': ft.Icons.SETTINGS,
            'SQLiteDatabase': ft.Icons.STORAGE,
            'ContentResolver': ft.Icons.SYNC,
            'FileProvider': ft.Icons.FOLDER,
            'AssetManager': ft.Icons.ARCHIVE,
            
            # 网络相关
            'HttpURLConnection': ft.Icons.HTTP,
            'NetworkInfo': ft.Icons.NETWORK_CHECK,
            'ConnectivityManager': ft.Icons.SIGNAL_WIFI_4_BAR,
            'DownloadManager': ft.Icons.DOWNLOAD,
            'UploadService': ft.Icons.UPLOAD,
            
            # 动画相关
            'Animation': ft.Icons.ANIMATION,
            'Animator': ft.Icons.PLAY_ARROW,
            'ValueAnimator': ft.Icons.TIMELINE,
            'ObjectAnimator': ft.Icons.TRANSFORM,
            'AnimationSet': ft.Icons.PLAYLIST_PLAY,
            
            # 手势相关
            'GestureDetector': ft.Icons.TOUCH_APP,
            'ScaleGestureDetector': ft.Icons.ZOOM_IN,
            'VelocityTracker': ft.Icons.SPEED,
            'DragEvent': ft.Icons.DRAG_INDICATOR,
            'MotionEvent': ft.Icons.TOUCH_APP
        }
        
        # 返回对应图标，如果找不到则返回默认图标
        return icon_map.get(element_type, ft.Icons.WIDGETS)

    def refresh_element_tree(self, e=None):
        """刷新元素树"""
        try:
            # 获取当前页面元素
            if self.device_controller:
                self.current_elements = self.device_controller.get_page_elements()
            
            # 更新DataTable数据
            if self.element_tree_ref.current:
                self.element_tree_ref.current.rows = self.create_element_data_rows()
                self.element_tree_ref.current.update()
            
            # 清空选中的元素
            self.selected_element = None
                
        except Exception as ex:
            print(f"刷新元素树失败: {ex}")

    def on_element_selected(self, element: Dict[str, Any]):
        """元素被选中时的回调"""
        self.selected_element = element
        # 触发选择事件，供外部监听
        if hasattr(self, 'on_element_select_callback') and self.on_element_select_callback:
            self.on_element_select_callback(element)

    def set_element_select_callback(self, callback):
        """设置元素选择回调函数"""
        self.on_element_select_callback = callback

    def update_elements(self, elements: List[Dict[str, Any]]):
        """更新元素列表（供外部调用）"""
        self.current_elements = elements
        self.selected_element = None
        # 更新DataTable
        if self.element_tree_ref.current:
            self.element_tree_ref.current.rows = self.create_element_data_rows()
            self.element_tree_ref.current.update()

    def get_selected_element(self) -> Optional[Dict[str, Any]]:
        """获取当前选中的元素"""
        return self.selected_element

    def select_element_by_id(self, element_id: str) -> bool:
        """根据元素ID选择元素"""
        for element in self.current_elements:
            if element.get('resource-id') == element_id or element.get('id') == element_id:
                self.on_element_selected(element)
                return True
        return False

    def get_mock_elements(self) -> List[Dict[str, Any]]:
        """获取模拟元素数据（用于测试）"""
        return [
            {
                'class': 'LinearLayout',
                'resource-id': 'main_container',
                'text': '',
                'bounds': '[0,0][1080,1920]',
                'clickable': 'false',
                'enabled': 'true',
                'focusable': 'false',
                'package': 'com.example.app'
            },
            {
                'class': 'TextView',
                'resource-id': 'app_title',
                'text': '应用标题',
                'bounds': '[0,0][1080,120]',
                'clickable': 'false',
                'enabled': 'true',
                'focusable': 'false',
                'package': 'com.example.app'
            },
            {
                'class': 'Button',
                'resource-id': 'login_button',
                'text': '登录',
                'bounds': '[100,200][300,260]',
                'clickable': 'true',
                'enabled': 'true',
                'focusable': 'true',
                'package': 'com.example.app'
            },
            {
                'class': 'EditText',
                'resource-id': 'username_input',
                'text': '',
                'content-desc': '请输入用户名',
                'bounds': '[50,300][350,350]',
                'clickable': 'true',
                'enabled': 'true',
                'focusable': 'true',
                'package': 'com.example.app'
            },
            {
                'class': 'RecyclerView',
                'resource-id': 'content_list',
                'text': '',
                'bounds': '[0,400][1080,1400]',
                'clickable': 'false',
                'enabled': 'true',
                'focusable': 'false',
                'scrollable': 'true',
                'package': 'com.example.app'
            }
        ]