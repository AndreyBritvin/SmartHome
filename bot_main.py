# import sys
# print(sys.version)
import logging
import paho.mqtt.publish as publish
import paho.mqtt.subscribe as subscribe

import telegram
import paho.mqtt.client as mqtt
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
import argparse
import threading
import multiprocessing

import bot_door
import bot_climate
import bot_flower
import mailing
import bot_weather
from constants import *


def getArgs():
    global mode, log
    parser = argparse.ArgumentParser(description='A tutorial of argparse!')
    parser.add_argument("-mode", default="test", help="This is the 'mode' variable.")
    parser.add_argument("-log", default="bot_test.log", help="This is the 'log' variable")
    # parser.add_argument("-b", default=456, help="This is the 'b' variable")
    # parser.add_argument("-c", default="mybot.log", help="This is the 'c' variable")
    args = parser.parse_args()
    mode = args.mode
    log = args.log
    # b = args.b
    # c = args.c


getArgs()
global mode, log
global TELEGRAM_BOT_TOKEN
global TELEGRAM_REPLAY_GROUPS
global LOG_FILE_NAME
if mode == "prod":
    prefix = "home"
else:
    prefix = mode
if mode == "test":
    """
    for j in list(FLOWER_TOPICS_LIST_WITH_ROOM_DICT.keys()):
        for i in range(len(list(FLOWER_TOPICS_LIST_WITH_ROOM_DICT[j].keys()))):
            topics = copy.copy(list(FLOWER_TOPICS_LIST_WITH_ROOM_DICT[j].keys()))
            print(topics)
            topics[i] = TEST_TOPIC + topics[i]
            print(topics[i])"""

    bot_flower.generateTopics(TEST_TOPIC)

    TELEGRAM_BOT_TOKEN = TELEGRAM_BOT_TOKEN_TEST
    TELEGRAM_REPLAY_GROUPS = TELEGRAM_REPLAY_GROUPS_TEST
elif mode == "prod":
    bot_flower.generateTopics(HOME_TOPIC)
    TELEGRAM_BOT_TOKEN = TELEGRAM_BOT_TOKEN_PROD
    TELEGRAM_REPLAY_GROUPS = TELEGRAM_REPLAY_GROUPS_PROD
LOG_FILE_NAME = log
topicInSettings = "NONE"
# print(TELEGRAM_BOT_TOKEN)
generateKeyboards()
timeWateringThread = threading.Thread(target=bot_flower.sendCommandToGetMeasurement, args=())

#  print(456)
logging.basicConfig(handlers=[logging.FileHandler(filename=LOG_FILE_NAME,
                                                  encoding='utf-8', mode='a+')],
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


# logger = logging.getLogger(__name__)


def on_message(client, userdata, msg):
    global MQTT_TOPIC_SETTINGS_MEASUREMENT
    #print("Topic: ", msg.topic + "\nMessage: " + str(msg.payload))
   # print(3, bot_door.textToGroup)
    if msg.topic in [MQTT_TOPIC_DOOR_LIFT, MQTT_TOPIC_DOOR_STAIRS, MQTT_TOPIC_DOOR_APARTMENT] and msg.payload.decode(
            "utf-8") == "off" and bot_door.textToGroup!="":
        logging.info("Door topic = off")
        bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
       # print(2, bot_door.textToGroup)
        # bot.edit_message_text(chat_id=bot_door.MYCHATID, text=bot_door.textToEdit)
        logging.info("Getting ready to sent to group")
        for i in range(0, len(TELEGRAM_REPLAY_GROUPS)):
      #      print(1, bot_door.textToGroup)

            bot.send_message(chat_id=TELEGRAM_REPLAY_GROUPS[i], text=bot_door.textToGroup)
            logging.info("Sent to group about door")
      #      print(11)
        bot.edit_message_text(text=bot_door.textToEdit, message_id=bot_door.MESSAGE_ID, chat_id=bot_door.MYCHATID)
        logging.info("Edited message")
     #   print(12)
        bot.send_message(chat_id=bot_door.MYCHATID, text=TELEGRAM_MAIN_MENU_TEXT,
                         reply_markup=KEYBOARD_MAIN)
    #    print(13)
   # print(14)
    # elif msg.topic == prefix+MQTT_TOPIC_SETTINGS_MEASUREMENT:
    # print("thread terminated")
    # timeWateringThread.terminate()


def on_connect(self, client, userdata, rc):
    global MQTT_TOPIC_SETTINGS_MEASUREMENT

    self.subscribe("corridor/door/#")
    #print("subscribed")
    # self.subscribe("test/watering/settings/delayHumidityMeasurement")
    if mode == "test":
        self.subscribe("test" + MQTT_TOPIC_SETTINGS_MEASUREMENT)
    else:
        self.subscribe("home" + MQTT_TOPIC_SETTINGS_MEASUREMENT)


def start(update, context):
    logging.info("start %s", update)

    if update.message.from_user.id not in TELEGRAM_ALLOWED_USERS_ID:
        update.message.reply_text("Это приватный бот. Вам доступ запрещён")
    else:
        update.message.reply_text(TELEGRAM_MAIN_MENU_TEXT, reply_markup=KEYBOARD_MAIN)


def inlineCallback(update, context):
    # print("inInline")
    global roomInWatering
    query = update.callback_query
    query.answer()
    # query = {'id': '1938189368626756704', 'chat_instance': '4634006372709804758', 'message': {'message_id': 163, 'date': 1593500217, 'chat': {'id': -154850675, 'type': 'group', 'title': 'Семейные разговоры', 'all_members_are_administrators': True}, 'reply_to_message': {'message_id': 162, 'date': 1593500217, 'chat': {'id': -154850675, 'type': 'group', 'title': 'Семейные разговоры', 'all_members_are_administrators': True}, 'text': '/open@TestToZamok_bot', 'entities': [{'type': 'bot_command', 'offset': 0, 'length': 21}], 'caption_entities': [], 'photo': [], 'new_chat_members': [], 'new_chat_photo': [], 'delete_chat_photo': False, 'group_chat_created': False, 'supergroup_chat_created': False, 'channel_chat_created': False, 'from': {'id': 131195706, 'first_name': 'Albert', 'is_bot': False, 'username': 'GreenGrad', 'language_code': 'ru'}}, 'text': 'Какую дверь открыть?', 'entities': [], 'caption_entities': [], 'photo': [], 'new_chat_members': [], 'new_chat_photo': [], 'delete_chat_photo': False, 'group_chat_created': False, 'supergroup_chat_created': False, 'channel_chat_created': False, 'reply_markup': {'inline_keyboard': [[{'text': 'лифтовая', 'callback_data': 'у лифта'}], [{'text': 'лестничная', 'callback_data': 'у лестницы'}]]}, 'from': {'id': 1318421029, 'first_name': 'TestToZamok', 'is_bot': True, 'username': 'TestToZamok_bot'}}, 'data': 'у лифта', 'from': {'id': 451269878, 'first_name': 'Andrey', 'is_bot': False, 'last_name': 'Britvin', 'language_code': 'ru'}}
    # print(update)
    callback_data = query.data
    print(callback_data)
    #  print(query["from"]['first_name'])
    # open(update, context)
    needBrake = False
    needStart = False
    try:
        a = callback_data.split(":")[1]
        needStart = True
    except:
        needStart = False
    if needStart:
        splitedData = callback_data.split(":")
        global topicInSettings, whatChange
        whatChange = splitedData[0]
        currentSettings = bot_flower.getCurrentSettings(splitedData[1])
        keyboard = bot_flower.getListOfSettingsForTopic(splitedData[1], roomInWatering)
        text = "Вот текущие настройки\n" + currentSettings
        #   print("whatChange=" + whatChange)
        # print(splitedData[0])
        #  print(list(FLOWER_SETTINGS_LIST.keys()))
        #  print(splitedData[0] in list(FLOWER_SETTINGS_LIST.keys()))
        if splitedData[0] == "water":
            bot_flower.water_flower(splitedData[1])
        elif splitedData[0] == "Settings":

            query.edit_message_text(text=text,
                                    reply_markup=keyboard)

            topicInSettings = splitedData[1]
        elif splitedData[0] in list(FLOWER_SETTINGS_LIST.keys()):
            text2 = FLOWER_SETTINGS_LIST[splitedData[0]] + "\n" + text
            #     print(text2)
            query.edit_message_text(text=text2,
                                    reply_markup=keyboard)
            topicInSettings = splitedData[1]
        # elif splitedData[0] == "waterDuration":
        #   query.edit_message_text(text="Отправь число",
        #                          reply_markup=bot_flower.getListOfSettingsForTopic(splitedData[1]))

    if callback_data in [KEYBOARD_DOOR_LIST_CALLBACK_LIFT, KEYBOARD_DOOR_LIST_CALLBACK_STAIRS,
                         KEYBOARD_DOOR_LIST_CALLBACK_APARTMENT, KEYBOARD_DOOR_LIST_CALLBACK_APARTMENT_AND_STAIRS,
                         KEYBOARD_DOOR_LIST_CALLBACK_APARTMENT_AND_LIFT]:
        logging.info("door %s", query)
        bot_door.openDoor(callback_data, query, update, context)
    elif callback_data == KEYBOARD_MAIN_CALLBACK_LOCK:
        query.edit_message_text(text="Выбери дверь, которую нужно открыть:", reply_markup=KEYBOARD_DOOR_LIST)
    elif callback_data == KEYBOARD_CALLBACK_MAIN_MENU:
        whatChange = "NONE"
        query.edit_message_text(text=TELEGRAM_MAIN_MENU_TEXT, reply_markup=KEYBOARD_MAIN)
    elif callback_data == KEYBOARD_MAIN_CALLBACK_HIDE_BUTTONS:
        query.edit_message_text(text="Кнопки скрыты. Чтобы их показать напиши /start")
    elif callback_data == KEYBOARD_MAIN_CALLBACK_FLAT_CLIMATE:
        query.edit_message_text(text="Выбери комнату", reply_markup=KEYBOARD_ROOM_LIST)
    elif callback_data in ROOM_LIST:
        bot_climate.showStat(callback_data, query, update, context)


    elif callback_data == KEYBOARD_MAIN_CALLBACK_WEATHER:
        #   query.edit_message_text(text="Выбери время")#, reply_markup=KEYBOARD_TIME_WEATHER_LIST)
        query.edit_message_text(text="Выбери погоду",
                                reply_markup=KEYBOARD_TIME_WEATHER_LIST)
    # update.message.reply_text(text = "lala", reply_markup=KEYBOARD_TIME_WEATHER_LIST)
    elif callback_data == "Изменить местоположение":
        query.edit_message_text(text="Жди дальнейших указаний")
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Нажми кнопку ниже, чтобы изменить местоположение для погоды "
                                      "или отошли боту местоположение",
                                 reply_markup=CHANGE_LOCATION)
    elif callback_data == "Погода_сейчас":
        bot_weather.showWeatherToday(update, context, query)
    elif callback_data == "Погода_завтра":
        bot_weather.showWeatherTomorrow(update, context, query)
    elif callback_data == "Погода_3":
        bot_weather.showWeatherIn3Days(update, context, query)
    elif callback_data == "Погода_7":
        bot_weather.showWeatherIn7Days(update, context, query)



    elif callback_data == KEYBOARD_MAIN_CALLBACK_FLOWER:
        query.edit_message_text(text="Выбери комнату для полива",
                                reply_markup=KEYBOARD_FLOWER_ROOM_LIST)
    elif callback_data == KEYBOARD_FLOWER_CALLBACK_WATER_ALL:
        bot_flower.water_all()
    elif callback_data in CALLBACK_LIST_TO_SHOW_FLOWERS_IN_THE_ROOM:
        # print(callback_data)
        whatChange = "NONE"
        roomInWatering = callback_data
        # print("room = ", roomInWatering)
        query.edit_message_text(text="Выбери цветок для полива",
                                reply_markup=WATERING_ROOM_CALLBACK_CONFORMITY[callback_data])
    elif callback_data in CALLBACK_LIST_TO_WATER_ALL_FLOWERS_IN_THE_ROOM:
        bot_flower.water_room(callback_data)
    elif callback_data == "Цветы_настройки":
        query.edit_message_text(text="Выбери настройку и напиши цифру",
                                reply_markup=KEYBOARD_WATERING_SETTINGS)
    elif callback_data == "Настройка_интервала":
        whatChange = "intervalSettings"
        query.edit_message_text(text="Пиши цифру",
                                reply_markup=KEYBOARD_WATERING_SETTINGS)


def help_command(update, context):
    update.message.reply_text("Нажми /start чтобы показать кнопки",
                              parse_mode="HTML")


def locationHandler(update, context):
    TELEGRAM_WEATHER_USER_LOCATION_LAST[update.effective_chat.id] = [str(update.message.location.latitude),
                                                                     str(update.message.location.longitude)]
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Местоположение изменено\n" + TELEGRAM_MAIN_MENU_TEXT, reply_markup=KEYBOARD_MAIN)
    pass


# print(update.message.location.latitude)
#  context.bot.send_message(chat_id = 451269878, text = "Hello")
#  bot_weather.showWeatherToday(update, context, update.message.location.latitude, update.message.location.longitude)

def messageHandler(update, context):
    global topicInSettings, whatChange
    #    print(topicInSettings + " " + whatChange)
    if topicInSettings != "NONE" and whatChange != "NONE":
        #       print("Получено чилсло " + update.message.text + " для топика " + topicInSettings)
        publish.single(topic=topicInSettings + "/" + whatChange, payload=update.message.text, hostname=MQTT_HOST,
                       port=MQTT_PORT,
                       auth={"username": MQTT_LOGIN, "password": MQTT_PASSWORD}, retain=True)

        whatChange = "NONE"
    elif whatChange == "intervalSettings":
        # print(MQTT_TOPIC_SETTINGS_MEASUREMENT)
        publish.single(topic=prefix + MQTT_TOPIC_SETTINGS_MEASUREMENT, payload=update.message.text, hostname=MQTT_HOST,
                       port=MQTT_PORT,
                       auth={"username": MQTT_LOGIN, "password": MQTT_PASSWORD}, retain=True)

        whatChange = "NONE"


def main():
    for j in list(FLOWER_TOPICS_LIST_WITH_ROOM_DICT.keys()):
        for i in FLOWER_TOPICS_LIST_WITH_ROOM_DICT[j]:
            x = threading.Thread(target=bot_flower.waitForNextWateringInMode1, args=(i,))
            x.start()
    global client

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.username_pw_set(MQTT_LOGIN, MQTT_PASSWORD)
    client.connect(MQTT_HOST, MQTT_PORT, 60)

    client.loop_start()

    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    updater.dispatcher.add_handler(CommandHandler('start', start))
    # updater.dispatcher.add_handler(CommandHandler('open', open))
    #  updater.dispatcher.add_handler(CommandHandler('open1', open1))

    updater.dispatcher.add_handler(CallbackQueryHandler(inlineCallback))
    updater.dispatcher.add_handler(CommandHandler('help', help_command))
    updater.dispatcher.add_handler(MessageHandler(Filters.location, locationHandler))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, messageHandler))
    # Start the Bot
    updater.start_polling()

    x = threading.Thread(target=mailing.mail, args=(TELEGRAM_BOT_TOKEN, TELEGRAM_REPLAY_GROUPS))
    x2 = threading.Thread(target=mailing.sendWeather, args=(TELEGRAM_BOT_TOKEN, TELEGRAM_REPLAY_GROUPS))
    x.start()

    x2.start()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    timeWateringThread.start()
    main()
