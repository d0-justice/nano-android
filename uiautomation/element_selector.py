"""
UI元素选择器

负责UI元素的选择、查找和操作
"""

from typing import Dict, List, Any, Optional, Callable
import re


class ElementSelector:
    """UI元素选择器"""
    
    def __init__(self):
        self.elements = []
        self.selection_callbacks = []
    
    def set_elements(self, elements: List[Dict[str, Any]]):
        """设置元素列表"""
        self.elements = elements
    
    def add_selection_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """添加元素选择回调"""
        if callback not in self.selection_callbacks:
            self.selection_callbacks.append(callback)
    
    def remove_selection_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """移除元素选择回调"""
        if callback in self.selection_callbacks:
            self.selection_callbacks.remove(callback)
    
    def select_element(self, element: Dict[str, Any]):
        """选择元素并触发回调"""
        for callback in self.selection_callbacks:
            try:
                callback(element)
            except Exception as e:
                print(f"元素选择回调执行失败: {e}")
    
    def find_by_text(self, text: str, exact_match: bool = True) -> List[Dict[str, Any]]:
        """根据文本查找元素"""
        results = []
        for element in self.elements:
            element_text = element.get('text', '')
            if exact_match:
                if element_text == text:
                    results.append(element)
            else:
                if text.lower() in element_text.lower():
                    results.append(element)
        return results
    
    def find_by_resource_id(self, resource_id: str) -> List[Dict[str, Any]]:
        """根据resource-id查找元素"""
        results = []
        for element in self.elements:
            if element.get('resource-id') == resource_id:
                results.append(element)
        return results
    
    def find_by_class(self, class_name: str) -> List[Dict[str, Any]]:
        """根据类名查找元素"""
        results = []
        for element in self.elements:
            if element.get('class') == class_name:
                results.append(element)
        return results
    
    def find_by_content_desc(self, content_desc: str, exact_match: bool = True) -> List[Dict[str, Any]]:
        """根据content-desc查找元素"""
        results = []
        for element in self.elements:
            element_desc = element.get('content-desc', '')
            if exact_match:
                if element_desc == content_desc:
                    results.append(element)
            else:
                if content_desc.lower() in element_desc.lower():
                    results.append(element)
        return results
    
    def find_by_package(self, package_name: str) -> List[Dict[str, Any]]:
        """根据包名查找元素"""
        results = []
        for element in self.elements:
            if element.get('package') == package_name:
                results.append(element)
        return results
    
    def find_clickable_elements(self) -> List[Dict[str, Any]]:
        """查找所有可点击的元素"""
        return [element for element in self.elements if element.get('clickable') == 'true']
    
    def find_scrollable_elements(self) -> List[Dict[str, Any]]:
        """查找所有可滚动的元素"""
        return [element for element in self.elements if element.get('scrollable') == 'true']
    
    def find_checkable_elements(self) -> List[Dict[str, Any]]:
        """查找所有可选择的元素"""
        return [element for element in self.elements if element.get('checkable') == 'true']
    
    def find_enabled_elements(self) -> List[Dict[str, Any]]:
        """查找所有启用的元素"""
        return [element for element in self.elements if element.get('enabled') == 'true']
    
    def find_by_bounds(self, x: int, y: int) -> List[Dict[str, Any]]:
        """根据坐标查找元素"""
        results = []
        for element in self.elements:
            bounds_str = element.get('bounds', '')
            if self._point_in_bounds(x, y, bounds_str):
                results.append(element)
        return results
    
    def _point_in_bounds(self, x: int, y: int, bounds_str: str) -> bool:
        """检查点是否在边界内"""
        try:
            # 解析格式如 "[0,0][1080,120]"
            matches = re.findall(r'\[(\d+),(\d+)\]', bounds_str)
            if len(matches) == 2:
                x1, y1 = int(matches[0][0]), int(matches[0][1])
                x2, y2 = int(matches[1][0]), int(matches[1][1])
                return x1 <= x <= x2 and y1 <= y <= y2
        except Exception:
            pass
        return False
    
    def find_by_regex(self, pattern: str, field: str = 'text') -> List[Dict[str, Any]]:
        """使用正则表达式查找元素"""
        results = []
        try:
            regex = re.compile(pattern, re.IGNORECASE)
            for element in self.elements:
                field_value = element.get(field, '')
                if regex.search(field_value):
                    results.append(element)
        except re.error as e:
            print(f"正则表达式错误: {e}")
        return results
    
    def find_by_multiple_criteria(self, **criteria) -> List[Dict[str, Any]]:
        """根据多个条件查找元素"""
        results = []
        for element in self.elements:
            match = True
            for key, value in criteria.items():
                if key not in element or element[key] != value:
                    match = False
                    break
            if match:
                results.append(element)
        return results
    
    def get_element_at_position(self, x: int, y: int) -> Optional[Dict[str, Any]]:
        """获取指定位置的最上层元素"""
        candidates = self.find_by_bounds(x, y)
        if not candidates:
            return None
        
        # 返回面积最小的元素（通常是最上层的）
        smallest_element = None
        smallest_area = float('inf')
        
        for element in candidates:
            bounds_str = element.get('bounds', '')
            area = self._calculate_bounds_area(bounds_str)
            if area < smallest_area:
                smallest_area = area
                smallest_element = element
        
        return smallest_element
    
    def _calculate_bounds_area(self, bounds_str: str) -> float:
        """计算边界面积"""
        try:
            matches = re.findall(r'\[(\d+),(\d+)\]', bounds_str)
            if len(matches) == 2:
                x1, y1 = int(matches[0][0]), int(matches[0][1])
                x2, y2 = int(matches[1][0]), int(matches[1][1])
                return (x2 - x1) * (y2 - y1)
        except Exception:
            pass
        return float('inf')
    
    def filter_by_visibility(self, elements: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """过滤出可见的元素"""
        target_elements = elements or self.elements
        visible_elements = []
        
        for element in target_elements:
            bounds_str = element.get('bounds', '')
            if self._is_element_visible(bounds_str):
                visible_elements.append(element)
        
        return visible_elements
    
    def _is_element_visible(self, bounds_str: str) -> bool:
        """检查元素是否可见（有有效的边界）"""
        try:
            matches = re.findall(r'\[(\d+),(\d+)\]', bounds_str)
            if len(matches) == 2:
                x1, y1 = int(matches[0][0]), int(matches[0][1])
                x2, y2 = int(matches[1][0]), int(matches[1][1])
                # 检查是否有有效的宽度和高度
                return x2 > x1 and y2 > y1
        except Exception:
            pass
        return False
    
    def get_element_hierarchy_path(self, target_element: Dict[str, Any]) -> List[str]:
        """获取元素的层次路径（简化版）"""
        # 这是一个简化的实现，实际的层次路径需要XML解析
        path = []
        if target_element.get('package'):
            path.append(f"package:{target_element['package']}")
        if target_element.get('class'):
            path.append(f"class:{target_element['class']}")
        if target_element.get('resource-id'):
            path.append(f"id:{target_element['resource-id']}")
        return path
    
    def create_element_selector_string(self, element: Dict[str, Any]) -> str:
        """创建元素选择器字符串"""
        selectors = []
        
        if element.get('resource-id'):
            selectors.append(f"resource-id='{element['resource-id']}'")
        elif element.get('text'):
            selectors.append(f"text='{element['text']}'")
        elif element.get('content-desc'):
            selectors.append(f"content-desc='{element['content-desc']}'")
        else:
            selectors.append(f"class='{element.get('class', 'Unknown')}'")
        
        return " AND ".join(selectors)