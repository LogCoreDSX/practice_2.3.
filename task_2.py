# task 3.2 (GUI 2.2)
import psutil
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# Константы
REFRESH_SECONDS = 0.5

# Глобальные переменные
running = True

# ------------------ Логика ------------------

# Функция получения информации о системе
def get_info_system(mode):
    if mode == "cpu":
        return psutil.cpu_percent(interval = 0.5)
    elif mode == "ram":
        memory_tuple = psutil.virtual_memory()
        return memory_tuple.percent
    elif mode == "disk":
        disk_tuple = psutil.disk_usage('/')
        return disk_tuple.percent
    return 0


# Функция обновления отображения в таблице
def update_display():
    global running
    if not running:
        return

    for i in tree.get_children():
        tree.delete(i)
    cpu_percent = get_info_system("cpu")
    memory_percent = get_info_system("ram")
    disk_percent = get_info_system("disk")
    times = datetime.now()
    time_info = times.strftime("%Y-%m-%d %H:%M:%S")
    tree.insert("", "end", values = ("CPU", f"{cpu_percent:.1f}%"))
    tree.insert("", "end", values = ("RAM", f"{memory_percent:.1f}%"))
    tree.insert("", "end", values = ("Disk", f"{disk_percent:.1f}%"))
    with open('system_monitor.log', 'a', encoding = 'utf-8') as log_file:
        log_file.write(
            f"CPU:{
            cpu_percent:.1f}% RAM:{
            memory_percent:.1f}% DISK:{disk_percent:.1f}% --- {time_info}\n")
    if running:
        winmain.after(int(REFRESH_SECONDS * 1000), update_display)


# Функция выхода
def exit_program():
    global running
    running = False
    winmain.destroy()


# Функция сохранения лога в файл
def save_log():
    messagebox.showinfo("Успех", "Сохранено в system_monitor.log")

# ------------------ GUI ------------------

# Создание окна
winmain = tk.Tk()
winmain.title("System Monitor")
winmain.geometry("350x250")
main_frame = ttk.Frame(winmain, padding = "10")
main_frame.pack(fill = "both", expand = True)
ttk.Label(main_frame, text = "").grid(row = 0, column = 0)
ttk.Label(main_frame, text = "").grid(row = 2, column = 0)
columns = ("Parameter", "Value")
tree = ttk.Treeview(main_frame,
                    columns = columns,
                    show = "headings",
                    height = 3)
tree.heading("Parameter", text = "Parameter")
tree.heading("Value", text = "Value")
tree.column("Parameter", width = 150)
tree.column("Value", width = 150)
tree.grid(row = 3, column = 0, columnspan = 2, pady = 10)
ttk.Label(main_frame, text = "").grid(row = 4, column = 0)
button_frame = ttk.Frame(main_frame)
button_frame.grid(row = 5, column = 0, columnspan = 2, pady = 15)
btn_save = ttk.Button(
    button_frame, text = "Сохранить лог", command = save_log)
btn_save.pack(side = "left", padx = 10)
btn_exit = ttk.Button(button_frame, text = "Выход", command = exit_program)
btn_exit.pack(side = "left", padx = 10)
ttk.Label(main_frame, text = "").grid(row = 6, column = 0)
main_frame.columnconfigure(0, weight = 1)

#Запуск
try:
    update_display()
    winmain.mainloop()
except KeyboardInterrupt:
    exit_program()