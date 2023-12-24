import tkinter as tk
from tkinter import filedialog
from io import BytesIO
from PIL import Image, ImageTk
from deep_translator import GoogleTranslator
from transformers import pipeline
import requests
import pyttsx3
import threading

# Натренированная модель, которая анализирует изображение
captioner = pipeline("image-to-text", model="Salesforce/blip-image-captioning-base", max_new_tokens=100)

class NeuroPalApp:
    def __init__(self, root):
        self.root = root
        root.resizable(width=False, height=False)
        root.title("НейроПаль")
        root.geometry("650x300")  # Увеличил ширину окна для размещения тумблера

        # Фрейм для отображения изображения
        self.image_frame = tk.Frame(root, bd=2, relief=tk.GROOVE)
        self.image_frame.place(relx=0.01, rely=0.02, relwidth=0.5, relheight=0.7)

        self.image_label = tk.Label(self.image_frame, text="Анализируемое изображение", width=40, height=15)
        self.image_label.pack(fill="both", expand=True)

        # Фрейм для вывода текста
        self.output_frame = tk.Frame(root, bd=2, relief=tk.GROOVE)
        self.output_frame.place(relx=0.52, rely=0.02, relwidth=0.470, relheight=0.8)

        self.output_text = tk.Label(self.output_frame, text="Текстовое описание", width=40, height=10, anchor='center', justify='center', wraplength=200)
        self.output_text.pack(fill="both", expand=True)

        # Переменная для хранения пути к текущему изображению
        self.current_image_path = None

        # Кнопка для сканирования изображения
        self.scan_button = tk.Button(root, text="Скан", command=self.analyze_image, width=20)
        self.scan_button.place(relx=0.5, rely=0.05, anchor="s")

        # Кнопка для выбора изображения
        self.choose_image_button = tk.Button(root, text="Выбрать изображение", command=self.choose_image, width=20)
        self.choose_image_button.place(relx=0.5, rely=1, anchor="s")

        # Озвучивание кнопок при наведении
        self.scan_button.bind("<Enter>", self.on_enter_scan)
        self.scan_button.bind("<Leave>", self.on_leave_scan)
        self.choose_image_button.bind("<Enter>", self.on_enter_choose_image)
        self.choose_image_button.bind("<Leave>", self.on_leave_choose_image)

        # Тумблер для включения/выключения озвучивания
        self.tts_enabled = tk.BooleanVar()
        self.tts_enabled.set(True)  # Изначально включено

        self.tts_toggle = tk.Checkbutton(root, text="выкл. озвучку", variable=self.tts_enabled, command=self.toggle_tts)
        self.tts_toggle.place(relx=0.99, rely=0.10, anchor="ne")

    def translate_text(self, text: str) -> str:
        translated = GoogleTranslator(source='en', target='ru').translate(text)
        return translated

    def update_text_label(self, text: str) -> None:
        self.output_text.config(text=f"Описание изображения:\n{text}")

    def update_image_placeholder(self, image_path: str) -> None:
        bytes_image = Image.open(image_path).resize((350, 180))  # размер изображения
        image_to_draw = ImageTk.PhotoImage(bytes_image)

        self.image_label.config(image=image_to_draw, width=350, height=180)
        self.image_label.image = image_to_draw

    def analyze_image(self) -> None:
        if self.current_image_path:
            threading.Thread(target=self.analyze_and_speak).start()
        else:
            print("Выберите изображение.")

    def choose_image(self) -> None:
        file_path = filedialog.askopenfilename(title="Выберите изображение", filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.gif")])

        if file_path:
            self.current_image_path = file_path
            self.update_image_placeholder(file_path)

    def speak(self, text: str) -> None:
        if self.tts_enabled.get():
            threading.Thread(target=self.speak_thread, args=(text,)).start()

    def speak_thread(self, text: str) -> None:
        engine = pyttsx3.init()
        if not engine._inLoop:  # Проверка, активен ли цикл озвучивания
            engine.say(text)
            engine.runAndWait()
        else:
            print("Цикл озвучивания уже запущен.")

    def toggle_tts(self):
        if self.tts_enabled.get():
            self.tts_toggle.configure(text="выкл. озвучку", fg="red")
        else:
            self.tts_toggle.configure(text="вкл. озвучку", fg="green")

    def on_enter_scan(self, event):
        if self.tts_enabled.get():
            self.speak("Скан")

    def on_leave_scan(self, event):
        pass

    def on_enter_choose_image(self, event):
        if self.tts_enabled.get():
            self.speak("Выбрать изображение")

    def on_leave_choose_image(self, event):
        pass

    def analyze_and_speak(self) -> None:
        try:
            image = Image.open(self.current_image_path)
            raw_analyzed_data = captioner(image)
            translated_data = self.translate_text(raw_analyzed_data[0]['generated_text'])
            self.update_text_label(translated_data)
            self.speak(translated_data)  # Озвучивание текста описания
        except Exception as e:
            print(f"Error analyzing image: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = NeuroPalApp(root)
    root.mainloop()


