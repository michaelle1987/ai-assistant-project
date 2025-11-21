import json
from typing import List, Dict, Any, Optional
from datetime import datetime


class ConversationBufferMemory:
    def __init__(self, max_messages: int = 10, return_messages: bool = True):
        self.max_messages = max_messages
        self.return_messages = return_messages
        self.chat_history: List[Dict] = []

    def add_user_message(self, message: str) -> None:
        """Добавить сообщение пользователя"""
        self.chat_history.append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })
        self._trim_history()

    def add_ai_message(self, message: str) -> None:
        """Добавить сообщение AI"""
        self.chat_history.append({
            "role": "assistant",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })
        self._trim_history()

    def add_message(self, role: str, message: str) -> None:
        """Добавить сообщение с указанием роли"""
        self.chat_history.append({
            "role": role,
            "content": message,
            "timestamp": datetime.now().isoformat()
        })
        self._trim_history()

    def _trim_history(self) -> None:
        """Обрезать историю до максимального размера"""
        if len(self.chat_history) > self.max_messages:
            # Оставляем последние max_messages сообщений
            self.chat_history = self.chat_history[-self.max_messages:]

    def clear(self) -> None:
        """Очистить историю"""
        self.chat_history = []

    def get_history(self, as_string: bool = False) -> Any:
        """Получить историю"""
        if as_string:
            return self._format_history_as_string()
        return self.chat_history.copy()

    def _format_history_as_string(self) -> str:
        """Форматировать историю как строку"""
        history_text = ""
        for msg in self.chat_history:
            if msg["role"] == "user":
                history_text += f"Пользователь: {msg['content']}\n"
            else:
                history_text += f"Ассистент: {msg['content']}\n"
        return history_text.strip()

    def get_recent_history(self, last_n: int = 5) -> List[Dict]:
        """Получить последние N сообщений"""
        return self.chat_history[-last_n:] if self.chat_history else []

    def save_to_file(self, file_path: str) -> None:
        """Сохранить историю в файл"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "max_messages": self.max_messages,
                    "chat_history": self.chat_history
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения истории: {e}")

    def load_from_file(self, file_path: str) -> None:
        """Загрузить историю из файла"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.max_messages = data.get("max_messages", 10)
                self.chat_history = data.get("chat_history", [])
        except Exception as e:
            print(f"Ошибка загрузки истории: {e}")

    @property
    def last_user_message(self) -> Optional[str]:
        """Получить последнее сообщение пользователя"""
        for msg in reversed(self.chat_history):
            if msg["role"] == "user":
                return msg["content"]
        return None

    @property
    def last_ai_message(self) -> Optional[str]:
        """Получить последнее сообщение AI"""
        for msg in reversed(self.chat_history):
            if msg["role"] == "assistant":
                return msg["content"]
        return None

    def get_conversation_summary(self) -> str:
        """Создать краткое резюме разговора"""
        if not self.chat_history:
            return "История пуста"

        user_messages = [msg["content"] for msg in self.chat_history if msg["role"] == "user"]
        if user_messages:
            last_user_msg = user_messages[-1]
            return f"Текущая тема: {last_user_msg[:100]}..." if len(
                last_user_msg) > 100 else f"Текущая тема: {last_user_msg}"
        return "Нет сообщений пользователя"