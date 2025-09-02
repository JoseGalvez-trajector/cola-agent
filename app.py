
from strands import Agent
from strands.models import BedrockModel
from tools import find_va_rate_info, check_va_rate_changes

# Create a Bedrock model instance with Amazon Nova Lite
model = BedrockModel(
    model_id="amazon.nova-lite-v1:0",  # Amazon Nova Lite model ID
    temperature=0.7,
    max_tokens=1000
)

# Create an agent with both tools
agent = Agent(
    model=model, 
    tools=[find_va_rate_info, check_va_rate_changes],
    system_prompt="""
You are a helpful assistant that helps users find information about VA disability rates.
You have access to tools that can:
1. Find the Year, Dependent Status, and Rating for a specific dollar amount
2. Check VA rate changes between two amounts and identify COLA adjustments
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
        # print(f"\nAgent > {response}")

# response = agent(message)
# print(response)



# # Ask the agent a question that uses the available tools
# message = """
# I have 1 request:

# 1. Find the Year, Dependent Status, and Rating for $1,659.95
# """

# response = agent(message)
# print(response)