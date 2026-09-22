import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPixmap, QColor
from qhapaqfit.app import STYLE, Window
from qhapaqfit.catalog import Favorites, load_catalog, matches


class CatalogTests(unittest.TestCase):
    def test_catalog_and_accent_insensitive_search(self):
        catalog = load_catalog()
        self.assertEqual(len(catalog), 5)
        self.assertTrue(matches(catalog[0], "cuádriceps squat"))
        self.assertFalse(matches(catalog[0], "mancuernas"))

    def test_favorites_persist_and_remove(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "favorites.sqlite3"
            db = Favorites(path)
            db.set("sentadilla", True)
            db.set("sentadilla", True)
            db.close()
            db = Favorites(path)
            self.assertEqual(db.all(), {"sentadilla"})
            db.set("sentadilla", False)
            self.assertEqual(db.all(), set())
            db.close()


class WindowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.app.setStyle("Fusion")
        cls.app.setStyleSheet(STYLE)

    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.window = Window(Path(self.folder.name) / "favorites.sqlite3")
        self.window.show()
        self.app.processEvents()

    def tearDown(self):
        self.window.close()
        self.app.processEvents()
        self.folder.cleanup()

    def test_search_filter_and_empty_recovery(self):
        self.assertEqual(self.window.items.count(), 5)
        self.window.search.setText("romanian")
        self.assertEqual(self.window.items.count(), 1)
        self.assertEqual(self.window.current["id"], "peso_muerto_rumano")
        self.window.search.setText("no-such-exercise")
        self.assertEqual(self.window.pages.currentIndex(), 0)
        self.window.search.clear()
        self.window.equipment.setCurrentText("Mancuernas")
        self.assertEqual(self.window.items.count(), 1)
        self.assertEqual(self.window.pages.currentIndex(), 1)

    def test_favorites_view_removal(self):
        self.window.favorite.click()
        self.window.set_view(True)
        self.assertEqual(self.window.items.count(), 1)
        self.window.favorite.click()
        self.assertEqual(self.window.items.count(), 0)
        self.window.set_view(False)
        self.assertEqual(self.window.items.count(), 5)

    def test_missing_media_and_resizing(self):
        self.assertEqual(self.window.media.currentIndex(), 0)
        self.assertTrue(self.window.controls.isHidden())
        for width, height in [(1240, 820), (860, 600)]:
            self.window.resize(width, height)
            self.app.processEvents()
            self.assertGreater(self.window.media.width(), 200)
            self.assertEqual(self.window.title.text(), "Sentadilla")
        self.window.refresh.click()
        self.assertEqual(self.window.media_note.text(), "Video pendiente")

    def test_image_added_after_opening_is_loaded_on_refresh(self):
        image = Path(self.folder.name) / "exercise.png"
        self.window.current = dict(self.window.current, image=str(image))
        self.window.reload_media()
        self.assertEqual(self.window.placeholder.text(), "Demostracion pendiente")
        pixmap = QPixmap(100, 80)
        pixmap.fill(QColor("teal"))
        pixmap.save(str(image))
        self.window.refresh.click()
        self.assertFalse(self.window.placeholder.pixmap().isNull())
        self.assertTrue(self.window.controls.isHidden())


if __name__ == "__main__":
    unittest.main()
