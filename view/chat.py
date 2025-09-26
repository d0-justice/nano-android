import flet as ft
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.signal_manager import SignalMixin
import datetime


class Chat(SignalMixin):
    """聊天管理类，负责处理聊天界面相关的UI和逻辑"""
    
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.messages = []
        self.chat_list_ref = ft.Ref[ft.ListView]()
        self.message_input_ref = ft.Ref[ft.TextField]()
    
    def add_message(self, message: str, is_user: bool = True):
        """添加消息到聊天列表"""
        if not self.chat_list_ref.current:
            print("⚠️ 聊天列表组件尚未初始化")
            return
            
        # 检查组件是否已添加到页面
        if not hasattr(self.chat_list_ref.current, 'page') or not self.chat_list_ref.current.page:
            print("⚠️ 聊天列表组件尚未添加到页面")
            return
            
        # 创建消息容器
        message_container = ft.Container(
            content=ft.Text(
                message,
                size=14,
                color=ft.colors.WHITE if is_user else ft.colors.BLACK87
            ),
            bgcolor=ft.colors.BLUE_600 if is_user else ft.colors.GREY_200,
            padding=10,
            margin=ft.margin.only(bottom=5),
            border_radius=10,
            alignment=ft.alignment.center_right if is_user else ft.alignment.center_left
        )
        
        # 添加到聊天列表
        self.chat_list_ref.current.controls.append(message_container)
        
        # 限制消息数量
        if len(self.chat_list_ref.current.controls) > 100:
            self.chat_list_ref.current.controls.pop(0)
        
        # 更新UI
        try:
            self.chat_list_ref.current.update()
        except Exception as e:
            print(f"更新聊天列表失败: {e}")
    
    def send_message(self, e):
        """发送消息"""
        if self.message_input_ref.current and self.message_input_ref.current.value.strip():
            message = self.message_input_ref.current.value.strip()
            
            # 添加用户消息
            self.add_message(message, is_user=True)
            
            # 清空输入框
            self.message_input_ref.current.value = ""
            self.message_input_ref.current.update()
            
            # 模拟AI回复（这里可以集成真实的AI服务）
            self.simulate_ai_response(message)
    
    def simulate_ai_response(self, user_message: str):
        """模拟AI回复"""
        import time
        import threading
        
        def delayed_response():
            time.sleep(1)  # 模拟思考时间
            
            # 简单的回复逻辑
            responses = [
                f"我收到了您的消息：'{user_message}'",
                "这是一个很有趣的问题！",
                "让我为您分析一下这个问题...",
                "根据您的描述，我建议...",
                "感谢您的提问，这里是我的回答..."
            ]
            
            import random
            response = random.choice(responses)
            
            # 在主线程中添加回复
            self.page.run_thread(lambda: self.add_message(response, is_user=False))
        
        # 在后台线程中处理回复
        threading.Thread(target=delayed_response, daemon=True).start()
    
    def clear_chat(self, e):
        """清空聊天记录"""
        self.messages.clear()
        if self.chat_list_ref.current:
            self.chat_list_ref.current.controls.clear()
            self.chat_list_ref.current.update()
    
    def on_message_input_submit(self, e):
        """处理输入框回车事件"""
        self.send_message(e)

    def create_chat_tab_content(self):
        """创建聊天标签页内容"""
        # 创建聊天消息列表
        chat_list = ft.ListView(
            ref=self.chat_list_ref,
            expand=True,
            spacing=5,
            padding=ft.padding.all(10),
            auto_scroll=True
        )
        
        # 创建消息输入框
        message_input = ft.TextField(
            ref=self.message_input_ref,
            hint_text="输入消息...",
            expand=True,
            multiline=True,
            min_lines=1,
            max_lines=3,
            on_submit=self.on_message_input_submit,
            border_radius=20,
            content_padding=ft.padding.symmetric(horizontal=15, vertical=10)
        )
        
        # 创建发送按钮
        send_button = ft.IconButton(
            icon=ft.Icons.SEND,
            tooltip="发送消息",
            on_click=self.send_message,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.BLUE_600,
                shape=ft.CircleBorder()
            )
        )
        
        # 创建清空按钮
        clear_button = ft.IconButton(
            icon=ft.Icons.CLEAR_ALL,
            tooltip="清空聊天",
            on_click=self.clear_chat,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.RED_600,
                shape=ft.CircleBorder()
            )
        )
        
        # 创建输入区域
        input_area = ft.Container(
            content=ft.Row([
                message_input,
                send_button,
                clear_button
            ], spacing=10),
            padding=ft.padding.all(10),
            bgcolor=ft.Colors.GREY_50,
            border=ft.border.only(top=ft.BorderSide(1, ft.Colors.GREY_300))
        )
        
        # 延迟添加欢迎消息，确保组件已添加到页面
        def add_welcome_message():
            self.add_message("欢迎使用聊天功能！您可以在这里与AI助手进行对话。", is_user=False)
        
        # 使用页面的after_update回调来延迟执行
        if hasattr(self.page, 'after_update'):
            self.page.after_update = add_welcome_message
        
        return ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.CHAT, size=24, color=ft.Colors.BLUE_800),
                        ft.Text("Chat Interface", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800)
                    ], spacing=10),
                    padding=ft.padding.all(20)
                ),
                ft.Container(
                    content=chat_list,
                    expand=True,
                    border=ft.border.all(1, ft.Colors.GREY_300),
                    border_radius=8,
                    margin=ft.margin.symmetric(horizontal=20)
                ),
                input_area
            ]),
            expand=True
        )