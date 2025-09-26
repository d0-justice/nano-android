"""
UI层次结构管理器

负责获取和解析Android设备的UI层次结构数据
"""

import subprocess
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional
import json


class HierarchyManager:
    """UI层次结构管理器"""
    
    def __init__(self, device_id: str = None):
        self.device_id = device_id
        self.current_hierarchy = None
        self.elements = []
    
    def get_hierarchy_data(self) -> Optional[str]:
        """获取设备的UI层次结构数据"""
        try:
            if not self.device_id:
                print("设备ID未设置，无法获取层次结构")
                return None
            
            # 使用adb命令获取UI层次结构
            cmd = f"adb -s {self.device_id} exec-out uiautomator dump /dev/tty"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and result.stdout:
                self.current_hierarchy = result.stdout
                self._parse_hierarchy(result.stdout)
                return result.stdout
            else:
                print(f"获取层次结构失败: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            print("获取层次结构超时")
            return None
        except Exception as e:
            print(f"获取层次结构异常: {e}")
            return None
    
    def _parse_hierarchy(self, xml_data: str):
        """解析XML层次结构数据"""
        try:
            # 清空之前的元素列表
            self.elements = []
            
            # 解析XML
            root = ET.fromstring(xml_data)
            
            # 递归解析所有节点
            self._parse_node(root)
            
            print(f"解析完成，共找到 {len(self.elements)} 个UI元素")
            
        except ET.ParseError as e:
            print(f"XML解析错误: {e}")
        except Exception as e:
            print(f"解析层次结构异常: {e}")
    
    def _parse_node(self, node: ET.Element):
        """递归解析XML节点"""
        # 提取节点属性
        element = {
            'class': node.get('class', ''),
            'resource-id': node.get('resource-id', ''),
            'text': node.get('text', ''),
            'content-desc': node.get('content-desc', ''),
            'bounds': node.get('bounds', ''),
            'clickable': node.get('clickable', 'false'),
            'enabled': node.get('enabled', 'true'),
            'focusable': node.get('focusable', 'false'),
            'scrollable': node.get('scrollable', 'false'),
            'checkable': node.get('checkable', 'false'),
            'checked': node.get('checked', 'false'),
            'selected': node.get('selected', 'false'),
            'package': node.get('package', ''),
            'index': node.get('index', '0')
        }
        
        # 只添加有意义的元素（有类名的）
        if element['class']:
            self.elements.append(element)
        
        # 递归处理子节点
        for child in node:
            self._parse_node(child)
    
    def get_elements(self) -> List[Dict[str, Any]]:
        """获取解析后的元素列表"""
        return self.elements
    
    def find_element_by_text(self, text: str) -> Optional[Dict[str, Any]]:
        """根据文本查找元素"""
        for element in self.elements:
            if element.get('text') == text:
                return element
        return None
    
    def find_element_by_resource_id(self, resource_id: str) -> Optional[Dict[str, Any]]:
        """根据resource-id查找元素"""
        for element in self.elements:
            if element.get('resource-id') == resource_id:
                return element
        return None
    
    def find_elements_by_class(self, class_name: str) -> List[Dict[str, Any]]:
        """根据类名查找元素"""
        return [element for element in self.elements if element.get('class') == class_name]
    
    def get_clickable_elements(self) -> List[Dict[str, Any]]:
        """获取所有可点击的元素"""
        return [element for element in self.elements if element.get('clickable') == 'true']
    
    def get_element_bounds(self, element: Dict[str, Any]) -> Optional[Dict[str, int]]:
        """解析元素的边界坐标"""
        bounds_str = element.get('bounds', '')
        if not bounds_str:
            return None
        
        try:
            # 解析格式如 "[0,0][1080,120]"
            import re
            matches = re.findall(r'\[(\d+),(\d+)\]', bounds_str)
            if len(matches) == 2:
                x1, y1 = int(matches[0][0]), int(matches[0][1])
                x2, y2 = int(matches[1][0]), int(matches[1][1])
                return {
                    'left': x1,
                    'top': y1,
                    'right': x2,
                    'bottom': y2,
                    'width': x2 - x1,
                    'height': y2 - y1,
                    'center_x': (x1 + x2) // 2,
                    'center_y': (y1 + y2) // 2
                }
        except Exception as e:
            print(f"解析边界坐标失败: {e}")
        
        return None
    
    def export_to_json(self) -> str:
        """导出元素数据为JSON格式"""
        return json.dumps(self.elements, ensure_ascii=False, indent=2)
    
    def get_hierarchy_summary(self) -> Dict[str, Any]:
        """获取层次结构摘要信息"""
        if not self.elements:
            return {}
        
        # 统计各种元素类型
        class_counts = {}
        clickable_count = 0
        text_elements = 0
        
        for element in self.elements:
            class_name = element.get('class', 'Unknown')
            class_counts[class_name] = class_counts.get(class_name, 0) + 1
            
            if element.get('clickable') == 'true':
                clickable_count += 1
            
            if element.get('text'):
                text_elements += 1
        
        return {
            'total_elements': len(self.elements),
            'clickable_elements': clickable_count,
            'text_elements': text_elements,
            'class_distribution': class_counts,
            'device_id': self.device_id
        }