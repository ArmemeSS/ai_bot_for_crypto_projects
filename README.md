# **Інструкція до запуску**

## Виконано на Python 3.12.7

Встановлюємо потрібні бібліотеки:
```
pip install -r requirements.txt
```

Налаштовуємоємо файл ```config.py```:

```
OPENAI_API_KEY = "вводимо ключ до OpenAI API"
```
Запуск чат-бота

```
python main.py
```

Зібрані дані про проекти у файлі ```output_example.txt```. 
Приклад результатів генерації у файлі ```crypto_projects.json```

## Документація
### src.assistant_interface

#### class ChatBotAssistant
Клас для ініціалізації та використання моделі GPT-4 з OpenAI API

### src.data_process

#### class ProjectDatabase
Клас для завантаження даних із JSON файлу з проектами

#### class ProjectQueryInterface
Клас для роботи із завантаженими даними
