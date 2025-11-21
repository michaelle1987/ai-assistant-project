import requests
import json
from datetime import datetime, timedelta
import os


class GroupStats:
    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{token}"
        self.messages_history = []
        self.load_data()

    def load_data(self):
        """Загружаем историю сообщений из файла"""
        try:
            with open('group_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.members_history = data.get('members_history', {})
                self.messages_history = data.get('messages', [])
        except FileNotFoundError:
            self.members_history = {}
            self.messages_history = []

    def save_data(self):
        """Сохраняем данные в файл"""
        data = {
            'members_history': self.members_history,
            'messages': self.messages_history[-1000:]  # храним последние 1000 сообщений
        }
        with open('group_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get_members_count(self):
        """Получаем количество участников группы"""
        try:
            response = requests.post(
                f"{self.base_url}/getChatMembersCount",
                data={'chat_id': self.chat_id}
            )
            result = response.json()
            if result.get('ok'):
                count = result['result']
                # Сохраняем в историю
                today = datetime.now().strftime('%Y-%m-%d')
                if today not in self.members_history:
                    self.members_history[today] = count
                self.save_data()
                return count
            return None
        except Exception as e:
            print(f"Ошибка получения количества участников: {e}")
            return None

    def get_recent_messages(self, hours=24):
        """Получаем сообщения за последние N часов"""
        try:
            response = requests.get(f"{self.base_url}/getUpdates")
            result = response.json()

            if not result.get('ok'):
                return []

            recent_messages = []
            cutoff_time = datetime.now() - timedelta(hours=hours)

            for update in result['result']:
                if 'message' in update:
                    message = update['message']

                    # Проверяем, что сообщение из нашей группы
                    if ('chat' in message and
                            message['chat'].get('id') == self.chat_id and
                            'text' in message):

                        message_time = datetime.fromtimestamp(message['date'])
                        if message_time > cutoff_time:
                            msg_data = {
                                'message_id': message['message_id'],
                                'user_id': message['from']['id'],
                                'username': message['from'].get('username', 'Unknown'),
                                'first_name': message['from'].get('first_name', 'Unknown'),
                                'text': message['text'],
                                'date': message_time.isoformat()
                            }
                            recent_messages.append(msg_data)

                            # Добавляем в историю если нового нет
                            if not any(m['message_id'] == msg_data['message_id']
                                       for m in self.messages_history):
                                self.messages_history.append(msg_data)

            self.save_data()
            return recent_messages

        except Exception as e:
            print(f"Ошибка получения сообщений: {e}")
            return []

    def get_user_activity(self, days=7):
        """Статистика активности пользователей за N дней"""
        cutoff_time = datetime.now() - timedelta(days=days)

        user_activity = {}
        for message in self.messages_history:
            msg_time = datetime.fromisoformat(message['date'])
            if msg_time > cutoff_time:
                user_id = message['user_id']
                if user_id not in user_activity:
                    user_activity[user_id] = {
                        'username': message['username'],
                        'first_name': message['first_name'],
                        'message_count': 0,
                        'last_activity': msg_time
                    }
                user_activity[user_id]['message_count'] += 1
                user_activity[user_id]['last_activity'] = max(
                    user_activity[user_id]['last_activity'], msg_time
                )

        return user_activity

    def get_daily_stats(self, days=7):
        """Статистика по дням"""
        daily_stats = {}
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            daily_stats[date] = {
                'members': self.members_history.get(date, 0),
                'messages': 0,
                'active_users': 0
            }

        # Считаем сообщения по дням
        user_activity_by_day = {}
        for message in self.messages_history:
            msg_date = datetime.fromisoformat(message['date']).strftime('%Y-%m-%d')
            if msg_date in daily_stats:
                daily_stats[msg_date]['messages'] += 1

                user_id = message['user_id']
                if msg_date not in user_activity_by_day:
                    user_activity_by_day[msg_date] = set()
                user_activity_by_day[msg_date].add(user_id)

        # Добавляем активных пользователей по дням
        for date, users in user_activity_by_day.items():
            if date in daily_stats:
                daily_stats[date]['active_users'] = len(users)

        return daily_stats

    def print_current_stats(self):
        """Вывод текущей статистики в консоль"""
        members_count = self.get_members_count()
        recent_messages = self.get_recent_messages(hours=24)
        user_activity = self.get_user_activity(days=1)
        daily_stats = self.get_daily_stats(days=7)

        print("📊 ТЕКУЩАЯ СТАТИСТИКА ГРУППЫ")
        print("=" * 50)

        if members_count:
            print(f"👥 Участников: {members_count}")

        print(f"💬 Сообщений за 24ч: {len(recent_messages)}")
        print(f"👤 Активных пользователей за 24ч: {len(user_activity)}")

        print("\n🏆 ТОП-5 активных пользователей (24ч):")
        sorted_users = sorted(user_activity.items(),
                              key=lambda x: x[1]['message_count'],
                              reverse=True)[:5]

        for i, (user_id, data) in enumerate(sorted_users, 1):
            name = data['first_name'] or data['username'] or f"User_{user_id}"
            print(f"  {i}. {name}: {data['message_count']} сообщ.")

        print("\n📈 СТАТИСТИКА ЗА НЕДЕЛЮ:")
        for date, stats in sorted(daily_stats.items()):
            if stats['members'] > 0 or stats['messages'] > 0:
                print(f"  {date}: 👥{stats['members']} | 💬{stats['messages']} | 👤{stats['active_users']}")


def main():
    # Настройки (замени на свои)
    BOT_TOKEN = "8262729679:AAGqrX0EUlm6jvfCnKsoUOrd9rdmeOCR7zU"
    GROUP_ID = -4280604102  # твой ID группы

    stats = GroupStats(BOT_TOKEN, GROUP_ID)

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("🤖 ТЕЛЕГРАМ АНАЛИТИКА ГРУППЫ")
        print("=" * 40)
        print("1. 📊 Текущая статистика")
        print("2. 🔄 Обновить данные")
        print("3. 📈 Статистика за неделю")
        print("4. 🏆 Топ пользователей")
        print("5. 🚪 Выход")
        print("=" * 40)

        choice = input("Выберите действие (1-5): ").strip()

        if choice == "1":
            stats.print_current_stats()
        elif choice == "2":
            print("🔄 Обновляем данные...")
            stats.get_members_count()
            stats.get_recent_messages()
            print("✅ Данные обновлены!")
        elif choice == "3":
            print_stats_week(stats)
        elif choice == "4":
            print_top_users(stats)
        elif choice == "5":
            print("👋 До свидания!")
            break
        else:
            print("❌ Неверный выбор!")

        input("\nНажмите Enter чтобы продолжить...")


def print_stats_week(stats):
    """Статистика за неделю"""
    daily_stats = stats.get_daily_stats(days=7)

    print("\n📈 СТАТИСТИКА ЗА НЕДЕЛЮ:")
    print("Дата       | Участн. | Сообщ. | Активн.")
    print("-" * 40)

    total_messages = 0
    for date, data in sorted(daily_stats.items()):
        if data['members'] > 0 or data['messages'] > 0:
            print(f"{date} | {data['members']:>7} | {data['messages']:>6} | {data['active_users']:>7}")
            total_messages += data['messages']

    print(f"\n📊 Итого сообщений за неделю: {total_messages}")


def print_top_users(stats):
    """Топ пользователей за неделю"""
    user_activity = stats.get_user_activity(days=7)

    print("\n🏆 ТОП-10 ПОЛЬЗОВАТЕЛЕЙ ЗА НЕДЕЛЮ:")
    sorted_users = sorted(user_activity.items(),
                          key=lambda x: x[1]['message_count'],
                          reverse=True)[:10]

    for i, (user_id, data) in enumerate(sorted_users, 1):
        name = data['first_name'] or data['username'] or f"User_{user_id}"
        last_active = data['last_activity'].strftime('%d.%m %H:%M')
        print(f"{i:2}. {name:<20} | {data['message_count']:>3} сообщ. | последнее: {last_active}")


if __name__ == "__main__":
    main()