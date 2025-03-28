from telebot import types
from bot.config import ADMIN_ID
from bot.database import (
    load_database,
    save_database,
    update_user,
    upgrade_user_to_premium
)


# ================================
# Handlers para Administrador (Admin)
# ================================
def register_handlers_admin(bot):
    """
    Handlers destinados a la administración del sistema.
    Solo el ADMIN_ID tiene acceso a estas funciones.
    """
    @bot.callback_query_handler(func=lambda call: call.data == "admin_panel")
    def admin_panel(call):
        data = load_database()
        user_admins = [u["user_id"] for u in data["usuarios"] if u.get('rol') == 'admin']
        
        if call.message.chat.id not in user_admins + [ADMIN_ID]:
            bot.send_message(call.message.chat.id, "❌ No tienes permiso para acceder a la administración.")
            return
        # Menú de administración con botones
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        btn_pending = types.KeyboardButton("📨 Solicitudes Pendientes")
        btn_all_users = types.KeyboardButton("👥 Ver Todos los Usuarios")
        btn_stats = types.KeyboardButton("📊 Estadísticas")
        btn_promote_admin = types.KeyboardButton("⭐ Promover a Administrador")
        btn_delete_user = types.KeyboardButton("❌ Eliminar Usuario")
        markup.add(btn_pending, btn_all_users, btn_stats, btn_delete_user, btn_promote_admin)
        bot.send_message(call.message.chat.id,
            "🔧 <b>Panel de Administración</b>\nSelecciona una opción:",
            parse_mode="HTML",
            reply_markup=markup)

    @bot.message_handler(func=lambda message: message.chat.id == ADMIN_ID and message.text == "📨 Solicitudes Pendientes")
    def pending_requests(message):
        """Lista las solicitudes pendientes de los usuarios y permite aceptarlas o rechazarlas."""
        data = load_database()
        pending = [u for u in data["usuarios"] if u.get("solicitud") in ("pendiente", "rechazada")]
        if not pending:
            bot.send_message(message.chat.id, "No hay solicitudes pendientes.")
            return
        
        # Mostrar usuarios con solicitudes pendientes enumerados
        response = "📨 <b>Solicitudes Pendientes:</b>\n"
        for idx, u in enumerate(pending, start=1):
            response += f"{idx}. @{u.get('username', 'Usuario')} (ID: {u.get('user_id')})\n"
        response += "\nPor favor, envía el número del usuario que deseas aceptar/rechazar o un rango de números separados por un guion (ejemplo: 1-3). Asegúrate de que los números sean válidos y correspondan a los usuarios listados:"
        bot.send_message(message.chat.id, response, parse_mode="HTML")
        
        bot.register_next_step_handler(message, lambda msg: validate_and_process_input(msg, "solicitude"))

    @bot.message_handler(func=lambda message: message.chat.id == ADMIN_ID and message.text == "👥 Ver Todos los Usuarios")
    def all_users(message):
        """Muestra la lista de todos los usuarios registrados."""
        data = load_database()
        if not data["usuarios"]:
            bot.send_message(message.chat.id, "No hay usuarios registrados.")
            return
        response = "👥 <b>Usuarios Registrados:</b>\n"
        for u in data["usuarios"]:
            response += f"• @{u.get('username', 'Usuario')} - Plan: {u.get('plan', 'Desconocido')}\n"
        bot.send_message(message.chat.id, response, parse_mode="HTML")

    @bot.message_handler(func=lambda message: message.chat.id == ADMIN_ID and message.text == "📊 Estadísticas")
    def statistics(message):
        """Muestra estadísticas básicas del sistema."""
        data = load_database()
        total_users = len(data["usuarios"])
        premium_users = len([u for u in data["usuarios"] if u.get("plan") == "premium"])
        basic_users = total_users - premium_users
        response = (
            "📊 <b>Estadísticas:</b>\n"
            f"• Total de usuarios: {total_users}\n"
            f"• Usuarios Premium: {premium_users}\n"
            f"• Usuarios Básicos: {basic_users}\n"
        )
        bot.send_message(message.chat.id, response, parse_mode="HTML")
    
    @bot.message_handler(func=lambda message: message.chat.id == ADMIN_ID and message.text == "⭐ Promover a Administrador")
    def promote_to_admin(message):
        """Promueve uno o varios usuarios a administrador."""
        data = load_database()
        if not data["usuarios"]:
            bot.send_message(message.chat.id, "No hay usuarios registrados.")
            return
        
        # Mostrar usuarios enumerados
        response = "👥 <b>Usuarios Registrados:</b>\n"
        for idx, u in enumerate(data["usuarios"], start=1):
            response += f"{idx}. @{u.get('username', 'Usuario')} (ID: {u.get('user_id')})\n"
        response += "\nPor favor, envía el número del usuario que deseas promover a administrador o un rango de números separados por un guion (ejemplo: 1-3). Asegúrate de que los números sean válidos y correspondan a los usuarios listados:"
        bot.send_message(message.chat.id, response, parse_mode="HTML")
        
        bot.register_next_step_handler(message, lambda msg: validate_and_process_input(msg, "promote"))

    @bot.message_handler(func=lambda message: message.chat.id == ADMIN_ID and message.text == "❌ Eliminar Usuario")
    def delete_user(message):
        """Elimina uno o varios usuarios del sistema."""
        data = load_database()
        if not data["usuarios"]:
            bot.send_message(message.chat.id, "No hay usuarios registrados.")
            return
        
        # Mostrar usuarios enumerados
        response = "👥 <b>Usuarios Registrados:</b>\n"
        for idx, u in enumerate(data["usuarios"], start=1):
            response += f"{idx}. @{u.get('username', 'Usuario')} (ID: {u.get('user_id')})\n"
        response += "\nPor favor, envía el número del usuario que deseas eliminar o un rango de números separados por un guion (ejemplo: 1-3). Asegúrate de que los números sean válidos y correspondan a los usuarios listados:"
        bot.send_message(message.chat.id, response, parse_mode="HTML")
        
        bot.register_next_step_handler(message, lambda msg: validate_and_process_input(msg, "delete"))

    @bot.callback_query_handler(func=lambda call: call.data.startswith("notificar_pago_"))
    def notify_admins(call):
        """
        Notifica a los administradores sobre un pago realizado por un usuario.
        """
        user_id = int(call.data.split("_")[-1])
        data = load_database()
        user = next((u for u in data["usuarios"] if u["user_id"] == user_id), None)

        if not user:
            bot.send_message(call.message.chat.id, "❌ Usuario no encontrado.")
            return

        # IDs de administradores: ADMIN_ID y usuarios con rol 'admin'
        admin_ids = [ADMIN_ID] + [u["user_id"] for u in data["usuarios"] if u.get("rol") == "admin"]

        for admin_id in admin_ids:
            bot.send_message(
                admin_id,
                f"📨 <b>Notificación de Pago</b>\n"
                f"El usuario @{user.get('username', 'Usuario')} (ID: {user['user_id']}) "
                "ha notificado un pago. Por favor, verifica y procesa la solicitud.",
                parse_mode="HTML"
            )

        bot.send_message(call.message.chat.id, "✅ Notificación enviada a los administradores.")
    
    # ================================
    # Función para validar y procesar la entrada del usuario
    # ================================
    def validate_and_process_input(msg, action):
        """
        Valida la entrada del usuario y procesa la acción correspondiente.

        Parámetros:
        - msg: Objeto mensaje de Telegram.
        - action: Acción a procesar ("solicitude", "promote" o "delete").
        """
        data = load_database()
        # IDs de administradores: ADMIN_ID y usuarios con rol 'admin'
        handler_ids = [ADMIN_ID] + [u["user_id"] for u in data["usuarios"] if u.get("rol") == "admin"]

        try:
            input_text = msg.text.strip()
            ids_to_process = []

            if action == "solicitude":
                # Se espera un formato: "1 A" o "1-5 D"
                parts = input_text.split()
                if len(parts) != 2 or parts[1] not in ["A", "D"]:
                    bot.send_message(msg.chat.id, "❌ Formato inválido. Usa el formato '1 A' o '1-5 D'.")
                    bot.register_next_step_handler(msg, lambda m: validate_and_process_input(m, action))
                    return

                range_part, decision = parts[0], parts[1]
                # Procesar rango de índices, por ejemplo "1-5"
                if "-" in range_part:
                    try:
                        start, end = map(int, range_part.split("-"))
                    except ValueError:
                        bot.send_message(msg.chat.id, "❌ Rango inválido. Asegúrate de usar números.")
                        bot.register_next_step_handler(msg, lambda m: validate_and_process_input(m, action))
                        return
                    if start > end or start < 1:
                        raise ValueError("Rango inválido.")
                    total_users = len(data["usuarios"])
                    if end > total_users:
                        bot.send_message(msg.chat.id, f"❌ El rango especificado excede el número de usuarios registrados ({total_users}).")
                        bot.register_next_step_handler(msg, lambda m: validate_and_process_input(m, action))
                        return
                    ids_to_process = [
                        {"user_id": data["usuarios"][i - 1]["user_id"], "decision": decision}
                        for i in range(start, end + 1)
                        if data["usuarios"][i - 1].get("solicitud") == "pendiente"
                    ]
                
                else:
                    try:
                        idx = int(range_part) - 1
                    except ValueError:
                        bot.send_message(msg.chat.id, "❌ Índice inválido. Debe ser un número.")
                        bot.register_next_step_handler(msg, lambda m: validate_and_process_input(m, action))
                        return
                    if idx < 0 or idx >= len(data["usuarios"]):
                        raise ValueError("Índice fuera de rango.")
                    user = data["usuarios"][idx]
                    ids_to_process = [{"user_id": user["user_id"], "decision": decision}]

                if not ids_to_process:
                    bot.send_message(msg.chat.id, "❌ No se encontraron solicitudes válidas para procesar.")
                    bot.register_next_step_handler(msg, lambda m: validate_and_process_input(m, action))
                    return

            elif action in ["promote", "delete"]:
                # Se espera formato simple: "1" o "1-5"
                if "-" in input_text:
                    try:
                        start, end = map(int, input_text.split("-"))
                    except ValueError:
                        bot.send_message(msg.chat.id, "❌ Formato inválido. Usa un rango válido como '1-3'.")
                        bot.register_next_step_handler(msg, lambda m: validate_and_process_input(m, action))
                        return
                    if start > end or start < 1:
                        raise ValueError("Rango inválido.")
                    ids_to_process = [data["usuarios"][i - 1] for i in range(start, end + 1) if i - 1 < len(data["usuarios"])]
                else:
                    try:
                        idx = int(input_text) - 1
                    except ValueError:
                        bot.send_message(msg.chat.id, "❌ Índice inválido. Debe ser un número.")
                        bot.register_next_step_handler(msg, lambda m: validate_and_process_input(m, action))
                        return
                    if idx < 0 or idx >= len(data["usuarios"]):
                        raise ValueError("Índice fuera de rango.")
                    ids_to_process = [data["usuarios"][idx]]

            # Evitar procesar a administradores
            if any(user["user_id"] in handler_ids for user in ids_to_process):
                bot.send_message(msg.chat.id, "❌ No puedes realizar esta acción en usuarios administradores.")
                return

            # Llamar a la función que procesa la acción final con los usuarios seleccionados
            process_user_input(msg, action, ids_to_process)

        except Exception as e:
            print("Error:", e)
            bot.send_message(msg.chat.id, "❌ Ocurrió un error. Por favor, intenta nuevamente.")
            bot.register_next_step_handler(msg, lambda m: validate_and_process_input(m, action))


    # ================================
    # Función para procesar entradas del usuario según la acción
    # ================================
    def process_user_input(msg, action, users_to_process):
        """
        Procesa la acción solicitada en los usuarios seleccionados.

        Parámetros:
        - msg: Objeto mensaje de Telegram.
        - action: Acción a procesar ("promote", "delete" o "solicitude").
        - users_to_process: Lista de usuarios o diccionarios con 'user_id' y, en el caso de "solicitude", 'decision'.
        """
        data = load_database()
        try:
            if not users_to_process:
                bot.send_message(msg.chat.id, "❌ No se encontraron usuarios para procesar.")
                return

            if action == "promote":
                # Promociona usuarios a rol "admin"
                for user in users_to_process:
                    user["rol"] = "admin"
                    update_user(user["user_id"], {"rol": user["rol"]})
                    bot.send_message(user["user_id"], f"✅ Haz sido promovido a administrador.")
                    bot.send_message(msg.chat.id, f"✅ Se le ha notificado al usuario @{user["username"]} que ha sido promovido a administrador.")
            elif action == "delete":
                # Elimina usuarios de la base de datos
                for user in users_to_process:
                    data["usuarios"].remove(user)
                save_database(data)
                bot.send_message(msg.chat.id, "✅ Usuario(s) eliminado(s) correctamente.")
            elif action == "solicitude":
                # Procesa solicitudes: 'A' para aceptar y 'D' para rechazar
                for user_data in users_to_process:
                    user_id, decision = user_data["user_id"], user_data["decision"]
                    user = next((u for u in data["usuarios"] if u["user_id"] == user_id), None)
                    if user:
                        user["solicitud"] = "aceptada" if decision == "A" else "rechazada"
                        if decision == "A":
                            # Asegúrate de definir o importar la función handle_pago
                            user = upgrade_user_to_premium(user["user_id"])
                            bot.send_message(user["user_id"],
                                f"🎉 <b>¡Felicidades!</b>\n\n"
                                f"✅ Tu pago ha sido confirmado y tu cuenta ha sido actualizada a Plan Premium.\n"
                                f"🔑 <b>Clave:</b> <code>{user['password']}</code>\n"
                                f"📅 <b>Inicio:</b> {user['fecha_inicio']}\n"
                                f"⏳ <b>Vencimiento:</b> {user['fecha_fin']}\n\n"
                                "¡Disfruta de todos los beneficios!",
                                parse_mode="HTML"
                                )
        
                            update_user(user["user_id"], {"solicitud": user["solicitud"], "plan": "premium", "pago" : True})
                        else:
                            bot.send_message(user["user_id"],
                                            "❌ Pago no confirmado. Realiza la transferencia y vuelve a intentarlo.")
                            update_user(user["user_id"], {"solicitud":"rechazada"})
                bot.send_message(msg.chat.id, "✅ Solicitud(es) procesada(s) correctamente.")
        except Exception as e:
            print("Error en process_user_input:", e)
            bot.send_message(msg.chat.id, "❌ Ocurrió un error al procesar la solicitud. Por favor, intenta nuevamente.")
