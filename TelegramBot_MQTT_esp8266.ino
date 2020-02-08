/*******************************************************************
*  An example of bot that echos back any messages received         *
*                                                                  *
*  written by Giacarlo Bacchio (Gianbacchio on Github)             *
*  adapted by Brian Lough                                          *
*******************************************************************/
#include <ESP8266WiFi.h>
#include <WiFiClientSecure.h>
#include <UniversalTelegramBot.h>
#include <PubSubClient.h>
String clientName = "CLIENTNAME";
// Initialize Wifi connection to the router
char ssid[] = "login";     // your network SSID (name)
char password[] = "password"; // your network key

const char *mqtt_server = "MQTT_IP"; // Имя сервера MQTT
const int mqtt_port = 0; // Порт для подключения к серверу MQTT
const char *mqtt_user = "loginMQTT"; // Логи от сервер
const char *mqtt_pass = "passwordMQTT"; // Пароль от сервера

// Initialize Telegram BOT
#define BOTtoken "BOT_TOKEN"  // your Bot Token (Get from Botfather)

WiFiClientSecure wclient;
WiFiClient wclientMQTT;
PubSubClient client(wclientMQTT, mqtt_server, mqtt_port);

UniversalTelegramBot bot(BOTtoken, wclient);

int Bot_mtbs = 1000; //mean time between scan messages
long Bot_lasttime;   //last time messages' scan has been done

const int ledPin = 1;
int ledStatus = 0;


void callback(const MQTT::Publish& pub)
{
//Serial.print("In callback    ");
Serial.print(pub.topic()); // выводим в сериал порт название топика
Serial.print(" => ");
Serial.println(pub.payload_string()); // выводим в сериал порт значение полученных данных

String payload = pub.payload_string();

if(String(pub.topic()) == "corridor/door/lift") // проверяем из нужного ли нам топика пришли данные
{

if(payload == "on")
{
toggleRelay(true); // включаем или выключаем светодиод в зависимоти от полученных значений данных
delay(1000);
toggleRelay(false);
Serial.println("door opened");
client.publish("corridor/door/lift", "off");
}

//client.publish("led/data", String(stled));//Replace from print to publish
}
}


void handleNewMessages(int numNewMessages) {
  Serial.println("handleNewMessages");
  Serial.println(String(numNewMessages));

  for (int i=0; i<numNewMessages; i++) {
    String chat_id = String(bot.messages[i].chat_id);
    String text = bot.messages[i].text;

    String from_name = bot.messages[i].from_name;
    if (from_name == "") from_name = "Guest";

    if (text == "/unlock") {
       toggleRelay(true);
       delay(1000);
       toggleRelay(false);
       Serial.println("door opened");
      digitalWrite(ledPin, HIGH);   // turn the LED on (HIGH is the voltage level)
      ledStatus = 0 ;
      bot.sendMessage(chat_id, "Door is ON", "");
    }

    if (text == "/status") {
      if(ledStatus){
        bot.sendMessage(chat_id, "Door is close", "");
      } else {
        bot.sendMessage(chat_id, "Door is OFF", "");
      }
    }

    if (text == "/start") {
      String welcome = "Welcome to Universal Arduino Telegram Bot library, " + from_name + ".\n";
      welcome += "This is opening door Bot example.\n\n";
      welcome += "/unlock : to unlock the door \n";
      welcome += "/dooroff : to switch the door OFF\n";
      welcome += "/status : Returns current status of door\n";
      bot.sendMessage(chat_id, welcome, "Markdown");
    }
  }
}


void toggleRelay(bool relayState)
{
    if (relayState)
    {
        const byte miBufferON[] = {0xA0, 0x01, 0x01, 0xA2};
        Serial.write(miBufferON, sizeof(miBufferON));
        // val = 1;
    }
    else
    {
        //To disable the Relay send it by serial port:
        const byte miBufferOFF[] = {0xA0, 0x01, 0x00, 0xA1};
        Serial.write(miBufferOFF, sizeof(miBufferOFF));
        // val = 0;
    }
}

void setup() {
  Serial.begin(9600);
 //delay(1000);
   Serial.println("set");
//   delay(2000);
 
//pinMode(ledPin, OUTPUT);
//delay(1000);
 
  Serial.println("done");
 //delay(1000);
 
///   digitalWrite(ledPin, LOW);
//delay(1000);
 
   Serial.println("set2");

 digitalWrite(ledPin, LOW); // initialize pin as off
    Serial.println("done2");

  // Set WiFi to station mode and disconnect from an AP if it was Previously
  // connected
  WiFi.mode(WIFI_STA);
  WiFi.disconnect();
  delay(100);

  // Attempt to connect to Wifi network:
  Serial.print("Connecting Wifi: ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(500);
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
 // bot._debug=true;
wclient.setInsecure();

 

}

void loop() {
 


if (WiFi.status() != WL_CONNECTED) {
Serial.print("Connecting to ");
Serial.print(ssid);
Serial.println("...");
WiFi.begin(ssid, password);

if (WiFi.waitForConnectResult() != WL_CONNECTED)
return;
Serial.println("WiFi connected");
}



// подключаемся к MQTT серверу
if (WiFi.status() == WL_CONNECTED) {
  
if (!client.connected()) {
Serial.println("Connecting to MQTT server");
if (client.connect(MQTT::Connect(clientName).set_auth(mqtt_user, mqtt_pass))) {
Serial.println("Connected to MQTT server");

//Serial.println("Start register callback");

client.set_callback(callback);
//Serial.println("Completed register callback");

//Serial.println("Start subscribe to test/led");

client.subscribe("corridor/door/lift"); // подписывааемся по топик с данными для светодиода
//Serial.println("End subscribtion");
//client.publish("test/test","its work");

} else {
Serial.println("Could not connect to MQTT server");
}
} else {

//Serial.println("MQTT is still connected");  
delay(1000);
}


if (client.connected()){
//Serial.println("client is connected");

//Serial.println("Start client.loop");

client.loop();
//Serial.println("Complete client.loop");

//Var = "";


//Serial.println("Var was initialized");
/*
  while(Serial.available())
  {
    Var = Var+(char)Serial.read();
  }
if (Var!="") {
  //Serial.println("Serial read ccompleted");
//Serial.println("Start publish");

//publishMessages(Var);
//Serial.println("Finished publish");
}*/

//client.publish("test/statusESP8266", "If you see, that count of messages is increasing, so ESP8266 is working!");




//Serial.println("End loop");
//delay(2000);
}
if (millis() > Bot_lasttime + Bot_mtbs)  {

    int numNewMessages = bot.getUpdates(bot.last_message_received + 1);
    //Serial.println("GetUpdates succesful");
    //Serial.println(numNewMessages);
    while(numNewMessages) {
    //  Serial.println("got response");
      handleNewMessages(numNewMessages);
      numNewMessages = bot.getUpdates(bot.last_message_received + 1);
    }

    Bot_lasttime = millis();
  }
}
//Serial.println("Start to get message from bot");
  
 }
 // конец основного цикла

  
