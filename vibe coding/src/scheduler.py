import json
import os
import uuid
import time
from datetime import datetime, timedelta


class Scheduler:
    def __init__(self, path="data/tasks.json"):
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not os.path.exists(path):
            self._write([])

    def _read(self):
        with open(self.path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write(self, data):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add(self, content, session_id, interval_seconds=None,
            run_at=None):
        """添加定时任务。

        interval_seconds: None=一次性, >0=周期性(秒)
        run_at: ISO格式的首次触发时间，默认为now+interval或now+5秒
        """
        now = datetime.now()
        if run_at:
            next_run = run_at
        elif interval_seconds:
            next_run = (now + timedelta(seconds=interval_seconds)).isoformat()
        else:
            next_run = (now + timedelta(seconds=5)).isoformat()

        task = {
            "id": f"task_{uuid.uuid4().hex[:6]}",
            "content": content,
            "session_id": session_id,
            "interval_seconds": interval_seconds,
            "next_run": next_run,
            "status": "pending",
            "history": [],
            "created_at": now.isoformat(),
        }
        tasks = self._read()
        tasks.append(task)
        self._write(tasks)
        return task["id"]

    def list_all(self):
        return self._read()

    def cancel(self, task_id):
        tasks = self._read()
        for t in tasks:
            if t["id"] == task_id:
                t["status"] = "cancelled"
                self._write(tasks)
                return True
        return False

    def get_due(self):
        """返回所有到期的 pending 任务。"""
        now = datetime.now().isoformat()
        tasks = self._read()
        due = []
        for t in tasks:
            if t["status"] == "pending" and t["next_run"] <= now:
                due.append(t)
        return due

    def mark_completed(self, task_id, result):
        tasks = self._read()
        for t in tasks:
            if t["id"] != task_id:
                continue
            t["history"].append({
                "run_at": datetime.now().isoformat(),
                "result": result[:200],
                "status": "ok",
            })
            if t["interval_seconds"]:
                # 周期性：计算下次触发
                t["next_run"] = (
                    datetime.now() + timedelta(seconds=t["interval_seconds"])
                ).isoformat()
                t["status"] = "pending"
            else:
                t["status"] = "completed"
            self._write(tasks)
            return

    def mark_failed(self, task_id, error):
        tasks = self._read()
        for t in tasks:
            if t["id"] != task_id:
                continue
            t["history"].append({
                "run_at": datetime.now().isoformat(),
                "result": str(error)[:200],
                "status": "error",
            })
            t["status"] = "pending"  # 保留以便重试
            self._write(tasks)
            return
