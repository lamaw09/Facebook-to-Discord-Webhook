# 🤖 Facebook to Discord Webhook

A high-performance automation tool built with **Python** and **Playwright**. This bot monitors a curated list of Facebook Pages and automatically broadcasts new posts—including text and images—to your **Discord Server** in real-time via Webhooks.

## ✨ Features
- **Multi-Page Monitoring:** Simultaneously tracks multiple Facebook pages from a single configuration.
- **Change Detection:** Smart comparison logic using a `history/` directory to ensure only unique, new content triggers a notification.
- **Auto-Reconnect:** Integrated network diagnostics to pause operations during internet outages and resume automatically.
- **Robust Logging:** Comprehensive activity and error tracking stored in `bot_activity.log`.
- **Media Extraction:** Automatically detects post images and direct permalinks for rich Discord embeds.

## 🛠 Tech Stack
- **Language:** Python 3.10+
- **Browser Automation:** [Playwright](https://playwright.dev/python/) (Chromium)
- **Notifications:** Discord Webhooks API
- **Key Libraries:** `requests`, `playwright`, `ctypes`, `socket`

## 🚀 Installation & Setup

1. **Clone the Repository:**
   ```bash
   git clone [https://github.com/lamaw09/Facebook-to-Discord-Webhook.git](https://github.com/lamaw09/Facebook-to-Discord-Webhook.git)
   cd Facebook-to-Discord-Webhook


