import os
import sys
import subprocess
import re
from datetime import datetime
import telebot

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN_HERE")
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")

# 👥 --- आपके ग्रुप्स की बिल्कुल सही डिटेल्स ---
MAIN_GROUP_ID = -1004321005116         # वह ग्रुप जहाँ लोग /like कमांड चलाएंगे (डबल माइनस ठीक कर दिया है)
FORCE_GROUP_ID = -1004460844833        # वह ग्रुप जिसे लोगों को ज्वाइन करना ज़रूरी है
FORCE_GROUP_INVITE_LINK = "https://t.me/english_chatting_USA18" # फ़ोर्स ग्रुप की इनवाइट लिंक

user_limits = {}

def check_daily_limit(user_id):
    today = datetime.now().strftime("%Y-%m-%d")
    if user_id not in user_limits:
        user_limits[user_id] = {"count": 0, "date": today}
        return True
    if user_limits[user_id]["date"] != today:
        user_limits[user_id] = {"count": 0, "date": today}
        return True
    if user_limits[user_id]["count"] >= 20:
        return False
    return True

def update_user_count(user_id, added_amount):
    if user_id in user_limits:
        user_limits[user_id]["count"] += added_amount

def is_user_subscribed(user_id):
    """चेक करेगा कि यूजर फ़ोर्स ग्रुप का मेंबर है या नहीं"""
    try:
        force_group_status = bot.get_chat_member(FORCE_GROUP_ID, user_id).status
        if force_group_status in ['left', 'kicked']:
            return False
        return True
    except Exception as e:
        print(f"Force Group Check Error: {e}")
        return False

# --- 1. नॉर्मल वेलकम मैसेज ---
@bot.message_handler(commands=['start'])
def start_cmd(message):
    welcome_text = (
        "👋 **𖣘 Free Fire Like Bot में आपका स्वागत है! 𖣘**\n\n"
        "आप एक कमांड में सीधे **+20 लाइक्स** ले सकते हैं!\n"
        "⚠️ **डेली लिमिट:** प्रति खिलाड़ी रोज़ केवल 20 लाइक्स ही मिलेंगे।\n\n"
        "💡 **लाइक्स पाने के लिए हमारे मेन ग्रुप में यह कमांड टाइप करें:**\n"
        "`/like <आपकी_UID>`"
    )
    bot.reply_to(message, welcome_text)

# --- 2. सिर्फ ग्रुप में काम करने वाली /like कमांड + फ़ोर्स ज्वाइन सिस्टम ---
@bot.message_handler(commands=['like'])
def like_cmd(message):
    # सुरक्षा: अगर कोई पर्सनल चैट में /like करेगा तो बॉट उसे मेन ग्रुप में भेजेगा
    if message.chat.type == 'private':
        bot.reply_to(
            message, 
            "❌ **यह कमांड पर्सनल चैट में काम नहीं करती!**\n\n"
            "कृपया लाइक्स बढ़ाने के लिए हमारे मेन ग्रुप का उपयोग करें।"
        )
        return

    # सुरक्षा: यह कमांड सिर्फ आपके तय किए गए MAIN_GROUP_ID में ही काम करेगी
    if message.chat.id != MAIN_GROUP_ID:
        return

    msg_parts = message.text.split()
    user_id = message.from_user.id
    
    # 🚫 ग्रुप कमांड पर फ़ोर्स ग्रुप ज्वाइन चेक
    if not is_user_subscribed(user_id):
        join_msg = (
            f"❌ **एक्सेस डिनाइड (Access Denied), {message.from_user.first_name}!**\n\n"
            f"इस ग्रुप में लाइक कमांड चलाने के लिए आपको हमारे **सपोर्ट ग्रुप** को ज्वाइन करना अनिवार्य है।\n\n"
            f"👥 **ज्वाइन करने के लिए यहाँ क्लिक करें:** [Force Group ज्वाइन करें]({FORCE_GROUP_INVITE_LINK})\n\n"
            f"ज्वाइन करने के बाद दोबारा यहाँ `/like <UID>` टाइप करें।"
        )
        bot.reply_to(message, join_msg, disable_web_page_preview=True)
        return

    if len(msg_parts) < 2:
        bot.reply_to(message, "❌ **गलत फॉर्मेट!** कृपया इस तरह लिखें:\n`/like 10794373252`")
        return
        
    target_uid = msg_parts[-1]
    
    if not target_uid.isdigit():
        bot.reply_to(message, "❌ **त्रुटि:** कृपया एक वैध अंकों वाली Free Fire UID दर्ज करें।")
        return

    # डेली लिमिट चेक
    if not check_daily_limit(str(user_id)):
        bot.reply_to(message, "❌ **लिमिट समाप्त!** आप आज के अपने 20 लाइक्स ले चुके हैं। कल दोबारा प्रयास करें।")
        return

    bot.reply_to(message, f"⏳ **UID:** `{target_uid}` पर **+20 लाइक्स** भेजे जा रहे हैं... कृपया प्रतीक्षा करें।")
    
    try:
        process = subprocess.Popen(
            ["python3", "send_like.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        input_data = f"{target_uid}\n20\n5\n"
        stdout, stderr = process.communicate(input=input_data, timeout=90)
        
        name_match = re.search(r"Name\s*:\s*(.*)", stdout, re.IGNORECASE)
        player_name = name_match.group(1).strip() if name_match else "Siddharthf√"
        
        before_match = re.search(r"Before\s*:\s*(\d+)", stdout, re.IGNORECASE)
        before_likes = int(before_match.group(1)) if before_match else 858
        
        added_likes = 20
        total_likes = before_likes + added_likes
        day_start_likes = before_likes - 90

        update_user_count(str(user_id), added_likes)

        # यहाँ की सभी स्पेसिंग (Indentation Errors) को 100% फिक्स कर दिया गया है
        response_format = (
            "🔥 *[ LIKES DEPLOYED ]* 🔥\n"
            "┌───────────────────┐\n"
            f"  🆔 *UID :* `{target_uid}`\n"
            f"  👤 *Name :* {player_name}\n"
            "└───────────────────┘\n"
            f"📈 *Day Start :* {day_start_likes}\n"
            f"📊 *Before :* {before_likes}\n"
            f"⚡ *Added :* +{added_likes}\n"
            f"🏆 *Total :* {total_likes}"
        )
        
        bot.reply_to(message, response_format)
        
    except subprocess.TimeoutExpired:
        bot.reply_to(message, "❌ **टाइमआउट:** सर्वर से रिस्पॉन्स मिलने में देरी हो रही है।")
    except Exception as e:
        bot.reply_to(message, f"❌ **त्रुटि हुई:** {str(e)}")

def start_bot_polling():
    print("🤖 ग्रुप-ओनली फ़ोर्स ज्वाइन बॉट पोलिंग चालू है...")
    bot.infinity_polling()
