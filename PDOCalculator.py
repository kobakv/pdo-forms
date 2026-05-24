import re
from collections import Counter
from pdo_data import DECODING, TOPICS

class PDOCalculator:
    def __init__(self, gender='male'):
        self.gender = gender
        self.scores = Counter()
        self.v_sum = 0
        self.errors = 0

    def calculate(self, first_answers: list[int], second_answers: list[int]):
        """
        Розрахунок результатів ПДО.
        first_answers: список номерів відповідей для 1-го дослідження (25 тем).
        second_answers: список номерів відповідей для 2-го дослідження (25 тем).
        """
        self.scores.clear()
        self.v_sum = 0
        self.errors = 0

        # Етап 1 & 2: Розкодування та підрахунок
        for i in range(len(TOPICS)):
            ans1 = first_answers[i] if i < len(first_answers) else None
            ans2 = second_answers[i] if i < len(second_answers) else None

            # Перевірка на помилки (однакова відповідь в обох дослідженнях)
            if ans1 is not None and ans1 == ans2 and ans1 != 0:
                self.errors += 1

            # Обробка 1-го дослідження
            if ans1 is not None:
                self._process_answer(i, 'first', ans1)
            
            # Обробка 2-го дослідження
            if ans2 is not None:
                self._process_answer(i, 'second', ans2)

        # Етап 3: Застосування бонусних правил
        self._apply_bonuses()

        return dict(self.scores), self.v_sum, self.errors

    def _process_answer(self, topic_idx, research, ans_num):
        topic_lookup = DECODING.get(topic_idx, {}).get(research, {})
        tok = topic_lookup.get(ans_num, '')
        if not tok or tok == 'О':
            return

        # Парсинг токена (наприклад: 'ГММ', 'М+1', '+2')
        # Листи (шкали)
        letters = re.findall(r'[А-ЯёЁа-яA-Za-z]', tok)
        for l in letters:
            if l != 'v':  # 'v' рахується окремо як сума чисел
                self.scores[l] += 1

        # Числові значення (v-показник)
        v_matches = re.findall(r'[+\-]\d+', tok)
        for v in v_matches:
            self.v_sum += int(v)

    def _apply_bonuses(self):
        """Логіка додаткових балів (Етап 3)"""
        s = self.scores
        def add(label, n=1):
            s[label] += n

        # Основні умови з вашої логіки
        if s['Г'] <= 1:           add('П'); add('С')
        if s['Ц'] >= 6:           add('Л')
        if s['А'] >= 4:           add('Л')
        if s['П'] <= 1:           add('Н')
        if s['Н'] <= 1:           add('П')
        if s['К'] == 0:           add('Ш', 2); add('И')
        if s['К'] == 1:           add('Ш')
        if s['Д'] >= 6:           add('Н')
        if s['Т'] > s['Д']:       add('П', 2); add('Ц')
        if s['В'] == 5:           add('Э')
        if s['В'] >= 6:           add('Э', 2)
        if s['Е'] >= 6:           add('Ш'); add('И')
        if s['d'] >= 5:           add('Ш')
        if s['О'] >= 6:           add('С')
        
        if self.gender == 'male' and s['М'] < s['Ф']:
            add('С'); add('Ш'); add('И')
            
        if self.v_sum <= -6:      add('С')
        if self.v_sum >= 6:       add('И')

        # Помилки вибору
        if self.errors == 1:      add('Э')
        if self.errors >= 2:      add('Э', 2)

    def get_profile(self):
        """Повертає фінальний словник результатів"""
        return {
            'scales': dict(self.scores),
            'v_index': self.v_sum,
            'errors': self.errors
        }
