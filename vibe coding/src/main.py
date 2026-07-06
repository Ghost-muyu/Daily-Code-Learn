import sys
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


def _session_new(store, _agent, _memory, _approval, _scheduler, _skill_mgr):
    session = store.create()
    print(f"Created session: {session.session_id}")
    return session


def _session_list(store, _agent, _memory, _approval, _scheduler, _skill_mgr, current):
    sessions = store.list_all()
    if not sessions:
        print("(no sessions)")
        return current
    for s in sessions:
        marker = "*" if s.session_id == current.session_id else " "
        print(f"{marker} {s.session_id}  {s.title:12s}  "
              f"messages={s.message_count():<4}  updated={s.updated_at[:16]}")
    return current


def _session_switch(store, _agent, _memory, _approval, _scheduler, _skill_mgr,
                    current, session_id):
    if not session_id:
        print("Usage: /session switch <sessionId>")
        return current
    session = store.get(session_id)
    if session is None:
        print(f"Session not found: {session_id}")
        return current
    print(f"Switched to session: {session_id}")
    if session.messages:
        print("History:")
        for m in session.messages[-6:]:
            print(f"{m['role'].capitalize()}> {m['content'][:80]}")
    return session


def _session_rename(store, _agent, _memory, _approval, _scheduler, _skill_mgr,
                    current, session_id, new_title):
    if not session_id or not new_title:
        print("Usage: /session rename <sessionId> <title>")
        return current
    session = store.rename(session_id, new_title)
    if session is None:
        print(f"Session not found: {session_id}")
    else:
        print(f"Renamed {session_id} to \"{new_title}\"")
    return current


def _session_delete(store, _agent, _memory, _approval, _scheduler, _skill_mgr,
                    current, session_id):
    if not session_id:
        print("Usage: /session delete <sessionId>")
        return current
    store.delete(session_id)
    print(f"Deleted session: {session_id}")
    if session_id == current.session_id:
        sessions = store.list_all()
        if not sessions:
            return store.create()
        return sessions[0]
    return current


# --- Memory commands ---

def _memory_add(memory_store, content):
    if not content:
        print("Usage: /memory add <content>")
        return
    mem_id = memory_store.add(content)
    print(f"Added memory: {mem_id}")


def _memory_list(memory_store):
    memories = memory_store.list_all()
    if not memories:
        print("(no memories)")
        return
    for m in memories:
        print(f"  {m['id']}  {m['content'][:80]}  ({m['created_at'][:10]})")


def _memory_delete(memory_store, memory_id):
    if not memory_id:
        print("Usage: /memory delete <memoryId>")
        return
    if memory_store.delete(memory_id):
        print(f"Deleted memory: {memory_id}")
    else:
        print(f"Memory not found: {memory_id}")


# --- Approval commands ---

def _approve(approval_store, approval_id):
    if not approval_id:
        print("Usage: /approve <approvalId>")
        return
    a = approval_store.get(approval_id)
    if a is None:
        print(f"Approval not found: {approval_id}")
        return
    a.approve()
    print(f"Approved: {a.description}")
    print("请让 AI 重新调用该工具以执行操作。")


def _deny(approval_store, approval_id):
    if not approval_id:
        print("Usage: /deny <approvalId>")
        return
    a = approval_store.get(approval_id)
    if a is None:
        print(f"Approval not found: {approval_id}")
        return
    a.deny()
    print(f"Denied: {a.description}")


def _check_pending_approvals(approval_store):
    pending = approval_store.list_pending()
    if pending:
        print(f"\n[!] 有 {len(pending)} 个待审批操作：")
        for a in pending:
            print(f"  {a.id}: {a.description}")


# --- Task commands ---

def _task_add(scheduler, current, content, interval_str=None):
    if not content:
        print("Usage: /task add <content> [interval_seconds]")
        return
    interval = None
    if interval_str:
        try:
            interval = int(interval_str)
        except ValueError:
            print(f"Invalid interval: {interval_str}")
            return
    task_id = scheduler.add(content, current.session_id, interval)
    tag = f"每 {interval} 秒" if interval else "一次性"
    print(f"Added task: {task_id} ({tag})")


def _task_list(scheduler):
    tasks = scheduler.list_all()
    if not tasks:
        print("(no tasks)")
        return
    for t in tasks:
        tag = f"每{t['interval_seconds']}秒" if t.get("interval_seconds") else "一次性"
        print(f"  {t['id']}  [{t['status']}] {t['content'][:50]}  "
              f"next={t['next_run'][:16]}  ({tag})")


def _task_cancel(scheduler, task_id):
    if not task_id:
        print("Usage: /task cancel <taskId>")
        return
    if scheduler.cancel(task_id):
        print(f"Cancelled task: {task_id}")
    else:
        print(f"Task not found: {task_id}")


# --- Skill commands ---

def _skill_list(skill_mgr):
    skills = skill_mgr.list_all()
    if not skills:
        print("(no skills)")
        return
    for s in skills:
        print(f"  {s.name}: {s.description}")


def _skill_use(skill_mgr, agent, skill_name):
    if not skill_name:
        print("Usage: /skill use <name>")
        return
    if agent.activate_skill(skill_name):
        print(f"Activated skill: {skill_name}")
    else:
        print(f"Skill not found: {skill_name}")


def _skill_off(agent):
    agent.deactivate_skill()
    print("Skill deactivated.")


# --- Workspace command ---

def _workspace_set(path):
    from src.tools import set_workspace
    if not path:
        from src.tools import get_workspace
        print(f"Current workspace: {get_workspace()}")
        return
    set_workspace(path)
    print(f"Workspace set to: {path}")


# --- Session command definitions ---
# Each: (handler, arg_count) where arg_count is how many rest args the handler takes

SESSION_COMMANDS = {
    "new":    (_session_new,    0),
    "list":   (_session_list,   0),
    "switch": (_session_switch, 1),
    "rename": (_session_rename, 2),
    "delete": (_session_delete, 1),
}


def _do_compact(config, store, current):
    old_count = current.message_count()
    try:
        changed = compact_session(
            current, config["base_url"], config["api_key"], config["model"])
    except CompactionError as e:
        print(f"[compact] 压缩失败: {e}")
        return

    if not changed:
        print(f"[compact] 消息数 {old_count}，无需压缩。")
        return

    store.save(current)
    print(f"[compact] session {current.session_id}: "
          f"old_messages={old_count}, recent_messages={current.message_count()}")
    print(f"[compact] summary: {current.summary[:200]}")


def handle_command(user_input, store, agent, memory_store, current, config,
                   approval_store, scheduler, skill_mgr):
    parts = user_input.split(maxsplit=2)
    cmd = parts[0][1:]
    sub = parts[1] if len(parts) > 1 else None
    rest = parts[2] if len(parts) > 2 else ""

    if cmd == "exit":
        return current, True

    if cmd == "compact":
        _do_compact(config, store, current)
        return current, False

    if cmd == "approve":
        _approve(approval_store, rest)
        return current, False

    if cmd == "deny":
        _deny(approval_store, rest)
        return current, False

    if cmd == "workspace":
        _workspace_set(rest)
        return current, False

    if cmd == "session":
        if sub not in SESSION_COMMANDS:
            print(f"Unknown: /session {sub}. "
                  f"Available: {', '.join(SESSION_COMMANDS)}")
            return current, False
        handler, arg_count = SESSION_COMMANDS[sub]
        if arg_count == 0:
            return handler(store, agent, memory_store,
                          approval_store, scheduler, skill_mgr), False
        elif arg_count == 1:
            return handler(store, agent, memory_store,
                          approval_store, scheduler, skill_mgr,
                          current, rest), False
        elif arg_count == 2:
            parts2 = rest.split(maxsplit=1)
            sid = parts2[0] if parts2 else ""
            val = parts2[1] if len(parts2) > 1 else ""
            return handler(store, agent, memory_store,
                          approval_store, scheduler, skill_mgr,
                          current, sid, val), False

    if cmd == "memory":
        if sub == "add":
            _memory_add(memory_store, rest)
        elif sub == "list":
            _memory_list(memory_store)
        elif sub == "delete":
            _memory_delete(memory_store, rest)
        else:
            print(f"Unknown: /memory {sub}. Available: add, list, delete")
        return current, False

    if cmd == "task":
        if sub == "add":
            parts2 = rest.split(maxsplit=1)
            content = parts2[0] if parts2 else ""
            interval_str = parts2[1] if len(parts2) > 1 else None
            _task_add(scheduler, current, content, interval_str)
        elif sub == "list":
            _task_list(scheduler)
        elif sub == "cancel":
            _task_cancel(scheduler, rest)
        else:
            print(f"Unknown: /task {sub}. Available: add, list, cancel")
        return current, False

    if cmd == "skill":
        if sub == "list":
            _skill_list(skill_mgr)
        elif sub == "use":
            _skill_use(skill_mgr, agent, rest)
        elif sub == "off":
            _skill_off(agent)
        else:
            print(f"Unknown: /skill {sub}. Available: list, use, off")
        return current, False

    return None, False


def main():
    try:
        config = load_config()
    except ConfigError as e:
        print(f"[错误] {e}", file=sys.stderr)
        sys.exit(1)

    store = SessionStore()
    memory_store = MemoryStore()
    approval_store = ApprovalStore()
    scheduler = Scheduler()
    skill_mgr = SkillManager()
    skill_mgr.scan()

    tool_registry = create_default_registry(approval_store=approval_store)
    agent = Agent(config, tool_registry=tool_registry, skill_manager=skill_mgr)

    sessions = store.list_all()
    if sessions:
        current = sessions[0]
        print(f"Restored session: {current.session_id}")
    else:
        current = store.create()
        print(f"Created session: {current.session_id}")

    if skill_mgr.list_all():
        print(f"Available skills: "
              f"{', '.join(s.name for s in skill_mgr.list_all())}")

    print(f"claw started. Type /exit to quit.\n")

    # 启动时检查到期任务
    _check_due_tasks(scheduler, agent, store, memory_store, config)

    while True:
        try:
            user_input = input("User> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nbye.")
            break

        if not user_input:
            continue

        if user_input.startswith("/"):
            result, should_exit = handle_command(
                user_input, store, agent, memory_store, current, config,
                approval_store, scheduler, skill_mgr)
            if should_exit:
                print("bye.")
                break
            if result is not None:
                current = result
            continue

        # 显示待审批提示
        _check_pending_approvals(approval_store)

        try:
            reply = agent.run_turn(current, user_input,
                                   memory_store=memory_store)
            store.save(current)
            print(f"Assistant> {reply}\n")
        except LLMError as e:
            print(f"[错误] {e}\n")
        except (SessionStoreError, MemoryStoreError) as e:
            print(f"[警告] {e}\n")
            continue

        # 自动压缩检查
        if needs_compaction(current):
            _do_compact(config, store, current)

        # 检查到期任务
        _check_due_tasks(scheduler, agent, store, memory_store, config)


def _check_due_tasks(scheduler, agent, store, memory_store, config):
    """执行到期的定时任务。"""
    due_tasks = scheduler.get_due()
    for task in due_tasks:
        session = store.get(task["session_id"])
        if session is None:
            scheduler.mark_failed(task["id"], "Session not found")
            continue
        print(f"\n[task] 执行定时任务: {task['id']} - {task['content'][:50]}")
        try:
            reply = agent.run_turn(session, task["content"],
                                   memory_store=memory_store)
            store.save(session)
            scheduler.mark_completed(task["id"], reply)
            print(f"[task] 完成: {reply[:100]}")
        except LLMError as e:
            scheduler.mark_failed(task["id"], str(e))
            print(f"[task] 失败: {e}")


if __name__ == "__main__":
    main()
