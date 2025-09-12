# 开发环境配置

## 快速开始

```bash
# 安装依赖
uv sync

# 运行所有测试（推荐）
uv run tox

# 或者单独运行测试步骤
uv run python -m py_compile passtk/passtk.py
uv run python passtk/passtk.py -u -l 2 -n 8
uv run flake8 passtk/
```

## 说明

- **Python版本**：仅支持Python 3.6+
- **包管理工具**：使用uv进行依赖管理
- **测试工具**：使用tox进行完整测试流程，包含编译检查、功能测试和代码风格检查