"""
UI自动化模块

该模块提供Android设备UI自动化相关功能，包括：
- 界面层次结构获取和管理
- UI元素可视化
- 元素选择和高亮
"""

from .hierarchy_manager import HierarchyManager
from .ui_visualizer import UIVisualizer
from .element_selector import ElementSelector

__all__ = [
    'HierarchyManager',
    'UIVisualizer', 
    'ElementSelector'
]

__version__ = '1.0.0'