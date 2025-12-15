from PyQt5.QtCore import QPropertyAnimation, QRect, QEasingCurve
import src.app_state as app_state

def slide_to_index(target_index, direction=1):
    """
    Slide animation when switching pages in the QStackedWidget.
    direction = 1 -> new page comes from right
    direction = -1 -> new page comes from left
    """
    widget = app_state.widget
    if widget is None:
        return

    current_index = widget.currentIndex()
    if current_index == target_index:
        return

    current_widget = widget.widget(current_index)
    next_widget = widget.widget(target_index)

    w = widget.width()
    h = widget.height()
    offset_x = w * direction

    next_widget.setGeometry(offset_x, 0, w, h)
    next_widget.show()

    anim_old = QPropertyAnimation(current_widget, b"geometry", widget)
    anim_old.setDuration(300)
    anim_old.setStartValue(QRect(0, 0, w, h))
    anim_old.setEndValue(QRect(-offset_x, 0, w, h))
    anim_old.setEasingCurve(QEasingCurve.InOutCubic)

    anim_new = QPropertyAnimation(next_widget, b"geometry", widget)
    anim_new.setDuration(300)
    anim_new.setStartValue(QRect(offset_x, 0, w, h))
    anim_new.setEndValue(QRect(0, 0, w, h))
    anim_new.setEasingCurve(QEasingCurve.InOutCubic)

    if not hasattr(widget, "_anims"):
        widget._anims = []
    widget._anims.extend([anim_old, anim_new])

    def on_finished():
        widget.setCurrentIndex(target_index)
        current_widget.hide()
        widget._anims.clear()

    anim_new.finished.connect(on_finished)
    anim_old.start()
    anim_new.start()
