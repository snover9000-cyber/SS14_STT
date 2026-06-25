import os
import time
import keyboard
import sounddevice as sd
import numpy as np
import pyperclip
from faster_whisper import WhisperModel

# ================= НАСТРОЙКИ =================
HOTKEY = 'f4'  
SAMPLE_RATE = 16000
WORDS_FILE = r"C:\Users\user\Desktop\ss14_words.txt"
CPU_THREADS = 6
# =============================================

if os.path.exists(WORDS_FILE):
    with open(WORDS_FILE, "r", encoding="utf-8") as f:
        user_words = f.read().strip()
        if user_words:
            default_prompt = user_words
            print("[ОК] Словарь успешно загружен!")
else:
    default_prompt = "Привет, инженер! Как там сингулярность? Бармен, налей попить."

print("Загрузка оптимизированной нейросети Faster-Whisper (small)...")
try:
    model = WhisperModel("small", device="cpu", compute_type="int8", cpu_threads=CPU_THREADS)
    print("\n[ОК] Нейросеть успешно загружена и готова!")
except Exception as e:
    print(f"\n[КРИТИЧЕСКАЯ ОШИБКА]: {e}")
    input()
    exit()

def record_audio():
    audio_data = []
    def callback(indata, frames, time_status, status):
        audio_data.append(indata.copy())
    
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, callback=callback):
        while keyboard.is_pressed(HOTKEY):
            time.sleep(0.02)
            
    if audio_data:
        audio_np = np.concatenate(audio_data, axis=0).flatten()
        return audio_np
    return None

def process_voice(audio_np):
    if audio_np is None:
        return
    try:
        smart_context = (
          "Привет! Как дела? Что это такое? Кто там? Вы это видели? Что произошло? "
            "Помогите! Синга улетела! Там ксено! Быстрее сюда! Бежим отсюда! "
            "Я хотел, я хотела, я сделал, я сделала, пришёл, пришла, понял, поняла. "
            "Да, нет, хорошо, окей, принял. "
            f"{default_prompt}"
        )
        
        segments, info = model.transcribe(
            audio_np, 
            language="ru", 
            initial_prompt=smart_context,
            beam_size=5,
            vad_filter=True,
            temperature=0.0,
            condition_on_previous_text=False
        )
        text = "".join([segment.text for segment in segments]).strip()
        
        if text and len(text) > 1:
            print(f"Распознано: {text}")
            
            old_clipboard = pyperclip.paste()
            pyperclip.copy(text)
            keyboard.send('ctrl+v')
            time.sleep(0.01)
            pyperclip.copy(old_clipboard)
            
    except Exception as e:
        print(f"Ошибка распознавания: {e}")

while True:
    keyboard.wait(HOTKEY)
    time.sleep(0.1)
    audio_bytes = record_audio()
    if audio_bytes is not None:
        process_voice(audio_bytes)
