#!/bin/bash

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "========================================"
echo "   🗂️ СКАНЕР ФАЙЛОВ v2.0"
echo "========================================"
echo -e "${NC}"

echo -e "${YELLOW}Запуск приложения...${NC}"
echo

# Проверяем наличие Python
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo -e "${RED}❌ Python не найден!${NC}"
    echo
    echo "Пожалуйста, установите Python:"
    echo "Ubuntu/Debian: sudo apt install python3 python3-tk"
    echo "CentOS/RHEL: sudo yum install python3 python3-tkinter"
    echo "macOS: brew install python-tk"
    echo
    exit 1
fi

# Определяем команду Python
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python"
fi

# Проверяем наличие tkinter
$PYTHON_CMD -c "import tkinter" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Модуль tkinter не найден!${NC}"
    echo
    echo "Установите tkinter:"
    echo "Ubuntu/Debian: sudo apt install python3-tk"
    echo "CentOS/RHEL: sudo yum install python3-tkinter"
    echo "macOS: модуль должен быть включен по умолчанию"
    echo
    exit 1
fi

# Запуск сканера
$PYTHON_CMD file_scanner_gui.py

# Проверяем код выхода
if [ $? -ne 0 ]; then
    echo
    echo -e "${RED}❌ Произошла ошибка при запуске!${NC}"
    echo
    read -p "Нажмите Enter для выхода..."
fi
