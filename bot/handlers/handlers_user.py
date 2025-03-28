from telebot import types
from bot.config import ADMIN_ID
from bot.database import (
    load_database, update_user,
    create_first_user, get_user_id
)

# ================================
# Handlers para Usuario (User)
# ================================
def register_handlers_user(bot):
    """Registra los manejadores de eventos para el usuario."""
        
    @bot.message_handler(commands=['start'])
    def start_command(message):
        """Inicia la interacción con el usuario y crea el registro si no existe."""
        
        if is_admin(message): return
        
        username = message.from_user.username or message.from_user.first_name
        created = create_first_user(message.chat.id, username)
        # Definir el menú principal con botones de teclado
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn_plan = types.KeyboardButton("Solicitar Plan 💰")
        btn_help = types.KeyboardButton("Ayuda ℹ️")
        btn_webapp = types.KeyboardButton("Acceder a la MiniApp 🌐")
        btn_group = types.KeyboardButton("Unirse al Grupo 📢")
        btn_contact = types.KeyboardButton("Contactar Soporte 📞")
        btn_account = types.KeyboardButton("Estado de cuenta 📊")
        markup.add(btn_plan, btn_help)
        markup.add(btn_webapp, btn_group)
        markup.add(btn_contact, btn_account)

        welcome_msg = (
            f"👋 ¡Hola, {username}! 🎉\n\n"
            "💼 Bienvenido al sistema de automatización de Compra-Venta más eficiente y confiable. 🚀\n\n"
            "🔑 ¿Quieres optimizar tu tiempo, gestionar tus publicaciones y acceder a herramientas exclusivas "
            "que impulsarán tus ventas? ¡Solicita un plan ahora mismo y lleva tu negocio al siguiente nivel! 💰\n\n"
            "⬇️ Usa los botones de abajo para explorar nuestras opciones y comenzar tu experiencia:"
        )
        again_msg = (
            f"👋 ¡Hola de nuevo, {username}! 🎉\n\n"
            "💼 Nos alegra verte de vuelta en el sistema de Compra-Venta más eficiente y confiable. 🚀\n\n"
            "🔑 ¿Listo para continuar optimizando tu tiempo y gestionando tus publicaciones? "
            "Explora nuestras herramientas exclusivas y lleva tu negocio al siguiente nivel. 💰\n\n"
            "⬇️ Usa los botones de abajo para continuar tu experiencia:"
        )

        if created:
            bot.send_message(message.chat.id, welcome_msg, reply_markup=markup)  
        else: 
            bot.send_message(message.chat.id, again_msg, reply_markup=markup)
        
    @bot.message_handler(func=lambda message: message.text == "Solicitar Plan 💰")
    def solicitar_plan(message):
        """Permite al usuario solicitar un plan, enviando botones inline para confirmar el pago."""
        user = get_user_id(message.chat.id)

        if not user:
            bot.send_message(message.chat.id, "❌ Usuario no encontrado. Por favor, usa /start para registrarte.")
            return

        # Verificar el estado actual de la solicitud
        solicitud = user.get("solicitud")
        if solicitud == "pendiente":
            bot.send_message(message.chat.id,
                "📨 Tu solicitud ya ha sido enviada y está en proceso de revisión. "
                "Por favor, espera a que sea confirmada. Si tienes dudas, contacta a soporte: @samperfree (SuperAdmin).")
            return
        elif solicitud == "rechazada":
            bot.send_message(message.chat.id,
                "❌ Tu solicitud ha sido rechazada. Realiza el pago para continuar con el proceso.")
            return
        elif solicitud == "aceptada":
            bot.send_message(message.chat.id,
                "✨ Tu solicitud ya ha sido procesada. Revisa tu estado actual o contacta a soporte si tienes dudas.")
            return


        if not user.get("notificado", False):
            bot.send_message(message.chat.id,
                "📨 Tu solicitud ya ha sido enviada y está en proceso de revisión. "
                "Realiza el pago y espera a que sea confirmado.\n\n"
                "💳 <b>Información de Pago:</b>\n"
                "🔢 <b>Número de Tarjeta:</b> <code>9224 0699 9059 4463</code>\n"
                "📞 <b>Número a Confirmar:</b> <code>56720773</code>\n\n"
                "🔍 <b>Estado de tu solicitud:</b> Puedes verificar el estado de tu solicitud en la opción 'Estado de cuenta 📊' del menú principal.\n\n"
                "✨ Si tienes dudas, contacta a soporte: @samperfree (SuperAdmin).",
                parse_mode="HTML")
            update_user(message.chat.id, {"notificado": True, "solicitud": "pendiente", "pago": False})
           
    @bot.message_handler(func=lambda message: message.text == "Ayuda ℹ️")
    def help_command(message):
        """Muestra la lista de comandos disponibles."""
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn_menu = types.KeyboardButton("Menú Principal 🏠")
        markup.add(btn_menu)
        bot.send_message(message.chat.id,
            "ℹ️ <b>Comandos disponibles:</b>\n\n"
            "🔹 /start - Iniciar el bot y acceder al menú principal.\n"
            "🔹 Solicitar Plan 💰 - Solicitar un plan para mejorar tu cuenta.\n"
            "🔹 Ayuda ℹ️ - Ver esta lista de comandos.\n"
            "🔹 Acceder a la MiniApp 🌐 - Accede a nuestra MiniApp para gestionar tus publicaciones.\n"
            "🔹 Unirse al Grupo 📢 - Únete a nuestro grupo.\n"
            "🔹 Contactar Soporte 📞 - Contacta al soporte técnico.\n"
            "🔹 Estado de cuenta 📊 - Consulta el estado de tu cuenta.\n\n"
            "⬇️ Usa el botón de abajo para volver al menú principal.",
            parse_mode="HTML",
            reply_markup=markup)

    @bot.message_handler(func=lambda message: message.text == "Contactar Soporte 📞")
    def soporte_command(message):
        """Envía información de contacto para soporte técnico."""
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn_menu = types.KeyboardButton("Menú Principal 🏠")
        markup.add(btn_menu)
        bot.send_message(message.chat.id,
            "📞 <b>Soporte Técnico:</b>\n\n"
            "🔹 Telegram: @samperfree\n"
            "🔹 Correo: <a href='mailto:sampere0111@gmail.com'>sampere0111@gmail.com</a>\n\n"
            "<a href='https://t.me/samperfree'><b>👤 Ver perfil de soporte</b></a>\n\n"
            "⬇️ Usa el botón de abajo para volver al menú principal.",
            parse_mode="HTML",
            reply_markup=markup)

    @bot.message_handler(func=lambda message: message.text == "Menú Principal 🏠")
    def menu_principal(message):
        """Vuelve al menú principal reinvocando el comando /start."""
        start_command(message)

    @bot.message_handler(func=lambda message: message.text == "Acceder a la MiniApp 🌐")
    def acceder_miniapp(message):
        """Proporciona un botón inline para acceder a la MiniApp."""
        markup = types.InlineKeyboardMarkup()
        btn_access = types.InlineKeyboardButton("🌐 Acceder a la MiniApp", web_app=types.WebAppInfo(url="https://esamper22.github.io/mi-portfolio/"))
        markup.add(btn_access)
        bot.send_message(message.chat.id,
            "🌐 <b>Acceso a la MiniApp:</b>\n\n"
            "Gestiona tus publicaciones y accede a herramientas exclusivas para impulsar tus ventas.\n\n"
            "✨ Haz clic en el botón de abajo para comenzar.\n\n"
            "Si necesitas ayuda, contacta a soporte.",
            parse_mode="HTML",
            reply_markup=markup)

    @bot.message_handler(func=lambda message: message.text == "Unirse al Grupo 📢")
    def unirse_grupo(message):
        """Envía un botón inline para unirse al grupo."""
        markup = types.InlineKeyboardMarkup()
        btn_join = types.InlineKeyboardButton("📢 Unirse al Grupo", url="https://t.me/examplegroup")
        markup.add(btn_join)
        bot.send_photo(message.chat.id,
            photo="https://cdn.pixabay.com/photo/2025/02/17/16/04/dog-9413394_960_720.jpg",
            caption=("📢 <b>Únete a nuestro grupo:</b>\n\n"
                     "Conéctate con otros usuarios y mantente informado sobre novedades y promociones.\n\n"
                     "✨ Haz clic en el botón para unirte ahora.\n\n"
                     "¡Te esperamos!"),
            parse_mode="HTML",
            reply_markup=markup)

    @bot.message_handler(func=lambda message: message.text == "Estado de cuenta 📊")
    def mi_cuenta(message):
        """Muestra el estado de cuenta del usuario."""
        data = load_database()
        user = next((u for u in data["usuarios"] if u.get("user_id") == message.chat.id), None)
        if not user:
            bot.send_message(message.chat.id,
                "❌ <b>¡Ups! No encontramos información de tu cuenta.</b>\n\n"
                "Asegúrate de haberte registrado usando /start. Si el problema persiste, contacta a soporte.",
                parse_mode="HTML")
            return

        if user.get("plan") == "premium":
            bot.send_message(message.chat.id,
                f"🌟 <b>¡Bienvenido a tu cuenta Premium!</b> 🌟\n\n"
                f"🔑 <b>Clave:</b> <code>{user['password']}</code>\n"
                f"📅 <b>Inicio:</b> {user['fecha_inicio']}\n"
                f"⏳ <b>Vencimiento:</b> {user['fecha_fin']}\n"
                f"🔹 <b>Rol:</b> {user['rol']}\n"
                f"🔹 <b>Solicitud Premium:</b> {user['solicitud']}\n"
                f"🔹 <b>Pago:</b> {'Realizado' if user['pago'] else 'No Realizado'}\n\n"
                "¡Disfruta de los beneficios exclusivos!",
                parse_mode="HTML")
        elif user.get("plan") == "basico":
            if "pago" in user:
                bot.send_message(message.chat.id,
                    f"👤 <b>Tu cuenta Básica:</b>\n\n"
                    f"🔹 <b>Rol:</b> {user['rol']}\n"
                    f"🔹 <b>Solicitud Premium:</b> {user['solicitud']}\n"
                    f"🔹 <b>Pago:</b> {'Realizado' if user['pago'] else 'No Realizado'}\n\n"
                    "Actualiza a Premium para disfrutar de herramientas avanzadas.",
                    parse_mode="HTML")
                # Agregar botón para notificar a los administradores sobre el pago
                markup = types.InlineKeyboardMarkup()
                btn_notify_admin = types.InlineKeyboardButton(
                    "📨 Notificar a los Administradores",
                    callback_data=f"notificar_pago_{message.chat.id}"
                )
                markup.add(btn_notify_admin)
                bot.send_message(message.chat.id,
                    "🔔 Si ya realizaste el pago, notifica a los administradores para que puedan procesar tu solicitud.",
                    reply_markup=markup)
            else:
                bot.send_message(message.chat.id,
                    f"👤 <b>Tu cuenta Básica:</b>\n\n"
                    f"🔹 <b>Rol:</b> {user['rol']}\n"
                    f"🔹 <b>Solicitud Premium:</b> {user['solicitud']}\n\n"
                    "Actualiza a Premium para disfrutar de herramientas avanzadas.",
                    parse_mode="HTML")
        else:
            bot.send_message(message.chat.id,
                "❌ <b>No has solicitado un plan aún.</b>\nSolicita un plan para acceder a herramientas exclusivas.",
                parse_mode="HTML")

    # ================================
    # Función para procesar si el usuario es administrador
    # ================================
    def is_admin(message):
        if message.chat.id == ADMIN_ID:
            # Agregar botón inline para ejecutar el comando /admin
            markup = types.InlineKeyboardMarkup()
            btn_admin = types.InlineKeyboardButton("Panel Administrativo", callback_data="admin_panel")
            markup.add(btn_admin)
            bot.send_message(message.chat.id, "👨‍💼 Bienvenido al panel de administración. Selecciona una opción:", reply_markup=markup)
            return True
        
        return False
