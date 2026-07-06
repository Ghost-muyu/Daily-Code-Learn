import uuid
from datetime import datetime


class Session:
    def __init__(self, session_id=None, title="新会话",
                 messages=None, created_at=None, updated_at=None,
                 summary=""):
        self.session_id = session_id or f"session_{uuid.uuid4().hex[:8]}"
        self.title = title
        self.messages = messages or []
        self.summary = summary
        self.created_at = created_at or datetime.now().isoformat()
        self.updated_at = updated_at or self.created_at

    def add_user(self, content):
        self.messages.append({"role": "user", "content": content})
        self.updated_at = datetime.now().isoformat()

    def add_assistant(self, content):
        self.messages.append({"role": "assistant", "content": content})
        self.updated_at = datetime.now().isoformat()

    def message_count(self):
        return len(self.messages)

    def to_dict(self):
        return {
            "session_id": self.session_id,
            "title": self.title,
            "messages": self.messages,
            "summary": self.summary,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            session_id=data["session_id"],
            title=data["title"],
            messages=data.get("messages", []),
            summary=data.get("summary", ""),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
