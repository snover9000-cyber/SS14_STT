@echo off
chcp 65001 > nul
echo [STT] Идёт установка библиотек... 
pip install faster-whisper pyperclip keyboard sounddevice numpy
echo [STT] Установка успешно завершена!
pause
