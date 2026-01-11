import os
from loguru import logger
from src.logger_format import Logger
from src.interpreter import program_execution_class

def main():
    Logger()
    user_prompt = os.environ.get("USER_PROMPT")

    if not user_prompt:
        raise ValueError("USER_PROMPT environment variable is not set")
    logger.info(f"User prompt:{user_prompt}")
    program_execution_class(user_prompt)
    
if __name__ == "__main__":
    main()

