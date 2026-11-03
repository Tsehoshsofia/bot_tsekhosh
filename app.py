from flask import Flask, request, jsonify
from flask_cors import CORS
import csv
import os
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)
CORS(app)

PRESENTATIONS = {
    "1": {"title": "Введение в программирование", "url": "ССЫЛКА_1"},
    "2": {"title": "Работа с числовыми данными", "url": "ССЫЛКА_2"},
    "3": {"title": "Работа с текстовыми данными", "url": "ССЫЛКА_3"},
    "4": {"title": "Условный оператор", "url": "ССЫЛКА_4"},
    "5": {"title": "Циклы", "url": "ССЫЛКА_5"},
    "6": {"title": "Множества", "url": "ССЫЛКА_6"},
    "7": {"title": "Строки и символы", "url": "ССЫЛКА_7"},
    "8": {"title": "Списки", "url": "ССЫЛКА_8"},
    "9": {"title": "Библиотеки, объекты, функции", "url": "ССЫЛКА_9"},
    "10": {"title": "Работа с табличными данными", "url": "ССЫЛКА_10"}
}

QUIZ_QUESTIONS = [
    {
        "type": "text",
        "question": "Что выведет код: print([10, 20, 30, 40][1:3])?",
        "options": ["[10, 20]", "[20, 30]", "[20, 30, 40]"],
        "correct": 1,
        "explanation": "Срез [1:3] берет элементы с индексом 1 до 2, не включая 3."
    },
    {
        "type": "image",
        "image_url": "https://via.placeholder.com/400x200.png?text=Тут+будет+картинка+с+ошибкой",
        "question": "Найди ошибку в коде на картинке:",
        "options": ["Неверное имя переменной", "Отсутствует двоеточие", "Не закрыта скобка"],
        "correct": 1,
        "explanation": "После if всегда ставится двоеточие."
    }
]

QUEST_STEPS = [
    {
        "question": "Шаг 1. Как объявить переменную с числом 55?",
        "options": ["55 = num", "num = 55", "int num = 55"],
        "correct": 1
    },
    {
        "question": "Шаг 2. Каким будет результат 10 / 3?",
        "options": ["3.33", "3", "Ошибка"],
        "correct": 0
    }
]

user_states = {}

def save_to_csv(user_id, age, gender, status, result):
    file_exists = os.path.isfile('analytics.csv')
    with open('analytics.csv', mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['user_id', 'age', 'gender', 'status', 'result'])
        writer.writerow([user_id, age, gender, status, result])

def generate_chart(score, total):
    plt.figure(figsize=(4, 4))
    labels = ['Правильно', 'Неправильно']
    sizes = [score, total - score]
    colors = ['#4CAF50', '#F44336']
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    plt.title('Ваш результат теста')
    
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return f"data:image/png;base64,{plot_url}"

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_id = data.get('user_id', 'default')
    message = data.get('message', '').strip().lower()

    if user_id not in user_states:
        user_states[user_id] = {
            "state": "registration_age",
            "age": None, "gender": None, "status": None,
            "quiz_index": 0, "quiz_score": 0,
            "quest_index": 0
        }

    state = user_states[user_id]["state"]

    if state == "registration_age":
        user_states[user_id]["age"] = message
        user_states[user_id]["state"] = "registration_gender"
        return jsonify({
            "text": f"Принято! {message} лет — отличный возраст для старта в IT. Теперь укажи свой пол (М/Ж), чтобы я знала, как к тебе обращаться:", 
            "buttons": []
        })
        
    elif state == "registration_gender":
        user_states[user_id]["gender"] = message
        user_states[user_id]["state"] = "registration_status"
        return jsonify({
            "text": "Супер! А теперь выбери свой статус:", 
            "buttons": [
                {"text": "🎓 Я студент 1 курса", "value": "Студент 1 курса"},
                {"text": "👨‍🏫 Я преподаватель", "value": "Преподаватель"}
            ]
        })

    elif state == "registration_status":
        user_states[user_id]["status"] = message
        user_states[user_id]["state"] = "menu"
        
        if message == "Преподаватель":
            welcome_text = "Здравствуйте! Я София. Готова помочь вам с проверкой знаний студентов. Все результаты сохраняются в аналитике."
        else:
            welcome_text = "Привет, первокурсник! Я София, твой цифровой помощник. Вместе мы прокачаем Python так, что сессия покажется легкой прогулкой. С чего начнем?"
            
        save_to_csv(user_id, user_states[user_id]["age"], user_states[user_id]["gender"], user_states[user_id]["status"], "Зарегистрирован")
        
        return jsonify({
            "text": welcome_text,
            "buttons": [
                {"text": "📚 Презентации", "value": "presentations"},
                {"text": "📝 Тестирование", "value": "start_quiz"},
                {"text": "🎮 Квест", "value": "start_quest"},
                {"text": "📊 Аналитика", "value": "analytics"}
            ]
        })

    if message in ["привет", "начать", "меню", "назад в меню"]:
        user_states[user_id]["state"] = "menu"
        return jsonify({
            "text": "Главное меню. Выбери пункт:",
            "buttons": [
                {"text": "📚 Презентации", "value": "presentations"},
                {"text": "📝 Тестирование", "value": "start_quiz"},
                {"text": "🎮 Квест", "value": "start_quest"},
                {"text": "📊 Аналитика", "value": "analytics"}
            ]
        })

    elif state == "menu" and message == "presentations":
        user_states[user_id]["state"] = "presentations_menu"
        buttons = [{"text": f"{k}. {v['title']}", "value": f"pres_{k}"} for k, v in PRESENTATIONS.items()]
        buttons.append({"text": "⬅️ Назад", "value": "menu"})
        return jsonify({"text": "Выбери тему презентации:", "buttons": buttons})

    elif state == "presentations_menu" and message.startswith("pres_"):
        pres_id = message.split("_")[1]
        pres = PRESENTATIONS[pres_id]
        return jsonify({
            "text": f"Тема: {pres['title']}. Скачивай по ссылке: {pres['url']}",
            "buttons": [{"text": "⬅️ Назад к темам", "value": "presentations"}]
        })

    elif message == "start_quiz":
        user_states[user_id]["state"] = "quiz"
        user_states[user_id]["quiz_index"] = 0
        user_states[user_id]["quiz_score"] = 0
        return ask_quiz(user_id)

    elif state == "quiz":
        q_idx = user_states[user_id]["quiz_index"]
        q = QUIZ_QUESTIONS[q_idx]
        
        try:
            ans = int(message)
            if ans == q["correct"]:
                user_states[user_id]["quiz_score"] += 1
                feedback = "✅ Верно! " + q["explanation"]
            else:
                feedback = "❌ Ошибка. " + q["explanation"]

            user_states[user_id]["quiz_index"] += 1
            
            if user_states[user_id]["quiz_index"] >= len(QUIZ_QUESTIONS):
                score = user_states[user_id]["quiz_score"]
                total = len(QUIZ_QUESTIONS)
                user_states[user_id]["state"] = "menu"
                save_to_csv(user_id, user_states[user_id]["age"], user_states[user_id]["gender"], user_states[user_id]["status"], f"Тест: {score}/{total}")
                return jsonify({
                    "text": f"{feedback}\n\n🏁 Тест завершен! Твой результат: {score} из {total}.",
                    "buttons": [{"text": "В меню", "value": "menu"}]
                })
            else:
                return ask_quiz(user_id, feedback)
        except ValueError:
             return jsonify({"text": "Нажми на кнопку с вариантом ответа!", "buttons": []})

    elif message == "start_quest":
        user_states[user_id]["state"] = "quest"
        user_states[user_id]["quest_index"] = 0
        return jsonify({
            "text": "⚠️ Внимание! В квесте нельзя ошибаться. Одна ошибка — и ты начинаешь заново!\n\n" + QUEST_STEPS[0]["question"],
            "buttons": [{"text": opt, "value": str(i)} for i, opt in enumerate(QUEST_STEPS[0]["options"])] + [{"text": "⬅️ В меню", "value": "menu"}]
        })

    elif state == "quest":
        q_idx = user_states[user_id]["quest_index"]
        q = QUEST_STEPS[q_idx]
        
        try:
            ans = int(message)
            if ans == q["correct"]:
                user_states[user_id]["quest_index"] += 1
                if user_states[user_id]["quest_index"] >= len(QUEST_STEPS):
                    user_states[user_id]["state"] = "menu"
                    return jsonify({
                        "text": "🏆 Поздравляю! Ты прошел квест без ошибок! София гордится тобой!",
                        "buttons": [{"text": "В меню", "value": "menu"}]
                    })
                else:
                    next_q = QUEST_STEPS[user_states[user_id]["quest_index"]]
                    return jsonify({
                        "text": "✅ Верно! Идем дальше:\n\n" + next_q["question"],
                        "buttons": [{"text": opt, "value": str(i)} for i, opt in enumerate(next_q["options"])] + [{"text": "⬅️ В меню", "value": "menu"}]
                    })
            else:
                user_states[user_id]["quest_index"] = 0
                return jsonify({
                    "text": "❌ ОШИБКА! Квест начинается заново.\n\n" + QUEST_STEPS[0]["question"],
                    "buttons": [{"text": opt, "value": str(i)} for i, opt in enumerate(QUEST_STEPS[0]["options"])] + [{"text": "⬅️ В меню", "value": "menu"}]
                })
        except ValueError:
             return jsonify({"text": "Пожалуйста, выбери вариант ответа.", "buttons": []})

    elif message == "analytics":
        score = user_states[user_id]["quiz_score"]
        total = len(QUIZ_QUESTIONS) if len(QUIZ_QUESTIONS) > 0 else 1
        chart_base64 = generate_chart(score, total)
        
        return jsonify({
            "text": f"📊 Твоя аналитика:\nПравильных ответов: {score}\nТвой прогресс на графике:",
            "image": chart_base64,
            "buttons": [{"text": "⬅️ В меню", "value": "menu"}]
        })

    return jsonify({"text": "Я не поняла. Нажми на кнопки.", "buttons": [{"text": "В меню", "value": "menu"}]})

def ask_quiz(user_id, prefix=""):
    q_idx = user_states[user_id]["quiz_index"]
    q = QUIZ_QUESTIONS[q_idx]
    
    if q["type"] == "image":
        text = f"{prefix}\n\nВопрос {q_idx+1}:\n{q['question']}"
        return jsonify({
            "text": text,
            "image": q["image_url"],
            "buttons": [{"text": opt, "value": str(i)} for i, opt in enumerate(q["options"])]
        })
    else:
        text = f"{prefix}\n\nВопрос {q_idx+1}:\n{q['question']}"
        return jsonify({
            "text": text,
            "buttons": [{"text": opt, "value": str(i)} for i, opt in enumerate(q["options"])]
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
