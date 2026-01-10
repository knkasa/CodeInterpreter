from typing import Tuple
import subprocess
import sys
from loguru import logger
from bs4 import BeautifulSoup
from src.creator import Creator

class program_execution_class:
    __slots__ = ['creator_engine']
    def __init__(self, user_prompt:str):
        logger.info('Initializing program_execution_class()')
        self.creator_engine = Creator()
                
        success, final_code, final_requirements, attempts_used = self.auto_fix_and_execute(
            user_prompt, 
            )
        
    def auto_fix_and_execute(self, user_prompt:str, max_attempts=10) -> Tuple[bool, str, str, int]:
        """
            Automatically generate, execute, and fix code until it succeeds.

            Args:
                user_prompt(str): User prompt.
                max_attempts(int): Number of retries (default=5)
            Returns:
                (bool): Boolean that tells whether it fails or not.
                (str): Generated python code.
                (str): Required libraries.
                (int): Number of attempts.
        """
        # Initial prompt.
        prompt = f'''{user_prompt} \n {self.python_template_func()}'''
        
        # Try executing in loops
        for attempt in range(1, max_attempts + 1):
            logger.info(f"Attempt {attempt}/{max_attempts}")
            logger.info("-" * 40)
            
            try:
                response = self.creator_engine.llm_code_creator(prompt)
                logger.info(response)
                
                python_code, requirements = self.extract_python_code(response)
                success, stdout, stderr = self.save_and_execute_script(python_code, requirements)
                
                if success:
                    return True, python_code, requirements, attempt
                
                # If failed, get another prompt, keep trying.
                if attempt < max_attempts:
                    logger.info(f"Preparing to fix errors for attempt {attempt + 1}...")
                    error_info = f"STDOUT: {stdout}\nSTDERR: {stderr}"
                    prompt = self.create_fix_prompt(
                        prompt, 
                        python_code, 
                        error_info, 
                        )
                
            except Exception as e:
                logger.error(f"Unexpected error in attempt {attempt}: {e}")
                if attempt == max_attempts:
                    break
                continue
        
        logger.warning(f"FAILED: Could not generate working code after {max_attempts} attempts")
        return False, None, None, max_attempts

    def extract_python_code(self, text:str):
        """Extract Python code from Claude's response."""

        soup = BeautifulSoup(text, 'html.parser')
        code_tag = soup.find('python_code')
        requirements_tag = soup.find('requirements')
        
        code = code_tag.string
        requirements = requirements_tag.string
        
        return code, requirements

    def save_and_execute_script(self, code:str, requirements:str) -> Tuple[bool, str, str]:
        """
            Save the generated code to a file and execute it.

            Args:
                code(str): Code.
                requirements(str): Required libraries.
            Returns:
                (bool): Boolean that tells whether it fails or not.
                (str): STDOUT.
                (str): STDERROR.
        """
        try:
            python_file_name = "generated_script.py"
            requirement_file_name = "requirements.txt"
            
            with open(python_file_name, 'w') as f:
                f.write(code)
            logger.info(f"Script saved as: {python_file_name}")

            with open(requirement_file_name, 'w') as f:
                f.write(requirements)
            logger.info(f"Requirements saved as: {requirement_file_name}")
            
            if requirements.strip():
                logger.info("Installing necessary libraries...")
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", "-r", requirement_file_name]
                )

            logger.info("Generated script executing...")
            result = subprocess.run(
                [sys.executable, python_file_name],
                capture_output=True,
                text=True,
                timeout=300
                )

            if result.stdout:
                logger.info("Script Output:")
                logger.info(result.stdout)
            if result.stderr:
                logger.info("Script Errors:")
                logger.info(result.stderr)

            logger.info(f"{'='*60}")
            if result.returncode == 0:
                logger.info("Script executed successfully!")
                return True, result.stdout, result.stderr
            else:
                logger.warning(f"Script failed with exit code: {result.returncode}")
                return False, result.stdout, result.stderr

        except subprocess.TimeoutExpired:
            logger.error("Script execution timed out (300 seconds)")
            return False, "", "Script execution timed out"
        except KeyboardInterrupt:
            logger.error("Execution interrupted by user")
            return False, "", "Execution interrupted by user"
        except Exception as e:
            logger.error(f"Error executing script: {e}")
            return False, "", str(e)

    def create_fix_prompt(self, user_prompt, code, error_output):
        """Create a prompt to fix the failing code."""
        return f"""
The following Python code failed to execute properly. Please fix the issues and provide corrected code.

Original request: {user_prompt}

<errored_python_code>
{code}
</errored_python_code>

Error output:
{error_output}

Requirements:
- Fix all the errors shown above.
- Provide the fixed python code inside <python_code> block shown below.
- Provide the fixed requirements.txt under <requirements> block shown below, to include necessary python libraries.
- No need to give any explanations.  Simply fill python_code and requirements block below.

<python_code>
import ...
</python_code>

<requirements>
numpy
</requirements>
"""

    def python_template_func(self) -> str:
        return '''
\n
Do this with python code.
- Use html format and write python code inside <python_code> block shown below.
- Also, provide libraries to install in requirements.txt under <requirements> block. Use standard Python libraries when possible.
- Use the code snippet shown inside <python_code> block, but make necessary changes as indicated by the comment.
- You do not need to explain to me about the code.  You may just provide the code insinde <python_code> block.

<python_code>
import redshift_connector
import pandas as pd
import boto3
#import other necessary libaries

conn = redshift_connector.connect(
    host=f'llm-executor-db.{os.getenv('AWS_ACCOUNT_NUM')}.us-east-1.redshift-serverless.amazonaws.com',
    database='dev',
    user=os.getenv('REDSHIFT_USER'),
    password=os.getenv('REDSHIFT_PASSWORD'),
    port=5439
    )

# Relace SQL based on the prompt.
sql = """
...
"""

df = pd.read_sql(sql, conn)
conn.close()

# continue your code below.
...

# Finally, save whatever you think might be helpful such as image, model files, and etc in AWS s3 bucket.
s3 = boto3.client('s3')
bucket_name = "my-s3-for-kendra" # Make sure to use this bucket name.
local_file_path = f"/tmp/any_file_here.txt" #Replace whatever files you want to save.
s3_key = f"results/any_file_here.txt" 

s3.upload_file(Filename=local_file_path, Bucket=bucket_name, Key=s3_key)
</python_code>

<requirements>
numpy
...
</requirements>

'''

