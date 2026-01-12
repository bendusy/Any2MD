# 贡献指南

感谢你对 Any2MD 项目的兴趣！欢迎任何形式的贡献。

## 如何贡献

### 报告问题

如果你发现了 bug 或有功能建议：

1. 先搜索 [现有 Issues](https://github.com/dustbinchen/Any2MD/issues) 确认是否已有相关讨论
2. 如果没有，创建新 Issue 并提供：
   - 清晰的问题描述
   - 复现步骤
   - 期望行为 vs 实际行为
   - 操作系统、Python 版本
   - 相关错误日志

### 提交代码

1. **Fork 仓库**

```bash
git clone https://github.com/你的用户名/Any2MD.git
cd Any2MD
```

2. **创建分支**

```bash
git checkout -b feature/你的功能名
# 或
git checkout -b fix/问题描述
```

3. **安装开发依赖**

```bash
pip install -e ".[dev]"
```

4. **进行修改并测试**

```bash
# 运行测试
pytest

# 检查代码风格
ruff check any2md/
```

5. **提交更改**

```bash
git add .
git commit -m "feat: 添加新功能描述"
# 或
git commit -m "fix: 修复问题描述"
```

6. **推送并创建 PR**

```bash
git push origin feature/你的功能名
```

然后在 GitHub 上创建 Pull Request。

## 提交规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式：

- `feat:` 新功能
- `fix:` 修复 bug
- `docs:` 文档更新
- `style:` 代码格式（不影响功能）
- `refactor:` 重构
- `test:` 测试相关
- `chore:` 构建/工具相关

示例：
```
feat: 添加拖拽多文件支持
fix: 修复 Windows 下路径编码问题
docs: 更新安装说明
```

## 代码规范

- 使用 Python 3.10+ 语法
- 遵循 PEP 8 规范
- 使用 type hints
- 保持函数简洁（单一职责）
- 添加必要的测试

## 开发环境

```bash
# 克隆仓库
git clone https://github.com/dustbinchen/Any2MD.git
cd Any2MD

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 启动应用
python -m any2md
```

## 项目结构

```
Any2MD/
├── any2md/
│   ├── __init__.py      # 包入口
│   ├── __main__.py      # 运行入口
│   ├── cli.py           # 命令行接口
│   ├── gui.py           # PyQt6 界面
│   ├── converter.py     # MarkItDown 封装
│   ├── unzipper.py      # ZIP 解压
│   └── cleaner.py       # 文件名清理
├── tests/               # 测试文件
├── docs/                # 文档
└── .github/workflows/   # CI/CD
```

## 需要帮助？

- 查看 [Issues](https://github.com/dustbinchen/Any2MD/issues) 寻找可以参与的任务
- 标记为 `good first issue` 的问题适合新手
- 有疑问可以在 Issue 中讨论

再次感谢你的贡献！
