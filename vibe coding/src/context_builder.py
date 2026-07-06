class ContextBuilder:
    """将各类上下文组装成 LLM 输入的 messages 列表。"""

    def build(self, system_prompt, soul, memory_contents, session):
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        if soul:
            messages.append({"role": "system", "content": soul})

        for mem in memory_contents:
            messages.append({"role": "system", "content": f"[memory] {mem}"})

        # 当前 session 的压缩摘要（属于 conversation context）
        if session.summary:
            messages.append(
                {"role": "system",
                 "content": f"[对话摘要] {session.summary}"}
            )

        messages.extend(session.messages)

        return messages
