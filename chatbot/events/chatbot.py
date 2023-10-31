import frappe

def create_chatbot_chat(room_name, users, room_type="Direct", task=None, chat_bot=None):
    """
    Create a new private room.

    Args:
        room_name (str): Room name
        users (list): List of user email addresses in room
        room_type (str): Type of room, default is "Direct"
        task (str, optional): Task associated with room, defaults to None
    """
    members = ", ".join(users)
    
    # Check for existing direct room
    if room_type == "Direct":
        room_doctype = frappe.qb.DocType("Chat Room")
        direct_room_exists = (
            frappe.qb.from_(room_doctype)
            .select("name")
            .where(room_doctype.type == "Direct")
            .where(room_doctype.members.like(f"%{users[0]}%"))
            .where(room_doctype.members.like(f"%{users[1]}%"))
        ).run(as_dict=True)
        
        if direct_room_exists:
            frappe.throw(title="Error", msg=_("Direct Room already exists!"))
    
    # Create Room
    room_doc = frappe.get_doc({
        "doctype": "Chat Room",
        "room_name": room_name,
        "members": members,
        "type": room_type,
        "task": task,
        "chat_bot":chat_bot
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
    
    # if room_type == "Direct":
    #     profile["member_names"] = [
    #         {"name": frappe.utils.get_full_name(u), "email": u} for u in users
    #     ]
        
    for user in users:
        frappe.publish_realtime(
            event="private_room_creation", 
            message=profile, 
            user=user, 
            after_commit=True
        )

    return profile
    # frappe.response["message"] = profile
def copy_triggers_from_template_to_chat_bot(doc):
    # Check if chat_bot_template is set
    if doc.chat_bot_template:
        # Get the template document
        template = frappe.get_doc("Chat Bot Template", doc.chat_bot_template)

        # Copy triggers from template to chat bot
        for trigger in template.triggers:
            doc.append('triggers', {
                'chat_bot_rule': trigger.chat_bot_rule,
                'enabled': trigger.enabled,
            })
    return doc

def before_insert(doc, method):
   doc = copy_triggers_from_template_to_chat_bot(doc)



def prepare_direct_chat(doc):
    user_email = doc.recipient  # Assuming `user` is the Link field to the User doctype in the "Chat Bot"
    bot_email = doc.user  # Replace with actual email/identifier of your bot user

    # Define room parameters
    room_name = f"Direct Chat - {user_email} and Bot"
    users = [user_email, bot_email]
    room_type = "Direct"
    task = None  # assuming no task, adjust as per requirement
    
    # Call the provided create_private function to create the chat room
    chat_room_profile = create_chatbot_chat(room_name, users, room_type, task,doc.name)
    doc.direct_chat_room = chat_room_profile["room"]
    doc.save()

def after_insert(doc,method):
    prepare_direct_chat(doc)
