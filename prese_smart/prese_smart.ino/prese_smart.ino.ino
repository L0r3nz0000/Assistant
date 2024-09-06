#include <WiFi.h> 
#include <WebServer.h>

#define rele 5

const char* ssid = "Home&Life SuperWiFi-FBAD";
const char* password = "Mostarda007";

WebServer server(80);

void setup() {
  // Avvia la seriale per il debug
  Serial.begin(9600);
  pinMode(rele, OUTPUT);
  delay(3000);

  // Connessione alla rete Wi-Fi
  WiFi.begin(ssid, password);
  Serial.print("Connessione in corso");
  
  // Attendi fino a quando non si connette al Wi-Fi
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("Connesso al Wi-Fi!");
  Serial.print("Indirizzo IP: ");
  Serial.println(WiFi.localIP());

  // Configura la route per la root "/"
  server.on("/login", HTTP_GET, []() {
    Serial.println("Received: GET /login");
    server.send(200, "text/html", "<html>ciao sei nella pagina /login</html>");
  });

  server.on("/power_on", HTTP_POST, []() {  // post request
    Serial.println("Received: POST /power_on");
    digitalWrite(rele, HIGH);
    server.send(200, "text/html", "<html>relè aceso</html>");
  });

  server.on("/power_off", HTTP_POST, []() {  // post request
    Serial.println("Received: POST /power_off");
    digitalWrite(rele, LOW);
    server.send(200, "text/html", "<html>relè spento</html>");
  });

  // Avvia il server
  server.begin();
  Serial.println("Server avviato!");
}

void loop() {
  // Mantieni il server in esecuzione
  server.handleClient();
}
