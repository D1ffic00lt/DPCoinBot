import openai


class GTP3Model(object):
    def __init__(self, token: str, model: str = "gpt-3.5-turbo-0301") -> None:
        self.token = token
        openai.api_key = self.token
        self.model = model
        self.content = []

    def answer(self, message: str) -> str:
        gpt_answer = openai.ChatCompletion.create(
            model=self.model, messages=[{"role": "user", "content": message}]
        )
        return gpt_answer.choices[0].message.content

    def answer_with_context(self, message: str) -> str:
        self.content.append({"role": "user", "content": message})
        gpt_answer = openai.ChatCompletion.create(
            model=self.model, messages=self.content
        )
        self.content.append({"role": "system", "content": gpt_answer.choices[0].message.content})
        return gpt_answer.choices[0].message.content
