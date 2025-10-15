import sheetsapi
import time
from pathlib import Path
from prompt_writer import fill_dict_with_list, fill_template_with_dict, get_most_recent_txt
from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv
from datetime import datetime

FOLDER_ID = '1gRMBVvVi7UV-If32wEjx1TGax3BqrFSK'
CREDENTIALS_PATH = 'C:\\Users\\Baron\\Downloads\\modern-venture-474620-a8-f4fa5868355c.json'
SHEET_NAME = "Product Evaluation (Part 1) (Responses)"

TEMPLATE_PATH = Path(r"C:\Users\Baron\Documents\Luna Labs Agent\SupportFiles\prompt_outline.txt")
PROMPT_PATH = Path(r"C:\Users\Baron\Documents\Luna Labs Agent\PromptFiles")
RESPONSE_FOLDER = Path(r"C:\Users\Baron\Documents\Luna Labs Agent\ResponseFiles")


most_recent_row = 1

form_keys_template = {
    "sys_prompt": None,
    "solution_name": None,
    "addressed_problem": None,
    "init_customer": None,
    "current_solution": None,
    "your_solution_description": None,
    "primary_market_sector": None,
    "market_geographic_focus": None,
    "known_competitors" : None,
    "primary_expected_business_model": None,
    "secondary_expected_business_model": None,
    "projected_revenue": None,
    "solution_stage": None,
    "paying_customers": None,
    "pilot_poc_count": None,
    "total_funding_td": None,
    "monthly_burn_active": None,
    "monthly_burn_inactive": None,
    "transferring_team_members" : None,
    "solution_type": None,
    "known_supply_chain_requirements": None,
    "ip_status": None,
    "evaluator_persona": None
}

sheet, drive_service = sheetsapi.init_google_services(CREDENTIALS_PATH, SHEET_NAME)

load_dotenv()

llm = ChatAnthropic(
    model="claude-opus-4-20250514",
    max_tokens=5_000  # 2x the capacity
)

while True: 
    try:

        if not sheetsapi.is_row_empty(most_recent_row + 1, sheet):
            sheet_values = sheetsapi.get_row_vals(most_recent_row + 1, sheet)

            filled_dict = fill_dict_with_list(form_keys_template.copy(), sheet_values)

            # Create file with prefix "filled"
            fill_template_with_dict(TEMPLATE_PATH, filled_dict, PROMPT_PATH, "filled")
            # Creates: filled_20250414_153022.txt

            # Search for files starting with "filled_"
            most_recent_prompt = get_most_recent_txt(PROMPT_PATH, "filled_*")
            prompt_content = most_recent_prompt.read_text(encoding="utf-8")
            # Finds: filled_20250414_153022.txt

            response = llm.invoke(prompt_content)  # Change from most_recent_prompt to prompt_content

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"claude_response_{timestamp}.txt"

            output_path = RESPONSE_FOLDER / output_filename

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(response.content)

            #sheetsapi.upload_txt_to_drive(drive_service, output_path, FOLDER_ID)

            most_recent_row += 1


        time.sleep(120)

    except KeyboardInterrupt:
        print("\n Script stopped by user")
        break