from typing import List, Optional
import re


class RecursiveCharacterTextSplitter:
    def __init__(
            self,
            chunk_size: int = 400,
            chunk_overlap: int = 200,
            separators: Optional[List[str]] = None,
            keep_separator: bool = True
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.keep_separator = keep_separator

        if separators is None:
            self.separators = ["\n\n", "\n", ". ", "! ", "? ", "; ", ", ", " ", ""]
        else:
            self.separators = separators

        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap должен быть меньше chunk_size")

    def split_text(self, text: str) -> List[str]:
        """Основной метод для разделения текста"""
        if not text.strip():
            return []

        return self._split_text_recursive(text, self.separators)

    def _split_text_recursive(self, text: str, separators: List[str]) -> List[str]:
        """Рекурсивно разделяет текст используя разделители по порядку"""
        chunks = []

        # Если текст уже достаточно маленький, возвращаем его
        if len(text) <= self.chunk_size:
            return [text] if text.strip() else []

        # Пробуем каждый разделитель по порядку
        for i, separator in enumerate(separators):
            if separator == "":
                # Последний разделитель - разделение посимвольно
                chunks = self._split_by_length(text)
                break

            if separator in text:
                # Разделяем текст по текущему разделителю
                splits = self._split_by_separator(text, separator)

                # Проверяем, что все части достаточно маленькие
                if all(len(split) <= self.chunk_size for split in splits):
                    chunks = splits
                    break
                else:
                    # Если есть большие части, рекурсивно обрабатываем их
                    chunks = []
                    for split in splits:
                        if len(split) <= self.chunk_size:
                            chunks.append(split)
                        else:
                            # Рекурсивный вызов с оставшимися разделителями
                            sub_chunks = self._split_text_recursive(split, separators[i + 1:])
                            chunks.extend(sub_chunks)
                    break

        # Если не нашли подходящего разделителя, разделяем по длине
        if not chunks:
            chunks = self._split_by_length(text)

        # Объединяем мелкие чанки и обрабатываем перекрытия
        return self._merge_chunks_with_overlap(chunks)

    def _split_by_separator(self, text: str, separator: str) -> List[str]:
        """Разделяет текст по разделителю"""
        if separator == "":
            return [text]

        parts = text.split(separator)
        result = []

        for i, part in enumerate(parts):
            if not part.strip():
                continue

            if self.keep_separator and i > 0:
                # Добавляем разделитель обратно к части
                result.append(separator + part)
            else:
                result.append(part)

        return result

    def _split_by_length(self, text: str) -> List[str]:
        """Разделяет текст по длине (посимвольно)"""
        chunks = []
        start = 0

        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end]
            if chunk.strip():  # Игнорируем пустые чанки
                chunks.append(chunk)
            start = end

        return chunks

    def _merge_chunks_with_overlap(self, chunks: List[str]) -> List[str]:
        """Объединяет чанки с учетом перекрытия"""
        if not chunks:
            return []

        # Если overlap = 0, просто возвращаем чанки как есть (после фильтрации)
        if self.chunk_overlap == 0:
            return [chunk for chunk in chunks if chunk.strip()]

        merged_chunks = []
        current_chunk = chunks[0]

        for i in range(1, len(chunks)):
            next_chunk = chunks[i]

            # Если текущий чанк слишком маленький, пробуем объединить со следующим
            if len(current_chunk) < self.chunk_size:
                combined = current_chunk + next_chunk

                if len(combined) <= self.chunk_size:
                    current_chunk = combined
                else:
                    # Добавляем текущий чанк и начинаем новый с перекрытием
                    merged_chunks.append(current_chunk)
                    # Создаем перекрытие для следующего чанка
                    overlap_start = max(0, len(current_chunk) - self.chunk_overlap)
                    current_chunk = current_chunk[overlap_start:] + next_chunk
            else:
                # Чанк достиг максимального размера
                merged_chunks.append(current_chunk)
                # Создаем перекрытие для следующего чанка
                overlap_start = max(0, len(current_chunk) - self.chunk_overlap)
                current_chunk = current_chunk[overlap_start:] + next_chunk

        # Добавляем последний чанк
        if current_chunk.strip():
            merged_chunks.append(current_chunk)

        return merged_chunks

