import json
import requests


class LLMError(Exception):
    pass


def _parse_message(message):
    """从 API 响应 message 中提取 content 和 tool_calls。"""
    content = message.get("content")
    raw_tool_calls = message.get("tool_calls")

    tool_calls = None
    if raw_tool_calls:
        tool_calls = []
        for tc in raw_tool_calls:
            func = tc.get("function", {})
            try:
                args = json.loads(func.get("arguments", "{}"))
            except json.JSONDecodeError:
                args = {}
            tool_calls.append({
                "id": tc.get("id"),
                "name": func.get("name"),
                "arguments": args,
            })

    return {"content": content, "tool_calls": tool_calls}


def call_llm(messages, base_url, api_key, model, tools=None):
    """发送 messages 到 LLM，返回 assistant 的回复。

    返回 dict: {"content": str|None, "tool_calls": list|None}
    - 普通回复时 content 有值，tool_calls 为 None
    - 工具调用时 content 为 None，tool_calls 有值
    """
    url = f"{base_url.rstrip('/')}/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    payload = {
        "model": model,
        "messages": messages,
    }
    if tools:
        payload["tools"] = tools

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
    except requests.exceptions.RequestException as e:
        raise LLMError(f"网络请求失败: {e}")

    if resp.status_code != 200:
        raise LLMError(
            f"API 返回错误 (HTTP {resp.status_code}): {resp.text[:500]}"
        )

    try:
        data = resp.json()
    except (json.JSONDecodeError, ValueError):
        raise LLMError("响应格式异常：无法解析 JSON。")

    try:
        choices = data["choices"]
        if not choices:
            raise LLMError("响应格式异常：choices 为空。")
        return _parse_message(choices[0]["message"])
    except (KeyError, IndexError, TypeError):
        raise LLMError("响应格式异常：缺少预期的字段 (choices/message/content)。")
