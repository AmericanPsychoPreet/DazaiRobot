from base64 import b64decode
from inspect import getfullargspec
from io import BytesIO
import requests
from aiohttp import ClientSession
from pyrogram import filters
from pyrogram.types import Message
from Dazai import Dazai

aiohttpsession = ClientSession()


async def post(url: str, *args, **kwargs):
    async with aiohttpsession.post(url, *args, **kwargs) as resp:
        try:
            data = await resp.json()
        except Exception:
            data = await resp.text()
    return data



async def take_screenshot(url: str, full: bool = False):
    url = "https://" + url if not url.startswith("http") else url
    payload = {
        "url": url,
        "width": 1920,
        "height": 1080,
        "scale": 1,
        "format": "jpeg",
    }
    if full:
        payload["full"] = True
    data = await post(
        "https://webscreenshot.vercel.app/api",
        data=payload,
    )
    if "image" not in data:
        return None
    b = data["image"].replace("data:image/jpeg;base64,", "")
    file = BytesIO(b64decode(b))
    file.name = "webss.jpg"
    return file


async def eor(msg: Message, **kwargs):
    func = (
        (msg.edit_text if msg.from_user.is_self else msg.reply)
        if msg.from_user
        else msg.reply
    )
    spec = getfullargspec(func.__wrapped__).args
    return await func(**{k: v for k, v in kwargs.items() if k in spec})


@Hiroko.on_message(filters.command(["webss", "ss", "webshot"]))
async def take_ss(_, message: Message):
    if len(message.command) < 2:
        return await eor(message, text="É¢Éªá´ á´‡ á´€ á´œÊ€ÊŸ á´›á´ Ò“á´‡á´›á´„Êœ sá´„Ê€á´‡á´‡É´sÊœá´á´›.")

    if len(message.command) == 2:
        url = message.text.split(None, 1)[1]
        full = False
    elif len(message.command) == 3:
        url = message.text.split(None, 2)[1]
        full = message.text.split(None, 2)[2].lower().strip() in [
            "yes",
            "y",
            "1",
            "true",
        ]
    else:
        return await eor(message, text="ÉªÉ´á´ á´€ÊŸÉªá´… á´„á´á´á´á´€É´á´….")

    m = await eor(message, text="á´„á´€á´˜á´›á´œÊ€ÉªÉ´É¢ sá´„Ê€á´‡á´‡É´sÊœá´á´›...")

    try:
        photo = await take_screenshot(url, full)
        if not photo:
            return await m.edit("Ò“á´€ÉªÊŸá´‡á´… á´›á´ á´›á´€á´‹á´‡ sá´„Ê€á´‡á´‡É´sÊœá´á´›.")

        m = await m.edit("á´œá´˜ÊŸá´á´€á´…ÉªÉ´É¢...")

        if not full:
            await message.reply_document(photo)
        else:
            await message.reply_document(photo)
        await m.delete()
    except Exception as e:
        await m.edit(str(e))


