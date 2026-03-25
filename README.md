# BookMyShow Telegram Notifier v2

A Python-based, fully headless web scraper combined with an interactive Telegram Bot. It continuously monitors BookMyShow for movie ticket availability (e.g., IMAX formats) and sends instant alerts straight to your phone to bypass rate-limits and Cloudflare blocks.

## Features
- **Interactive Telegram Commands:** Add or remove movies to track right from your phone cache (`/add <url> IMAX`, `/list`, `/remove <id>`).
- **Multi-Movie Tracking:** Monitor completely different movies simultaneously.
- **Extreme Anti-Bot Evasion:** Headless Chrome deployment disguised efficiently to avoid BookMyShow's strict automation blocks.
- **Fail-Safe Alerts:** The Bot pings you if BookMyShow locks down your IP, ensuring you are never in the dark.

---

## 🚀 Setup & Deployment Guide (AWS EC2 using `screen`)

This guide outlines the optimal way to deploy the bot 24/7 on an Ubuntu EC2 instance.

### 1. EC2 Instance Preparation
1. Spin up an **Ubuntu** EC2 instance.
2. SSH into your instance.
3. Install Python, Pip, and Google Chrome:
   ```bash
   sudo apt update
   sudo apt install -y python3 python3-pip python3-venv wget screen
   wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
   sudo apt install ./google-chrome-stable_current_amd64.deb -y
   ```

### 2. Download Project & Install Dependencies
Clone your GitHub repository or upload the files using `scp`.
```bash
# Navigate to the project directory
cd bookmyshow-notifier

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install the required packages
pip install -r requirements.txt
```

### 3. Configure the Bot
1. Open Telegram and message `@BotFather` to create a new bot and copy your **Bot Token**.
2. Rename `.env.example` to `.env` in the bot's root directory:
   ```bash
   mv .env.example .env
   nano .env
   ```
3. Paste your token into the `TELEGRAM_BOT_TOKEN="your_token_here"` variable and save.

### 4. Running the Bot Continuously (via `screen`)
To ensure the bot keeps checking for shows even after you close your SSH connection, we use `screen`.

1. Start a new detached screen session named "bmsbot":
   ```bash
   screen -S bmsbot
   ```
2. Activate your virtual environment and start the bot:
   ```bash
   source venv/bin/activate
   python bot.py
   ```
3. **Detach from the screen session:** Press `Ctrl+A` then press `D`. The bot is now running safely in the background!
4. You can safely close your SSH terminal.

#### Screen Useful Commands
- **To view the bot running again:** Run `screen -r bmsbot`.
- **To close the bot permanently:** Reattach to the screen and press `Ctrl+C`.
- **To kill a stuck screen session:** Run `screen -X -S bmsbot quit`.

---

## 💬 Usage
From your Telegram app, message your bot:
- `/start` - Wake the bot up
- `/add https://in.bookmyshow.com/... IMAX` - Begin monitoring the specified URL, filtering ONLY for IMAX formats! (If you don't care about format, type `/add <url> ANY`)
- `/list` - View your active tracking list.
- `/remove <id>` - Remove a movie from your active tracking list using its 8 character ID.
