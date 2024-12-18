#!/usr/bin/env python
import rospy
from std_msgs.msg import String
import openai
import tkinter as tk
from tkinter import scrolledtext
import threading  # 导入线程模块

# 设置OpenAI API密钥
openai.api_key = (
    "sk-onUOQjipYR8JgJPI07Ed8685Dc094bC5BbF7A58cBf3935Cb"  # 请替换为您的API密钥
)
# 设置自定义的base_url，如果需要的话
openai.api_base = "https://free.v36.cm/v1/"


# ROS回调函数，用于处理收到的用户消息并返回 GPT 回复
def user_message_callback(data):
    rospy.loginfo("Received from user: %s", data.data)

    try:
        # 向GPT发送请求并获取回复
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": data.data},
            ],
        )

        # 获取GPT的回复
        gpt_reply = response["choices"][0]["message"]["content"]
        rospy.loginfo("GPT Reply: %s", gpt_reply)

        # 发布GPT的回复
        gpt_reply_pub.publish(gpt_reply)

        # 更新GUI显示
        update_gui_with_reply(gpt_reply)

    except Exception as e:
        rospy.logerr("Error occurred while querying GPT: %s", str(e))


# GUI部分：用于显示聊天界面
def create_gui():
    # 创建Tkinter窗口
    window = tk.Tk()
    window.title("Chat with GPT")

    # 创建文本框，显示聊天记录
    chat_box = scrolledtext.ScrolledText(window, width=60, height=20, wrap=tk.WORD)
    chat_box.grid(row=0, column=0, padx=10, pady=10)
    chat_box.config(state=tk.DISABLED)  # 默认不可编辑

    # 创建输入框
    user_input = tk.Entry(window, width=50)
    user_input.grid(row=1, column=0, padx=10, pady=10)

    # 发送按钮的回调函数
    def send_message():
        user_message = user_input.get()  # 获取用户输入
        if user_message:
            chat_box.config(state=tk.NORMAL)
            chat_box.insert(tk.END, f"You: {user_message}\n")
            chat_box.config(state=tk.DISABLED)

            # 发布用户消息给ROS
            rospy.loginfo(f"Publishing message: {user_message}")
            user_message_pub.publish(user_message)

            user_input.delete(0, tk.END)  # 清空输入框

    send_button = tk.Button(window, text="Send", command=send_message)
    send_button.grid(row=2, column=0, padx=10, pady=10)

    return window, chat_box


# 更新GUI显示的函数
def update_gui_with_reply(gpt_reply):
    chat_box.config(state=tk.NORMAL)
    chat_box.insert(tk.END, f"GPT: {gpt_reply}\n")
    chat_box.config(state=tk.DISABLED)


# ROS 节目的线程化方法
def start_ros():
    # 在主线程中初始化ROS节点
    rospy.init_node("chatgpt_ros_gui_node", anonymous=True)

    # 创建ROS发布者，用于发布用户输入的消息
    global user_message_pub
    user_message_pub = rospy.Publisher("user_to_gpt", String, queue_size=10)

    # 创建ROS订阅者，用于接收GPT的回复
    rospy.Subscriber("gpt_reply_to_user", String, user_message_callback)

    rospy.spin()  # 进入ROS事件循环


if __name__ == "__main__":
    try:
        # 在主线程中启动ROS节点
        # 启动GUI并确保在主线程中调用ros相关方法
        window, chat_box = create_gui()

        # 启动ROS节点和GUI
        # 启动一个线程来运行ROS事件循环
        ros_thread = threading.Thread(target=start_ros)
        ros_thread.daemon = True  # 设为守护线程，主程序退出时，线程会自动退出
        ros_thread.start()

        # 启动Tkinter的主循环
        window.mainloop()

    except rospy.ROSInterruptException:
        pass
