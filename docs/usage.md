# Any2MD 使用指南

## 目录

- [安装](#安装)
- [快速开始](#快速开始)
- [图形界面](#图形界面)
- [命令行使用](#命令行使用)
- [支持的格式](#支持的格式)
- [常见问题](#常见问题)

## 安装

### 方式一：下载可执行文件（推荐）

从 [Releases](https://github.com/dustbinchen/Any2MD/releases) 页面下载对应平台的可执行文件：

| 平台 | 文件 |
|------|------|
| Windows | `Any2MD-windows-x64.exe` |
| macOS | `Any2MD-macos-x64` |
| Linux | `Any2MD-linux-x64` |

### 方式二：pip 安装

```bash
pip install any2md
```

### 方式三：从源码安装

```bash
git clone https://github.com/dustbinchen/Any2MD.git
cd Any2MD
pip install -e .
```

## 快速开始

### 启动图形界面

```bash
# 直接运行
any2md

# 或者
python -m any2md
```

### 命令行转换

```bash
# 转换单个文件
any2md convert document.pdf -o ./output

# 转换文件夹
any2md convert ./documents -o ./markdown-output

# 转换 ZIP 压缩包
any2md convert archive.zip -o ./output
```

## 图形界面

启动程序后，你会看到一个简洁的界面：

1. **拖拽区域**：直接将文件/文件夹/ZIP 拖入窗口
2. **输入路径**：手动输入或点击「浏览」选择
3. **输出目录**：选择转换后的 Markdown 文件保存位置
4. **开始转换**：点击按钮开始批量转换
5. **日志区域**：查看转换进度和结果

### 操作步骤

1. 拖入文件夹或 ZIP 文件（或点击选择）
2. 确认输出目录
3. 点击「开始转换」
4. 等待完成，查看输出目录

## 命令行使用

### 基本语法

```bash
any2md convert <输入路径> [选项]
```

### 选项

| 选项 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| `--output` | `-o` | 输出目录 | `./output` |
| `--recursive` | `-r` | 递归处理子目录 | `True` |

### 示例

```bash
# 转换当前目录下所有文档
any2md convert . -o ./md-output

# 转换指定文件夹，不递归
any2md convert ./docs -o ./output --no-recursive

# 转换 PDF 文件
any2md convert report.pdf -o ./output

# 转换 ZIP 并自动解压
any2md convert notes-export.zip -o ./my-notes
```

## 支持的格式

Any2MD 基于 [Microsoft MarkItDown](https://github.com/microsoft/markitdown) 引擎，支持以下格式：

| 类型 | 格式 | 说明 |
|------|------|------|
| 文档 | `.pdf` | PDF 文档（文本提取） |
| 文档 | `.docx` `.doc` | Word 文档 |
| 演示 | `.pptx` `.ppt` | PowerPoint 演示文稿 |
| 表格 | `.xlsx` `.xls` | Excel 表格 |
| 网页 | `.html` `.htm` | HTML 网页 |
| 数据 | `.json` `.csv` `.xml` | 结构化数据 |
| 文本 | `.txt` `.md` `.rtf` | 纯文本 |
| 图片 | `.jpg` `.png` `.gif` `.webp` | 图片（OCR 可选） |
| 音频 | `.mp3` `.wav` `.m4a` | 音频（语音转文字） |
| 压缩 | `.zip` | 自动解压处理 |

## 常见问题

### Q: 转换后的 Markdown 格式不正确？

A: 这取决于源文件的质量。复杂格式（如多栏 PDF）可能无法完美转换。建议转换后手动检查和调整。

### Q: 如何启用 OCR 识别图片中的文字？

A: MarkItDown 支持 OCR，但需要额外配置。请参考 [MarkItDown 文档](https://github.com/microsoft/markitdown)。

### Q: 转换大文件很慢？

A: 大型 PDF 或包含大量图片的文档需要更多时间处理。请耐心等待。

### Q: 支持批量重命名吗？

A: 目前输出文件名与源文件名相同（扩展名改为 `.md`）。后续版本将支持自定义命名规则。

### Q: 如何报告问题？

A: 请在 [GitHub Issues](https://github.com/dustbinchen/Any2MD/issues) 提交问题，附上：
- 操作系统和版本
- 源文件格式
- 错误信息截图

## 更多资源

- [GitHub 仓库](https://github.com/dustbinchen/Any2MD)
- [问题反馈](https://github.com/dustbinchen/Any2MD/issues)
- [MarkItDown 项目](https://github.com/microsoft/markitdown)
