#!/usr/bin/python3
# -*- coding: utf-8 -*-
import rospy
from std_msgs.msg import String
import tkinter as tk
from tkinter import scrolledtext, OptionMenu
import json  # 导入 JSON 库来处理 Unicode 转义字符
from PIL import Image, ImageTk


class ChatGPTGUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("小果的 ChatGPT")
        self.window.geometry("800x600")  # 设置窗口大小

        # 加载背景图片
        self.background_image = Image.open(
            "/home/zy/chatgpt_ros/gpt_ws/src/chatgpt_ros/picture/1.jpg"
        )  # 替换为你的背景图片路径
        self.bg_photo = ImageTk.PhotoImage(self.background_image)

        # 创建 Canvas 来放置背景图片
        self.canvas = tk.Canvas(self.window, width=800, height=600)
        self.canvas.pack(fill="both", expand=True)

        # 在 Canvas 上绘制背景图片
        self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)

        # 聊天记录框
        self.chat_box = scrolledtext.ScrolledText(
            self.window, width=60, height=20, wrap=tk.WORD
        )
        self.chat_box.place(x=50, y=50)  # 设置聊天框的位置
        self.chat_box.config(state=tk.NORMAL)  # 设置为可编辑状态，写入初始内容
        self.chat_box.insert(tk.END, "GPT：你好，有什么可以帮助你的吗？\n")
        self.chat_box.config(state=tk.DISABLED)  # 设置为不可编辑状态

        # 输入框
        self.user_input = tk.Entry(self.window, width=60)
        self.user_input.place(x=50, y=450)  # 输入框位置

        # 发送按钮
        self.send_button = tk.Button(
            self.window, text="发送", command=self.send_message
        )
        self.send_button.place(x=700, y=450)  # 发送按钮位置

        # 清屏按钮
        self.clear_button = tk.Button(
            self.window, text="清屏", command=self.clear_chat_box, bg="lightgray"
        )
        self.clear_button.place(x=700, y=500)  # 清屏按钮位置

        # 添加模型选择按钮
        self.model_label = tk.Label(self.window, text="选择模型：", font=("Arial", 12))
        self.model_label.place(x=600, y=50)

        self.models = [
            "gpt-4",
            "gpt-4-0314",
            "gpt-4-0613",
            "gpt-4-32k",
            "gpt-4-32k-0314",
            "gpt-4-32k-0613",
            "gpt-4-turbo-preview",
            "gpt-4-1106-preview",
            "gpt-4-0125-preview",
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-0301",
            "gpt-3.5-turbo-0613",
            "gpt-3.5-turbo-16k",
            "gpt-3.5-turbo-16k-0613",
            "gpt-3.5-turbo-1106",
            "gpt-3.5-turbo-0125",
        ]

        # 当前选中的模型
        self.selected_model = tk.StringVar(value=self.models[0])
        self.model_selector = OptionMenu(
            self.window, self.selected_model, *self.models, command=self.change_model
        )
        self.model_selector.place(x=680, y=45)

        # ROS Publisher
        self.pub = rospy.Publisher("user_to_gpt", String, queue_size=10)

    def clear_chat_box(self):
        """清空聊天记录框的内容"""
        self.chat_box.config(state=tk.NORMAL)  # 允许编辑
        self.chat_box.delete("1.0", tk.END)  # 删除从第一行到最后一行的内容
        self.chat_box.config(state=tk.DISABLED)  # 设置为不可编辑

    def send_message(self):
        user_message = self.user_input.get()
        if user_message:
            selected_model = self.selected_model.get()  # 获取当前选择的模型
            self.chat_box.config(state=tk.NORMAL)  # 设置文本框可编辑
            self.chat_box.insert(tk.END, f"小果: {user_message}\n")
            self.chat_box.config(state=tk.DISABLED)  # 设置文本框不可编辑

            # Publish message to ROS，包含模型信息
            message_with_model = json.dumps(
                {"model": selected_model, "message": user_message}
            )
            self.pub.publish(message_with_model)

            self.user_input.delete(0, tk.END)  # 清空输入框

    def update_gui_with_reply(self, gpt_reply):
        try:
            # 如果 gpt_reply 是带有 Unicode 转义的字符串，进行解码
            decoded_reply = (
                json.loads(gpt_reply.data)
                if "\\u" in gpt_reply.data
                else gpt_reply.data
            )
            self.window.after(0, self._update_chat_box, decoded_reply)
        except Exception as e:
            # 如果解码失败，显示原始数据并打印错误
            print(f"Error decoding GPT reply: {e}")
            self.window.after(0, self._update_chat_box, gpt_reply.data)

    def _update_chat_box(self, gpt_reply):
        self.chat_box.config(state=tk.NORMAL)
        self.chat_box.insert(tk.END, f"GPT: {gpt_reply}\n")
        self.chat_box.config(state=tk.DISABLED)

    def change_model(self, selected_model):
        """当选择新的模型时，更新聊天记录框"""
        self.chat_box.config(state=tk.NORMAL)
        self.chat_box.tag_config("model_switch", foreground="green")  # 设置标签颜色
        self.chat_box.insert(tk.END, f"已切换模型：{selected_model}\n", "model_switch")
        self.chat_box.config(state=tk.DISABLED)

    def start_gui(self):
        self.window.mainloop()


def gui_node():
    # Initialize the ROS node
    rospy.init_node("chatgpt_gui_node", anonymous=True)

    # Create the GUI instance
    gui = ChatGPTGUI()
    # 订阅 gpt 回复
    rospy.Subscriber("gpt_reply_to_user", String, gui.update_gui_with_reply)

    # Run the GUI in the main thread
    gui.start_gui()

    rospy.spin()  # 保持 ROS 节点运行


if __name__ == "__main__":
    try:
        gui_node()
    except rospy.ROSInterruptException:
        pass
