@echo off
chcp 65001 >nul
title Сканер файлов
echo.
echo ========================================
echo    🗂️ СКАНЕР ФАЙЛОВ v2.0
echo ========================================
echo.
echo Запуск приложения...
echo.

REM Проверяем наличие Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python не найден!
    echo.
    echo Пожалуйста, установите Python с https://python.org
    echo.
    pause
    exit /b 1
)

REM Запуск сканера
python file_scanner_gui.py

REM Если программа завершилась с ошибкой
if %errorlevel% neq 0 (
    echo.
    echo ❌ Произошла ошибка при запуске!
    echo.
    pause
)
