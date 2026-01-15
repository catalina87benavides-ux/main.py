from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)
import random
import asyncio
import json
import os

# =====================
# CONFIGURACIÓN
# =====================
TOKEN = "8541063771:AAE96tp6GFJzggXMYrYCEzESAhUfUz6XSvA"

ADMIN_IDS = [
    7275042647,
    1179613392
]

DATA_FILE = "data.json"

# =====================
# MANEJO DE DATOS
# =====================
def cargar_datos():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def guardar_datos(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

datos = cargar_datos()

# =====================
# SORTEO
# =====================
participantes = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    teclado = [
        [InlineKeyboardButton("🎉 Participar", callback_data="participar")],
        [InlineKeyboardButton("⏱ Iniciar sorteo (5s)", callback_data="iniciar")]
    ]
    await update.message.reply_text(
        "🎉 BOT DE SORTEOS 🎉",
        reply_markup=InlineKeyboardMarkup(teclado)
    )

async def participar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    participantes[q.from_user.id] = q.from_user.full_name
    await q.message.reply_text("✅ Estás participando")

async def iniciar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if q.from_user.id not in ADMIN_IDS:
        await q.message.reply_text("⛔ Solo admins")
        return

    if not participantes:
        await q.message.reply_text("❌ No hay participantes")
        return

    for i in range(5, 0, -1):
        await q.message.reply_text(f"⏳ {i}")
        await asyncio.sleep(1)

    ganador = random.choice(list(participantes.values()))
    await q.message.reply_text(f"🏆 GANADOR:\n{ganador}")
    participantes.clear()

# =====================
# COMANDOS DE PRECIOS
# =====================
async def mostrar(update: Update, context: ContextTypes.DEFAULT_TYPE, key):
    await update.message.reply_text(datos.get(key, "❌ No configurado"))

async def usd(update, context): await mostrar(update, context, "usd")
async def mex(update, context): await mostrar(update, context, "mex")
async def peru(update, context): await mostrar(update, context, "peru")
async def colombia(update, context): await mostrar(update, context, "colombia")
async def guate(update, context): await mostrar(update, context, "guate")
async def crobux(update, context): await mostrar(update, context, "crobux")
async def robux(update, context): await mostrar(update, context, "robux")

async def cmmds(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start\n/cmmds\n/usd\n/mex\n/peru\n/colombia\n/guate\n/crobux\n/robux\n\n"
        "/set <comando> (solo admin)"
    )

# =====================
# EDITAR DESDE TELEGRAM
# =====================
async def set_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id not in ADMIN_IDS:
        await update.message.reply_text("⛔ Solo admins")
        return

    if not context.args:
        await update.message.reply_text("Uso: /set <comando>")
        return

    cmd = context.args[0]
    context.user_data["editando"] = cmd
    await update.message.reply_text(f"✏️ Envía el nuevo texto para /{cmd}")

async def recibir_texto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "editando" not in context.user_data:
        return

    cmd = context.user_data.pop("editando")
    datos[cmd] = update.message.text
    guardar_datos(datos)
    await update.message.reply_text(f"✅ /{cmd} actualizado")

# =====================
# BOT
# =====================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("cmmds", cmmds))
app.add_handler(CommandHandler("usd", usd))
app.add_handler(CommandHandler("mex", mex))
app.add_handler(CommandHandler("peru", peru))
app.add_handler(CommandHandler("colombia", colombia))
app.add_handler(CommandHandler("guate", guate))
app.add_handler(CommandHandler("crobux", crobux))
app.add_handler(CommandHandler("robux", robux))
app.add_handler(CommandHandler("set", set_cmd))

app.add_handler(CallbackQueryHandler(participar, pattern="participar"))
app.add_handler(CallbackQueryHandler(iniciar, pattern="iniciar"))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_texto))

print("🤖 Bot activo 24/7")
app.run_polling()

