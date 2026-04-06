from google import genai

client = genai.Client(api_key="AIzaSyAzK9NGRsInb_o4TPu5gitqjsiA-Eu8R3U")

response = client.models.generate_content(
    model="gemini-1.5-pro",
    contents="What is Ohm's law?"
)

print(response.text)