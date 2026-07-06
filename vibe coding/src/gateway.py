"""
SJTUClaw Gateway — Web 图形化入口。
启动方式: python -m src.gateway
复用同一套 runtime: session_store, memory_store, agent, tool_registry。
"""
import os
import json
from flask import Flask, request, jsonify, send_from_directory

from src.config import load_config, ConfigError
from src.llm import LLMError
from src.session_store import SessionStore, SessionStoreError
from src.memory_store import MemoryStore, MemoryStoreError
from src.agent import Agent
from src.tools import create_default_registry
from src.compaction import compact_session, needs_compaction, CompactionError
from src.approval import ApprovalStore
from src.scheduler import Scheduler
from src.skills import SkillManager

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = Flask(__name__, template_folder="../templates")

# --- 全局 runtime（所有请求复用） ---
_config = None
_store = None
_memory_store = None
_tool_registry = None
_agent = None
_current_session = None
_approval_store = None
_scheduler = None
_skill_mgr = None

# 附件元数据按 session 隔离
_attachments = {}  # session_id -> [{"name": ..., "path": ..., "size": ...}]


def _init_runtime():
    global _config, _store, _memory_store, _tool_registry, _agent
    global _current_session, _approval_store, _scheduler, _skill_mgr
    try:
        _config = load_config()
    except ConfigError as e:
        print(f"[错误] {e}")
        return False
    _store = SessionStore()
    _memory_store = MemoryStore()
    _approval_store = ApprovalStore()
    _scheduler = Scheduler()
    _skill_mgr = SkillManager()
    _skill_mgr.scan()

    _tool_registry = create_default_registry(approval_store=_approval_store)
    _agent = Agent(_config, tool_registry=_tool_registry,
                   skill_manager=_skill_mgr)

    sessions = _store.list_all()
    _current_session = sessions[0] if sessions else _store.create()
    print(f"Gateway started. Current session: {_current_session.session_id}")

    skills = _skill_mgr.list_all()
    if skills:
        print(f"Skills: {', '.join(s.name for s in skills)}")
    return True


# ==================== 页面 ====================

@app.route("/")
def index():
    return send_from_directory("../templates", "index.html")


# ==================== Session API ====================

@app.route("/api/sessions", methods=["GET"])
def api_sessions():
    sessions = _store.list_all()
    return jsonify([{
        "session_id": s.session_id,
        "title": s.title,
        "message_count": s.message_count(),
        "updated_at": s.updated_at,
    } for s in sessions])


@app.route("/api/sessions", methods=["POST"])
def api_create_session():
    data = request.get_json(silent=True) or {}
    title = data.get("title", "新会话")
    session = _store.create(title=title)
    return jsonify({"session_id": session.session_id, "title": session.title})


@app.route("/api/switch", methods=["POST"])
def api_switch():
    global _current_session
    data = request.get_json(silent=True) or {}
    session_id = data.get("session_id", "")
    session = _store.get(session_id)
    if session is None:
        return jsonify({"error": f"Session not found: {session_id}"}), 404
    _current_session = session
    return jsonify({
        "session_id": session.session_id,
        "title": session.title,
        "messages": _safe_messages(session.messages),
    })


# ==================== Chat API ====================

@app.route("/api/chat", methods=["POST"])
def api_chat():
    global _current_session
    data = request.get_json(silent=True) or {}
    user_input = data.get("message", "").strip()
    if not user_input:
        return jsonify({"error": "消息不能为空"}), 400

    try:
        reply = _agent.run_turn(_current_session, user_input,
                                memory_store=_memory_store)
        _store.save(_current_session)
    except LLMError as e:
        return jsonify({"error": str(e)}), 500
    except (SessionStoreError, MemoryStoreError) as e:
        return jsonify({"error": f"保存失败: {e}"}), 500

    # 自动压缩检查
    compact_info = None
    if needs_compaction(_current_session):
        try:
            old = _current_session.message_count()
            compact_session(_current_session,
                            _config["base_url"], _config["api_key"],
                            _config["model"])
            _store.save(_current_session)
            compact_info = {
                "old_messages": old,
                "new_messages": _current_session.message_count(),
                "summary": _current_session.summary[:200],
            }
        except CompactionError:
            pass

    # 待审批列表
    pending_approvals = [{
        "id": a.id,
        "tool_name": a.tool_name,
        "description": a.description,
    } for a in _approval_store.list_pending()]

    # 到期任务检查
    _check_due_tasks()

    return jsonify({
        "reply": reply,
        "session_id": _current_session.session_id,
        "compact": compact_info,
        "pending_approvals": pending_approvals,
    })


@app.route("/api/sessions/<session_id>/messages", methods=["GET"])
def api_messages(session_id):
    session = _store.get(session_id)
    if session is None:
        return jsonify({"error": f"Session not found: {session_id}"}), 404
    return jsonify(_safe_messages(session.messages))


# ==================== Upload API ====================

@app.route("/api/upload", methods=["POST"])
def api_upload():
    global _current_session
    if "file" not in request.files:
        return jsonify({"error": "未选择文件"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "文件名为空"}), 400

    sid = _current_session.session_id
    session_dir = os.path.join(UPLOAD_DIR, sid)
    os.makedirs(session_dir, exist_ok=True)
    save_path = os.path.join(session_dir, file.filename)
    file.save(save_path)

    meta = {
        "name": file.filename,
        "path": save_path,
        "size": os.path.getsize(save_path),
    }
    _attachments.setdefault(sid, []).append(meta)

    return jsonify({"ok": True, "file": meta})


@app.route("/api/attachments", methods=["GET"])
def api_attachments():
    sid = _current_session.session_id
    return jsonify(_attachments.get(sid, []))


# ==================== Approval API ====================

@app.route("/api/approvals", methods=["GET"])
def api_approvals():
    pending = _approval_store.list_pending()
    return jsonify([{
        "id": a.id,
        "tool_name": a.tool_name,
        "description": a.description,
        "status": a.status,
        "created_at": a.created_at,
    } for a in pending])


@app.route("/api/approve/<approval_id>", methods=["POST"])
def api_approve(approval_id):
    a = _approval_store.get(approval_id)
    if a is None:
        return jsonify({"error": f"Approval not found: {approval_id}"}), 404
    a.approve()
    return jsonify({"ok": True, "id": approval_id, "status": "approved"})


@app.route("/api/deny/<approval_id>", methods=["POST"])
def api_deny(approval_id):
    a = _approval_store.get(approval_id)
    if a is None:
        return jsonify({"error": f"Approval not found: {approval_id}"}), 404
    a.deny()
    return jsonify({"ok": True, "id": approval_id, "status": "denied"})


# ==================== Task API ====================

@app.route("/api/tasks", methods=["GET"])
def api_tasks():
    tasks = _scheduler.list_all()
    return jsonify(tasks)


@app.route("/api/tasks", methods=["POST"])
def api_create_task():
    global _current_session
    data = request.get_json(silent=True) or {}
    content = data.get("content", "").strip()
    interval_seconds = data.get("interval_seconds")
    if not content:
        return jsonify({"error": "任务内容不能为空"}), 400
    task_id = _scheduler.add(content, _current_session.session_id,
                             interval_seconds)
    return jsonify({"ok": True, "task_id": task_id})


@app.route("/api/tasks/<task_id>/cancel", methods=["POST"])
def api_cancel_task(task_id):
    if _scheduler.cancel(task_id):
        return jsonify({"ok": True})
    return jsonify({"error": f"Task not found: {task_id}"}), 404


# ==================== Skill API ====================

@app.route("/api/skills", methods=["GET"])
def api_skills():
    skills = _skill_mgr.list_all()
    return jsonify([{
        "name": s.name,
        "description": s.description,
    } for s in skills])


@app.route("/api/skills/use", methods=["POST"])
def api_skill_use():
    global _agent
    data = request.get_json(silent=True) or {}
    skill_name = data.get("name", "").strip()
    if not skill_name:
        return jsonify({"error": "Skill name required"}), 400
    if _agent.activate_skill(skill_name):
        return jsonify({"ok": True, "active_skill": skill_name})
    return jsonify({"error": f"Skill not found: {skill_name}"}), 404


@app.route("/api/skills/off", methods=["POST"])
def api_skill_off():
    global _agent
    _agent.deactivate_skill()
    return jsonify({"ok": True, "active_skill": None})


# ==================== 工具函数 ====================

def _safe_messages(messages):
    """过滤掉 tool_calls 的内部字段，只返回可展示的消息。"""
    result = []
    for m in messages:
        if m.get("tool_calls"):
            for tc in m["tool_calls"]:
                result.append({
                    "role": "tool_call",
                    "content": f"[调用工具] {tc['function']['name']}",
                })
        elif m["role"] == "tool":
            result.append({
                "role": "tool_result",
                "content": m["content"][:200],
            })
        else:
            result.append({"role": m["role"], "content": m.get("content", "")})
    return result


def _check_due_tasks():
    """执行到期的定时任务。"""
    due_tasks = _scheduler.get_due()
    for task in due_tasks:
        session = _store.get(task["session_id"])
        if session is None:
            _scheduler.mark_failed(task["id"], "Session not found")
            continue
        print(f"[task] 执行定时任务: {task['id']} - {task['content'][:50]}")
        try:
            reply = _agent.run_turn(session, task["content"],
                                    memory_store=_memory_store)
            _store.save(session)
            _scheduler.mark_completed(task["id"], reply)
            print(f"[task] 完成: {reply[:100]}")
        except LLMError as e:
            _scheduler.mark_failed(task["id"], str(e))
            print(f"[task] 失败: {e}")


# ==================== 入口 ====================

def main():
    if not _init_runtime():
        print("Gateway 启动失败：配置错误。请检查 .env 文件。")
        return
    print("SJTUClaw Gateway: http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=False)


if __name__ == "__main__":
    main()
