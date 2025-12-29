from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, ConfigDict, Field

from browser_use.llm.messages import (
	BaseMessage,
)

if TYPE_CHECKING:
	pass


# 一条历史日志，记录某一步干了什么，有没有出错，结果怎样。类似“流水账的一条记录”。
class HistoryItem(BaseModel):
	"""
	👉 一条“行动历史记录”。
	它们存在于 MessageManagerState.agent_history_items 这个列表里。
	每个 HistoryItem 记录一小步执行情况。
	"""
	step_number: int | None = None  # 第几步。比如 step_number=1 表示第一步。
	evaluation_previous_goal: str | None = None  # 对上一步目标的评价（Agent 回顾自己做得对不对）。
	memory: str | None = None  # 记忆，可能是对环境的总结。
	next_goal: str | None = None  # 下一步要干啥。
	action_results: str | None = None  # 执行动作的结果，比如“成功点击了按钮”。
	error: str | None = None  # 出错信息。
	system_message: str | None = None  # 系统级别的消息（比如初始化、任务说明）。

	model_config = ConfigDict(arbitrary_types_allowed=True)

	def model_post_init(self, __context) -> None:
		"""👉 不能既有错误又有系统消息，因为一条记录要么是“报错”，要么是“系统说明”，避免混淆。"""
		if self.error is not None and self.system_message is not None:
			raise ValueError('Cannot have both error and system_message at the same time')

	# 输出方法：
	def to_string(self) -> str:
		"""把记录转换成字符串（XML-like 格式），方便拼接到 prompt 里。"""
		step_str = 'step' if self.step_number is not None else 'step_unknown'

		if self.error:
			return f"""<{step_str}>
{self.error}"""
		elif self.system_message:
			return self.system_message
		else:
			content_parts = []

			# Only include evaluation_previous_goal if it's not None/empty
			if self.evaluation_previous_goal:
				content_parts.append(f'{self.evaluation_previous_goal}')

			# Always include memory
			if self.memory:
				content_parts.append(f'{self.memory}')

			# Only include next_goal if it's not None/empty
			if self.next_goal:
				content_parts.append(f'{self.next_goal}')

			if self.action_results:
				content_parts.append(self.action_results)

			content = '\n'.join(content_parts)

			return f"""<{step_str}>
{content}"""


# 保存给 LLM 的消息顺序（系统→状态→上下文）。类似“给AI的一封邮件，里面有正文、附件、补充说明”。
class MessageHistory(BaseModel):
	"""
		👉 专门负责存储 和 LLM 交互的消息。
		它在 MessageManagerState 里就是一个字段。
		内部分为：
			system_message（规则）
			state_message（状态描述）
			context_messages（上下文补充）
	"""
	system_message: BaseMessage | None = None# 系统提示词（通常是初始化 Agent 时设置的规则）。
	state_message: BaseMessage | None = None# Agent 的状态描述（环境总结、历史等）。
	context_messages: list[BaseMessage] = Field(default_factory=list)# 当前步骤临时加的上下文，比如“上一步失败，请重试”。
	model_config = ConfigDict(arbitrary_types_allowed=True)

	def get_messages(self) -> list[BaseMessage]:
		"""
		获取消息时，顺序固定：
				系统消息（全局规则）
				状态消息（当前环境）
				上下文消息（临时补充）
		就像：规则 → 当前情况 → 附加提醒
		"""
		messages = []
		if self.system_message:
			messages.append(self.system_message)
		if self.state_message:
			messages.append(self.state_message)
		messages.extend(self.context_messages)

		return messages


# 最外层整体对外暴露的容器，放历史记录（步骤）、消息（对话）、工具ID。类似“文件夹”，里面装着账本和信件。
class MessageManagerState(BaseModel):
	"""
	👉 最外层的大容器（整个“档案柜”）。
		它包含：
		一个 MessageHistory（消息历史记录簿）
		一组 HistoryItem（行动步骤的流水账）
		还有一些额外字段（比如 tool_id、read_state_description）
	"""

	history: MessageHistory = Field(default_factory=MessageHistory)
	tool_id: int = 1 # 当前工具的 ID，Agent 调用工具时会用到。
	agent_history_items: list[HistoryItem] = Field(
		default_factory=lambda: [HistoryItem(step_number=0, system_message='Agent initialized')]
	)# 行动步骤的历史（HistoryItem 列表）默认会有一个初始化条目：意思是：第 0 步就是“Agent 已经启动”。。
	read_state_description: str = '' # 用来临时存储“读取到的页面内容摘要”。
	# Images to include in the next state message (cleared after each step)
	read_state_images: list[dict[str, Any]] = Field(default_factory=list)

	model_config = ConfigDict(arbitrary_types_allowed=True)
