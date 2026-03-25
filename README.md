# Meeting Video Pipeline (local)

Локальный пайплайн для обработки записей встреч (`.webm`, включая Яндекс Телемост) с двумя режимами:
- встреча **с презентацией**: строится PPTX по смене слайда/сцены;
- встреча **без презентации**: строится один итоговый слайд.

## Что делает

На входе:
- видео `webm` / `mp4` / другой формат, который читает ffmpeg.

На выходе:
1. `video_subtitled.mp4` — H.264/AAC MP4 с "впаянными" субтитрами (hard subtitles).
2. `video_softsubs.mp4` — MP4 с отдельной текстовой дорожкой субтитров `mov_text` (если нужен совместимый soft-sub вариант).
3. `transcript.txt` — полная расшифровка с таймкодами и speaker labels.
4. `transcript.json` — слова, спикеры, сцены, субтитры и служебная метаинформация.
5. `slides.pptx` — презентация по сценам/слайдам.
6. `slides.pdf` — если установлен LibreOffice (`soffice`) и включён флаг `--export-pdf`.

## Стек

- `ffmpeg` — извлечение аудио, перекодирование, сборка MP4 и кадры.
- `faster-whisper` — локальная ASR на GPU.
- `pyannote.audio` (`community-1`) — локальная speaker diarization.
- `PySceneDetect` — детекция смены сцен/слайдов.
- `python-pptx` — сборка презентации.

## Рекомендуемая установка

### 1) Системные зависимости
Установи:
- `ffmpeg`
  - если хочешь аппаратное сжатие видео на NVIDIA GPU, используй сборку ffmpeg с поддержкой `h264_nvenc` / CUDA
- (опционально) `libreoffice` / `soffice` — если нужен PDF

### 2) Python
Рекомендую Python 3.11.

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate  # Windows PowerShell
```

### 3) PyTorch
Поставь `torch` под свою CUDA через официальный selector PyTorch.

### 4) Остальные пакеты
```bash
pip install -r requirements.txt
```

### 5) pyannote community-1
Для первого запуска:
- прими user conditions у `pyannote/speaker-diarization-community-1` на Hugging Face;
- создай `HF_TOKEN`.

```bash
export HF_TOKEN=hf_xxx
# Windows PowerShell:
# $env:HF_TOKEN="hf_xxx"
```

## Быстрый запуск

```bash
python meeting_pipeline.py \
  --input /path/to/meeting.webm \
  --output-dir /path/to/out \
  --hf-token "$HF_TOKEN" \
  --language ru \
  --presentation auto \
  --ffmpeg-video-encoder auto \
  --export-pdf
```

## Полезные флаги

- `--presentation auto|yes|no`
  - `auto`: попытка понять, есть ли презентация
  - `yes`: насильно строить по сценам
  - `no`: всегда один слайд
- `--model large-v3|distil-large-v3|turbo`
- `--ffmpeg-video-encoder auto|h264_nvenc|libx264`
  - `auto`: предпочитает `h264_nvenc`, если он доступен в текущей сборке ffmpeg
  - `h264_nvenc`: принудительно использовать NVIDIA NVENC для кодирования видео
  - `libx264`: принудительно использовать CPU-кодирование
- `--num-speakers N`
- `--min-speakers N`
- `--max-speakers N`
- `--scene-detector content|adaptive|hash`
- `--scene-threshold ...`
- `--min-scene-sec ...`
- `--subtitle-max-chars ...`
- `--subtitle-max-duration ...`
- `--start-from prepare|asr|diarize|align|scenes|slides|write|render`
  - позволяет продолжить пайплайн с нужного шага для отладки
  - для повторного запуска с середины сначала сохрани промежуточные файлы через `--keep-work-files`

## Примеры

### Просто разговор, один итоговый слайд
```bash
python meeting_pipeline.py   --input call.webm   --output-dir out_call   --hf-token "$HF_TOKEN"   --presentation no
```

### Презентация со сменой слайдов
```bash
python meeting_pipeline.py   --input demo.webm   --output-dir out_demo   --hf-token "$HF_TOKEN"   --presentation yes   --scene-detector content   --min-scene-sec 5
```

### Задать известное число спикеров
```bash
python meeting_pipeline.py   --input interview.webm   --output-dir out_interview   --hf-token "$HF_TOKEN"   --num-speakers 2
```

### Отладка: пересобрать только финальное видео
```bash
python meeting_pipeline.py \
  --input demo.webm \
  --output-dir out_demo \
  --start-from render \
  --keep-work-files
```

### Отладка: пересчитать сцены и все следующие шаги
```bash
python meeting_pipeline.py \
  --input demo.webm \
  --output-dir out_demo \
  --start-from scenes \
  --keep-work-files
```

## Замечания

- Автоопределение "есть ли презентация" — эвристика. Для сложных записей лучше руками переключать `--presentation yes/no`.
- Для подготовки `work.mp4` и финального hard-sub видео скрипт умеет использовать `h264_nvenc`. В режиме `auto` при недоступности NVENC он автоматически откатывается на `libx264`.
- Для запуска с середины пайплайна скрипт пишет `pipeline_state.json` в выходную директорию и читает его при `--start-from ...`.
- Если `ffmpeg` собран без `libass`, hard subtitles могут не собраться. Тогда используй `video_softsubs.mp4`.
- Для русского текста в PPTX специальных шрифтов этот скрипт не прикладывает; PowerPoint обычно подставит системный шрифт. Если нужен PDF с идеальным типографским контролем, проще конвертировать PPTX через LibreOffice.
