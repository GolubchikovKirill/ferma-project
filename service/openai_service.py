import openai
import random
from config import OPENAI_API_KEY
import logging

openai.api_key = OPENAI_API_KEY

logger = logging.getLogger(__name__)

# Список случайных тем для генерации комментариев
COMMENT_PROMPTS = [
    "Напиши осмысленный комментарий к этому посту:",
    "Что бы сказал обычный человек в ответ на этот пост?",
    "Как бы ты прокомментировал этот текст?",
]

async def generate_name():
    """Генерирует случайные имя и фамилию"""
    try:
        prompt = "Сгенерируй реалистичное русское имя и фамилию."
        response = await openai.ChatCompletion.create(  # Используйте ChatCompletion
            model="gpt-3.5-turbo",  # Или gpt-4, если нужно
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=10,
        )
        # Разделим результат на имя и фамилию
        return response["choices"][0]["message"]["content"].strip().split()
    except Exception as e:
        logger.error(f"OpenAI error: {e}")
        return "User", str(random.randint(1000, 9999))  # дефолтное имя

async def generate_comment(post_text: str):
    """Генерирует правдоподобный комментарий на основе текста поста"""
    prompt = f"{random.choice(COMMENT_PROMPTS)}\n\n{post_text}"
    try:
        response = await openai.ChatCompletion.create(  # Используйте ChatCompletion
            model="gpt-3.5-turbo",  # Или gpt-4, если нужно
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=50,
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        logger.error(f"OpenAI error while generating comment: {e}")
        return "Не могу сгенерировать комментарий."