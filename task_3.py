# task 3.3 (GUI 2.3)

import requests
import json
import tkinter as tk
from tkinter import ttk, messagebox

# Константы
URL_CBR = "https://www.cbr-xml-daily.ru/daily_json.js"
SAVE_FILE = "resource/save.json"

# ------------------ Логика ------------------

# Функция получения данных о курсах валют
def get_currency_data():
    try:
        response = requests.get(URL_CBR, timeout = 10)
        response.raise_for_status()
        data_dict = response.json()
        return data_dict["Valute"]
    except (requests.exceptions.RequestException, KeyError):
        messagebox.showerror("Ошибка", "Не удалось получить данные!")
        return {}


# Функция загрузки групп из JSON файла
def load_groups():
    try:
        with open(SAVE_FILE, 'r', encoding = 'utf-8') as file_load:
            return json.load(file_load)
    except (json.JSONDecodeError, FileNotFoundError):
        messagebox.showerror("Ошибка", "Не удалось загрузить файл!")
        return {}


# Функция сохранения групп в JSON файл
def save_groups(group_dict):
    try:
        with open(SAVE_FILE, 'w', encoding = 'utf-8') as file_save:
            json.dump(group_dict, file_save, ensure_ascii = False, indent = 4)
        return True
    except FileNotFoundError:
        messagebox.showerror("Ошибка", "Не удалось сохранить файл!")
        return False


# Функция обновления списка валют в дереве
def update_currency_tree(tree, currency_dict):
    for i in tree.get_children():
        tree.delete(i)
    for code, info_dict in currency_dict.items():
        tree.insert("", tk.END, values = (
            code,
            info_dict['Name'],
            f"{info_dict['Value']:.4f}",
            info_dict['Nominal']
        ))


# Функция обновления списка групп
def update_group_list(listbox, group_dict):
    listbox.delete(0, tk.END)
    for group_name in group_dict.keys():
        listbox.insert(tk.END, group_name)


# Функция отображения валют выбранной группы
def show_group_currencies(group_dict, currency_dict, group_name, text_area):
    text_area.delete(1.0, tk.END)
    if group_name not in group_dict:
        text_area.insert(tk.END, "Группа не найдена!\n")
        return

    currency_codes = group_dict[group_name]
    if not currency_codes:
        text_area.insert(tk.END, f"Группа '{group_name}' пуста\n")
        return

    text_area.insert(tk.END, f"Группа: {group_name}\n")
    text_area.insert(tk.END, "-" * 50 + "\n")
    for i in currency_codes:
        if i in currency_dict:
            info_dict = currency_dict[i]
            text_area.insert(
                tk.END, f"{i} - {
                info_dict['Name']}: {
                info_dict['Value']:.4f} RUB\n")
        else:
            text_area.insert(tk.END, f"{i} - (неизвестная валюта)\n")


# Функция создания группы
def create_group(group_dict, group_listbox):
    dialog = tk.Toplevel()
    dialog.title("Создание группы")
    dialog.geometry("300x150")
    dialog.transient()
    dialog.grab_set()
    ttk.Label(dialog, text = "Введите название группы:").pack(pady = 10)
    entry = ttk.Entry(dialog, width = 30)
    entry.pack(pady = 5)


    def do_create():
        group_name = entry.get().strip()
        if group_name == "":
            messagebox.showerror("Ошибка", "Название не может быть пустым!")
            return
        if group_name in group_dict:
            messagebox.showerror("Ошибка", "Группа уже существует!")
            return
        group_dict[group_name] = []
        if save_groups(group_dict):
            update_group_list(group_listbox, group_dict)
            messagebox.showinfo("Успех", f"Группа '{group_name}' создана")
            dialog.destroy()
    ttk.Button(dialog, text = "Создать", command = do_create).pack(pady = 10)


# Функция добавления валюты в группу
def add_currency_to_group(currency_dict, group_dict):
    if not group_dict:
        messagebox.showerror("Ошибка", "Нет групп. Сначала создайте группу!")
        return

    dialog = tk.Toplevel()
    dialog.title("Добавление валюты в группу")
    dialog.geometry("300x200")
    dialog.transient()
    dialog.grab_set()
    ttk.Label(dialog, text = "Выберите группу:").pack(pady = 5)
    group_var = tk.StringVar()
    group_combo = ttk.Combobox(
        dialog, textvariable = group_var, values = list(
            group_dict.keys()), width = 27)
    group_combo.pack(pady=5)
    ttk.Label(dialog, text = "Введите код валюты:").pack(pady = 5)
    code_entry = ttk.Entry(dialog, width = 30)
    code_entry.pack(pady = 5)


    def add_from_group():
        group_name = group_var.get()
        currency_code = code_entry.get().strip().upper()

        if group_name not in group_dict:
            messagebox.showerror("Ошибка", "Группа не найдена!")
            return
        if currency_code == "":
            messagebox.showerror("Ошибка", "Код валюты не может быть пустым!")
            return
        if currency_code not in currency_dict:
            messagebox.showerror("Ошибка", "Код валюты не найден!")
            return

        if currency_code in group_dict[group_name]:
            messagebox.showwarning(
                "Внимание", f"Валюта '{
                currency_code}' уже есть в группе '{
                group_name}'")
            return

        group_dict[group_name].append(currency_code)
        if save_groups(group_dict):
            messagebox.showinfo(
                "Успех", f"Валюта '{
                currency_code}' добавлена в группу '{
                group_name}'")
            dialog.destroy()
    ttk.Button(
        dialog, text = "Добавить", command = add_from_group).pack(pady = 10)


# Функция удаления валюты из группы
def remove_currency_from_group(group_dict, group_listbox, text_area):
    if not group_dict:
        messagebox.showerror("Ошибка", "Нет групп!")
        return

    dialog = tk.Toplevel()
    dialog.title("Удаление валюты из группы")
    dialog.geometry("350x300")
    dialog.transient()
    dialog.grab_set()
    ttk.Label(dialog, text = "Выберите группу:").pack(pady = 5)
    group_var = tk.StringVar()
    group_combo = ttk.Combobox(
        dialog, textvariable = group_var, values = list(
            group_dict.keys()), width = 30)
    group_combo.pack(pady = 5)
    ttk.Label(dialog, text = "Выберите валюту для удаления:").pack(pady =5)
    currency_listbox = tk.Listbox(dialog, height = 8, width = 40)
    currency_listbox.pack(pady = 5)


    def update_currency_list():
        currency_listbox.delete(0, tk.END)
        group_name = group_var.get()
        if group_name in group_dict:
            for code in group_dict[group_name]:
                currency_listbox.insert(tk.END, code)
    group_combo.bind("<<ComboboxSelected>>", update_currency_list)


    def remove_currency():
        group_name = group_var.get()
        selection = currency_listbox.curselection()
        if group_name not in group_dict:
            messagebox.showerror("Ошибка", "Группа не найдена!")
            return

        if not selection:
            messagebox.showerror("Ошибка", "Выберите валюту для удаления!")
            return

        currency_code = currency_listbox.get(selection[0])
        group_dict[group_name].remove(currency_code)
        if save_groups(group_dict):
            update_group_list(group_listbox, group_dict)
            show_group_currencies(group_dict, currency_dict, group_name, text_area)
            messagebox.showinfo(
                "Успех", f"Валюта '{
                currency_code}' удалена из группы '{
                group_name}'")
            dialog.destroy()
    ttk.Button(
        dialog, text = "Удалить", command = remove_currency).pack(pady = 10)


# Функция просмотра всех групп
def visible_all_group(group_dict, currency_dict, text_area):
    text_area.delete(1.0, tk.END)
    if not group_dict:
        text_area.insert(tk.END, "Группы не созданы\n")
        return

    for group_name, currency_codes in group_dict.items():
        text_area.insert(tk.END, f"Группа: {group_name}\n")
        text_area.insert(tk.END, "-" * 40 + "\n")
        if not currency_codes:
            text_area.insert(tk.END, "  (пустая группа)\n")
        else:
            for code in currency_codes:
                if code in currency_dict:
                    info_dict = currency_dict[code]
                    text_area.insert(
                        tk.END, f"  {code} - {
                        info_dict['Name']}: {
                        info_dict['Value']:.4f} RUB\n")
                else:
                    text_area.insert(
                        tk.END, f"  {code} - (неизвестная валюта)\n")
        text_area.insert(tk.END, "\n")


# Функция просмотра выбранной группы
def visible_selected_group(
        group_dict,
        currency_dict,
        group_listbox,
        text_area):
    selection = group_listbox.curselection()
    if not selection:
        messagebox.showwarning("Внимание", "Сначала выберите группу!")
        return
    group_name = group_listbox.get(selection[0])
    show_group_currencies(group_dict, currency_dict, group_name, text_area)


# ------------------ GUI ------------------


# Создание окна
winmain = tk.Tk()
winmain.title("Курсы валют")
winmain.geometry("1200x600")

# Получение данных
currency_dict_main = get_currency_data()
group_dict_main = load_groups()

# Основной фрейм
main_frame = ttk.Frame(winmain, padding = "10")
main_frame.pack(fill = "both", expand = True)

# Левая панель - группы
left_frame = ttk.LabelFrame(main_frame, text ="Группы", padding = "10")
left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

group_listbox_main = tk.Listbox(left_frame, height = 20, width = 25)
group_listbox_main.pack(fill = "both", expand = True, pady = (0, 5))

update_group_list(group_listbox_main, group_dict_main)

# Кнопки управления группами
btn_frame = ttk.Frame(left_frame)
btn_frame.pack(fill = "x")

ttk.Button(btn_frame,
           text = "Создать",
           command = lambda: create_group(
               group_dict_main, group_listbox_main)).pack(
    side = "left", padx = 2)
ttk.Button(btn_frame,
           text = "Добавить валюту",
           command = lambda: add_currency_to_group(
               currency_dict_main, group_dict_main)).pack(
    side = "left", padx = 2)
ttk.Button(btn_frame,
           text= "Удалить валюту",
           command = lambda: remove_currency_from_group(
               group_dict_main, group_listbox_main, text_area_main)).pack(
    side = "left", padx = 2)

# Центральная панель - дерево валют
center_frame = ttk.LabelFrame(main_frame, text = "Все валюты", padding = "10")
center_frame.grid(row = 0, column = 1, sticky = "nsew", padx = 5)
columns = ("Код", "Название", "Курс", "Номинал")
tree_main = ttk.Treeview(
    center_frame, columns = columns, show = "headings", height = 15)
tree_main.heading("Код", text = "Код")
tree_main.heading("Название", text = "Название")
tree_main.heading("Курс", text = "Курс (RUB)")
tree_main.heading("Номинал", text = "Номинал")
tree_main.column("Код", width = 80)
tree_main.column("Название", width = 200)
tree_main.column("Курс", width = 100)
tree_main.column("Номинал", width = 80)
scrollbar = ttk.Scrollbar(
    center_frame, orient = "vertical", command = tree_main.yview)
tree_main.configure(yscrollcommand = scrollbar.set)
tree_main.pack(side = "left", fill = "both", expand = True)
scrollbar.pack(side = "right", fill = "y")

update_currency_tree(tree_main, currency_dict_main)

# Правая панель - отображение группы
right_frame = ttk.LabelFrame(
    main_frame, text = "Детали группы", padding = "10")
right_frame.grid(row = 0, column = 2, sticky = "nsew", padx = (5, 0))
text_area_main = tk.Text(right_frame, height=20, width=40, wrap = "word")
text_area_main.pack(fill = "both", expand = True, pady = (0, 5))
scrollbar_text = ttk.Scrollbar(
    right_frame, orient = "vertical", command = text_area_main.yview)
text_area_main.configure(yscrollcommand  =  scrollbar_text.set)
scrollbar_text.pack(side = "right", fill = "y")

# Кнопка показа выбранной группы
ttk.Button(right_frame,
           text = "Показать выбранную группу",
           command = lambda: visible_selected_group(
               group_dict_main,
               currency_dict_main,
               group_listbox_main,
               text_area_main)).pack()

# Кнопка показа всех групп
ttk.Button(right_frame,
           text = "Показать все группы",
           command = lambda: visible_all_group(
               group_dict_main,
               currency_dict_main,
               text_area_main)).pack(pady = (5, 0))
main_frame.columnconfigure(0, weight = 0)
main_frame.columnconfigure(1, weight = 1)
main_frame.columnconfigure(2, weight = 0)
main_frame.rowconfigure(0, weight = 1)

# Кнопка обновления курсов
refresh_frame  =  ttk.Frame(main_frame)
refresh_frame.grid(row = 1, column = 0, columnspan = 3, pady = 10)


def refresh_currencies():
    global currency_dict
    new_currency_dict = get_currency_data()
    if new_currency_dict:
        currency_dict = new_currency_dict
        update_currency_tree(tree_main, currency_dict)
        messagebox.showinfo("Успех", "Курсы обновлены!")
ttk.Button(
    refresh_frame, text = "Обновить курсы", command = refresh_currencies).pack()


# Запуск
winmain.mainloop()
