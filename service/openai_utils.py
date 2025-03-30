import openai
import random

OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"
openai.api_key = OPENAI_API_KEY

# Список случайных тем для генерации комментариев
COMMENT_PROMPTS = [
    "Напиши осмысленный комментарий к этому посту:",
    "Что бы сказал обычный человек в ответ на этот пост?",
    "Как бы ты прокомментировал этот текст?",
]


async def generate_name():
    """Генерирует случайные имя и фамилию"""
    prompt = "Сгенерируй реалистичное русское имя и фамилию."
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=10,
    )
    return response["choices"][0]["message"]["content"]


async def generate_comment(post_text: str):
    """Генерирует правдоподобный комментарий на основе текста поста"""
    prompt = f"{random.choice(COMMENT_PROMPTS)}\n\n{post_text}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=50,
    )
    return response["choices"][0]["message"]["content"]