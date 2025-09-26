import flet as ft
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.signal_manager import SignalMixin
import json


class Code(SignalMixin):
    """代码编辑管理类，负责处理代码编辑界面相关的UI和逻辑"""
    
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.code_editor_ref = ft.Ref[ft.TextField]()
        self.file_list_ref = ft.Ref[ft.ListView]()
        self.current_file = None
        self.file_contents = {}
        self.supported_extensions = ['.py', '.js', '.html', '.css', '.json', '.txt', '.md']
    
    def load_file_list(self):
        """加载文件列表"""
        # 确保file_list_ref已经被添加到页面
        if self.file_list_ref.current is None:
            print("⚠️ 文件列表组件尚未初始化")
            return
            
        self.file_list_ref.current.controls.clear()
        
        # 获取当前目录下的文件
        try:
            current_dir = os.getcwd()
            files = []
            
            for item in os.listdir(current_dir):
                if os.path.isfile(item):
                    _, ext = os.path.splitext(item)
                    if ext.lower() in self.supported_extensions:
                        files.append(item)
            
            files.sort()
            
            for file_name in files:
                file_item = ft.ListTile(
                    leading=ft.Icon(self.get_file_icon(file_name)),
                    title=ft.Text(file_name, size=14),
                    subtitle=ft.Text(f"Size: {self.get_file_size(file_name)}", size=12),
                    on_click=lambda e, f=file_name: self.open_file(f),
                    hover_color=ft.Colors.BLUE_50
                )
                self.file_list_ref.current.controls.append(file_item)
            
            # 只有在组件已添加到页面时才更新
            if hasattr(self.file_list_ref.current, 'page') and self.file_list_ref.current.page:
                self.file_list_ref.current.update()
            
        except Exception as e:
            self.show_error(f"加载文件列表失败: {str(e)}")
    
    def get_file_icon(self, file_name: str):
        """根据文件扩展名获取图标"""
        _, ext = os.path.splitext(file_name)
        ext = ext.lower()
        
        icon_map = {
            '.py': ft.Icons.CODE,
            '.js': ft.Icons.JAVASCRIPT,
            '.html': ft.Icons.WEB,
            '.css': ft.Icons.STYLE,
            '.json': ft.Icons.DATA_OBJECT,
            '.txt': ft.Icons.TEXT_SNIPPET,
            '.md': ft.Icons.DESCRIPTION
        }
        
        return icon_map.get(ext, ft.Icons.INSERT_DRIVE_FILE)
    
    def get_file_size(self, file_name: str):
        """获取文件大小"""
        try:
            size = os.path.getsize(file_name)
            if size < 1024:
                return f"{size} B"
            elif size < 1024 * 1024:
                return f"{size / 1024:.1f} KB"
            else:
                return f"{size / (1024 * 1024):.1f} MB"
        except:
            return "Unknown"
    
    def open_file(self, file_name: str):
        """打开文件"""
        try:
            with open(file_name, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.current_file = file_name
            self.file_contents[file_name] = content
            
            if self.code_editor_ref.current:
                self.code_editor_ref.current.value = content
                self.code_editor_ref.current.update()
            
            self.show_info(f"已打开文件: {file_name}")
            
        except Exception as e:
            self.show_error(f"打开文件失败: {str(e)}")
    
    def save_file(self, e):
        """保存文件"""
        if not self.current_file or not self.code_editor_ref.current:
            self.show_error("没有打开的文件")
            return
        
        try:
            content = self.code_editor_ref.current.value or ""
            
            with open(self.current_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.file_contents[self.current_file] = content
            self.show_info(f"文件已保存: {self.current_file}")
            
        except Exception as e:
            self.show_error(f"保存文件失败: {str(e)}")
    
    def new_file(self, e):
        """新建文件"""
        def create_file(file_name: str):
            if not file_name:
                return
            
            try:
                # 创建空文件
                with open(file_name, 'w', encoding='utf-8') as f:
                    f.write("")
                
                self.current_file = file_name
                self.file_contents[file_name] = ""
                
                if self.code_editor_ref.current:
                    self.code_editor_ref.current.value = ""
                    self.code_editor_ref.current.update()
                
                self.load_file_list()
                self.show_info(f"已创建文件: {file_name}")
                
            except Exception as e:
                self.show_error(f"创建文件失败: {str(e)}")
        
        # 显示输入对话框
        self.show_input_dialog("新建文件", "请输入文件名:", create_file)
    
    def refresh_files(self, e):
        """刷新文件列表"""
        self.load_file_list()
        self.show_info("文件列表已刷新")
    
    def format_code(self, e):
        """格式化代码（简单的缩进处理）"""
        if not self.code_editor_ref.current:
            return
        
        content = self.code_editor_ref.current.value or ""
        
        # 简单的Python代码格式化
        if self.current_file and self.current_file.endswith('.py'):
            lines = content.split('\n')
            formatted_lines = []
            indent_level = 0
            
            for line in lines:
                stripped = line.strip()
                if not stripped:
                    formatted_lines.append("")
                    continue
                
                # 减少缩进
                if stripped.startswith(('except', 'elif', 'else', 'finally')) or stripped in ['break', 'continue', 'pass', 'return']:
                    if indent_level > 0:
                        indent_level -= 1
                
                formatted_lines.append("    " * indent_level + stripped)
                
                # 增加缩进
                if stripped.endswith(':'):
                    indent_level += 1
            
            formatted_content = '\n'.join(formatted_lines)
            self.code_editor_ref.current.value = formatted_content
            self.code_editor_ref.current.update()
            self.show_info("代码已格式化")
        else:
            self.show_info("当前文件类型不支持格式化")
    
    def show_info(self, message: str):
        """显示信息消息"""
        print(f"ℹ️ 信息: {message}")
        # 使用 SnackBar 而不是 show_snack_bar
        snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.colors.BLUE_400
        )
        self.page.overlay.append(snack_bar)
        snack_bar.open = True
        self.page.update()
    
    def show_error(self, message: str):
        """显示错误消息"""
        print(f"❌ 错误: {message}")
        # 使用 SnackBar 而不是 show_snack_bar
        snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.colors.RED_400
        )
        self.page.overlay.append(snack_bar)
        snack_bar.open = True
        self.page.update()
    
    def show_input_dialog(self, title: str, hint: str, callback):
        """显示输入对话框"""
        input_field = ft.TextField(hint_text=hint, expand=True)
        
        def on_submit(e):
            callback(input_field.value)
            self.page.close(dialog)
        
        def on_cancel(e):
            self.page.close(dialog)
        
        dialog = ft.AlertDialog(
            title=ft.Text(title),
            content=input_field,
            actions=[
                ft.TextButton("取消", on_click=on_cancel),
                ft.TextButton("确定", on_click=on_submit)
            ]
        )
        
        self.page.open(dialog)

    def create_code_tab_content(self):
        """创建代码编辑标签页内容"""
        # 创建文件列表
        file_list = ft.ListView(
            ref=self.file_list_ref,
            expand=True,
            spacing=2,
            padding=ft.padding.all(5)
        )
        
        # 创建代码编辑器
        code_editor = ft.TextField(
            ref=self.code_editor_ref,
            multiline=True,
            expand=True,
            hint_text="在这里编辑代码...",
            text_style=ft.TextStyle(font_family="Consolas, Monaco, monospace"),
            border=ft.InputBorder.OUTLINE,
            content_padding=ft.padding.all(10)
        )
        
        # 创建工具栏
        toolbar = ft.Row([
            ft.IconButton(
                icon=ft.Icons.ADD,
                tooltip="新建文件",
                on_click=self.new_file
            ),
            ft.IconButton(
                icon=ft.Icons.SAVE,
                tooltip="保存文件",
                on_click=self.save_file
            ),
            ft.IconButton(
                icon=ft.Icons.REFRESH,
                tooltip="刷新文件列表",
                on_click=self.refresh_files
            ),
            ft.IconButton(
                icon=ft.Icons.FORMAT_ALIGN_LEFT,
                tooltip="格式化代码",
                on_click=self.format_code
            )
        ], spacing=5)
        
        # 创建文件浏览器面板
        file_panel = ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Text("文件浏览器", size=16, weight=ft.FontWeight.BOLD),
                    padding=ft.padding.all(10),
                    bgcolor=ft.Colors.GREY_100
                ),
                ft.Container(
                    content=file_list,
                    expand=True
                )
            ]),
            width=250,
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=8
        )
        
        # 创建编辑器面板
        editor_panel = ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Row([
                        ft.Text("代码编辑器", size=16, weight=ft.FontWeight.BOLD),
                        ft.Container(expand=True),
                        toolbar
                    ]),
                    padding=ft.padding.all(10),
                    bgcolor=ft.Colors.GREY_100
                ),
                ft.Container(
                    content=code_editor,
                    expand=True,
                    padding=ft.padding.all(5)
                )
            ]),
            expand=True,
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=8
        )
        
        # 加载文件列表
        self.load_file_list()
        
        return ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.CODE, size=24, color=ft.Colors.PURPLE_800),
                        ft.Text("Code Editor", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.PURPLE_800)
                    ], spacing=10),
                    padding=ft.padding.all(20)
                ),
                ft.Container(
                    content=ft.Row([
                        file_panel,
                        ft.Container(width=10),  # 间距
                        editor_panel
                    ], expand=True),
                    expand=True,
                    padding=ft.padding.symmetric(horizontal=20, vertical=10)
                )
            ]),
            expand=True
        )