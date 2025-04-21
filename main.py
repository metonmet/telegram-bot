from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import config
from utils.qr import generate_qr

bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot)

# Dil seçimi
lang_kb = ReplyKeyboardMarkup(resize_keyboard=True)
lang_kb.add(KeyboardButton("🇹🇷 Türkçe"), KeyboardButton("🇬🇧 English"))
lang_kb.add(KeyboardButton("🇷🇺 Русский"), KeyboardButton("🇸🇦 العربية"))

# Ürünler
products = {
    "Leyla Abla": {"1 Şarjör": "1000₺", "4 Şarjör, 1 Kutu": "3000₺"},
    "Aspirin": {"1 Gram": "150$", "2 Gram": "200$"}
}

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("🌍 Lütfen bir dil seçin:", reply_markup=lang_kb)

@dp.message_handler(lambda msg: msg.text in ["🇹🇷 Türkçe", "🇬🇧 English", "🇷🇺 Русский", "🇸🇦 العربية"])
async def show_products(message: types.Message):
    kb = InlineKeyboardMarkup()
    for product in products:
        kb.add(InlineKeyboardButton(product, callback_data=product))
    await message.answer("📦 Ürünlerimiz:", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data in products)
async def show_options(call: types.CallbackQuery):
    selected = call.data
    kb = InlineKeyboardMarkup()
    for option, price in products[selected].items():
        kb.add(InlineKeyboardButton(f"{option} – {price}", callback_data=f"pay_{selected}_{option}"))
    await call.message.answer(f"{selected} için seçenekler:", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data.startswith("pay_"))
async def pay_product(call: types.CallbackQuery):
    _, product, option = call.data.split("_", 2)
    crypto_address = "bitcoin:1BoatSLRHtKNngkdXEeobR76b53LETtpyT"  # örnek BTC adresi
    qr_path = generate_qr(crypto_address, f"{call.from_user.id}_qr")
    await bot.send_photo(call.message.chat.id, open(qr_path, "rb"),
        caption=f"💳 {product} - {option}\n\n🔗 Ödeme adresi:\n{crypto_address}\n\nLütfen ödemenizi yapınız ve /confirm yazınız.")

@dp.message_handler(commands=['confirm'])
async def confirm(message: types.Message):
    await message.answer("✅ Ödemeniz alındı! Siparişiniz işleme alınacak. Teşekkürler.")

# Admin komutu
@dp.message_handler(commands=['admin'])
async def admin(message: types.Message):
    if message.from_user.id == config.ADMIN_ID:
        await message.answer("🛠 Admin paneline hoş geldin.")
    else:
        await message.answer("⛔ Yetkisiz erişim.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
