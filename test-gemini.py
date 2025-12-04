import os
from dotenv import load_dotenv
from google import genai
# Add this for debugging
import google.genai
print(f"📦 SDK Location: {google.genai.__file__}")
print(f"📦 SDK Version: {getattr(google.genai, '__version__', 'Unknown')}")
# 1. Load Environment Variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

def test_gemini_connection():
    print("--- Gemini File Search Connection Test ---\n")

    # Check if Key Exists
    if not api_key:
        print("❌ Error: GEMINI_API_KEY not found in environment variables.")
        print("   Make sure you have a .env file with GEMINI_API_KEY=your_key")
        return

    print(f"✅ Found API Key: {api_key[:5]}...{api_key[-4:]}")

    try:
        # 2. Initialize Client with v1beta (THE CRITICAL FIX)
        print("🔄 Initializing Client with api_version='v1beta'...")
        
        client = genai.Client(
            api_key=api_key,
            http_options={'api_version': 'v1beta'} # This enables File Search
        )
        
        # 3. Test Access to file_search_stores
        # We will try to list stores. If the attribute is missing, this lines fails.
        print("📡 Attempting to list existing File Search Stores...")
        
        pager = client.file_search_stores.list()
        
        # Convert pager to list to count items
        stores = list(pager)
        
        print(f"✅ Success! Connection established.")
        print(f"   Found {len(stores)} existing store(s).")
        
        for store in stores:
            print(f"   - Store: {store.display_name} ({store.name})")

    except AttributeError as e:
        print(f"\n❌ AttributeError: {e}")
        print("   This usually means the client isn't targeting 'v1beta'.")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")

if __name__ == "__main__":
    test_gemini_connection()