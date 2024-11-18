import random
import json
import torch
from datetime import datetime, timedelta
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

bot_name = "ShopBot"
cart = {}
total_amount = 0.0
order_history = {}  # Stores completed orders for tracking

# Available items in the shop
order_items = {
    1: ("Wireless Bluetooth Earbuds", 29.99),
    2: ("Smartphone Stand with Adjustable Angle", 14.49),
    3: ("Portable Power Bank 10000mAh", 22.95),
    4: ("4K Ultra HD Streaming Stick", 39.99),
    5: ("Noise-Cancelling Over-Ear Headphones", 59.99)
}

# Function to handle orders based on item names or item numbers
def handle_order(msg):
    global total_amount
    words = msg.lower().split()
    item_num = None
    quantity = 1

    # Parse message for item number or quantity
    for word in words:
        if word.isdigit():
            if int(word) in order_items:
                item_num = int(word)
            else:
                quantity = int(word)
        elif word in [name.lower() for name, _ in order_items.values()]:
            for num, (name, price) in order_items.items():
                if word in name.lower():
                    item_num = num

    # Add the item to the cart
    if item_num is not None:
        item_name, price = order_items[item_num]
        if item_name in cart:
            cart[item_name]['quantity'] += quantity
        else:
            cart[item_name] = {'quantity': quantity, 'price': price}
        total_amount += price * quantity
        return f"Added {quantity} {item_name}(s) to your cart at ${price:.2f} each."
    return "Invalid item number or name. Please try again."

# Function to display the current cart summary
def display_cart():
    if not cart:
        return "Your cart is empty."
    cart_summary = "Your cart:\n"
    for item, details in cart.items():
        qty, price = details['quantity'], details['price']
        cart_summary += f"- {item}: {qty} x ${price:.2f} = ${qty * price:.2f}\n"
    cart_summary += f"Total Amount: ${total_amount:.2f}"
    return cart_summary

# Function to finalize the order
def finalize_order():
    global cart, total_amount
    if not cart:
        return "Your cart is empty."
    
    # Generate a unique order ID and set the delivery time
    order_id = f"ORD{random.randint(1000, 9999)}"
    delivery_time = datetime.now() + timedelta(days=3)

    # Save order details in order_history for future tracking
    order_history[order_id] = {
        "summary": display_cart(),  # Get the cart summary as the order summary
        "delivery_time": delivery_time.strftime('%Y-%m-%d %H:%M:%S')
    }

    # Create the final summary message
    summary = f"{order_history[order_id]['summary']}\n\nOrder ID: {order_id}\nExpected delivery by: {order_history[order_id]['delivery_time']}"
    
    # Clear the cart and reset the total amount after finalizing the order
    cart.clear()
    total_amount = 0.0
    return summary

# Function to track the order using an order ID
def track_order(order_id):
    """Provide delivery details if order ID exists."""
    if order_id in order_history:
        return f"Order ID: {order_id}\nExpected delivery by: {order_history[order_id]['delivery_time']}"
    return "Invalid order ID. Please check and try again."

# Main function to process user input and respond
def get_response(msg):
    # Tokenize and process user input
    sentence = tokenize(msg.lower())
    X = bag_of_words(sentence, all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X).to(device)

    # Get model output
    output = model(X)
    _, predicted = torch.max(output, dim=1)
    tag = tags[predicted.item()]
    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]

    if prob.item() > 0.65:
        for intent in intents['intents']:
            if fuzz.ratio(tag, intent["tag"]) > 75:
                if intent["tag"] == "item_list":
                    return random.choice(intent['responses'])
                elif intent["tag"] == "order_item":
                    return handle_order(msg)
                elif intent["tag"] == "display_cart":
                    return display_cart()
                elif intent["tag"] == "finalize_order":
                    return finalize_order()
                elif intent["tag"] == "order_status":
                    return "Please provide your order ID to check the status."
                elif any(word.startswith("ord") for word in msg.split()):
                    order_id = next((word for word in msg.split() if word.startswith("ord")), None)
                    if order_id:
                        return track_order(order_id)
                return random.choice(intent['responses'])
    return "I do not understand..."