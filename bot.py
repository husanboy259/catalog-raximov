"""
MEBEL KATALOG BOTI
Telegram bot - aiogram 3.x
"""

import asyncio
import logging

from dotenv import load_dotenv

load_dotenv()

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup,
    InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton,
    ReplyKeyboardRemove, InputMediaPhoto
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from catalog import MebelKatalog
from config import BOT_TOKEN

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─── FSM Holatlari ───────────────────────────────────────────────────────────
Admin_ID = 6905461427
class YangiMebel(StatesGroup):
    rasm       = State()
    nomi       = State()
    narxi      = State()
    tavsif     = State()
    kategoriya = State()

class TahrirlashHolat(StatesGroup):
    id_kirish  = State()
    maydon     = State()
    qiymat     = State()

class QidiruvHolat(StatesGroup):
    so_z = State()

# ─── Global ob'ektlar ─────────────────────────────────────────────────────────

katalog = MebelKatalog()
bot_instance: Bot = None

# ─── Klaviaturalar ────────────────────────────────────────────────────────────

def asosiy_menu() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="➕ Mahsulot qo'shish"),
        KeyboardButton(text="📋 Katalog"),
    )
    builder.row(
        KeyboardButton(text="🔍 Qidirish"),
        KeyboardButton(text="🗂 Kategoriya"),
    )
    builder.row(
        KeyboardButton(text="📊 Statistika"),
        KeyboardButton(text="💰 Narx bo'yicha"),
    )
    return builder.as_markup(resize_keyboard=True)


def kategoriya_klaviatura() -> InlineKeyboardMarkup:
    kategoriyalar = katalog.kategoriyalar
    builder = InlineKeyboardBuilder()
    for kat in kategoriyalar:
        builder.button(text=kat, callback_data=f"kat:{kat}")
    builder.button(text="❌ Bekor qilish", callback_data="bekor")
    builder.adjust(2)
    return builder.as_markup()


def mahsulot_amallar(mahsulot_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✏️ Tahrirlash",  callback_data=f"tahrir:{mahsulot_id}")
    builder.button(text="🗑 O'chirish",   callback_data=f"ochir:{mahsulot_id}")
    builder.button(text="🔙 Orqaga",      callback_data="katalog_bosh")
    builder.adjust(2)
    return builder.as_markup()


def tahrirlash_maydonlar(mahsulot_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    maydonlar = [
        ("📝 Nomi",      "nomi"),
        ("💰 Narxi",     "narxi"),
        ("📄 Tavsif",    "tavsif"),
        ("🗂 Kategoriya","kategoriya"),
        ("🖼 Rasm",      "rasm"),
    ]
    for matn, kod in maydonlar:
        builder.button(text=matn, callback_data=f"maydon:{mahsulot_id}:{kod}")
    builder.button(text="❌ Bekor", callback_data="bekor")
    builder.adjust(2)
    return builder.as_markup()


def katalog_kategoriya_filter() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for kat in katalog.kategoriyalar:
        soni = len(katalog.kategoriya_boyicha(kat))
        builder.button(text=f"{kat} ({soni})", callback_data=f"filter:{kat}")
    builder.button(text="📋 Barchasi", callback_data="filter:barchasi")
    builder.adjust(2)
    return builder.as_markup()


def narx_saralash() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="⬆️ Arzondan qimmatga", callback_data="narx:oshish")
    builder.button(text="⬇️ Qimmatdan arzonga", callback_data="narx:kamayish")
    builder.adjust(1)
    return builder.as_markup()

# ─── Yordamchi funksiyalar ────────────────────────────────────────────────────

def mahsulot_matni(m: dict) -> str:
    return (
        f"🪑 <b>{m['nomi']}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 <b>ID:</b> <code>{m['id']}</code>\n"
        f"🗂 <b>Kategoriya:</b> {m['kategoriya']}\n"
        f"💰 <b>Narxi:</b> {int(m['narxi']):,} so'm\n"
        f"📄 <b>Tavsif:</b> {m['tavsif']}\n"
        f"📅 <b>Qo'shilgan:</b> {m['sana']}\n"
        f"✅ <b>Holati:</b> {m['holat']}"
    )

# ─── Handlerlar ───────────────────────────────────────────────────────────────

async def start_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "👋 <b>Mebel Katalog Botiga xush kelibsiz!</b>\n\n"
        "Bu bot orqali mebel katalogini boshqarishingiz mumkin.\n"
        "Quyidagi menyudan kerakli amalni tanlang:",
        reply_markup=asosiy_menu(),
        parse_mode="HTML"
    )


async def help_handler(message: Message):
    await message.answer(
        "📌 <b>Bot buyruqlari:</b>\n\n"
        "/yangi — Yangi mahsulot qo'shish\n"
        "/katalog — Barcha mahsulotlar\n"
        "/qidirish — Mahsulot qidirish\n"
        "/statistika — Statistika\n"
        "/tahrirlash — Mahsulot tahrirlash\n"
        "/ochirish — Mahsulot o'chirish\n\n"
        "Yoki quyidagi tugmalardan foydalaning 👇",
        reply_markup=asosiy_menu(),
        parse_mode="HTML"
    )

# ── Yangi mahsulot ─────────────────────────────────────────────────────────────

async def yangi_start(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(YangiMebel.rasm)
    await message.answer(
        "🖼 <b>Yangi mahsulot qo'shish</b>\n\n"
        "1️⃣ Mebel rasmini yuboring:",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="HTML"
    )


async def yangi_rasm(message: Message, state: FSMContext):
    if not message.photo:
        await message.answer("⚠️ Iltimos, rasm yuboring!")
        return
    await state.update_data(rasm_id=message.photo[-1].file_id)
    await state.set_state(YangiMebel.nomi)
    await message.answer("2️⃣ Mebel nomini kiriting:")


async def yangi_nomi(message: Message, state: FSMContext):
    if len(message.text.strip()) < 2:
        await message.answer("⚠️ Nom kamida 2 ta belgidan iborat bo'lishi kerak!")
        return
    await state.update_data(nomi=message.text.strip())
    await state.set_state(YangiMebel.narxi)
    await message.answer("3️⃣ Narxini kiriting (faqat raqam, so'mda):\nMisol: 8500000")


async def yangi_narxi(message: Message, state: FSMContext):
    try:
        narx = int(message.text.strip().replace(" ", "").replace(",", ""))
        if narx <= 0:
            raise ValueError
    except ValueError:
        await message.answer("⚠️ Narx to'g'ri raqam bo'lishi kerak!\nMisol: 8500000")
        return
    await state.update_data(narxi=narx)
    await state.set_state(YangiMebel.tavsif)
    await message.answer("4️⃣ Qisqacha tavsif kiriting:")


async def yangi_tavsif(message: Message, state: FSMContext):
    await state.update_data(tavsif=message.text.strip())
    await state.set_state(YangiMebel.kategoriya)
    await message.answer(
        "5️⃣ Kategoriyani tanlang:",
        reply_markup=kategoriya_klaviatura()
    )


async def yangi_kategoriya_cb(callback: CallbackQuery, state: FSMContext):
    if callback.data == "bekor":
        await state.clear()
        await callback.message.edit_text("❌ Qo'shish bekor qilindi.")
        await callback.message.answer("Asosiy menyu:", reply_markup=asosiy_menu())
        return

    kat = callback.data.split(":", 1)[1]
    data = await state.get_data()

    mahsulot = katalog.qosh(
        nomi=data["nomi"],
        narxi=data["narxi"],
        tavsif=data["tavsif"],
        kategoriya=kat,
        rasm_id=data["rasm_id"]
    )
    await state.clear()
    await callback.message.edit_text("✅ Mahsulot muvaffaqiyatli qo'shildi!")
    await callback.message.answer_photo(
        photo=mahsulot["rasm_id"],
        caption=mahsulot_matni(mahsulot),
        parse_mode="HTML",
        reply_markup=asosiy_menu()
    )
    await callback.answer("✅ Saqlandi!")

# ── Katalog ko'rish ────────────────────────────────────────────────────────────

async def katalog_handler(message: Message):
    mahsulotlar = katalog.barchasi()
    if not mahsulotlar:
        await message.answer(
            "📭 Katalog bo'sh.\n\n➕ Mahsulot qo'shish uchun tugmani bosing.",
            reply_markup=asosiy_menu()
        )
        return
    await message.answer(
        f"📋 <b>Katalog</b> — jami {len(mahsulotlar)} ta mahsulot\n\nKategoriya bo'yicha filtrlash:",
        reply_markup=katalog_kategoriya_filter(),
        parse_mode="HTML"
    )


async def filter_callback(callback: CallbackQuery):
    kat = callback.data.split(":", 1)[1]
    if kat == "barchasi":
        mahsulotlar = katalog.barchasi()
        sarlavha = "📋 Barcha mahsulotlar"
    else:
        mahsulotlar = katalog.kategoriya_boyicha(kat)
        sarlavha = f"🗂 {kat}"

    if not mahsulotlar:
        await callback.answer("Bu kategoriyada mahsulot yo'q!", show_alert=True)
        return

    await callback.message.edit_text(
        f"{sarlavha} — {len(mahsulotlar)} ta mahsulot\n\nMahsulotni ko'rish uchun ID kiriting yoki /qidirish dan foydalaning.",
        parse_mode="HTML"
    )
    # Har bir mahsulotni yuborish
    for m in mahsulotlar[:10]:  # Max 10 ta ko'rsatiladi
        try:
            await callback.message.answer_photo(
                photo=m["rasm_id"],
                caption=mahsulot_matni(m),
                parse_mode="HTML",
                reply_markup=mahsulot_amallar(m["id"])
            )
        except Exception:
            await callback.message.answer(
                mahsulot_matni(m),
                parse_mode="HTML",
                reply_markup=mahsulot_amallar(m["id"])
            )
    if len(mahsulotlar) > 10:
        await callback.message.answer(f"... va yana {len(mahsulotlar)-10} ta mahsulot.")
    await callback.answer()

# ── Qidirish ───────────────────────────────────────────────────────────────────

async def qidirish_start(message: Message, state: FSMContext):
    await state.set_state(QidiruvHolat.so_z)
    await message.answer(
        "🔍 <b>Qidirish</b>\n\nMahsulot nomi yoki ID kiriting:",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="HTML"
    )


async def qidirish_natija(message: Message, state: FSMContext):
    so_z = message.text.strip()
    await state.clear()
    natijalar = katalog.qidirish(so_z)
    if not natijalar:
        await message.answer(
            f"🔍 '<b>{so_z}</b>' bo'yicha hech narsa topilmadi.",
            reply_markup=asosiy_menu(),
            parse_mode="HTML"
        )
        return
    await message.answer(
        f"🔍 '{so_z}' bo'yicha <b>{len(natijalar)}</b> ta natija:",
        reply_markup=asosiy_menu(),
        parse_mode="HTML"
    )
    for m in natijalar:
        try:
            await message.answer_photo(
                photo=m["rasm_id"],
                caption=mahsulot_matni(m),
                parse_mode="HTML",
                reply_markup=mahsulot_amallar(m["id"])
            )
        except Exception:
            await message.answer(
                mahsulot_matni(m),
                parse_mode="HTML",
                reply_markup=mahsulot_amallar(m["id"])
            )

# ── Tahrirlash ─────────────────────────────────────────────────────────────────

async def tahrirlash_start(message: Message, state: FSMContext):
    await state.set_state(TahrirlashHolat.id_kirish)
    await message.answer(
        "✏️ <b>Tahrirlash</b>\n\nMahsulot ID sini kiriting (misol: DAM-0001):",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="HTML"
    )


async def tahrirlash_id(message: Message, state: FSMContext):
    mid = message.text.strip().upper()
    m = katalog.id_boyicha(mid)
    if not m:
        await message.answer(f"⚠️ <code>{mid}</code> IDli mahsulot topilmadi!", parse_mode="HTML")
        return
    await state.update_data(mahsulot_id=mid)
    await state.set_state(TahrirlashHolat.maydon)
    await message.answer(
        f"✏️ <b>{m['nomi']}</b> mahsulotini tahrirlash\n\nQaysi maydonni o'zgartirmoqchisiz?",
        reply_markup=tahrirlash_maydonlar(mid),
        parse_mode="HTML"
    )


async def tahrirlash_maydon_cb(callback: CallbackQuery, state: FSMContext):
    if callback.data == "bekor":
        await state.clear()
        await callback.message.edit_text("❌ Tahrirlash bekor qilindi.")
        await callback.message.answer("Asosiy menyu:", reply_markup=asosiy_menu())
        return

    _, mid, maydon = callback.data.split(":")
    await state.update_data(maydon=maydon)
    await state.set_state(TahrirlashHolat.qiymat)

    if maydon == "kategoriya":
        await callback.message.edit_text(
            "🗂 Yangi kategoriyani tanlang:",
            reply_markup=kategoriya_klaviatura()
        )
    elif maydon == "rasm":
        await callback.message.edit_text("🖼 Yangi rasmni yuboring:")
    else:
        nomlar = {"nomi": "Yangi nom", "narxi": "Yangi narx (raqam)", "tavsif": "Yangi tavsif"}
        await callback.message.edit_text(f"📝 {nomlar.get(maydon, 'Yangi qiymat')}ni kiriting:")
    await callback.answer()


async def tahrirlash_qiymat(message: Message, state: FSMContext):
    data = await state.get_data()
    mid = data["mahsulot_id"]
    maydon = data["maydon"]

    if maydon == "rasm":
        if not message.photo:
            await message.answer("⚠️ Rasm yuboring!")
            return
        yangi = message.photo[-1].file_id
    elif maydon == "narxi":
        try:
            yangi = int(message.text.strip().replace(" ", "").replace(",", ""))
        except ValueError:
            await message.answer("⚠️ Narx raqam bo'lishi kerak!")
            return
    else:
        yangi = message.text.strip()

    katalog.tahrirlash(mid, maydon, yangi)
    await state.clear()
    m = katalog.id_boyicha(mid)
    await message.answer(
        f"✅ <b>{m['nomi']}</b> muvaffaqiyatli yangilandi!",
        reply_markup=asosiy_menu(),
        parse_mode="HTML"
    )


async def tahrirlash_kategoriya_cb(callback: CallbackQuery, state: FSMContext):
    current = await state.get_state()
    if current != TahrirlashHolat.qiymat:
        return
    data = await state.get_data()
    if data.get("maydon") != "kategoriya":
        return

    if callback.data == "bekor":
        await state.clear()
        await callback.message.edit_text("❌ Tahrirlash bekor qilindi.")
        await callback.message.answer("Asosiy menyu:", reply_markup=asosiy_menu())
        return

    kat = callback.data.split(":", 1)[1]
    katalog.tahrirlash(data["mahsulot_id"], "kategoriya", kat)
    await state.clear()
    await callback.message.edit_text(f"✅ Kategoriya <b>{kat}</b> ga o'zgartirildi!", parse_mode="HTML")
    await callback.message.answer("Asosiy menyu:", reply_markup=asosiy_menu())
    await callback.answer()

# ── O'chirish ──────────────────────────────────────────────────────────────────

async def ochirish_callback(callback: CallbackQuery):
    mid = callback.data.split(":", 1)[1]
    m = katalog.id_boyicha(mid)
    if not m:
        await callback.answer("Mahsulot topilmadi!", show_alert=True)
        return

    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Ha, o'chirish", callback_data=f"tasdiqlash:{mid}")
    builder.button(text="❌ Yo'q",          callback_data="bekor")
    builder.adjust(2)

    await callback.message.answer(
        f"🗑 <b>{m['nomi']}</b> mahsulotini o'chirishni tasdiqlaysizmi?",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    await callback.answer()


async def tasdiqlash_ochirish(callback: CallbackQuery):
    mid = callback.data.split(":", 1)[1]
    m = katalog.id_boyicha(mid)
    if katalog.ochir(mid):
        await callback.message.edit_text(
            f"✅ <b>{m['nomi']}</b> ({mid}) katalogdan o'chirildi.",
            parse_mode="HTML"
        )
    else:
        await callback.message.edit_text("⚠️ O'chirishda xatolik yuz berdi.")
    await callback.message.answer("Asosiy menyu:", reply_markup=asosiy_menu())
    await callback.answer()

# ── Statistika ────────────────────────────────────────────────────────────────

async def statistika_handler(message: Message):
    stat = katalog.statistika()
    matn = (
        "📊 <b>Katalog Statistikasi</b>\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        f"📦 Jami mahsulotlar: <b>{stat['jami']}</b>\n"
        f"✅ Aktiv: <b>{stat['aktiv']}</b>\n\n"
        "<b>Kategoriyalar bo'yicha:</b>\n"
    )
    for kat, soni in stat["kategoriyalar"].items():
        if soni > 0:
            matn += f"  • {kat}: {soni} ta\n"

    matn += f"\n💰 <b>Narx ko'rsatkichlari:</b>\n"
    if stat["jami"] > 0:
        matn += (
            f"  • Eng arzon: {stat['min_narx']:,} so'm\n"
            f"  • Eng qimmat: {stat['max_narx']:,} so'm\n"
            f"  • O'rtacha: {stat['ortacha_narx']:,} so'm"
        )
    else:
        matn += "  Ma'lumot yo'q"

    await message.answer(matn, reply_markup=asosiy_menu(), parse_mode="HTML")

# ── Narx bo'yicha saralash ────────────────────────────────────────────────────

async def narx_saralash_handler(message: Message):
    await message.answer(
        "💰 <b>Narx bo'yicha saralash</b>",
        reply_markup=narx_saralash(),
        parse_mode="HTML"
    )


async def narx_callback(callback: CallbackQuery):
    tartib = callback.data.split(":", 1)[1]
    teskari = tartib == "kamayish"
    mahsulotlar = katalog.narx_boyicha(teskari=teskari)

    if not mahsulotlar:
        await callback.answer("Katalog bo'sh!", show_alert=True)
        return

    tartib_matn = "⬇️ Qimmatdan arzonga" if teskari else "⬆️ Arzondan qimmatga"
    await callback.message.edit_text(
        f"💰 {tartib_matn} — {len(mahsulotlar)} ta mahsulot:"
    )
    for m in mahsulotlar[:10]:
        try:
            await callback.message.answer_photo(
                photo=m["rasm_id"],
                caption=mahsulot_matni(m),
                parse_mode="HTML",
                reply_markup=mahsulot_amallar(m["id"])
            )
        except Exception:
            await callback.message.answer(
                mahsulot_matni(m),
                parse_mode="HTML",
                reply_markup=mahsulot_amallar(m["id"])
            )
    await callback.answer()


async def bekor_callback(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Amal bekor qilindi.")
    await callback.message.answer("Asosiy menyu:", reply_markup=asosiy_menu())
    await callback.answer()


async def katalog_bosh_callback(callback: CallbackQuery):
    await callback.message.answer("Asosiy menyu:", reply_markup=asosiy_menu())
    await callback.answer()

# ─── Dispatcher sozlash ───────────────────────────────────────────────────────

def setup_handlers(dp: Dispatcher):
    # Start / Help
    dp.message.register(start_handler,     Command("start"))
    dp.message.register(help_handler,      Command("help"))

    # Menyu tugmalari
    dp.message.register(yangi_start,           F.text == "➕ Mahsulot qo'shish")
    dp.message.register(yangi_start,           Command("yangi"))
    dp.message.register(katalog_handler,       F.text == "📋 Katalog")
    dp.message.register(katalog_handler,       Command("katalog"))
    dp.message.register(qidirish_start,        F.text == "🔍 Qidirish")
    dp.message.register(qidirish_start,        Command("qidirish"))
    dp.message.register(statistika_handler,    F.text == "📊 Statistika")
    dp.message.register(statistika_handler,    Command("statistika"))
    dp.message.register(narx_saralash_handler, F.text == "💰 Narx bo'yicha")
    dp.message.register(tahrirlash_start,      F.text.startswith("🗂 Kategoriya"))
    dp.message.register(tahrirlash_start,      Command("tahrirlash"))
    dp.message.register(start_handler,         Command("ochirish"))  # ID kerak

    # FSM: Yangi mahsulot
    dp.message.register(yangi_rasm,      YangiMebel.rasm)
    dp.message.register(yangi_nomi,      YangiMebel.nomi)
    dp.message.register(yangi_narxi,     YangiMebel.narxi)
    dp.message.register(yangi_tavsif,    YangiMebel.tavsif)
    dp.callback_query.register(yangi_kategoriya_cb,
                                F.data.startswith("kat:") | (F.data == "bekor"),
                                YangiMebel.kategoriya)

    # FSM: Tahrirlash
    dp.message.register(tahrirlash_id,     TahrirlashHolat.id_kirish)
    dp.callback_query.register(tahrirlash_maydon_cb,
                                F.data.startswith("maydon:") | (F.data == "bekor"),
                                TahrirlashHolat.maydon)
    dp.message.register(tahrirlash_qiymat,  TahrirlashHolat.qiymat)
    dp.callback_query.register(tahrirlash_kategoriya_cb,
                                F.data.startswith("kat:") | (F.data == "bekor"),
                                TahrirlashHolat.qiymat)

    # FSM: Qidirish
    dp.message.register(qidirish_natija, QidiruvHolat.so_z)

    # Callback'lar
    dp.callback_query.register(filter_callback,      F.data.startswith("filter:"))
    dp.callback_query.register(ochirish_callback,    F.data.startswith("ochir:"))
    dp.callback_query.register(tasdiqlash_ochirish,  F.data.startswith("tasdiqlash:"))
    dp.callback_query.register(narx_callback,        F.data.startswith("narx:"))
    dp.callback_query.register(bekor_callback,       F.data == "bekor")
    dp.callback_query.register(katalog_bosh_callback, F.data == "katalog_bosh")
    dp.callback_query.register(
        lambda cb, state: tahrirlash_start.__wrapped__(cb.message, state)
        if hasattr(tahrirlash_start, '__wrapped__') else None,
        F.data.startswith("tahrir:")
    )

    # Tahrirlash callback (alohida handler)
    async def tahrir_callback(callback: CallbackQuery, state: FSMContext):
        mid = callback.data.split(":", 1)[1]
        await state.update_data(mahsulot_id=mid)
        await state.set_state(TahrirlashHolat.maydon)
        m = katalog.id_boyicha(mid)
        if not m:
            await callback.answer("Mahsulot topilmadi!", show_alert=True)
            return
        await callback.message.answer(
            f"✏️ <b>{m['nomi']}</b> — qaysi maydonni o'zgartirish?",
            reply_markup=tahrirlash_maydonlar(mid),
            parse_mode="HTML"
        )
        await callback.answer()

    dp.callback_query.register(tahrir_callback, F.data.startswith("tahrir:"))


async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    setup_handlers(dp)
    logger.info("Bot ishga tushdi...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
