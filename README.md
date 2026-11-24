# Personal Recipe Telegram Bot (starter)

## Included
- Two separate recipe profiles: `me` and `boyfriend`
- Category browsing
- Random recipe picker
- Recipe cards with ingredients and steps
- Favorites (currently held in memory; they reset when the bot restarts)
- Starter recipe set in `recipes.json`

## Run
1. Create a bot in Telegram with **@BotFather** and copy the token.
2. Install Python 3.10+.
3. In this folder, install dependencies:
   `python -m pip install -r requirements.txt`
4. Set the token in your environment (do not paste it into public chats or commit it):
   macOS/Linux:
   `export BOT_TOKEN="YOUR_TOKEN"`
   Windows PowerShell:
   `$env:BOT_TOKEN="YOUR_TOKEN"`
5. Start:
   `python bot.py`

This is a starter build. Next we can add persistent SQLite storage, ingredient search (“what's in my fridge?”), servings calculator, and recipe photos.
