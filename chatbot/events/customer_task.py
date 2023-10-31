import frappe


def create_task_chat(room_name, users, room_type="Group", task=None, chat_bot=None):
    """
    Create a task-related chat room involving the user, poster user, and chatbot.

    Args:
        room_name (str): Room name
        users (list): List of user email addresses in room
        room_type (str): Type of room, default is "Group"
        task (str, optional): Task associated with room, defaults to None
    """
    members = ", ".join(users)

    # Check if a room with the same name already exists
    if frappe.db.exists("Chat Room", {"room_name": room_name}):
        frappe.throw("A chat room for this task already exists.")

    # Create Room
    room_doc = frappe.get_doc({
        "doctype": "Chat Room",
        "room_name": room_name,
        "members": members,
        "type": room_type,
        "task": task,
        "chat_bot": chat_bot
    }).insert(ignore_permissions=True)

    # Create and send profile data
    profile = {
        "room_name": room_name,
        "last_date": room_doc.modified,
        "room": room_doc.name,
        "is_read": 0,
        "room_type": room_type,
        "members": members
    }

    for user in users:
        frappe.publish_realtime(
            event="private_room_creation",
            message=profile,
            user=user,
            after_commit=True
        )
    return profile


def create_task_related_chat(doc, method=None):
    """
    Create a group chat room related to a task, involving the user, poster_user, and chatbot.

    Args:
        doc (Document): The document object representing the new Customer Task.
        method (str, optional): The method calling this function, if applicable.
    """
    # Get user, poster_user, and task details from Customer Task
    # user_email = doc.owner  # Email of the user who created the task
    # Email of the poster user, adjust if field type/naming is different
    poster_email = doc.poster_user
    chat_bot = doc.chat_bot
    # Retrieve the chat bot email from the poster_user’s "User" document using `get_single_value`
    # Assume chat_bot field in "User" holds the email/ID for a chatbot user, adjust accordingly
    chat_bot_email = frappe.db.get_value('Chat Bot', chat_bot, 'user')

    # Validate data
    if not chat_bot_email:
        frappe.throw(
            "No Chat Bot assigned to poster user: {0}".format(poster_email))

    # Define room parameters
    room_name = f"Group Chat for Task - {doc.name}"
    users = [poster_email, chat_bot_email]

    # Use create_private to generate the room
    # Passing doc.name as task parameter assuming room doc has a Link field to task, adjust accordingly
    create_task_chat(room_name, users, room_type="Group",
                     task=doc.name, chat_bot=chat_bot)


def after_insert(doc, method):
    create_task_related_chat(doc, method)
