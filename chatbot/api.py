import frappe
from chat.api.message import send
@frappe.whitelist()
def send_direct_message_from_bot(chat_bot, content):
    """
    Send a message from a Chat Bot to a user through a direct chat room.
    
    Args:
        chat_bot (str): The name of the Chat Bot doctype instance.
        content (str): The message content.
    """
    # Retrieve the Chat Bot document
    chat_bot_doc = frappe.get_doc("Chat Bot", chat_bot)
    
    # Retrieve the direct chat room
    direct_chat_room = chat_bot_doc.direct_chat_room
    
    # Send the message
    send(
        content=content,
        user=chat_bot_doc.user,
        room=direct_chat_room,
        email=chat_bot_doc.user
    )

@frappe.whitelist()
def send_group_message_on_task(task_name, content):
    """
    Send a message to a group chat room upon task creation.
    
    Args:
        task_name (str): The name of the task doctype instance.
        content (str): The message content.
    """
    # Retrieve task document
    task_doc = frappe.get_doc("Customer Task", task_name)
    
    # Retrieve the chat bot associated with the poster_user
    poster_user_doc = frappe.get_doc("User", task_doc.poster_user)
    chat_bot_doc = frappe.get_doc("Chat Bot", task_doc.chat_bot)
    rooms = get(email=chat_bot_doc.user, task=task_name)
    
    if rooms:
        # Assuming that the relevant chat room is the first one returned
        room_name = rooms[0]['name']
        
        # Send the message
        send(
            content=content,
            user=chat_bot_doc.user,
            room=room_name,
            email=chat_bot_doc.user
        )
    else:
        frappe.throw(_("No chat room found for the given task."))
