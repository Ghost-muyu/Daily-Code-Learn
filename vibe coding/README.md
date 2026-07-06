# SJTUClaw

面向教学的 AI Agent Runtime，支持 CLI 命令行和 Web 网页两种使用方式。

## 环境要求

- Python 3.10+
- DeepSeek API Key（或其他兼容 OpenAI 接口的 API）

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的 API 信息：

```
LLM_API_KEY=sk-xxxxxxxxxxxxxxxx
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-chat
```

### 3. 启动

**Web 网页模式（推荐）：**

```bash
python -m src.gateway
```

浏览器打开 **http://127.0.0.1:5000** 即可使用。

**CLI 命令行模式：**

```bash
python -m src.main
```

## Web 网页界面

启动 Gateway 后，访问 http://127.0.0.1:5000 进入聊天界面：

- **左侧栏**：会话列表，可创建/切换/删除会话
- **右侧区域**：聊天窗口，发送消息与 AI 对话
- **文件上传**：支持上传附件

> 网页地址是 **本地的**，只能在你自己的电脑上访问。如果需要让别人也能访问，需要部署到云服务器或使用内网穿透工具（如 ngrok）。

## CLI 命令参考

| 命令 | 说明 |
|------|------|
| `/exit` | 退出程序 |
| `/compact` | 手动压缩当前会话历史 |
| `/session new` | 创建新会话 |
| `/session list` | 列出所有会话 |
| `/session switch <id>` | 切换会话 |
| `/session rename <id> <title>` | 重命名会话 |
| `/session delete <id>` | 删除会话 |
| `/memory add <内容>` | 添加长期记忆 |
| `/memory list` | 列出所有记忆 |
| `/memory delete <id>` | 删除记忆 |
| `/approve <id>` | 批准操作（写文件/执行命令） |
| `/deny <id>` | 拒绝操作 |
| `/workspace [path]` | 查看或设置工作目录 |
| `/task add <内容> [间隔秒]` | 添加定时任务 |
| `/task list` | 列出定时任务 |
| `/task cancel <id>` | 取消定时任务 |
| `/skill list` | 列出可用技能 |
| `/skill use <name>` | 激活技能 |
| `/skill off` | 关闭技能 |

## 内置技能

| 技能名 | 功能 |
|--------|------|
| `translate` | 中/英/日 多语言翻译 |
| `code-review` | 代码审查与分析 |
| `course-report` | 课程报告生成 |

## 可用工具

| 工具 | 说明 | 需要审批 |
|------|------|----------|
| `get_time` | 获取当前时间 | 否 |
| `list_dir` | 列出目录内容 | 否 |
| `read_file` | 读取文本文件 | 否 |
| `write_file` | 在 workspace 写入文件 | **是** |
| `run_shell` | 执行 Shell 命令 | **是** |

## 项目结构

```
├── config/             # 系统配置 (system_prompt + soul)
├── skills/             # 技能定义 (SKILL.md)
├── src/                # 源代码
├── templates/          # Web 页面模板
├── data/               # 运行时数据 (自动生成)
│   ├── sessions/       # 会话持久化
│   ├── memories.json   # 长期记忆
│   └── tasks.json      # 定时任务
├── workspace/          # 文件操作沙箱 (自动生成)
├── uploads/            # 上传文件目录 (自动生成)
├── .env                # API 配置 (不提交到 git)
├── .env.example        # 配置模板
├── requirements.txt    # Python 依赖
└── README.md
```

## 打包分发

将整个项目文件夹打包为 zip 即可分发给他人：

**Windows**：右键项目文件夹 → 发送到 → 压缩文件夹

**命令行**：

```bash
# macOS / Linux
zip -r SJTUClaw.zip . -x "__pycache__/*" "data/*" ".git/*"

# Windows PowerShell
Compress-Archive -Path * -DestinationPath SJTUClaw.zip
```

接收方解压后按上方"快速开始"步骤配置 `.env` 并安装依赖即可运行。

> 注意：分发时确保 **不要包含 `.env` 文件**（内含 API Key），已在 `.gitignore` 中排除。
