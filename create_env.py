#!/usr/bin/env python
"""Create a proper .env file with the necessary configuration"""

with open('.env', 'w') as f:
    f.write('GOOGLE_API_KEY=AIzaSyDhgOyMyTKjMzSh01X0TIVUbrBiPWWIcS0\n')
    f.write('DEFAULT_MODEL=gemini-2.0-flash\n')

print("Created .env file with Google API key and model configuration") 