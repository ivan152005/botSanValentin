import logging
from telegram import Update, ForceReply
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

# Configuración del logging para depuración
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Token de tu bot (reemplaza por el token real)
TOKEN = "7582374391:AAEYVIaPhCqt7Hxb3QMeS2SW0ynF6FMNOJ8"

# Estados del ConversationHandler para el cuestionario /love
PASTIME, QUALITIES, DATE = range(3)

# Lista simulada de perfiles de usuarios para calcular afinidad
user_profiles = [
    {
        "name": "Ana",
        "pastime": "leer",
        "qualities": "amistosa divertida",
        "ideal_date": "cena romántica",
    },
    {
        "name": "Carlos",
        "pastime": "fútbol",
        "qualities": "aventurero sincero",
        "ideal_date": "cine y paseo",
    },
    {
        "name": "Lucía",
        "pastime": "pintar",
        "qualities": "creativa cariñosa",
        "ideal_date": "picnic en el parque",
    },
    {
        "name": "Miguel",
        "pastime": "videojuegos",
        "qualities": "divertido espontáneo",
        "ideal_date": "juegos de mesa y charla",
    },
]

def compute_affinity(user_data: dict) -> list:
    """
    Función que compara las respuestas del usuario con los perfiles de la lista
    y devuelve los 3 mejores matches.
    """
    def score(candidate: dict) -> int:
        s = 0
        # Sumar punto si el pasatiempo del usuario aparece en el candidato
        if user_data["pastime"].lower() in candidate["pastime"]:
            s += 1
        # Sumar puntos por coincidencias en las cualidades
        candidate_qualities = candidate["qualities"].split()
        user_qualities = user_data["qualities"].lower().split()
        s += sum(1 for q in user_qualities if q in candidate_qualities)
        # Sumar punto si la cita ideal del usuario se encuentra en la del candidato
        if user_data["ideal_date"].lower() in candidate["ideal_date"]:
            s += 1
        return s

    scored_candidates = [(score(candidate), candidate) for candidate in user_profiles]
    scored_candidates.sort(key=lambda x: x[0], reverse=True)
    top3 = [candidate for score_val, candidate in scored_candidates][:3]
    return top3

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /start: Envía un mensaje de bienvenida personalizado."""
    user = update.effective_user
    mensaje = (
        f"¡Hola {user.first_name}! Bienvenido al bot de Cupido lanzado desde el Virgen de Gracia.\n"
        "Aquí podrás encontrar a tu pareja perfecta. ¡Prepárate para enamorarte!"
    )
    await update.message.reply_text(mensaje, reply_markup=ForceReply(selective=True))

async def love(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Comando /love: Inicia el cuestionario para encontrar la pareja ideal."""
    await update.message.reply_text("Pregunta 1: ¿Cuál es tu pasatiempo favorito?")
    return PASTIME

async def get_pastime(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["pastime"] = update.message.text
    await update.message.reply_text("Pregunta 2: ¿Qué cualidades valoras en una pareja?")
    return QUALITIES

async def get_qualities(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["qualities"] = update.message.text
    await update.message.reply_text("Pregunta 3: ¿Cómo sería tu cita ideal?")
    return DATE

async def get_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["ideal_date"] = update.message.text
    # Procesar respuestas y calcular afinidad
    matches = compute_affinity(context.user_data)
    if matches:
        response = "Estos son tus 3 mejores matches:\n"
        for match in matches:
            response += f"- {match['name']}\n"
    else:
        response = "No se encontraron coincidencias."
    await update.message.reply_text(response)
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Permite cancelar el cuestionario en cualquier momento."""
    await update.message.reply_text("Cuestionario cancelado. Puedes iniciar de nuevo con /love")
    return ConversationHandler.END

async def back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /back: Permite regresar al inicio del cuestionario."""
    mensaje = "Has elegido volver atrás. Si deseas reiniciar el cuestionario, escribe /start."
    await update.message.reply_text(mensaje)

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /stop: Finaliza la sesión o cancela el cuestionario en curso."""
    mensaje = "La sesión ha sido detenida. Para reiniciar, escribe /start."
    await update.message.reply_text(mensaje)

def main() -> None:
    """Inicia el bot."""
    application = Application.builder().token(TOKEN).build()

    # Comandos básicos
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("back", back))
    application.add_handler(CommandHandler("stop", stop))

    # ConversationHandler para el cuestionario /love
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("love", love)],
        states={
            PASTIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_pastime)],
            QUALITIES: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_qualities)],
            DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_date)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    application.add_handler(conv_handler)

    # Ejecuta el bot hasta que el usuario presione Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()