from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

import requests, logging, json
from restcountries import RestCountryApiV2 as rapi
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, ForceReply
from telegram.ext import Updater, Filters, CallbackQueryHandler, CallbackContext, MessageHandler, CommandHandler

#   ---------------------------------------- تنظیمات لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

#   ---------------------------------------- متغیر های عمومی رباط
botToken = '1769684256:AAFvf2iiIV-tV85pyRgGPI1n7sBs9qF1ZPE'
numbers = [0,1,2,3,4,5,6,7,8,9]
#============================================================================================================================================







#   ---------------------------------------- تابع های مورد نیاز
#   مربوط به دریافت پرچم از لینک
#   دانلود و تبدیل svg to png
def svgtopng(svglink):
    #   حذف آدرس لینک و استخراج نام فایل
    file_name = svglink[29:]
    #   دانلود فایل از لینک داده شده و ذخیره در ادرس مورد نظر
    with open('imgs/dls/' + file_name, 'wb') as handle:
        response = requests.get(svglink, stream=True)
        if not response.ok:
            print (response)
        for block in response.iter_content(1024):
            if not block:
                break
            handle.write(block)
    #   خواندن فایل svg
    drawing = svg2rlg('imgs/dls/' + file_name)
    #   تبدیل به png 
    renderPM.drawToFile(drawing, 'imgs/uls/' + file_name[:-3] + 'png', fmt='PNG')
#============================================================================================================================================







#   ---------------------------------------- تابع های درخواست شده
#   فانکشن با دریافت آیپی اطلاعات مورد نظر را پاسخ میدهد
def ip_finder(ip_address):
    try:
        # طراحی لینک با ایپی مورد نظر
        url = 'http://ipwhois.app/json/' + ip_address
        # ارسال درخاست و دیکد کردن جواب
        response = requests.get(url)
        result = response.content.decode()
        # تبدیل اطلاعات ب یک دیکشنری
        result  = json.loads(result)
        # مقدار دهی متغیر ها
        country = result['country']
        city = result['city']
        isp = result['isp']
        result = f"""
        اطلاعات آیپی
        کشور   {country}
        شهر   {city}
        سرویس دهنده   {isp}
        .
        """
        return result
    except:
        return 'درخاست نا مناسب'
    

#   فانکشن مربوط به پیدا کردن اطلاعات کشور -> ورودی نام کشور را میگیرد و اطلاعات را خروجی میدهد
def countrydet(name):
    try:
        #   استخراج فهرست کشور هایی که نام انتخابی در نام انها وجود دارد
        country_list = rapi.get_countries_by_name(name)
        #   جدا سازی المنت 0 لیست یعنی کشور اصلی
        coo = country_list[0]
        #   طراحی قالب اطلاعات کشور مورد نظر
        details = f"""
        اطلاعات کشور
        نام   {coo.name} - {coo.native_name}
        پایتخت   {coo.capital}
        پیش شماره   {coo.calling_codes}
        واحد پولی   {coo.currencies[0]['name']}
        جمعیت   {coo.population}
        منطقع   {coo.region}
        همسایه ها   {coo.borders}
        .
        """
        result = [details, coo.flag]
        #   دانلود و تبدیل تصویر پرچم
        svgtopng(coo.flag)
        #   بازگشت دادن جواب به محلی که تابع فراخانی شده
        return result
    except:
        return 'درخاست نا مناسب'
    

#   فهرست تمام کشور ها اگر ورودی 1 بود نیمه ی اول و اگر 2 بود نیمه ی دوم
def countrylist(num):
    index = 0
    country_list = rapi.get_all()
    res = 'فهرست کشور ها \n'
    for country in country_list:
        index += 1
        res += str(country.name) +'\n'
        if index == int(len(country_list)/2):
            result = res
            res = 'فهرست کشور ها \n'
        if index == int(len(country_list)):
            result2 = res

    if num == 1:
        return result
    else:
        return result2
    
#============================================================================================================================================
reply_keyboard = [
    ['فهرست کشور ها1', 'فهرست کشورها2'],
    ['🇮🇷','🇦🇫','🇦🇲','🇦🇿'],
    ['🇮🇶','🇵🇰','🇹🇷','🇹🇲'],
]
main_markup = ReplyKeyboardMarkup(reply_keyboard)





#   ---------------------------------------- تابع های اصلی ربات
def echo(update:Update, context:CallbackContext):
    global numbers

    if update.message.text == '/start':
        update.message.reply_text(text='درود', reply_markup=main_markup)

    elif update.message.text.isalpha():
        context.bot.send_photo(chat_id=int(update.message.from_user.id), photo=open('imgs/uls/' + countrydet(update.message.text)[1][29:-3] + 'png', 'rb'), caption=countrydet(update.message.text)[0], reply_markup=main_markup)

    elif update.message.text.startswith('فهرست کشور ها') and update.message.text.endswith('1') or update.message.text.endswith('2'):
        update.message.reply_text(text=countrylist(int(update.message.text[len(update.message.text)-1])), reply_markup=main_markup)

    elif update.message.text == '🇮🇷':
        context.bot.send_photo(chat_id=int(update.message.from_user.id), photo=open('imgs/uls/' + countrydet('iran')[1][29:-3] + 'png', 'rb'), caption=countrydet('iran')[0], reply_markup=main_markup)

    elif update.message.text == '🇦🇫':
        context.bot.send_photo(chat_id=int(update.message.from_user.id), photo=open('imgs/uls/' + countrydet('Afghanistan')[1][29:-3] + 'png', 'rb'), caption=countrydet('Afghanistan')[0], reply_markup=main_markup)

    elif update.message.text == '🇦🇲':
        context.bot.send_photo(chat_id=int(update.message.from_user.id), photo=open('imgs/uls/' + countrydet('Armenia')[1][29:-3] + 'png', 'rb'), caption=countrydet('Armenia')[0], reply_markup=main_markup)

    elif update.message.text == '🇦🇿':
        context.bot.send_photo(chat_id=int(update.message.from_user.id), photo=open('imgs/uls/' + countrydet('Azerbaijan')[1][29:-3] + 'png', 'rb'), caption=countrydet('Azerbaijan')[0], reply_markup=main_markup)

    elif update.message.text == '🇮🇶':
        context.bot.send_photo(chat_id=int(update.message.from_user.id), photo=open('imgs/uls/' + countrydet('Iraq')[1][29:-3] + 'png', 'rb'), caption=countrydet('Iraq')[0], reply_markup=main_markup)

    elif update.message.text == '🇵🇰':
        context.bot.send_photo(chat_id=int(update.message.from_user.id), photo=open('imgs/uls/' + countrydet('Pakistan')[1][29:-3] + 'png', 'rb'), caption=countrydet('Pakistan')[0], reply_markup=main_markup)

    elif update.message.text == '🇹🇷':
        context.bot.send_photo(chat_id=int(update.message.from_user.id), photo=open('imgs/uls/' + countrydet('Turkey')[1][29:-3] + 'png', 'rb'), caption=countrydet('Turkey')[0], reply_markup=main_markup)

    elif update.message.text == '🇹🇲':
        context.bot.send_photo(chat_id=int(update.message.from_user.id), photo=open('imgs/uls/' + countrydet('Turkmenistan')[1][29:-3] + 'png', 'rb'), caption=countrydet('Turkmenistan')[0], reply_markup=main_markup)

    else:
        update.message.reply_text(text=ip_finder(str(update.message.text)), reply_markup=main_markup)
        

def main() -> None:
    updater = Updater(botToken)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.text , echo))

    updater.start_polling()
    updater.idle()
#   ------------------------------------------------
if __name__ == '__main__':
    main()

