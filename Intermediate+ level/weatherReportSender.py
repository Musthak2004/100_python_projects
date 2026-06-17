import sys
import re
import smtplib
import math
import requests
import datetime as dt
from email.mime.text import MIMEText

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QMessageBox, QGroupBox,
    QFormLayout, QGridLayout, QComboBox, QFrame, QGraphicsOpacityEffect,
    QSizePolicy, QCheckBox,
)
from PyQt5.QtCore import (
    Qt, QThread, pyqtSignal, QSettings, QTimer, QPropertyAnimation,
    QEasingCurve, QPoint,
)
from PyQt5.QtGui import (
    QFont, QColor, QPalette, QLinearGradient, QBrush, QPainter,
)

WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

CITY_PRESETS = [
    ("Colombo, Sri Lanka", 6.9271, 79.8612),
    ("London, UK", 51.5074, -0.1278),
    ("New York, USA", 40.7128, -74.0060),
    ("Tokyo, Japan", 35.6762, 139.6503),
    ("Dubai, UAE", 25.2048, 55.2708),
    ("Paris, France", 48.8566, 2.3522),
    ("Sydney, Australia", -33.8688, 151.2093),
    ("Mumbai, India", 19.0760, 72.8777),
]

WEATHER_META = {
    0:  ("\u2600\ufe0f", "Clear",         "#f9d976", "#f39f86"),
    1:  ("\u26c5",      "Mainly Clear",   "#f9d976", "#e0c3fc"),
    2:  ("\u26c5",      "Partly Cloudy",  "#bdc3c7", "#a1c4fd"),
    3:  ("\u2601\ufe0f","Overcast",       "#a1c4fd", "#c2e9fb"),
    45: ("\ud83c\udf2b\ufe0f","Fog",     "#d7d2cc", "#304352"),
    48: ("\ud83c\udf2b\ufe0f","Rime Fog","#d7d2cc", "#304352"),
    51: ("\ud83c\udf27\ufe0f","Light Drizzle","#89ABE3","#4A6FA5"),
    53: ("\ud83c\udf27\ufe0f","Moderate Drizzle","#89ABE3","#4A6FA5"),
    55: ("\ud83c\udf27\ufe0f","Dense Drizzle","#89ABE3","#4A6FA5"),
    61: ("\ud83c\udf27\ufe0f","Slight Rain","#74b9ff","#0984e3"),
    63: ("\ud83c\udf27\ufe0f","Moderate Rain","#74b9ff","#0984e3"),
    65: ("\ud83c\udf27\ufe0f","Heavy Rain","#74b9ff","#0652DD"),
    71: ("\ud83c\udf28\ufe0f","Slight Snow","#e0eafc","#cfdef3"),
    73: ("\ud83c\udf28\ufe0f","Moderate Snow","#e0eafc","#cfdef3"),
    75: ("\ud83c\udf28\ufe0f","Heavy Snow","#e0eafc","#a8c0ff"),
    80: ("\ud83c\udf27\ufe0f","Rain Showers","#74b9ff","#0652DD"),
    81: ("\ud83c\udf27\ufe0f","Rain Showers","#74b9ff","#0652DD"),
    82: ("\ud83c\udf27\ufe0f","Violent Rain","#74b9ff","#0652DD"),
    95: ("\u26c8\ufe0f",  "Thunderstorm",  "#2c3e50", "#3498db"),
    96: ("\u26c8\ufe0f",  "Thunderstorm",  "#2c3e50", "#2980b9"),
    99: ("\u26c8\ufe0f",  "Thunderstorm",  "#2c3e50", "#c0392b"),
}


def weather_info(code: int) -> tuple:
    return WEATHER_META.get(code, ("\ud83c\udf21\ufe0f", "Unknown", "#636e72", "#b2bec3"))


class WeatherFetcher(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, lat: float, lng: float):
        super().__init__()
        self.lat = lat
        self.lng = lng

    def run(self):
        params = {
            "latitude": self.lat,
            "longitude": self.lng,
            "current": [
                "temperature_2m", "relative_humidity_2m",
                "apparent_temperature", "weather_code", "wind_speed_10m",
                "wind_direction_10m", "surface_pressure", "visibility",
            ],
            "daily": [
                "temperature_2m_max", "temperature_2m_min",
                "precipitation_sum", "sunrise", "sunset",
            ],
            "timezone": "auto",
        }
        try:
            resp = requests.get(WEATHER_URL, params=params, timeout=10)
            resp.raise_for_status()
            self.finished.emit(resp.json())
        except requests.RequestException as e:
            self.error.emit(str(e))


class AnimatedLabel(QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.effect)
        self.anim = QPropertyAnimation(self.effect, b"opacity")
        self.anim.setDuration(400)
        self.anim.setEasingCurve(QEasingCurve.OutCubic)

    def fade_in(self):
        self.anim.stop()
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.start()

    def set_text_fade(self, text: str):
        self.setText(text)
        self.fade_in()


class Toast(QFrame):
    def __init__(self, parent, message: str, toast_type: str = "info"):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)

        colors = {
            "success": "#6aab73",
            "error": "#cc6666",
            "info": "#61afef",
            "warning": "#e5c07b",
        }
        bg = colors.get(toast_type, "#61afef")

        self.setStyleSheet(f"""
            background-color: {bg};
            color: #ffffff;
            border-radius: 8px;
            padding: 12px 24px;
            font-size: 11pt;
            font-weight: bold;
        """)
        self.label = QLabel(message, self)
        self.label.setStyleSheet("color: #ffffff; background: transparent;")
        self.label.adjustSize()
        self.resize(self.label.size())

        self.effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.effect)
        self.anim = QPropertyAnimation(self.effect, b"opacity")
        self.anim.setDuration(300)

    def show_with_fade(self):
        parent_rect = self.parent().geometry()
        x = parent_rect.center().x() - self.width() // 2
        y = parent_rect.bottom() - 80
        self.move(x, y)
        self.show()

        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.start()

        QTimer.singleShot(2500, self._fade_out)

    def _fade_out(self):
        self.anim.setStartValue(1.0)
        self.anim.setEndValue(0.0)
        self.anim.finished.connect(self.close)
        self.anim.start()


class GradientCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._color1 = "#2d2d2d"
        self._color2 = "#252525"
        self.setStyleSheet(self._style())

    def _style(self):
        return f"""
            GradientCard {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {self._color1}, stop:1 {self._color2});
                border: 1px solid #3c3c3c;
                border-radius: 12px;
            }}
        """

    def set_gradient(self, c1: str, c2: str):
        self._color1 = c1
        self._color2 = c2
        self.setStyleSheet(self._style())


class PasswordToggle(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self.input = QLineEdit()
        self.input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.input)

        self.toggle_btn = QPushButton("\U0001f441")
        self.toggle_btn.setFixedSize(32, 32)
        self.toggle_btn.setCursor(Qt.PointingHandCursor)
        self.toggle_btn.setToolTip("Toggle visibility")
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.toggled.connect(
            lambda c: self.input.setEchoMode(QLineEdit.Normal if c else QLineEdit.Password)
        )
        layout.addWidget(self.toggle_btn)


class WeatherApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("WeatherApp", "WeatherReportSender")
        self._weather_data = None
        self._setup_window()
        self._build_ui()
        self._load_settings()
        self._connect_signals()

    def _setup_window(self):
        self.setWindowTitle("Weather Report")
        self.setMinimumSize(780, 600)
        self.setStyleSheet("""
            QMainWindow { background-color: #161618; }
            QLabel { color: #cdd6f4; }
        """)
        QApplication.instance().setStyle("Fusion")
        p = QPalette()
        for role, color in {
            QPalette.Window: "#161618",
            QPalette.WindowText: "#cdd6f4",
            QPalette.Base: "#1e1e22",
            QPalette.Text: "#cdd6f4",
            QPalette.Button: "#2a2a30",
            QPalette.ButtonText: "#cdd6f4",
            QPalette.Highlight: "#6aab73",
            QPalette.ToolTipBase: "#2a2a30",
            QPalette.ToolTipText: "#cdd6f4",
        }.items():
            p.setColor(role, QColor(color))
        QApplication.instance().setPalette(p)

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(28, 20, 28, 20)
        root.setSpacing(16)

        self._build_header(root)
        self._build_content(root)
        self._build_email_section(root)

    def _build_header(self, root: QVBoxLayout):
        header = QHBoxLayout()
        header.setSpacing(12)

        icon = QLabel("\ud83c\udf21\ufe0f")
        icon.setFont(QFont("Segoe UI", 24))
        header.addWidget(icon)

        titles = QVBoxLayout()
        titles.setSpacing(0)
        t = QLabel("Weather Report")
        t.setFont(QFont("Segoe UI", 18, QFont.Bold))
        titles.addWidget(t)
        st = QLabel("Real-time weather & email delivery")
        st.setFont(QFont("Segoe UI", 10))
        st.setStyleSheet("color: #6c7086;")
        titles.addWidget(st)
        header.addLayout(titles)

        header.addStretch()
        root.addLayout(header)

    def _styled_input(self, text="", placeholder="") -> QLineEdit:
        inp = QLineEdit(text)
        inp.setPlaceholderText(placeholder)
        inp.setStyleSheet("""
            QLineEdit {
                background-color: #1e1e22; color: #cdd6f4;
                border: 1px solid #313138; border-radius: 8px;
                padding: 9px 12px; font-size: 11pt;
            }
            QLineEdit:focus { border: 1px solid #6aab73; }
        """)
        return inp

    def _accent_btn(self, text: str) -> QPushButton:
        btn = QPushButton(text)
        btn.setMinimumHeight(42)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFont(QFont("Segoe UI", 11, QFont.Bold))
        btn.setStyleSheet("""
            QPushButton {
                background-color: #6aab73; color: #ffffff;
                border: none; border-radius: 8px; padding: 8px 24px;
            }
            QPushButton:hover { background-color: #76b87f; }
            QPushButton:pressed { background-color: #5c9a65; }
            QPushButton:disabled {
                background-color: #2a2a30; color: #585b70;
                border: 1px solid #313138;
            }
        """)
        return btn

    def _icon_btn(self, text: str) -> QPushButton:
        btn = QPushButton(text)
        btn.setFixedSize(38, 38)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #1e1e22; color: #cdd6f4;
                border: 1px solid #313138; border-radius: 8px;
                font-size: 14pt;
            }
            QPushButton:hover { background-color: #313138; }
        """)
        return btn

    def _build_content(self, root: QVBoxLayout):
        row = QHBoxLayout()
        row.setSpacing(16)

        self._build_location_panel(row)
        self._build_weather_panel(row)
        root.addLayout(row, stretch=1)

    def _build_location_panel(self, row: QHBoxLayout):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #1c1c20; border: 1px solid #2a2a30;
                border-radius: 14px;
            }
        """)
        card.setFixedWidth(260)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(12)

        title = QLabel("Location")
        title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        layout.addWidget(title)

        self.preset_combo = QComboBox()
        self.preset_combo.addItem("Custom...")
        for name, *_ in CITY_PRESETS:
            self.preset_combo.addItem(name)
        self.preset_combo.setStyleSheet("""
            QComboBox {
                background-color: #1e1e22; color: #cdd6f4;
                border: 1px solid #313138; border-radius: 8px;
                padding: 8px 12px; font-size: 11pt;
            }
            QComboBox:hover { border-color: #4a4a55; }
            QComboBox::drop-down { border: none; width: 28px; }
            QComboBox QAbstractItemView {
                background-color: #1e1e22; color: #cdd6f4;
                selection-background-color: #6aab73;
                border: 1px solid #313138; border-radius: 6px;
                padding: 4px;
            }
            QComboBox QAbstractItemView::item {
                padding: 6px 10px; border-radius: 4px;
            }
        """)
        layout.addWidget(self.preset_combo)

        self.city_input = self._styled_input("Colombo")
        self.city_input.setToolTip("City display name")
        layout.addWidget(QLabel("City"))
        layout.addWidget(self.city_input)

        self.lat_input = self._styled_input("6.9271")
        self.lat_input.setToolTip("Decimal latitude")
        layout.addWidget(QLabel("Latitude"))
        layout.addWidget(self.lat_input)

        self.lng_input = self._styled_input("79.8612")
        self.lng_input.setToolTip("Decimal longitude")
        layout.addWidget(QLabel("Longitude"))
        layout.addWidget(self.lng_input)

        self.fetch_btn = self._accent_btn("\u2318  Fetch Weather")
        layout.addWidget(self.fetch_btn)
        layout.addStretch()
        row.addWidget(card)

    def _build_weather_panel(self, row: QHBoxLayout):
        self.weather_card = QFrame()
        self.weather_card.setStyleSheet("""
            QFrame {
                background-color: #1c1c20; border: 1px solid #2a2a30;
                border-radius: 14px;
            }
        """)
        layout = QVBoxLayout(self.weather_card)
        layout.setContentsMargins(24, 18, 24, 18)
        layout.setSpacing(0)

        # Skeleton placeholder overlay
        self.skeleton = QFrame()
        self.skeleton.setStyleSheet("""
            QFrame {
                background-color: #1e1e22; border-radius: 10px;
            }
        """)
        sk_layout = QVBoxLayout(self.skeleton)
        sk_layout.setAlignment(Qt.AlignCenter)

        sk_icon = QLabel("\ud83c\udf21\ufe0f")
        sk_icon.setFont(QFont("Segoe UI", 40))
        sk_icon.setAlignment(Qt.AlignCenter)
        sk_layout.addWidget(sk_icon)

        sk_text = QLabel("Enter coordinates and fetch\nweather data to see results")
        sk_text.setAlignment(Qt.AlignCenter)
        sk_text.setFont(QFont("Segoe UI", 12))
        sk_text.setStyleSheet("color: #585b70;")
        sk_layout.addWidget(sk_text)

        layout.addWidget(self.skeleton)

        # Data content (hidden initially)
        self.content_widget = QWidget()
        self.content_widget.hide()
        cl = QVBoxLayout(self.content_widget)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.setSpacing(8)

        emoji_row = QHBoxLayout()
        self.emoji_label = QLabel()
        self.emoji_label.setFont(QFont("Segoe UI", 42))
        emoji_row.addWidget(self.emoji_label)

        self.temp_label = AnimatedLabel("--\u00b0C")
        self.temp_label.setFont(QFont("Segoe UI", 34, QFont.Bold))
        emoji_row.addWidget(self.temp_label)

        self.desc_label = QLabel("No data")
        self.desc_label.setFont(QFont("Segoe UI", 13))
        self.desc_label.setStyleSheet("color: #a6adc8;")
        self.desc_label.setAlignment(Qt.AlignBottom)
        emoji_row.addWidget(self.desc_label)
        emoji_row.addStretch()
        cl.addLayout(emoji_row)

        self.feels_label = QLabel("")
        self.feels_label.setFont(QFont("Segoe UI", 11))
        self.feels_label.setStyleSheet("color: #6c7086;")
        cl.addWidget(self.feels_label)

        cl.addSpacing(6)

        self.humidity_label = AnimatedLabel("--%")
        self.wind_label = AnimatedLabel("-- km/h")
        self.pressure_label = AnimatedLabel("-- hPa")
        self.visibility_label = AnimatedLabel("-- km")

        detail_grid = QGridLayout()
        detail_grid.setSpacing(6)
        pairs = [
            ("\ud83d\udca7  Humidity",   self.humidity_label),
            ("\ud83d\udca8  Wind",       self.wind_label),
            ("\ud83e\udea7  Pressure",   self.pressure_label),
            ("\ud83d\udc41  Visibility", self.visibility_label),
        ]
        for i, (lbl, val) in enumerate(pairs):
            c = QLabel(lbl)
            c.setFont(QFont("Segoe UI", 10))
            c.setStyleSheet("color: #585b70;")
            detail_grid.addWidget(c, i // 2, (i % 2) * 2)
            detail_grid.addWidget(val, i // 2, (i % 2) * 2 + 1)

        cl.addLayout(detail_grid)
        cl.addSpacing(6)

        forecast_card = QFrame()
        forecast_card.setStyleSheet("""
            QFrame {
                background-color: #1e1e22; border: 1px solid #2a2a30;
                border-radius: 10px;
            }
        """)
        fcl = QHBoxLayout(forecast_card)
        fcl.setContentsMargins(16, 10, 16, 10)
        fcl.setSpacing(20)

        self.high_label = AnimatedLabel("\u2191 --\u00b0C")
        self.high_label.setFont(QFont("Segoe UI", 11))
        fcl.addWidget(self.high_label)

        self.low_label = AnimatedLabel("\u2193 --\u00b0C")
        self.low_label.setFont(QFont("Segoe UI", 11))
        self.low_label.setStyleSheet("color: #6c7086;")
        fcl.addWidget(self.low_label)

        self.precip_label = AnimatedLabel("\ud83c\udf27\ufe0f -- mm")
        self.precip_label.setFont(QFont("Segoe UI", 11))
        self.precip_label.setStyleSheet("color: #6c7086;")
        fcl.addWidget(self.precip_label)

        self.sun_label = AnimatedLabel("")
        self.sun_label.setFont(QFont("Segoe UI", 11))
        self.sun_label.setStyleSheet("color: #6c7086;")
        fcl.addWidget(self.sun_label)

        fcl.addStretch()
        cl.addWidget(forecast_card)

        cl.addStretch()

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        self.copy_btn = self._icon_btn("\ud83d\udccb")
        self.copy_btn.setToolTip("Copy report")
        btn_row.addWidget(self.copy_btn)

        self.clear_btn = self._icon_btn("\ud83d\uddd1\ufe0f")
        self.clear_btn.setToolTip("Clear report")
        btn_row.addWidget(self.clear_btn)

        btn_row.addStretch()
        self.send_btn = self._accent_btn("\u2709\ufe0f  Send Email")
        self.send_btn.setEnabled(False)
        btn_row.addWidget(self.send_btn)
        cl.addLayout(btn_row)

        layout.addWidget(self.content_widget)
        row.addWidget(self.weather_card, stretch=1)

    def _build_email_section(self, root: QVBoxLayout):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #1c1c20; border: 1px solid #2a2a30;
                border-radius: 14px;
            }
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 14, 20, 14)
        layout.setSpacing(10)

        header = QHBoxLayout()
        h = QLabel("\u2709\ufe0f  Email Settings")
        h.setFont(QFont("Segoe UI", 12, QFont.Bold))
        header.addWidget(h)
        header.addStretch()

        self.collapse_btn = QPushButton("\u25b4")
        self.collapse_btn.setFixedSize(28, 28)
        self.collapse_btn.setCursor(Qt.PointingHandCursor)
        self.collapse_btn.setStyleSheet("""
            QPushButton {
                background: transparent; color: #6c7086;
                border: none; font-size: 14pt;
            }
            QPushButton:hover { color: #cdd6f4; }
        """)
        header.addWidget(self.collapse_btn)
        layout.addLayout(header)

        self.email_body = QWidget()
        el = QGridLayout(self.email_body)
        el.setSpacing(8)
        el.setContentsMargins(0, 4, 0, 0)
        el.setColumnStretch(0, 0)
        el.setColumnStretch(1, 1)

        self.sender_input = self._styled_input("musthak20041027@gmail.com")
        el.addWidget(QLabel("Sender"), 0, 0)
        el.addWidget(self.sender_input, 0, 1)

        self.password_widget = PasswordToggle()
        self.password_widget.input.setEchoMode(QLineEdit.Password)
        el.addWidget(QLabel("Password"), 1, 0)
        el.addWidget(self.password_widget, 1, 1)

        self.recipient_input = self._styled_input("musthak20041027@gmail.com")
        el.addWidget(QLabel("Recipient"), 2, 0)
        el.addWidget(self.recipient_input, 2, 1)

        self.save_check = QCheckBox("Save Settings")
        self.save_check.setStyleSheet("""
            QCheckBox {
                color: #a6adc8; font-size: 10pt; spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px; height: 18px; border-radius: 4px;
                border: 2px solid #6aab73; background: transparent;
            }
            QCheckBox::indicator:checked {
                background: #6aab73;
            }
            QCheckBox:hover { color: #cdd6f4; }
        """)
        el.addWidget(self.save_check, 3, 1)

        layout.addWidget(self.email_body)

        self.collapse_btn.clicked.connect(self._toggle_email)
        root.addWidget(card)

    def _toggle_email(self):
        collapsed = self.email_body.isHidden()
        self.email_body.setVisible(collapsed)
        self.collapse_btn.setText("\u25b4" if collapsed else "\u25be")

    def _connect_signals(self):
        self.preset_combo.currentIndexChanged.connect(self._on_preset)
        self.lat_input.textChanged.connect(lambda: self.preset_combo.setCurrentIndex(0))
        self.lng_input.textChanged.connect(lambda: self.preset_combo.setCurrentIndex(0))
        self.lat_input.returnPressed.connect(self._fetch)
        self.lng_input.returnPressed.connect(self._fetch)
        self.fetch_btn.clicked.connect(self._fetch)
        self.copy_btn.clicked.connect(self._copy)
        self.clear_btn.clicked.connect(self._clear)
        self.send_btn.clicked.connect(self._send)

    def _on_preset(self, idx: int):
        if idx == 0:
            return
        name, lat, lng = CITY_PRESETS[idx - 1]
        self.lat_input.blockSignals(True)
        self.lng_input.blockSignals(True)
        self.lat_input.setText(str(lat))
        self.lng_input.setText(str(lng))
        self.lat_input.blockSignals(False)
        self.lng_input.blockSignals(False)
        self.city_input.setText(name.split(",")[0])

    def _toast(self, msg: str, t: str = "info"):
        toast = Toast(self, msg, t)
        toast.show_with_fade()

    @staticmethod
    def _is_valid_email(email: str) -> bool:
        return bool(re.match(r"[^@\s]+@[^@\s]+\.[^@\s]+$", email))

    def _highlight_field(self, field: QLineEdit, valid: bool):
        if valid:
            field.setStyleSheet("""
                QLineEdit {
                    background-color: #1e1e22; color: #cdd6f4;
                    border: 1px solid #313138; border-radius: 8px;
                    padding: 9px 12px; font-size: 11pt;
                }
                QLineEdit:focus { border: 1px solid #6aab73; }
            """)
        else:
            field.setStyleSheet("""
                QLineEdit {
                    background-color: #1e1e22; color: #cdd6f4;
                    border: 1px solid #cc6666; border-radius: 8px;
                    padding: 9px 12px; font-size: 11pt;
                }
                QLineEdit:focus { border: 1px solid #cc6666; }
            """)

    def _fetch(self):
        try:
            lat = float(self.lat_input.text())
            lng = float(self.lng_input.text())
        except ValueError:
            self._toast("Latitude and Longitude must be numeric.", "error")
            return

        self.fetch_btn.setEnabled(False)
        self.fetch_btn.setText("\u23f3  Fetching...")
        self.fetcher = WeatherFetcher(lat, lng)
        self.fetcher.finished.connect(self._on_data)
        self.fetcher.error.connect(self._on_err)
        self.fetcher.start()

    def _on_data(self, data: dict):
        self._weather_data = data
        self.fetch_btn.setEnabled(True)
        self.fetch_btn.setText("\u2318  Fetch Weather")

        current = data["current"]
        daily = data["daily"]
        code = current["weather_code"]
        emoji, desc, c1, c2 = weather_info(code)

        self.skeleton.hide()
        self.content_widget.show()

        self.emoji_label.setText(emoji)
        self.temp_label.set_text_fade(f"{current['temperature_2m']}\u00b0C")
        self.desc_label.setText(f"{desc}")
        self.feels_label.setText(f"Feels like {current['apparent_temperature']}\u00b0C")
        self.humidity_label.set_text_fade(f"{current['relative_humidity_2m']}%")
        wind_dir = self._wind_arrow(current.get("wind_direction_10m", 0))
        self.wind_label.set_text_fade(f"{current['wind_speed_10m']} km/h {wind_dir}")
        self.pressure_label.set_text_fade(f"{current.get('surface_pressure', '--')} hPa")
        vis_m = current.get("visibility")
        vis_km = f"{vis_m / 1000:.1f} km" if vis_m is not None else "-- km"
        self.visibility_label.set_text_fade(vis_km)

        self.high_label.set_text_fade(f"\u2191 High: {daily['temperature_2m_max'][0]}\u00b0C")
        self.low_label.set_text_fade(f"\u2193 Low: {daily['temperature_2m_min'][0]}\u00b0C")
        self.precip_label.set_text_fade(f"\ud83c\udf27\ufe0f {daily['precipitation_sum'][0]} mm")

        sunrise = daily.get("sunrise", [""])[0]
        sunset = daily.get("sunset", [""])[0]
        if sunrise and sunset:
            sr = sunrise.split("T")[1][:5] if "T" in sunrise else sunrise
            ss = sunset.split("T")[1][:5] if "T" in sunset else sunset
            self.sun_label.set_text_fade(f"\u2600\ufe0f {sr}  \ud83c\udf19 {ss}")

        self.send_btn.setEnabled(True)
        self._toast(f"Weather data for {self.city_input.text().strip()} loaded", "success")

    def _on_err(self, msg: str):
        self.fetch_btn.setEnabled(True)
        self.fetch_btn.setText("\u2318  Fetch Weather")
        self._toast(f"Error: {msg}", "error")

    @staticmethod
    def _wind_arrow(deg: float) -> str:
        dirs = ["\u2191", "\u2197", "\u2192", "\u2198", "\u2193", "\u2199", "\u2190", "\u2196"]
        idx = round(deg / 45) % 8
        return dirs[idx]

    def _copy(self):
        if not self._weather_data:
            return
        d = self._weather_data
        city = self.city_input.text().strip() or "Unknown"
        code = d["current"]["weather_code"]
        _, desc, _, _ = weather_info(code)
        report = (
            f"Weather Report - {city}\n"
            f"{dt.date.today().strftime('%A, %B %d, %Y')}\n"
            f"{'=' * 40}\n"
            f"Condition:  {desc}\n"
            f"Temp:       {d['current']['temperature_2m']}\u00b0C\n"
            f"Feels like: {d['current']['apparent_temperature']}\u00b0C\n"
            f"Humidity:   {d['current']['relative_humidity_2m']}%\n"
            f"Wind:       {d['current']['wind_speed_10m']} km/h\n"
            f"Pressure:   {d['current'].get('surface_pressure', '--')} hPa\n"
            f"High:       {d['daily']['temperature_2m_max'][0]}\u00b0C\n"
            f"Low:        {d['daily']['temperature_2m_min'][0]}\u00b0C\n"
            f"Rain:       {d['daily']['precipitation_sum'][0]} mm"
        )
        QApplication.instance().clipboard().setText(report)
        self._toast("Report copied to clipboard", "success")

    def _clear(self):
        self._weather_data = None
        self.content_widget.hide()
        self.skeleton.show()
        self.send_btn.setEnabled(False)
        self._toast("Report cleared", "info")

    def _send(self):
        sender = self.sender_input.text().strip()
        password = self.password_widget.input.text().strip()
        recipient = self.recipient_input.text().strip()

        self._highlight_field(self.sender_input, True)
        self._highlight_field(self.recipient_input, True)

        has_error = False
        if not self._is_valid_email(sender):
            self._highlight_field(self.sender_input, False)
            has_error = True
        if not self._is_valid_email(recipient):
            self._highlight_field(self.recipient_input, False)
            has_error = True
        if has_error:
            self._toast("Invalid email format", "error")
            return
        if not password:
            self._toast("Password cannot be empty", "error")
            return
        if not self._weather_data:
            self._toast("Fetch weather data first", "error")
            return

        self.send_btn.setEnabled(False)
        self.send_btn.setText("\u23f3  Sending...")
        QApplication.processEvents()

        d = self._weather_data
        city = self.city_input.text().strip() or "Unknown"
        code = d["current"]["weather_code"]
        _, desc, _, _ = weather_info(code)
        wind_dir = self._wind_arrow(d["current"].get("wind_direction_10m", 0))

        report = (
            f"Weather Report - {city}\n"
            f"{dt.date.today().strftime('%A, %B %d, %Y')}\n"
            f"{'=' * 40}\n\n"
            f"Current Conditions:\n"
            f"  Weather:     {desc}\n"
            f"  Temperature: {d['current']['temperature_2m']}\u00b0C\n"
            f"  Feels Like:  {d['current']['apparent_temperature']}\u00b0C\n"
            f"  Humidity:    {d['current']['relative_humidity_2m']}%\n"
            f"  Wind:        {d['current']['wind_speed_10m']} km/h {wind_dir}\n"
            f"  Pressure:    {d['current'].get('surface_pressure', '--')} hPa\n\n"
            f"Today's Forecast:\n"
            f"  High:        {d['daily']['temperature_2m_max'][0]}\u00b0C\n"
            f"  Low:         {d['daily']['temperature_2m_min'][0]}\u00b0C\n"
            f"  Rain:        {d['daily']['precipitation_sum'][0]} mm"
        )

        msg = MIMEText(report)
        msg["Subject"] = f"Weather Report - {city} - {dt.date.today()}"
        msg["From"] = sender
        msg["To"] = recipient

        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(sender, password)
                server.send_message(msg)
            self._toast("Weather report sent successfully!", "success")
            if self.save_check.isChecked():
                self._save_settings()
        except smtplib.SMTPAuthenticationError:
            self._toast("SMTP authentication failed. Check password.", "error")
        except smtplib.SMTPException as e:
            self._toast(f"SMTP error: {e}", "error")
        except Exception as e:
            self._toast(f"Error: {e}", "error")
        finally:
            self.send_btn.setEnabled(True)
            self.send_btn.setText("\u2709\ufe0f  Send Email")

    def _load_settings(self):
        if self.settings.value("save_creds", "false") == "true":
            self.sender_input.setText(self.settings.value("sender", ""))
            self.password_widget.input.setText(self.settings.value("password", ""))
            self.recipient_input.setText(self.settings.value("recipient", ""))
            self.save_check.setChecked(True)
        self.lat_input.setText(self.settings.value("lat", "6.9271"))
        self.lng_input.setText(self.settings.value("lng", "79.8612"))
        self.city_input.setText(self.settings.value("city", "Colombo"))

    def _save_settings(self):
        self.settings.setValue("sender", self.sender_input.text())
        self.settings.setValue("password", self.password_widget.input.text())
        self.settings.setValue("recipient", self.recipient_input.text())
        self.settings.setValue("save_creds", "true")
        self.settings.setValue("lat", self.lat_input.text())
        self.settings.setValue("lng", self.lng_input.text())
        self.settings.setValue("city", self.city_input.text())


def main():
    app = QApplication(sys.argv)
    w = WeatherApp()
    w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
