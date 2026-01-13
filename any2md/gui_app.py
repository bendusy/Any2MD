import sys
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QFileDialog,
    QTextEdit,
    QProgressBar,
    QMessageBox,
    QFrame,
    QCheckBox,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QStandardPaths, QUrl
from PyQt6.QtGui import QDragEnterEvent, QDropEvent
from PyQt6.QtGui import QDesktopServices

from .converter import Any2MDConverter, ConvertResult
from .unzipper import Unzipper


class ConvertWorker(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(
        self,
        input_path: Path,
        output_path: Path,
        merge_to_single: bool,
        merged_filename: str,
    ):
        super().__init__()
        self.input_path = input_path
        self.output_path = output_path
        self.merge_to_single = merge_to_single
        self.merged_filename = merged_filename

    def run(self):
        try:
            converter = Any2MDConverter()
            results = []
            base_dir = self.input_path

            if self.input_path.suffix.lower() == ".zip":
                self.progress.emit("解压 ZIP 文件...")
                with Unzipper() as unzipper:
                    extracted = unzipper.extract_recursive(self.input_path)
                    self.progress.emit("转换文件...")
                    base_dir = extracted
                    results = converter.convert_directory(extracted, self.output_path)
            elif self.input_path.is_dir():
                self.progress.emit("转换文件夹...")
                results = converter.convert_directory(self.input_path, self.output_path)
            else:
                self.progress.emit("转换文件...")
                results = [converter.convert_file(self.input_path, self.output_path)]

            if self.merge_to_single:
                self.progress.emit("合并为单个 Markdown...")
                merged_name = (self.merged_filename or "").strip() or "Any2MD-合并.md"
                if not merged_name.lower().endswith(".md"):
                    merged_name += ".md"
                merged_path = self.output_path / merged_name
                converter.write_merged_markdown(
                    results=results, merged_path=merged_path, base_dir=base_dir
                )

            self.finished.emit(results)
        except Exception as e:
            self.error.emit(str(e))


class DropArea(QFrame):
    pathDropped = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Sunken)
        self.setMinimumHeight(150)
        self.setStyleSheet("""
            DropArea {
                border: 2px dashed #aaa;
                border-radius: 10px;
                background-color: #f9f9f9;
            }
            DropArea:hover {
                border-color: #666;
                background-color: #f0f0f0;
            }
        """)

        layout = QVBoxLayout(self)
        self.label = QLabel("拖拽文件/文件夹/ZIP 到这里\n或点击选择")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("font-size: 16px; color: #666;")
        layout.addWidget(self.label)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet("""
                DropArea {
                    border: 2px dashed #4CAF50;
                    border-radius: 10px;
                    background-color: #e8f5e9;
                }
            """)

    def dragLeaveEvent(self, event):
        self.setStyleSheet("""
            DropArea {
                border: 2px dashed #aaa;
                border-radius: 10px;
                background-color: #f9f9f9;
            }
        """)

    def dropEvent(self, event: QDropEvent):
        self.setStyleSheet("""
            DropArea {
                border: 2px dashed #aaa;
                border-radius: 10px;
                background-color: #f9f9f9;
            }
        """)
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            self.pathDropped.emit(path)

    def mousePressEvent(self, event):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "选择文件",
            "",
            "所有支持的文件 (*.pdf *.docx *.pptx *.xlsx *.html *.zip);;所有文件 (*)",
        )
        if path:
            self.pathDropped.emit(path)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Any2MD - 批量转换为 Markdown")
        self.setMinimumSize(600, 500)
        self.worker: Optional[ConvertWorker] = None
        self.setup_ui()

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        self.drop_area = DropArea()
        self.drop_area.pathDropped.connect(self.on_path_dropped)
        layout.addWidget(self.drop_area)

        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("输入:"))
        self.input_edit = QLineEdit()
        self.input_edit.setPlaceholderText("文件/文件夹/ZIP 路径")
        input_layout.addWidget(self.input_edit)
        self.browse_input_btn = QPushButton("浏览")
        self.browse_input_btn.clicked.connect(self.browse_input)
        input_layout.addWidget(self.browse_input_btn)
        layout.addLayout(input_layout)

        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("输出:"))
        self.output_edit = QLineEdit(str(self._default_output_dir()))
        output_layout.addWidget(self.output_edit)
        self.browse_output_btn = QPushButton("浏览")
        self.browse_output_btn.clicked.connect(self.browse_output)
        output_layout.addWidget(self.browse_output_btn)

        self.open_output_btn = QPushButton("打开")
        self.open_output_btn.clicked.connect(self.open_output_dir)
        output_layout.addWidget(self.open_output_btn)
        layout.addLayout(output_layout)

        merge_layout = QHBoxLayout()
        self.merge_checkbox = QCheckBox("合并为单个 Markdown（便于上传到 AI）")
        self.merge_checkbox.setChecked(True)
        self.merge_checkbox.stateChanged.connect(self.on_merge_toggle)
        merge_layout.addWidget(self.merge_checkbox)

        merge_layout.addWidget(QLabel("文件名:"))
        self.merge_name_edit = QLineEdit("Any2MD-合并.md")
        merge_layout.addWidget(self.merge_name_edit)
        layout.addLayout(merge_layout)

        self.convert_btn = QPushButton("开始转换")
        self.convert_btn.setMinimumHeight(40)
        self.convert_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.convert_btn.clicked.connect(self.start_convert)
        layout.addWidget(self.convert_btn)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        layout.addWidget(self.log_text)

    def _default_output_dir(self) -> Path:
        desktop = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.DesktopLocation
        )
        if desktop:
            p = Path(desktop) / "Any2MD-output"
            return p
        documents = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.DocumentsLocation
        )
        if documents:
            p = Path(documents) / "Any2MD-output"
            return p
        return Path.home() / "Any2MD-output"

    def on_merge_toggle(self):
        enabled = self.merge_checkbox.isChecked()
        self.merge_name_edit.setEnabled(enabled)

    def on_path_dropped(self, path: str):
        self.input_edit.setText(path)
        self.drop_area.label.setText(f"已选择: {Path(path).name}")

    def browse_input(self):
        path = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if path:
            self.input_edit.setText(path)

    def browse_output(self):
        path = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if path:
            self.output_edit.setText(path)

    def open_output_dir(self):
        output_path = Path(self.output_edit.text().strip() or str(self._default_output_dir()))
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(output_path)))

    def start_convert(self):
        input_path = Path(self.input_edit.text().strip())
        output_path = Path(self.output_edit.text().strip())
        merge_to_single = self.merge_checkbox.isChecked()
        merged_filename = self.merge_name_edit.text().strip()

        if not input_path or not input_path.exists():
            QMessageBox.warning(self, "错误", "请选择有效的输入路径")
            return

        self.convert_btn.setEnabled(False)
        self.progress_bar.show()
        self.log_text.clear()

        self.worker = ConvertWorker(
            input_path=input_path,
            output_path=output_path,
            merge_to_single=merge_to_single,
            merged_filename=merged_filename,
        )
        self.worker.progress.connect(self.on_progress)
        self.worker.finished.connect(self.on_finished)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    def on_progress(self, message: str):
        self.status_label.setText(message)
        self.log_text.append(message)

    def on_finished(self, results: list[ConvertResult]):
        self.progress_bar.hide()
        self.convert_btn.setEnabled(True)

        success = sum(1 for r in results if r.success)
        fail = len(results) - success

        self.status_label.setText(f"完成！成功: {success}, 失败: {fail}")

        for r in results:
            if r.success:
                self.log_text.append(f"✓ {r.input_path.name} → {r.output_path}")
            else:
                self.log_text.append(f"✗ {r.input_path.name}: {r.error}")

        if fail == 0:
            QMessageBox.information(self, "完成", f"成功转换 {success} 个文件！")
        else:
            QMessageBox.warning(self, "完成", f"成功: {success}, 失败: {fail}")

    def on_error(self, error: str):
        self.progress_bar.hide()
        self.convert_btn.setEnabled(True)
        self.status_label.setText(f"错误: {error}")
        QMessageBox.critical(self, "错误", error)


def run_gui():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run_gui()
