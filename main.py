import requests
import tkinter as tk
from io import BytesIO
from PIL import Image, ImageTk
from transformers import pipeline
from deep_translator import GoogleTranslator

# Натренированная модель, которая анализирует изображение
captioner = pipeline("image-to-text", model="Salesforce/blip-image-captioning-base")


def translate_text(text: str) -> str:
    translated = GoogleTranslator(source='en', target='ru').translate(text)
    return translated


def update_text_label(text: str) -> None:
    output_text.config(text=f"Описание изображения:\n{text}", anchor='n', wraplength=250)


def update_image_placeholder(image_url: str) -> None:
    response = requests.get(image_url)
    bytes_image = Image.open(BytesIO(response.content)).resize((350, 300))
    image_to_draw = ImageTk.PhotoImage(bytes_image)

    image_label.config(image=image_to_draw, width=350, height=300)
    image_label.image = image_to_draw


def analyze_image() -> None:
    entered_text = input_field.get()

    raw_analyzed_data = captioner(entered_text)
    translated_data = translate_text(raw_analyzed_data[0]['generated_text'])

    update_text_label(translated_data)
    update_image_placeholder(entered_text)


if __name__ == "__main__":
    # Создаем главное окно
    root = tk.Tk()
    root.resizable(width=False, height=False)
    root.title("НейроПаль")
    root.geometry("660x330")  # Размеры окна

    # Поле для ввода текста
    text_from_input_field = tk.StringVar()
    input_field = tk.Entry(root, textvariable=text_from_input_field, width=30)
    input_field.place(x=10, y=20)

    # Кнопка для сабмита ввода
    submit_button = tk.Button(root, text="Скан", command=analyze_image, width=10)
    submit_button.place(x=205, y=15)

    # Место для картинки
    image_label = tk.Label(root, text="Анализируемое изображение", width=50, height=20, relief=tk.GROOVE)
    image_label.place(x=300, y=20)

    # Поле для вывода текста
    output_text = tk.Label(root, text="Текстовое описание", width=40, height=10, relief=tk.GROOVE)
    output_text.place(x=5, y=50)

    # Запускаем цикл событий
    root.mainloop()

