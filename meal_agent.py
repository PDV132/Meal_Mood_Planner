from langchain.prompts import PromptTemplate
from langchain_openai import OpenAI
import os

# Make sure you set your API key as an environment variable
if "OPENAI_API_KEY" not in os.environ:
    raise ValueError("OPENAI_API_KEY environment variable not set.")

# Prompt template for LangChain
prompt_template = PromptTemplate.from_template("""
You are a kind and knowledgeable wellness coach.

The user is feeling {mood_1} and {mood_2}.
You recommend a meal called "{meal}" with {calories} calories.

**Reason for recommendation**: {reason}
**Health benefit**: {benefit}

Now write a friendly explanation to the user about how this meal can help their current mood and promote emotional balance.
Use simple, encouraging language.
""")

# LangChain LLM wrapper (uses OpenAI under the hood)
llm = OpenAI(temperature=0.7)

def explain_meal(mood_1, mood_2, meal):
    prompt = prompt_template.format(
        mood_1=mood_1,
        mood_2=mood_2,
        meal=meal["meal_name"],
        calories=meal["calories"],
        reason=meal["reason"],
        benefit=meal["benefit"]
    )

    return llm(prompt)



