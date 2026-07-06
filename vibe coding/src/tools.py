import os
import subprocess
from datetime import datetime


class Tool:
    def __init__(self, name, description, parameters, handler,
                 requires_approval=False):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.handler = handler
        self.requires_approval = requires_approval

    def to_openai_spec(self):
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }

    def execute(self, arguments):
        return self.handler(arguments)


class ToolRegistry:
    def __init__(self):
        self._tools = {}

    def register(self, tool):
        self._tools[tool.name] = tool

    def get(self, name):
        return self._tools.get(name)

    def list_specs(self):
        return [t.to_openai_spec() for t in self._tools.values()]


# ============================================================
# 只读工具
# ============================================================

def _tool_get_time(_args):
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _tool_list_dir(args):
    path = args.get("path", ".")
    if not os.path.isdir(path):
        return f"错误：目录不存在 - {path}"
    try:
        entries = os.listdir(path)
        if not entries:
            return f"目录 '{path}' 为空。"
        lines = [f"目录 '{path}' 的内容："]
        for name in sorted(entries):
            full = os.path.join(path, name)
            tag = "[DIR]" if os.path.isdir(full) else "[FILE]"
            lines.append(f"  {tag} {name}")
        return "\n".join(lines)
    except PermissionError:
        return f"错误：无权访问目录 - {path}"


def _tool_read_file(args):
    path = args.get("path", "")
    if not path:
        return "错误：未指定文件路径。"
    if not os.path.isfile(path):
        return f"错误：文件不存在或不是普通文件 - {path}"
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        if len(content) > 3000:
            content = content[:3000] + "\n...(内容已截断，仅显示前3000字符)"
        return content
    except PermissionError:
        return f"错误：无权读取文件 - {path}"
    except UnicodeDecodeError:
        return f"错误：文件不是UTF-8文本文件 - {path}"


# ============================================================
# Advanced 工具（需要 approval 和 workspace）
# ============================================================

_workspace_dir = "workspace"
_approval_store = None


def set_workspace(path):
    global _workspace_dir
    _workspace_dir = path
    os.makedirs(_workspace_dir, exist_ok=True)


def get_workspace():
    return _workspace_dir


def set_approval_store(store):
    global _approval_store
    _approval_store = store


def _safe_path(path):
    """将相对路径解析到 workspace 内，防止路径穿越。"""
    abs_path = os.path.abspath(os.path.join(_workspace_dir, path))
    ws_abs = os.path.abspath(_workspace_dir)
    if not abs_path.startswith(ws_abs):
        raise ValueError(f"路径必须在 workspace 内: {path}")
    return abs_path


def _tool_write_file(args):
    path = args.get("path", "")
    content = args.get("content", "")
    if not path:
        return "错误：未指定文件路径。"

    try:
        abs_path = _safe_path(path)
    except ValueError as e:
        return str(e)

    if _approval_store:
        existing = _approval_store.find_by_tool("write_file", path)
        if existing is None:
            approval = _approval_store.create(
                "write_file",
                {"path": path, "content": content},
                f"写文件: {path} ({len(content)} 字符)",
            )
            return (
                f"[等待审批] {approval.id}\n"
                f"操作：写入文件 {path}（{len(content)} 字符）\n"
                f"请使用 /approve {approval.id} 批准，"
                f"或 /deny {approval.id} 拒绝。"
            )
        if existing.status == "pending":
            return f"[等待审批] 操作已提交，请使用 /approve {existing.id} 审批。"
        if existing.status == "denied":
            return f"[已拒绝] 文件写入被拒绝: {path}"
        _approval_store.remove(existing.id)
        # 使用审批时保存的 content
        content = existing.arguments.get("content", content)

    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    with open(abs_path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"文件写入成功: {path} ({len(content)} 字符)"


def _tool_run_shell(args):
    command = args.get("command", "")
    if not command:
        return "错误：未指定命令。"

    cwd = _workspace_dir

    if _approval_store:
        existing = _approval_store.find_by_tool("run_shell", command)
        if existing is None:
            approval = _approval_store.create(
                "run_shell",
                {"command": command},
                f"运行命令: {command}",
            )
            return (
                f"[等待审批] {approval.id}\n"
                f"操作：运行命令 `{command}`（工作目录: {cwd}）\n"
                f"请使用 /approve {approval.id} 批准，"
                f"或 /deny {approval.id} 拒绝。"
            )
        if existing.status == "pending":
            return f"[等待审批] 操作已提交，请使用 /approve {existing.id} 审批。"
        if existing.status == "denied":
            return f"[已拒绝] 命令执行被拒绝: {command}"
        _approval_store.remove(existing.id)
        command = existing.arguments.get("command", command)

    try:
        result = subprocess.run(
            command, shell=True, cwd=cwd,
            capture_output=True, text=True, timeout=30,
        )
        out = result.stdout
        if result.stderr:
            out += f"\n[stderr]\n{result.stderr}"
        if not out.strip():
            out = f"(exit code: {result.returncode})"
        if len(out) > 2000:
            out = out[:2000] + "\n...(输出已截断)"
        return out
    except subprocess.TimeoutExpired:
        return "错误：命令执行超时(30秒)。"


# ============================================================

def create_default_registry(approval_store=None):
    set_approval_store(approval_store)
    set_workspace("workspace")

    registry = ToolRegistry()
    registry.register(Tool(
        name="get_time",
        description="获取当前的日期和时间。",
        parameters={"type": "object", "properties": {}, "required": []},
        handler=_tool_get_time,
    ))
    registry.register(Tool(
        name="list_dir",
        description="列出指定目录下的文件和子目录。",
        parameters={
            "type": "object",
            "properties": {
                "path": {"type": "string",
                         "description": "目录路径，默认为当前目录 '.'"}
            },
            "required": []
        },
        handler=_tool_list_dir,
    ))
    registry.register(Tool(
        name="read_file",
        description="读取文本文件内容（UTF-8），最多3000字符。",
        parameters={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "文件路径"}
            },
            "required": ["path"]
        },
        handler=_tool_read_file,
    ))
    registry.register(Tool(
        name="write_file",
        description="在 workspace 内写入文件。需要审批。",
        parameters={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "相对于 workspace 的文件路径"},
                "content": {"type": "string", "description": "文件内容"},
            },
            "required": ["path", "content"]
        },
        handler=_tool_write_file,
        requires_approval=True,
    ))
    registry.register(Tool(
        name="run_shell",
        description="在 workspace 目录下执行 shell 命令。需要审批。",
        parameters={
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "要执行的命令"},
            },
            "required": ["command"]
        },
        handler=_tool_run_shell,
        requires_approval=True,
    ))
    return registry
