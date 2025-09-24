import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from dotenv import load_dotenv

load_dotenv()

import discord  # 这是 discord.py 库，主流的 Discord bot 开发框架。
from discord.ext import commands  # 一个带有命令系统的 Discord 机器人。

from browser_use.agent.service import Agent
from browser_use.browser import BrowserProfile, BrowserSession  # 浏览器的配置（比如是否无头模式、cookie 配置、代理等）。实际管理一次浏览器的运行。
from browser_use.llm import BaseChatModel  # 抽象类，代表一个大语言模型（比如 GPT）。


# 文档里说的很清楚：这个机器人能在 Discord 聊天里，异步处理任务，然后把执行结果回复给用户。
class DiscordBot(commands.Bot):
    """Discord bot implementation for Browser-Use tasks.

    This bot allows users to run browser automation tasks through Discord messages.
    Processes tasks asynchronously and sends the result back to the user in response to the message.
    Messages must start with the configured prefix (default: "$bu") followed by the task description.

    Args:
        llm (BaseChatModel): Language model instance to use for task processing
        prefix (str, optional): Command prefix for triggering browser tasks. Defaults to "$bu"
        ack (bool, optional): Whether to acknowledge task receipt with a message. Defaults to False
        browser_profile (BrowserProfile, optional): Browser profile settings.
            Defaults to headless mode

    Usage:
        ```python
        from browser_use import ChatOpenAI

        llm = ChatOpenAI()
        bot = DiscordBot(llm=llm, prefix='$bu', ack=True)
        bot.run('YOUR_DISCORD_TOKEN')
        ```

    Discord Usage:
        Send messages starting with the prefix:
        "$bu search for python tutorials"
    """

    def __init__(
            self,
            llm: BaseChatModel,
            prefix: str = '$bu',  # 触发命令的前缀
            ack: bool = False,  # 是否先发一条“任务已收到”的提示（相当于回执）。
            browser_profile: BrowserProfile = BrowserProfile(headless=True),  # 浏览器配置，默认是无头模式。
    ):
        self.llm = llm
        self.prefix = prefix.strip()
        self.ack = ack
        self.browser_profile = browser_profile

        # Define intents.
        intents = discord.Intents.default()  # type: ignore
        intents.message_content = True  # Enable message content intent
        intents.members = True  # Enable members intent for user info

        # Initialize the bot with a command prefix and intents.
        super().__init__(command_prefix='!', intents=intents)  # You may not need prefix, just here for flexibility

    # self.tree = app_commands.CommandTree(self) # Initialize command tree for slash commands.

    # 机器人启动事件
    async def on_ready(self):
        """Called when the bot is ready."""
        try:
            print(f'We have logged in as {self.user}')
            cmds = await self.tree.sync()  # Sync the command tree with discord

        except Exception as e:
            print(f'Error during bot startup: {e}')

    # 消息监听
    async def on_message(self, message):
        """逻辑：
		忽略机器人自己发的消息。

		如果消息是 $bu xxx 这种格式，就触发任务：

		如果 ack=True，先回复“Starting browser use task...”

		调用 run_agent() 执行任务

		把结果再发回 Discord
		"""
        try:
            if message.author == self.user:  # Ignore the bot's messages
                return
            if message.content.strip().startswith(f'{self.prefix} '):
                if self.ack:
                    try:
                        await message.reply(
                            'Starting browser use task...',
                            mention_author=True,  # Don't ping the user
                        )
                    except Exception as e:
                        print(f'Error sending start message: {e}')

                try:
                    agent_message = await self.run_agent(message.content.replace(f'{self.prefix} ', '').strip())
                    await message.channel.send(content=f'{agent_message}', reference=message, mention_author=True)
                except Exception as e:
                    await message.channel.send(
                        content=f'Error during task execution: {str(e)}',
                        reference=message,
                        mention_author=True,
                    )

        except Exception as e:
            print(f'Error in message handling: {e}')


	# 执行任务
    async def run_agent(self, task: str) -> str:
        """
        流程：

		创建一个新的浏览器会话。

		用任务 + LLM + 会话构建 Agent。

		await agent.run() 运行任务。

		从 result.history 里取出最后一步的输出内容。

		如果没有结果，就返回一条默认错误信息。
        """
        try:
            browser_session = BrowserSession(browser_profile=self.browser_profile)
            agent = Agent(task=(task), llm=self.llm, browser_session=browser_session)
            result = await agent.run()

            agent_message = None
            if result.is_done():
                agent_message = result.history[-1].result[0].extracted_content

            if agent_message is None:
                agent_message = 'Oops! Something went wrong while running Browser-Use.'

            return agent_message

        except Exception as e:
            raise Exception(f'Browser-use task failed: {str(e)}')
