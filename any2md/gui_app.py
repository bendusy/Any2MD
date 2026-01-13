import sys
from pathlib import Path
from typing import Optional, List, Dict
import os

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
    QProgressBar,
    QMessageBox,
    QFrame,
    QCheckBox,
    QGraphicsDropShadowEffect,
    QStackedWidget,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QDialog,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QUrl, QPoint
from PyQt6.QtGui import (
    QDragEnterEvent,
    QDropEvent,
    QColor,
    QDesktopServices,
    QBrush,
    QAction,
)

from .converter import Any2MDConverter, ConvertResult


# --- 2025 Design System: "Morning Light" ---


class MorningTheme:
    # Fresh, airy, welcoming
    BG_MAIN = "#ffffff"  # Pure white
    BG_PANEL = "#f5f5f7"  # macOS App/Sidebar gray
    BG_INPUT = "#ffffff"

    # Modern macOS-like Accents
    ACCENT_PRIMARY = "#007aff"  # macOS Blue
    ACCENT_HOVER = "#0062cc"
    ACCENT_SUBTLE = "#eef7ff"  # Very light blue for backgrounds

    # Text - Optimally contrast
    TEXT_PRIMARY = "#1d1d1f"  # Almost black
    TEXT_SECONDARY = "#86868b"  # Neutral gray
    TEXT_MUTED = "#6e6e73"

    # Borders
    BORDER_LIGHT = "#d2d2d7"
    BORDER_FOCUS = "#007aff"

    # Status
    SUCCESS = "#34c759"
    ERROR = "#ff3b30"
    WARNING = "#ffcc00"
    PROCESSING = "#007aff"

    FONT_FAMILY = '-apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", "Segoe UI", Roboto, sans-serif'

    STYLESHEET = f"""
        QMainWindow {{
            background-color: {BG_MAIN};
        }}
        QDialog {{
            background-color: {BG_MAIN};
        }}
        QWidget {{
            background-color: transparent;
            color: {TEXT_PRIMARY};
            font-family: {FONT_FAMILY};
            font-size: 14px;
        }}
        
        /* Typography */
        QLabel[role="heading"] {{
            font-size: 24px;
            font-weight: 600;
            color: {TEXT_PRIMARY};
            margin-bottom: 5px;
        }}
        QLabel[role="subheading"] {{
            font-size: 14px;
            color: {TEXT_SECONDARY};
            font-weight: 400;
        }}
        QLabel[role="label"] {{
            color: {TEXT_PRIMARY};
            font-size: 13px;
            font-weight: 600;
            margin-bottom: 4px;
        }}
        QLabel[role="helper"] {{
            color: {TEXT_SECONDARY};
            font-size: 12px;
            margin-top: 2px;
        }}
        QLabel[role="step-number"] {{
            background-color: {BG_PANEL};
            color: {ACCENT_PRIMARY};
            font-weight: bold;
            border-radius: 12px;
            min-width: 24px;
            max-width: 24px;
            min-height: 24px;
            max-height: 24px;
            qproperty-alignment: AlignCenter;
        }}

        /* Cards & Panels */
        QFrame[class="panel"] {{
            background-color: {BG_PANEL};
            border-left: 1px solid {BORDER_LIGHT};
        }}
        QFrame[class="card"] {{
            background-color: {BG_INPUT};
            border: 1px solid {BORDER_LIGHT};
            border-radius: 10px;
        }}

        /* Inputs */
        QLineEdit {{
            background-color: {BG_INPUT};
            border: 1px solid {BORDER_LIGHT};
            border-radius: 8px;
            padding: 10px;
            color: {TEXT_PRIMARY};
            font-size: 14px;
        }}
        QLineEdit:focus {{
            border: 1px solid {BORDER_FOCUS};
            background-color: {BG_INPUT};
        }}
        QLineEdit[readOnly="true"] {{
            color: {TEXT_SECONDARY};
            background: {BG_PANEL};
            border: none;
        }}
        
        /* List Widget */
        QListWidget {{
            background-color: {BG_INPUT};
            border: 1px solid {BORDER_LIGHT};
            border-radius: 10px;
            outline: none;
        }}
        QListWidget::item {{
            padding: 8px;
            border-bottom: 1px solid {BG_PANEL};
            color: {TEXT_PRIMARY};
        }}
        QListWidget::item:selected {{
            background-color: {ACCENT_SUBTLE};
            color: {ACCENT_PRIMARY};
            border: none;
        }}

        /* Buttons */
        QPushButton {{
            background-color: {BG_INPUT};
            border: 1px solid {BORDER_LIGHT};
            border-radius: 8px;
            padding: 8px 16px;
            color: {TEXT_PRIMARY};
            font-weight: 500;
        }}
        QPushButton:hover {{
            background-color: #f2f2f5;
            border-color: #b5b5b5;
        }}
        
        QPushButton[role="primary"] {{
            background-color: {ACCENT_PRIMARY};
            border: 1px solid {ACCENT_PRIMARY};
            color: white;
            font-weight: 600;
            font-size: 15px;
            border-radius: 10px;
        }}
        QPushButton[role="primary"]:hover {{
            background-color: {ACCENT_HOVER};
            border-color: {ACCENT_HOVER};
        }}
        QPushButton[role="primary"]:pressed {{
            background-color: #0051a8;
        }}
        QPushButton[role="primary"]:disabled {{
            background-color: {BORDER_LIGHT};
            border-color: {BORDER_LIGHT};
            color: rgba(255,255,255,0.7);
        }}
        
        /* Menu */
        QMenu {{
            background-color: {BG_INPUT};
            border: 1px solid {BORDER_LIGHT};
            border-radius: 8px;
            padding: 5px;
        }}
        QMenu::item {{
            padding: 8px 20px;
            border-radius: 4px;
            color: {TEXT_PRIMARY};
        }}
        QMenu::item:selected {{
            background-color: {ACCENT_PRIMARY};
            color: white;
        }}

        /* Checkbox */
        QCheckBox {{
            spacing: 12px;
            color: {TEXT_PRIMARY};
            font-weight: 500;
        }}
        QCheckBox::indicator {{
            width: 20px;
            height: 20px;
            border-radius: 6px;
            border: 1px solid {BORDER_LIGHT};
            background-color: {BG_INPUT};
        }}
        QCheckBox::indicator:checked {{
            background-color: {ACCENT_PRIMARY};
            border-color: {ACCENT_PRIMARY};
        }}
        
        /* Table */
        QTableWidget {{
            background-color: {BG_INPUT};
            border: 1px solid {BORDER_LIGHT};
            gridline-color: {BG_PANEL};
            selection-background-color: {ACCENT_SUBTLE};
            selection-color: {TEXT_PRIMARY};
        }}
        QHeaderView::section {{
            background-color: {BG_PANEL};
            padding: 6px;
            border: none;
            border-bottom: 1px solid {BORDER_LIGHT};
            font-weight: 600;
        }}

        /* Logs */
        QTextEdit {{
            background-color: {BG_INPUT};
            border: 1px solid {BORDER_LIGHT};
            border-radius: 8px;
            padding: 8px;
            color: {TEXT_MUTED};
            font-family: "Menlo", "Consolas", monospace;
            font-size: 12px;
            line-height: 1.4;
        }}
    """


# --- Helper Logic ---


class FileItemData:
    def __init__(self, path: Path, relative_to: Optional[Path] = None):
        self.path = path
        self.relative_to = relative_to
        self.status = "pending"  # pending, processing, success, error
        self.error_msg = ""

    @property
    def display_name(self):
        return self.path.name

    @property
    def location_hint(self):
        if self.relative_to:
            try:
                rel = self.path.parent.relative_to(self.relative_to)
                if str(rel) == ".":
                    return ""
                return str(rel)
            except ValueError:
                pass
        return str(self.path.parent)


class PreScanner(QThread):
    files_found = pyqtSignal(list)
    finished_scan = pyqtSignal()

    def __init__(self, raw_paths: List[Path]):
        super().__init__()
        self.raw_paths = raw_paths
        self._stop = False

    def stop(self):
        self._stop = True

    def run(self):
        found = []
        # Support extensions from Any2MDConverter (mocked list here as we don't import internals of converter easily)
        # Assuming we know typical extensions
        valid_exts = Any2MDConverter.SUPPORTED_EXTENSIONS

        def scan_dir(d: Path, root: Path):
            try:
                for entry in os.scandir(d):
                    if self._stop:
                        return
                    p = Path(entry.path)
                    if entry.is_dir() and not entry.name.startswith("."):
                        scan_dir(p, root)
                    elif entry.is_file():
                        if p.suffix.lower() in valid_exts or p.suffix.lower() == ".zip":
                            found.append(FileItemData(p, relative_to=root))
            except PermissionError:
                pass

        for path in self.raw_paths:
            if self._stop:
                break
            if path.is_file():
                found.append(FileItemData(path, relative_to=path.parent))
            elif path.is_dir():
                scan_dir(path, path)

        self.files_found.emit(found)
        self.finished_scan.emit()


class ConvertWorker(QThread):
    file_started = pyqtSignal(str)  # path string
    file_finished = pyqtSignal(str, bool, str)  # path string, success, error_msg
    progress_global = pyqtSignal(int, int)  # current, total
    finished_all = pyqtSignal(list)  # list[ConvertResult]
    error_critical = pyqtSignal(str)

    def __init__(
        self, items: List[FileItemData], output_path: Path, merge: bool, merge_name: str
    ):
        super().__init__()
        self.items = items
        self.output_path = output_path
        self.merge = merge
        self.merge_name = merge_name
        self._stop = False

    def stop(self):
        self._stop = True

    def run(self):
        try:
            converter = Any2MDConverter()
            results = []

            total = len(self.items)

            # For merge base dir, verify logic
            if self.items:
                # Find common ancestor? Simplification: use the relative_to of the first item main request?
                # Actually, Converter's merge needs relative paths.
                # We can't easily guess the "session root" if mixed files are dropped.
                # So we pass None as base_dir to write_merged_markdown to disable structure preservation inside merge?
                # OR we try to determine common path.
                try:
                    common_path = Path(
                        os.path.commonpath([str(i.path.parent) for i in self.items])
                    )
                except Exception:
                    common_path = None
            else:
                common_path = None

            for i, item in enumerate(self.items):
                if self._stop:
                    break

                self.progress_global.emit(i + 1, total)
                self.file_started.emit(str(item.path))

                try:
                    # Logic needs to handle Zips?
                    # If item is a zip, we should probably handle it specially or let converter handle it.
                    # Current Converter `convert_file` doesn't auto-unpack zips unless using `convert_directory` logic.
                    # But for now let's assume `convert_file` handles simple files.
                    # If it's a zip and user wants to convert content, we might have complexity here.
                    # Simplification: If zip, we just ignore for now or treat as file if backend supports it.
                    # Assuming backend supports generic file conversion.

                    if item.path.suffix.lower() == ".zip":
                        # If it's a zip, extracting it might generate MULTIPLE results from ONE item.
                        # This complicates 1-1 mapping in list.
                        # For V5, lets stick to direct conversion. If Any2MDConverter supports zip->folder conversion, strict 1-1.
                        pass

                    res = converter.convert_file(item.path, self.output_path)

                    # Update status
                    if res.success:
                        self.file_finished.emit(str(item.path), True, "")
                    else:
                        self.file_finished.emit(
                            str(item.path), False, res.error or "Unknown error"
                        )

                    results.append(res)

                except Exception as e:
                    self.file_finished.emit(str(item.path), False, str(e))
                    # Mock result for exception
                    results.append(
                        ConvertResult(
                            success=False,
                            input_path=item.path,
                            output_path=None,
                            error=str(e),
                        )
                    )

            if self.merge and results and not self._stop:
                try:
                    name = (self.merge_name or "").strip() or "Any2MD-Merged.md"
                    if not name.lower().endswith(".md"):
                        name += ".md"
                    converter.write_merged_markdown(
                        results, self.output_path / name, common_path
                    )
                except Exception as e:
                    print(f"Merge failed: {e}")

            self.finished_all.emit(results)
        except Exception as e:
            self.error_critical.emit(str(e))


class ResultDialog(QDialog):
    def __init__(self, parent, results: List[ConvertResult]):
        super().__init__(parent)
        self.setWindowTitle("转换报告")
        self.resize(600, 400)
        self.setStyleSheet(MorningTheme.STYLESHEET)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        success_count = sum(1 for r in results if r.success)
        fail_count = len(results) - success_count

        # Summary
        summary = QLabel(f"处理完成: {success_count} 成功, {fail_count} 失败")
        summary.setStyleSheet(
            f"font-size: 16px; font-weight: 600; color: {'red' if fail_count > 0 else MorningTheme.SUCCESS}"
        )
        layout.addWidget(summary)

        # Details Table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["文件", "状态", "详情"])
        self.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self.table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.Stretch
        )
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        self.table.setRowCount(len(results))
        for i, res in enumerate(results):
            # Name
            name_item = QTableWidgetItem(res.input_path.name)
            self.table.setItem(i, 0, name_item)

            # Status
            status_str = "成功" if res.success else "失败"
            status_item = QTableWidgetItem(status_str)
            if res.success:
                status_item.setForeground(QBrush(QColor(MorningTheme.SUCCESS)))
            else:
                status_item.setForeground(QBrush(QColor(MorningTheme.ERROR)))
            self.table.setItem(i, 1, status_item)

            # Details
            msg = str(res.output_path) if res.success else res.error
            msg_item = QTableWidgetItem(msg)
            msg_item.setToolTip(msg)
            self.table.setItem(i, 2, msg_item)

        layout.addWidget(self.table)

        # Buttons
        btn_box = QHBoxLayout()
        btn_copy = QPushButton("复制错误信息")
        btn_copy.clicked.connect(self.copy_errors)
        btn_copy.setVisible(fail_count > 0)

        btn_close = QPushButton("关闭")
        btn_close.setProperty("role", "primary")
        btn_close.clicked.connect(self.accept)

        btn_box.addStretch()
        btn_box.addWidget(btn_copy)
        btn_box.addWidget(btn_close)

        layout.addLayout(btn_box)

    def copy_errors(self):
        # Extract failures
        lines = []
        for row in range(self.table.rowCount()):
            if self.table.item(row, 1).text() == "失败":
                name = self.table.item(row, 0).text()
                err = self.table.item(row, 2).text()
                lines.append(f"{name}: {err}")

        if lines:
            QApplication.clipboard().setText("\n".join(lines))
            QMessageBox.information(self, "复制成功", "错误信息已复制到剪贴板。")


class InstructionStep(QWidget):
    def __init__(self, number: str, text: str):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 5)
        layout.setSpacing(15)

        num_label = QLabel(number)
        num_label.setProperty("role", "step-number")

        text_label = QLabel(text)
        text_label.setStyleSheet(
            f"color: {MorningTheme.TEXT_SECONDARY}; font-size: 14px;"
        )
        text_label.setWordWrap(True)

        layout.addWidget(num_label)
        layout.addWidget(text_label)
        layout.addStretch()


class DropZone(QFrame):
    rawPathsDropped = pyqtSignal(list)  # Emits list[Path]

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setFrameShape(QFrame.Shape.NoFrame)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 40)
        self.layout.setSpacing(10)

        # Spacer
        self.layout.addStretch()

        # Center Content
        center_container = QWidget()
        center_layout = QVBoxLayout(center_container)
        center_layout.setSpacing(20)
        center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.icon_label = QLabel("📥")
        self.icon_label.setStyleSheet(
            f"font-size: 72px; color: {MorningTheme.BORDER_LIGHT};"
        )
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.addWidget(self.icon_label)

        self.main_text = QLabel("拖入文件或文件夹")
        self.main_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_text.setStyleSheet(
            f"font-size: 20px; font-weight: 600; color: {MorningTheme.TEXT_PRIMARY};"
        )
        center_layout.addWidget(self.main_text)

        support_text = QLabel("程序将自动扫描文件夹内的所有可转换文档")
        support_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        support_text.setStyleSheet(
            f"color: {MorningTheme.TEXT_SECONDARY}; font-size: 13px;"
        )
        center_layout.addWidget(support_text)

        self.layout.addWidget(center_container)

        self.layout.addStretch()

        # Bottom Instructions
        instr_group = QWidget()
        instr_layout = QVBoxLayout(instr_group)
        instr_layout.setSpacing(5)
        instr_layout.addWidget(InstructionStep("1", "点击添加或直接拖入文件/文件夹"))
        instr_layout.addWidget(InstructionStep("2", "程序会自动解包文件夹结构"))
        instr_layout.addWidget(InstructionStep("3", "确认清单后开始转换"))

        self.layout.addWidget(instr_group)
        self.layout.addSpacing(20)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self._set_active(True)

    def dragLeaveEvent(self, event):
        self._set_active(False)

    def dropEvent(self, event: QDropEvent):
        self._set_active(False)
        urls = event.mimeData().urls()
        if urls:
            paths = [u.toLocalFile() for u in urls]
            self.rawPathsDropped.emit([Path(p) for p in paths])

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.show_context_menu(event.globalPosition().toPoint())

    def show_context_menu(self, pos):
        menu = QMenu(self)

        action_file = QAction("📄 选择文件 (支持多选)", self)
        action_file.triggered.connect(self.action_select_files)

        action_dir = QAction("📁 选择文件夹", self)
        action_dir.triggered.connect(self.action_select_dir)

        menu.addAction(action_file)
        menu.addAction(action_dir)

        menu.exec(pos)

    def action_select_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "选择文件",
            "",
            "所有支持的文件 (*.pdf *.doc *.docx *.ppt *.pptx *.xls *.xlsx *.html *.htm *.txt *.rtf *.zip);;所有文件 (*)",
        )
        if files:
            self.rawPathsDropped.emit([Path(p) for p in files])

    def action_select_dir(self):
        path = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if path:
            self.rawPathsDropped.emit([Path(path)])

    def _set_active(self, active: bool):
        if active:
            self.setStyleSheet(f"background-color: {MorningTheme.ACCENT_SUBTLE};")
            self.icon_label.setStyleSheet(
                f"font-size: 80px; color: {MorningTheme.ACCENT_PRIMARY};"
            )
            self.main_text.setText("释放以添加")
            self.main_text.setStyleSheet(
                f"font-size: 22px; font-weight: 700; color: {MorningTheme.ACCENT_PRIMARY};"
            )
        else:
            self.setStyleSheet("background-color: transparent;")
            self.icon_label.setStyleSheet(
                f"font-size: 72px; color: {MorningTheme.BORDER_LIGHT};"
            )
            self.main_text.setText("拖入文件或文件夹")
            self.main_text.setStyleSheet(
                f"font-size: 20px; font-weight: 600; color: {MorningTheme.TEXT_PRIMARY};"
            )


class ZenWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Any2MD - 文档转 Markdown 工具")
        self.resize(1100, 720)
        self.setStyleSheet(MorningTheme.STYLESHEET)

        # State
        self.file_items: List[FileItemData] = []
        self.map_path_to_item: Dict[str, QListWidgetItem] = {}

        self.setup_ui()

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- LEFT PANEL (45%) ---
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # File Info Overlay (Initially Hidden)
        self.file_list_panel = QWidget()
        self.file_list_panel.hide()
        flp_layout = QVBoxLayout(self.file_list_panel)
        flp_layout.setContentsMargins(20, 40, 20, 40)
        flp_layout.setSpacing(15)

        header_row = QHBoxLayout()
        self.flp_title = QLabel("已就绪 0 个文件")
        self.flp_title.setStyleSheet(
            f"font-size: 18px; font-weight: 600; color: {MorningTheme.TEXT_PRIMARY};"
        )

        self.flp_add = QPushButton("添加...")
        self.flp_add.setCursor(Qt.CursorShape.PointingHandCursor)
        self.flp_add.clicked.connect(self.show_add_menu)
        self.flp_add.setFixedWidth(80)

        self.flp_clear = QPushButton("清空")
        self.flp_clear.setCursor(Qt.CursorShape.PointingHandCursor)
        self.flp_clear.clicked.connect(self.reset_files)
        self.flp_clear.setFixedWidth(60)

        header_row.addWidget(self.flp_title)
        header_row.addStretch()
        header_row.addWidget(self.flp_add)
        header_row.addWidget(self.flp_clear)

        self.file_list_widget = QListWidget()
        self.file_list_widget.setSelectionMode(
            QListWidget.SelectionMode.ExtendedSelection
        )
        self.file_list_widget.setStyleSheet("""
            QListWidget {{
                font-size: 13px;
            }}
        """)

        flp_layout.addLayout(header_row)
        flp_layout.addWidget(self.file_list_widget)

        self.stack = QStackedWidget()
        self.drop_zone = DropZone()
        self.drop_zone.rawPathsDropped.connect(self.start_prescan)

        self.scan_loading = QLabel("正在扫描文件夹内容...")
        self.scan_loading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scan_loading.setStyleSheet(
            f"font-size: 16px; color: {MorningTheme.TEXT_SECONDARY};"
        )

        self.stack.addWidget(self.drop_zone)
        self.stack.addWidget(self.scan_loading)
        self.stack.addWidget(self.file_list_panel)

        left_layout.addWidget(self.stack)
        main_layout.addWidget(left_widget, 45)

        # --- RIGHT PANEL (55%) ---
        right_panel = QFrame()
        right_panel.setProperty("class", "panel")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(40, 50, 40, 40)
        right_layout.setSpacing(25)

        # Header
        header = QWidget()
        h_layout = QVBoxLayout(header)
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.setSpacing(2)

        h_title = QLabel("转换设置")
        h_title.setProperty("role", "heading")
        h_sub = QLabel("自定义您的文档处理方式。")
        h_sub.setProperty("role", "subheading")

        h_layout.addWidget(h_title)
        h_layout.addWidget(h_sub)
        right_layout.addWidget(header)

        right_layout.addSpacing(10)

        # Settings
        # 1. Output Folder
        out_card = QFrame()
        out_card.setProperty("class", "card")
        og_layout = QVBoxLayout(out_card)
        og_layout.setContentsMargins(20, 20, 20, 20)
        og_layout.setSpacing(10)

        lbl_out = QLabel("输出目录")
        lbl_out.setProperty("role", "label")
        og_layout.addWidget(lbl_out)

        out_row = QHBoxLayout()
        self.out_edit = QLineEdit(str(self._default_output_dir()))
        self.out_edit.setReadOnly(True)

        btn_browse = QPushButton("浏览...")
        btn_browse.clicked.connect(self.browse_output)

        out_row.addWidget(self.out_edit)
        out_row.addWidget(btn_browse)
        og_layout.addLayout(out_row)

        lbl_help_out = QLabel("转换后的 Markdown 文件将保存在此处。")
        lbl_help_out.setProperty("role", "helper")
        og_layout.addWidget(lbl_help_out)

        right_layout.addWidget(out_card)

        # 2. Merge Option
        merge_card = QFrame()
        merge_card.setProperty("class", "card")
        mc_layout = QVBoxLayout(merge_card)
        mc_layout.setContentsMargins(20, 20, 20, 20)
        mc_layout.setSpacing(10)

        self.merge_check = QCheckBox("合并为 AI 知识库文件")
        self.merge_check.setChecked(True)
        self.merge_check.stateChanged.connect(self.toggle_merge)

        self.merge_input = QLineEdit("Batch-KnowledgeBase.md")
        self.merge_input.setPlaceholderText("例如: Project-Docs.md")

        lbl_help_merge = QLabel(
            "将所有文档整合到一个 Markdown 文件中，非常适合上传给 Claude 或 ChatGPT 进行分析。"
        )
        lbl_help_merge.setProperty("role", "helper")
        lbl_help_merge.setWordWrap(True)

        mc_layout.addWidget(self.merge_check)
        mc_layout.addWidget(self.merge_input)
        mc_layout.addWidget(lbl_help_merge)

        right_layout.addWidget(merge_card)

        right_layout.addStretch()

        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{ background: {MorningTheme.BORDER_LIGHT}; border-radius: 3px; }}
            QProgressBar::chunk {{ background: {MorningTheme.ACCENT_PRIMARY}; border-radius: 3px; }}
        """)
        self.progress_bar.hide()
        right_layout.addWidget(self.progress_bar)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet(
            f"color: {MorningTheme.TEXT_SECONDARY}; font-size: 13px;"
        )
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(self.status_label)

        # Action Button
        self.convert_btn = QPushButton("开始转换")
        self.convert_btn.setProperty("role", "primary")
        self.convert_btn.setFixedHeight(50)
        self.convert_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.convert_btn.clicked.connect(self.start_convert)

        # Soft Shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 122, 255, 60))
        shadow.setOffset(0, 8)
        self.convert_btn.setGraphicsEffect(shadow)

        right_layout.addWidget(self.convert_btn)

        main_layout.addWidget(right_panel, 55)

    def _default_output_dir(self) -> Path:
        return Path.home() / "Downloads" / "Any2MD_Output"

    def show_add_menu(self):
        # Programmatically trigger the menu on the add button
        menu = QMenu(self)
        action_file = QAction("📄 添加文件...", self)
        action_file.triggered.connect(lambda: self.drop_zone.action_select_files())
        action_dir = QAction("📁 添加文件夹...", self)
        action_dir.triggered.connect(lambda: self.drop_zone.action_select_dir())
        menu.addAction(action_file)
        menu.addAction(action_dir)

        menu.exec(self.flp_add.mapToGlobal(QPoint(0, self.flp_add.height())))

    def start_prescan(self, raw_paths: list):
        self.stack.setCurrentWidget(self.scan_loading)
        # Disable interaction
        self.drop_zone.setEnabled(False)

        self.scanner = PreScanner(raw_paths)
        self.scanner.files_found.connect(self.on_scan_results)
        self.scanner.finished_scan.connect(self.on_scan_finished)
        self.scanner.start()

    def on_scan_results(self, items: List[FileItemData]):
        # Add to existing items, avoiding strict duplicates by path
        existing_paths = {i.path for i in self.file_items}
        added_count = 0
        for item in items:
            if item.path not in existing_paths:
                self.file_items.append(item)
                self.add_list_item(item)
                added_count += 1

        self.refresh_title()

    def on_scan_finished(self):
        self.drop_zone.setEnabled(True)
        if self.file_items:
            self.stack.setCurrentWidget(self.file_list_panel)
        else:
            self.stack.setCurrentWidget(self.drop_zone)
            if not self.file_items:
                self.status_label.setText("未在文件夹中找到支持的文档")

    def add_list_item(self, item: FileItemData):
        # Format: Icon  Filename  (Relative Path)
        hint = item.location_hint
        if hint:
            text = f"{item.display_name}   ({hint})"
        else:
            text = item.display_name

        icon = "📄"  # Distinction based on suffix?
        suffix = item.path.suffix.lower()
        if suffix in [".pdf"]:
            icon = "📕"
        elif suffix in [".doc", ".docx"]:
            icon = "📘"
        elif suffix in [".ppt", ".pptx"]:
            icon = "📙"
        elif suffix in [".xls", ".xlsx"]:
            icon = "📗"
        elif suffix == ".zip":
            icon = "📦"

        list_item = QListWidgetItem(f"{icon}  {text}")
        list_item.setData(Qt.ItemDataRole.UserRole, str(item.path))
        self.file_list_widget.addItem(list_item)
        self.map_path_to_item[str(item.path)] = list_item

    def refresh_title(self):
        count = len(self.file_items)
        self.flp_title.setText(f"已就绪 {count} 个文件")

        if count > 1:
            self.merge_check.setChecked(True)
            self.merge_input.setText("Batch-KnowledgeBase.md")
        elif count == 1:
            self.merge_check.setChecked(False)  # Default false for single? Or True?
            self.merge_input.setText(f"{self.file_items[0].path.stem}.md")

    def reset_files(self):
        self.file_items = []
        self.map_path_to_item = {}
        self.file_list_widget.clear()
        self.stack.setCurrentWidget(self.drop_zone)
        self.status_label.setText("")

    def browse_output(self):
        path = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if path:
            self.out_edit.setText(path)

    def toggle_merge(self):
        self.merge_input.setEnabled(self.merge_check.isChecked())

    def start_convert(self):
        if not self.file_items:
            QMessageBox.warning(self, "提示", "列表中没有可转换的文件。")
            return

        self.convert_btn.setEnabled(False)
        self.convert_btn.setText("正在转换...")
        self.flp_add.setEnabled(False)
        self.flp_clear.setEnabled(False)
        self.progress_bar.setRange(0, len(self.file_items))
        self.progress_bar.setValue(0)
        self.progress_bar.show()

        # Reset item status visuals
        for i in range(self.file_list_widget.count()):
            it = self.file_list_widget.item(i)
            it.setForeground(QBrush(QColor(MorningTheme.TEXT_PRIMARY)))
            # Reset icon processing?

        self.worker = ConvertWorker(
            self.file_items,
            Path(self.out_edit.text()),
            self.merge_check.isChecked(),
            self.merge_input.text(),
        )
        self.worker.progress_global.connect(self.progress_bar.setValue)
        self.worker.file_started.connect(self.on_file_started)
        self.worker.file_finished.connect(self.on_file_finished)
        self.worker.finished_all.connect(self.on_finished_all)
        self.worker.error_critical.connect(self.on_error_critical)
        self.worker.start()

    def on_file_started(self, path: str):
        item = self.map_path_to_item.get(path)
        if item:
            item.setForeground(QBrush(QColor(MorningTheme.PROCESSING)))
            item.setText("🔄 " + item.text()[2:])  # Hacky replace icon
            self.file_list_widget.scrollToItem(item)

    def on_file_finished(self, path: str, success: bool, error: str):
        item = self.map_path_to_item.get(path)
        if item:
            if success:
                item.setForeground(QBrush(QColor(MorningTheme.SUCCESS)))
                item.setText("✅ " + item.text()[2:])
            else:
                item.setForeground(QBrush(QColor(MorningTheme.ERROR)))
                item.setText("❌ " + item.text()[2:])
                item.setToolTip(f"失败: {error}")

    def on_finished_all(self, results):
        self.convert_btn.setEnabled(True)
        self.convert_btn.setText("开始转换")
        self.flp_add.setEnabled(True)
        self.flp_clear.setEnabled(True)
        self.progress_bar.hide()

        success_count = sum(1 for r in results if r.success)
        fail_count = len(results) - success_count

        if fail_count == 0:
            self.status_label.setText(f"✨ 全部完成！共 {len(results)} 个文件")
            self.status_label.setStyleSheet(
                f"color: {MorningTheme.SUCCESS}; font-weight: 500;"
            )

            reply = QMessageBox.question(
                self,
                "完成",
                f"成功处理所有 {len(results)} 个文件。\n是否打开输出目录？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                QDesktopServices.openUrl(QUrl.fromLocalFile(self.out_edit.text()))
        else:
            self.status_label.setText(f"完成，存在 {fail_count} 个错误")
            self.status_label.setStyleSheet(
                f"color: {MorningTheme.ERROR}; font-weight: 500;"
            )

            # Show Detailed Report
            dlg = ResultDialog(self, results)
            dlg.exec()

    def on_error_critical(self, err):
        self.convert_btn.setEnabled(True)
        self.convert_btn.setText("开始转换")
        self.flp_add.setEnabled(True)
        self.flp_clear.setEnabled(True)
        self.progress_bar.hide()
        self.status_label.setText("发生严重错误")
        QMessageBox.critical(self, "系统错误", f"转换进程异常退出:\n{err}")


def run_gui():
    app = QApplication(sys.argv)
    window = ZenWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run_gui()
