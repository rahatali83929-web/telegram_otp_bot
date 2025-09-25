import requests
from bs4 import BeautifulSoup
import time
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

# 🔐 Hardcoded credentials (from you)
BOT_TOKEN = '8038680012:AAG8YLsYzcq6qEWu8Fy6JXy5f8-ul81HirI'
GROUP_ID = -1002995417831
PANEL_USERNAME = 'Rahatg'
PANEL_PASSWORD = 'Rahatg'

bot = Bot(token=BOT_TOKEN)

def get_buttons():
    keyboard = [
        [InlineKeyboardButton("✨ 𝐃𝐞𝐯𝐞𝐥𝐨𝐩𝐞𝐫", url="https://t.me/Rolex_inxide")],
        [InlineKeyboardButton("⚡ 𝐍𝐮𝐦𝐛𝐞𝐫 𝐂𝐡𝐚𝐧𝐧𝐞𝐥", url="https://t.me/Rolex_Numbers_Hub")]
    ]
    return InlineKeyboardMarkup(keyboard)

def login_panel():
    session = requests.Session()
    login_url = "http://www.roxysms.net/Login"

    # Step 1: Load login page to get captcha
    login_page = session.get(login_url)
    soup = BeautifulSoup(login_page.text, 'html.parser')

    # Step 2: Find captcha question like "Solve: 3 + 5 ="
    captcha_label = soup.find('label', text=lambda t: t and 'Solve:' in t)
    if captcha_label:
        question = captcha_label.text.replace('Solve:', '').replace('=', '').strip()
        try:
            answer = eval(question)
        except:
            print("❌ Failed to solve captcha.")
            return None
    else:
        print("❌ Captcha not found.")
        return None

    # Step 3: Send login request
    login_data = {
        'username': PANEL_USERNAME,
        'password': PANEL_PASSWORD,
        'captcha': answer
    }

    response = session.post(login_url, data=login_data)
    if response.ok:
        print("✅ Logged in successfully with captcha")
        return session
    else:
        print("❌ Login failed!")
        return None

def fetch_otps(session):
    otp_url = "http://www.roxysms.net/client/SMSCDRStats"
    response = session.get(otp_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Update this class name as per your actual HTML
    otp_elements = soup.find_all('div', class_='otp-message')
    otps = []
    for elem in otp_elements:
        text = elem.text.strip()
        if "WhatsApp" in text:
            app = "WhatsApp"
        elif "Facebook" in text:
            app = "Facebook"
        elif "Instagram" in text:
            app = "Instagram"
        elif "Telegram" in text:
            app = "Telegram"
        else:
            app = "Unknown"
        otps.append((app, text))
    return otps

def format_message(app, otp_text):
    message = (
        f"🔐 *𝐑𝐎𝐋𝐄𝐗 𝐎𝐓𝐏 𝐑𝐄𝐂𝐄𝐈𝐕𝐄𝐃*\n\n"
        f"📲 *App:* {app}\n"
        f"📨 *Message:* `{otp_text}`\n\n"
        f"⏰ Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        f"پھر یہ حیات بھی، تاحیات تھوڑی ہے 🖤"
    )
    return message

def main():
    session = login_panel()
    if not session:
        return

    old_otps = set()
    try:
        with open('sent_otps.txt', 'r') as f:
            old_otps = set(f.read().splitlines())
    except FileNotFoundError:
        pass

    new_otps = fetch_otps(session)

    for app, otp_text in new_otps:
        if otp_text not in old_otps:
            message = format_message(app, otp_text)
            bot.send_message(chat_id=GROUP_ID, text=message, parse_mode='Markdown', reply_markup=get_buttons())
            print("📨 New OTP sent to Telegram group.")
            old_otps.add(otp_text)

    with open('sent_otps.txt', 'w') as f:
        for otp in old_otps:
            f.write(f"{otp}\n")

# 🔁 24/7 loop every 10 seconds
if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            print("⚠️ Error:", e)
        time.sleep(10)
