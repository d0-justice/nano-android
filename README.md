# Nano Android - Android Device Screen Mirroring & Control

A modern Android device screen mirroring and control application built with Python and Flet framework. This project provides real-time Android device screen mirroring, mouse/keyboard control, and screenshot functionality through a clean desktop interface.

## Features

### 🖥️ Real-time Screen Mirroring
- High-quality Android device screen mirroring using scrcpy protocol
- Configurable resolution (max 800px width) and bitrate (4Mbps default)
- Smooth 20 FPS display with optimized frame processing
- Support for multiple device connections simultaneously

### 🎮 Device Control
- **Mouse Control**: Click, drag, and scroll on the mirrored screen
- **Keyboard Input**: Full keyboard support for text input and shortcuts
- **Touch Gestures**: Native Android touch event simulation
- **Real-time Interaction**: Low-latency input response

### 📸 Screenshot Functionality
- **Quick Screenshot**: Press `` ` `` (backtick) key to capture screenshots
- **Batch Screenshots**: Capture screenshots from all connected devices
- **Auto-save**: Screenshots automatically saved with timestamps
- **Multiple Formats**: Support for various image formats

### 🔧 Advanced Features
- **Multi-device Support**: Connect and control multiple Android devices
- **Responsive UI**: Modern Flet-based desktop interface
- **Device Auto-detection**: Automatic detection of connected Android devices
- **Connection Management**: Easy connect/disconnect device management
- **Error Handling**: Robust error handling and recovery mechanisms

## Requirements

### System Requirements
- Python 3.8 or higher
- Windows/macOS/Linux support
- ADB (Android Debug Bridge) installed and configured

### Android Device Requirements
- Android 5.0 (API level 21) or higher
- USB debugging enabled
- Screen recording permission granted

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/d0-justice/nano-android.git
   cd nano-android
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup ADB**:
   - Install Android SDK Platform Tools
   - Add ADB to your system PATH
   - Enable USB debugging on your Android device

4. **Deploy scrcpy server** (automatic on first connection):
   ```bash
   adb push scrcpy/scrcpy/scrcpy-server.jar /data/local/tmp/
   ```

## Usage

### Quick Start

1. **Connect your Android device** via USB and enable USB debugging

2. **Verify device connection**:
   ```bash
   adb devices
   ```

3. **Run the application**:
   ```bash
   python main.py
   ```

4. **Access the web interface**:
   - Open your browser and navigate to `http://localhost:8550`
   - The application will automatically detect and connect to available devices

### Keyboard Shortcuts

- **`` ` ``** (Backtick): Take screenshot of all connected devices
- **F1-F4**: Navigate between different views/devices
- **Mouse**: Click and drag for device interaction
- **Keyboard**: Type directly on the mirrored screen

### Screenshot Management

Screenshots are automatically saved with the following naming convention:
```
screenshot_[device_id]_[timestamp].png
```

## Project Structure

```
nano-android/
├── main.py                 # Main application entry point
├── signal_manager.py       # Signal system for component communication
├── requirements.txt        # Python dependencies
├── view/                   # UI components and views
│   ├── __init__.py        # Package initialization
│   ├── main_window.py     # Main application window
│   ├── device_view.py     # Device screen view component
│   ├── device_screenshot.py # Screenshot functionality
│   ├── element_inspector.py # UI element inspection
│   ├── hierarchy.py       # UI hierarchy viewer
│   ├── chat.py           # Chat interface component
│   ├── code.py           # Code editor component
│   ├── flow.py           # Flow diagram component
│   └── graph.py          # Graph visualization component
├── test/                  # Test files
│   ├── __init__.py       # Package initialization
│   ├── test_signal_system.py # Signal system tests
│   └── test_decorator_signal_system.py # Decorator signal tests
├── scrcpy/               # Scrcpy client library
│   ├── core.py          # Core scrcpy client
│   ├── device.py        # Device management
│   └── scrcpy/          # Scrcpy server and utilities
├── uiautomation/        # UI automation utilities
│   ├── element_selector.py # Element selection utilities
│   ├── hierarchy_manager.py # Hierarchy management
│   └── ui_visualizer.py # UI visualization tools
├── utils/               # Utility functions
├── adb_proxy/          # ADB proxy utilities
└── README.md           # This file
```

## Configuration

The application can be configured through the `Config` class in `main.py`:

```python
class Config:
    WINDOW_WIDTH = 1200        # Application window width
    WINDOW_HEIGHT = 800        # Application window height
    LEFT_CONTAINER_WIDTH = 800 # Device view container width
    NODE_SIZE = 80            # UI element size
    # ... more configuration options
```

## Troubleshooting

### Common Issues

1. **Device not detected**:
   - Ensure USB debugging is enabled
   - Check ADB connection: `adb devices`
   - Try different USB cable or port

2. **Connection timeout**:
   - Increase connection timeout in device configuration
   - Restart ADB server: `adb kill-server && adb start-server`

3. **Screen recording permission**:
   - Grant screen recording permission when prompted on device
   - Some devices require manual permission in Settings

4. **Performance issues**:
   - Reduce bitrate or resolution in client configuration
   - Close other applications using device resources

### Debug Mode

Enable debug logging by setting environment variable:
```bash
export DEBUG=1
python main.py
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -am 'Add feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## Dependencies

### Core Dependencies
- **flet (0.28.3)**: Modern UI framework for desktop applications
- **opencv-python**: Image processing and computer vision
- **numpy**: Numerical computing library
- **httpx**: Modern HTTP client library

### Scrcpy Dependencies
- **scrcpy-client**: Python client for scrcpy protocol
- **adb-shell**: Android Debug Bridge shell interface

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [scrcpy](https://github.com/Genymobile/scrcpy) - The original scrcpy project
- [py-scrcpy-client](https://github.com/leng-yue/py-scrcpy-client) - Python scrcpy client library
- [Flet](https://flet.dev/) - Modern UI framework for Python

## Support

For support and questions:
- Create an issue on GitHub
- Check the troubleshooting section above
- Review the scrcpy documentation for device-specific issues

---

**Note**: This project is for educational and development purposes. Ensure you comply with your organization's policies when using device mirroring tools.

