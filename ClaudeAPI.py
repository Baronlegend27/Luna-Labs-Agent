from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime
from prompt_writer import get_most_recent_txt


load_dotenv()

PROMPT_FOLDER = Path(r"C:\Users\Baron\Documents\Luna Labs Agent\PromptFiles")
RESPONSE_FOLDER = Path(r"C:\Users\Baron\Documents\Luna Labs Agent\ResponseFiles")


# Get the most recent filled prompt file
most_recent_prompt = get_most_recent_txt(
    PROMPT_FOLDER, 
    pattern="filledprompt_*"
)

filled_prompt_form = most_recent_prompt.read_text()


llm = ChatAnthropic(model="claude-sonnet-4-5-20250929")


with open(filled_prompt_form, "r", encoding="utf-8") as f:
    file_content = f.read()


response = llm.invoke(file_content)

# Create timestamp for unique filename
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_filename = f"claude_response_{timestamp}.txt"

output_path = RESPONSE_FOLDER / output_filename

# Save response
with open(output_path, "w", encoding="utf-8") as f:
    f.write(response.content)
