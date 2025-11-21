import re


def _clean_text_for_speech(text: str) -> str:
    """Очищает текст от символов, которые не должны озвучиваться"""

    # Убираем маркеры списков (*, -, •) в начале строк
    text = re.sub(r'^[\s]*[*\-•][\s]+', '', text, flags=re.MULTILINE)

    # Убираем маркеры списков в середине текста, но сохраняем математические *
    # Сложная логика: убираем * только если вокруг пробелы и это не похоже на умножение
    text = re.sub(r'(?<!\S)[*\-•](?!\S)', ' ', text)

    # Убираем лишние пробелы
    text = re.sub(r'\s+', ' ', text).strip()

    return text


def _clean_text_for_speech_keep_mathexpression(text: str) -> str:
    """Умная очистка текста для озвучки"""
    import re

    # Сохраняем математические выражения
    math_patterns = [
        r'\d+\s*\*\s*\d+',  # 2*2, 5 * 3
        r'\w+\s*\*\s*\w+',  # переменная*переменная
    ]

    # Временно заменяем математические выражения
    math_replacements = {}
    for i, pattern in enumerate(math_patterns):
        matches = re.finditer(pattern, text)
        for match in matches:
            placeholder = f"__MATH_{i}_{len(math_replacements)}__"
            math_replacements[placeholder] = match.group()
            text = text.replace(match.group(), placeholder)

    # Убираем маркеры форматирования
    text = re.sub(r'^[\s]*[*\-•][\s]+', '', text, flags=re.MULTILINE)  # списки
    text = re.sub(r'[*\-•](?=[\s,.!?])', '', text)  # маркеры перед пунктуацией
    text = re.sub(r'(?<=[\s])[*\-•](?=\s)', '', text)  # одиночные маркеры

    # Восстанавливаем математические выражения
    for placeholder, original in math_replacements.items():
        text = text.replace(placeholder, original)

    # Чистим пробелы
    text = re.sub(r'\s+', ' ', text).strip()

    return text


def _clean_text_for_speech_simple(text: str) -> str:
    """Простая очистка - убираем только маркеры списков"""
    import re

    # Убираем * - • в начале строк (маркеры списков)
    lines = text.split('\n')
    cleaned_lines = []

    for line in lines:
        # Убираем маркеры списков в начале строки
        cleaned_line = re.sub(r'^[\s]*[*\-•][\s]+', '', line)
        cleaned_lines.append(cleaned_line)

    return '\n'.join(cleaned_lines)

text="""Домашнюю лису следует кормить сбалансированно, включая в рацион как мясные, так и другие продукты. В меню могут быть:

* мясо (курица, индейка, говядина);
* субпродукты (сердце, печень);
* каши на воде;
* овощи и фрукты (морковь, кабачок, яблоко);
* кисломолочные продукты (творог, кефир).

Важно помнить, что у лис особые потребности в питательных веществах, поэтому перед составлением рациона лучше проконсультироваться с ветеринаром.
"""
# cleaned_text=_clean_text_for_speech(text)
# print(cleaned_text)