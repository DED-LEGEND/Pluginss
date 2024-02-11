import string

from telethon.tl.types import Channel
from TelethonPbx.plugins import *

global msg_cache
global groupsid
msg_cache = {}
groupsid = []


async def all_groups_id(Pbx):
    Pbxgroups = []
    async for dialog in Pbx.client.iter_dialogs():
        entity = dialog.entity
        if isinstance(entity, Channel) and entity.megagroup:
            Pbxgroups.append(entity.id)
    return Pbxgroups


@Pbx_cmd(pattern="frwd$")
async def _(event):
    if Config.LOGGER_ID == 0:
        await parse_error(event, "`LOGGER_ID` not configured.", False)
        return
    try:
        e = await event.client.get_entity(Config.LOGGER_ID)
    except Exception as err:
        await parse_error(event, err)
    else:
        re_message = await event.get_reply_message()
        fwd_message = await event.client.forward_messages(e, re_message, silent=True)
        await event.client.forward_messages(event.chat_id, fwd_message)
        await event.delete()


@Pbx_cmd(pattern="resend$")
async def _(event):
    m = await event.get_reply_message()
    await event.delete()
    if m:
        await event.respond(m)


@Pbx_cmd(pattern="copy$")
async def _(event):
    m = await event.get_reply_message()
    await event.delete()
    if m:
        await event.client.send_message(event.chat_id, m, reply_to=m.id)


@Pbx_cmd(pattern="fpost(?:\s|$)([\s\S]*)")
async def _(event):
    global groupsid
    global msg_cache
    await event.delete()
    text = event.text[7:]
    destination = await event.get_input_chat()
    if len(groupsid) == 0:
        groupsid = await all_groups_id(event)
    for c in text.lower():
        if c not in string.ascii_lowercase:
            continue
        if c not in msg_cache:
            async for msg in event.client.iter_messages(event.chat_id, search=c):
                if msg.raw_text.lower() == c and msg.media is None:
                    msg_cache[c] = msg
                    break
        if c not in msg_cache:
            for i in groupsid:
                async for msg in event.client.iter_messages(event.chat_id, search=c):
                    if msg.raw_text.lower() == c and msg.media is None:
                        msg_cache[c] = msg
                        break
        await event.client.forward_messages(destination, msg_cache[c])


CmdHelp("messages").add_command(
    "fpost", "<your msg>", "Checks all your groups and sends the message matching the given keyword."
).add_command(
    "frwd", "<reply to a msg>", "Enables seen counter in replied msg. To know how many users have seen your message."
).add_command(
    "resend", "<reply to a msg>", "Just resends the replied message."
).add_command(
    "copy", "<reply to a msg>", "Resends the replied message by replying to the original message."
).add_info(
    "Messages tools."
).add_warning(
    "✅ Harmless Module."
).add()
