下面是从更新版本到上传 PyPI 的完整命令流程（Windows cmd，已在虚拟环境中）：

1) 更新版本号
- 在项目里修改版本号（`pyproject.toml` 或 `setup.py/setup.cfg`），例如改为 0.1.1。

2) 清理旧构建产物
```
rmdir /s /q dist build
for /d %d in (*.egg-info) do rmdir /s /q "%d"
```

3) 安装打包工具（如未安装）
```
pip install --upgrade build twine
```

4) 构建 sdist + wheel
```
python -m build
```

5) 本地检查包元数据
```
twine check dist\*
```

6) 上传（正式 PyPI）
```
twine upload dist\*
```
- 输入 PyPI token：用户名 `__token__`，密码为你的 API token。

可选：先发 TestPyPI 验证
```
twine upload -r testpypi dist\*
pip install -i https://test.pypi.org/simple --extra-index-url https://pypi.org/simple lightweight-agent==0.1.1
```

若要跳过已存在的文件（不覆盖），可用：
```
twine upload --skip-existing dist\*
```

请先确认新版本号已修改，再按以上顺序执行。