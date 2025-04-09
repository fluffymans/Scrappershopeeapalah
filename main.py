import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Halo! Saya bot pencari harga murah di Shopee.\n\n"
        "Gunakan perintah:\n"
        "`/cari sepatu pria`\n"
        "untuk mencari barang termurah.",
        parse_mode="Markdown"
    )

async def cari(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Kirim kata kunci setelah /cari, contoh: /cari jam tangan")
        return

    keyword = ' '.join(context.args)
    await update.message.reply_text(f"Mencari barang termurah untuk: *{keyword}*...", parse_mode="Markdown")

    url = f"https://shopee.co.id/api/v4/search/search_items?by=price&keyword={keyword}&limit=5&newest=0&order=asc&page_type=search"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        if not data['data'].get('items'):
            await update.message.reply_text("Tidak ditemukan hasil.")
            return

        results = data['data']['items']
        msg = f"Top 5 barang termurah untuk: *{keyword}*\n\n"

        for item in results:
            info = item['item_basic']
            name = info['name']
            price = info['price'] // 100000
            link = f"https://shopee.co.id/product/{info['shopid']}/{info['itemid']}"
            msg += f"*{name}*\nHarga: Rp {price:,}\n[Link Produk]({link})\n\n"

        await update.message.reply_text(msg, parse_mode="Markdown", disable_web_page_preview=True)

    except Exception as e:
        await update.message.reply_text(f"Gagal mengambil data: {str(e)}")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("cari", cari))
app.run_polling()
