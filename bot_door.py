import logging
import paho.mqtt.publish as publish
from constants import *
import datetime
import time
import threading
MYCHATID = 0
MESSAGE_ID = 0
textToEdit = ""
textToGroup = ""
baseTextToGroup = ""
"""
import paho.mqtt.client as mqtt
def onCallback(client, userdata, message):
   # global x
    print(message.payload)
    print(message.topic)
    print(str(client))
  #  x.terminate()
    if message.topic in [MQTT_TOPIC_DOOR_LIFT, MQTT_TOPIC_DOOR_STAIRS] and message.payload.decode("utf-8") == "off":
      #  query.edit_message_text(text=textToEdit)
     #   context.bot.send_message(chat_id=update.effective_chat.id, text="Главное меню:", reply_markup=KEYBOARD_MAIN)
        client.disconect()
def getCallback(query, context, update, textToEdit):
    print("start callback")
    subscribe.callback(hostname=MQTT_HOST, port=MQTT_PORT,
                           auth={'username': MQTT_LOGIN, 'password': MQTT_PASSWORD}, callback=onCallback,
                           topics=[MQTT_TOPIC_DOOR_LIFT, MQTT_TOPIC_DOOR_STAIRS])
    print("end callback")
def getSubData(query, context, update, textToEdit):

    m = subscribe.simple(hostname=MQTT_HOST, port=MQTT_PORT,
                         auth={'username': MQTT_LOGIN, 'password': MQTT_PASSWORD},
                         topics=[MQTT_TOPIC_DOOR_LIFT, MQTT_TOPIC_DOOR_STAIRS], msg_count=2)
    for a in m:
        print(a.topic)
        print(a.payload)
    if m[0].payload.decode("utf-8") == "off" and m[1].payload.decode("utf-8") == "off":
        query.edit_message_text(text=textToEdit)
        context.bot.send_message(chat_id=update.effective_chat.id, text="Главное меню:", reply_markup=KEYBOARD_MAIN)
"""
def openDoorToApartment(secDelay):
    global textToGroup
    global baseTextToGroup
    time.sleep(secDelay)
    publish.single(MQTT_TOPIC_DOOR_APARTMENT, MQTT_TEXT_TO_OPEN_DOOR, hostname=MQTT_HOST, port=MQTT_PORT,
                   auth={'username': MQTT_LOGIN, 'password': MQTT_PASSWORD}, retain=True)
    textToGroup = baseTextToGroup+"в квартиру"

def openDoor(cb_data, query, update, context):
    global MYCHATID
    global USERNAME
    global textToEdit
    global MESSAGE_ID
    global baseTextToGroup
    global textToGroup
    # print("openDoor")
    username = USER_ID_TO_NAME[query.message.chat_id]#getUserName(query, update)
    baseTextToGroup = username
    baseTextToGroup+=" открыл дверь "
   # print(username, query.message.chat_id)

    if cb_data == KEYBOARD_DOOR_LIST_CALLBACK_LIFT:
        textToGroup = baseTextToGroup + cb_data
        publish.single(MQTT_TOPIC_DOOR_LIFT, MQTT_TEXT_TO_OPEN_DOOR, hostname=MQTT_HOST, port=MQTT_PORT,
                       auth={'username': MQTT_LOGIN, 'password': MQTT_PASSWORD}, retain=True)

    elif cb_data == KEYBOARD_DOOR_LIST_CALLBACK_STAIRS:
        textToGroup = baseTextToGroup + cb_data
        publish.single(MQTT_TOPIC_DOOR_STAIRS, MQTT_TEXT_TO_OPEN_DOOR, hostname=MQTT_HOST, port=MQTT_PORT,
                       auth={'username': MQTT_LOGIN, 'password': MQTT_PASSWORD}, retain=True)
        # publish.single(MQTT_TOPIC_STAIRS, "open_stairs", hostname=MQTT_HOST, port=MQTT_PORT,
        #              auth={'username': MQTT_LOGIN, 'password': MQTT_PASSWORD}, retain=True)
    elif cb_data == KEYBOARD_DOOR_LIST_CALLBACK_APARTMENT:
        textToGroup = baseTextToGroup + cb_data
        publish.single(MQTT_TOPIC_DOOR_APARTMENT, MQTT_TEXT_TO_OPEN_DOOR, hostname=MQTT_HOST, port=MQTT_PORT,
                       auth={'username': MQTT_LOGIN, 'password': MQTT_PASSWORD}, retain=True)

    elif cb_data == KEYBOARD_DOOR_LIST_CALLBACK_APARTMENT_AND_LIFT:
        publish.single(MQTT_TOPIC_DOOR_LIFT, MQTT_TEXT_TO_OPEN_DOOR, hostname=MQTT_HOST, port=MQTT_PORT,
                      auth={'username': MQTT_LOGIN, 'password': MQTT_PASSWORD}, retain=True)
        textToGroup = baseTextToGroup + KEYBOARD_DOOR_LIST_CALLBACK_LIFT
        x = threading.Thread(target=openDoorToApartment, args=[10])
        x.start()
    elif cb_data == KEYBOARD_DOOR_LIST_CALLBACK_APARTMENT_AND_STAIRS:
        publish.single(MQTT_TOPIC_DOOR_STAIRS, MQTT_TEXT_TO_OPEN_DOOR, hostname=MQTT_HOST, port=MQTT_PORT,
                      auth={'username': MQTT_LOGIN, 'password': MQTT_PASSWORD}, retain=True)
        textToGroup = baseTextToGroup + KEYBOARD_DOOR_LIST_CALLBACK_STAIRS
        x = threading.Thread(target=openDoorToApartment, args=[23])
        x.start()


    textToEdit = textToEdit = "Здравствуйте, "
    textToEdit+=username
    textToEdit += "\nДверь открыта, заходите, пожалуйста"
    #print(textToGroup)
    #textToGroup+=str(datetime.datetime.now())



    MYCHATID = query.message.chat_id
    USERNAME = textToEdit
    MESSAGE_ID = query.message.message_id


#  x = multiprocessing.Process(target=getCallback(query, context, update, textToEdit), args=(1,))
#  x.start()
# print("end Thread")
# x.join()
#   query.edit_message_text(text=textToEdit)
#  context.bot.send_message(chat_id=update.effective_chat.id, text="Главное меню:", reply_markup=KEYBOARD_MAIN)

def getUserName(query, update):

    if query.message.chat.type == "group":
        try:
            return query.from_user.first_name + " " + query.from_user.last_name

        except:
            return query.from_user.first_name
    else:
        try:
            return update.callback_query.message.chat.first_name + " " + update.callback_query.message.chat.last_name  # !!!добавить фильтр по имени

        except:
            return update.callback_query.message.chat.first_name  # !!!добавить фильтр по имени