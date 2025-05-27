import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Menu
import os
import json
import csv
from pathlib import Path
from datetime import datetime
import threading
import webbrowser

class FileScannerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Сканер файлов v2.1")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Данные
        self.files_data = []
        self.scanning = False
        self.scan_progress = 0
        self.total_files_to_scan = 0
        
        # Темная тема
        self.dark_theme = False
        
        # Настройка стиля
        self.setup_styles()
        
        # Создание интерфейса
        self.create_widgets()
        
        # Горячие клавиши
        self.setup_hotkeys()
        
        # Центрируем окно
        self.center_window()
    
    def setup_styles(self):
        """Настройка стилей для красивого интерфейса"""
        self.style = ttk.Style()
        
        # Используем современную тему
        available_themes = self.style.theme_names()
        if 'clam' in available_themes:
            self.style.theme_use('clam')
        elif 'alt' in available_themes:
            self.style.theme_use('alt')
        
        # Настройка цветов для светлой темы
        self.apply_theme()
    
    def apply_theme(self):
        """Применить текущую тему"""
        if self.dark_theme:
            # Темная тема
            self.root.configure(bg='#2b2b2b')
            self.style.theme_use('clam')
            self.style.configure('TLabel', background='#2b2b2b', foreground='white')
            self.style.configure('TFrame', background='#2b2b2b')
            self.style.configure('TLabelFrame', background='#2b2b2b', foreground='white')
            self.style.configure('TButton', background='#404040', foreground='white')
            self.style.configure('TEntry', background='#404040', foreground='white')
            self.style.configure('TCheckbutton', background='#2b2b2b', foreground='white')
            self.style.configure('Treeview', background='#404040', foreground='white', fieldbackground='#404040')
            self.style.configure('Treeview.Heading', background='#505050', foreground='white')
        else:
            # Светлая тема
            self.root.configure(bg='SystemButtonFace')
            self.style.theme_use('clam')
            self.style.configure('TLabel', background='SystemButtonFace', foreground='black')
            self.style.configure('TFrame', background='SystemButtonFace')
            self.style.configure('TLabelFrame', background='SystemButtonFace', foreground='black')
            self.style.configure('TButton', background='SystemButtonFace', foreground='black')
            self.style.configure('TEntry', background='white', foreground='black')
            self.style.configure('TCheckbutton', background='SystemButtonFace', foreground='black')
            self.style.configure('Treeview', background='white', foreground='black', fieldbackground='white')
            self.style.configure('Treeview.Heading', background='SystemButtonFace', foreground='black')
    
    def toggle_theme(self):
        """Переключить тему"""
        self.dark_theme = not self.dark_theme
        self.apply_theme()
    
    def setup_hotkeys(self):
        """Настройка горячих клавиш"""
        self.root.bind('<F5>', lambda e: self.start_scan())
        self.root.bind('<Control-s>', lambda e: self.save_results())
        self.root.bind('<Delete>', lambda e: self.clear_results())
        self.root.bind('<F3>', lambda e: self.show_search_dialog())
        self.root.bind('<Control-f>', lambda e: self.show_filter_dialog())
        self.root.bind('<Control-q>', lambda e: self.quick_save())
        self.root.bind('<F1>', lambda e: self.show_help())
        self.root.bind('<Control-t>', lambda e: self.toggle_theme())
    
    def center_window(self):
        """Центрирует окно на экране"""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (900 // 2)
        y = (self.root.winfo_screenheight() // 2) - (700 // 2)
        self.root.geometry(f"900x700+{x}+{y}")
    
    def create_widgets(self):
        """Создание всех элементов интерфейса"""
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Настройка растяжения
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
        # Заголовок с кнопкой темы
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        title_label = ttk.Label(header_frame, text="🗂️ Сканер файлов v2.1", font=('Arial', 16, 'bold'))
        title_label.pack(side=tk.LEFT)
        
        theme_button = ttk.Button(header_frame, text="🌙", command=self.toggle_theme, width=3)
        theme_button.pack(side=tk.RIGHT, padx=(20, 0))
        
        # Выбор папки
        folder_frame = ttk.LabelFrame(main_frame, text="Выбор папки", padding="10")
        folder_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        folder_frame.columnconfigure(1, weight=1)
        
        ttk.Label(folder_frame, text="Папка:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        self.folder_var = tk.StringVar()
        self.folder_entry = ttk.Entry(folder_frame, textvariable=self.folder_var, font=('Arial', 10))
        self.folder_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Button(folder_frame, text="Обзор...", command=self.browse_folder).grid(row=0, column=2)
        
        # Настройки
        settings_frame = ttk.LabelFrame(main_frame, text="Настройки сканирования", padding="10")
        settings_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Чекбоксы
        options_frame = ttk.Frame(settings_frame)
        options_frame.grid(row=0, column=0, columnspan=2, sticky=tk.W)
        
        self.include_hidden = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Включить скрытые файлы", 
                       variable=self.include_hidden).grid(row=0, column=0, sticky=tk.W, padx=(0, 20))
        
        self.show_details = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Показать детали", 
                       variable=self.show_details).grid(row=0, column=1, sticky=tk.W)
        
        # Фильтр расширений
        ttk.Label(settings_frame, text="Фильтр расширений:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        
        self.extensions_var = tk.StringVar()
        extensions_entry = ttk.Entry(settings_frame, textvariable=self.extensions_var, width=40)
        extensions_entry.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=(10, 0))
        
        ttk.Label(settings_frame, text="(например: .txt .py .jpg)", font=('Arial', 8)).grid(
            row=2, column=1, sticky=tk.W, padx=(10, 0), pady=(2, 0))
        
        # Кнопки действий
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=3, column=0, columnspan=3, pady=(0, 10))
        
        self.scan_button = ttk.Button(buttons_frame, text="🔍 Сканировать (F5)", 
                                     command=self.start_scan)
        self.scan_button.grid(row=0, column=0, padx=(0, 10))
        
        ttk.Button(buttons_frame, text="💾 Сохранить (Ctrl+S)", 
                  command=self.save_results).grid(row=0, column=1, padx=(0, 10))
        
        ttk.Button(buttons_frame, text="⚡ JSON (Ctrl+Q)", 
                  command=self.quick_save).grid(row=0, column=2, padx=(0, 10))
        
        ttk.Button(buttons_frame, text="🔍 Поиск (F3)", 
                  command=self.show_search_dialog).grid(row=0, column=3, padx=(0, 10))
        
        ttk.Button(buttons_frame, text="🗑️ Очистить", 
                  command=self.clear_results).grid(row=0, column=4, padx=(0, 10))
        
        ttk.Button(buttons_frame, text="❓ Справка (F1)", 
                  command=self.show_help).grid(row=0, column=5)
        
        # Прогресс-бар с процентами
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        self.progress_var = tk.StringVar(value="Готов к сканированию")
        progress_label = ttk.Label(progress_frame, textvariable=self.progress_var)
        progress_label.grid(row=1, column=0)
        
        # Результаты
        results_frame = ttk.LabelFrame(main_frame, text="Результаты", padding="5")
        results_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(1, weight=1)
        
        # Статистика
        self.stats_var = tk.StringVar(value="Статистика появится после сканирования")
        stats_label = ttk.Label(results_frame, textvariable=self.stats_var, font=('Arial', 10, 'bold'))
        stats_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        # Таблица результатов с сортировкой
        columns = ('name', 'path', 'size', 'extension', 'modified')
        self.tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=15)
        
        # Настройка колонок с сортировкой
        self.tree.heading('name', text='Имя файла ▲▼', command=lambda: self.sort_column('name'))
        self.tree.heading('path', text='Путь ▲▼', command=lambda: self.sort_column('path'))
        self.tree.heading('size', text='Размер (MB) ▲▼', command=lambda: self.sort_column('size'))
        self.tree.heading('extension', text='Расширение ▲▼', command=lambda: self.sort_column('extension'))
        self.tree.heading('modified', text='Изменен ▲▼', command=lambda: self.sort_column('modified'))
        
        self.tree.column('name', width=200)
        self.tree.column('path', width=300)
        self.tree.column('size', width=100)
        self.tree.column('extension', width=100)
        self.tree.column('modified', width=150)
        
        # Переменные для сортировки
        self.sort_column_name = None
        self.sort_reverse = False
        
        # Скроллбары
        v_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(results_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Размещение таблицы и скроллбаров
        self.tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
        # Контекстное меню
        self.create_context_menu()
    
    def sort_column(self, column):
        """Сортировка колонки"""
        if self.sort_column_name == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_reverse = False
            self.sort_column_name = column
        
        # Получаем данные для сортировки
        data = []
        for child in self.tree.get_children():
            values = self.tree.item(child)['values']
            data.append((child, values))
        
        # Определяем функцию сортировки
        if column == 'name':
            data.sort(key=lambda x: x[1][0].lower(), reverse=self.sort_reverse)
        elif column == 'path':
            data.sort(key=lambda x: x[1][1].lower(), reverse=self.sort_reverse)
        elif column == 'size':
            data.sort(key=lambda x: float(x[1][2]) if x[1][2] else 0, reverse=self.sort_reverse)
        elif column == 'extension':
            data.sort(key=lambda x: x[1][3].lower(), reverse=self.sort_reverse)
        elif column == 'modified':
            data.sort(key=lambda x: x[1][4], reverse=self.sort_reverse)
        
        # Переупорядочиваем элементы
        for index, (child, values) in enumerate(data):
            self.tree.move(child, '', index)
        
        # Обновляем заголовки
        self.update_column_headers()
    
    def update_column_headers(self):
        """Обновить заголовки колонок с индикаторами сортировки"""
        headers = {
            'name': 'Имя файла',
            'path': 'Путь', 
            'size': 'Размер (MB)',
            'extension': 'Расширение',
            'modified': 'Изменен'
        }
        
        for col in headers:
            if col == self.sort_column_name:
                arrow = ' ▼' if self.sort_reverse else ' ▲'
                self.tree.heading(col, text=headers[col] + arrow)
            else:
                self.tree.heading(col, text=headers[col] + ' ▲▼')
    
    def show_search_dialog(self):
        """Показать диалог поиска"""
        if not self.files_data:
            messagebox.showinfo("Информация", "Сначала выполните сканирование")
            return
        
        search_window = tk.Toplevel(self.root)
        search_window.title("🔍 Поиск файлов")
        search_window.geometry("400x150")
        search_window.transient(self.root)
        search_window.grab_set()
        
        # Центрируем окно
        search_window.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (400 // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (150 // 2)
        search_window.geometry(f"400x150+{x}+{y}")
        
        ttk.Label(search_window, text="Поиск в именах файлов:", font=('Arial', 12)).pack(pady=10)
        
        search_var = tk.StringVar()
        search_entry = ttk.Entry(search_window, textvariable=search_var, width=40)
        search_entry.pack(pady=5)
        search_entry.focus()
        
        def perform_search():
            query = search_var.get().lower()
            if not query:
                return
            
            # Очищаем текущие результаты
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Фильтруем и показываем только найденные файлы
            found_count = 0
            for file_info in self.files_data:
                if query in file_info['name'].lower():
                    self.tree.insert('', 'end', values=(
                        file_info['name'],
                        file_info['full_path'],
                        file_info['size_mb'],
                        file_info['extension'],
                        file_info['modified_date']
                    ))
                    found_count += 1
            
            self.stats_var.set(f"Найдено: {found_count} файлов по запросу '{query}'")
            search_window.destroy()
        
        def reset_search():
            search_window.destroy()
            self.update_results()
        
        buttons_frame = ttk.Frame(search_window)
        buttons_frame.pack(pady=20)
        
        ttk.Button(buttons_frame, text="Найти", command=perform_search).pack(side=tk.LEFT, padx=10)
        ttk.Button(buttons_frame, text="Сбросить", command=reset_search).pack(side=tk.LEFT, padx=10)
        ttk.Button(buttons_frame, text="Отмена", command=search_window.destroy).pack(side=tk.LEFT, padx=10)
        
        # Enter для поиска
        search_entry.bind('<Return>', lambda e: perform_search())
    
    def show_filter_dialog(self):
        """Показать диалог фильтрации"""
        if not self.files_data:
            messagebox.showinfo("Информация", "Сначала выполните сканирование")
            return
        
        filter_window = tk.Toplevel(self.root)
        filter_window.title("🔧 Фильтрация файлов")
        filter_window.geometry("400x200")
        filter_window.transient(self.root)
        filter_window.grab_set()
        
        # Центрируем окно
        filter_window.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (400 // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (200 // 2)
        filter_window.geometry(f"400x200+{x}+{y}")
        
        ttk.Label(filter_window, text="Фильтр по размеру файла:", font=('Arial', 12)).pack(pady=10)
        
        size_frame = ttk.Frame(filter_window)
        size_frame.pack(pady=5)
        
        ttk.Label(size_frame, text="Размер больше:").pack(side=tk.LEFT)
        size_var = tk.StringVar(value="0")
        size_entry = ttk.Entry(size_frame, textvariable=size_var, width=10)
        size_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(size_frame, text="MB").pack(side=tk.LEFT)
        
        ttk.Label(filter_window, text="Фильтр по расширению:", font=('Arial', 12)).pack(pady=(20, 5))
        
        ext_var = tk.StringVar()
        ext_entry = ttk.Entry(filter_window, textvariable=ext_var, width=20)
        ext_entry.pack(pady=5)
        
        def apply_filter():
            try:
                min_size = float(size_var.get())
            except ValueError:
                min_size = 0
            
            ext_filter = ext_var.get().lower().strip()
            
            # Очищаем текущие результаты
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Применяем фильтры
            found_count = 0
            for file_info in self.files_data:
                if file_info['size_mb'] >= min_size:
                    if not ext_filter or file_info['extension'].lower() == ext_filter:
                        self.tree.insert('', 'end', values=(
                            file_info['name'],
                            file_info['full_path'],
                            file_info['size_mb'],
                            file_info['extension'],
                            file_info['modified_date']
                        ))
                        found_count += 1
            
            filter_desc = f"размер ≥ {min_size}MB"
            if ext_filter:
                filter_desc += f", расширение: {ext_filter}"
            
            self.stats_var.set(f"Отфильтровано: {found_count} файлов ({filter_desc})")
            filter_window.destroy()
        
        def reset_filter():
            filter_window.destroy()
            self.update_results()
        
        buttons_frame = ttk.Frame(filter_window)
        buttons_frame.pack(pady=20)
        
        ttk.Button(buttons_frame, text="Применить", command=apply_filter).pack(side=tk.LEFT, padx=10)
        ttk.Button(buttons_frame, text="Сбросить", command=reset_filter).pack(side=tk.LEFT, padx=10)
        ttk.Button(buttons_frame, text="Отмена", command=filter_window.destroy).pack(side=tk.LEFT, padx=10)
    
    def quick_save(self, format_type='json'):
        """Быстрое сохранение на рабочий стол"""
        if not self.files_data:
            messagebox.showwarning("Внимание", "Нет данных для сохранения!")
            return
        
        try:
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            if not os.path.exists(desktop):
                # Если Desktop не существует, сохраняем в домашнюю папку
                desktop = os.path.expanduser("~")
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"files_scan_{timestamp}.{format_type}"
            file_path = os.path.join(desktop, filename)
            
            if format_type == 'txt':
                self.save_to_txt(file_path)
            elif format_type == 'csv':
                self.save_to_csv(file_path)
            elif format_type == 'json':
                self.save_to_json(file_path)
            
            messagebox.showinfo("Быстрое сохранение", f"Файл сохранен:\n{filename}\n\nРасположение: {desktop}")
            return file_path
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при быстром сохранении: {e}")
            return None
    
    def create_context_menu(self):
        """Создание контекстного меню"""
        self.context_menu = Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Копировать путь", command=self.copy_path)
        self.context_menu.add_command(label="Открыть папку", command=self.open_folder)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Показать свойства", command=self.show_properties)
        
        self.tree.bind("<Button-3>", self.show_context_menu)  # Правая кнопка мыши
    
    def show_context_menu(self, event):
        """Показать контекстное меню"""
        item = self.tree.selection()[0] if self.tree.selection() else None
        if item:
            self.context_menu.post(event.x_root, event.y_root)
    
    def copy_path(self):
        """Копировать путь к файлу"""
        item = self.tree.selection()[0] if self.tree.selection() else None
        if item:
            path = self.tree.item(item)['values'][1]  # путь - второй элемент
            self.root.clipboard_clear()
            self.root.clipboard_append(path)
            messagebox.showinfo("Скопировано", f"Путь скопирован в буфер обмена:\n{path}")
    
    def open_folder(self):
        """Открыть папку с файлом"""
        item = self.tree.selection()[0] if self.tree.selection() else None
        if item:
            path = self.tree.item(item)['values'][1]
            folder = os.path.dirname(path)
            try:
                if os.name == 'nt':  # Windows
                    os.startfile(folder)
                elif os.name == 'posix':  # macOS and Linux
                    import subprocess
                    if hasattr(os, 'uname') and os.uname().sysname == 'Darwin':  # macOS
                        subprocess.run(['open', folder])
                    else:  # Linux
                        subprocess.run(['xdg-open', folder])
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось открыть папку: {e}")
    
    def show_properties(self):
        """Показать свойства файла"""
        item = self.tree.selection()[0] if self.tree.selection() else None
        if item:
            values = self.tree.item(item)['values']
            name, path, size, ext, modified = values
            
            # Найти полную информацию о файле
            file_info = None
            for f in self.files_data:
                if f['full_path'] == path:
                    file_info = f
                    break
            
            if file_info:
                props_text = f"""Свойства файла:

Имя: {file_info['name']}
Полный путь: {file_info['full_path']}
Размер: {file_info['size_mb']} MB ({file_info['size_bytes']} байт)
Расширение: {file_info['extension']}
Создан: {file_info['created_date']}
Изменен: {file_info['modified_date']}
Папка: {file_info['directory']}"""
                
                messagebox.showinfo("Свойства файла", props_text)
    
    def browse_folder(self):
        """Выбор папки"""
        folder = filedialog.askdirectory(title="Выберите папку для сканирования")
        if folder:
            self.folder_var.set(folder)
    
    def start_scan(self):
        """Запуск сканирования в отдельном потоке"""
        folder = self.folder_var.get().strip()
        if not folder:
            messagebox.showwarning("Внимание", "Выберите папку для сканирования!")
            return
        
        if not os.path.exists(folder):
            messagebox.showerror("Ошибка", "Выбранная папка не существует!")
            return
        
        if self.scanning:
            messagebox.showinfo("Информация", "Сканирование уже выполняется!")
            return
        
        # Запуск в отдельном потоке
        thread = threading.Thread(target=self.scan_files, args=(folder,))
        thread.daemon = True
        thread.start()
    
    def scan_files(self, directory):
        """Сканирование файлов с прогрессом"""
        self.scanning = True
        self.scan_button.config(state='disabled')
        self.progress.config(mode='indeterminate')
        self.progress.start()
        self.progress_var.set("Подсчет файлов...")
        
        try:
            self.files_data = []
            
            # Получение настроек
            include_hidden = self.include_hidden.get()
            extensions_text = self.extensions_var.get().strip()
            file_extensions = None
            
            if extensions_text:
                file_extensions = [ext.strip().lower() for ext in extensions_text.split() if ext.strip()]
            
            # Первый проход - подсчет файлов для прогресса
            self.total_files_to_scan = 0
            for root, dirs, files in os.walk(directory):
                if not include_hidden:
                    dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                for file in files:
                    if not include_hidden and file.startswith('.'):
                        continue
                    
                    file_ext = os.path.splitext(file)[1].lower()
                    if file_extensions and file_ext not in file_extensions:
                        continue
                    
                    self.total_files_to_scan += 1
            
            # Переключаемся на детерминированный прогресс
            self.progress.stop()
            self.progress.config(mode='determinate', maximum=self.total_files_to_scan)
            self.scan_progress = 0
            
            # Второй проход - само сканирование
            for root, dirs, files in os.walk(directory):
                # Исключаем скрытые папки, если нужно
                if not include_hidden:
                    dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                for file in files:
                    if not include_hidden and file.startswith('.'):
                        continue
                    
                    file_path = os.path.join(root, file)
                    file_ext = os.path.splitext(file)[1].lower()
                    
                    # Фильтруем по расширениям
                    if file_extensions and file_ext not in file_extensions:
                        continue
                    
                    try:
                        stat = os.stat(file_path)
                        file_info = {
                            'name': file,
                            'full_path': file_path,
                            'relative_path': os.path.relpath(file_path, directory),
                            'directory': root,
                            'extension': file_ext or 'нет',
                            'size_bytes': stat.st_size,
                            'size_mb': round(stat.st_size / (1024 * 1024), 3),
                            'modified_date': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                            'created_date': datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
                        }
                        self.files_data.append(file_info)
                        
                        # Обновляем прогресс
                        self.scan_progress += 1
                        progress_percent = (self.scan_progress / self.total_files_to_scan) * 100
                        self.root.after(0, self.update_progress, self.scan_progress, progress_percent)
                        
                    except (PermissionError, OSError):
                        continue
            
            # Обновление интерфейса в главном потоке
            self.root.after(0, self.update_results)
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Ошибка", f"Ошибка при сканировании: {e}"))
        finally:
            self.scanning = False
            self.root.after(0, self.scan_complete)
    
    def update_progress(self, current, percent):
        """Обновление прогресса"""
        self.progress['value'] = current
        self.progress_var.set(f"Сканирование... {current}/{self.total_files_to_scan} ({percent:.1f}%)")
    
    def scan_complete(self):
        """Завершение сканирования"""
        self.progress.stop()
        self.progress['value'] = self.total_files_to_scan
        self.scan_button.config(state='normal')
        self.progress_var.set(f"Сканирование завершено: {len(self.files_data)} файлов")
    
    def update_results(self):
        """Обновление результатов в интерфейсе"""
        # Очистка предыдущих результатов
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Добавление новых результатов с цветовой индикацией
        for file_info in self.files_data:
            item = self.tree.insert('', 'end', values=(
                file_info['name'],
                file_info['full_path'],
                file_info['size_mb'],
                file_info['extension'],
                file_info['modified_date']
            ))
            
            # Цветовая индикация по размеру
            if file_info['size_mb'] > 100:  # Большие файлы - красный
                self.tree.set(item, 'size', f"{file_info['size_mb']} 🔴")
            elif file_info['size_mb'] > 10:  # Средние файлы - желтый
                self.tree.set(item, 'size', f"{file_info['size_mb']} 🟡")
            else:  # Маленькие файлы - зеленый
                self.tree.set(item, 'size', f"{file_info['size_mb']} 🟢")
        
        # Обновление статистики
        self.update_statistics()
    
    def update_statistics(self):
        """Обновление статистики"""
        if not self.files_data:
            self.stats_var.set("Файлы не найдены")
            return
        
        total_files = len(self.files_data)
        total_size_mb = sum(f['size_mb'] for f in self.files_data)
        total_size_gb = total_size_mb / 1024
        
        # Статистика по расширениям
        extensions = {}
        for file_info in self.files_data:
            ext = file_info['extension']
            extensions[ext] = extensions.get(ext, 0) + 1
        
        # Топ-5 расширений
        top_extensions = sorted(extensions.items(), key=lambda x: x[1], reverse=True)[:5]
        ext_text = ", ".join([f"{ext}: {count}" for ext, count in top_extensions])
        
        if total_size_gb > 1:
            size_text = f"{total_size_gb:.2f} GB"
        else:
            size_text = f"{total_size_mb:.2f} MB"
        
        stats_text = f"📁 Файлов: {total_files} | 💾 Размер: {size_text} | 🏆 Топ: {ext_text}"
        self.stats_var.set(stats_text)
    
    def save_results(self):
        """Сохранение результатов"""
        if not self.files_data:
            messagebox.showwarning("Внимание", "Нет данных для сохранения!")
            return
        
        # Диалог выбора формата
        save_window = tk.Toplevel(self.root)
        save_window.title("💾 Сохранение результатов")
        save_window.geometry("350x250")
        save_window.transient(self.root)
        save_window.grab_set()
        
        # Центрируем окно
        save_window.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (350 // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (250 // 2)
        save_window.geometry(f"350x250+{x}+{y}")
        
        ttk.Label(save_window, text="Выберите формат файла:", font=('Arial', 12)).pack(pady=20)
        
        format_var = tk.StringVar(value="json")
        
        ttk.Radiobutton(save_window, text="📄 Текстовый файл (.txt)", 
                       variable=format_var, value="txt").pack(anchor=tk.W, padx=50, pady=5)
        ttk.Radiobutton(save_window, text="📊 CSV файл (.csv)", 
                       variable=format_var, value="csv").pack(anchor=tk.W, padx=50, pady=5)
        ttk.Radiobutton(save_window, text="🗂️ JSON файл (.json)", 
                       variable=format_var, value="json").pack(anchor=tk.W, padx=50, pady=5)
        
        buttons_frame = ttk.Frame(save_window)
        buttons_frame.pack(pady=20)
        
        def do_save():
            format_type = format_var.get()
            save_window.destroy()
            self.save_file(format_type)
        
        def do_quick_save():
            format_type = format_var.get()
            save_window.destroy()
            self.quick_save(format_type)
        
        ttk.Button(buttons_frame, text="💾 Сохранить как...", command=do_save).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="⚡ Быстро", command=do_quick_save).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="❌ Отмена", command=save_window.destroy).pack(side=tk.LEFT, padx=5)
    
    def save_file(self, format_type):
        """Сохранение файла в выбранном формате"""
        if not self.files_data:
            messagebox.showwarning("Внимание", "Нет данных для сохранения!")
            return
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"files_scan_{timestamp}.{format_type}"
        
        try:
            # Поднимаем главное окно на передний план
            self.root.lift()
            self.root.focus_force()
            
            # Определяем типы файлов для диалога
            if format_type == 'txt':
                filetypes = [("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
            elif format_type == 'csv':
                filetypes = [("CSV файлы", "*.csv"), ("Все файлы", "*.*")]
            elif format_type == 'json':
                filetypes = [("JSON файлы", "*.json"), ("Все файлы", "*.*")]
            else:
                filetypes = [("Все файлы", "*.*")]
            
            file_path = filedialog.asksaveasfilename(
                title=f"Сохранить как {format_type.upper()}",
                defaultextension=f".{format_type}",
                filetypes=filetypes,
                initialname=filename
            )
            
            if not file_path:
                return
            
            # Сохраняем файл
            if format_type == 'txt':
                self.save_to_txt(file_path)
            elif format_type == 'csv':
                self.save_to_csv(file_path)
            elif format_type == 'json':
                self.save_to_json(file_path)
            
            messagebox.showinfo("Успех", f"Файл сохранен:\n{file_path}")
            
            # Предлагаем открыть папку с файлом
            if messagebox.askyesno("Открыть папку?", "Открыть папку с сохраненным файлом?"):
                self.open_file_location(file_path)
        
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении: {e}")
    
    def open_file_location(self, file_path):
        """Открыть папку с файлом"""
        try:
            folder = os.path.dirname(file_path)
            if os.name == 'nt':  # Windows
                os.startfile(folder)
            elif os.name == 'posix':  # macOS and Linux
                import subprocess
                if hasattr(os, 'uname') and os.uname().sysname == 'Darwin':  # macOS
                    subprocess.run(['open', folder])
                else:  # Linux
                    subprocess.run(['xdg-open', folder])
        except Exception as e:
            print(f"Couldn't open folder: {e}")
    
    def save_to_txt(self, filename):
        """Сохранение в текстовый файл"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("🗂️ ОТЧЕТ О СКАНИРОВАНИИ ФАЙЛОВ\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"📅 Дата сканирования: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"📁 Сканированная папка: {self.folder_var.get()}\n")
            f.write(f"📊 Всего найдено файлов: {len(self.files_data)}\n")
            total_size = sum(f['size_mb'] for f in self.files_data)
            f.write(f"💾 Общий размер: {total_size:.2f} MB ({total_size/1024:.2f} GB)\n\n")
            
            # Статистика по расширениям
            extensions = {}
            for file_info in self.files_data:
                ext = file_info['extension']
                extensions[ext] = extensions.get(ext, 0) + 1
            
            f.write("📈 СТАТИСТИКА ПО РАСШИРЕНИЯМ:\n")
            f.write("-" * 30 + "\n")
            for ext, count in sorted(extensions.items(), key=lambda x: x[1], reverse=True):
                f.write(f"{ext}: {count} файлов\n")
            
            f.write("\n📋 СПИСОК ФАЙЛОВ:\n")
            f.write("-" * 30 + "\n")
            for file_info in sorted(self.files_data, key=lambda x: x['size_mb'], reverse=True):
                size_indicator = "🔴" if file_info['size_mb'] > 100 else "🟡" if file_info['size_mb'] > 10 else "🟢"
                f.write(f"{size_indicator} {file_info['full_path']} ({file_info['size_mb']} MB)\n")
    
    def save_to_csv(self, filename):
        """Сохранение в CSV файл"""
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'name', 'full_path', 'relative_path', 'directory', 
                'extension', 'size_bytes', 'size_mb', 'modified_date', 'created_date'
            ])
            writer.writeheader()
            writer.writerows(self.files_data)
    
    def save_to_json(self, filename):
        """Сохранение в JSON файл"""
        # Статистика
        extensions = {}
        for file_info in self.files_data:
            ext = file_info['extension']
            extensions[ext] = extensions.get(ext, 0) + 1
        
        total_size_mb = sum(f['size_mb'] for f in self.files_data)
        
        data = {
            'scan_info': {
                'version': '2.1',
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'scanned_folder': self.folder_var.get(),
                'total_files': len(self.files_data),
                'total_size_mb': round(total_size_mb, 2),
                'total_size_gb': round(total_size_mb / 1024, 2),
                'extensions_stats': extensions,
                'largest_files': sorted(self.files_data, key=lambda x: x['size_mb'], reverse=True)[:10]
            },
            'files': self.files_data
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def clear_results(self):
        """Очистка результатов"""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Очистка данных
        self.files_data = []
        
        # Сброс статистики и прогресса
        self.stats_var.set("Готов к сканированию")
        self.progress_var.set("Готов к сканированию")
        self.progress['value'] = 0
        self.scan_progress = 0
        self.total_files_to_scan = 0
    
    def show_help(self):
        """Показать справку"""
        help_text = """
🗂️ СКАНЕР ФАЙЛОВ v2.1 - СПРАВКА

✨ НОВЫЕ ВОЗМОЖНОСТИ:
• Сортировка колонок (клик по заголовку)
• Цветовая индикация размеров файлов
• Темная/светлая тема (🌙 или Ctrl+T)
• Прогресс сканирования в процентах
• Быстрое сохранение на рабочий стол

🎯 ОСНОВНЫЕ ВОЗМОЖНОСТИ:
• Сканирование папок и всех подпапок
• Детальная информация о файлах
• Фильтрация по расширениям и размеру
• Поиск по именам файлов
• Статистика по типам файлов
• Экспорт в TXT, CSV, JSON

🔧 КАК ИСПОЛЬЗОВАТЬ:
1. Выберите папку для сканирования
2. Настройте опции (по желанию)
3. Нажмите "Сканировать" (F5)
4. Используйте поиск (F3) и фильтры (Ctrl+F)
5. Сохраните отчет (Ctrl+S или Ctrl+Q)

🎨 ЦВЕТОВЫЕ ИНДИКАТОРЫ:
🔴 Большие файлы (>100 MB)
🟡 Средние файлы (10-100 MB)  
🟢 Маленькие файлы (<10 MB)

⌨️ ГОРЯЧИЕ КЛАВИШИ:
F5 - Сканировать
F3 - Поиск файлов
F1 - Справка
Ctrl+S - Сохранить как...
Ctrl+Q - Быстрое сохранение
Ctrl+F - Фильтрация
Ctrl+T - Переключить тему
Del - Очистить результаты

👆 КОНТЕКСТНОЕ МЕНЮ:
ПКМ по файлу → Копировать путь, Открыть папку, Свойства

📁 ФИЛЬТРЫ:
• Расширения: .txt .py .jpg .doc
• Размер: файлы больше X MB
• Поиск: по имени файла

💾 СОХРАНЕНИЕ:
• Сохранить (Ctrl+S): выбор формата TXT/CSV/JSON
• Быстро JSON (Ctrl+Q): мгновенное сохранение в JSON
• Все файлы сохраняются рядом со скриптом
• Формат имени: "Название папки - Анализ - дата-время.расширение"

🎨 ТЕМЫ:
• Светлая тема (по умолчанию)
• Темная тема (кнопка 🌙)

АВТОР: File Scanner v2.1 Enhanced
"""
        
        messagebox.showinfo("Справка", help_text)

def main():
    root = tk.Tk()
    app = FileScannerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()