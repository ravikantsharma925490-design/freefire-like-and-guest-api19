import os
import threading
from flask import Flask
from bot import start_bot_polling  # bot.py से फंक्शन इम्पोर्ट किया

app = Flask(__name__)

@app.route('/')
def home():
    return "<h1>Free Fire Advanced Like Bot Server is Online 24/7!</h1>"

if __name__ == "__main__":
    # बॉट को एक अलग थ्रेड (रास्ते) पर चलाना ताकि वेब सर्वर ब्लॉक न हो
    bot_thread = threading.Thread(target=start_bot_polling)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Render क्लाउड सर्वर का पोर्ट असाइन करना
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
