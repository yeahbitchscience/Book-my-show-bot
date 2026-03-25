import os
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from scraper import fetch_shows
from state_manager import load_tracked_movies, add_tracked_movie, remove_tracked_movie, is_show_seen, save_seen_show

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def escape_markdown(text):
    escape_chars = '_*[]()~`>#+-=|{}.!'
    for c in escape_chars:
        text = text.replace(c, f"\\{c}")
    return text

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_msg = "👋 Welcome to BookMyShow Notifier v2!\n\n" \
                  "Use `/add <url> <Optional: Format e.g. IMAX>` to track a movie.\n" \
                  "Use `/list` to see tracked movies.\n" \
                  "Use `/remove <id>` to stop tracking."
    await update.message.reply_text(welcome_msg)

async def add_movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("Usage: `/add <url> <Optional: format>`", parse_mode="Markdown")
        return
        
    url = args[0]
    movie_format = args[1].upper() if len(args) > 1 else "ANY"
    
    movie_id = add_tracked_movie(url, movie_format, str(update.effective_chat.id))
    await update.message.reply_text(f"✅ Successfully added movie to tracking list.\n**ID:** `{movie_id}`\n**Format Filter:** {movie_format}", parse_mode="Markdown")

async def list_movies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    movies = load_tracked_movies()
    
    user_movies = {k: v for k, v in movies.items() if v["chat_id"] == chat_id}
    
    if not user_movies:
        await update.message.reply_text("You are not tracking any movies.")
        return
        
    msg = "🎬 **Your Tracked Movies:**\n\n"
    for m_id, data in user_movies.items():
        msg += f"ID: `{m_id}`\nFormat: {data['format']}\nURL: {data['url']}\n\n"
        
    await update.message.reply_text(msg, parse_mode="Markdown")

async def remove_movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("Usage: `/remove <id>`")
        return
        
    movie_id = args[0]
    if remove_tracked_movie(movie_id):
        await update.message.reply_text(f"✅ Removed movie `{movie_id}`")
    else:
        await update.message.reply_text("❌ Movie ID not found.")

# --- Background Job ---
async def check_shows_job(context: ContextTypes.DEFAULT_TYPE):
    movies = load_tracked_movies()
    if not movies:
        return
        
    for m_id, data in movies.items():
        url = data["url"]
        target_format = data["format"]
        chat_id = data["chat_id"]
        
        # Run synchronous selenium scraper in a separate thread to not block bot
        result = await asyncio.to_thread(fetch_shows, url)
        
        status = result["status"]
        
        if status == "blocked":
            await context.bot.send_message(chat_id=chat_id, text=f"🚨 **ALERT:** I got blocked by BookMyShow rate limits while checking URL:\n{url}", parse_mode="Markdown")
            continue
        elif status != "success":
            print(f"Error checking {url} (status: {status})")
            continue
            
        shows = result.get("shows", [])
        for show in shows:
            if show["status"] in ["Sold Out", "Disabled"]:
                continue
                
            if target_format != "ANY" and target_format not in show["format"].upper() and target_format not in show["venue"].upper():
                continue
                
            show_id = f"{show['venue']}_{show['date']}_{show['time']}_{show['format']}"
            if not is_show_seen(show_id):
                save_seen_show(show_id)
                msg = f"🎥 *New Show Alert\\!*\n\n"
                msg += f"📍 *Venue:* {escape_markdown(show['venue'])}\n"
                msg += f"🎬 *Format:* {escape_markdown(show['format'])}\n"
                msg += f"⏰ *Time:* {escape_markdown(show['time'])}\n"
                msg += f"🟢 *Status:* {escape_markdown(show['status'])}\n\n"
                msg += f"[Book Now]({escape_markdown(url)})"
                
                await context.bot.send_message(chat_id=chat_id, text=msg, parse_mode="MarkdownV2")

def main():
    if not TELEGRAM_BOT_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not found in .env")
        return
        
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_movie))
    app.add_handler(CommandHandler("list", list_movies))
    app.add_handler(CommandHandler("remove", remove_movie))
    
    # Run every 900 seconds (15 minutes), start checking 10 seconds after boot
    app.job_queue.run_repeating(check_shows_job, interval=900, first=10)
    
    print("Bot is running. Press CTRL+C to stop.")
    app.run_polling()

if __name__ == "__main__":
    main()
