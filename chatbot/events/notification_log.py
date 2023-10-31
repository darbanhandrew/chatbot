import json
import frappe
from bs4 import BeautifulSoup
from chatbot.api import send_direct_message_from_bot, send_group_message_on_task

@frappe.whitelist()
def after_insert(doc, method=None):
    # Step 2: Check for_user
    if isinstance(doc, str):
        doc = frappe.get_doc("Notification Log",doc)
    if doc.for_user != 'chatbot@taskerpage.com':
        return
    
    # Step 3: Parse and Process the Message
    try:
        # Extract text from HTML message
        soup = BeautifulSoup(doc.email_content, 'html.parser')
        text_content = soup.get_text(strip=True)
        
        # Convert text message to JSON
        json_content = json.loads(text_content)
        
        # Further steps...
        process_chatbot_notifications(json_content)
    
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error parsing Notification Log message")
        pass
    
    return doc

def process_chatbot_notifications(notification_data):
    for chat_bot_info in notification_data.get("chat_bots", []):
        # 3.b Check if Notification is enabled in Chat Bot's triggers
        chat_bot_doc = frappe.get_doc("Chat Bot", chat_bot_info["chat_bot"])
        
        # Find if the notification is enabled in triggers
        is_notification_enabled = any(
            [trigger for trigger in chat_bot_doc.triggers if trigger.notification == notification_data["notification"] and trigger.enabled]
        )
        
        if not is_notification_enabled:
            continue
        
        # 3.c Determine message type and send
        if chat_bot_info["related_doctype"] == "User":
            # Direct message flow...
            send_direct_message_from_bot(chat_bot_info["chat_bot"], chat_bot_info["message"])
        elif chat_bot_info["related_doctype"] == "Customer Task":
            # Task message flow...
            send_group_message_on_task(chat_bot_info["related_docname"], chat_bot_info["message"])
        # Add more conditions here if needed