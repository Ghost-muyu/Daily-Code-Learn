from src.llm import call_llm, LLMError

COMPACT_THRESHOLD = 20
KEEP_RECENT = 8
COMPACT_SYSTEM = (
    "你是一个对话摘要助手。你需要将一段对话历史压缩成简洁的摘要。"
    "摘要应保留：当前任务、已完成内容、用户明确的要求和约束、"
    "尚未解决的问题、影响继续回答的重要事实。"
    "应删除：寒暄、重复表达、无关细节、没有继续使用价值的中间过程。"
    "输出直接给出摘要文本，不要添加任何解释或标记。"
)


class CompactionError(Exception):
    pass


def _messages_to_text(messages):
    lines = []
    for m in messages:
        content = m.get("content") or ""
        lines.append(f"[{m['role']}] {content}")
    return "\n".join(lines)


def compact_session(session, base_url, api_key, model):
    total = len(session.messages)
    if total <= KEEP_RECENT:
        return False

    old_messages = session.messages[:total - KEEP_RECENT]
    recent_messages = session.messages[total - KEEP_RECENT:]

    compact_user = f"已有的摘要：\n{session.summary or '（无）'}\n\n"
    compact_user += f"需要压缩的旧对话：\n{_messages_to_text(old_messages)}\n\n"
    compact_user += "请将以上对话压缩为新的摘要。"

    compact_input = [
        {"role": "system", "content": COMPACT_SYSTEM},
        {"role": "user", "content": compact_user},
    ]

    try:
        result = call_llm(
            messages=compact_input,
            base_url=base_url,
            api_key=api_key,
            model=model,
        )
    except LLMError as e:
        raise CompactionError(f"压缩请求失败: {e}")

    new_summary = result["content"]
    if not new_summary or not new_summary.strip():
        raise CompactionError("压缩结果为空，保留原始历史。")

    session.summary = new_summary.strip()
    session.messages = recent_messages
    return True


def needs_compaction(session):
    return len(session.messages) > COMPACT_THRESHOLD
