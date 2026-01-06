import os
from pathlib import Path

working_dir="E:\pycharm_project\lightweight-agent\examples"
if not os.path.isabs(working_dir):
    raise ValueError(f"working_dir must be an absolute path, got: {working_dir}")

# 工作目录（已经是绝对路径，直接使用）
print(Path(working_dir).resolve())

