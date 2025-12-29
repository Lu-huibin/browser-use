# 功能：把对话过程保存到文件里（方便调试、复盘、日志记录）。可以把它理解成“秘书”，专门负责把 AI 的对话内容整理好，然后归档到一个文件里。

from __future__ import annotations

import json
import logging
import anyio
from pathlib import Path
from typing import Any

import anyio
# 对话消息的基本结构（消息一定是这个类型）。
from browser_use.llm.messages import BaseMessage

logger = logging.getLogger(__name__)

# 主函数： 接收一组 输入消息 (input_messages)，和 LLM 的响应 (response)，把它们保存成一个文本文件，文件路径是 target。
async def save_conversation(
	input_messages: list[BaseMessage],
	response: Any,
	target: str | Path,
	encoding: str | None = None,
) -> None:
	"""Save conversation history to file asynchronously."""
	target_path = Path(target)
	# create folders if not exists
	if target_path.parent:# 如果目录不存在，自动创建。
		await anyio.Path(target_path.parent).mkdir(parents=True, exist_ok=True)

	await anyio.Path(target_path).write_text(
		await _format_conversation(input_messages, response),
		encoding=encoding or 'utf-8',
	)# 把 _format_conversation 格式化后的文本写进去。
	# 👉 这保证了即使目标目录之前没建，也能顺利写入。

# 格式化函数：作用：把消息和响应拼接成一个清晰的字符串，便于保存。
async def _format_conversation(messages: list[BaseMessage], response: Any) -> str:
	lines = []
	# 遍历消息：
	for message in messages:
		lines.append(f' {message.role} ')
		lines.append(message.text)
		lines.append('')  # Empty line after each message

	# 处理响应：
	lines.append(json.dumps(json.loads(response.model_dump_json(exclude_unset=True)), indent=2, ensure_ascii=False))

	return '\n'.join(lines)


# Note: _write_messages_to_file and _write_response_to_file have been merged into _format_conversation
# This is more efficient for async operations and reduces file I/O
