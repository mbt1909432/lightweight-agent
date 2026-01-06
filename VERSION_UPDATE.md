# 版本更新指南 (Version Update Guide)

本指南说明如何更新 `lightweight-agent` 的版本并发布到 PyPI。

This guide explains how to update the version of `lightweight-agent` and publish to PyPI.

## 快速更新流程

### 1. 更新版本号

需要同时更新两个文件：

#### 更新 `pyproject.toml`

```toml
[project]
version = "0.1.1"  # 更新为新版本号
```

#### 更新 `src/lightweight_agent/__init__.py`

```python
__version__ = "0.1.1"  # 更新为新版本号
```

### 2. 更新 CHANGELOG（可选但推荐）

在 `README.md` 的"更新日志"部分添加新版本的变更说明。

### 3. 构建新版本

```bash
# Windows PowerShell
Remove-Item -Recurse -Force build, dist, *.egg-info -ErrorAction SilentlyContinue
python -m build
twine check dist/*

# Linux/Mac
rm -rf build dist *.egg-info
python -m build
twine check dist/*
```

### 4. 本地测试（推荐）

```bash
# Windows PowerShell
pip install dist\lightweight_agent-0.1.1-py3-none-any.whl

# Linux/Mac
pip install dist/lightweight_agent-0.1.1-py3-none-any.whl

# 验证安装
python -c "import lightweight_agent; print(lightweight_agent.__version__)"
```

### 5. 发布到 PyPI

```bash
# 设置认证信息（如果还没有配置）
# Windows PowerShell
$env:TWINE_USERNAME = "__token__"
$env:TWINE_PASSWORD = "pypi-your-api-token-here"

# Linux/Mac
export TWINE_USERNAME="__token__"
export TWINE_PASSWORD="pypi-your-api-token-here"

# 上传到 PyPI
twine upload dist/*
```

### 6. 验证发布

等待几分钟后（PyPI需要时间同步），测试安装：

```bash
pip install --upgrade lightweight-agent
python -c "import lightweight_agent; print(lightweight_agent.__version__)"
```

## 版本号规范

遵循 [语义化版本](https://semver.org/)：

- **主版本号** (MAJOR): 不兼容的 API 修改
  - 例如：`0.1.0` → `1.0.0`
  
- **次版本号** (MINOR): 向后兼容的功能新增
  - 例如：`0.1.0` → `0.2.0`
  
- **修订号** (PATCH): 向后兼容的问题修复
  - 例如：`0.1.0` → `0.1.1`

## 完整示例

假设要发布 `0.1.1` 版本：

### 步骤 1: 更新版本号

**`pyproject.toml`**:
```toml
[project]
version = "0.1.1"
```

**`src/lightweight_agent/__init__.py`**:
```python
__version__ = "0.1.1"
```

### 步骤 2: 更新 README.md

在"更新日志"部分添加：

```markdown
### 0.1.1 (2025-01-XX)

- 修复了某个bug
- 改进了某个功能
```

### 步骤 3: 构建和发布

```bash
# 清理
rm -rf build dist *.egg-info

# 构建
python -m build

# 验证
twine check dist/*

# 上传
twine upload dist/*
```

### 步骤 4: 验证

```bash
pip install --upgrade lightweight-agent
```

## 常见问题

### Q: 如何获取 PyPI API Token？

A: 
1. 访问 https://pypi.org/manage/account/token/
2. 创建新的 API token
3. 复制 token（以 `pypi-` 开头）

### Q: 上传时提示版本已存在？

A: 需要更新版本号。PyPI 不允许覆盖已发布的版本。

### Q: 可以先测试到 TestPyPI 吗？

A: 可以！先上传到 TestPyPI 测试：

```bash
# 上传到 TestPyPI
twine upload --repository testpypi dist/*

# 从 TestPyPI 测试安装
pip install --index-url https://test.pypi.org/simple/ lightweight-agent
```

### Q: 如何自动化版本更新？

A: 可以使用工具如 `bump2version` 或 `semantic-release` 来自动化版本管理。

## 相关文档

- 详细打包指南: [`PACKAGING.md`](PACKAGING.md)
- PyPI 项目页面: https://pypi.org/project/lightweight-agent/

