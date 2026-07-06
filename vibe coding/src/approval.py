import uuid
from datetime import datetime


class Approval:
    def __init__(self, tool_name, arguments, description, key=""):
        self.id = f"approval_{uuid.uuid4().hex[:6]}"
        self.tool_name = tool_name
        self.arguments = arguments
        self.description = description
        self.key = key  # 用于快速查找的匹配键
        self.status = "pending"  # pending | approved | denied
        self.created_at = datetime.now().isoformat()
        self.resolved_at = None

    def approve(self):
        self.status = "approved"
        self.resolved_at = datetime.now().isoformat()

    def deny(self):
        self.status = "denied"
        self.resolved_at = datetime.now().isoformat()


class ApprovalStore:
    def __init__(self):
        self._pending = {}  # id -> Approval

    def create(self, tool_name, arguments, description):
        key = arguments.get("path") or arguments.get("command") or ""
        approval = Approval(tool_name, arguments, description, key=key)
        self._pending[approval.id] = approval
        return approval

    def get(self, approval_id):
        return self._pending.get(approval_id)

    def list_pending(self):
        return [a for a in self._pending.values() if a.status == "pending"]

    def remove(self, approval_id):
        self._pending.pop(approval_id, None)

    def find_by_tool(self, tool_name, key):
        """根据工具名和关键参数查找审批（不区分状态）。"""
        for a in self._pending.values():
            if a.tool_name == tool_name and a.key == key:
                return a
        return None
