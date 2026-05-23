import os
import re
from typing import List, Tuple, Match

MAX_FILE_SIZE = 5 * 1024 * 1024
FILE_PATH_PATTERN = r'@::(.*?)::'


def replace_placeholders(text: str) -> str:
    def replacer(match: Match[str]) -> str:
        filepath = match.group(1).strip()
        try:
            content = _read_file(filepath)
            return f'\n>>> {filepath}\n{content}\n<<<'
        except Exception as e:
            return f'\n\n[Ошибка: {e}]\n'

    return re.sub(FILE_PATH_PATTERN, replacer, text)


def _read_file(filepath: str) -> str:
    if not os.path.exists(filepath):
        raise FileNotFoundError('Файл не найден по пути')

    size = os.path.getsize(filepath)
    if size > MAX_FILE_SIZE:
        raise ValueError('Файл превышает 5 МБ')

    with open(filepath, encoding='utf-8') as file:
        return file.read()


def split_by_paragraphs(file_content: str, paragraphs_per_chunk: int = 1) -> List[str]:
    paragraphs = [parag for parag in file_content.split('\n\n') if parag.strip()]

    if not paragraphs:
        return [file_content]

    chunks = []
    for i in range(0, len(paragraphs), paragraphs_per_chunk):
        chunk = '\n\n'.join(paragraphs[i : i + paragraphs_per_chunk])
        chunks.append(chunk)

    return chunks


def split_by_length(content: str, chunk_size: int = 150) -> List[str]:
    if len(content) <= chunk_size:
        return [content]

    chunks = []
    start = 0
    while start < len(content):
        end = min(start + chunk_size, len(content))

        if end < len(content):
            last_line = content.rfind('\n', start, end)
            if last_line > start:
                end = last_line + 1

        chunks.append(content[start:end].strip())
        start = end

    return [ch for ch in chunks if ch]


def parse_chunk_command(args: str) -> Tuple[str, int, bool]:
    confirm = '-y' in args
    args = args.replace('-y', '').strip()

    if 'paragraph=' in args:
        total_parts = args.split('paragraph=')[1].split()[0]
        value = int(total_parts) if total_parts.isdigit() else 1
        return ('paragraph', value, confirm)

    elif 'len=' in args:
        total_parts = args.split('len=')[1].split()[0]
        value = int(total_parts) if total_parts.isdigit() else 1
        return ('len', value, confirm)

    else:
        return ('paragraph', 1, confirm)
