import time
import uuid
from mailtm import MailTMClient  # 你本地库里应该有 __init__.py 暴露这个类

def create_temp_account():
    # 1. 获取可用域名
    domains = MailTMClient.get_domains()
    domain = domains[0].domain  # Domain 对象的字段名是 a_domain
    localpart = "tmp" + uuid.uuid4().hex[:6]
    email = f"{localpart}@{domain}"
    password = "P@ss" + uuid.uuid4().hex[:6]

    print("准备注册:", email)

    # 2. 创建账号
    account = MailTMClient.create_account(email, password)
    print("账号创建成功:", account)

    # 3. 登录获取 token，并实例化客户端
    client = MailTMClient(account=email, password=password)
    print("token:", client.token)

    return client, email, password


def wait_for_message(client, timeout=600, poll_interval=5):
    """
    轮询等待收件箱邮件
    """
    print("等待邮件中...")
    start = time.time()
    while time.time() - start < timeout:
        msgs = client.get_messages()
        if msgs:
            msg = msgs[0]
            print("收到邮件:", msg.subject, "发件人:", msg.from_)
            detail = client.get_message_by_id(msg.id)
            print("邮件正文:\n", detail.text)
            return detail
        time.sleep(poll_interval)
    print("超时未收到邮件")
    return None


if __name__ == "__main__":
    client, email, password = create_temp_account()
    print("临时邮箱:", email)

    # 等待收邮件（比如注册验证码）
    msg = wait_for_message(client, timeout=120, poll_interval=5)
    if msg:
        # 这里可以用正则提取验证码
        import re
        m = re.search(r"\b[A-Za-z0-9]{4,8}\b", msg.text or "")
        if m:
            print("验证码:", m.group(0))