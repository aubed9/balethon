from balethon import Client
from balethon.conditions import document, private, text, video
from balethon.objects import InlineKeyboard, ReplyKeyboard
from gradio_client import Client as C
from gradio_client import handle_file
import json
import queue
import asyncio
import requests
import aiohttp

#client_hf = C("rayesh/process_miniapp")
bot = Client("640108494:Y4Hr2wDc8hdMjMUZPJ5DqL7j8GfSwJIETGpwMH12")


user_states = {}
user_parametrs_sub={}
user_parametrs_dub={}

# Define reply keyboards
home_keyboard = ReplyKeyboard(["خانه"])
#back_home_keyboard = ReplyKeyboard(["بازگشت", "خانه"])

# Handle all text messages (including navigation buttons)
@bot.on_message(text)
async def answer_message(message):
    user_id = message.author.id
    state = user_states.get(user_id)
    print("on message")

    
    # Handle "Home" button
    if message.text == "خانه" or message.text =="/start":
        user_states[user_id] = ['awaiting_choose']
        print(user_states[user_id][0]+"1\n")
        await message.reply (
            """🎉 یه خبر خفن برای تولیدکننده‌های محتوا!
دیگه نگران ترجمه و دوبله ویدیوهای انگلیسی نباشید! 🎙✨
ربات "شهر فرنگ" همه کارو براتون انجام می‌ده:
✅  زیرنویس فارسی سریع و دقیق
✅ قابلیت شخصی سازی زیرنویس و ترجمه
✅ صرفه‌جویی در زمان و هزینه

دیگه وقتشه محتوای جهانی تولید کنی! 🚀🔥
🔗 همین حالا امتحان کن!""",
            reply_markup=InlineKeyboard(
                [("تولید زیرنویس 📜 ", "sub")],
                [("دوبله فارسی(در حال توسعه) 🎬 ", "a")],
                [(" توضیحات بیشتر 📖 ", "toturial")]
            )
        )
    
# Handle inline keyboard selections
@bot.on_callback_query()
async def handle_callbacks(callback_query):
    user_id = callback_query.author.id
    if user_id not in user_states:
        await bot.send_message(
            chat_id=callback_query.message.chat.id,
            text="لطفا ابتدا فرمان /start را ارسال کنید."
        )
    print('callback_query')
    #print(user_states[user_id][0]+"2\n")
    if user_states[user_id][0] == 'awaiting_choose':
        print("callback choose")
        if callback_query.data == "toturial":
            await bot.send_message(
                chat_id=callback_query.message.chat.id,
                text="""🎬 راهنمای سریع "شهر فرنگ"!

🔹 مرحله ۱: انتخاب نوع تبدیل
🎙 دوبله فارسی(در حال توسعه) یا 📜 زیرنویس فارسی؟

🔹 مرحله ۲: سریع یا پیشرفته؟
⚡️ سریع (بی‌دردسر و فوری)
⚙️ پیشرفته (شخصی‌سازی بیشتر)

🔹 مرحله ۳: آپلود ویدیو
⏳ کمی صبر کن تا هوش مصنوعی جادو کنه! ✨
""",
                reply_markup=InlineKeyboard(
                [("تولید زیرنویس ", "sub")],
               
            )
        )
            
        elif callback_query.data == "sub":
            
            user_states[user_id][0] = "awaiting_parametrs"
            user_states[user_id].append("sub")
            print(user_states[user_id][0]+"2 in sub send \n")
            #print(user_states[user_id][1]+"2 in sub saved value \n")
            await bot.send_message(
            chat_id=callback_query.message.chat.id,
            text="لطفا یک گزینه را از کیبورد انتخاب کنید.",
            reply_markup=InlineKeyboard(
                    [("تولید زیرنویس سریع ⚡️", "sub_def")],
                    [("(به زودی)تولید زیرنویس پیشرفته ⚙️", "sub_custome")]
                    ),
          #  reply_markup=home_keyboard
            )
        elif callback_query.data == "dub":
            user_states[user_id][0] = "awaiting_parametrs"
            user_states[user_id].append("dub")
            await bot.send_message(
                chat_id=callback_query.message.chat.id,
                text="لطفا یک گزینه را از کیبورد انتخاب کنید.",
                reply_markup=InlineKeyboard(
                        [("دوبله سریع ⚡️ ", "dub_def")],
                        [(" دوبله پیشرفته ⚙️ ", "dub_custome")]
                    ),
                #reply_markup=home_keyboard
                )
         #await bot.send_message(
       #         chat_id=callback_query.message.chat.id,
       #         text="لطفا ویدیو خود را برای دوبله آپلود کنید ",
       #         reply_markup=home_keyboard
       #    )
    #choose custome or default 
    elif user_states[user_id][0] == 'awaiting_parametrs':
        print(user_states[user_id][0]+"3 call back choose dub custome or sub custome \n")
        if callback_query.data == "dub_custome":
            user_states[user_id][0] = 'awaiting_send_parametrs'
            print(user_states[user_id][0]+"4 dub custome choose call back \n")
            await bot.send_message(
            chat_id=callback_query.message.chat.id,
            text="لطفا یک گوینده را از کیبورد انتخاب کنید 🧐.",
            reply_markup=InlineKeyboard(
                    [(" 🧔🏻‍♂️ آقا", "he")],
                    [(" 🧕🏻 خانم", "she")]
             )
            ) 
        elif callback_query.data == "sub_custome":
            if user_states[user_id][0] == 'awaiting_parametrs':
                user_states[user_id][0] = 'awaiting_send_parametrs'
                print(user_states[user_id][0]+"4 sub custome choose call back \n")
                await bot.send_message(
                chat_id=callback_query.message.chat.id,
                text=" رنگ زیرنویس رو انتخاب کن 🧐.",
                reply_markup=InlineKeyboard(
                        [(" ⚪️ سفید", "white")],
                    [(" ⚫️ سیاه", "black")],
                    [(" 🟡 زرد", "yellow")]
                    )
                )
        elif callback_query.data == "sub_def":
            print(1)
            user_states[user_id][0] = 'awaiting_document'
            user_parametrs_sub[user_id]=['yellow']
            user_parametrs_sub[user_id].append("arial")
        elif callback_query.data == "dub_def":
             print(2)
             user_states[user_id][0] = 'awaiting_document'
    #choose color and speakers
    elif user_states[user_id][0] == 'awaiting_send_parametrs' :
        if callback_query.data == "he":
            user_parametrs_dub[user_id]=['he']
            print(3)
            user_states[user_id][0]= 'awaiting_document'
            print(user_states[user_id][0]+"he choosed\n")
        elif callback_query.data == "she":
            print(4)
            user_states[user_id][0]= 'awaiting_document'
            user_parametrs_dub[user_id]=['she']
            print(user_states[user_id][0]+"she choosed\n")
        elif callback_query.data=="black":
            user_parametrs_sub[user_id]=['black']
            user_states[user_id][0] = 'awaiting_font'
            print(user_states[user_id][0]+"black choosed\n")
        elif callback_query.data=="white":
            user_parametrs_sub[user_id]=['white']
            user_states[user_id][0]= 'awaiting_font'
            print(user_states[user_id][0]+"white choosed\n")
        elif callback_query.data=="yellow":
            user_parametrs_sub[user_id]=['yellow']
            user_states[user_id][0] = 'awaiting_font'
            print(user_states[user_id][0]+"yellow choosed\n")
    #choose font
    if user_states[user_id][0] == 'awaiting_font':
        user_states[user_id][0]= 'append_font'
        await bot.send_message(
            chat_id=callback_query.message.chat.id,
            text="فونت مورد نظر را انتخاب کنید 📑",
            reply_markup=InlineKeyboard(
                [("ب نازنین", "nazanin")],
                [("ب یکان", "yekan")],
                [("آریا", "arial")]
            )
        )
    if user_states[user_id][0] == 'append_font': 
        print(user_states[user_id][0])
        if callback_query.data == "yekan":
            user_parametrs_sub[user_id].append('yekan')
            user_states[user_id][0]= 'awaiting_document'
            print(user_states[user_id][0]+"yekan choosed\n")
        elif callback_query.data == "nazanin":
            user_states[user_id][0]= 'awaiting_document'
            user_parametrs_sub[user_id].append('nazanin')
        elif callback_query.data == "arial":
            print(6)
            user_states[user_id][0]= 'awaiting_document'
            user_parametrs_sub[user_id].append('arial')
        elif len(user_parametrs_sub[user_id])==2:
            print(5)
            user_states[user_id][0]= 'awaiting_document'
        '''await bot.send_message(
                chat_id=callback_query.message.chat.id,
                text="ایا از انتخاب خود مطمین هستید ؟",
                reply_markup=InlineKeyboard(
                        [("بلی ", "confirm")],
                        )
        )'''
    if user_states[user_id][0] == 'awaiting_document':         
        await bot.send_message(
                chat_id=callback_query.message.chat.id,
                text="لطفا ویدیو انگلیسی مورد نظر خود را آپلود کنید"
        )
# Handle video uploads
@bot.on_message(video)
async def handle_document(message):
    user_id = message.author.id
    if message.video.duration <= 300:
        if user_states[user_id][0] == 'awaiting_document': 
            downloading = await message.reply("در صف پردازش . . . 💡")
            if user_states[user_id][1]=="dub":
                pass
                '''file = await bot.get_file(message.video.id)
                file_path = file.path
                job = client_hf.submit(
                    url=f"https://tapi.bale.ai/file/bot1261816176:T4jSrvlJiCfdV5UzUkpywN2HFrzef1IZJs5URAkz/{file_path}",
                    clip_type=user_states[user_id][1],
                    parameters=user_parametrs_dub,
                    api_name="/main",
                )'''
            elif user_states[user_id][1]=="sub":
                    
                try:
                    file = await bot.get_file(message.video.id)
                    file_path = file.path
                    video_url = f"https://tapi.bale.ai/file/640108494:Y4Hr2wDc8hdMjMUZPJ5DqL7j8GfSwJIETGpwMH12/{file_path}"
                    
                    job = client_hf.submit(
                    url=f"https://tapi.bale.ai/file/bot1261816176:T4jSrvlJiCfdV5UzUkpywN2HFrzef1IZJs5URAkz/{file_path}",
                    clip_type=user_states[user_id][1],
                    parameters=user_parametrs_dub,
                    api_name="/main",
                    )
                    print(job.status())
                    final_video = None
                    for update in job:
                        progress_msg, video_output = update
                        if progress_msg:
                            await downloading.edit_text(f"وضعیت: {progress_msg}")
                        if video_output is not None:
                            final_video = video_output
                    print(final_video)
                    if final_video:
                        await bot.send_video(
                        chat_id=message.chat.id,
                        video=final_video["video"],
                        caption="🎭 شهر فرنگه، از همه رنگه!✨ پردازش ویدیوی شما تموم شد! ✨"
                    )
                    user_states[user_id][0] = 'awaiting_choose'
                    await bot.send_message(
                    chat_id=message.chat.id,
                    text="برای ادامه، یک گزینه را انتخاب کنید:",
                    reply_markup=InlineKeyboard(
                    [("تولید زیرنویس 📜 ", "sub")]
                    )
                )
                    reply_markup=home_keyboard
                except Exception as e:
                    await downloading.edit_text(f"❌ خطا در پردازش: {str(e)}")
                    user_states[user_id][0] = 'awaiting_choose'

bot.run()
    

