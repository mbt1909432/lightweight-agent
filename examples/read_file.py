resolved_path=fr"E:\pycharm_project\lightweight-agent\examples\my_project\test.txt"
with open(resolved_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(lines)