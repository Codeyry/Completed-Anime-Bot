import os, random
from config import START_PIC, START_MSG, ABOUT_MSG, CMD_MSG, LOGGER, DEV_MODE
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton 
from pyrogram.enums import ParseMode, ChatAction
from bot import Bot
from database.database import add_user

logger = LOGGER(__name__)


#-- 🫆 start command --#
@Client.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):
  logger.info("Start command received from user %s", message.from_user.id)
  # chat action
  await client.send_chat_action(message.chat.id, ChatAction.PLAYING)
  
  # save user id to mongodb
  await add_user(message.from_user.id) 
  
  bot = await client.get_me() # obj
  bot_username = bot.username # username
  # buttons 
  reply_btns = InlineKeyboardMarkup(
    [
      [
        InlineKeyboardButton("Aᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ᴄʜᴀᴛ", url=f"https://t.me/{bot_username}?startgroup=botstart")
      ],
      [
        InlineKeyboardButton("✏️ Aʙᴏᴜᴛ", callback_data="about"),
        InlineKeyboardButton("💨 Cᴏᴍᴍᴀɴᴅs", callback_data="cmd")
      ]
    ]
  )

  photo = random.choice(START_PIC)
  logger.debug("Selected start photo for user %s", message.from_user.id)
  
  # send a photo with msg 
  await message.reply_photo(
    photo = photo,
    caption = START_MSG.format(
    mention = message.from_user.mention),
    reply_markup = reply_btns
  )
  logger.info("Start response sent to user %s", message.from_user.id)
  

#-- Callback Queries --#
@Client.on_callback_query(filters.regex("^(about|cmd|back)$"))
async def callback_queries(client: Bot, query: CallbackQuery):
    logger.info("Callback %s received from user %s", query.data, query.from_user.id)
    #-- About --#
    if query.data == "about":
        await query.message.edit_text(
            text = ABOUT_MSG.format(mention=query.from_user.mention),
            disable_web_page_preview = True, 
            parse_mode = ParseMode.HTML,
            reply_markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("🖇️ ʙᴀᴄᴋ", callback_data="back"),
                        InlineKeyboardButton("💨 Cᴏᴍᴍᴀɴᴅs", callback_data="cmd")
                    ]
                ]
            )
        )
        logger.debug("Displayed About content")
    
    #-- Commands --#
    elif query.data == "cmd":
        await query.message.edit_text(
            text = CMD_MSG.format(mention=query.from_user.mention),
            disable_web_page_preview = True, 
            parse_mode = ParseMode.HTML,
            reply_markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("✏️ Aʙᴏᴜᴛ", callback_data="about"),
                        InlineKeyboardButton("🖇️ ʙᴀᴄᴋ", callback_data="back")
                    ]
                ]
            )
        )
        logger.debug("Displayed command list")
    
    #-- Back Callback --#
    elif query.data == "back":
        await query.message.edit_text(
            text = START_MSG.format(mention=query.from_user.mention),
            disable_web_page_preview = True,
            reply_markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("✏️ Aʙᴏᴜᴛ", callback_data="about"),
                        InlineKeyboardButton("💨 Cᴏᴍᴍᴀɴᴅs", callback_data="cmd")
                    ]
                ]
            )
        )
        logger.debug("Returned to start content")

