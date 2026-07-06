import json
import os
import uuid
from datetime import datetime


class MemoryStoreError(Exception):
    pass


class MemoryStore:
    def __init__(self, path="data/memories.json"):
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not os.path.exists(path):
            self._write([])

    def _read(self):
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            raise MemoryStoreError(f"记忆文件损坏或无法读取: {e}")

    def _write(self, data):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add(self, content):
        memories = self._read()
        mem = {
            "id": f"mem_{uuid.uuid4().hex[:6]}",
            "content": content,
            "created_at": datetime.now().isoformat(),
        }
        memories.append(mem)
        self._write(memories)
        return mem["id"]

    def list_all(self):
        return self._read()

    def delete(self, memory_id):
        memories = self._read()
        filtered = [m for m in memories if m["id"] != memory_id]
        if len(filtered) == len(memories):
            return False
        self._write(filtered)
        return True
