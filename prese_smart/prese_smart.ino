#include <WebServer.h>
#include <WiFi.h>

#define sensore 5

WebServer server(80);  // Crea un oggetto server sulla porta 80
const char* ap_ssid = "Tachimetro";  // Nome AP per la configurazione
const char* ap_password = "supersecurepassword";  // Password AP

void setup() {
  // Avvia la seriale per il debug
  Serial.begin(9600);
  pinMode(sensore, INPUT);

  // Avvia l'AP
  WiFi.softAP(ap_ssid, ap_password);
  Serial.println("Access Point creato");
  Serial.print("Indirizzo IP AP: ");
  Serial.println(WiFi.softAPIP());

  // Pagina per inviare le credenziali Wi-Fi
  /*server.on("/config_wifi", HTTP_POST, []() {
    if (server.hasArg("ssid") && server.hasArg("password")) {
      String wifi_ssid = server.arg("ssid");
      String wifi_password = server.arg("password");
      server.send(200, "text/html", "<html>Credenziali ricevute. Tentativo di connessione in corso...</html>");
      Serial.println("Credenziali Wi-Fi ricevute:");
      Serial.println("SSID: " + wifi_ssid);
      Serial.println("Password: " + wifi_password);

    } else {
      server.send(400, "text/html", "<html>Errore: Credenziali non valide.</html>");
    }
  });*/

  server.on("/index", HTTP_GET, []() {
    Serial.println("Received: GET /index");
    server.send(200, "text/html", "<html>pagina principale (grafico velocità, velocità massima, strada percorsa</html>");
  });

  server.on("/config", HTTP_POST, []() {
    Serial.println("Received: POST /config");
    server.send(200, "text/html", "<html>ok</html>");
  });

  server.on("/config", HTTP_GET, []() {
    Serial.println("Received: GET /config");
    server.send(200, "text/html", "<html>front-end per configurare nome, password, diametro ruota</html>");
  });

  // Avvia il server web
  server.begin();
  Serial.println("Server AP avviato!");
}

int start;

void loop() {
  // Mantieni il server in esecuzione
  server.handleClient();
}