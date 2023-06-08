import json
import os
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate


class LangChainTextGenerator:
    def __init__(self):
        # load openai credentials
        f = open(os.path.realpath(os.path.join(os.path.dirname(__file__), "..", "..", "config/openai_credentials.json")), "r")
        data = json.load(f)
        self.OPEN_API_KEY = data["OPEN_API_KEY"]
        f.close()

        os.environ["OPENAI_API_KEY"] = self.OPEN_API_KEY

        print('Starting LangChainTextGenerator...')
        print("===============================================================")

        self.llm = OpenAI(temperature=0.9)


    def generateText(self, label):
        language_prompt = PromptTemplate(
            input_variables=["product"],
            template="What is a french translation of {product}?",
        )
        input = label.lower().strip()
        return self.llm(language_prompt.format(product=input))





if __name__ == "__main__":
    llm = LangChainTextGenerator()
    llm.generateText("apple")