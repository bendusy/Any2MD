# 开发文档

## 架构概述

Any2MD 采用简洁的模块化架构：

```
┌─────────────┐     ┌─────────────┐
│   CLI/GUI   │────▶│  Converter  │
└─────────────┘     └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  MarkItDown │
                    └─────────────┘
```

### 核心模块

#### converter.py

封装 Microsoft MarkItDown，提供统一的转换接口。

```python
from any2md import Any2MDConverter

converter = Any2MDConverter()

# 转换单个文件
result = converter.convert_file(Path("doc.pdf"), Path("./output"))

# 转换目录
results = converter.convert_directory(Path("./docs"), Path("./output"))
```

**ConvertResult 结构：**
- `success: bool` - 是否成功
- `input_path: Path` - 输入文件路径
- `output_path: Path | None` - 输出文件路径
- `markdown: str` - 转换后的 Markdown 内容
- `title: str | None` - 文档标题
- `error: str | None` - 错误信息

#### unzipper.py

处理 ZIP 压缩包的解压，支持嵌套压缩包。

```python
from any2md import Unzipper

with Unzipper() as unzipper:
    extracted_dir = unzipper.extract_recursive(Path("archive.zip"))
    # 处理解压后的文件
# 自动清理临时目录
```

#### cleaner.py

文件名清理工具，处理非法字符和格式化。

```python
from any2md import FilenameCleaner

cleaner = FilenameCleaner({
    "replace_spaces_with": "_",
    "lowercase": True,
    "max_length": 100
})

clean_name = cleaner.clean("My File <Name>.pdf")
# 输出: my_file_name.pdf
```

### GUI 架构

基于 PyQt6 实现：

- `MainWindow` - 主窗口
- `DropArea` - 拖拽区域组件
- `ConvertWorker` - 后台转换线程

使用 QThread 避免 UI 阻塞：

```python
class ConvertWorker(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal(list)
    error = pyqtSignal(str)
```

## 扩展指南

### 添加新的转换格式

MarkItDown 已支持大多数格式。如需自定义处理：

```python
class Any2MDConverter:
    def convert_file(self, input_path, output_path):
        # 在调用 MarkItDown 前后添加自定义逻辑
        if input_path.suffix == ".custom":
            return self._custom_convert(input_path)
        
        result = self.md.convert(str(input_path))
        # ...
```

### 添加配置选项

修改 `converter.py` 的 `__init__` 方法：

```python
def __init__(self, config: dict | None = None):
    self.config = config or {}
    self.md = MarkItDown(
        enable_plugins=self.config.get("enable_plugins", True)
    )
```

## 测试

```bash
# 运行所有测试
pytest

# 带覆盖率
pytest --cov=any2md --cov-report=html

# 运行特定测试
pytest tests/test_converter.py -v
```

## 构建发布

### 本地构建

```bash
# 构建 wheel
python -m build

# PyInstaller 打包
pyinstaller Any2MD.spec
```

### 发布新版本

1. 更新版本号 (`any2md/__init__.py`, `pyproject.toml`)
2. 创建 git tag: `git tag v0.1.0`
3. 推送: `git push origin v0.1.0`
4. GitHub Actions 自动构建并发布
