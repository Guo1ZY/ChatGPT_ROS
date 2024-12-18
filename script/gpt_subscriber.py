#!/usr/bin/env python
import rospy
from std_msgs.msg import String
import httpx
from openai import OpenAI

# 初始化OpenAI客户端
client = OpenAI(
    base_url="https://api.nextapi.fun",
    api_key="ak-oHn3yr6Sjq1wXGBhRoX9hYQNebgCs5iKOUilkmxKbLnE3Ylv",  # 请替换为您的API密钥
    http_client=httpx.Client(
        base_url="https://api.nextapi.fun",  #
        follow_redirects=True,
    ),
)


def user_message_callback(data):
    rospy.loginfo("Received from user: %s", data.data)

    # 向GPT发送请求，并获取回复
    chat_completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": data.data},  # 使用接收到的用户消息
        ],
    )

    # 获取GPT的回复
    gpt_reply = chat_completion.choices[0].message.content
    rospy.loginfo("GPT Reply: %s", gpt_reply)

    # 发布GPT的回复
    gpt_reply_pub.publish(gpt_reply)


if __name__ == "__main__":
    try:
        rospy.init_node("chatgpt_ros_node", anonymous=True)

        # 订阅用户消息
        rospy.Subscriber("user_to_gpt", String, user_message_callback)

        # 创建发布者，用于发布GPT的回复
        gpt_reply_pub = rospy.Publisher("gpt_reply_to_user", String, queue_size=10)

        rospy.spin()
    except rospy.ROSInterruptException:
        pass
