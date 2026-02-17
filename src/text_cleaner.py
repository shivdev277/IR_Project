import re

def clean_text(text):
    text = text.replace("\n", " ")

    # Remove dates like 14-08-2025
    text = re.sub(r"\d{2}-\d{2}-\d{4}", "", text)

    # Remove extra spaces
    text = " ".join(text.split())

    return text
