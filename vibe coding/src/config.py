import os
from dotenv import load_dotenv

load_dotenv()


class ConfigError(Exception):
    pass


def _read_file(path):
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


def load_config():
    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_BASE_URL")
    model = os.getenv("LLM_MODEL")

    missing = []
    if not api_key:
        missing.append("LLM_API_KEY")
    if not base_url:
        missing.append("LLM_BASE_URL")
    if not model:
        missing.append("LLM_MODEL")

    if missing:
        raise ConfigError(
            f"缺少必要配置项: {', '.join(missing)}。"
            "请在 .env 文件或环境变量中设置。"
        )

    return {
        "api_key": api_key,
        "base_url": base_url,
        "model": model,
        "system_prompt": _read_file("config/system_prompt.md"),
        "soul": _read_file("config/soul.md"),
    }
