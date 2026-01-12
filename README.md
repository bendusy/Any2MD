# Any2MD

**一键导入文件夹或 ZIP → 自动解压 → 批量转换为 Markdown**

Any2MD 是一个基于 [Microsoft MarkItDown](https://github.com/microsoft/markitdown) 的图形化批量转换工具，帮助你快速把各种文档、笔记、网页导出文件等批量转换成统一的 Markdown 格式。

## 特性

- 🎯 **基于 Microsoft MarkItDown** - 强大的文档转换引擎
- 📁 **支持拖拽** - 直接拖入文件夹或 ZIP 文件
- 🗜️ **自动解压** - ZIP 压缩包自动解压后处理
- 📄 **多格式支持** - PDF、DOCX、PPTX、XLSX、HTML、图片等
- 🖥️ **图形界面** - 简洁易用的 PyQt6 界面
- ⌨️ **命令行支持** - 适合脚本批量处理

## 支持的格式

基于 MarkItDown 支持的所有格式：

| 格式 | 说明 |
|------|------|
| PDF | 文本提取 |
| Word | .docx 文档 |
| PowerPoint | .pptx 演示文稿 |
| Excel | .xlsx / .xls 表格 |
| HTML | 网页文件 |
| ZIP | 自动解压处理 |

## 快速开始

### 安装

```bash
git clone https://github.com/dustbinchen/Any2MD.git
cd Any2MD

# CLI（不含 GUI，体积更小）
pip install -e .

# GUI
pip install -e ".[gui]"

# 全功能（未来要 OCR/音频等再装这个，会显著变大）
pip install -e ".[full]"
```

### 图形界面

```bash
python -m any2md
```

1. 拖入文件夹或 ZIP 文件
2. 选择输出目录
3. 点击「开始转换」
4. 完成！

### 命令行

```bash
# 转换文件夹
python -m any2md convert ./docs --output ./output

# 转换 ZIP
python -m any2md convert archive.zip --output ./output

# 转换单个文件
python -m any2md convert document.pdf --output ./output
# 转换单个文件
python -m any2md convert document.pdf --output ./output
```

## 常见问题 (FAQ)

### macOS 提示"无法打开...，因为Apple无法检查其是否包含恶意软件"

由于 Any2MD 未进行 Apple 开发者签名（Notarization），首次打开时可能会遇到此提示。请按以下步骤操作：

1. **不要直接双击打开 APP**
2. 在 `Any2MD.app` 上 **点击右键** (或按住 Control 键点击)
3. 在弹出的菜单中选择 **"打开" (Open)**
4. 在随后弹出的确认对话框中点击 **"打开" (Open)** 即可

或者：

1. 打开 "系统设置" -> "隐私与安全性"
2. 找到由 "未知开发者" 开发的 Any2MD
3. 点击 **"仍要打开" (Open Anyway)**

### 命令行解决 (进阶)

如果你熟悉终端，也可以使用以下命令清除应用的隔离属性：

```bash
xattr -cr /Applications/Any2MD.app
# 或者针对解压后的 Any2MD.app 路径
xattr -cr path/to/Any2MD.app
```

## 项目结构

```
Any2MD/
├── any2md/
│   ├── __init__.py
│   ├── __main__.py      # 入口
│   ├── cli.py           # 命令行接口
│   ├── gui.py           # GUI 启动器（可选依赖）
│   ├── gui_app.py       # PyQt6 图形界面
│   ├── converter.py     # 核心转换引擎（封装 MarkItDown）
│   ├── unzipper.py      # ZIP 解压
│   └── cleaner.py       # 文件名清理
├── tests/
├── requirements.txt
└── README.md
```

## 依赖

- Python >= 3.10
- markitdown - Microsoft MarkItDown（精简安装，暂不包含 OCR/音频等重依赖）
- PyQt6 - 图形界面（可选：`pip install 'any2md[gui]'`）
- typer - 命令行接口

## 许可证

MIT License

---

**Any2MD** —— 让任何内容都变成可搜索、可链接的 Markdown。
