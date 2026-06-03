#task 3.1 (GUI 2.1)

import requests
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

#Константы
URL_LIST = [
    "https://github.com/",
    "https://www.binance.com/en",
    "https://tomtit.tomsk.ru/",
    "https://jsonplaceholder.typicode.com/",
    "https://moodle.tomtit-tomsk.ru/"
]

#Глобальные переменные
status_list = []

# ------------------ Логика ------------------

#Функция сопоставление статус числа
def get_status_text(status_code):
    if status_code == 200:
        return "Available"
    elif status_code == 403:
        return "No access"
    elif status_code == 404:
        return "Not Found"
    elif status_code in (500, 502, 503):
        return "Server Error"
    else:
        return "Not Available"


#Функция проверки URL
def check_url_status(url):
    try:
        response = requests.get(url, timeout = 10, allow_redirects = True)
        return response.status_code, get_status_text(response.status_code)
    except requests.exceptions.RequestException:
        return None, "Not Available"


#Функция вывода результата
def run_check():
    global status_list
    status_list.clear()
    text_area.delete(1.0, tk.END)
    btn_check.config(state = tk.DISABLED)
    btn_save.config(state = tk.DISABLED)
    status_var.set("Пожалуйста подождите...")
    winmain.update()
    text_area.insert(tk.END, " - HTTP Status Site - \n\n")
    for url in URL_LIST:
        text_area.insert(tk.END, f"{url}\n")
        code, text = check_url_status(url)
        if code is None:
            text_area.insert(tk.END, f"  Status: {text}\n\n")
            status_list.append({"url": url, "status": text, "code": "N/A"})
            status_var.set("Готово")
        else:
            text_area.insert(tk.END, f"  Status: {text} - {code}\n\n")
            status_list.append({"url": url, "status": text, "code": code})
            status_var.set("Готово")


#Функция сохранения результата
def save_file():
    if not status_list:
        messagebox.showwarning(
            "Предупреждение", "Сначала выполните проверку !")
        return False
    try:
        with open('http_monitor.txt', 'w', encoding = 'utf-8') as file_save:
            file_save.write("- HTTP Status Monitor -\n\n")
            file_save.write("URL - Available - Code\n\n")
            for i in status_list:
                file_save.write(f"{i['url']} - {i['status']} - {i['code']}\n")
        messagebox.showinfo(
            "Успех", "Результат сохранён в http_monitor.txt")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")


#Функция выхода
def exit_program():
    exit()


#Функция завершние работы после удачного сохранения
def shutdown():
    if save_file() != False:
        exit_program()

# ------------------ GUI элементы ------------------

#Создание окна
winmain = tk.Tk()
winmain.title("HTTP Status")
winmain.geometry("800x400")

#Кнопки
btn_frame = ttk.Frame(winmain)
btn_frame.pack(fill = "x", padx = 10, pady = 10)

btn_check = ttk.Button(
    btn_frame, text = "Проверить статусы", command = run_check)
btn_check.pack(side = "left", padx = 5)

btn_save = ttk.Button(
    btn_frame, text = "Сохранить результат", command = shutdown)
btn_save.pack(side = "left", padx = 5)

btn_save = ttk.Button(
    btn_frame, text = "Выход", command = exit_program)
btn_save.pack(side = "left", padx = 5)

#Сообщение
status_var = tk.StringVar()
status_var.set(
    "Нажмите 'Проверить статусы' чтоб проверить доступность URL Ссылок.")
status_bar = ttk.Label(
    winmain, textvariable = status_var, relief = "sunken", anchor = "w")
status_bar.pack(side = "bottom", fill = "x")
text_area = scrolledtext.ScrolledText(
    winmain, font = ("Segoe UI", 10), height = 25)
text_area.pack(
    fill = "both", expand = True, padx = 10, pady = 10)

#Запуск
try:
    winmain.mainloop()
except KeyboardInterrupt:
    exit_program()