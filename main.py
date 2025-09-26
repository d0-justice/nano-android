import flet as ft

from view.main_window import MainWindow

def main(page: ft.Page):
    main_frame = MainWindow(page)

if __name__ == "__main__":
    ft.app(target=main)
