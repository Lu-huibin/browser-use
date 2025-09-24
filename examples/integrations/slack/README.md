# Slack 集成

创建和配置 Slack 机器人的步骤：

1. 创建 Slack 应用：
* 前往 Slack API：https://api.slack.com/apps
* 点击“创建新应用”。
* 选择“从头开始”，为您的应用命名并选择工作区。
* 为您的机器人提供名称和描述（这些是必填字段）。
2. 配置机器人：
* 导航到屏幕左侧的“OAuth 和权限”选项卡。
* 在“范围”下，添加必要的机器人令牌范围（添加“chat:write”、“channels:history”和“im:history”）。
3. 启用事件订阅：
* 导航到“事件订阅”选项卡。
* 启用事件并添加必要的机器人事件（添加“message.channels”和“message.im”）。
* 添加您的请求 URL（如有需要，您可以使用 ngrok 公开您的本地服务器）。[查看如何设置 ngrok](#installing-and-starting-ngrok)。
* **注意**：ngrok 提供的 URL 是临时的，每次启动 ngrok 时都会更改。每次重启 ngrok 时，您都需要在机器人的设置中更新请求 URL。[查看如何更新请求 URL](#updating-the-request-url-in-bots-settings)。
4. 将机器人添加到您的 Slack 工作区：
* 导航到“OAuth 和权限”选项卡。
* 在“您的工作区的 OAuth 令牌”下，点击“将应用安装到工作区”。
* 按照提示授权应用并将其添加到您的工作区。
5. 设置环境变量：
* 获取 `SLACK_SIGNING_SECRET`：
* 前往 Slack API：https://api.slack.com/apps
* 选择您的应用。
* 导航至“基本信息”选项卡。
* 复制“签名密钥”。
* 获取 `SLACK_BOT_TOKEN`：
* 前往 Slack API：https://api.slack.com/apps
* 选择您的应用。
* 导航至“OAuth 和权限”选项卡。
* 复制“机器人用户 OAuth 令牌”。
* 在项目根目录中创建一个 `.env` 文件，并添加以下代码：
```env
SLACK_SIGNING_SECRET=你的签名密钥
SLACK_BOT_TOKEN=你的机器人令牌
```
6. 邀请机器人加入频道：
* 在您希望机器人处于活动状态的 Slack 频道中使用 `/invite @你的机器人名称` 命令。
7. 运行 `examples/slack_example.py` 中的代码，使用您的机器人令牌和签名密钥启动机器人。
8. 例如，输入“$bu 东京的天气怎么样？”，启动一个浏览器使用任务并在 Slack 频道内获取响应。

## 安装和启动 ngrok

要将本地服务器暴露到互联网，您可以使用 ngrok。请按照以下步骤安装并启动 ngrok：

1. 从官方网站下载 ngrok：https://ngrok.com/download
2. 创建免费帐户并按照官方步骤安装 ngrok。
3. 在终端中运行以下命令启动 ngrok：
```sh
ngrok http 3000
```
将 `3000` 替换为您本地服务器运行的端口号。

## 在机器人设置中更新请求 URL

如果您需要更新请求 URL（例如，当 ngrok URL 发生变化时），请按照以下步骤操作：

1. 前往 Slack API：https://api.slack.com/apps
2. 选择您的应用。
3. 导航到“事件订阅”选项卡。
4. 使用新的 ngrok URL 更新“请求 URL”字段。 URL 应类似于：`https://<ngrok-id>.ngrok-free.app/slack/events`
5. 保存更改。

## 安装所需软件包

要运行此示例，您需要安装以下软件包：

- `fastapi`
- `uvicorn`
- `slack_sdk`

您可以使用 pip 安装这些软件包：

```sh
pip install fastapi uvicorn slack_sdk