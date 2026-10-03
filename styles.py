# VibeStreamer PRO Stylesheet

THEME_STYLE = """
/* Global Styles */
QWidget {
    background-color: #0F0F1A;
    color: #E2E8F0;
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif;
    font-size: 13px;
}

/* Main Window */
QMainWindow {
    background-color: #0F0F1A;
}

/* Sidebar Navigation */
QFrame#Sidebar {
    background-color: #161626;
    border-right: 1px solid #23233B;
}

QLabel#BrandLabel {
    font-size: 20px;
    font-weight: 800;
    color: #FFFFFF;
    background: transparent;
    padding: 10px 0px;
}

QPushButton#NavButton {
    background-color: transparent;
    color: #94A3B8;
    border: none;
    border-radius: 8px;
    padding: 12px 16px;
    text-align: left;
    font-size: 14px;
    font-weight: 600;
}

QPushButton#NavButton:hover {
    background-color: #1E1E38;
    color: #FFFFFF;
}

QPushButton#NavButton:checked {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7C3AED, stop:1 #4F46E5);
    color: #FFFFFF;
    font-weight: 700;
}

/* Tab Container */
QStackedWidget {
    background-color: #0F0F1A;
}

/* Input Controls */
QLineEdit {
    background-color: #161626;
    border: 2px solid #23233B;
    border-radius: 8px;
    padding: 10px 14px;
    color: #FFFFFF;
    font-size: 13px;
}

QLineEdit:focus {
    border: 2px solid #7C3AED;
    background-color: #1A1A30;
}

QComboBox {
    background-color: #161626;
    border: 2px solid #23233B;
    border-radius: 8px;
    padding: 8px 12px;
    color: #E2E8F0;
    min-width: 120px;
}

QComboBox:focus {
    border: 2px solid #7C3AED;
}

QComboBox::drop-down {
    border: 0px;
}

QComboBox QAbstractItemView {
    background-color: #161626;
    border: 2px solid #23233B;
    selection-background-color: #7C3AED;
    selection-color: #FFFFFF;
}

/* Buttons */
QPushButton#PrimaryButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7C3AED, stop:1 #4F46E5);
    color: #FFFFFF;
    font-weight: 700;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 13px;
}

QPushButton#PrimaryButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8B5CF6, stop:1 #6366F1);
}

QPushButton#PrimaryButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6D28D9, stop:1 #4338CA);
}

QPushButton#SecondaryButton {
    background-color: #1E1E38;
    color: #E2E8F0;
    border: 1px solid #3B3B5C;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: 600;
}

QPushButton#SecondaryButton:hover {
    background-color: #2D2D54;
    border-color: #4F46E5;
}

/* ScrollBars */
QScrollBar:vertical {
    border: none;
    background: #0F0F1A;
    width: 8px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #2D2D4E;
    min-height: 20px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #4F46E5;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    border: none;
    background: none;
}

/* Cards & Items */
QFrame#Card {
    background-color: #161626;
    border: 1px solid #23233B;
    border-radius: 12px;
}

QFrame#ResultCard {
    background-color: #161626;
    border: 1px solid #23233B;
    border-radius: 12px;
}

QFrame#ResultCard:hover {
    border: 1px solid #7C3AED;
}

/* Progress Bars */
QProgressBar {
    background-color: #161626;
    border: 1px solid #23233B;
    border-radius: 8px;
    text-align: center;
    color: #FFFFFF;
    font-weight: bold;
    height: 18px;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7C3AED, stop:1 #10B981);
    border-radius: 6px;
}

/* Tooltips */
QToolTip {
    background-color: #1E1E38;
    border: 1px solid #4F46E5;
    color: #FFFFFF;
    border-radius: 4px;
    padding: 4px;
}

/* Lists */
QListWidget {
    background-color: #0F0F1A;
    border: none;
    outline: none;
}

QListWidget::item {
    background-color: transparent;
    padding: 4px;
    margin-bottom: 8px;
}
"""