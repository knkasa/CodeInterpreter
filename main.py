import os
from loguru import logger
from src.logger_format import Logger
from src.interpreter import program_execution_class

def main():
    Logger()
    #user_prompt = '''
    #    I am trying to create a machine learning model using logistic classification.
    #    Use "users" table and "interaction" table from Redshift.
    #    The target is the purchase column in interaction table.
    #    Use whatever features you think is good for the input data.
    #    Convert categorical columns into binary.  Impute null if exists.
    #    Do other preprocessing as necessary.
    #    '''
    #user_prompt = '''can you do something with "users" table with python?  Just run some simple python code.'''
    user_prompt = os.environ.get("USER_PROMPT")

    if not user_prompt:
        raise ValueError("USER_PROMPT environment variable is not set")
    logger.info(f"User prompt:{user_prompt}")
    program_execution_class(user_prompt)
    
if __name__ == "__main__":
    main()
