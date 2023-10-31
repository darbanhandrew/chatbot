import frappe


def create_and_assign_chat_bot(user_doc):
    # Create a new Chat Bot record and assign it to the user.
    chat_template = frappe.get_last_doc("Chat Bot Template")
    chat_bot = frappe.get_doc({
        "doctype": "Chat Bot",
        "chat_bot_template": chat_template.name,
        "recipient": user_doc.name
    })
    chat_bot.insert()
    user_doc.chat_bot = chat_bot.name
    user_doc.save()


def after_insert(doc, method):
    create_and_assign_chat_bot(doc)
