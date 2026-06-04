# task 3.4 (GUI 2.4)

import requests
import json
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

# Константы
GITHUB_API_URL = "https://api.github.com"
SAVE_FILE = "resource/github_data.json"

# ------------------ Логика ------------------

# Функция выполнение запроса к GitHub API
def make_github_request(url):
    try:
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Python-GitHub-App"
        }
        response = requests.get(url, headers = headers, timeout = 10)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return None
        else:
            return None
    except (requests.exceptions.RequestException, json.JSONDecodeError):
        return None


# Функция получение профиля пользователя
def get_user_profile(username):
    url = f"{GITHUB_API_URL}/users/{username}"
    data = make_github_request(url)
    if data is None:
        return None
    profile = {
        "username": data.get("login", "N/A"),
        "name": data.get("name", "Not specified"),
        "profile_url": data.get("html_url", "N/A"),
        "repos_count": data.get("public_repos", 0),
        "gists_count": data.get("public_gists", 0),
        "following_count": data.get("following", 0),
        "followers_count": data.get("followers", 0),
        "created_at": data.get("created_at", "N/A"),
        "company": data.get("company", "Not specified"),
        "location": data.get("location", "Not specified"),
        "bio": data.get("bio", "Not specified")
    }
    return profile


# Функция получение репозиториев пользователя
def get_user_repositories(username):
    url = f"{GITHUB_API_URL}/users/{username}/repos?per_page=100&sort=updated"
    data = make_github_request(url)
    if data is None:
        return None

    repositories = []
    for i in data:
        repo_info = {
            "name": i.get("name", "N/A"),
            "url": i.get("html_url", "N/A"),
            "language": i.get("language", "Not specified"),
            "visibility": "Public" if not i.get("private", False) else "Private",
            "default_branch": i.get("default_branch", "N/A"),
            "stars": i.get("stargazers_count", 0),
            "forks": i.get("forks_count", 0),
            "description": i.get("description", "No description")
        }
        repositories.append(repo_info)
    return repositories


# Функция поиск репозиториев по названию
def search_repositories(query):
    url = f"{GITHUB_API_URL}/search/repositories?q={query}&per_page=20"
    data = make_github_request(url)
    if data is None:
        return None

    repositories = []
    for repo in data.get("items", []):
        repo_info = {
            "full_name": repo.get("full_name", "N/A"),
            "url": repo.get("html_url", "N/A"),
            "language": repo.get("language", "Not specified"),
            "stars": repo.get("stargazers_count", 0),
            "forks": repo.get("forks_count", 0),
            "description": repo.get("description", "No description"),
            "owner": repo.get("owner", {}).get("login", "N/A")
        }
        repositories.append(repo_info)
    return repositories


# Функция сохранения данных в JSON
def save_to_file(data, filename):
    try:
        with open(filename, 'w', encoding = 'utf-8') as save_file:
            json.dump(data, save_file, ensure_ascii = False, indent = 4)
        return True
    except FileNotFoundError:
        return False


# ------------------ GUI ------------------


# Создание окна
winmain = tk.Tk()
winmain.title("GitHub API Explorer")
winmain.geometry("700x700")


# Функция показа профиля пользователя
def show_user_profile():
    username = entry_username.get().strip()
    if username == "":
        messagebox.showerror("Ошибка", "Введите имя пользователя!")
        return

    text_area.delete(1.0, tk.END)
    text_area.insert(tk.END, "Загрузка профиля...\n")
    winmain.update()
    profile = get_user_profile(username)
    if profile is None:
        text_area.delete(1.0, tk.END)
        text_area.insert(
            tk.END, f"Ошибка! Пользователь '{username}' не найден!\n")
        messagebox.showerror(
            "Ошибка", f"Пользователь '{username}' не найден!")
        return

    text_area.delete(1.0, tk.END)
    text_area.insert(tk.END, f"-- Профиль пользователя --\n\n")
    text_area.insert(tk.END, f"Username:     {profile['username']}\n")
    text_area.insert(tk.END, f"Name:         {profile['name']}\n")
    text_area.insert(tk.END, f"Profile URL:  {profile['profile_url']}\n")
    text_area.insert(tk.END, f"Bio:          {profile['bio']}\n")
    text_area.insert(tk.END, f"Location:     {profile['location']}\n")
    text_area.insert(tk.END, f"Company:      {profile['company']}\n")
    text_area.insert(tk.END, f"Created:      {profile['created_at'][:10]}\n")
    text_area.insert(tk.END, f"Public Repos: {profile['repos_count']}\n")
    text_area.insert(tk.END, f"Public Gists: {profile['gists_count']}\n")
    text_area.insert(tk.END, f"Following:    {profile['following_count']}\n")
    text_area.insert(tk.END, f"Followers:    {profile['followers_count']}\n")


    # Кнопка сохранения
    def save_profile():
        if save_to_file(profile, SAVE_FILE):
            messagebox.showinfo("Успех", f"Профиль сохранён в {SAVE_FILE}")
        else:
            messagebox.showerror("Ошибка", "Не удалось сохранить файл!")
    btn_save = ttk.Button(
        right_inner_frame, text = "Сохранить профиль", command = save_profile)
    btn_save.pack(pady = 5)


# Функция показа репозиториев пользователя
def show_user_repositories():
    username = entry_username.get().strip()
    if username == "":
        messagebox.showerror("Ошибка", "Введите имя пользователя!")
        return

    text_area.delete(1.0, tk.END)
    text_area.insert(tk.END, "Загрузка репозиториев...\n")
    winmain.update()
    repos = get_user_repositories(username)
    if repos is None:
        text_area.delete(1.0, tk.END)
        text_area.insert(
            tk.END, f"Ошибка! Пользователь '{username}' не найден!\n")
        messagebox.showerror(
            "Ошибка", f"Пользователь '{username}' не найден!")
        return

    if not repos:
        text_area.delete(1.0, tk.END)
        text_area.insert(
            tk.END,
            f"У пользователя '{username}' нет публичных репозиториев\n")
        return

    text_area.delete(1.0, tk.END)
    text_area.insert(
        tk.END, f"-- Репозитории пользователя '{username}' --\n\n")
    text_area.insert(tk.END, f"Найдено: {len(repos)} репозиториев\n\n")
    for i, repo in enumerate(repos, 1):
        text_area.insert(tk.END, f"{i}. {repo['name']}\n")
        text_area.insert(tk.END, f"   URL:           {repo['url']}\n")
        text_area.insert(tk.END, f"   Language:      {repo['language']}\n")
        text_area.insert(tk.END, f"   Visibility:    {repo['visibility']}\n")
        text_area.insert(
            tk.END, f"   Default branch:{repo['default_branch']}\n")
        text_area.insert(tk.END, f"   Stars:         {repo['stars']}\n")
        text_area.insert(tk.END, f"   Forks:         {repo['forks']}\n")
        if repo['description'] != "No description":
            text_area.insert(
                tk.END, f"   Description:   {repo['description']}\n")
        text_area.insert(tk.END, "\n")


# Функция поиска репозиториев
def search_repositories_by_name():
    query = entry_search.get().strip()
    if query == "":
        messagebox.showerror("Ошибка", "Введите название или ключевое слово!")
        return

    text_area.delete(1.0, tk.END)
    text_area.insert(tk.END, f"Поиск репозиториев по запросу '{query}'...\n")
    winmain.update()
    repos = search_repositories(query)
    if repos is None:
        text_area.delete(1.0, tk.END)
        text_area.insert(tk.END, "Ошибка при выполнении поиска!\n")
        messagebox.showerror("Ошибка", "Ошибка при выполнении поиска!")
        return

    if not repos:
        text_area.delete(1.0, tk.END)
        text_area.insert(tk.END, f"По запросу '{query}' ничего не найдено\n")
        return

    text_area.delete(1.0, tk.END)
    text_area.insert(tk.END, f"-- Результаты поиска: '{query}' --\n\n")
    text_area.insert(tk.END, f"Найдено: {len(repos)} репозиториев\n\n")
    for i, repo in enumerate(repos, 1):
        text_area.insert(tk.END, f"{i}. {repo['full_name']}\n")
        text_area.insert(tk.END, f"   URL:         {repo['url']}\n")
        text_area.insert(tk.END, f"   Owner:       {repo['owner']}\n")
        text_area.insert(tk.END, f"   Language:    {repo['language']}\n")
        text_area.insert(tk.END, f"   Stars:       {repo['stars']}\n")
        text_area.insert(tk.END, f"   Forks:       {repo['forks']}\n")
        if repo['description'] != "No description":
            text_area.insert(
                tk.END, f"   Description: {repo['description']}\n")
        text_area.insert(tk.END, "\n")


# Функция очистки области вывода
def clear_output():
    text_area.delete(1.0, tk.END)


# ------------------ GUI элементы ------------------


# Основной фрейм
main_frame = ttk.Frame(winmain, padding = "10")
main_frame.pack(fill = "both", expand = True)

# Левая панель - управление
left_frame = ttk.LabelFrame(main_frame, text = "Управление", padding = "10")
left_frame.grid(row = 0, column = 0, sticky = "nsew", padx = (0, 5))

# Поле для ввода username
ttk.Label(left_frame,
          text = "Имя пользователя GitHub:").pack(anchor = "w", pady = (0, 5))
entry_username = ttk.Entry(left_frame, width = 30)
entry_username.pack(fill = "x", pady = (0, 10))
entry_username.bind("<Return>", lambda event: show_user_profile())

# Кнопка просмотра профиля
ttk.Button(left_frame,
           text = "Просмотреть профиль",
           command = show_user_profile).pack(fill = "x", pady = 2)

# Кнопка просмотра репозиториев
ttk.Button(left_frame,
           text = "Просмотреть репозитории",
           command = show_user_repositories).pack(fill = "x", pady = 2)

# Разделитель
ttk.Separator(left_frame,
              orient = "horizontal").pack(fill = "x", pady = 10)

# Поле для поиска репозиториев
ttk.Label(left_frame,
          text = "Поиск репозиториев:").pack(anchor = "w", pady = (0, 5))
entry_search = ttk.Entry(left_frame, width = 30)
entry_search.pack(fill = "x", pady = (0, 10))
entry_search.bind("<Return>", lambda event: search_repositories_by_name())

# Кнопка поиска
ttk.Button(left_frame,
           text = "Найти репозитории",
           command = search_repositories_by_name).pack(fill = "x", pady = 2)

# Разделитель
ttk.Separator(left_frame,
              orient = "horizontal").pack(fill = "x", pady = 10)

# Кнопка очистки
ttk.Button(left_frame,
           text = "Очистить вывод",
           command = clear_output).pack(fill = "x", pady = 2)

# Правая панель - вывод информации
right_frame = ttk.LabelFrame(main_frame, text = "Результат", padding = "10")
right_frame.grid(row = 0, column = 1, sticky = "nsew", padx = (5, 0))

# Внутренний фрейм для текста и кнопок
right_inner_frame = ttk.Frame(right_frame)
right_inner_frame.pack(fill = "both", expand = True)

# Область вывода текста с прокруткой
text_area = scrolledtext.ScrolledText(
    right_inner_frame,
    font = ("Segoe UI", 10),
    wrap = tk.WORD,
    height = 35
)
text_area.pack(fill = "both", expand = True)

#Начальное сообщение
text_area.insert(tk.END, "GitHub API Explorer!\n")
main_frame.columnconfigure(0, weight = 0)
main_frame.columnconfigure(1, weight = 1)
main_frame.rowconfigure(0, weight = 1)

# Запуск
winmain.mainloop()