import datetime
from PDOCalculator import PDOCalculator
from pdo_data import SCALES_DESC, EXTRA_SCALES, EXTENDED_DESC

class PDOReportGenerator:
    def __init__(self, name="Клієнт", gender="male"):
        self.name = name
        self.gender = gender
        self.calc = PDOCalculator(gender)

    def generate(self, ans1_str: str, ans2_str: str):
        # Парсинг вхідних рядків
        ans1 = [int(x.strip()) for x in ans1_str.split(',') if x.strip()]
        ans2 = [int(x.strip()) for x in ans2_str.split(',') if x.strip()]

        # Розрахунок
        self.calc.calculate(ans1, ans2)
        results = self.calc.get_profile()
        
        # Генерація звіту
        report = self._build_markdown(results)
        
        filename = f"Звіт_PDO_{self.name}_{datetime.date.today()}.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(report)
        
        return filename

    def _build_markdown(self, res):
        scales = res['scales']
        v_index = res['v_index']
        errors = res['errors']

        # Mermaid Chart
        chart = "```mermaid\ngraph BT\n"
        sorted_scales = sorted(scales.items(), key=lambda x: x[1], reverse=True)
        for ltr, val in sorted_scales:
            if ltr in SCALES_DESC:
                label = f"{ltr} ({SCALES_DESC[ltr]})"
                chart += f'    {ltr}["{label}"] --> |{val}| Score_{ltr}(("{val}"))\n'
        chart += "```"

        report = f"""# Психологічний профіль (ПДО): {self.name}
> Дата: {datetime.date.today().strftime('%d.%m.%Y')} | Стать: {'Чол' if self.gender == 'male' else 'Жін'}

---

## 📊 Графік акцентуацій характеру
Цей графік відображає інтенсивність прояву різних рис характеру. Чим вищий бал, тим яскравіше виражена ця особливість.

{chart}

---

## 🔍 Детальна розшифровка шкал

### Основні типи:
"""
        for ltr, val in sorted_scales:
            if ltr in SCALES_DESC:
                level = "Високий" if val >= 6 else ("Середній" if val >= 3 else "Низький")
                report += f"#### **{SCALES_DESC[ltr]} ({ltr})**: {val} балів — *{level} рівень.*\n"
                
                # Додаємо розширений опис, якщо бал високий
                if val >= 6 and ltr in EXTENDED_DESC:
                    desc = EXTENDED_DESC[ltr]
                    report += f"> **{desc['title']}**\n"
                    report += f"> {desc['text']}\n"
                    report += f"> [Читати більше про цей тип]({desc['link']})\n\n"

        report += "\n### Додаткові показники:\n"
        for ltr, val in scales.items():
            if ltr in EXTRA_SCALES:
                report += f"- **{EXTRA_SCALES[ltr]} ({ltr})**: {val} балів\n"
        
        report += f"\n- **Індекс щирості (v)**: {v_index} (Норма: від -4 до +4)\n"
        report += f"- **Кількість помилок вибору**: {errors}\n"

        report += """
---

## 📌 Що це означає для вас?

Цей профіль не є вироком, це лише опис вашої «внутрішньої архітектури». Знання свого типу допомагає:
1. Розуміти причини конфліктів у парі.
2. Помітити, коли ви дієте за «автоматичним» сценарієм.
3. Використовувати свої сильні сторони, не руйнуючись об слабкі.

**Бажаєте розібрати цей звіт детальніше?**
Запишіться на 20-хвилинну безкоштовну консультацію, щоб зрозуміти, як ці результати впливають на ваш стан сьогодні.

[👉 Записатись на розбір](https://t.me/kobak_vit)
"""
        return report

# Тестовий запуск (приклад)
if __name__ == "__main__":
    # Тестові дані (25 відповідей для кожного дослідження)
    test_ans1 = "2, 1, 1, 1, 5, 4, 1, 4, 2, 1, 3, 7, 9, 3, 5, 9, 3, 1, 1, 1, 1, 2, 2, 1, 1"
    test_ans2 = "2, 10, 2, 7, 3, 11, 2, 1, 2, 11, 3, 10, 1, 3, 0, 7, 2, 5, 4, 11, 9, 8, 4, 9, 1"
    
    gen = PDOReportGenerator("Віталій (Тест)")
    file = gen.generate(test_ans1, test_ans2)
    print(f"Звіт згенеровано: {file}")
