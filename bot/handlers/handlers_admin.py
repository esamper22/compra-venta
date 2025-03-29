from telebot import types
from bot.config import SUPER_ADMIN
from bot.utils import parse_id_list, parse_solicitude_list
from controller.queries import (
    get_admins,
    load_database,
    save_database,
    update_user,
    get_user_id,
    upgrade_user_to_premium,
    check_is_admin
)

# ================================
# Handlers para Administrador (Admin)
# ================================
def register_handlers_admin(bot):
    """
    Registra los handlers de administración.
    Solo pueden acceder aquellos cuyo ID esté en la lista de admins o sea el SUPER_ADMIN.
    """
    @bot.callback_query_handler(func=lambda call: call.data == "admin_panel")
    def admin_panel(call):
        data = load_database()
        # Obtener los IDs de administradores
        user_admins = [u["user_id"] for u in data["usuarios"] if u.get('rol') == 'admin']
        if call.message.chat.id not in user_admins + [SUPER_ADMIN['user_id']]:
            bot.send_message(call.message.chat.id, "❌ No tienes permiso para acceder a la administración.")
            return

        # Menú de administración con botones
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        btn_pending = types.KeyboardButton("📨 Solicitudes Pendientes")
        btn_all_users = types.KeyboardButton("👥 Ver Todos los Usuarios")
        btn_stats = types.KeyboardButton("📊 Estadísticas")
        btn_promote_admin = types.KeyboardButton("🔝 Promover a Admin")
        btn_delete_user = types.KeyboardButton("❌ Eliminar Usuario")
        btn_demote_admin = types.KeyboardButton("🔻 Despromover Admin")
        markup.add(btn_pending, btn_all_users, btn_stats, btn_delete_user, btn_promote_admin, btn_demote_admin)
        bot.send_message(call.message.chat.id,
            "🔧 <b>Panel de Administración</b>\nSelecciona una opción:",
            parse_mode="HTML",
            reply_markup=markup)

    @bot.message_handler(func=lambda message: message.chat.id in check_is_admin() and message.text == "📨 Solicitudes Pendientes")
    def pending_requests(message):
        """Lista las solicitudes pendientes de los usuarios (solicitud 'pendiente' o 'rechazada')."""
        data = load_database()
        pending = [u for u in data["usuarios"] if u.get("solicitud") in ("pendiente", "rechazada")]
        if not pending:
            bot.send_message(message.chat.id, "No hay solicitudes pendientes.")
            return
        
        response = "📨 <b>Solicitudes Pendientes:</b>\n"
        for u in pending:
            response += f"• @{u.get('username', 'Usuario')} (ID: {u.get('user_id')})\n"
        response += ("\nEnvía los IDs de los usuarios y su decisión (A para aceptar, D para rechazar) separados por comas.\n"
                     "Ejemplo: '12345 A,67890 D'\n"
                     "Escribe 0 para cancelar.")
        bot.send_message(message.chat.id, response, parse_mode="HTML")
        bot.register_next_step_handler(message, lambda msg: validate_and_process_input(msg, "solicitude"))

    @bot.message_handler(func=lambda message: message.chat.id in check_is_admin() and message.text == "👥 Ver Todos los Usuarios")
    def all_users(message):
        """Muestra la lista de todos los usuarios registrados, junto con su rol y plan."""
        data = load_database()
        if not data["usuarios"]:
            bot.send_message(message.chat.id, "No hay usuarios registrados.")
            return
        response = "👥 <b>Usuarios Registrados:</b>\n"
        for u in data["usuarios"]:
            response += f"• @{u.get('username', 'Usuario')} - Plan: {u.get('plan', 'Desconocido')} - Rol: {u.get('rol', 'N/A')}\n"
        bot.send_message(message.chat.id, response, parse_mode="HTML")

    @bot.message_handler(func=lambda message: message.chat.id in check_is_admin() and message.text == "📊 Estadísticas")
    def statistics(message):
        """Muestra estadísticas del sistema, incluyendo roles de usuarios."""
        data = load_database()
        total_users = len(data["usuarios"])
        premium_users = len([u for u in data["usuarios"] if u.get("plan") == "premium"])
        basic_users = total_users - premium_users
        admin_users = len([u for u in data["usuarios"] if u.get("rol") == "admin"])
        response = (
            "📊 <b>Estadísticas:</b>\n"
            f"• Total de usuarios: {total_users}\n"
            f"• Usuarios Premium: {premium_users}\n"
            f"• Usuarios Básicos: {basic_users}\n"
            f"• Administradores: {admin_users}\n"
        )
        bot.send_message(message.chat.id, response, parse_mode="HTML")
    
    @bot.message_handler(func=lambda message: message.chat.id in check_is_admin() and message.text == "🔝 Promover a Admin")
    def promote_to_admin(message):
        """Promueve uno o varios usuarios a administrador utilizando sus IDs."""
        data = load_database()
        if not data["usuarios"]:
            bot.send_message(message.chat.id, "No hay usuarios registrados.")
            return
        
        # Mostrar lista de usuarios (excluyendo al administrador que envía el comando)
        response = "👥 <b>Usuarios Registrados:</b>\n"
        for u in data["usuarios"]:
            if u.get("user_id") != message.chat.id:
                response += f"• @{u.get('username', 'Usuario')} (ID: {u.get('user_id')})\n"
        response += ("\nEnvía los IDs de los usuarios que deseas promover, separados por comas.\n"
                     "Ejemplo: '12345,67890'\n"
                     "Escribe 0 para cancelar.")
        bot.send_message(message.chat.id, response, parse_mode="HTML")
        bot.register_next_step_handler(message, lambda msg: validate_and_process_input(msg, "promote"))

    @bot.message_handler(func=lambda message: message.chat.id in check_is_admin() and message.text == "❌ Eliminar Usuario")
    def delete_user(message):
        """Elimina uno o varios usuarios del sistema utilizando sus IDs."""
        data = load_database()
        if not data["usuarios"]:
            bot.send_message(message.chat.id, "No hay usuarios registrados.")
            return
        
        response = "👥 <b>Usuarios Registrados:</b>\n"
        for u in data["usuarios"]:
            if u.get("user_id") != message.chat.id:
                response += f"• @{u.get('username', 'Usuario')} (ID: {u.get('user_id')})\n"
        response += ("\nEnvía los IDs de los usuarios que deseas eliminar, separados por comas.\n"
                     "Ejemplo: '12345,67890'\n"
                     "Escribe 0 para cancelar.")
        bot.send_message(message.chat.id, response, parse_mode="HTML")
        bot.register_next_step_handler(message, lambda msg: validate_and_process_input(msg, "delete"))

    @bot.message_handler(func=lambda message: message.chat.id == SUPER_ADMIN.get("user_id") and message.text == "🔻 Despromover Admin")
    def demote_admin(message):
        """Despromueve uno o varios administradores (excepto el superadmin) utilizando sus IDs."""
        data = load_database()
        response = "👥 <b>Administradores Actuales:</b>\n"
        admins = [u for u in data["usuarios"] if u.get("rol") == "admin" and u.get("user_id") != SUPER_ADMIN.get("user_id")]
        if not admins:
            bot.send_message(message.chat.id, "No hay administradores para despromover.")
            return
        for u in admins:
            response += f"• @{u.get('username', 'Usuario')} (ID: {u.get('user_id')})\n"
        response += ("\nEnvía los IDs de los administradores que deseas despromover, separados por comas.\n"
                     "Ejemplo: '12345,67890'\n"
                     "Escribe 0 para cancelar.")
        bot.send_message(message.chat.id, response, parse_mode="HTML")
        bot.register_next_step_handler(message, lambda msg: validate_and_process_input(msg, "demote"))

    # ================================
    # Función para validar y procesar la entrada del usuario
    # ================================
    def validate_and_process_input(msg, action):
        """
        Valida la entrada del usuario y procesa la acción correspondiente.
        Permite ingresar múltiples IDs separados por comas.
        
        Parámetros:
          - msg: Objeto mensaje de Telegram.
          - action: Acción a procesar ("solicitude", "promote", "delete" o "demote").
        """
        data = load_database()
        # Obtener los IDs de administradores para evitar que se procese alguno
        handler_ids = get_admins()

        try:
            input_text = msg.text.strip()
            # Si se ingresa "0", se cancela la acción
            if input_text == "0":
                bot.send_message(msg.chat.id, "❌ Has cancelado la acción.")
                return

            ids_to_process = []
            if action == "solicitude":
                # Espera formato: "userID decision" separados por comas, ejemplo: "12345 A,67890 D"
                solicitudes = parse_solicitude_list(input_text)
                if not solicitudes:
                    bot.send_message(msg.chat.id, "❌ Formato inválido. Usa el formato '12345 A,67890 D'.")
                    bot.register_next_step_handler(msg, lambda m: validate_and_process_input(m, action))
                    return
                ids_to_process = solicitudes
            elif action in ["promote", "delete", "demote"]:
                # Espera una lista de IDs separados por comas, ejemplo: "12345,67890"
                id_list = parse_id_list(input_text)
                if not id_list:
                    bot.send_message(msg.chat.id, "❌ Formato inválido. Asegúrate de ingresar números separados por comas.")
                    bot.register_next_step_handler(msg, lambda m: validate_and_process_input(m, action))
                    return
                # Convertir cada ID en el formato esperado (para promote, delete o demote)
                ids_to_process = id_list

            # Verificar que no se procese ningún usuario administrador (excepto en demote, que solo debe aplicarse a admins)
            if action in ["promote", "delete"]:
                if any(user_id in handler_ids for user_id in ids_to_process):
                    bot.send_message(msg.chat.id, "❌ No puedes realizar esta acción en usuarios administradores.")
                    return

            # Llamar a la función que procesa la acción final
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
        Procesa la acción solicitada en base a los IDs proporcionados.
        
        Parámetros:
          - msg: Objeto mensaje de Telegram.
          - action: Acción a procesar ("promote", "delete", "solicitude" o "demote").
          - users_to_process: Lista de IDs (para promote, delete o demote) o lista de diccionarios (para solicitude).
        """
        data = load_database()
        try:
            if not users_to_process:
                bot.send_message(msg.chat.id, "❌ No se encontraron usuarios para procesar.")
                return

            if action == "promote":
                # Promover a admin: procesar cada ID
                for user_id in users_to_process:
                    user = get_user_id(user_id)
                    if user:
                        update_user(user_id, {"rol": "admin"})
                        bot.send_message(user_id, "✅ Haz sido promovido a administrador.")
                        bot.send_message(msg.chat.id, f"✅ Usuario @{user.get('username')} promovido a administrador.")
                    else:
                        bot.send_message(msg.chat.id, f"❌ Usuario con ID {user_id} no encontrado.")
            elif action == "delete":
                # Eliminar usuarios
                removed_users = []
                for user_id in users_to_process:
                    user = get_user_id(user_id)
                    if user:
                        data["usuarios"].remove(user)
                        removed_users.append(user.get("username", str(user_id)))
                    else:
                        bot.send_message(msg.chat.id, f"❌ Usuario con ID {user_id} no encontrado.")
                save_database(data)
                if removed_users:
                    bot.send_message(msg.chat.id, f"✅ Usuario(s) {', '.join(removed_users)} eliminado(s) correctamente.")
            elif action == "demote":
                # Despromover usuarios administradores (excepto el superadmin)
                for user_id in users_to_process:
                    # Evitar despromover al superadmin
                    if user_id == SUPER_ADMIN.get("user_id"):
                        bot.send_message(msg.chat.id, "❌ No puedes despromover al superadmin.")
                        continue
                    user = get_user_id(user_id)
                    if user and user.get("rol") == "admin":
                        update_user(user_id, {"rol": "usuario"})
                        bot.send_message(user_id, "⚠️ Has sido despromovido y ya no eres administrador.")
                        bot.send_message(msg.chat.id, f"✅ Usuario @{user.get('username')} despromovido correctamente.")
                    else:
                        bot.send_message(msg.chat.id, f"❌ Usuario con ID {user_id} no es administrador o no se encontró.")
            elif action == "solicitude":
                # Procesar solicitudes: se reciben diccionarios con user_id y decision
                for item in users_to_process:
                    user_id, decision = item["user_id"], item["decision"]
                    user = get_user_id(user_id)
                    if user:
                        if decision == "A":
                            # Actualiza al plan premium
                            user = upgrade_user_to_premium(user_id)
                            bot.send_message(user_id,
                                f"🎉 <b>¡Felicidades!</b>\n\n"
                                f"✅ Tu pago ha sido confirmado y tu cuenta ha sido actualizada a Plan Premium.\n\n"
                                f"👤 <b>Usuario:</b> <code>{user['username']}</code>\n"
                                f"🔑 <b>Clave:</b> <code>{user['password']}</code>\n"
                                f"📅 <b>Inicio:</b> {user['fecha_inicio']}\n"
                                f"⏳ <b>Vencimiento:</b> {user['fecha_fin']}\n\n"
                                "¡Disfruta de todos los beneficios!",
                                parse_mode="HTML")
                        else:
                            bot.send_message(user_id,
                                "❌ Tu solicitud ha sido rechazada. Realiza la transferencia y vuelve a intentarlo.")
                        update_user(user_id, {"solicitud": "aceptada" if decision == "A" else "rechazada"})
                    else:
                        bot.send_message(msg.chat.id, f"❌ Usuario con ID {user_id} no encontrado.")
                bot.send_message(msg.chat.id, "✅ Solicitud(es) procesada(s) correctamente.")
        except Exception as e:
            print("Error en process_user_input:", e)
            bot.send_message(msg.chat.id, "❌ Ocurrió un error al procesar la solicitud. Por favor, intenta nuevamente.")
