import os
import threading
import time
from datetime import datetime

import cv2
import numpy as np
from PIL import ImageGrab
import tkinter as tk
from tkinter import messagebox

class ScreenRecorder:
    def __init__(self):
        self.recording = False          # 录制状态标志
        self.thread = None               # 录制线程
        self.out = None                  # VideoWriter 对象
        self.fps = 10                     # 帧率（可根据需要调整）

    def start_recording(self):
        """开始录制"""
        if self.recording:
            return

        # 生成文件名（当前时间）
        filename = datetime.now().strftime("recording_%Y%m%d_%H%M%S.avi")
        filepath = os.path.join(os.getcwd(), filename)

        # 获取屏幕尺寸
        screen = ImageGrab.grab()
        width, height = screen.size
        # OpenCV 中尺寸为 (width, height)
        size = (width, height)

        # 定义视频编码器（此处使用 XVID，若系统不支持可尝试 'MJPG' 或 'mp4v'）
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.out = cv2.VideoWriter(filepath, fourcc, self.fps, size)

        if not self.out.isOpened():
            messagebox.showerror("错误", "无法创建视频文件，请检查编码器支持。")
            return

        self.recording = True
        self.thread = threading.Thread(target=self._record)
        self.thread.daemon = True   # 主窗口关闭时线程自动退出
        self.thread.start()
        messagebox.showinfo("提示", f"录制已开始，保存至：{filepath}")

    def stop_recording(self):
        """停止录制"""
        if not self.recording:
            return
        self.recording = False
        if self.thread:
            self.thread.join(timeout=2.0)
        if self.out:
            self.out.release()
            self.out = None
        messagebox.showinfo("提示", "录制已停止并保存。")

    def _record(self):
        """录制线程主函数"""
        while self.recording:
            # 截图并转换为 OpenCV 格式（BGR）
            img = ImageGrab.grab()
            frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            self.out.write(frame)
            # 控制帧率
            time.sleep(1.0 / self.fps)

def main():
    root = tk.Tk()
    root.title("简易屏幕录制器")
    root.geometry("300x150")
    root.resizable(False, False)

    recorder = ScreenRecorder()

    # 按钮样式
    btn_frame = tk.Frame(root, padx=20, pady=20)
    btn_frame.pack(expand=True)

    btn_start = tk.Button(btn_frame, text="开始录制", command=recorder.start_recording,
                          width=15, height=2, bg="lightgreen")
    btn_start.pack(pady=5)

    btn_stop = tk.Button(btn_frame, text="停止录制", command=recorder.stop_recording,
                         width=15, height=2, bg="salmon")
    btn_stop.pack(pady=5)

    # 窗口关闭时确保停止录制并释放资源
    def on_closing():
        if recorder.recording:
            recorder.stop_recording()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()