import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackContext,
    ConversationHandler
)
from diccionarioAUtilizar import personas

# Token de mi bot
TOKEN = "7918204738:AAFK08lFWmyFuUVX8I3g4igNUKxMo8Yrjcw"

# Configuración del logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Estados para el ConversationHandler
GRADO, FIN, HIJOS = range(3)

async def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    mensaje = (
        f"Hola {user.first_name}, bienvenido al bot de Cupido lanzado desde el Virgen de Gracia.\n"
        "Utiliza /love para comenzar el cuestionario y encontrar tu pareja perfecta."
    )
    await update.message.reply_text(mensaje)

async def love(update: Update, context: CallbackContext) -> int:
    context.user_data["current_state"] = GRADO
    keyboard = [["Informatica", "Deporte", "Comercio", "Mecanizado"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("Pregunta 1: ¿Cuál es tu área de interés?", reply_markup=reply_markup)
    return GRADO

async def grado(update: Update, context: CallbackContext) -> int:
    respuesta = update.message.text
    if respuesta not in ["Informatica", "Deporte", "Comercio", "Mecanizado"]:
        await update.message.reply_text("Selecciona una opción válida.")
        return GRADO
    context.user_data["grado"] = respuesta
    context.user_data["current_state"] = FIN
    keyboard = [["Relacion estable", "Nada serio", "Duda"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("Pregunta 2: ¿Qué tipo de relación buscas?", reply_markup=reply_markup)
    return FIN

async def fin(update: Update, context: CallbackContext) -> int:
    answer = update.message.text
    if answer not in ["Relacion estable", "Nada serio", "Duda"]:
        await update.message.reply_text("Selecciona una opción válida.")
        return FIN
    context.user_data["fin"] = answer
    context.user_data["current_state"] = HIJOS
    keyboard = [["Si quiero", "No quiero", "Duda"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("Pregunta 3: ¿Qué opinas sobre tener hijos?", reply_markup=reply_markup)
    return HIJOS

async def hijos(update: Update, context: CallbackContext) -> int:
    respuesta = update.message.text
    if respuesta not in ["Si quiero", "No quiero", "Duda"]:
        await update.message.reply_text("Selecciona una opción válida.")
        return HIJOS
    context.user_data["hijos"] = respuesta

    # Calcula los matches comparando cada respuesta con los datos de los candidatos
    matches = comparar_datos(context.user_data, personas)
    response = "Estos son tus 3 mejores matches:\n\n"
    if not matches:
        response += "No se encontraron coincidencias."
    else:
        for match in matches:
            response += (
                f"{match['NombreCompleto']}, Edad: {match['Edad']}, Sexo: {match['Sexo']}, "
                f"Área: {match['Grado']}, Relación: {match['Fin']}, Hijos: {match['Hijos']}\n\n"
            )
    await update.message.reply_text(response)
    return ConversationHandler.END

def comparar_datos(user_data: dict, candidatos: dict) -> list:
    scored = []
    for persona in candidatos.values():
        score = 0
        if persona.get("Grado") == user_data.get("grado"):
            score += 1
        if persona.get("Fin") == user_data.get("fin"):
            score += 1
        if persona.get("Hijos") == user_data.get("hijos"):
            score += 1
        scored.append((score, persona))
    scored.sort(key=lambda x: x[0], reverse=True)
    top_matches = [persona for score, persona in scored if score > 0][:3]
    return top_matches

async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("El cuestionario ha sido cancelado. Usa /love para intentarlo de nuevo.")
    return ConversationHandler.END

async def back(update: Update, context: CallbackContext) -> int:
    # Obtenemos el estado actual
    current_state = context.user_data.get("current_state", GRADO)
    if current_state == FIN:
        # Eliminamos la respuesta de la pregunta 2
        context.user_data.pop("fin", None)
        context.user_data["current_state"] = GRADO
        keyboard = [["Informatica", "Deporte", "Comercio", "Mecanizado"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text("Volviendo a la Pregunta 1: ¿Cuál es tu área de interés?", reply_markup=reply_markup)
        return GRADO
    elif current_state == HIJOS:
        # Eliminamos la respuesta de la pregunta 3
        context.user_data.pop("hijos", None)
        context.user_data["current_state"] = FIN
        keyboard = [["Relacion estable", "Nada serio", "Duda"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text("Volviendo a la Pregunta 2: ¿Qué tipo de relación buscas?", reply_markup=reply_markup)
        return FIN
    else:
        await update.message.reply_text("No se puede retroceder más.")
        return current_state

def main():
    app = Application.builder().token(TOKEN).build()

    # Registra el comando /start globalmente
    app.add_handler(CommandHandler("start", start))

    # ConversationHandler para el flujo del cuestionario, que incluye /love, /stop y /back
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("love", love)],
        states={
            GRADO: [MessageHandler(filters.TEXT & ~filters.COMMAND, grado)],
            FIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, fin)],
            HIJOS: [MessageHandler(filters.TEXT & ~filters.COMMAND, hijos)]
        },
        fallbacks=[
            CommandHandler("stop", cancel),
            CommandHandler("back", back)
        ]
    )
    app.add_handler(conv_handler)

    app.run_polling()

if __name__ == "__main__":
    main()
