# from openai import OpenAI
# import os


# OPENAI_API_KEY = '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'

# def identify_dark_patterns(text):
#     prompt = f"Analyze this text: {text} Does it employ manipulative tactics to influence my behavior or choices? If so, identify the specific dark patterns (Social Proof, Urgency, Misdirection, Scarcity, Obstruction) present and explain how they are used, considering the sentiment and stylistic elements you identified."
#     client = OpenAI()

#     response = client.completions.create(
#     model="gpt-3.5-turbo-instruct",
#     prompt="Write a tagline for an ice cream shop.",
#     api_key=OPENAI_API_KEY
#     )
#     return response.choices[0].text
# print(identify_dark_patterns('hi'))