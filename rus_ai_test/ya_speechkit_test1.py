import requests
from ai_api.api.get_bearer_token import create_iam_token


def find_ogg_page_boundaries(audio_data):
    """Находит границы OGG страниц в файле"""
    boundaries = []
    i = 0

    while i < len(audio_data) - 4:
        # Ищем заголовок OGG: 'OggS'
        if audio_data[i:i + 4] == b'OggS':
            boundaries.append(i)
            # Пропускаем текущую страницу
            try:
                segment_table_offset = i + 26
                number_of_segments = audio_data[segment_table_offset]
                segment_table_length = number_of_segments

                # Суммируем размеры сегментов
                total_segments_size = 0
                for seg in range(number_of_segments):
                    seg_size = audio_data[segment_table_offset + 1 + seg]
                    total_segments_size += seg_size

                page_size = 27 + number_of_segments + total_segments_size
                i += page_size
            except:
                i += 1
        else:
            i += 1

    return boundaries


def split_ogg_file_properly(audio_data, max_chunk_duration_sec=30):
    """Правильно разбивает OGG файл по границам страниц"""
    # Находим границы OGG страниц
    boundaries = find_ogg_page_boundaries(audio_data)

    if not boundaries:
        print("⚠️ Не найдены OGG границы, используем простую разбивку")
        return split_audio_file_simple(audio_data, max_chunk_duration_sec)

    print(f"📋 Найдено {len(boundaries)} OGG страниц")

    # Примерный расчет: 1500 байт/сек
    target_chunk_size = max_chunk_duration_sec * 1500
    chunks = []
    current_chunk_start = 0

    for i in range(1, len(boundaries)):
        chunk_size = boundaries[i] - boundaries[current_chunk_start]

        # Если добавляя следующую страницу превысим лимит - создаем chunk
        if chunk_size > target_chunk_size and current_chunk_start < i - 1:
            chunk_end = boundaries[i - 1]
            chunk_data = audio_data[boundaries[current_chunk_start]:chunk_end]

            chunks.append({
                'data': chunk_data,
                'duration_sec': len(chunk_data) / 1500,
                'size_bytes': len(chunk_data),
                'chunk_number': len(chunks) + 1,
                'type': 'ogg_proper'
            })

            current_chunk_start = i - 1

    # Добавляем последний chunk
    if current_chunk_start < len(boundaries):
        chunk_data = audio_data[boundaries[current_chunk_start]:]
        chunks.append({
            'data': chunk_data,
            'duration_sec': len(chunk_data) / 1500,
            'size_bytes': len(chunk_data),
            'chunk_number': len(chunks) + 1,
            'type': 'ogg_proper'
        })

    return chunks


def split_audio_file_simple(audio_data, chunk_duration_sec=30):
    """Простая разбивка (для сравнения)"""
    chunk_size = chunk_duration_sec * 1500
    chunks = []

    for i in range(0, len(audio_data), chunk_size):
        chunk = audio_data[i:i + chunk_size]
        chunks.append({
            'data': chunk,
            'duration_sec': len(chunk) / 1500,
            'size_bytes': len(chunk),
            'chunk_number': len(chunks) + 1,
            'type': 'simple'
        })

    return chunks


def recognize_audio_chunk(audio_chunk, token, folder_id):
    """Распознает один фрагмент аудио"""
    url = "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize"

    try:
        response = requests.post(
            url,
            headers={"Authorization": f"Bearer {token}"},
            params={'folderId': folder_id, 'lang': 'ru-RU'},
            data=audio_chunk,
            timeout=30
        )

        if response.status_code == 200:
            return {
                'success': True,
                'text': response.json().get('result', ''),
                'error': None
            }
        else:
            return {
                'success': False,
                'text': '',
                'error': response.text
            }
    except Exception as e:
        return {
            'success': False,
            'text': '',
            'error': str(e)
        }


def recognize_audio_file_advanced(file_path, folder_id, max_chunk_duration=30):
    """Улучшенная функция распознавания с правильной разбивкой OGG"""

    with open(file_path, 'rb') as f:
        audio_data = f.read()

    file_size = len(audio_data)
    total_duration = file_size / 1500

    print(f"📊 Анализ файла:")
    print(f"   Размер: {file_size} байт")
    print(f"   Длительность: {total_duration:.1f} секунд")

    # Пробуем правильную разбивку OGG
    print("🔧 Пробую правильную разбивку OGG...")
    chunks = split_ogg_file_properly(audio_data, max_chunk_duration)

    # Если не получилось, пробуем простую разбивку
    if len(chunks) <= 1:
        print("🔧 Пробую простую разбивку...")
        chunks = split_audio_file_simple(audio_data, max_chunk_duration)

    print(f"   Количество частей: {len(chunks)}")

    token = create_iam_token()
    results = []

    for chunk in chunks:
        print(f"\n🔊 Обрабатываю часть {chunk['chunk_number']}/{len(chunks)} "
              f"({chunk['duration_sec']:.1f} сек, {chunk['size_bytes']} байт, {chunk['type']})...")

        result = recognize_audio_chunk(chunk['data'], token, folder_id)

        if result['success']:
            results.append(result['text'])
            print(f"✅ Успешно: {result['text'][:100]}...")
        else:
            error_msg = result['error']
            # Если ошибка OGG header, пробуем добавить заголовок
            if "ogg header" in error_msg.lower():
                print("🔄 Пробую восстановить OGG заголовок...")
                fixed_chunk = repair_ogg_chunk(chunk['data'])
                if fixed_chunk:
                    result2 = recognize_audio_chunk(fixed_chunk, token, folder_id)
                    if result2['success']:
                        results.append(result2['text'])
                        print(f"✅ Восстановлено: {result2['text'][:100]}...")
                    else:
                        results.append(f"[ОШИБКА: не удалось восстановить]")
                        print(f"❌ Ошибка после восстановления: {result2['error']}")
                else:
                    results.append(f"[ОШИБКА: поврежденный OGG]")
                    print(f"❌ Не удалось восстановить OGG структуру")
            else:
                results.append(f"[ОШИБКА: {error_msg[:50]}...]")
                print(f"❌ Ошибка: {error_msg}")

    return results, total_duration


def repair_ogg_chunk(chunk_data):
    """Пытается восстановить OGG структуру для chunk'а"""
    # Простая попытка: если данные начинаются не с OggS, но содержат OggS внутри
    if chunk_data[:4] != b'OggS':
        # Ищем первый OggS внутри данных
        oggs_pos = chunk_data.find(b'OggS')
        if oggs_pos > 0 and oggs_pos < len(chunk_data) - 100:
            return chunk_data[oggs_pos:]

    return chunk_data


# Основная программа
if __name__ == "__main__":
    AUDIO_FILE_PATH = 'D:/yandex_speechkit_test.ogg'
    FOLDER_ID = 'b1goe0ht2mcgvsi5hgfd'

    print("🎙️ Начинаю улучшенное распознавание аудиофайла...")

    try:
        recognized_texts, total_duration = recognize_audio_file_advanced(
            AUDIO_FILE_PATH, FOLDER_ID, max_chunk_duration=30
        )

        # Вывод результатов
        print("\n" + "=" * 60)
        print("🎯 РЕЗУЛЬТАТЫ РАСПОЗНАВАНИЯ:")
        print("=" * 60)

        success_parts = [t for t in recognized_texts if not t.startswith('[ОШИБКА')]
        print(f"✅ Успешно распознано: {len(success_parts)}/{len(recognized_texts)} частей")

        for i, text in enumerate(recognized_texts, 1):
            print(f"\n📄 Часть {i}:")
            print(text)

        # Сохраняем только успешные части
        successful_text = " ".join(success_parts)

        output_file = 'D:/recognized_improved.txt'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("УЛУЧШЕННОЕ РАСПОЗНАВАНИЕ:\n")
            f.write("=" * 50 + "\n")
            f.write(f"Успешно: {len(success_parts)}/{len(recognized_texts)} частей\n\n")

            for i, text in enumerate(recognized_texts, 1):
                f.write(f"--- ЧАСТЬ {i} ---\n")
                f.write(text + "\n\n")

        print(f"💾 Результаты сохранены в: {output_file}")

    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")