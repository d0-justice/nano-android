# Nano Android - Android设备屏幕镜像与控制

一个基于Python和Flet框架构建的现代化Android设备屏幕镜像与控制应用程序。本项目通过简洁的桌面界面提供实时Android设备屏幕镜像、鼠标/键盘控制和截图功能。

## 功能特性

### 🖥️ 实时屏幕镜像
- 使用scrcpy协议的高质量Android设备屏幕镜像
- 可配置分辨率（最大800px宽度）和比特率（默认4Mbps）
- 优化帧处理的流畅20 FPS显示
- 支持同时连接多个设备

### 🎮 设备控制
- **鼠标控制**：在镜像屏幕上点击、拖拽和滚动
- **键盘输入**：完整的键盘支持，用于文本输入和快捷键
- **触摸手势**：原生Android触摸事件模拟
- **实时交互**：低延迟输入响应

### 📸 截图功能
- **快速截图**：按 `` ` ``（反引号）键捕获截图
- **批量截图**：从所有连接的设备捕获截图
- **自动保存**：截图自动保存并带有时间戳
- **多种格式**：支持各种图像格式

### 🔧 高级功能
- **多设备支持**：连接和控制多个Android设备
- **响应式UI**：基于Flet的现代桌面界面
- **设备自动检测**：自动检测已连接的Android设备
- **连接管理**：简单的设备连接/断开管理
- **错误处理**：强大的错误处理和恢复机制

## 系统要求

### 系统环境要求
- Python 3.8 或更高版本
- Windows/macOS/Linux 支持
- 已安装并配置ADB（Android调试桥）

### Android设备要求
- Android 5.0（API级别21）或更高版本
- 已启用USB调试
- 已授予屏幕录制权限

## 安装说明

1. **克隆仓库**：
   ```bash
   git clone https://github.com/your-username/nano-android.git
   cd nano-android
   ```

2. **安装依赖**：
   ```bash
   pip install -r requirements.txt
   ```

3. **设置ADB**：
   - 安装Android SDK Platform Tools
   - 将ADB添加到系统PATH
   - 在Android设备上启用USB调试

4. **部署scrcpy服务器**（首次连接时自动执行）：
   ```bash
   adb push scrcpy/scrcpy/scrcpy-server.jar /data/local/tmp/
   ```

## 使用方法

### 快速开始

1. **连接Android设备**：通过USB连接并启用USB调试

2. **验证设备连接**：
   ```bash
   adb devices
   ```

3. **运行应用程序**：
   ```bash
   python main.py
   ```

4. **访问Web界面**：
   - 打开浏览器并导航到 `http://localhost:8550`
   - 应用程序将自动检测并连接到可用设备

### 键盘快捷键

- **`` ` ``**（反引号）：对所有连接的设备进行截图
- **F1-F4**：在不同视图/设备之间导航
- **鼠标**：点击和拖拽进行设备交互
- **键盘**：直接在镜像屏幕上输入

### 截图管理

截图会自动保存，命名规则如下：
```
screenshot_[设备ID]_[时间戳].png
```

## 项目结构

```
nano-android/
├── main.py                 # 主应用程序入口点
├── signal_manager.py       # 组件通信信号系统
├── requirements.txt        # Python依赖
├── view/                   # UI组件和视图
│   ├── __init__.py        # 包初始化文件
│   ├── main_window.py     # 主应用程序窗口
│   ├── device_view.py     # 设备屏幕视图组件
│   ├── device_screenshot.py # 截图功能
│   ├── element_inspector.py # UI元素检查器
│   ├── hierarchy.py       # UI层次结构查看器
│   ├── chat.py           # 聊天界面组件
│   ├── code.py           # 代码编辑器组件
│   ├── flow.py           # 流程图组件
│   └── graph.py          # 图形可视化组件
├── test/                  # 测试文件
│   ├── __init__.py       # 包初始化文件
│   ├── test_signal_system.py # 信号系统测试
│   └── test_decorator_signal_system.py # 装饰器信号测试
├── scrcpy/               # Scrcpy客户端库
│   ├── core.py          # 核心scrcpy客户端
│   ├── device.py        # 设备管理
│   └── scrcpy/          # Scrcpy服务器和工具
├── uiautomation/        # UI自动化工具
│   ├── element_selector.py # 元素选择工具
│   ├── hierarchy_manager.py # 层次结构管理
│   └── ui_visualizer.py # UI可视化工具
├── utils/               # 工具函数
├── adb_proxy/          # ADB代理工具
└── README.md           # 英文说明文档
```

## 配置选项

应用程序可以通过 `main.py` 中的 `Config` 类进行配置：

```python
class Config:
    WINDOW_WIDTH = 1200        # 应用程序窗口宽度
    WINDOW_HEIGHT = 800        # 应用程序窗口高度
    LEFT_CONTAINER_WIDTH = 800 # 设备视图容器宽度
    NODE_SIZE = 80            # UI元素大小
    # ... 更多配置选项
```

## 故障排除

### 常见问题

1. **设备未检测到**：
   - 确保已启用USB调试
   - 检查ADB连接：`adb devices`
   - 尝试不同的USB线缆或端口

2. **连接超时**：
   - 在设备配置中增加连接超时时间
   - 重启ADB服务器：`adb kill-server && adb start-server`

3. **屏幕录制权限**：
   - 在设备上出现提示时授予屏幕录制权限
   - 某些设备需要在设置中手动授权

4. **性能问题**：
   - 在客户端配置中降低比特率或分辨率
   - 关闭其他使用设备资源的应用程序

### 调试模式

通过设置环境变量启用调试日志：
```bash
export DEBUG=1
python main.py
```

## 贡献指南

1. Fork 仓库
2. 创建功能分支：`git checkout -b feature-name`
3. 提交更改：`git commit -am 'Add feature'`
4. 推送到分支：`git push origin feature-name`
5. 提交Pull Request

## 依赖项

### 核心依赖
- **flet (0.28.3)**：用于桌面应用程序的现代UI框架
- **opencv-python**：图像处理和计算机视觉库
- **numpy**：数值计算库
- **httpx**：现代HTTP客户端库

### Scrcpy依赖
- **scrcpy-client**：scrcpy协议的Python客户端
- **adb-shell**：Android调试桥shell接口

## 许可证

本项目采用MIT许可证 - 详见 [LICENSE](LICENSE) 文件。

## 致谢

- [scrcpy](https://github.com/Genymobile/scrcpy) - 原始scrcpy项目
- [py-scrcpy-client](https://github.com/leng-yue/py-scrcpy-client) - Python scrcpy客户端库
- [Flet](https://flet.dev/) - Python现代UI框架

## 技术支持

如需支持和咨询：
- 在GitHub上创建issue
- 查看上述故障排除部分
- 查阅scrcpy文档了解设备特定问题

## 开发说明

### 主要组件

1. **main.py**：应用程序主入口，包含UI布局和事件处理
2. **device_view.py**：设备屏幕显示组件，处理屏幕镜像和用户交互
3. **device_screenshot.py**：截图功能实现
4. **scrcpy/**：scrcpy协议客户端实现

### 架构特点

- **模块化设计**：各功能模块独立，便于维护和扩展
- **异步处理**：使用多线程处理设备连接和帧更新
- **事件驱动**：基于事件的用户交互处理
- **错误恢复**：完善的错误处理和自动重连机制

---

**注意**：本项目仅用于教育和开发目的。使用设备镜像工具时请确保遵守您所在组织的相关政策。

