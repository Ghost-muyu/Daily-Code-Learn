import json
import os
from src.session import Session


class SessionStoreError(Exception):
    pass


class SessionStore:
    def __init__(self, data_dir="data/sessions"):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)

    def _path(self, session_id):
        return os.path.join(self.data_dir, f"{session_id}.json")

    def create(self, title="新会话"):
        session = Session(title=title)
        self.save(session)
        return session

    def get(self, session_id):
        path = self._path(session_id)
        if not os.path.exists(path):
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            raise SessionStoreError(
                f"会话文件损坏或无法读取 ({session_id}): {e}"
            )
        return Session.from_dict(data)

    def list_all(self):
        sessions = []
        if not os.path.isdir(self.data_dir):
            return sessions
        for filename in sorted(os.listdir(self.data_dir)):
            if not filename.endswith(".json"):
                continue
            session_id = filename[:-5]
            session = self.get(session_id)
            if session:
                sessions.append(session)
        # Sort by updated_at descending
        sessions.sort(key=lambda s: s.updated_at, reverse=True)
        return sessions

    def save(self, session):
        path = self._path(session.session_id)
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(session.to_dict(), f, ensure_ascii=False, indent=2)
        except IOError as e:
            raise SessionStoreError(
                f"保存会话失败 ({session.session_id}): {e}"
            )

    def delete(self, session_id):
        path = self._path(session_id)
        if os.path.exists(path):
            try:
                os.remove(path)
            except IOError as e:
                raise SessionStoreError(
                    f"删除会话失败 ({session_id}): {e}"
                )

    def rename(self, session_id, new_title):
        session = self.get(session_id)
        if session is None:
            return None
        session.title = new_title
        self.save(session)
        return session
