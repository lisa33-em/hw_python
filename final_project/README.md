# GigaVibeMiptCode

Консольный ИИ-ассистент для взаимодействия с LLM через OpenAI-совместимый API (Ollama).

- Чат с ИИ
- Контроль длины контекста
- Подстановка файлов
- Режим чанковой обрабоки файлов
- Streaming — вывод ответов по мере генерации

## Команды
`\q` - выход из программы
`/reset` - очистить историю и экран
`/file_chunk` - обработать файл по частям

## Структура

final_project/
├── src/
│  ├── __init__.py
│  ├── chunk_load.py
│  ├── config.py
│  ├── main.py
│  ├── file_handler.py
│  └── ollamaChat.py
│
├── tests/
|   ├── __init__.py
|   ├── test_chunk_load.py
│   ├── test_config.py
│   ├── test_file_handler.py
│   └── test_ollama_chat.py
│
├── README.md
├── chat.yaml
├── requirements.txt
└── ruff.toml

## Установка

1) Установить Ollama
Скачать можно с [ollama.com](https://ollama.com). Далее нужно запустить фоном.

Следующий шаг - скачать модель в терминале

```bash
ollama pull gemma3:270m
```

2) Установка зависимостей
``` bash
git clone <your-repo-url>
cd final_project

pip install -r final_project/requirements.txt
```

3) Создать config.yaml
```
api_host: http://localhost:11434/v1/
api_key: ollama
limit_message: 20
limit_chars: 5000
temperature: 0.7
system_prompt: "You are a helpful AI bot."
```

4) Запуск
```bash
ollama serve
python main.py
```