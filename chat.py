import random
import json
import torch
from fuzzywuzzy import fuzz
from model import NeuralNet
from nltk_utils import bag_of_words, tokenize

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Load intents and model data
with open('intents.json', 'r') as json_data:
    intents = json.load(json_data)

FILE = "data.pth"
data = torch.load(FILE)

input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data['all_words']
tags = data['tags']
model_state = data["model_state"]

model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()

bot_name = "Bot_14"
user_order = {}

def handle_order(msg):
    words = msg.lower().split()
    item = None
    quantity = 1  # Default quantity
    
    # Check for item keywords and quantities in the message
    for word in words:
        if word.isdigit():
            quantity = int(word)
        elif word in ["coffee", "tea", "cookies", "sandwich"]:
            item = word

    if item:
        user_order[item] = user_order.get(item, 0) + quantity
        return f"Added {quantity} {item}(s) to your order."
    else:
        return "I'm sorry, I couldn't understand the item. Please specify an item and quantity."


def get_response(msg):
    # Tokenize and process user input
    sentence = tokenize(msg.lower())  # Convert input to lowercase for case insensitivity
    X = bag_of_words(sentence, all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X).to(device)

    # Get model output
    output = model(X)
    _, predicted = torch.max(output, dim=1)
    tag = tags[predicted.item()]
    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]

    # Apply threshold and fuzzy matching
    if prob.item() > 0.65:  # Lowered threshold for more flexible matching
        for intent in intents['intents']:
            # Fuzzy match the predicted tag to the intent tag
            if fuzz.ratio(tag, intent["tag"]) > 75:  # Fuzzy match threshold
                # Check if the intent is 'order' and handle ordering
                if intent["tag"] == "order":
                    return handle_order(msg)
                return random.choice(intent['responses'])
    
    return "I do not understand..."
