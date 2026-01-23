from openai import OpenAI

from settings import YANDEX_CLOUD_API_KEY, YANDEX_CLOUD_FOLDER
from vk_parser import VKParser


UNSUCCESSFUL_GENERATION_TEXT = "я не могу обсуждать эту тему"


class PostGenerator:

    def __init__(self, use_vk_parser=True, default_model="z-ai/glm-4.6"):
        self.openai = OpenAI(
            api_key=YANDEX_CLOUD_API_KEY,
            base_url="https://api.vsellm.ru/v1",
        )
        self.vk_parser = VKParser() if use_vk_parser else None
        self.default_model = default_model
        self.model_override = None

    def _generate_post(self):
        if self.vk_parser is None:
            raise RuntimeError("VK parser is disabled for this generator")
        original_post = self.vk_parser.choose_post()
        prompt = PROMPT.format(original_post=original_post)
        return self._generate_post_from_prompt(prompt)

    def _generate_post_from_prompt(self, prompt):
        response = self.openai.chat.completions.create(
            model=self._resolve_model(),
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=700,
            temperature=1.0,
        )

        return response.choices[0].message.content

    def _resolve_model(self):
        return self.model_override or self.default_model

    def set_model_override(self, model_name):
        self.model_override = model_name or None

    def generate(self):
        while True:
            post = self._generate_post()
            if post and UNSUCCESSFUL_GENERATION_TEXT not in post.lower():
                return post


PROMPT = """
Ты — автор статей для сатирического новостного портала "Parsalov Rhymes". Твой стиль — кринжовый, слегка обидный юмор в стиле желтой прессы.

### КОНТЕКСТ:
*   "Parsalov Rhymes" — это вымышленный музыкальный лейбл, который якобы выпускает песни про реального человека Валентина Парсалова (его прозвище — Валёк).
*   **ВАЖНО:** Валёк НЕ имеет НИКАКОГО отношения к музыке. Он НЕ рэпер, НЕ пишет песен, НЕ снимает клипов, НЕ выступает. Он — обычный человек.

### ЗАДАНИЕ:
Напиши новость на 2-3 абзаца, относительно оригинального поста. Оригинальный пост будет указан ниже.
Важно - не нужно полностью копировать новость, заменяя имена в посте на имя Валька.
Используй пост как основу для вдохновения. Также допускается копировать стилистику написания из оригинального поста.
Новость обязательно должна быть абсурдной, словно текст писал сумасшедший, помешанный на теориях заговора человек.

### ТРЕБОВАНИЯ К НОВОСТИ:
1.  **Тон:** Кринж, абсурд, преувеличение. Пиши так, как будто это сенсация в таблоиде.
2.  **Сюжет:** Придумай **нелепую и провальную ситуацию, уровня скандалов селебрити или скамерских реклам телеграм каналов**.
3.  **Заголовок:** Придумай кричащий, кликбейтный заголовок (выдели его **жирным**).
4.  **Структура:** 2-3 коротких абзаца, динамично.

### СТРОГИЕ ПРАВИЛА:
*   **ГЛАВНОЕ ПРАВИЛО:** Валёк **НЕ СОЗДАЁТ МУЗЫКУ**. В тексте не должно быть ни намёка, что он что-то спел, записал, выпустил, сочинил. Его "вклад в музыку" — это исключительно его бытовые провалы, которые мы высмеиваем.
*   **Имя:** Используй "Валёк" (именно так, с "ё"). Или полное - Валентин Парсалов, или просто Валентин.
*   **Склонения имени:** Падежи для прозвища "Валёк": Именительный: Валёк; Родительный: Валька; Дательный: Вальку; Винительный: Валька; Творительный: Вальком; Предложный: О Вальке.
*   **Формат:** Только текст новости, без вступлений.
*   **Смайлики:** Активно используй смайлики и различные эмодзи, даже немного надоедливо.
*   **Песни лейбла:** Никто не упоминай, что лейбл собирается делать песню о событии, описанном в твоей новости.
*   **Оригинальный пост:** Ни за что не упоминай в тексте оригинальный пост. Оригинальный пост используется только как опора для написания новости.

Начинай писать сразу с заголовка.

<ОРИГИНАЛЬНЫЙ_ПОСТ>
{original_post}
</ОРИГИНАЛЬНЫЙ_ПОСТ>
"""
