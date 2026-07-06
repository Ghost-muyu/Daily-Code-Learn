from src.llm import call_llm, LLMError
from src.context_builder import ContextBuilder

MAX_TOOL_ROUNDS = 8


class Agent:
    def __init__(self, config, tool_registry=None, skill_manager=None):
        self.config = config
        self.tool_registry = tool_registry
        self.skill_manager = skill_manager
        self.context_builder = ContextBuilder()
        self._active_skill = None

    def activate_skill(self, skill_name):
        if self.skill_manager and self.skill_manager.get(skill_name):
            self._active_skill = skill_name
            return True
        return False

    def deactivate_skill(self):
        self._active_skill = None

    def _build_messages(self, session, memory_store):
        memory_contents = [m["content"] for m in memory_store.list_all()] \
            if memory_store else []

        system_prompt = self.config.get("system_prompt", "")
        soul = self.config.get("soul", "")

        # 激活 skill 时注入其内容
        if self._active_skill and self.skill_manager:
            skill_context = self.skill_manager.build_context(self._active_skill)
            soul = soul + "\n\n" + skill_context if soul else skill_context

        return self.context_builder.build(
            system_prompt=system_prompt,
            soul=soul,
            memory_contents=memory_contents,
            session=session,
        )

    def run_turn(self, session, user_input, memory_store=None):
        session.add_user(user_input)

        tool_specs = self.tool_registry.list_specs() \
            if self.tool_registry else None

        for _ in range(MAX_TOOL_ROUNDS):
            messages = self._build_messages(session, memory_store)

            try:
                result = call_llm(
                    messages=messages,
                    base_url=self.config["base_url"],
                    api_key=self.config["api_key"],
                    model=self.config["model"],
                    tools=tool_specs,
                )
            except LLMError:
                raise

            tool_calls = result.get("tool_calls")
            content = result.get("content")

            if tool_calls:
                raw_calls = []
                for tc in tool_calls:
                    raw_calls.append({
                        "id": tc["id"],
                        "type": "function",
                        "function": {
                            "name": tc["name"],
                            "arguments": json_dumps(tc["arguments"]),
                        },
                    })
                session.messages.append({
                    "role": "assistant",
                    "content": None,
                    "tool_calls": raw_calls,
                })

                for tc in tool_calls:
                    tool = self.tool_registry.get(tc["name"])
                    if tool is None:
                        obs = f"错误：未知工具 - {tc['name']}"
                    else:
                        try:
                            obs = tool.execute(tc["arguments"])
                        except Exception as e:
                            obs = f"工具执行异常: {e}"

                    session.messages.append({
                        "role": "tool",
                        "tool_call_id": tc["id"],
                        "content": obs,
                    })

                continue

            if content:
                session.add_assistant(content)
                return content

            raise LLMError("模型返回了空的 content 和 tool_calls。")

        raise LLMError("工具调用轮次超过上限。")


def json_dumps(obj):
    import json
    return json.dumps(obj, ensure_ascii=False)
