import sys
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QPointF
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtWidgets import QApplication, QMainWindow

class CircleOverlay(QMainWindow):
    def __init__(self, x, y, radius=50, duration=2):
        super().__init__()

        self.setWindowTitle("Circle Overlay")
        self.setGeometry(0, 0, 1920, 1080)  # Full screen size
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.x = x
        self.y = y
        self.radius = radius
        self.duration = duration

        # Timer to handle opacity animation
        self.opacity_timer = QTimer(self)
        self.opacity_timer.timeout.connect(self.update_opacity)
        self.opacity_timer.start(50)  # Update opacity every 50 ms

        # Set the starting opacity
        self.opacity = 0.0  # Start fully transparent
        self.opacity_direction = 1  # 1 means fade in, -1 means fade out

        # Timer to close the window after `duration`
        QTimer.singleShot(duration * 1000, self.close)

    def update_opacity(self):
        """Bounce opacity in and out"""
        if self.opacity_direction == 1:
            self.opacity += 0.05  # Increase opacity
            if self.opacity >= 1.0:
                self.opacity_direction = -1  # Switch to fade out
        else:
            self.opacity -= 0.05  # Decrease opacity
            if self.opacity <= 0.0:
                self.opacity_direction = 1  # Switch to fade in
        
        self.update()  # Trigger a repaint to reflect the new opacity

    def paintEvent(self, event):
        """Draw the circle with the current opacity"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.red)  # Circle outline color
        painter.setBrush(QColor(255, 0, 0, int(self.opacity * 255)))  # Semi-transparent fill
        painter.drawEllipse(self.x - self.radius, self.y - self.radius,
                            self.radius * 2, self.radius * 2)  # Draw circle

def highlight(x, y, radius=50, duration=2):
    if sys.platform == "darwin":
        import objc
        from Foundation import NSBundle
        from AppKit import NSApplication, NSApp, NSApplicationActivationPolicyAccessory
        NSBundle.mainBundle().infoDictionary()["LSBackgroundOnly"] = "1"
        app = NSApplication.sharedApplication()
        app.setActivationPolicy_(NSApplicationActivationPolicyAccessory)
    app = QApplication(sys.argv)
    circle_overlay = CircleOverlay(x, y, radius, duration)
    circle_overlay.show()
    sys.exit(app.exec_())

