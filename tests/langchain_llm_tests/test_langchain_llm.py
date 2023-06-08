# coding=utf-8

import pytest
import sys

from modules.langchain_llm.LangChainTextGenerator import LangChainTextGenerator as TextGenerator

def test_langchain_llm():
    assert TextGenerator(0).generate_response("What is the Spanish translation of {input}? Provide only the answer.", "Apple") == "Manzana"
