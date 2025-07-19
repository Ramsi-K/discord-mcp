import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Clear any problematic SSL environment variables
if "SSL_CERT_FILE" in os.environ:
    print(f"Removing problematic SSL_CERT_FILE: {os.environ['SSL_CERT_FILE']}")
    del os.environ["SSL_CERT_FILE"]

if "SSL_CERT_DIR" in os.environ:
    print(f"Removing problematic SSL_CERT_DIR: {os.environ['SSL_CERT_DIR']}")
    del os.environ["SSL_CERT_DIR"]

# Try importing and initializing Anthropic
try:
    from anthropic import Anthropic

    print("Successfully imported Anthropic")

    # Try initializing the client
    client = Anthropic()
    print("Successfully initialized Anthropic client")

    # Print API key status (not the actual key)
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if api_key:
        print("ANTHROPIC_API_KEY is set")
    else:
        print("ANTHROPIC_API_KEY is not set")

except Exception as e:
    print(f"Error: {e}")
    print(f"Error type: {type(e)}")
    import traceback

    traceback.print_exc()

print("Environment variables:")
for key, value in os.environ.items():
    if "SSL" in key or "CERT" in key:
        print(f"{key}: {value}")
