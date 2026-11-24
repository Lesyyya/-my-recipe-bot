import asyncio, json, os, random
from pathlib import Path
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("Set BOT_TOKEN environment variable before starting the bot.")

RECIPES = json.loads(Path(__file__).with_name("recipes.json").read_text(encoding="utf-8"))
dp = Dispatcher()
profiles = {}  # Telegram user ID -> selected profile
favorites = {}  # Telegram user ID -> set(recipe IDs)

PROFILE_LABELS = {"me": "👩 Мои рецепты", "boyfriend": "👨 Рецепты для парня"}

def main_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="👩 Мои рецепты и продукты", callback_data="profile:me")
    kb.button(text="👨 Рецепты для парня", callback_data="profile:boyfriend")
    kb.button(text="❤️ Избранное", callback_data="favorites")
    kb.adjust(1)
    return kb.as_markup()

def profile_menu(profile):
    items = [r for r in RECIPES if r["profile"] == profile]
    categories = sorted({r["category"] for r in items})
    kb = InlineKeyboardBuilder()
    kb.button(text="🎲 Случайный рецепт", callback_data=f"random:{profile}")
    for category in categories:
        kb.button(text=f"📂 {category}", callback_data=f"category:{profile}:{category}")
    kb.button(text="⬅️ Главное меню", callback_data="home")
    kb.adjust(1)
    return kb.as_markup()

def recipe_card(r, user_id):
    text = f"🍽 <b>{r['title']}</b>\n⏱ {r['time']} минут · 👥 {r['servings']} порции\n\n<b>Ингредиенты:</b>\n"
    text += "\n".join("• " + x for x in r["ingredients"])
    text += "\n\n<b>Приготовление:</b>\n"
    text += "\n".join(f"{i}. {step}" for i, step in enumerate(r["steps"], 1))
    kb = InlineKeyboardBuilder()
    is_fav = r["id"] in favorites.get(user_id, set())
    kb.button(text=("💔 Убрать из избранного" if is_fav else "❤️ В избранное"), callback_data=f"fav:{r['id']}")
    kb.button(text="🔄 Другой рецепт", callback_data=f"random:{r['profile']}")
    kb.button(text="⬅️ К разделу", callback_data=f"profile:{r['profile']}")
    kb.adjust(1)
    return text, kb.as_markup()

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("Привет! 👩‍🍳\nЯ твой личный бот с рецептами. Выбирай, для кого ищем блюдо:", reply_markup=main_menu())

@dp.callback_query(F.data == "home")
async def home(call: CallbackQuery):
    await call.message.edit_text("Выбирай раздел рецептов:", reply_markup=main_menu())
    await call.answer()

@dp.callback_query(F.data.startswith("profile:"))
async def choose_profile(call: CallbackQuery):
    profile = call.data.split(":", 1)[1]
    profiles[call.from_user.id] = profile
    await call.message.edit_text(f"{PROFILE_LABELS[profile]}\nВыбери категорию или случайный рецепт:", reply_markup=profile_menu(profile))
    await call.answer()

@dp.callback_query(F.data.startswith("category:"))
async def choose_category(call: CallbackQuery):
    _, profile, category = call.data.split(":", 2)
    found = [r for r in RECIPES if r["profile"] == profile and r["category"] == category]
    kb = InlineKeyboardBuilder()
    for r in found:
        kb.button(text=f"🍴 {r['title']}", callback_data=f"recipe:{r['id']}")
    kb.button(text="⬅️ Назад", callback_data=f"profile:{profile}")
    kb.adjust(1)
    await call.message.edit_text(f"📂 <b>{category}</b>\nВыбери рецепт:", reply_markup=kb.as_markup())
    await call.answer()

@dp.callback_query(F.data.startswith("random:"))
async def random_recipe(call: CallbackQuery):
    profile = call.data.split(":", 1)[1]
    pool = [r for r in RECIPES if r["profile"] == profile]
    if not pool:
        await call.answer("В этом разделе пока нет рецептов.", show_alert=True)
        return
    r = random.choice(pool)
    text, markup = recipe_card(r, call.from_user.id)
    await call.message.edit_text(text, reply_markup=markup)
    await call.answer()

@dp.callback_query(F.data.startswith("recipe:"))
async def show_recipe(call: CallbackQuery):
    recipe_id = call.data.split(":", 1)[1]
    r = next((r for r in RECIPES if r["id"] == recipe_id), None)
    if not r:
        await call.answer("Рецепт не найден.", show_alert=True)
        return
    text, markup = recipe_card(r, call.from_user.id)
    await call.message.edit_text(text, reply_markup=markup)
    await call.answer()

@dp.callback_query(F.data.startswith("fav:"))
async def toggle_favorite(call: CallbackQuery):
    recipe_id = call.data.split(":", 1)[1]
    user_favs = favorites.setdefault(call.from_user.id, set())
    if recipe_id in user_favs:
        user_favs.remove(recipe_id)
    else:
        user_favs.add(recipe_id)
    r = next((r for r in RECIPES if r["id"] == recipe_id), None)
    if r:
        text, markup = recipe_card(r, call.from_user.id)
        await call.message.edit_text(text, reply_markup=markup)
    await call.answer("Избранное обновлено ❤️")

@dp.callback_query(F.data == "favorites")
async def show_favorites(call: CallbackQuery):
    user_favs = favorites.get(call.from_user.id, set())
    found = [r for r in RECIPES if r["id"] in user_favs]
    kb = InlineKeyboardBuilder()
    for r in found:
        kb.button(text=f"❤️ {r['title']}", callback_data=f"recipe:{r['id']}")
    kb.button(text="⬅️ Главное меню", callback_data="home")
    kb.adjust(1)
    await call.message.edit_text("❤️ <b>Избранное</b>" if found else "Пока нет сохранённых рецептов.", reply_markup=kb.as_markup())
    await call.answer()

async def main():
    bot = Bot(TOKEN)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
