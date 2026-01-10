# 发布新版本到 PyPI 的完整流程指南

本文档记录了从代码修改到发布新版本到 PyPI 的完整流程，可作为自动化发布的参考。

## 📋 发布前检查清单

### 1. 代码修改完成
- [ ] 所有功能开发完成
- [ ] 代码已测试
- [ ] 没有明显的 bug
- [ ] 代码格式符合规范（black, ruff）

### 2. 版本号更新（必须同步 - 最容易遗漏！）

**⚠️ 重要：版本号必须在以下三个文件中完全一致：**

#### 2.1 更新 `pyproject.toml`
```toml
[project]
version = "X.Y.Z"  # 例如：0.1.2, 0.2.0, 1.0.0
```

#### 2.2 更新 `src/lightweight_agent/__init__.py`
```python
__version__ = "X.Y.Z"  # 必须与 pyproject.toml 中的版本号完全一致
```

#### 2.3 更新 `RELEASE_GUIDE.md`（文档末尾）
```markdown
**当前版本**: X.Y.Z  # 必须与上述两个文件中的版本号完全一致
```

**版本号规则：**
- `X.Y.Z` 格式（语义化版本）
- `X` - 主版本号（不兼容的 API 修改）
- `Y` - 次版本号（向下兼容的功能性新增）
- `Z` - 修订号（向下兼容的问题修正）

**快速验证命令：**
```bash
# Windows PowerShell
(grep "version = " pyproject.toml; grep "__version__ = " src/lightweight_agent/__init__.py; grep "当前版本" RELEASE_GUIDE.md)

# Linux/Mac
grep -E "(version = |__version__ = |当前版本)" pyproject.toml src/lightweight_agent/__init__.py RELEASE_GUIDE.md
```

### 3. 导出类检查

确保所有需要公开使用的类都在 `src/lightweight_agent/__init__.py` 中导出：

```python
# 导入
from .agent import ReActAgent, TodoBasedAgent, CitationAgent, FigureAgent, build_system_prompt

# 导出到 __all__
__all__ = [
    "ReActAgent",
    "TodoBasedAgent",
    "CitationAgent",
    "FigureAgent",
    "build_system_prompt",
    # ... 其他类
]
```

**检查点：**
- [ ] 新增的 Agent 类已导入
- [ ] 新增的 Agent 类已添加到 `__all__`
- [ ] 其他新增的公共类/函数已导出

### 4. 配置文件检查

#### 4.1 `pyproject.toml` 检查
- [ ] 版本号已更新
- [ ] 依赖项列表完整且版本正确
- [ ] GitHub URL 正确（`https://github.com/mbt1909432/lightweight-agent`）
- [ ] 描述信息准确

#### 4.2 `MANIFEST.in` 检查
确保包含所有需要打包的文件：
```
include README.md
include LICENSE
recursive-include Use_Case *.py
recursive-include examples *.py
```

#### 4.3 `README.md` 检查
- [ ] 文档路径正确（如 `Use_Case/` 而不是 `src/Use_Case/`）
- [ ] 示例代码路径正确
- [ ] 新增功能的文档已更新

### 5. 文件完整性检查
- [ ] `LICENSE` 文件存在
- [ ] `README.md` 存在且内容完整
- [ ] 所有示例文件路径正确

## 🚀 发布流程

### 步骤 1: 清理旧的构建文件
```bash
# Windows
rmdir /s /q dist build *.egg-info 2>nul

# Linux/Mac
rm -rf dist/ build/ *.egg-info
```

### 步骤 2: 构建包
```bash
# 确保已安装 build 工具
pip install build

# 构建包（生成 wheel 和 source distribution）
python -m build
```

构建成功后会在 `dist/` 目录生成：
- `lightweight_agent-X.Y.Z-py3-none-any.whl` (wheel 包)
- `lightweight_agent-X.Y.Z.tar.gz` (源码包)

### 步骤 3: 检查构建的包（可选但推荐）
```bash
# 安装 twine（如果还没安装）
pip install twine

# 检查包是否有问题
twine check dist/*
```

### 步骤 4: 测试上传到 TestPyPI（推荐）
```bash
# 上传到测试 PyPI
twine upload --repository testpypi dist/*

# 会提示输入用户名和密码
# 用户名：__token__
# 密码：pypi-开头的 API token（从 TestPyPI 获取）
```

**测试安装：**
```bash
# 从 TestPyPI 安装测试
pip install --index-url https://test.pypi.org/simple/ lightweight-agent==X.Y.Z
```

### 步骤 5: 正式上传到 PyPI
```bash
# 上传到正式 PyPI
twine upload dist/*

# 会提示输入用户名和密码
# 用户名：__token__
# 密码：pypi-开头的 API token（从 PyPI 获取）
```

### 步骤 6: Git 提交和推送

#### 6.1 提交更改
```bash
# 查看更改
git status

# 添加所有更改
git add .

# 提交（使用语义化提交信息）
git commit -m "chore: bump version to X.Y.Z"

# 或者更详细的提交信息
git commit -m "chore: bump version to X.Y.Z

- Update version in pyproject.toml and __init__.py
- Add new features: [描述新功能]
- Fix bugs: [描述修复的问题]"
```

#### 6.2 创建 Git Tag（推荐）
```bash
# 创建带注释的 tag
git tag -a vX.Y.Z -m "Release version X.Y.Z"

# 推送 tag 到远程仓库
git push origin vX.Y.Z
```

#### 6.3 推送到远程仓库
```bash
# 推送代码
git push origin main

# 或者推送到主分支（根据你的分支名）
git push origin master
```

## 📝 发布后验证

### 1. 检查 PyPI 页面
访问：`https://pypi.org/project/lightweight-agent/`
- [ ] 版本号正确
- [ ] 描述信息正确
- [ ] 文件已上传

### 2. 测试安装
```bash
# 卸载旧版本
pip uninstall lightweight-agent -y

# 安装新版本
pip install lightweight-agent

# 验证版本
python -c "import lightweight_agent; print(lightweight_agent.__version__)"
```

### 3. 测试导入
```python
# 测试所有主要类的导入
from lightweight_agent import (
    ReActAgent,
    TodoBasedAgent,
    CitationAgent,
    FigureAgent,
    OpenAIClient,
    AnthropicClient,
    # ... 其他类
)
```

## 🔄 快速发布脚本（参考）

可以创建一个 `release.py` 脚本自动化部分流程：

```python
#!/usr/bin/env python3
"""自动化发布脚本"""
import subprocess
import sys
import re
from pathlib import Path

def run_cmd(cmd):
    """运行命令"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"错误: {cmd}")
        print(result.stderr)
        sys.exit(1)
    return result.stdout

def get_version():
    """从 pyproject.toml 获取版本号"""
    with open("pyproject.toml") as f:
        content = f.read()
        match = re.search(r'version = "([^"]+)"', content)
        if match:
            return match.group(1)
    raise ValueError("无法找到版本号")

def main():
    version = get_version()
    print(f"准备发布版本: {version}")
    
    # 清理
    print("清理旧文件...")
    run_cmd("rmdir /s /q dist build *.egg-info 2>nul" if sys.platform == "win32" else "rm -rf dist/ build/ *.egg-info")
    
    # 构建
    print("构建包...")
    run_cmd("python -m build")
    
    # 检查
    print("检查包...")
    run_cmd("twine check dist/*")
    
    print(f"\n✅ 构建完成！版本: {version}")
    print("\n下一步:")
    print("1. 测试上传: twine upload --repository testpypi dist/*")
    print("2. 正式上传: twine upload dist/*")
    print("3. Git 提交: git add . && git commit -m 'chore: bump version to {version}'")
    print("4. 创建 Tag: git tag -a v{version} -m 'Release version {version}'")
    print("5. 推送: git push origin main && git push origin v{version}")

if __name__ == "__main__":
    main()
```

## ⚠️ 常见错误和陷阱

### 1. 版本号同步问题（最容易遗漏！）

**错误现象：**
- 构建成功但版本号不一致
- 安装后 `import lightweight_agent; print(lightweight_agent.__version__)` 显示的版本与 PyPI 不一致
- 用户安装的版本号与预期不符

**必须同步更新的文件（按顺序检查）：**
1. ✅ `pyproject.toml` - `[project]` 下的 `version = "X.Y.Z"`
2. ✅ `src/lightweight_agent/__init__.py` - `__version__ = "X.Y.Z"`
3. ✅ `RELEASE_GUIDE.md` - 文档末尾的 `**当前版本**: X.Y.Z`

**检查命令：**
```bash
# 检查 pyproject.toml
grep "version = " pyproject.toml

# 检查 __init__.py
grep "__version__ = " src/lightweight_agent/__init__.py

# 检查 RELEASE_GUIDE.md
grep "当前版本" RELEASE_GUIDE.md
```

**解决方案：**
- 使用查找替换功能同时更新所有文件
- 更新后立即验证三个文件的版本号是否一致

### 2. 导出类遗漏问题

**错误现象：**
- 新增的 Agent 类无法通过 `from lightweight_agent import NewAgent` 导入
- 用户报告 `ImportError: cannot import name 'NewAgent'`

**必须检查的文件：**
- `src/lightweight_agent/__init__.py` 中的导入和 `__all__` 列表

**检查清单：**
- [ ] 新增的类是否已从对应模块导入？
- [ ] 新增的类是否已添加到 `__all__` 列表？
- [ ] 导入路径是否正确（相对导入 vs 绝对导入）？

### 3. 文件路径错误

**错误现象：**
- README.md 中的示例代码路径不正确
- 用户无法找到示例文件
- 打包时缺少必要文件

**常见错误：**
- 文档中写的是 `src/Use_Case/` 但实际路径是 `Use_Case/`
- `MANIFEST.in` 中未包含新添加的示例文件

**检查清单：**
- [ ] README.md 中的路径是否与实际目录结构一致？
- [ ] `MANIFEST.in` 是否包含所有需要打包的文件？
- [ ] 示例文件是否在正确的位置？

### 4. 构建和上传错误

**错误 1: 版本已存在**
```
HTTPError: 400 Client Error: File already exists. See https://pypi.org/help/#file-name-reuse
```
**解决方案：** 必须更新版本号，PyPI 不允许覆盖已发布的版本

**错误 2: 认证失败**
```
HTTPError: 401 Client Error: Invalid or non-existent authentication information
```
**解决方案：** 
- 检查 API token 是否正确
- 确认使用的是 `__token__` 作为用户名
- 确认 token 有上传权限

**错误 3: 包检查失败**
```
twine check dist/*
```
如果检查失败，查看具体错误信息，常见原因：
- 缺少必需文件（LICENSE, README.md）
- 文件格式问题
- 元数据错误

### 5. 依赖版本冲突

**错误现象：**
- 构建成功但安装时出现依赖冲突
- 用户环境无法安装包

**检查清单：**
- [ ] `pyproject.toml` 中的依赖版本是否合理？
- [ ] 是否使用了过于严格的版本限制（如 `==` 而不是 `>=`）？
- [ ] 依赖是否与 Python 版本兼容？

### 6. 文档更新遗漏

**容易遗漏的文档更新：**
- [ ] `RELEASE_GUIDE.md` 中的当前版本号
- [ ] `README.md` 中的更新日志（如果有）
- [ ] `VERSION_UPDATE.md` 中的示例版本号（如果存在）

### 7. Git 提交遗漏

**错误现象：**
- 发布成功但忘记提交代码
- 版本号更新未同步到仓库

**检查清单：**
- [ ] 所有更改是否已 `git add`？
- [ ] 是否已 `git commit`？
- [ ] 是否已创建并推送 tag？
- [ ] 是否已推送到远程仓库？

## ⚠️ 注意事项

1. **版本号必须同步**：`pyproject.toml`、`__init__.py` 和 `RELEASE_GUIDE.md` 中的版本号必须完全一致
2. **不要跳过测试**：建议先上传到 TestPyPI 测试
3. **API Token 安全**：不要在代码中硬编码 API token，使用环境变量或交互式输入
4. **提交信息规范**：使用语义化提交信息（chore, feat, fix 等）
5. **回滚准备**：如果发布有问题，可以发布一个修复版本（如 0.1.2 -> 0.1.3）
6. **发布前完整检查**：使用本文档的检查清单逐项确认

## 📚 相关资源

- PyPI 账户：https://pypi.org/account/
- TestPyPI：https://test.pypi.org/
- 语义化版本：https://semver.org/
- 项目仓库：https://github.com/mbt1909432/lightweight-agent

---

**最后更新**: 2024-12-19
**当前版本**: 0.1.2

