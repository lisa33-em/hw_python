from src.ollamaChat import OllamaBot
from src.file_handler import split_by_paragraphs, split_by_length
from typing import List


def process_file_in_chunks(
    bot: OllamaBot, filepath: str, prompt: str, chunk_method: str, chunk_value: int, confirm: bool
) -> bool:
    try:
        with open(filepath, encoding='utf-8') as file:
            file_content = file.read()
    except Exception:
        return False

    if not file_content.strip():
        return False

    chunks: List[str] = []
    if chunk_method == 'paragraph':
        chunks = split_by_paragraphs(file_content, chunk_value)
    else:
        chunks = split_by_length(file_content, chunk_value)

    for i, chunk in enumerate(chunks, 1):
        full_message = f'{prompt}: {chunk}'
        print(f'Чанк {i}/{len(chunks)}')

        try:
            response = bot.send_message_sync(full_message)
            print(response)

            if not confirm and i < len(chunks):
                input('Нажмите Enter для обработки следующего чанка')
                
        except Exception as e:
            print(f'Ошибка при обработке чанка {i}: {e}')
            return False

    return True
