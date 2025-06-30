import os, sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

from prompts import system_prompt
from call_function import available_functions, call_function
from config import MAX_RESPONSES


def main():
    load_dotenv()

    verbose = "--verbose" in sys.argv
    args = [arg for arg in sys.argv[1:] if not arg.startswith("--")]

    if not args:
        print("Usage: uv run main.py <prompt>")
        sys.exit(1)

    user_prompt = " ".join(args)

    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    
    if verbose:
        print(f"User prompt: {user_prompt}")
    
    #chat log for LLM to go through
    messages = [
        types.Content(role="user", parts=[types.Part(text=user_prompt)]),
    ]

    count = 0
    while True:
        count += 1
        if count > MAX_RESPONSES:
            print(f"max responses generated ({MAX_RESPONSES}). exiting")
            sys.exit(1)
        
        try:
            final_response = generate_response(client, messages, verbose)
            if final_response:
                print("final response:")
                print(final_response)
                break
        except Exception as e:
            print(f"Error in generate_content: {e}")


def generate_response(client, messages, verbose):

    response = client.models.generate_content(
        model = 'gemini-2.0-flash-001', 
        contents = messages,
        config=types.GenerateContentConfig(
            tools=[available_functions],
            system_instruction=system_prompt
        )
    )
   
    #adds user msgs to history
    if response.candidates:
        for candidate in response.candidates:
            messages.append(candidate.content)

    #if no function calls, return gemini response
    if not response.function_calls:
        return response.text
    
    function_responses = [] #stores all function call results
    for function_call_part in response.function_calls:
        function_call_result = call_function(function_call_part, verbose)
        if (
            not function_call_result.parts or not function_call_result.parts[0].function_response
        ):
            raise Exception("Empty function call result")
        if verbose:
            print(f'-> {function_call_result.parts[0].function_response.response["result"]}')
        function_responses.append(function_call_result.parts[0])

    if not function_responses: #function called but no response....
        raise Exception("No function responses generated, exiting.")
    
    messages.append(types.Content(role="tool", parts=function_responses)) #add function result to history
    
    if verbose:
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
    
 


if __name__ == "__main__":
    main()

    