import os
import time
import keyboard
import sounddevice as sd
import scipy.io.wavfile as wavfile
import numpy as np
import pyperclip
from faster_whisper import WhisperModel

# ================= НАСТРОЙКИ =================
HOTKEY = 'f4'  
FILE_NAME = "temp_voice.wav"
SAMPLE_RATE = 16000
WORDS_FILE = r"C:\Users\user\Desktop\ss14_words.txt"
# =============================================

if os.path.exists(WORDS_FILE):
    with open(WORDS_FILE, "r", encoding="utf-8") as f:
        user_words = f.read().strip()
        if user_words:
            default_prompt = user_words
            print("[ОК] Словарь успешно загружен!")
else:
    default_prompt = "Привет, инженер, сингулярность, бармен."

print("Загрузка нейросети Faster-Whisper (small)...")
try:
    model = WhisperModel("small", device="cpu", compute_type="float32")
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
        audio_np = np.concatenate(audio_data, axis=0)
        wavfile.write(FILE_NAME, SAMPLE_RATE, audio_np)
        return True
    return False

def process_voice():
    if not os.path.exists(FILE_NAME):
        return
    try:
        # Промтыч для ИИшки.
        smart_context = (
            "Я хотел, я хотела, я сделал, я сделала, пришёл, пришла. "
            "Привет! Как дела? Что там произошло? Синга улетела! Помогите, пожалуйста. "
            f"{default_prompt}"
        )
        
        segments, info = model.transcribe(
            FILE_NAME, 
            language="ru", 
            initial_prompt=smart_context,
            beam_size=5,
            vad_filter=True,
            temperature=0.0,
            condition_on_previous_text=True
        )
        text = "".join([segment.text for segment in segments]).strip()
        
        if text and len(text) > 1:
            print(f"Распознано: {text}")
            
            # Вставка через буфер обмена
            old_clipboard = pyperclip.paste()
            pyperclip.copy(text)
            keyboard.send('ctrl+v')
            time.sleep(0.05)
            pyperclip.copy(old_clipboard)
            
    except Exception as e:
        print(f"Ошибка распознавания: {e}")
    if os.path.exists(FILE_NAME):
        os.remove(FILE_NAME)

while True:
    keyboard.wait(HOTKEY)
    time.sleep(0.1)
    if record_audio():
        process_voice()