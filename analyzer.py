# analyzer.py
from openai import AzureOpenAI
from config import AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_KEY, AZURE_OPENAI_DEPLOYMENT

instruction = """You are a news summarization assistant specialized in Vietnam news.
                You receive multiple article texts and produce short, clear summaries
                of information related only to the user's chosen topic.
                Your tone should be factual, neutral, and easy to read.
                If the topic is unclear, ask the user to clarify.
                # FORMAT INSTRUCTION
                You must respond in the following format ONLY.
                Do not include any commentary, explanation, or additional text.
                
                Format example:
                ---
                <ID>: <content>
                <ID>: <content>
                ---"""

def summarize_articles(articles, topic):
    client = AzureOpenAI(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_KEY,
        api_version="2024-05-01-preview"
    )

    articles_text = "\n\n".join([f"{a['title']}: {a['summary']}" for a in articles])

    messages = [
        {
            "role": "system",
            "content": instruction
        },
        {
            "role": "user",
            "content": f"Articles:\n{articles_text}\n\nTopic of interest: {topic}"
        }
    ]

    response = client.chat.completions.create(
        model=AZURE_OPENAI_DEPLOYMENT,
        messages=messages,
        temperature=0.5,
        max_tokens=400
    )

    return response.choices[0].message.content