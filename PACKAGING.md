# 打包和分发指南 (Packaging and Distribution Guide)

本指南说明如何打包和分发 `lightweight-agent` 包。

This guide explains how to package and distribute the `lightweight-agent` package.

## 准备工作 (Prerequisites)

### 1. 确认工作目录

**重要**：所有命令都必须在项目根目录运行，即包含 `pyproject.toml` 文件的目录。

**Important**: All commands must be run from the project root directory (the directory containing `pyproject.toml`).

项目根目录示例：
- Windows: `E:\pycharm_project\lightweight-agent\`
- Linux/Mac: `/path/to/lightweight-agent/`

验证当前目录：
```bash
# Windows PowerShell
pwd
Test-Path pyproject.toml

# Linux/Mac
pwd
ls pyproject.toml
```

### 2. 安装打包工具

确保已安装以下工具：

Make sure you have the following tools installed:

```bash
pip install build twine
```

## 构建包 (Building the Package)

### 方法 1: 使用 build 模块（推荐）

在项目根目录运行：

Run from the project root directory:

```bash
python -m build
```

这将创建：
- `dist/lightweight_agent-<version>.tar.gz` - 源码分发包
- `dist/lightweight_agent-<version>-py3-none-any.whl` - Wheel 分发包

### 方法 2: 使用构建脚本

项目提供了便捷的构建脚本：

```bash
python build_package.py
```

### 验证构建结果

构建完成后，验证包：

After building, verify the package:

```bash
# 检查包内容
twine check dist/*
```

如果看到 `PASSED`，说明包构建成功。

If you see `PASSED`, the package was built successfully.

## 本地安装测试 (Installing Locally)

### 从本地构建安装

**Windows PowerShell 用户注意**：PowerShell 中通配符 `*` 的处理方式不同，建议使用完整文件名。

**Note for Windows PowerShell users**: Wildcards `*` work differently in PowerShell, use full filenames.

#### Windows PowerShell

```powershell
# 方法 1: 使用完整文件名（推荐）
pip install dist\lightweight_agent-0.1.0-py3-none-any.whl

# 方法 2: 使用通配符（需要引号）
pip install "dist\lightweight_agent-*.whl"

# 方法 3: 使用 Get-ChildItem 展开通配符
pip install (Get-ChildItem dist\*.whl)[0].FullName
```

#### Linux/Mac 或 Git Bash

```bash
# 从 wheel 安装
pip install dist/lightweight_agent-*.whl

# 或从源码分发包安装
pip install dist/lightweight_agent-*.tar.gz
```

### 开发模式安装

用于开发时，可以安装为可编辑模式：

For development, install in editable mode:

```bash
# 可编辑模式安装
pip install -e .

# 包含开发依赖
pip install -e ".[dev]"
```

### Install in Development Mode

```bash
# Install in editable mode (for development)
pip install -e .

# With dev dependencies
pip install -e ".[dev]"
```

## 发布到 PyPI (Publishing to PyPI)

### 1. 获取 PyPI API Token

**推荐使用 API Token**，比密码更安全：

**Recommended: Use API Token** for better security:

1. 访问 https://pypi.org/manage/account/token/
2. 创建新的 API token
3. 复制 token（只显示一次，请妥善保存）

### 2. 先测试到 TestPyPI

建议先发布到 TestPyPI 进行测试：

It's recommended to test on TestPyPI before publishing to the main PyPI:

#### Windows PowerShell

```powershell
# 上传到 TestPyPI
twine upload --repository testpypi dist\*

# 从 TestPyPI 测试安装
pip install --index-url https://test.pypi.org/simple/ lightweight-agent
```

#### Linux/Mac

```bash
# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ lightweight-agent
```

### 3. 发布到 PyPI

测试通过后，发布到正式 PyPI：

Once tested, publish to the main PyPI:

#### Windows PowerShell

```powershell
# 上传到 PyPI
twine upload dist\*
```

#### Linux/Mac

```bash
# Upload to PyPI
twine upload dist/*
```

### 4. 使用 API Token 认证

当提示输入凭证时：

When prompted for credentials:

**方法 1: 交互式输入**
- Username: `__token__`
- Password: 粘贴你的 API token（以 `pypi-` 开头）

**方法 2: 使用环境变量（推荐）**

```bash
# Windows PowerShell
$env:TWINE_USERNAME = "__token__"
$env:TWINE_PASSWORD = "pypi-your-api-token-here"
twine upload dist\*

# Linux/Mac
export TWINE_USERNAME="__token__"
export TWINE_PASSWORD="pypi-your-api-token-here"
twine upload dist/*
```

**方法 3: 使用配置文件**

创建或编辑 `~/.pypirc` 文件：

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-your-api-token-here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-test-token-here
```

**注意**：配置文件包含敏感信息，请确保文件权限正确（Linux/Mac: `chmod 600 ~/.pypirc`）

**Note**: The config file contains sensitive information, ensure proper file permissions (Linux/Mac: `chmod 600 ~/.pypirc`)

### 3. Verify Installation

After publishing, verify the installation:

```bash
pip install lightweight-agent
```

## 版本管理 (Version Management)

更新版本号：

To update the version:

1. 更新 `src/lightweight_agent/__init__.py` 中的 `__version__`
2. 更新 `pyproject.toml` 中的 `version`
3. 重新构建和发布
4. Update `__version__` in `src/lightweight_agent/__init__.py`
5. Update `version` in `pyproject.toml`
6. Rebuild and publish

示例：

Example:

```python
# In src/lightweight_agent/__init__.py
__version__ = "0.1.1"
```

```toml
# In pyproject.toml
[project]
version = "0.1.1"
```

### 版本号规范

遵循 [语义化版本](https://semver.org/)：
- **主版本号** (MAJOR): 不兼容的 API 修改
- **次版本号** (MINOR): 向后兼容的功能新增
- **修订号** (PATCH): 向后兼容的问题修复

Follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Incompatible API changes
- **MINOR**: Backward-compatible functionality additions
- **PATCH**: Backward-compatible bug fixes

## Project Structure

The package follows the standard Python package structure:

```
lightweight-agent/
├── src/
│   └── lightweight_agent/
│       ├── __init__.py          # Main package exports
│       ├── agent/                # Agent implementations
│       ├── clients/              # LLM clients
│       ├── session/              # Session management
│       └── tools/                # Tool system
├── examples/                     # Example code (not included in package)
├── tests/                        # Tests (not included in package)
├── pyproject.toml               # Package configuration
├── README.md                     # Project documentation
└── LICENSE                       # License file
```

## Package Configuration

The package is configured in `pyproject.toml`:

- **Package name**: `lightweight-agent` (installed as `lightweight_agent`)
- **Source location**: `src/` directory
- **Dependencies**: Listed in `[project.dependencies]`
- **Optional dependencies**: Listed in `[project.optional-dependencies]`

## 故障排除 (Troubleshooting)

### 常见问题

#### 1. 包安装后找不到

**Package not found after installation**

- 确保使用正确的包名：pip 安装时使用 `lightweight-agent`（带连字符），Python 导入时使用 `lightweight_agent`（下划线）
- Make sure you're using the correct package name: `lightweight-agent` (with hyphen) for pip, but `lightweight_agent` (with underscore) in Python imports

#### 2. 构建失败

**Build fails**

- 确保所有必需文件都存在
- 检查所有包目录中是否存在 `__init__.py` 文件
- 验证 `pyproject.toml` 语法
- Make sure all required files are present
- Check that `__init__.py` files exist in all package directories
- Verify `pyproject.toml` syntax

#### 3. 导入错误

**Import errors**

- 确保所有导出的类/函数都在 `__init__.py` 的 `__all__` 中列出
- 检查 `__init__.py` 中的导入是否正确
- Ensure all exported classes/functions are listed in `__all__` in `__init__.py`
- Check that imports in `__init__.py` are correct

#### 4. Windows PowerShell 通配符问题

**Windows PowerShell wildcard issues**

错误示例：
```
ERROR: Invalid wheel filename (wrong number of parts): 'lightweight_agent-*'
```

解决方案：
```powershell
# ❌ 错误：直接使用通配符
pip install dist/lightweight_agent-*.whl

# ✅ 正确：使用完整文件名
pip install dist\lightweight_agent-0.1.0-py3-none-any.whl

# ✅ 正确：使用引号包裹通配符
pip install "dist\lightweight_agent-*.whl"

# ✅ 正确：使用 Get-ChildItem 展开
pip install (Get-ChildItem dist\*.whl)[0].FullName
```

#### 5. Twine 上传时认证失败

**Twine upload authentication failed**

- 确保 API token 以 `pypi-` 开头
- 使用 `__token__` 作为用户名，不要使用你的 PyPI 用户名
- 如果使用配置文件，检查文件路径和权限
- Make sure API token starts with `pypi-`
- Use `__token__` as username, not your PyPI username
- If using config file, check file path and permissions

#### 6. 版本冲突

**Version conflicts**

如果包已经存在于 PyPI，需要更新版本号：
- 更新 `pyproject.toml` 中的 `version`
- 更新 `src/lightweight_agent/__init__.py` 中的 `__version__`
- 重新构建和上传

If package already exists on PyPI, update version:
- Update `version` in `pyproject.toml`
- Update `__version__` in `src/lightweight_agent/__init__.py`
- Rebuild and upload

## 完整打包流程示例 (Complete Workflow Example)

### 标准流程

```bash
# 1. 切换到项目根目录
cd E:\pycharm_project\lightweight-agent  # Windows
# 或
cd /path/to/lightweight-agent  # Linux/Mac

# 2. 安装/更新打包工具
pip install --upgrade build twine

# 3. 清理旧的构建文件（可选）
# Windows PowerShell
Remove-Item -Recurse -Force build, dist, *.egg-info -ErrorAction SilentlyContinue
# Linux/Mac
rm -rf build dist *.egg-info

# 4. 构建包
python -m build

# 5. 验证包
twine check dist/*

# 6. 本地测试安装
# Windows
pip install dist\lightweight_agent-0.1.0-py3-none-any.whl  # PowerShell
# 或
pip install dist/lightweight_agent-0.1.0-py3-none-any.whl  # Linux/Mac

# 7. 测试导入
python -c "import lightweight_agent; print(lightweight_agent.__version__)"

# 8. 上传到 TestPyPI（测试）
twine upload --repository testpypi dist/*

# 9. 从 TestPyPI 测试安装
pip install --index-url https://test.pypi.org/simple/ lightweight-agent

# 10. 上传到正式 PyPI
twine upload dist/*

# 11. 验证发布
pip install lightweight-agent
```

## 持续集成 (Continuous Integration)

可以设置 CI/CD 实现自动化构建和发布：

For automated building and publishing, you can set up CI/CD:

1. **GitHub Actions**: 创建 `.github/workflows/publish.yml`
2. **GitLab CI**: 在 `.gitlab-ci.yml` 中添加发布任务
3. **自动化版本管理**: 使用 `bump2version` 或 `semantic-release` 等工具

## Additional Resources

- [Python Packaging User Guide](https://packaging.python.org/)
- [PyPI Documentation](https://pypi.org/help/)
- [setuptools Documentation](https://setuptools.pypa.io/)

