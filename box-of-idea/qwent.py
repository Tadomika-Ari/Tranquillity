from ollama import chat

response = chat(
    model='qwen3-next:80b-cloud',
    messages=[{'role': 'user', 'content': 'Hello!'}],
)
print(response.message.content)