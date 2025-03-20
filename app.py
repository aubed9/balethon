from balethon import Client
from balethon.conditions import document, private, text, video
from balethon.objects import InlineKeyboard, ReplyKeyboard
from gradio_client import Client as C
from gradio_client import handle_file
import json
import queue
import asyncio
import requests
import time

client_hf = C("rayesh/process_miniapp")
bot = Client("1261816176:T4jSrvlJiCfdV5UzUkpywN2HFrzef1IZJs5URAkz")

user_states = {}
user_parametrs_sub={}
user_parametrs_dub={}

async def init_state(id, state):
    user_states[id] = state

async def handle_state(id, state, app=""):
    user_states[id][0] = state
    if app: 
        user_states[id].append(app)

async def init_sub_para(id, para):
    user_parametrs_sub[id] = para

async def handle_sub_paramiters(id, app=""):
    
    user_parametrs_sub[id][0].append(app)

# Function to process the Gradio job in a separate thread
def process_video(job, progress_queue):
    final_video = None
    print("test3")
    for update in job:
        progress_msg, video_output = update
        if progress_msg:
            progress_queue.put(progress_msg)
        if video_output is not None:
            final_video = video_output
    return final_video

# Async function to update progress messages
async def update_progress(downloading, progress_queue):
    while True:
        try:
            progress_msg = progress_queue.get_nowait()
            await downloading.edit_text(f"وضعیت: {progress_msg}")
        except queue.Empty:
            await asyncio.sleep(0.1)  # Small sleep to avoid busy waiting

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
        await init_state(user_id , ['awaiting_choose'])
        print(user_states[user_id][0]+"1\n")
        await message.reply (
            """🎉 یه خبر خفن برای تولیدکننده‌های محتوا!
دیگه نگران ترجمه و دوبله ویدیوهای انگلیسی نباشید! 🎙✨
ربات "شهر فرنگ" همه کارو براتون انجام می‌ده:
✅  زیرنویس فارسی سریع و دقیق
✅ دوبله فارسی با صدای طبیعی 
✅ صرفه‌جویی در زمان و هزینه

دیگه وقتشه محتوای جهانی تولید کنی! 🚀🔥
🔗 همین حالا امتحان کن!""",
            reply_markup=InlineKeyboard(
                [("د تولید زیرنویس سریع📜 ", "sub_def")],
                [(" تولید زیرنویس پیشرفته ", "sub_c")],
                [(" توضیحات بیشتر 📖 ", "toturial")]
            )
        )
        await bot.send_message(
            chat_id=message.chat.id,
            text="برای ناوبری از کیبورد زیر استفاده کنید.",
            reply_markup=home_keyboard
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
🎙 دوبله فارسی یا 📜 زیرنویس فارسی؟

🔹 مرحله ۲: سریع یا پیشرفته؟
⚡️ سریع (بی‌دردسر و فوری)
⚙️ پیشرفته (شخصی‌سازی بیشتر)

🔹 مرحله ۳: آپلود ویدیو
⏳ کمی صبر کن تا هوش مصنوعی جادو کنه! ✨

💡 نکته: ما همیشه در حال بهتر کردن "شهر فرنگ" هستیم، نظرت برامون مهمه!🚀 شروع کن و محتوای حرفه‌ای بساز!""",
                reply_markup=InlineKeyboard(
                [("د تولید زیرنویس سریع📜 ", "sub_def")],
                [("د تولید زیرنویس پیشرفته ", "sub_c")],
               
            )
        )
            
        elif callback_query.data == "sub_def":
            
            await handle_state(user_id, "awaiting_document", "sub")
            print(user_states[user_id][0]+"2 in sub send \n")
            #print(user_states[user_id][1]+"2 in sub saved value \n")
            await bot.send_message(
                chat_id=callback_query.message.chat.id,
                text="لطفا ویدئوی خود را بار گزاری کنید",
                )
        elif callback_query.data == "sub_c":
            
            await handle_state(user_id, "awaiting_document", "sub")
            print(user_states[user_id][0]+"2 in sub send \n")
            #print(user_states[user_id][1]+"2 in sub saved value \n")
            await bot.send_message(
                chat_id=callback_query.message.chat.id,
                text="لطفا ویدئوی خود را بار گزاری کنید",
                )

@bot.on_message(video)
async def handle_document(message):
    user_id = message.author.id
    if message.video.duration <= 300:
        if user_states[user_id][0] == 'awaiting_document':
            downloading = await message.reply("ویدئو آپلود شد. لطفا چند لحظه صبر کنید")
            time.sleep(10)
            try:
                file = await bot.get_file(message.video.id)
                file_path = file.path
                video_url = f"https://tapi.bale.ai/file/1261816176:T4jSrvlJiCfdV5UzUkpywN2HFrzef1IZJs5URAkz/{file_path}"
                
                # Initialize job as None
                

                print("test")
                job = client_hf.submit(
                    url=video_url,
                    parameters="arial,32,yellow,s,s,s,s",
                    api_name="/main",
                )
                
                # Create a queue for progress updates specific to this request
                progress_queue = queue.Queue()
                # Start a task to handle progress updates
                progress_task = asyncio.create_task(update_progress(downloading, progress_queue))
                
                try:
                    print("test4")
                    # Run the blocking job iteration in a separate thread
                    final_video = await asyncio.to_thread(process_video, job, progress_queue)
                    if final_video:
                        await bot.send_video(
                            chat_id=message.chat.id,
                            video=final_video["video"],
                            caption="🎭 شهر فرنگه، از همه رنگه!✨ پردازش ویدیوی شما تموم شد! ✨"
                        )
                    await bot.send_message(
                        chat_id=message.chat.id,
                        text="برای ادامه، یک گزینه را انتخاب کنید:",
                        reply_markup=InlineKeyboard(
                            [("تولید زیرنویس 📜 ", "sub")],
                            [("دوبله فارسی 🎬 ", "dub")]
                        )
                    )
                finally:
                    # Cancel the progress task when done
                    progress_task.cancel()
            except Exception as e:
                await downloading.edit_text(f"❌ خطا در پردازش: {str(e)}")
                await handle_state(user_id ,  'awaiting_choose')
                await bot.send_message(
                    chat_id=message.chat.id,
                    text="برای ادامه، یک گزینه را انتخاب کنید:",
                    reply_markup=InlineKeyboard(
                        [("تولید زیرنویس 📜 ", "sub")],
                        [("دوبله فارسی 🎬 ", "dub")]
                    )
                )
    else:
        await message.reply("❌ لطفا ویدئوی زیر ۵ دقیقه ارسال کنید")
        await handle_state(user_id, 'awaiting_choose')

bot.run()
