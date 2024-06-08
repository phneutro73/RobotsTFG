#include <WiFi.h>
#include <AsyncTCP.h>
#include <ESPAsyncWebSrv.h>
#include <esp_now.h>

const char* ssid = "RedTFG";
const char* password = "TFG12345678!";
AsyncWebServer server(80);

// MAC Addresses de los dispositivos ESP32 esclavos
uint8_t broadcastAddress1[] = {0x08, 0xD1, 0xF9, 0xE2, 0xC8, 0xA0};
uint8_t broadcastAddress2[] = {0x08, 0xD1, 0xF9, 0xE2, 0xD5, 0x98};

// Configurar la página web
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
            flex-direction: column;
            justify-content: center;
            align-items: center;
            
            height: 100vh;
            margin: 0;
            background-color: #8a8a8a;
        }

        .top-bottom{
          display: flex;
          justify-content: center;
          align-items: center;
          padding: 10px;
        }

        .center {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 10px;
        }
        button {
            width: 120px;
            height: 120px;
            font-size: 64px;
            border: none;
            border-radius: 50%;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        #stop{
          font-size: 32px;
        }
        button:hover {
            background-color: #ddd;
        }

    </style>
</head>
<body>
    <h1>Control de Motores</h1>
    <div class="top-bottom"><button onclick="sendCommand('S')">&#9650;</button></div>
    <div class="center">
        <button onclick="sendCommand('A')">&#9664;</button>
        <button id="stop" onclick="sendCommand('0')">STOP</button>
        <button onclick="sendCommand('D')">&#9654;</button>
    </div>
    <div class="top-bottom"><button onclick="sendCommand('Z')">&#9660;</button></div>
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

void sendEspNowCommand(String command, String id) {
    // Convertir la cadena en un array de char
    char cmd[2];
    command.toCharArray(cmd, 2);

    if (id == "71") {
        esp_now_send(broadcastAddress1, (uint8_t *)cmd, sizeof(cmd));
    } else if (id == "101") {
        esp_now_send(broadcastAddress2, (uint8_t *)cmd, sizeof(cmd));
    } else {
        esp_now_send(broadcastAddress1, (uint8_t *)cmd, sizeof(cmd));
        // esp_now_send(broadcastAddress2, (uint8_t *)cmd, sizeof(cmd));
    }
    
    // Lista de todos los dispositivos a los cuales enviar el mensaje
    uint8_t* broadcastAddresses[] = {broadcastAddress1, broadcastAddress2};
    size_t numberOfDevices = sizeof(broadcastAddresses) / sizeof(broadcastAddresses[0]);
    
    // Enviar el comando a cada dispositivo en la lista
    for (int i = 0; i < numberOfDevices; i++) {
        esp_now_send(broadcastAddresses[i], (uint8_t *)cmd, sizeof(cmd));
    }
}

void OnDataSent(const uint8_t *mac_addr, esp_now_send_status_t status) {
    Serial.print("Last Packet Send Status:\t");
    Serial.println(status == ESP_NOW_SEND_SUCCESS ? "Delivery Success" : "Delivery Fail");
}

void setup() {
    Serial.begin(115200);

    Serial.println("--- Prueba flota transmitter ---");

    // Iniciar WiFi
    WiFi.mode(WIFI_STA);
    WiFi.begin(ssid, password);

    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.println("Connecting to WiFi..");
    }

    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());

    // Configurar servidor web
    server.on("/", HTTP_GET, [](AsyncWebServerRequest *request){
        request->send(200, "text/html", html);
    });

    server.on("/command", HTTP_GET, [](AsyncWebServerRequest *request) {
        String cmd;
        String id;
        if (request->hasParam("cmd")) {
            cmd = request->getParam("cmd")->value();
            sendEspNowCommand(cmd,id);
            request->send(200, "text/plain", "Command Sent: " + cmd);
        } else {
            request->send(400, "text/plain", "Command not specified");
        }
    });

    server.begin();

    // Iniciar ESP-NOW
    if (esp_now_init() != ESP_OK) {
        Serial.println("Error initializing ESP-NOW");
        return;
    }
    else {
        Serial.println("Success: Initialized ESP-NOW");
    }

    // Añadir todos los dispositivos como pares
    addPeer(broadcastAddress1);
    addPeer(broadcastAddress2);

    esp_now_register_send_cb(OnDataSent);
}

void addPeer(uint8_t *peerAddress) {
    esp_now_peer_info_t peerInfo;
    memset(&peerInfo, 0, sizeof(esp_now_peer_info_t));
    memcpy(peerInfo.peer_addr, peerAddress, 6);
    peerInfo.channel = 0;
    peerInfo.encrypt = false;

    if (esp_now_add_peer(&peerInfo) != ESP_OK) {
        Serial.print("Failed to add peer with MAC: ");
        for (int i = 0; i < 6; ++i) {
            Serial.printf("%02X:", peerAddress[i]);
        }
        Serial.println();
    }
    else {
        Serial.print("Success: Added peer with MAC: ");
        for (int i = 0; i < 6; ++i) {
            Serial.printf("%02X:", peerAddress[i]);
        }
        Serial.println();
    }
}

void loop() {
    // Poner aquí más código si es necesario
}
