import sys
from pathlib import Path

from PySide6.QtCore import Qt, QSize, QUrl, QStandardPaths
from PySide6.QtGui import QDesktopServices, QIcon, QPixmap
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QFrame, QHBoxLayout, QLabel,
    QLineEdit, QListWidget, QListWidgetItem, QMainWindow, QMessageBox,
    QPushButton, QScrollArea, QSlider, QSplitter, QStackedWidget,
    QStyle, QToolButton, QVBoxLayout, QWidget,
)

from .catalog import ROOT, Favorites, load_catalog, matches


STYLE = """
QWidget { font-family: 'Segoe UI'; font-size: 14px; color: #19334a; }
QMainWindow, QScrollArea, #detail { background: #ffffff; }
#sidebar { background: #f0f6f9; border-right: 1px solid #dde6ec; }
#brand { font-size: 25px; font-weight: 700; color: #126d8b; }
#title { font-size: 28px; font-weight: 700; }
#subtitle, #count { color: #607487; }
#section { font-size: 16px; font-weight: 600; color: #13877f; }
#placeholder { background: #eef3f5; color: #687f8d; border-radius: 8px; }
QLineEdit, QComboBox { padding: 9px; border: 1px solid #d5e1e8; border-radius: 6px; background: white; }
QPushButton, QToolButton { padding: 9px; border: 1px solid #d5e1e8; border-radius: 6px; background: #ffffff; }
QPushButton:hover, QToolButton:hover { background: #eaf4fb; }
QPushButton:checked, QToolButton:checked { background: #dceefc; color: #086cc2; border-color: #76b6ef; }
QPushButton:disabled, QToolButton:disabled { color: #8c9aa4; }
QListWidget { background: #ffffff; border: none; outline: none; }
QListWidget::item { padding: 12px; margin: 4px 0; border: 1px solid #e2e9ee; border-radius: 7px; }
QListWidget::item:selected { background: #e8f4fd; color: #115fa0; border: 1px solid #56a9ed; }
QListWidget::item:hover { background: #f1f8fc; }
QScrollArea { border: none; }
QSlider::groove:horizontal { height: 5px; background: #dce5eb; }
QSlider::handle:horizontal { width: 13px; margin: -4px 0; border-radius: 6px; background: #1287d7; }
QSplitter::handle { background: #edf2f5; width: 1px; }
"""


def label(text="", name=None):
    widget = QLabel(text)
    widget.setWordWrap(True)
    widget.setTextFormat(Qt.TextFormat.PlainText)
    if name:
        widget.setObjectName(name)
    return widget


class Window(QMainWindow):
    def __init__(self, database=None):
        super().__init__()
        self.setWindowTitle("QhapaqFit")
        logo_path = ROOT / "assets/branding/qhapaqdata-logo.png"
        self.setWindowIcon(QIcon(str(logo_path)))
        self.resize(1240, 820)
        self.setMinimumSize(860, 600)
        self.exercises = load_catalog()
        location = Path(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppLocalDataLocation))
        self.favorites = Favorites(database or location / "favorites.sqlite3")
        self.current = None
        self.only_favorites = False
        self.player = QMediaPlayer(self)
        self.audio = QAudioOutput(self)
        self.audio.setMuted(False)
        self.audio.setVolume(0.7)
        self.player.setAudioOutput(self.audio)
        shell = QWidget()
        outer = QHBoxLayout(shell)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        self.setCentralWidget(shell)
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(190)
        nav = QVBoxLayout(sidebar)
        nav.setContentsMargins(18, 28, 18, 22)
        self.brand_logo = QLabel()
        self.brand_logo.setFixedSize(80, 80)
        self.brand_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.brand_logo.setAccessibleName("QhapaqFit")
        self.brand_logo.setToolTip("QhapaqFit")
        self.brand_logo.setPixmap(QPixmap(str(logo_path)).scaled(
            80, 80, Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation))
        nav.addWidget(self.brand_logo, 0, Qt.AlignmentFlag.AlignHCenter)
        nav.addWidget(label("QhapaqFit", "brand"))
        nav.addWidget(label("Tu mejor version, hoy", "subtitle"))
        nav.addSpacing(32)
        self.browse = QPushButton("Ejercicios")
        self.saved = QPushButton("Favoritos")
        for button in (self.browse, self.saved):
            button.setCheckable(True)
            button.setMinimumHeight(44)
            nav.addWidget(button)
        self.browse.setChecked(True)
        self.browse.clicked.connect(lambda: self.set_view(False))
        self.saved.clicked.connect(lambda: self.set_view(True))
        nav.addStretch()
        folder = QPushButton("Abrir multimedia")
        folder.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DirOpenIcon))
        folder.clicked.connect(lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(str(ROOT / "assets"))))
        nav.addWidget(folder)
        nav.addWidget(label("Enciclopedia de ejercicios", "subtitle"))
        outer.addWidget(sidebar)
        workspace = QWidget()
        body = QVBoxLayout(workspace)
        body.setContentsMargins(24, 22, 24, 20)
        body.setSpacing(14)
        top = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Buscar ejercicios, musculos, equipamiento...")
        self.search.setClearButtonEnabled(True)
        self.search.textChanged.connect(self.populate)
        top.addWidget(self.search)
        self.refresh = self.icon_button(QStyle.StandardPixmap.SP_BrowserReload, "Actualizar multimedia")
        self.refresh.clicked.connect(self.reload_media)
        top.addWidget(self.refresh)
        body.addLayout(top)
        self.heading = label("Ejercicios", "title")
        body.addWidget(self.heading)
        filters = QHBoxLayout()
        self.count = label("", "count")
        filters.addWidget(self.count, 1)
        self.group = QComboBox()
        self.group.addItem("Todas las zonas")
        self.group.addItems(sorted({e["group"] for e in self.exercises}))
        self.group.currentIndexChanged.connect(self.populate)
        filters.addWidget(self.group)
        self.equipment = QComboBox()
        self.equipment.addItem("Todo el equipamiento")
        self.equipment.addItems(sorted({e["equipment"] for e in self.exercises}))
        self.equipment.currentIndexChanged.connect(self.populate)
        filters.addWidget(self.equipment)
        body.addLayout(filters)
        split = QSplitter(Qt.Orientation.Horizontal)
        self.items = QListWidget()
        self.items.setMinimumWidth(210)
        self.items.setWordWrap(True)
        self.items.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.items.setIconSize(QSize(56, 56))
        self.items.currentItemChanged.connect(self.select)
        split.addWidget(self.items)
        self.pages = QStackedWidget()
        empty = label("No hay ejercicios para mostrar.")
        empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pages.addWidget(empty)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        detail = QWidget()
        detail.setObjectName("detail")
        info = QVBoxLayout(detail)
        info.setContentsMargins(22, 8, 8, 20)
        info.setSpacing(16)
        title_row = QHBoxLayout()
        self.title = label("", "title")
        title_row.addWidget(self.title, 1)
        self.favorite = self.icon_button(QStyle.StandardPixmap.SP_DialogYesButton, "Guardar en favoritos")
        self.favorite.setIcon(QIcon())
        self.favorite.setText("\u2606")
        self.favorite.setStyleSheet("font-size: 24px; padding: 0;")
        self.favorite.setCheckable(True)
        self.favorite.clicked.connect(self.toggle_favorite)
        title_row.addWidget(self.favorite)
        info.addLayout(title_row)
        self.description = label()
        info.addWidget(self.description)
        self.media = QStackedWidget()
        self.media.setFixedHeight(265)
        self.placeholder = label("", "placeholder")
        self.placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.media.addWidget(self.placeholder)
        self.video = QVideoWidget()
        self.media.addWidget(self.video)
        self.player.setVideoOutput(self.video)
        info.addWidget(self.media)
        self.media_note = label("", "subtitle")
        info.addWidget(self.media_note)
        self.controls = QWidget()
        controls = QHBoxLayout(self.controls)
        controls.setContentsMargins(0, 0, 0, 0)
        self.play = self.icon_button(QStyle.StandardPixmap.SP_MediaPlay, "Reproducir o pausar")
        self.play.clicked.connect(self.toggle_play)
        controls.addWidget(self.play)
        self.seek = QSlider(Qt.Orientation.Horizontal)
        self.seek.setRange(0, 0)
        self.seek.setToolTip("Posicion del video")
        self.seek.sliderMoved.connect(self.player.setPosition)
        controls.addWidget(self.seek, 1)
        self.time = label("0:00 / 0:00")
        controls.addWidget(self.time)
        self.loop = QCheckBox("Bucle")
        self.loop.setChecked(True)
        self.loop.toggled.connect(lambda on: self.player.setLoops(QMediaPlayer.Loops.Infinite if on else QMediaPlayer.Loops.Once))
        self.player.setLoops(QMediaPlayer.Loops.Infinite)
        controls.addWidget(self.loop)
        self.mute = self.icon_button(QStyle.StandardPixmap.SP_MediaVolume, "Silenciar")
        self.mute.setCheckable(True)
        self.mute.clicked.connect(self.toggle_mute)
        controls.addWidget(self.mute)
        self.volume = QSlider(Qt.Orientation.Horizontal)
        self.volume.setRange(0, 100)
        self.volume.setFixedWidth(70)
        self.volume.setValue(70)
        self.volume.setAccessibleName("Volumen")
        self.volume.valueChanged.connect(self.change_volume)
        controls.addWidget(self.volume)
        self.audio.mutedChanged.connect(self.sync_audio_controls)
        self.audio.volumeChanged.connect(self.sync_audio_controls)
        self.sync_audio_controls()
        info.addWidget(self.controls)
        self.fields = {}
        for key, heading in [("muscles", "Musculos trabajados"), ("steps", "Como realizarlo"),
                             ("mistakes", "Errores comunes"), ("equipment", "Equipamiento y nivel")]:
            info.addWidget(label(heading, "section"))
            self.fields[key] = label()
            info.addWidget(self.fields[key])
        self.muscle_image = QLabel()
        self.muscle_image.setAlignment(Qt.AlignmentFlag.AlignLeft)
        info.addWidget(self.muscle_image)
        info.addStretch()
        scroll.setWidget(detail)
        self.pages.addWidget(scroll)
        split.addWidget(self.pages)
        split.setSizes([300, 650])
        split.setChildrenCollapsible(False)
        body.addWidget(split, 1)
        outer.addWidget(workspace, 1)
        self.player.positionChanged.connect(self.position_changed)
        self.player.durationChanged.connect(lambda duration: self.seek.setRange(0, duration))
        self.player.playbackStateChanged.connect(self.play_state)
        self.player.errorOccurred.connect(self.media_error)
        self.populate()

    def icon_button(self, icon, tooltip):
        button = QToolButton()
        button.setIcon(self.style().standardIcon(icon))
        button.setToolTip(tooltip)
        button.setAccessibleName(tooltip)
        button.setFixedSize(38, 38)
        return button

    def set_view(self, favorites):
        self.only_favorites = favorites
        self.browse.setChecked(not favorites)
        self.saved.setChecked(favorites)
        self.heading.setText("Favoritos" if favorites else "Ejercicios")
        self.populate()

    def populate(self, *_):
        previous = self.current["id"] if self.current else None
        saved = self.favorites.all()
        self.items.blockSignals(True)
        self.items.clear()
        chosen = None
        for exercise in self.exercises:
            if not matches(exercise, self.search.text()):
                continue
            if self.only_favorites and exercise["id"] not in saved:
                continue
            if self.group.currentIndex() and exercise["group"] != self.group.currentText():
                continue
            if self.equipment.currentIndex() and exercise["equipment"] != self.equipment.currentText():
                continue
            item = QListWidgetItem(exercise["name"] + "\n" + exercise["summary"])
            item.setData(Qt.ItemDataRole.UserRole, exercise)
            item.setSizeHint(QSize(210, 82))
            item.setToolTip(exercise["name"] + " - " + exercise["summary"])
            image = ROOT / exercise["image"]
            if not image.is_file():
                image = image.with_suffix(".png")
            if image.is_file():
                item.setIcon(QIcon(str(image)))
            self.items.addItem(item)
            if exercise["id"] == previous:
                chosen = item
        self.items.blockSignals(False)
        self.count.setText(f"{self.items.count()} ejercicios")
        if self.items.count():
            self.items.setCurrentItem(chosen or self.items.item(0))
        else:
            self.player.stop()
            self.current = None
            self.pages.setCurrentIndex(0)

    def select(self, item, _previous=None):
        if not item:
            return
        self.current = item.data(Qt.ItemDataRole.UserRole)
        exercise = self.current
        self.pages.setCurrentIndex(1)
        self.title.setText(exercise["name"])
        self.description.setText(exercise["description"])
        self.favorite.setChecked(exercise["id"] in self.favorites.all())
        self.favorite.setText("\u2605" if self.favorite.isChecked() else "\u2606")
        self.favorite.setToolTip("Quitar de favoritos" if self.favorite.isChecked() else "Guardar en favoritos")
        self.fields["muscles"].setText(", ".join(exercise["muscles"]))
        for key in ("steps", "mistakes"):
            self.fields[key].setText("\n\n".join(f"{i}. {text}" for i, text in enumerate(exercise[key], 1)))
        self.fields["equipment"].setText(exercise["equipment"] + "  |  " + exercise["level"])
        muscle = QPixmap(str(ROOT / "assets/images/muscles" / (exercise["id"] + ".png")))
        self.muscle_image.setVisible(not muscle.isNull())
        if not muscle.isNull():
            self.muscle_image.setPixmap(muscle.scaled(220, 180, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        self.reload_media()

    def reload_media(self):
        if not self.current:
            return
        self.player.stop()
        self.player.setSource(QUrl())
        self.seek.setRange(0, 0)
        self.time.setText("0:00 / 0:00")
        self.show_image()
        image = ROOT / self.current["image"]
        if not image.is_file():
            image = image.with_suffix(".png")
        if self.items.currentItem():
            self.items.currentItem().setIcon(QIcon(str(image)) if image.is_file() else QIcon())
        path = ROOT / self.current["video"]
        self.controls.setVisible(path.is_file())
        self.media_note.setText("Video pendiente" if not path.is_file() else "")
        if path.is_file():
            self.media.setCurrentIndex(1)
            self.player.setSource(QUrl.fromLocalFile(str(path)))

    def show_image(self):
        self.media.setCurrentIndex(0)
        self.placeholder.clear()
        path = ROOT / self.current["image"]
        if not path.is_file():
            path = path.with_suffix(".png")
        pixmap = QPixmap(str(path))
        if pixmap.isNull():
            self.placeholder.setText("Demostracion pendiente")
        else:
            self.placeholder.setPixmap(pixmap.scaled(max(100, self.media.width() - 20), 245,
                                                    Qt.AspectRatioMode.KeepAspectRatio,
                                                    Qt.TransformationMode.SmoothTransformation))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.current and self.media.currentIndex() == 0:
            self.show_image()

    def toggle_favorite(self, enabled):
        if not self.current:
            return
        self.favorites.set(self.current["id"], enabled)
        self.favorite.setText("\u2605" if enabled else "\u2606")
        self.favorite.setToolTip("Quitar de favoritos" if enabled else "Guardar en favoritos")
        if self.only_favorites:
            self.populate()

    def toggle_mute(self):
        if self.audio.isMuted() or self.audio.volume() == 0:
            if self.volume.value() == 0:
                self.volume.setValue(70)
            self.audio.setMuted(False)
        else:
            self.audio.setMuted(True)

    def change_volume(self, value):
        self.audio.setVolume(value / 100)
        if value > 0:
            self.audio.setMuted(False)

    def sync_audio_controls(self, *_):
        silent = self.audio.isMuted() or self.audio.volume() == 0
        self.mute.setChecked(silent)
        icon = QStyle.StandardPixmap.SP_MediaVolumeMuted if silent else QStyle.StandardPixmap.SP_MediaVolume
        self.mute.setIcon(self.style().standardIcon(icon))
        action = "Activar sonido" if silent else "Silenciar"
        self.mute.setToolTip(action)
        self.mute.setAccessibleName(action)
        self.volume.setToolTip(f"Volumen: {round(self.audio.volume() * 100)}%")

    def toggle_play(self):
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
        else:
            self.player.play()

    def play_state(self, state):
        icon = QStyle.StandardPixmap.SP_MediaPause if state == QMediaPlayer.PlaybackState.PlayingState else QStyle.StandardPixmap.SP_MediaPlay
        self.play.setIcon(self.style().standardIcon(icon))

    def position_changed(self, position):
        if not self.seek.isSliderDown():
            self.seek.setValue(position)
        def clock(ms):
            seconds = ms // 1000
            return f"{seconds // 60}:{seconds % 60:02}"
        self.time.setText(f"{clock(position)} / {clock(self.player.duration())}")

    def media_error(self, _error, message):
        if not self.current or self.player.source().isEmpty():
            return
        self.player.stop()
        self.video.setFullScreen(False)
        self.show_image()
        self.controls.hide()
        self.media_note.setText("No se pudo reproducir el video.")
        self.media_note.setToolTip(message)

    def closeEvent(self, event):
        self.player.stop()
        self.video.setFullScreen(False)
        self.favorites.close()
        super().closeEvent(event)


def main():
    app = QApplication(sys.argv)
    app.setOrganizationName("QhapaqFit")
    app.setApplicationName("QhapaqFit")
    app.setStyle("Fusion")
    app.setStyleSheet(STYLE)
    try:
        window = Window()
    except (OSError, ValueError, KeyError) as error:
        QMessageBox.critical(None, "QhapaqFit", f"No se pudo abrir el catalogo:\n{error}")
        return 1
    window.show()
    return app.exec()
