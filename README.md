# 🪑 Mebel Katalog Boti

Telegram bot — mebel katalogini boshqarish uchun.

## Fayl tuzilmasi

```
mebel_bot/
├── bot.py           # Asosiy bot (handlerlar, FSM)
├── catalog.py       # Katalog ma'lumotlar sinfi
├── config.py        # Token va sozlamalar
├── requirements.txt # Kutubxonalar
├── .env.example     # Token namunasi
└── katalog.json     # Ma'lumotlar (avtomatik yaratiladi)
```

## O'rnatish

```bash
# 1. Virtual muhit
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 2. Kutubxonalar
pip install -r requirements.txt

# 3. Token sozlash
cp .env.example .env
# .env faylini oching va BOT_TOKEN ni o'zgartiring
```

## Ishga tushirish

```bash
python bot.py
```

## Imkoniyatlar

| Buyruq / Tugma         | Tavsif                          |
|------------------------|---------------------------------|
| `/start`               | Botni ishga tushirish           |
| `/yangi`               | Yangi mahsulot qo'shish         |
| `/katalog`             | Barcha mahsulotlar              |
| `/qidirish`            | Nom yoki ID bo'yicha qidirish   |
| `/statistika`          | Katalog statistikasi            |
| `/tahrirlash`          | Mahsulotni tahrirlash           |
| 💰 Narx bo'yicha       | Narx bo'yicha saralash          |
| 🗂 Kategoriya          | Kategoriya bo'yicha filtrlash   |

## Mahsulot formati

```
ID: DAM-0001
Nomi: Premium Divan
Kategoriya: Divan
Narxi: 8,500,000 so'm
Tavsif: Yumshoq va zamonaviy divan
Rasm: (yuklangan rasm)
Qo'shilgan: 11.06.2025 14:30
Holati: Aktiv
```

## Kategoriyalar

Divan • Kreslo • Stol • Stul • Shkaf  
Krovat • Komod • Oshxona mebellari • Ofis mebellari • Boshqa
