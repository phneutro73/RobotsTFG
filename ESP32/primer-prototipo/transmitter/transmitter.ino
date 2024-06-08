#include <esp_now.h>
#include <AsyncTCP.h>
#include <ESPAsyncWebSrv.h>
#include <WiFi.h>

const char* ssid = "RedTFG";
const char* password = "TFG12345678!";
AsyncWebServer server(80);

uint8_t receiverMacAddress[] = {0x08, 0xD1, 0xF9, 0xE2, 0xC8, 0xA0}; // MAC Address of the receiver

struct PacketData
{
  byte dirValue;
};
PacketData data;

//Web page controller code
const char* html = R"html(
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Control de Motores</title>
    <style>
        body {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background-color: #f4f4f4;
        }
        .joystick {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 10px;
        }
        button {
            width: 60px;
            height: 60px;
            font-size: 24px;
            border: none;
            border-radius: 50%;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        button:hover {
            background-color: #ddd;
        }
        #stop {
            grid-column: 2;
            grid-row: 2;
        }
    </style>
</head>
<body>
    <div class="joystick">
        <button onclick="sendCommand('S')">&#9650;</button> <!-- Arriba -->
        <button onclick="sendCommand('A')">&#9664;</button> <!-- Izquierda -->
        <button id="stop" onclick="sendCommand('0')">STOP</button> <!-- Parar -->
        <button onclick="sendCommand('D')">&#9654;</button> <!-- Derecha -->
        <button onclick="sendCommand('Z')">&#9660;</button> <!-- Abajo -->
    </div>
    <script>
        function sendCommand(cmd) {
            var xhr = new XMLHttpRequest();
            xhr.open('GET', '/command?cmd=' + cmd, true);
            xhr.onreadystatechange = function () {
                if (xhr.readyState === 4 && xhr.status === 200) {
                    console.log('Response: ' + xhr.responseText);
                }
            };
            xhr.send();
        }
    </script>
</body>
</html>
)html";

void sendEspNowCommand(String command) {
  // Convertir la cadena en char array
  char cmd[2];
  command.toCharArray(cmd, 2);
  esp_now_send(receiverMacAddress, (uint8_t *)cmd, sizeof(cmd));
}

// callback when data is sent
void OnDataSent(const uint8_t *mac_addr, esp_now_send_status_t status)
{
  //Serial.print("\r\nLast Packet Send Status:\t ");
  //Serial.println(status);
  Serial.println(status == ESP_NOW_SEND_SUCCESS ? "Message sent" : "Message failed");
}

void setup() 
{
  
  Serial.begin(115200);
  WiFi.mode(WIFI_STA);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi..");
  }

  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  //Setup web server
  server.on("/", HTTP_GET, [](AsyncWebServerRequest *request) {
    request->send(200, "text/html", html);
  });

  server.on("/command", HTTP_GET, [](AsyncWebServerRequest *request) {
    String cmd;
      if (request->hasParam("cmd")) {
          cmd = request->getParam("cmd")->value();
          sendEspNowCommand(cmd);
          request->send(200, "text/plain", "Command Sent: " + cmd);
      } else {
          request->send(400, "text/plain", "Command not specified");
      }
  });

  server.begin();

  // Init ESP-NOW
  if (esp_now_init() != ESP_OK) 
  {
    Serial.println("Error initializing ESP-NOW");
    return;
  }
  else
  {
    Serial.println("Success: Initialized ESP-NOW");
  }

  
  
  // Register peer
  esp_now_peer_info_t peerInfo;
  memset(&peerInfo, 0, sizeof(esp_now_peer_info_t));
  memcpy(peerInfo.peer_addr, receiverMacAddress, 6);
  peerInfo.channel = 0;  
  peerInfo.encrypt = false;
  
  // Add peer        
  if (esp_now_add_peer(&peerInfo) != ESP_OK)
  {
    Serial.println("Failed to add peer");
    return;
  }
  else
  {
    Serial.println("Success: Added peer");
  } 
   
  esp_now_register_send_cb(OnDataSent);
}

void loop()
{
  esp_err_t result = esp_now_send(receiverMacAddress, (uint8_t *) &data, sizeof(data));
  if (result == ESP_OK) 
  {
    //Serial.println("Sent with success");
  }
  else 
  {
    // Serial.println("Error sending the data");
  }
  sendEspNowCommand("Q");
  delay(1000);
}
