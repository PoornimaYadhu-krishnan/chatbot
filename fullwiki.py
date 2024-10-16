from quart import Quart, request, Response, jsonify
import openai
import requests
from bs4 import BeautifulSoup
import re
import logging
import spacy

# Initialize the spaCy NLP model
nlp = spacy.load("en_core_web_sm")

# Initialize Quart app
app = Quart(__name__)



# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Global variable to store chat history
chat_history = []

# Function to fetch Wikipedia content
def fetch_wikipedia_content(title):
    url = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        content_div = soup.find('div', class_='mw-parser-output')

        if content_div:
            remove_tags = ['sup', 'table', 'style', 'script', 'noscript', 'span', 'div', 'hr', 'tr']
            for tag in remove_tags:
                for match in content_div.findAll(tag):
                    match.decompose()

            text = re.sub(r'\[\d+\]', '', content_div.text)  # Remove reference numbers
            text = re.sub(r'\[citation needed\]', '', text)  # Remove citation needed tags
            text = re.sub(r'\n{2,}', '\n', text).strip()  # Normalize newlines

            return text
        else:
            return f"Failed to extract content from Wikipedia page: {url}"
    else:
        return f"Failed to fetch Wikipedia page: {url}"

# Function to search Wikipedia
def search_wikipedia(query):
    search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={query}&format=json&utf8=1"
    response = requests.get(search_url)
    if response.status_code == 200:
        search_results = response.json().get("query", {}).get("search", [])
        titles = [result['title'] for result in search_results]
        logging.debug(titles)
        return titles
    else:
        logging.error("Failed to search Wikipedia.")
        return []

# Function to extract keywords using spaCy
def extract_keywords(query):
    doc = nlp(query)
    keywords = [token.text for token in doc if token.is_alpha and not token.is_stop]
    return keywords

# Function to check relevance of a title based on the user query
def is_relevant(title, user_query):
    title_lower = title.lower()
    query_lower = user_query.lower()
    keywords = re.findall(r'\b\w+\b', query_lower)  # Extract words from the query
    return any(keyword in title_lower for keyword in keywords)

# Function to generate response using OpenAI GPT-3
def generate_response(user_query):
    # Extract keywords from the user query
    keywords = extract_keywords(user_query)
    logging.debug(f"Extracted keywords: {keywords}")

    # Search for relevant Wikipedia articles
    wiki_titles = search_wikipedia(user_query)

    # Filter relevant titles
    relevant_titles = [title for title in wiki_titles if is_relevant(title, user_query)]
    logging.debug(f"Relevant titles: {relevant_titles}")

    # If no relevant titles are found, return a message
    if not relevant_titles:
        return "Sorry, I couldn't find any relevant articles on Wikipedia for your query."

    wiki_texts = []
    token_limit = 3800  # Set a token limit that leaves room for the response

    for title in relevant_titles:
        wiki_text = fetch_wikipedia_content(title)
        if wiki_text:
            combined_text_length = sum(len(text) for text in wiki_texts) + len(wiki_text)
            if combined_text_length < token_limit:
                wiki_texts.append(wiki_text)
            else:
                break  # Stop if token limit is exceeded

    # Construct the messages for the chat history, including relevant wiki content
    messages = [{"role": "user", "content": user_query}]

    if wiki_texts:
        combined_wiki_text = "\n\n".join(wiki_texts)  # Combine all wiki texts
        messages.append({"role": "assistant", "content": combined_wiki_text})  # Add Wikipedia content to the context

    # Generate the assistant's response
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=150  # Adjust max tokens for the response
        )
        if response.choices and response.choices[0].message["content"]:
            assistant_response = response.choices[0].message["content"].strip()
            # Store both user query and assistant response in chat history
            chat_history.append({"role": "user", "content": user_query})
            chat_history.append({"role": "assistant", "content": assistant_response})

            return assistant_response
        else:
            logging.error("Empty or invalid response from OpenAI.")
            return "Sorry, I couldn't generate a response at the moment."

    except Exception as e:
        logging.error(f"Error generating response from OpenAI: {str(e)}")
        return "Sorry, I encountered an error and couldn't process your request."


# Endpoint to handle incoming messages
@app.route("/api/messages", methods=["POST"])
async def messages():
    if "application/json" in request.headers["Content-Type"]:
        body = await request.json
    else:
        return Response(status=415)

    logging.debug(f"Incoming request body: {body}")

    try:
        user_query = body.get("text", "")

        # Generate response
        response_text = generate_response(user_query)

        # Return the response in JSON format
        return Response(response_text, status=200, mimetype='application/json')

    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return Response(status=400, response="Invalid request")

# Endpoint to retrieve chat history
@app.route("/api/chat_history", methods=["GET"])
async def chat_history_endpoint():
    return jsonify({"history": chat_history}), 200

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    app.run(port=3978)
