#!/usr/bin/env python3
"""
FAQ-бот для терминала.
Отвечает на вопросы о репетиции хакатона на основе faq.txt.
"""

import os
import re
import sys
from difflib import SequenceMatcher

STOP_WORDS = {
    "и", "в", "во", "не", "что", "он", "на", "я", "с", "со", "как", "а", "то", "все",
    "она", "так", "его", "но", "да", "ты", "к", "у", "же", "вы", "за", "бы", "по",
    "только", "ее", "мне", "было", "вот", "от", "меня", "еще", "о", "из", "ему",
    "теперь", "когда", "даже", "ну", "вдруг", "ли", "если", "уже", "или", "ни",
    "быть", "был", "него", "до", "вас", "нибудь", "опять", "уж", "вам", "ведь",
    "там", "потом", "себя", "ничего", "ей", "может", "они", "тут", "где", "есть",
    "надо", "ней", "для", "мы", "тебя", "их", "чем", "была", "сам", "чтоб", "без",
    "будто", "чего", "про", "лишь", "том", "раз", "этот", "который", "какой", "какие",
    "какая", "какое", "это"
}

TOPIC_KEYWORDS = [
    # 0: Время / длительность
    {"врем", "когд", "скольк", "длит", "начал", "окончан", "расписан", "тайминг", "часов", "час"},
    # 1: Команда / участники
    {"команд", "состав", "участник", "человек", "людей", "капитан", "рол", "количеств"},
    # 2: Трек / направления
    {"трек", "направлен", "тем", "задач", "кейс", "стек", "выбор"},
    # 3: Сдача / отправка
    {"сдач", "сдат", "отправ", "куда", "дедлайн", "репозитор", "гитхаб", "github", "формат"},
    # 4: Призы / награды
    {"приз", "наград", "победит", "мерч", "подар", "бонус", "выигрыш", "мест"}
]


def clean_and_tokenize(text: str) -> list[str]:
    """Разбивает текст на слова, удаляя пунктуацию и стоп-слова."""
    words = re.findall(r'[a-zA-Zа-яА-ЯёЁ0-9]+', text.lower())
    return [w for w in words if w not in STOP_WORDS and len(w) > 1]


def load_faq(filepath: str) -> list[dict]:
    """Загружает пары вопрос-ответ из faq.txt."""
    if not os.path.exists(filepath):
        print(f"Ошибка: файл {filepath} не найден.", file=sys.stderr)
        sys.exit(1)

    faq_list = []
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    blocks = [b.strip() for b in content.split("\n\n") if b.strip()]
    for idx, block in enumerate(blocks):
        lines = block.splitlines()
        q_line = ""
        a_line = ""
        for line in lines:
            line_str = line.strip()
            if line_str.startswith("Q:"):
                q_line = line_str[2:].strip()
            elif line_str.startswith("A:"):
                a_line = line_str[2:].strip()
        if q_line and a_line:
            tokens = clean_and_tokenize(q_line)
            keywords = TOPIC_KEYWORDS[idx] if idx < len(TOPIC_KEYWORDS) else set()
            faq_list.append({
                "question": q_line,
                "answer": a_line,
                "tokens": tokens,
                "keywords": keywords,
                "index": idx
            })

    return faq_list


def calculate_match_score(user_query: str, faq_item: dict) -> float:
    """Вычисляет степень совпадения вопроса пользователя с элементом FAQ."""
    user_tokens = clean_and_tokenize(user_query)
    if not user_tokens:
        return 0.0

    score = 0.0
    # 1. Совпадение по ключевым корням/словам темы (высокий вес)
    keyword_matches = 0
    for u_token in user_tokens:
        for kw in faq_item["keywords"]:
            if u_token.startswith(kw) or kw.startswith(u_token) or kw in u_token:
                keyword_matches += 1
                break
    score += keyword_matches * 3.0

    # 2. Пересечение токенов вопроса и токенов пользователя (по схожести)
    for u_tok in user_tokens:
        best_token_sim = 0.0
        for q_tok in faq_item["tokens"]:
            sim = SequenceMatcher(None, u_tok, q_tok).ratio()
            if sim > best_token_sim:
                best_token_sim = sim
        if best_token_sim >= 0.7:
            score += best_token_sim * 1.5

    # 3. Общая схожесть полной строки вопроса
    clean_user = " ".join(user_tokens)
    clean_q = " ".join(faq_item["tokens"])
    full_sim = SequenceMatcher(None, clean_user, clean_q).ratio()
    score += full_sim * 1.0

    return score


def find_best_answer(user_query: str, faq_list: list[dict], threshold: float = 2.0) -> str:
    """Находит наиболее подходящий ответ либо возвращает 'не знаю'."""
    best_item = None
    best_score = 0.0

    for item in faq_list:
        score = calculate_match_score(user_query, item)
        if score > best_score:
            best_score = score
            best_item = item

    if best_item is not None and best_score >= threshold:
        return best_item["answer"]

    return "К сожалению, я не знаю ответа на этот вопрос."


def main():
    faq_path = os.path.join(os.path.dirname(__file__), "faq.txt")
    faq_list = load_faq(faq_path)

    print("=" * 60)
    print("🤖 Привет! Я FAQ-бот репетиции хакатона.")
    print("Я могу ответить на вопросы о времени, команде, треках, сдаче и призах.")
    print("Для выхода введите 'выход', 'exit' или 'q'.")
    print("=" * 60)

    while True:
        try:
            user_input = input("\nВы: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nДо встречи!")
            break

        if not user_input:
            continue

        if user_input.lower() in {"выход", "exit", "quit", "q"}:
            print("Бот: Удачи на репетиции! До связи.")
            break

        answer = find_best_answer(user_input, faq_list)
        print(f"Бот: {answer}")


if __name__ == "__main__":
    main()
