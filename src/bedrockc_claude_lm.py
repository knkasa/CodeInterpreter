import os
import json
import boto3
import dspy

class BedrockClaudeLM(dspy.LM):
    def __init__(
        self,
        model_id:str,
        region="us-east-1",
        temperature=os.getenv('TEMP'),
        max_tokens=os.getenv('MAX_TOKENS'),
    ):
        super().__init__(model=model_id)

        session = boto3.Session()
        self.client = session.client(
            "bedrock-runtime",
            region_name=region
        )

        self.model_id = model_id
        self.temperature = temperature
        self.max_tokens = max_tokens

def __call__(self, prompt=None, messages=None, **kwargs):
    if messages is not None:
        prompt = "\n".join(
            m["content"] if isinstance(m["content"], str)
            else m["content"][0]["text"]
            for m in messages
        )

    payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "temperature": self.temperature,
        "max_tokens": self.max_tokens,
        "messages": [
            {
                "role": "system",
                "content": [{
                    "type": "text",
                    "text": (
                        "You must respond ONLY in valid JSON.\n"
                        "The JSON must contain exactly these fields:\n"
                        "- reasoning\n"
                        "- answer\n"
                        "Do not include any extra text outside JSON."
                    )
                }]
            },
            {
                "role": "user",
                "content": [{"type": "text", "text": prompt}]
            }
        ],
    }

    response = self.client.invoke_model(
        modelId=self.model_id,
        body=json.dumps(payload),
        contentType="application/json",
        accept="application/json",
    )

    body = json.loads(response["body"].read())

    return body["content"][0]["text"]
