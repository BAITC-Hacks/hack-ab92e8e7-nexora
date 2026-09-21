import unittest
import os
from bot import load_faq, find_best_answer


class TestFAQBot(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        faq_path = os.path.join(os.path.dirname(__file__), "faq.txt")
        cls.faq_list = load_faq(faq_path)

    def test_faq_loaded(self):
        self.assertEqual(len(self.faq_list), 5)

    def test_question_time(self):
        answer = find_best_answer("Во сколько начинается и когда финиш?", self.faq_list)
        self.assertIn("18:00 до 21:00", answer)

    def test_question_team(self):
        answer = find_best_answer("Сколько человек может быть в команде?", self.faq_list)
        self.assertIn("от 2 до 5 человек", answer)

    def test_question_tracks(self):
        answer = find_best_answer("Какие есть треки и направления?", self.faq_list)
        self.assertIn("AI/ML сервисы", answer)

    def test_question_submission(self):
        answer = find_best_answer("Куда и как сдавать проект?", self.faq_list)
        self.assertIn("ссылки на публичный репозиторий", answer)

    def test_question_prizes(self):
        answer = find_best_answer("Какие призы получат победители?", self.faq_list)
        self.assertIn("мерч", answer)

    def test_unknown_question(self):
        answer = find_best_answer("Какая завтра погода в Лондоне?", self.faq_list)
        self.assertEqual(answer, "К сожалению, я не знаю ответа на этот вопрос.")

    def test_irrelevant_words(self):
        answer = find_best_answer("купить пиццу с доставкой", self.faq_list)
        self.assertEqual(answer, "К сожалению, я не знаю ответа на этот вопрос.")


if __name__ == "__main__":
    unittest.main()
