import functools
import socket
import struct
from time import sleep

import scrcpy
from scrcpy import const


def inject(control_type: int):
    """
    Inject control code, with this inject, we will be able to do unit test

    Args:
        control_type: event to send, TYPE_*
    """

    def wrapper(f):
        @functools.wraps(f)
        def inner(*args, **kwargs):
            package = struct.pack(">B", control_type) + f(*args, **kwargs)
            if args[0].parent.control_socket is not None:
                with args[0].parent.control_socket_lock:
                    args[0].parent.control_socket.send(package)
            return package

        return inner

    return wrapper


class ControlSender:
    def __init__(self, parent):
        self.parent = parent

    @inject(const.TYPE_INJECT_KEYCODE)
    def keycode(
        self, keycode: int, action: int = const.ACTION_DOWN, repeat: int = 0
    ) -> bytes:
        """
        Send keycode to device

        Args:
            keycode: const.KEYCODE_*
            action: ACTION_DOWN | ACTION_UP
            repeat: repeat count
        """
        return struct.pack(">Biii", action, keycode, repeat, 0)

    @inject(const.TYPE_INJECT_TEXT)
    def text(self, text: str) -> bytes:
        """
        Send text to device

        Args:
            text: text to send
        """

        buffer = text.encode("utf-8")
        return struct.pack(">i", len(buffer)) + buffer

    @inject(const.TYPE_INJECT_TOUCH_EVENT)
    def touch(
        self, x: int, y: int, action: int = const.ACTION_DOWN, touch_id: int = 0x1234567887654321
    ) -> bytes:
        """
        Touch screen

        Args:
            x: horizontal position
            y: vertical position
            action: ACTION_DOWN | ACTION_UP | ACTION_MOVE
            touch_id: Default using virtual id -1, you can specify it to emulate multi finger touch
        """
        x, y = max(x, 0), max(y, 0)
        return struct.pack(
            ">BqiiHHHii",
            action,
            touch_id,
            int(x),
            int(y),
            int(self.parent.resolution[0]),
            int(self.parent.resolution[1]),
            0xFFFF,
            1,
            1,
        )

    @inject(const.TYPE_INJECT_SCROLL_EVENT)
    def scroll(self, x: int, y: int, h: int, v: int) -> bytes:
        """
        Scroll screen

        Args:
            x: horizontal position
            y: vertical position
            h: horizontal movement
            v: vertical movement
        """
        x, y = max(x, 0), max(y, 0)
        
        # 滚动值放大倍数，针对scrcpy 3.3.2版本优化
        scroll_multiplier = 50
        h_scaled = int(h * scroll_multiplier)
        v_scaled = int(v * scroll_multiplier)
        
        # 限制在int16范围内
        h_scroll = max(-32767, min(32767, h_scaled))
        v_scroll = max(-32767, min(32767, v_scaled))
        
        return struct.pack(
            ">iiHHhhI",
            int(x),
            int(y),
            int(self.parent.resolution[0]),
            int(self.parent.resolution[1]),
            h_scroll,
            v_scroll,
            0,  # buttons状态
        )

    @inject(const.TYPE_BACK_OR_SCREEN_ON)
    def back_or_turn_screen_on(self, action: int = const.ACTION_DOWN) -> bytes:
        """
        If the screen is off, it is turned on only on ACTION_DOWN

        Args:
            action: ACTION_DOWN | ACTION_UP
        """
        return struct.pack(">B", action)

    @inject(const.TYPE_EXPAND_NOTIFICATION_PANEL)
    def expand_notification_panel(self) -> bytes:
        """
        Expand notification panel
        """
        return b""

    @inject(const.TYPE_EXPAND_SETTINGS_PANEL)
    def expand_settings_panel(self) -> bytes:
        """
        Expand settings panel
        """
        return b""

    @inject(const.TYPE_COLLAPSE_PANELS)
    def collapse_panels(self) -> bytes:
        """
        Collapse all panels
        """
        return b""

    def get_clipboard(self, copy_key: int = const.COPY_KEY_NONE) -> str:
        """
        Get clipboard with copy key support

        Args:
            copy_key: COPY_KEY_NONE, COPY_KEY_COPY, or COPY_KEY_CUT
        """
        # Since this function need socket response, we can't auto inject it any more
        s: socket.socket = self.parent.control_socket

        with self.parent.control_socket_lock:
            # Flush socket
            s.setblocking(False)
            while True:
                try:
                    s.recv(1024)
                except BlockingIOError:
                    break
            s.setblocking(True)

            # Read package with copy_key
            package = struct.pack(">BB", const.TYPE_GET_CLIPBOARD, copy_key)
            s.send(package)
            (code,) = struct.unpack(">B", s.recv(1))
            assert code == 0
            (length,) = struct.unpack(">i", s.recv(4))

            return s.recv(length).decode("utf-8")

    @inject(const.TYPE_SET_CLIPBOARD)
    def set_clipboard(self, text: str, paste: bool = False, sequence: int = 0) -> bytes:
        """
        Set clipboard with sequence support

        Args:
            text: the string you want to set
            paste: paste now
            sequence: sequence number for sync
        """
        buffer = text.encode("utf-8")
        return struct.pack(">Q?i", sequence, paste, len(buffer)) + buffer

    @inject(const.TYPE_SET_DISPLAY_POWER)
    def set_display_power(self, on: bool = True) -> bytes:
        """
        Set display power mode

        Args:
            on: True to turn on, False to turn off
        """
        return struct.pack(">?", on)
    
    # 保持向后兼容性
    def set_screen_power_mode(self, mode: int = scrcpy.POWER_MODE_NORMAL) -> bytes:
        """
        Set screen power mode (deprecated, use set_display_power instead)

        Args:
            mode: POWER_MODE_OFF | POWER_MODE_NORMAL
        """
        return self.set_display_power(mode == scrcpy.POWER_MODE_NORMAL)

    @inject(const.TYPE_ROTATE_DEVICE)
    def rotate_device(self) -> bytes:
        """
        Rotate device
        """
        return b""

    @inject(const.TYPE_UHID_CREATE)
    def uhid_create(self, id: int, vendor_id: int, product_id: int, name: str, report_desc: bytes) -> bytes:
        """
        Create UHID device

        Args:
            id: device id
            vendor_id: vendor id
            product_id: product id
            name: device name
            report_desc: report descriptor
        """
        name_bytes = name.encode("utf-8")
        return struct.pack(">IIII", id, vendor_id, product_id, len(name_bytes)) + name_bytes + report_desc

    @inject(const.TYPE_UHID_INPUT)
    def uhid_input(self, id: int, data: bytes) -> bytes:
        """
        Send UHID input

        Args:
            id: device id
            data: input data
        """
        return struct.pack(">I", id) + data

    @inject(const.TYPE_UHID_DESTROY)
    def uhid_destroy(self, id: int) -> bytes:
        """
        Destroy UHID device

        Args:
            id: device id
        """
        return struct.pack(">I", id)

    @inject(const.TYPE_OPEN_HARD_KEYBOARD_SETTINGS)
    def open_hard_keyboard_settings(self) -> bytes:
        """
        Open hardware keyboard settings
        """
        return b""

    @inject(const.TYPE_START_APP)
    def start_app(self, app_name: str) -> bytes:
        """
        Start an app

        Args:
            app_name: name of the app to start
        """
        return app_name.encode("utf-8")

    @inject(const.TYPE_RESET_VIDEO)
    def reset_video(self) -> bytes:
        """
        Reset video encoding
        """
        return b""

    def swipe(
        self,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
        move_step_length: int = 5,
        move_steps_delay: float = 0.005,
    ) -> None:
        """
        Swipe on screen

        Args:
            start_x: start horizontal position
            start_y: start vertical position
            end_x: start horizontal position
            end_y: end vertical position
            move_step_length: length per step
            move_steps_delay: sleep seconds after each step
        :return:
        """

        self.touch(start_x, start_y, const.ACTION_DOWN)
        next_x = start_x
        next_y = start_y

        if end_x > self.parent.resolution[0]:
            end_x = self.parent.resolution[0]

        if end_y > self.parent.resolution[1]:
            end_y = self.parent.resolution[1]

        decrease_x = True if start_x > end_x else False
        decrease_y = True if start_y > end_y else False
        while True:
            if decrease_x:
                next_x -= move_step_length
                if next_x < end_x:
                    next_x = end_x
            else:
                next_x += move_step_length
                if next_x > end_x:
                    next_x = end_x

            if decrease_y:
                next_y -= move_step_length
                if next_y < end_y:
                    next_y = end_y
            else:
                next_y += move_step_length
                if next_y > end_y:
                    next_y = end_y

            self.touch(next_x, next_y, const.ACTION_MOVE)

            if next_x == end_x and next_y == end_y:
                self.touch(next_x, next_y, const.ACTION_UP)
                break
            sleep(move_steps_delay)
