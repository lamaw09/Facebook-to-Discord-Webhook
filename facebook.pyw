import requests
import time
import os
import re
import ctypes
import logging
import socket  # Added for network checking
from playwright.sync_api import sync_playwright

# --- 1. SETUP LOGGING ---
# Kini maghimo og file nga "bot_activity.log" sa samang folder
logging.basicConfig(
    filename='bot_activity.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# --- 2. CONFIGURATION ---
PAGES_TO_WATCH = [
    "https://www.facebook.com/bomboradyophilippines",
    "https://www.facebook.com/101.7XFMBUKIDNON2025",
    "https://www.facebook.com/profile.php?id=100063929018518",
    "https://www.facebook.com/juanderradyo",
    "https://www.facebook.com/88.1RBMalaybalay",
    "https://www.facebook.com/DXDBRadyoBandilyo",
    "https://www.facebook.com/profile.php?id=100071214578309",
    "https://www.facebook.com/BomboRadyoDavao",
    "https://www.facebook.com/bombobutuandxbr",
    "https://www.facebook.com/bomboradyogensan",
    "https://www.facebook.com/bomboradyodxif",
]

DISCORD_WEBHOOK_URL = 'https://discordapp.com/api/webhooks/1452846039798251540/jzw3CaYf76XfjiR-u7riIp4hhu_fED2vgynkbPmMMZZUUdpOxVa3HJ1ynah1_EubJmMR'
SAVE_DIR = "history"

if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

# --- 3. HELPER FUNCTIONS ---

def check_internet():
    """Checks if the network is available."""
    try:
        # Ping Google's Public DNS (8.8.8.8)
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        return True
    except OSError:
        return False

def disable_close_button():
    """Para dili ma-close ang window kon i-run as normal CMD."""
    try:
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd != 0:
            hMenu = ctypes.windll.user32.GetSystemMenu(hwnd, False)
            if hMenu != 0:
                ctypes.windll.user32.DeleteMenu(hMenu, 0xF060, 0x0)
                logging.info("CMD Close button disabled.")
    except Exception as e:
        logging.error(f"Failed to disable close button: {e}")

def get_latest_fb_post_playwright(page_url):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            page.goto(page_url, timeout=35000)
            page.keyboard.press("Escape")
            page.wait_for_selector('div[role="main"]', timeout=15000)
            
            message_locator = page.locator('div[data-ad-preview="message"]').first
            if message_locator.count() == 0:
                browser.close()
                return None, None, None

            newest_text = message_locator.inner_text().strip()
            post_container = message_locator.locator("xpath=./ancestor::div[contains(@class, 'x1yzt60q')]").first
            
            post_link = page_url
            link_elements = post_container.locator('a[role="link"]').all()
            for link in link_elements:
                href = link.get_attribute("href")
                if href and ("/posts/" in href or "/videos/" in href):
                    post_link = href.split('?')[0]
                    break

            img_locator = post_container.locator("img").first
            img_url = img_locator.get_attribute("src") if img_locator.count() > 0 else None

            browser.close()
            return newest_text, img_url, post_link
    except Exception as e:
        logging.warning(f"Error scraping {page_url}: {e}")
        return None, None, None

def send_to_discord(content, img_url, post_url, page_url):
    page_name = page_url.split('/')[-1] if "profile.php" not in page_url else "Facebook Page"
    payload = {
        "embeds": [{
            "title": f"📢 New Post Detected!",
            "description": content[:2000],
            "url": post_url,
            "color": 3447003,
            "image": {"url": img_url} if img_url else None,
            "footer": {"text": f"Source: {page_name} | {time.strftime('%Y-%m-%d %H:%M:%S')}"}
        }]
    }
    try:
        # Added timeout to prevent hanging on poor connection
        r = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=15)
        if r.status_code == 204:
            logging.info(f"Successfully sent update for {page_name} to Discord.")
    except Exception as e:
        logging.error(f"Error sending to Discord: {e}")

# --- 4. MAIN LOOP ---
if __name__ == "__main__":
    disable_close_button()
    logging.info("Bot started. Monitoring pages...")

    while True:
        # AUTO RECONNECT / NETWORK CHECK
        if not check_internet():
            logging.warning("No internet connection detected. Retrying in 30 seconds...")
            time.sleep(30)
            continue

        for fb_url in PAGES_TO_WATCH:
            # Re-check internet during the loop in case it drops mid-cycle
            if not check_internet():
                logging.warning("Internet connection lost during loop. Pausing cycle.")
                break

            raw_name = fb_url.split('/')[-1]
            safe_name = re.sub(r'[^\w\-]', '_', raw_name) + ".txt"
            save_path = os.path.join(SAVE_DIR, safe_name)

            logging.info(f"Checking: {fb_url}")
            current_text, current_img, current_url = get_latest_fb_post_playwright(fb_url)
            
            if current_text:
                last_text = ""
                if os.path.exists(save_path):
                    with open(save_path, "r", encoding="utf-8") as f:
                        last_text = f.read().strip()

                if current_text != last_text:
                    logging.info(f"✨ NEW CONTENT found on {fb_url}")
                    send_to_discord(current_text, current_img, current_url, fb_url)
                    
                    with open(save_path, "w", encoding="utf-8") as f:
                        f.write(current_text)
            
            # Small delay para dili ma-flag as bot/spam sa FB
            time.sleep(3)

        logging.info("Cycle complete. Waiting for next scan...")
        # Optional: Add a sleep here (e.g., time.sleep(600) for 10 mins) if you want to control scan frequency