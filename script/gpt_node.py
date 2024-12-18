#!/usr/bin/python3
# -*- coding: utf-8 -*-
import rospy
from std_msgs.msg import String
import httpx
import json
from openai import OpenAI

# 初始化 OpenAI 客户端
client = OpenAI(
    base_url="https://api.nextapi.fun",
    api_key="ak-oHn3yr6Sjq1wXGBhRoX9hYQNebgCs5iKOUilkmxKbLnE3Ylv",  # 请替换为您的API密钥
    http_client=httpx.Client(
        base_url="https://api.nextapi.fun",
        follow_redirects=True,
    ),
)


def user_message_callback(data):
    rospy.loginfo("Received from user: %s", data.data)

    try:
        # 将接收到的 JSON 字符串转换为字典
        message_data = json.loads(data.data)
        user_message = message_data["message"]  # 提取用户消息
        model_name = message_data["model"]  # 提取模型名称

        rospy.loginfo("Using model: %s", model_name)

        # 向 GPT API 发送请求
        chat_completion = client.chat.completions.create(
            model=model_name,  # 使用接收到的模型名称
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_message},
            ],
        )

        # 获取 GPT 的回复
        gpt_reply = chat_completion.choices[0].message.content
        rospy.loginfo("GPT Reply: %s", gpt_reply)

        # 发布 GPT 的回复
        gpt_reply_pub.publish(gpt_reply)

    except Exception as e:
        rospy.logerr("Error occurred while querying GPT: %s", str(e))
        gpt_reply_pub.publish("Error: Failed to get response from GPT")


def gpt_node():
    # 初始化 ROS 节点
    rospy.init_node("chatgpt_gpt_node", anonymous=True)

    # 发布者：发布 GPT 回复到 "gpt_reply_to_user" 话题
    global gpt_reply_pub
    gpt_reply_pub = rospy.Publisher("gpt_reply_to_user", String, queue_size=10)

    # 订阅者：接收用户消息（JSON 格式）
    rospy.Subscriber("user_to_gpt", String, user_message_callback)

    rospy.spin()


if __name__ == "__main__":
    try:
        gpt_node()
    except rospy.ROSInterruptException:
        pass
