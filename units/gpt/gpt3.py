import openai_async


class GPT3Model(object):
    def __init__(self, token: str, model: str = "gpt-3.5-turbo-0301") -> None:
        self.token = token
        self.model = model
        self.content = []

    async def answer(self, message: str) -> str:
        response = await openai_async.chat_complete(
            self.token,
            timeout=100,
            payload={
                "model": self.model,
                "messages": [{"role": "user", "content": message}],
            },
        )
        return response.json()["choices"][0]["message"]["content"]

    async def answer_with_context(self, message: str) -> str:
        self.content.append({"role": "user", "content": message})
        response = await openai_async.chat_complete(
            self.token,
            timeout=100,
            payload={
                "model": self.model,
                "messages": self.content,
            },
        )
        self.content.append({"role": "system", "content": response.json()["choices"][0]["message"]})
        return response.json()["choices"][0]["message"]["content"]
