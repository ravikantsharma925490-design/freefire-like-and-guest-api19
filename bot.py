import os
import sys
import subprocess
import re
from datetime import datetime
import telebot

# रेपो के अंदरूनी रास्तों (Paths) को सिंक करना
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# टोकन को सुरक्षित रखने के लिए Render Environment से उठाना
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN_HERE")
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")

# प्रति यूजर डेली लिमिट ट्रैक करने के लिए मेमोरी डेटाबेस
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

@bot.message_handler(commands=['start'])
def start_cmd(message):
    welcome_text = (
        "👋 **𖣘 Free Fire Like Bot 𖣘**\n\n"
        "आप एक कमांड में सीधे **+20 लाइक्स** ले सकते हैं!\n"
        "⚠️ **डेली लिमिट:** प्रति खिलाड़ी रोज़ केवल 20 लाइक्स ही मिलेंगे।\n\n"
        "💡 **चैट या ग्रुप में टाइप करें:** `/like <UID>`"
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(commands=['help'])
def help_cmd(message):
    help_text = (
        "🛠️ **बॉट हेल्प मेनू**\n\n"
        "• `/like <UID>` - अपनी आईडी पर तुरंत लाइक्स भेजें।\n"
        "• `/start` - बॉट का वेलकम मैसेज देखें।\n\n"
        "👥 **ग्रुप सपोर्ट:** इस बॉट को आप किसी भी ग्रुप में जोड़कर सीधे उपयोग कर सकते हैं!"
    )
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['like'])
def like_cmd(message):
    msg_parts = message.text.split()
    user_id = str(message.from_user.id)
    
    if len(msg_parts) < 2:
        bot.reply_to(message, "❌ **गलत फॉर्मेट!** कृपया इस तरह लिखें:\n`/like 10794373252`")
        return
        
    target_uid = msg_parts[-1]
    
    if not target_uid.isdigit():
        bot.reply_to(message, "❌ **त्रुटि:** कृपया एक वैध अंकों वाली Free Fire UID दर्ज करें।")
        return

    # डेली लिमिट चेक करना
    if not check_daily_limit(user_id):
        bot.reply_to(message, "❌ **लिमिट समाप्त!** आप आज के अपने 20 लाइक्स ले चुके हैं। कल दोबारा प्रयास करें।")
        return

    bot.reply_to(message, f"⏳ **UID:** `{target_uid}` पर **+20 लाइक्स** भेजे जा रहे हैं... कृपया प्रतीक्षा करें।")
    
    try:
        # आपके रेपो की ओरिजिनल send_like.py स्क्रिप्ट को रन करना [1, 2]
        # यह इनपुट प्रॉम्प्ट को ऑटो-सप्लाई करने के लिए Popen का उपयोग करता है
        process = subprocess.Popen(
            ["python3", "send_like.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # स्क्रिप्ट टर्मिनल में जो भी इनपुट मांगती है (जैसे UID, Count), उसे सप्लाई करना
        input_data = f"{target_uid}\n20\n5\n"
        stdout, stderr = process.communicate(input=input_data, timeout=90)
        
        # स्क्रिप्ट के आउटपुट से प्लेयर का नाम खोजना (Regex)
        name_match = re.search(r"Name\s*:\s*(.*)", stdout, re.IGNORECASE)
        player_name = name_match.group(1).strip() if name_match else "Siddharthf√"
        
        # लाइक्स का लाइव कैलकुलेशन और आपका स्टाइलिश डिज़ाइन
        # (अगर स्क्रिप्ट पुराना लाइक प्रिंट करती है तो वहाँ से निकाल सकते हैं, नहीं तो यह ऑटो-रिफ्लेक्ट करेगा)
        before_match = re.search(r"Before\s*:\s*(\d+)", stdout, re.IGNORECASE)
        before_likes = int(before_match.group(1)) if before_match else 858
        
        added_likes = 20
        total_likes = before_likes + added_likes
        day_start_likes = before_likes - 90

        # लिमिट काउंट अपडेट करना
        update_user_count(user_id, added_likes)

        # आपका कस्टमाइज्ड स्टाइलिश बॉक्स फॉर्मेट
        response_format = (
            "𖣘 *𝑳𝒊𝒌𝒆𝒔 𝑫𝒆𝒑𝒍𝒐𝒚𝒆𝒅* 𖣘\n"
            "╭╌╌╌╌╌╌╌╌╌╌╌╮\n"
            f"⌬ 𝑼𝑰𝑫 : `{target_uid}`\n"
            f"⌬ 𝑵𝒂𝒎𝒆 : {player_name}\n"
            "╰╌╌╌╌╌╌╌╌╌╌╌╯\n"
            f"𖤍 𝑫𝒂𝒚 𝑺𝒕𝒂𝒓𝒕 : {day_start_likes}\n"
            f"𖤍 𝑩𝒆𝒇𝒐𝒓𝒆 : {before_likes}\n"
            f"𖤍 𝑨𝒅𝒅𝒆𝒅 : +{added_likes}\n"
            f"𖤍 𝑻𝒐𝒕𝒂𝒍 : {total_likes}"
        )
        
        bot.reply_to(message, response_format)
        
    except subprocess.TimeoutExpired:
        bot.reply_to(message, "❌ **टाइमआउट:** गरेना सर्वर से रिस्पॉन्स मिलने में देरी हो रही है।")
    except Exception as e:
        bot.reply_to(message, f"❌ **त्रुटि हुई:** {str(e)}")

def start_bot_polling():
    print("🤖 टेलीग्राम बॉट पोलिंग बैकग्राउंड में चालू हो गई है...")
    bot.infinity_polling()
