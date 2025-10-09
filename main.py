import os
from dotenv import load_dotenv

def main():
    # Load environment variables from .env file
    load_dotenv()
    
    print("Hello from my-project-05!")
    
    # Example: Reading environment variables
    # api_key = os.getenv('API_KEY')
    # debug = os.getenv('DEBUG', 'False')
    # print(f"API Key: {api_key}")
    # print(f"Debug mode: {debug}")


if __name__ == "__main__":
    main()
