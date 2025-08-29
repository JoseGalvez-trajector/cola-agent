
from strands import Agent, tool
from strands_tools import calculator, current_time
from strands.models import BedrockModel
import pandas as pd
import os

# Create a Bedrock model instance with Amazon Nova Lite
model = BedrockModel(
    model_id="amazon.nova-lite-v1:0",  # Amazon Nova Lite model ID
    temperature=0.7,
    max_tokens=1000
)

@tool
def va_cola_lookup(rating: str, dependent_status: str) -> str:
    """
    Look up VA COLA rates from the CSV file based on rating and dependent status.
    
    Args:
        rating: The disability rating (e.g., "30%", "40%", "50%", "60%", "70%", "80%", "90%", "100%")
        dependent_status: The dependent status (e.g., "Veteran alone (no dependents)", "With spouse (no dependents)")
    
    Returns:
        The monthly COLA rate for the specified rating and dependent status
    """
    try:
        # Read the CSV file with proper handling of commas in text fields
        csv_path = os.path.join("docs", "va_cola_rates.csv")
        
        # Read the file manually to handle the comma issue
        with open(csv_path, 'r') as file:
            lines = file.readlines()
        
        # Parse the header
        header = lines[0].strip().split(',')
        
        # Find the rating column index
        rating_col_idx = None
        for i, col in enumerate(header):
            if rating in col:
                rating_col_idx = i
                break
        
        if rating_col_idx is None:
            return f"Invalid rating: {rating}. Valid ratings are: {', '.join([col for col in header if '%' in col])}"
        
        # Search for the dependent status
        found_rate = None
        for line in lines[1:]:  # Skip header
            line = line.strip()
            if not line:
                continue
                
            # Split by comma, but be careful with commas in the dependent status
            parts = line.split(',')
            
            # The dependent status is in the second column (index 1)
            if len(parts) > 1:
                # Handle cases where dependent status might contain commas
                if dependent_status in parts[1]:
                    # Check if we have enough columns for the rating
                    if len(parts) > rating_col_idx:
                        rate_str = parts[rating_col_idx].strip()
                        if rate_str and rate_str != '':
                            try:
                                found_rate = float(rate_str)
                                break
                            except ValueError:
                                continue
        
        if found_rate is None:
            return f"No rate available for {rating} with {dependent_status}"
        
        return f"VA COLA Rate for {rating} with {dependent_status}: ${found_rate:,.2f} per month"
        
    except Exception as e:
        return f"Error looking up VA COLA rate: {str(e)}"

# Create an agent with tools from the community-driven strands-tools package
# as well as our custom letter_counter tool
agent = Agent( model=model, tools=[calculator, current_time, va_cola_lookup])

# Ask the agent a question that uses the available tools
message = """
What is the VA COLA rate for 30% disability with "With spouse (no dependents)"?
"""
agent(message)