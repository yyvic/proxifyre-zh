# -*- coding: utf-8 -*-
"""源码级汉化：替换 ProxiFyreUI C# 源码中的英文字符串字面量为中文。"""
import os, re, sys, json

SRC = r"C:\Users\yiyao\Tools\proxifyre-zh\proxifyre-src\ProxiFyreUI"

# 复用 binary localize.py 的映射表
sys.path.insert(0, r"C:\Users\yiyao\Tools\proxifyre-zh")
src = open(r"C:\Users\yiyao\Tools\proxifyre-zh\localize.py", encoding="utf-8").read()
m = re.search(r"M = \{(.*?)\n\}", src, re.S)
M = eval("{" + m.group(1) + "}")

total = 0
files_changed = []
for root, dirs, files in os.walk(SRC):
    for f in files:
        if not f.endswith(".cs"):
            continue
        path = os.path.join(root, f)
        text = open(path, encoding="utf-8-sig").read()
        orig = text
        count = 0
        for en, zh in M.items():
            # 只替换完整字符串字面量（带双引号），避免误伤注释/标识符
            needle = '"' + en + '"'
            if needle in text:
                # C# 源码中的 & 无需转义；检查是否含需转义字符
                assert '"' not in zh and "\\" not in zh, zh
                text = text.replace(needle, '"' + zh + '"')
                count += 1
        if text != orig:
            open(path, "w", encoding="utf-8").write(text)
            files_changed.append((os.path.relpath(path, SRC), count))
            total += count

print(f"files changed: {len(files_changed)}, literal replacements: {total}")
for f, c in sorted(files_changed):
    print(f"  {c:3d}  {f}")
