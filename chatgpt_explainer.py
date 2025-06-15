# chatgpt_explainer.py

import os
from openai import OpenAI
from openai import OpenAIError

client = OpenAI(api_key="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")  # your full key as string here


def explain_article_with_gpt(article, prediction_label):
    try:
        prompt = (
            f"The following news article is predicted as **{prediction_label}**.\n\n"
            f"Explain why this article might be {prediction_label.lower()} in simple language:\n\n{article}"
        )

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You're a helpful assistant for news credibility analysis."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        return response.choices[0].message.content.strip()

    except OpenAIError as e:
        return f"⚠️ ChatGPT Explanation Failed:\n\n{str(e)}"
