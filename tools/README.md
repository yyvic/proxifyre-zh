# 汉化工具（tools）

- `localize.py` — 二进制免编译补丁：直接修改已安装的 `ProxiFyreUI.Managed.dll`（#US 字符串堆原地替换），立即生效，无需编译环境。用法：`python localize.py`（dry-run） / `python localize.py --apply`（写入）。
- `localize_src.py` — 源码级汉化：对 `ProxiFyreUI/` 下的 C# 源码做同样的字符串替换（已由本仓库应用，留存供对照与上游同步时重新生成）。

两个脚本共用同一套中英文映射表（定义在 `localize.py` 的 `M` 字典中）。
上游发布新版本后，重新运行 `localize_src.py` 即可再生成源码汉化；二进制补丁需按新 dll 重新运行 `localize.py`。
