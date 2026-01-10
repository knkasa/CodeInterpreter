import os
from loguru import logger
import dspy
from src.bedrockc_claude_lm import BedrockClaudeLM


class Creator:
    __slots__ = ["bedrock_lm"]

    def __init__(self):
        logger.info("Initializing Creator()")
        self.bedrock_lm = BedrockClaudeLM(
            model_id=os.getenv(
                "MODEL_ID"
            )  # "us.anthropic.claude-sonnet-4-20250514-v1:0",
        )

    def llm_code_creator(self, prompt: str) -> str:
        """
        Accepts prompt and generate response.

        Args:
            prompt(str): Promt.
        Returns:
            responst(str): Response.
        """
        dspy.settings.configure(lm=self.bedrock_lm, adapter=dspy.ChatAdapter())

        loaded_rag = BasicQA()
        loaded_rag.load("my_optimized_rag.json")
        response_raw = loaded_rag(prompt)

        return response_raw["answer"]


class QuestionAnswer(dspy.Signature):
    """Answer questions with short factual answers."""

    question = dspy.InputField()
    answer = dspy.OutputField()


class BasicQA(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generate_answer = dspy.ChainOfThought(QuestionAnswer)

    def forward(self, question):
        return self.generate_answer(question=question)
