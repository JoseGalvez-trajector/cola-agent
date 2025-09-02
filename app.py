
from strands import Agent
from strands.models import BedrockModel
from strands.agent.agent import null_callback_handler
from tools import find_va_rate_info, check_va_rate_changes

model = BedrockModel(
    model_id="amazon.nova-lite-v1:0", 
    temperature=0.7,
    max_tokens=1000
)

agent = Agent(
    model=model, 
    tools=[find_va_rate_info, check_va_rate_changes],
    system_prompt="""
You are a helpful assistant that helps users find information about VA disability rates.
You have access to tools that can:
1. Find the Year, Dependent Status, and Rating for a specific dollar amount
2. Check VA rate changes between two amounts and identify COLA adjustments

IMPORTANT: Provide clear, concise responses without redundant information. Do not repeat yourself or show internal thinking processes. Give direct, helpful answers using the available tools.
"""
)

if __name__ == "__main__":
    print("\n Ask me anything.\n")

    # Run the agent in a loop for interactive conversation
    while True:
        user_input = input("\nYou > ")
        if user_input.lower() == "exit":
            print("Have a great day!")
            break
        response = agent(user_input)
    
