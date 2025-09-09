
import tkinter as tk
from tkinter import ttk, messagebox
import urllib.request
import xml.dom.minidom
#from matplotlib.figure import Figure
#from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime

# Цветовые темы
themes = {
    "Светлая": {
        "bg": "#f0f0f0",
        "fg": "#f0f0f0",
        "button_bg": "#e0e0e0",
        "button_fg": "#000000",
        "tab_bg": "#ffffff",
        "tab_fg": "#000000",
        "plot_bg": "#ffffff",
        "entry_bg": "#ffffff",
        "entry_fg": "#000000",
        "tab_selected_bg": "#ffffff",
        "tab_selected_fg": "#000000"
    },
    "Темная": {
        "bg": "#2d2d2d",
        "fg": "#ffffff",
        "button_bg": "#3d3d3d",
        "button_fg": "#ffffff",
        "tab_bg": "#1e1e1e",
        "tab_fg": "#ffffff",
        "plot_bg": "#1e1e1e",
        "entry_bg": "#3d3d3d",
        "entry_fg": "#ffffff",
        "tab_selected_bg": "#3d3d3d",
        "tab_selected_fg": "#ffffff"
    },
    "Синяя": {
        "bg": "#d9e8ff",
        "fg": "#003366",
        "button_bg": "#b3d1ff",
        "button_fg": "#003366",
        "tab_bg": "#e6f2ff",
        "tab_fg": "#003366",
        "plot_bg": "#e6f2ff",
        "entry_bg": "#ffffff",
        "entry_fg": "#003366",
        "tab_selected_bg": "#ffffff",
        "tab_selected_fg": "#003366"
    }
}

current_theme = "Светлая"
favorites = []
conversion_history = []
plot_widget = None  # Инициализация глобальной переменной


def apply_theme(theme_name):
    global current_theme
    current_theme = theme_name
    theme = themes[theme_name]

    # Основное окно
    window.config(bg=theme["bg"])

    # Стили для ttk
    style = ttk.Style()

    # Общие настройки
    style.configure('.',
                    background=theme["bg"],
                    foreground=theme["fg"])

    # Стиль для Frame
    style.configure('TFrame', background=theme["tab_bg"])

    # Стиль для кнопок
    style.configure('TButton',
                    background=theme["button_bg"],
                    foreground=theme["button_fg"],
                    borderwidth=1)

    # Стиль для Combobox
    style.configure('TCombobox',
                    fieldbackground=theme["entry_bg"],
                    background=theme["entry_bg"],
                    foreground=theme["fg"],
                    insertcolor=theme["fg"])
    style.map('TCombobox',
              fieldbackground=[('readonly', theme["entry_bg"])],
              background=[('readonly', theme["entry_bg"])])

    # Стиль для Notebook и вкладок
    style.configure('TNotebook', background=theme["bg"])
    style.configure('TNotebook.Tab',
                    background=theme["bg"],
                    foreground=theme["tab_fg"],
                    padding=[5, 2],
                    lightcolor=theme["bg"],
                    darkcolor=theme["bg"])
    style.map('TNotebook.Tab',
              background=[('selected', theme["tab_selected_bg"])],
              foreground=[('selected', theme["tab_selected_fg"])])

    # Вкладка 1 (обычные tkinter виджеты)
    label_currency1.config(bg=theme["tab_bg"], fg=theme["fg"])
    amount_entry.config(bg=theme["entry_bg"], fg=theme["entry_fg"],
                        insertbackground=theme["fg"])
    btn.config(bg=theme["button_bg"], fg=theme["button_fg"])
    result_label.config(bg=theme["tab_bg"], fg=theme["fg"])
    reverse_btn.config(bg=theme["button_bg"], fg=theme["button_fg"])
    fav_btn.config(bg=theme["button_bg"], fg=theme["button_fg"])

    # Вкладка 2 (обычные tkinter виджеты)
    label_currency2.config(bg=theme["tab_bg"], fg=theme["fg"])
    radiobutton1.config(bg=theme["tab_bg"], fg=theme["fg"], selectcolor=theme["bg"])
    radiobutton2.config(bg=theme["tab_bg"], fg=theme["fg"], selectcolor=theme["bg"])
    radiobutton3.config(bg=theme["tab_bg"], fg=theme["fg"], selectcolor=theme["bg"])
    radiobutton4.config(bg=theme["tab_bg"], fg=theme["fg"], selectcolor=theme["bg"])
    analysis_btn.config(bg=theme["button_bg"], fg=theme["button_fg"])

    # Обновляем график, если он есть
    if plot_widget is not None:
        show_plot()


def change_theme():
    theme_names = list(themes.keys())
    current_index = theme_names.index(current_theme)
    next_index = (current_index + 1) % len(theme_names)
    apply_theme(theme_names[next_index])


def update_currency_list():
    today_date = datetime.datetime.now()
    today_data = today_date.strftime("%d/%m/%Y")
    url = f"http://www.cbr.ru/scripts/XML_daily.asp?date_req={today_data}"
    try:
        response = urllib.request.urlopen(url)
        dom = xml.dom.minidom.parse(response)
        dom.normalize()
        currencies = dom.getElementsByTagName("Valute")
        currency_names = []
        currency_values = {}
        for currency in currencies:
            name = currency.getElementsByTagName("Name")[0].firstChild.nodeValue
            value = float(currency.getElementsByTagName("Value")[0].firstChild.nodeValue.replace(',', '.'))
            nominal = int(currency.getElementsByTagName("Nominal")[0].firstChild.nodeValue)
            currency_values[name] = value / nominal
            currency_names.append(name)
        combo1_1["values"] = currency_names
        combo1_2["values"] = currency_names
        combo2_1["values"] = currency_names
        return currency_values
    except urllib.error.URLError as e:
        messagebox.showerror("Ошибка", f"Не удалось загрузить курсы валют: {e}")
        return {}


# Функция обратной конвертации
def reverse_currencies():
    curr1 = combo1_1.get()
    curr2 = combo1_2.get()
    combo1_1.set(curr2)
    combo1_2.set(curr1)


# Функции для избранных валют
def add_to_favorites():
    currency = combo1_1.get()
    if currency:
        favorites.append(currency)
        update_favorites_menu()



def update_favorites_menu():
    fav_menu.delete(0, 'end')
    for currency in favorites:
        fav_menu.add_command(label=currency,
                             command=lambda c=currency: select_favorite(c))


def select_favorite(currency):
    combo1_1.set(currency)


# Функция анализа курса
def show_analysis():
    currency = combo2_1.get()
    if not currency:
        messagebox.showerror("Ошибка", "Выберите валюту для анализа")
        return

    period = scale_var0.get()
    start_date, end_date = update_combo2_2()
    data = fetch_currency_data(currency, start_date, end_date, period)

    values = [value for date, value in data if value is not None]
    if values:
        analysis_window = tk.Toplevel(window)
        analysis_window.title(f"Анализ курса {currency}")

        min_val = min(values)
        max_val = max(values)
        avg_val = sum(values) / len(values)
        last_val = values[-1]

        text = (f"Период: {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}\n"
                f"Минимальный курс: {min_val:.4f}\n"
                f"Максимальный курс: {max_val:.4f}\n"
                f"Средний курс: {avg_val:.4f}\n"
                f"Текущий курс: {last_val:.4f}\n"
                f"Изменение: {((last_val - values[0]) / values[0] * 100):+.2f}%")

        tk.Label(analysis_window, text=text, justify=tk.LEFT).pack(padx=10, pady=10)

        # Кнопка закрытия
        tk.Button(analysis_window, text="Закрыть", command=analysis_window.destroy).pack(pady=5)


# Функция конвертации с сохранением истории
def convert():
    from_currency = combo1_1.get()
    to_currency = combo1_2.get()
    amount_str = amount_entry.get()

    if not from_currency or not to_currency:
        messagebox.showerror("Ошибка", "Выберите валюты для конвертации")
        return

    try:
        amount = float(amount_str)
    except ValueError:
        messagebox.showerror("Ошибка", "Введите корректную сумму")
        return

    currency_values = update_currency_list()
    if from_currency in currency_values and to_currency in currency_values:
        convert_amount = amount / currency_values[from_currency] / currency_values[to_currency]
        result_label.config(text=f"{convert_amount:.4f}")

        # Добавляем в историю
        conversion_history.append({
            'date': datetime.datetime.now().strftime("%d.%m.%Y %H:%M"),
            'from': (amount, from_currency),
            'to': (convert_amount, to_currency)
        })
    else:
        result_label.config(text="Не удалось найти курс валюты")


window = tk.Tk()
window.title("Конвертер Валют")
window.geometry("600x400")

# Меню с избранными валютами
menubar = tk.Menu(window)
fav_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="Избранное", menu=fav_menu)
window.config(menu=menubar)

# Кнопка смены темы
theme_button = tk.Button(window, text="Сменить тему", command=change_theme)
theme_button.pack(side=tk.BOTTOM, pady=5)

'''КОНВЕРТЕР ВАЛЮТ'''
tab_control = ttk.Notebook(window)
tab1 = ttk.Frame(tab_control)
tab2 = ttk.Frame(tab_control)

tab_control.add(tab1, text="Конвертация валют")
tab_control.add(tab2, text="Динамика курса")
tab_control.pack(expand=1, fill="both")

# Вкладка 1 - Конвертация
label_currency1 = tk.Label(tab1, text="Из валюты:")
label_currency1.grid(column=0, row=0, padx=5, pady=5)

# Поле выбора валюты и кнопка избранного
combo1_1 = ttk.Combobox(tab1, width=15)
combo1_1.grid(column=0, row=1, padx=(5, 0), pady=5)

# Кнопка добавления в избранное (теперь справа от поля выбора валюты)
fav_btn = tk.Button(tab1, text="★", command=add_to_favorites, width=2)
fav_btn.grid(column=1, row=1, padx=(0, 5), pady=5)

# Кнопка обратной конвертации (между полями выбора валют)
reverse_btn = tk.Button(tab1, text="↔", command=reverse_currencies, width=2)
reverse_btn.grid(column=0, row=2, columnspan=2, pady=5)

label_currency2 = tk.Label(tab1, text="Из валюты:")
label_currency2.grid(column=0, row=3, padx=5, pady=5)

combo1_2 = ttk.Combobox(tab1, width=15)
combo1_2.grid(column=0, row=4, padx=5, pady=5, columnspan=2)

# Поле для ввода суммы
amount_label = tk.Label(tab1, text="Сумма:")
amount_label.grid(column=2, row=0, padx=5, pady=5)

amount_entry = tk.Entry(tab1, width=15)
amount_entry.grid(column=2, row=1, padx=5, pady=5)

# Кнопка конвертации
btn = tk.Button(tab1, text="Конвертировать", command=convert)
btn.grid(column=2, row=2, padx=5, pady=5)

# Поле результата
result_label = tk.Label(tab1, text="")
result_label.grid(column=2, row=4, padx=5, pady=5)
'''ДИНАМИКА КУРСА'''
label_currency2 = tk.Label(tab2, text="Валюта")
label_currency2.grid(column=0, row=0)

combo2_1 = ttk.Combobox(tab2)
combo2_1.grid(column=0, row=1, padx=5, pady=10)

scale_var0 = tk.IntVar()
scale_var0.set(4)

radiobutton1 = tk.Radiobutton(tab2, text='неделя', value=1, variable=scale_var0)
radiobutton1.grid(column=1, row=1, padx=5, pady=10)
radiobutton2 = tk.Radiobutton(tab2, text='месяц', value=2, variable=scale_var0)
radiobutton2.grid(column=1, row=2, padx=5, pady=10)
radiobutton3 = tk.Radiobutton(tab2, text='квартал', value=3, variable=scale_var0)
radiobutton3.grid(column=1, row=3, padx=5, pady=10)
radiobutton4 = tk.Radiobutton(tab2, text='год', value=4, variable=scale_var0)
radiobutton4.grid(column=1, row=4, padx=5, pady=10)

combo2_2 = ttk.Combobox(tab2)
combo2_2.grid(column=2, row=1, padx=5, pady=10)

# Кнопка анализа курса
analysis_btn = tk.Button(tab2, text="Анализ", command=show_analysis)
analysis_btn.grid(column=2, row=2, padx=5, pady=10)

plot1_button = ttk.Button(tab2, text="Получить данные")
plot1_button.grid(column=2, row=3, padx=5, pady=10)

plot_button = ttk.Button(tab2, text="Построить график", command=lambda: None)
plot_button.grid(column=2, row=4, padx=5, pady=10)


def update_combo2_2():
    value = scale_var0.get()
    today = datetime.datetime.now()
    start_date = None
    end_date = None

    if value == 1:
        end_date = today
        start_date = end_date - datetime.timedelta(days=7)
    elif value == 2:
        end_date = today
        start_date = datetime.datetime(end_date.year, end_date.month, 1)
    elif value == 3:
        end_date = today
        start_date = datetime.datetime(end_date.year, (end_date.month - 1) // 3 * 3 + 1, 1)
    elif value == 4:
        end_date = today
        start_date = datetime.datetime(end_date.year, 1, 1)

    if value == 1:
        combo2_2["value"] = [f"{start_date.strftime('%d.%m.%Y')}-{end_date.strftime('%d.%m.%Y')}",
                             f"{start_date - datetime.timedelta(days=7):%d.%m.%Y}-{start_date:%d.%m.%Y}",
                             f"{start_date - datetime.timedelta(days=14):%d.%m.%Y}-{start_date - datetime.timedelta(days=7):%d.%m.%Y}",
                             f"{start_date - datetime.timedelta(days=21):%d.%m.%Y}-{start_date - datetime.timedelta(days=14):%d.%m.%Y}"]
    elif value == 2:
        combo2_2["value"] = [f"{start_date:%m.%Y}",
                             f"{start_date - datetime.timedelta(days=30):%m.%Y}",
                             f"{start_date - datetime.timedelta(days=60):%m.%Y}",
                             f"{start_date - datetime.timedelta(days=90):%m.%Y}"]
    elif value == 3:
        combo2_2["value"] = [f"{start_date:%d.%m.%Y}-{end_date:%d.%m.%Y}",
                             f"{start_date - datetime.timedelta(days=90):%d.%m.%Y}-{start_date - datetime.timedelta(days=60):%d.%m.%Y}",
                             f"{start_date - datetime.timedelta(days=180):%d.%m.%Y}-{start_date - datetime.timedelta(days=120):%d.%m.%Y}",
                             f"{start_date - datetime.timedelta(days=270):%d.%m.%Y}-{start_date - datetime.timedelta(days=210):%d.%m.%Y}"]
    elif value == 4:
        combo2_2["value"] = [f"{start_date:%Y}",
                             f"{start_date - datetime.timedelta(days=365):%Y}",
                             f"{start_date - datetime.timedelta(days=730):%Y}",
                             f"{start_date - datetime.timedelta(days=1095):%Y}"]

    return start_date, end_date


scale_var0.trace('w', lambda *args: update_combo2_2())


def fetch_currency_data(currency, start_date, end_date, period):
    current_date = start_date
    currency_data = []

    while current_date <= end_date:
        url = f"http://www.cbr.ru/scripts/XML_daily.asp?date_req={current_date.strftime('%d/%m/%Y')}"
        try:
            response = urllib.request.urlopen(url)
            dom = xml.dom.minidom.parse(response)
            dom.normalize()

            found = False
            for record in dom.getElementsByTagName("Valute"):
                if record.getElementsByTagName("Name")[0].firstChild.nodeValue == currency:
                    value = float(record.getElementsByTagName("Value")[0].firstChild.nodeValue.replace(',', '.'))
                    nominal = int(record.getElementsByTagName("Nominal")[0].firstChild.nodeValue)
                    currency_data.append((current_date, value / nominal))
                    found = True
                    break

            if not found:
                currency_data.append((current_date, None))
        except urllib.error.URLError as e:
            currency_data.append((current_date, None))
            print(f"Ошибка при получении курса на {current_date}: {e}")

        if period == 1:
            current_date += datetime.timedelta(days=1)
        elif period == 2:
            current_date += datetime.timedelta(days=4)
        elif period == 3:
            current_date += datetime.timedelta(weeks=1)
        elif period == 4:
            current_date += datetime.timedelta(days=30)

    return currency_data


def plot_currency_data(currency_data):
    fig = Figure(figsize=(10, 5))
    ax = fig.add_subplot(111)
    dates = [date for date, value in currency_data]
    values = [value for date, value in currency_data if value is not None]
    ax.plot(dates, values, marker='o', linestyle='-')
    ax.set_title('Курс валюты')
    ax.set_xlabel('Дата')
    ax.set_ylabel('Значение курса')
    ax.grid(True)
    ax.tick_params(axis='x', rotation=45)

    theme = themes[current_theme]
    fig.patch.set_facecolor(theme["tab_bg"])
    ax.set_facecolor(theme["tab_bg"])
    ax.title.set_color(theme["fg"])
    ax.xaxis.label.set_color(theme["fg"])
    ax.yaxis.label.set_color(theme["fg"])
    ax.tick_params(axis='x', colors=theme["fg"])
    ax.tick_params(axis='y', colors=theme["fg"])
    for spine in ax.spines.values():
        spine.set_color(theme["fg"])

    return fig


def show_plot():
    global plot_widget
    currency = combo2_1.get()
    if not currency:
        messagebox.showerror("Ошибка", "Выберите валюту для графика")
        return

    period = scale_var0.get()
    start_date, end_date = update_combo2_2()
    data = fetch_currency_data(currency, start_date, end_date, period)
    fig = plot_currency_data(data)

    if plot_widget is not None:
        plot_widget.get_tk_widget().destroy()

    plot_widget = FigureCanvasTkAgg(fig, master=tab2)
    plot_widget.draw()
    plot_widget.get_tk_widget().grid(column=0, row=5, columnspan=3, padx=5, pady=10)


plot_button.config(command=show_plot)

# Применяем начальную тему
apply_theme(current_theme)
window.after(100, update_currency_list)

window.mainloop()