# -*- coding: utf-8 -*-
"""
ProxiFyre UI 汉化脚本（#US user-string heap 原地替换）
原理：解析 PE -> CLR -> 元数据 -> #US 流，把 UTF-16LE 字符串字面量
替换为中文。新 blob <= 旧 blob 时原地写入，尾部补 0，长度前缀按原编码档位重写。
"""
import struct, sys, json

DLL = r"C:\Program Files\ProxiFyre\ProxiFyreUI.Managed.dll"

# ---------------- 汉化映射表 ----------------
M = {
    # 顶栏
    "Service:": "服务：",
    "Configuration:": "配置：",
    "Changes:": "更改：",
    "Start": "启动",
    "Stop": "停止",
    "Restart": "重启",
    "Install service": "安装服务",
    "Uninstall service": "卸载服务",
    # Tab 页
    "Routing": "路由",
    "Exclusions": "排除",
    "Logs": "日志",
    "Settings / Diagnostics": "设置 / 诊断",
    # 路由按钮与表格列头
    "Add": "添加",
    "Edit": "编辑",
    "Duplicate": "复制",
    "Remove": "移除",
    "Move up": "上移",
    "Move down": "下移",
    "Order": "序号",
    "Applications": "应用程序",
    "Proxy endpoint": "代理端点",
    "Authentication": "认证",
    "Transport": "传输方式",
    "Protocols": "协议",
    "Address families": "地址类型",
    "Warnings": "警告",
    # 底部按钮与状态
    "Reload": "重新加载",
    "Validate": "验证",
    "Save": "保存",
    "Apply && Restart": "应用并重启",
    "Ready": "就绪",
    # 设置页
    "Resolved engine locations": "引擎路径定位",
    "ProxiFyre executable:": "ProxiFyre 可执行文件：",
    "Browse for engine": "浏览引擎",
    "app-config.json:": "配置文件路径：",
    "Open config folder": "打开配置目录",
    "Log directory:": "日志目录：",
    "Engine and GUI settings": "引擎与界面设置",
    "&Engine log level:": "引擎日志级别(&E)：",
    "Takes effect after service restart.": "重启服务后生效。",
    "Bypass local network (LAN) traffic": "绕过局域网（LAN）流量",
    "Allows local network traffic to remain direct while matched internet traffic uses the proxy.": "允许局域网流量保持直连，匹配的互联网流量走代理。",
    "Closing the window hides ProxiFyreUI in the notification area": "关闭窗口时隐藏到通知区域",
    "Diagnostics (credentials are redacted)": "诊断信息（凭据已脱敏）",
    "Service name:": "服务名称：",
    "GUI version:": "界面版本：",
    "Engine version:": "引擎版本：",
    "Architecture:": "系统架构：",
    "Copy diagnostics": "复制诊断信息",
    "Uninstalling preserves app-config.json, its backup, and all log files.": "卸载会保留 app-config.json、其备份及所有日志文件。",
    # 日志页
    "Follow": "跟随",
    "&View filter (display only):": "视图过滤（仅显示）(&V)：",
    "Search:": "搜索：",
    "Copy selected": "复制所选",
    "Copy visible": "复制可见",
    "Clear view": "清除视图",
    "Open log file": "打开日志文件",
    "Open log folder": "打开日志目录",
    "All levels": "所有级别",
    "Waiting for log location": "等待日志路径",
    # 排除页
    "Exclusions bypass proxy routing and take priority over catch-all rules. Matching is permissive: names and path entries use substring-style matching. Exclude VPN/tunnel carrier processes when needed to prevent recursive routing.": "排除项绕过代理路由，优先于通配规则。匹配规则宽松：名称和路径使用子串匹配。需要时排除 VPN/隧道载体进程以防止递归路由。",
    # 规则/排除对话框
    "Add proxy rule": "添加代理规则",
    "Edit proxy rule": "编辑代理规则",
    "Remove the selected proxy rule?": "确定移除所选代理规则？",
    "Remove proxy rule": "移除代理规则",
    "Add exclusion": "添加排除项",
    "Enter a process name or path substring. Exclusion matching is deliberately permissive:": "输入进程名或路径子串。排除匹配刻意保持宽松：",
    "Remove the selected exclusion?": "确定移除所选排除项？",
    "Remove exclusion": "移除排除项",
    "Applications (matching is ordered; first proxy rule wins)": "应用程序（按顺序匹配，首个规则优先）",
    "Match all applications not handled by an earlier rule": "匹配所有未被前面规则处理的应用程序",
    "Add application match": "添加应用程序匹配",
    "Enter an executable name or full/path substring. The value is preserved exactly:": "输入可执行文件名或完整/路径子串。输入值将原样保留：",
    "Select application executable": "选择应用程序可执行文件",
    "Enter the upstream SOCKS5 host.": "输入上游 SOCKS5 主机地址。",
    "The current engine requires an IPv4 upstream endpoint. IPv6 literals are not supported.": "当前引擎要求 IPv4 上游端点，不支持 IPv6 字面量。",
    "Enter an IPv4 literal or hostname without a scheme or path.": "输入不含协议和路径的 IPv4 地址或主机名。",
    "Username and password must either both be entered or both be empty.": "用户名和密码必须同时填写或同时留空。",
    "Select at least one traffic protocol.": "至少选择一种流量协议。",
    "Select at least one destination address family.": "至少选择一种目标地址类型。",
    "Choose TCP or TLS to replace the unsupported transport value.": "选择 TCP 或 TLS 以替换不支持的传输方式。",
    "Rule is valid. No network connection is attempted during validation.": "规则有效。验证过程不会发起网络连接。",
    "TCP, UDP (default)": "TCP、UDP（默认）",
    "IPv4, IPv6 (default)": "IPv4、IPv6（默认）",
    "Credentials configured": "已配置凭据",
    "None": "无",
    "<none>": "<无>",
    # 进程选择器
    "Process name": "进程名",
    "Executable path": "可执行文件路径",
    "Use full executable path when available": "可用时使用完整可执行文件路径",
    "Add running process": "添加运行中的进程",
    "Add executable": "添加可执行文件",
    "Add path": "添加路径",
    "Add manually": "手动添加",
    "Add full path": "添加完整路径",
    "Enumerating running processes": "正在枚举运行中的进程",
    "Refresh": "刷新",
    # 消息框与状态
    "Error": "错误",
    "Warning": "警告",
    "Cancel": "取消",
    "Continue?": "确定继续？",
    "Unknown": "未知",
    "Not loaded": "未加载",
    "Not resolved": "未解析",
    "Configuration valid": "配置有效",
    "Configuration invalid": "配置无效",
    "Configuration unavailable": "配置不可用",
    "Configuration missing": "配置缺失",
    "Configuration not yet saved": "配置尚未保存",
    "Configuration was not saved": "配置未保存",
    "Configuration warnings": "配置警告",
    "Configuration validation": "配置验证",
    "Configuration is invalid": "配置无效",
    "Configuration saved. It will be used on the next service start.": "配置已保存，将在下次服务启动时生效。",
    "Configuration saved. Restart the service to apply it.": "配置已保存，重启服务后生效。",
    "Saved configuration is invalid": "已保存的配置无效",
    "Configuration reloaded from disk.": "已从磁盘重新加载配置。",
    "The configuration could not be reloaded.": "配置重新加载失败。",
    "app-config.json changed outside ProxiFyreUI after it was loaded.": "app-config.json 在 ProxiFyreUI 加载后被外部修改。",
    "External configuration change": "外部配置变更",
    "The external configuration could not be loaded.": "外部配置加载失败。",
    "The live configuration was not changed.": "当前配置未更改。",
    "There are unsaved edits. The service will use the configuration currently on disk, not these edits.": "存在未保存的编辑，服务将使用磁盘上的当前配置而非这些编辑。",
    "Unsaved edits": "未保存的编辑",
    "Unsaved changes": "有未保存的更改",
    "There are unsaved configuration changes. Continuing will discard them.": "存在未保存的配置更改，继续将丢弃它们。",
    "Discard unsaved changes": "放弃未保存的更改",
    "Applied": "已应用",
    "Saved, restart required": "已保存，需重启服务",
    "Saved; service not running": "已保存；服务未运行",
    "Running; apply state unknown": "运行中；应用状态未知",
    "The live app-config.json is missing. A blank unsaved configuration was created.": "未找到 app-config.json，已创建空白配置（未保存）。",
    "The live app-config.json is missing. A sample was loaded as unsaved working configuration.": "未找到 app-config.json，已加载示例作为未保存的工作配置。",
    "Add at least one valid proxy rule, then save before starting the service.": "请至少添加一条有效代理规则并保存后再启动服务。",
    "Log file not available": "日志文件不可用",
    "Opened ": "已打开 ",
    "The current log file could not be opened.": "当前日志文件无法打开。",
    "No ProxiFyre log file is available yet. Start the service or reload the Logs tab after a log is created.": "暂无日志文件。请先启动服务，或在日志生成后重新加载“日志”页。",
    "Redacted diagnostics copied to the clipboard.": "脱敏诊断信息已复制到剪贴板。",
    "Diagnostics could not be copied.": "诊断信息复制失败。",
    "View cleared. Service log files were not deleted.": "视图已清除。服务日志文件未删除。",
    "Service: ": "服务：",
    "Service: Unknown": "服务：未知",
    "Open ProxiFyre": "打开 ProxiFyre",
    "Open logs": "打开日志",
    "Exit": "退出",
    "Select executable": "选择可执行文件",
    "32-bit": "32 位",
    "64-bit": "64 位",
    "Enter value": "输入值",
    "Value:": "值：",
    "ProxiFyre service": "ProxiFyre 服务",
}

# ---------------- PE/CLR/#US 解析 ----------------
def rva2off(rva, sections):
    for vaddr, vsize, rawptr, rawsize in sections:
        if vaddr <= rva < vaddr + max(vsize, rawsize):
            return rawptr + (rva - vaddr)
    raise ValueError("bad rva")

def find_us_stream(data):
    e_lfanew = struct.unpack_from("<I", data, 0x3C)[0]
    coff = e_lfanew + 4
    num_sections = struct.unpack_from("<H", data, coff + 2)[0]
    opt_size = struct.unpack_from("<H", data, coff + 16)[0]
    opt = coff + 20
    magic = struct.unpack_from("<H", data, opt)[0]
    dd_off = opt + (96 if magic == 0x10B else 112)
    com_rva = struct.unpack_from("<I", data, dd_off + 14 * 8)[0]
    sect = opt + opt_size
    sections = []
    for i in range(num_sections):
        s = sect + i * 40
        vsize, vaddr, rawsize, rawptr = struct.unpack_from("<IIII", data, s + 8)
        sections.append((vaddr, vsize, rawptr, rawsize))
    clr = rva2off(com_rva, sections)
    meta_rva = struct.unpack_from("<I", data, clr + 8)[0]
    meta = rva2off(meta_rva, sections)
    ver_len = struct.unpack_from("<I", data, meta + 12)[0]
    p = meta + 16 + ver_len
    p = (p + 3) & ~3
    p += 2  # flags
    stream_count = struct.unpack_from("<H", data, p)[0]
    p += 2  # streams count
    for _ in range(stream_count):
        off, size = struct.unpack_from("<II", data, p)
        p += 8
        name_end = data.index(b"\0", p)
        name = data[p:name_end].decode("ascii")
        p = (name_end + 1 + 3) & ~3
        if name == "#US":
            return meta + off, size
    raise ValueError("#US not found")

def read_varint(data, p):
    b0 = data[p]
    if b0 & 0x80 == 0:
        return b0, 1
    if b0 & 0xC0 == 0x80:
        return ((b0 & 0x3F) << 8) | data[p + 1], 2
    return ((b0 & 0x1F) << 24) | (data[p + 1] << 16) | (data[p + 2] << 8) | data[p + 3], 4

def encode_varint_min(v):
    if v < 0x80:
        return bytes([v])
    if v < 0x4000:
        return bytes([0x80 | (v >> 8), v & 0xFF])
    return bytes([0xC0 | ((v >> 24) & 0x1F), (v >> 16) & 0xFF, (v >> 8) & 0xFF, v & 0xFF])

def main(apply=False):
    data = bytearray(open(DLL, "rb").read())
    us_off, us_size = find_us_stream(data)
    entries = []
    p = us_off + 1  # 首个 0 字节
    while p < us_off + us_size:
        length, hdr = read_varint(data, p)
        if length == 0:
            p += hdr
            continue
        entries.append((p, length, hdr))
        p += hdr + length

    hit = miss = skip = 0
    skipped = []
    originals = set()
    for off, length, hdr in entries:
        blob = bytes(data[off + hdr: off + hdr + length])
        text = blob.decode("utf-16-le", errors="ignore").rstrip("\0")
        originals.add(text)
        if text not in M:
            continue
        zh = M[text]
        new_data = zh.encode("utf-16-le") + b"\x00\x00"
        if len(new_data) > length:
            skip += 1
            skipped.append((text, f"too long (need {len(new_data)} > {length})"))
            continue
        # 原地写入：最小编码头 + 中文数据 + 尾部补零，总占用 hdr+length 不变
        new_hdr = encode_varint_min(len(new_data))
        total_new = len(new_hdr) + len(new_data)
        assert total_new <= hdr + length, "blob overflow"
        data[off: off + hdr + length] = new_hdr + new_data + b"\x00" * (hdr + length - total_new)
        hit += 1

    mapped = len(M)
    originals = {bytes(data[o + h: o + h + l]).decode("utf-16-le", "ignore").rstrip("\0") for o, l, h in entries}
    notfound = [k for k in M if k not in originals]
    print(f"#US entries: {len(entries)}")
    print(f"mapping entries: {mapped}, replaced: {hit}, skipped: {skip}, not-found: {len(notfound)}")
    for t, why in skipped:
        print(f"  SKIP [{why}]: {t[:70]}")
    for t in notfound:
        print(f"  NOTFOUND: {t[:70]}")
    if apply:
        open(DLL, "wb").write(bytes(data))
        print(f"WRITTEN: {DLL}")
    return hit

if __name__ == "__main__":
    main(apply="--apply" in sys.argv)
