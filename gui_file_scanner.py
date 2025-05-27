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
        self.root.title("Сканер файлов v2.0")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Данные
        self.files_data = []
        self.scanning = False
        
        # Настройка стиля
        self.setup_styles()
        
        # Создание интерфейса
        self.create_widgets()
        
        # Центрируем окно
        self.center_window()
    
    def setup_styles(self):
        """Настройка стилей для красивого интерфейса"""
        style = ttk.Style()
        
        # Используем современную тему
        available_themes = style.theme_names()
        if 'clam' in available_themes:
            style.theme_use('clam')
        elif 'alt' in available_themes:
            style.theme_use('alt')
    
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
        main_frame.rowconfigure(4, weight=1)
        
        # Заголовок
        title_label = ttk.Label(main_frame, text="🗂️ Сканер файлов", font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
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
        
        self.scan_button = ttk.Button(buttons_frame, text="🔍 Сканировать", 
                                     command=self.start_scan, style='Accent.TButton')
        self.scan_button.grid(row=0, column=0, padx=(0, 10))
        
        ttk.Button(buttons_frame, text="💾 Сохранить", 
                  command=self.save_results).grid(row=0, column=1, padx=(0, 10))
        
        ttk.Button(buttons_frame, text="🗑️ Очистить", 
                  command=self.clear_results).grid(row=0, column=2, padx=(0, 10))
        
        ttk.Button(buttons_frame, text="❓ Справка", 
                  command=self.show_help).grid(row=0, column=3)
        
        # Прогресс-бар
        self.progress_var = tk.StringVar(value="Готов к сканированию")
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 5))
        
        progress_label = ttk.Label(main_frame, textvariable=self.progress_var)
        progress_label.grid(row=5, column=0, columnspan=3, pady=(0, 10))
        
        # Результаты
        results_frame = ttk.LabelFrame(main_frame, text="Результаты", padding="5")
        results_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(1, weight=1)
        
        # Статистика
        self.stats_var = tk.StringVar(value="Статистика появится после сканирования")
        stats_label = ttk.Label(results_frame, textvariable=self.stats_var, font=('Arial', 10, 'bold'))
        stats_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        # Таблица результатов
        columns = ('name', 'path', 'size', 'extension', 'modified')
        self.tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=15)
        
        # Настройка колонок
        self.tree.heading('name', text='Имя файла')
        self.tree.heading('path', text='Путь')
        self.tree.heading('size', text='Размер (MB)')
        self.tree.heading('extension', text='Расширение')
        self.tree.heading('modified', text='Изменен')
        
        self.tree.column('name', width=200)
        self.tree.column('path', width=300)
        self.tree.column('size', width=100)
        self.tree.column('extension', width=100)
        self.tree.column('modified', width=150)
        
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
                    os.system(f'open "{folder}"' if sys.platform == 'darwin' else f'xdg-open "{folder}"')
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
        """Сканирование файлов"""
        self.scanning = True
        self.scan_button.config(state='disabled')
        self.progress.start()
        self.progress_var.set("Сканирование...")
        
        try:
            self.files_data = []
            
            # Получение настроек
            include_hidden = self.include_hidden.get()
            extensions_text = self.extensions_var.get().strip()
            file_extensions = None
            
            if extensions_text:
                file_extensions = [ext.strip().lower() for ext in extensions_text.split() if ext.strip()]
            
            # Сканирование
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
                    except (PermissionError, OSError):
                        continue
            
            # Обновление интерфейса в главном потоке
            self.root.after(0, self.update_results)
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Ошибка", f"Ошибка при сканировании: {e}"))
        finally:
            self.scanning = False
            self.root.after(0, self.scan_complete)
    
    def scan_complete(self):
        """Завершение сканирования"""
        self.progress.stop()
        self.scan_button.config(state='normal')
        self.progress_var.set("Сканирование завершено")
    
    def update_results(self):
        """Обновление результатов в интерфейсе"""
        # Очистка предыдущих результатов
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Добавление новых результатов
        for file_info in self.files_data:
            self.tree.insert('', 'end', values=(
                file_info['name'],
                file_info['full_path'],
                file_info['size_mb'],
                file_info['extension'],
                file_info['modified_date']
            ))
        
        # Обновление статистики
        self.update_statistics()
    
    def update_statistics(self):
        """Обновление статистики"""
        if not self.files_data:
            self.stats_var.set("Файлы не найдены")
            return
        
        total_files = len(self.files_data)
        total_size_mb = sum(f['size_mb'] for f in self.files_data)
        
        # Статистика по расширениям
        extensions = {}
        for file_info in self.files_data:
            ext = file_info['extension']
            extensions[ext] = extensions.get(ext, 0) + 1
        
        # Топ-5 расширений
        top_extensions = sorted(extensions.items(), key=lambda x: x[1], reverse=True)[:5]
        ext_text = ", ".join([f"{ext}: {count}" for ext, count in top_extensions])
        
        stats_text = f"Найдено файлов: {total_files} | Общий размер: {total_size_mb:.2f} MB | Топ расширения: {ext_text}"
        self.stats_var.set(stats_text)
    
    def save_results(self):
        """Сохранение результатов"""
        if not self.files_data:
            messagebox.showwarning("Внимание", "Нет данных для сохранения!")
            return
        
        # Диалог выбора формата
        save_window = tk.Toplevel(self.root)
        save_window.title("Сохранение результатов")
        save_window.geometry("300x200")
        save_window.transient(self.root)
        save_window.grab_set()
        
        # Центрируем окно
        save_window.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (300 // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (200 // 2)
        save_window.geometry(f"300x200+{x}+{y}")
        
        ttk.Label(save_window, text="Выберите формат файла:", font=('Arial', 12)).pack(pady=20)
        
        format_var = tk.StringVar(value="txt")
        
        ttk.Radiobutton(save_window, text="Текстовый файл (.txt)", 
                       variable=format_var, value="txt").pack(anchor=tk.W, padx=50)
        ttk.Radiobutton(save_window, text="CSV файл (.csv)", 
                       variable=format_var, value="csv").pack(anchor=tk.W, padx=50)
        ttk.Radiobutton(save_window, text="JSON файл (.json)", 
                       variable=format_var, value="json").pack(anchor=tk.W, padx=50)
        
        buttons_frame = ttk.Frame(save_window)
        buttons_frame.pack(pady=20)
        
        def do_save():
            format_type = format_var.get()
            save_window.destroy()
            self.save_file(format_type)
        
        ttk.Button(buttons_frame, text="Сохранить", command=do_save).pack(side=tk.LEFT, padx=10)
        ttk.Button(buttons_frame, text="Отмена", command=save_window.destroy).pack(side=tk.LEFT)
    
    def save_file(self, format_type):
        """Сохранение файла в выбранном формате"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"files_scan_{timestamp}.{format_type}"
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=f".{format_type}",
            filetypes=[(f"{format_type.upper()} files", f"*.{format_type}"), ("All files", "*.*")],
            initialname=filename
        )
        
        if not file_path:
            return
        
        try:
            if format_type == 'txt':
                self.save_to_txt(file_path)
            elif format_type == 'csv':
                self.save_to_csv(file_path)
            elif format_type == 'json':
                self.save_to_json(file_path)
            
            messagebox.showinfo("Успех", f"Файл сохранен: {file_path}")
        
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении: {e}")
    
    def save_to_txt(self, filename):
        """Сохранение в текстовый файл"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("ОТЧЕТ О СКАНИРОВАНИИ ФАЙЛОВ\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Дата сканирования: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Сканированная папка: {self.folder_var.get()}\n")
            f.write(f"Всего найдено файлов: {len(self.files_data)}\n")
            f.write(f"Общий размер: {sum(f['size_mb'] for f in self.files_data):.2f} MB\n\n")
            
            # Статистика по расширениям
            extensions = {}
            for file_info in self.files_data:
                ext = file_info['extension']
                extensions[ext] = extensions.get(ext, 0) + 1
            
            f.write("СТАТИСТИКА ПО РАСШИРЕНИЯМ:\n")
            f.write("-" * 30 + "\n")
            for ext, count in sorted(extensions.items(), key=lambda x: x[1], reverse=True):
                f.write(f"{ext}: {count} файлов\n")
            
            f.write("\n" + "СПИСОК ФАЙЛОВ:\n")
            f.write("-" * 30 + "\n")
            for file_info in self.files_data:
                f.write(f"{file_info['full_path']} ({file_info['size_mb']} MB)\n")
    
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
        
        data = {
            'scan_info': {
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'scanned_folder': self.folder_var.get(),
                'total_files': len(self.files_data),
                'total_size_mb': round(sum(f['size_mb'] for f in self.files_data), 2),
                'extensions_stats': extensions
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
        
        # Сброс статистики
        self.stats_var.set("Готов к сканированию")
        self.progress_var.set("Готов к сканированию")
    
    def show_help(self):
        """Показать справку"""
        help_text = """
🗂️ СКАНЕР ФАЙЛОВ - СПРАВКА

ОСНОВНЫЕ ВОЗМОЖНОСТИ:
• Сканирование папок и всех подпапок
• Детальная информация о файлах
• Фильтрация по расширениям
• Статистика по типам файлов
• Экспорт в TXT, CSV, JSON

КАК ИСПОЛЬЗОВАТЬ:
1. Выберите папку для сканирования
2. Настройте опции (по желанию)
3. Нажмите "Сканировать"
4. Просмотрите результаты
5. Сохраните отчет (по желанию)

ФИЛЬТР РАСШИРЕНИЙ:
Введите расширения через пробел:
.txt .py .jpg .doc

КОНТЕКСТНОЕ МЕНЮ:
ПКМ по файлу → Копировать путь, Открыть папку

ГОРЯЧИЕ КЛАВИШИ:
F5 - Начать сканирование
Ctrl+S - Сохранить результаты
Del - Очистить результаты

АВТОР: File Scanner v2.0
"""
        
        messagebox.showinfo("Справка", help_text)

def main():
    root = tk.Tk()
    app = FileScannerGUI(root)
    
    # Горячие клавиши
    root.bind('<F5>', lambda e: app.start_scan())
    root.bind('<Control-s>', lambda e: app.save_results())
    root.bind('<Delete>', lambda e: app.clear_results())
    
    root.mainloop()

if __name__ == "__main__":
    main()