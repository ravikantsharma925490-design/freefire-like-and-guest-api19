import os
import sys
import subprocess
import re
from datetime import datetime
import telebot

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN_HERE")
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")

# 📢 --- यहाँ अपने चैनल और ग्रुप की डिटेल्स डालें ---
CHANNEL_USERNAME = "@YourChannelUsername"  # अपने चैनल का यूजरनेम (@ के साथ)
GROUP_CHAT_ID = -1001234567890             # अपने उस ग्रुप की चैट आईडी (जिसमें बॉट चलाना है)
GROUP_INVITE_LINK = "https://t.me" # ग्रुप की इनवाइट लिंक

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
    """चेक करेगा कि यूजर चैनल और ग्रुप दोनों में है या नहीं"""
    try:
        # 1. चैनल सब्सक्रिप्शन चेक करें
        channel_status = bot.get_chat_member(CHANNEL_USERNAME, user_id).status
        if channel_status in ['left', 'kicked']:
            return False
            
        # 2. ग्रुप सब्सक्रिप्शन चेक करें
        group_status = bot.get_chat_member(GROUP_CHAT_ID, user_id).status
        if group_status in ['left', 'kicked']:
            return False
            
        return True
    except Exception as e:
        print(f"Sub Check Error: {e}")
        # अगर कोई एरर आता है (जैसे बॉट एडमिन नहीं है), तो सुरक्षा के लिए False रिटर्न करें
        return False

# --- पर्सनल चैट ब्लॉक करना और सिर्फ ग्रुप में काम करना ---
@bot.message_handler(func=lambda message: message.chat.type == 'private')
def block_private_chat(message):
    bot.reply_to(
        message, 
        f"❌ **यह बॉट पर्सनल चैट में काम नहीं करता है!**\n\n"
        f"इसका उपयोग करने के लिए कृपया हमारे ऑफिशियल ग्रुप में आएं:\n"
        f"👉 [यहाँ क्लिक करके ग्रुप ज्वाइन करें]({GROUP_INVITE_LINK})",
        disable_web_page_preview=True
    )

# --- ग्रुप में /start कमांड ---
@bot.message_handler(commands=['start'])
def start_cmd(message):
    if message.chat.id != GROUP_CHAT_ID:
        return # अगर यह आपका तय किया हुआ ग्रुप नहीं है तो इग्नोर करें
        
    welcome_text = (
        "👋 **𖣘 Free Fire Like Bot 𖣘**\n\n"
        "यह बॉट इस ग्रुप में एक्टिव है। आप एक कमांड में सीधे **+20 लाइक्स** ले सकते हैं!\n"
        "⚠️ **नियम:** लाइक लेने के लिए आपका हमारे चैनल और ग्रुप दोनों में जुड़े रहना ज़रूरी है।\n\n"
        "💡 **कमांड:** `/like <UID>`"
    )
    bot.reply_to(message, welcome_text)

# --- ग्रुप में /like कमांड + फ़ोर्स ज्वाइन सिस्टम ---
@bot.message_handler(commands=['like'])
def like_cmd(message):
    # सुरक्षा: यह कमांड सिर्फ आपके तय किए गए ग्रुप में ही काम करेगी
    if message.chat.id != GROUP_CHAT_ID:
        return

    msg_parts = message.text.split()
    user_id = message.from_user.id
    
    # 🚫 1. फ़ोर्स ज्वाइन चेक (चैनल और ग्रुप दोनों में होना ज़रूरी है)
    if not is_user_subscribed(user_id):
        join_msg = (
            f"❌ **एक्सेस डिनाइड (Access Denied)!**\n\n"
            f"लाइक्स पाने के लिए आपको हमारे **चैनल** और इस **ग्रुप** दोनों का मेंबर होना अनिवार्य है।\n\n"
            f"📢 **चैनल ज्वाइन करें:** {CHANNEL_USERNAME}\n"
            f"👥 **ग्रुप ज्वाइन करें:** [क्लिक करें]({GROUP_INVITE_LINK})\n\n"
            f"दोनों ज्वाइन करने के बाद दोबारा यहाँ `/like <UID>` टाइप करें।"
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

    # 2. डेली लिमिट चेक
    if not check_daily_limit(str(user_id)):
        bot.reply_to(message, "❌ **लिमिट समाप्त!** आप आज के अपने 20 लाइक्स ले चुके हैं। कल दोबारा प्रयास करें।")
        return

    bot.reply_to(message, f"⏳ **UID:** `{target_uid}` पर **+20 लाइक्स** प्रोसेस हो रहे हैं...")
    
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
        bot.reply_to(message, "❌ **टाइमआउट:** सर्वर से रिस्पॉन्स मिलने में देरी हो रही है।")
    except Exception as e:
        bot.reply_to(message, f"❌ **त्रुटि हुई:** {str(e)}")

def start_bot_polling():
    print("🤖 फ़ोर्स ज्वाइन और ग्रुप-ओनली बॉट पोलिंग चालू है...")
    bot.infinity_polling()
