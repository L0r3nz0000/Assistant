// #include <WiFi.h> 
// #include <WebServer.h>

// #define rele 5

// const char* ssid = "Lorenzo";
// const char* password = "bohunapassword";

// WebServer server(80);

// void setup() {
//   // Avvia la seriale per il debug
//   Serial.begin(9600);
//   pinMode(rele, OUTPUT);
//   delay(3000);

//   // Connessione alla rete Wi-Fi
//   WiFi.begin(ssid, password);
//   Serial.print("Connessione in corso");
  
//   // Attendi fino a quando non si connette al Wi-Fi
//   while (WiFi.status() != WL_CONNECTED) {
//     delay(1000);
//     Serial.print(".");
//   }

//   Serial.println("");
//   Serial.println("Connesso al Wi-Fi!");
//   Serial.print("Indirizzo IP: ");
//   Serial.println(WiFi.localIP());

//   // Configura la route per la root "/"
//   server.on("/login", HTTP_GET, []() {
//     Serial.println("Received: GET /login");
//     server.send(200, "text/html", "<html>ciao sei nella pagina /login</html>");
//   });

//   server.on("/power_on", HTTP_POST, []() {  // post request
//     Serial.println("Received: POST /power_on");
//     digitalWrite(rele, HIGH);
//     server.send(200, "text/html", "<html>relè acceso</html>");
//   });

//   server.on("/power_off", HTTP_POST, []() {  // post request
//     Serial.println("Received: POST /power_off");
//     digitalWrite(rele, LOW);
//     server.send(200, "text/html", "<html>relè spento</html>");
//   });

//   // Avvia il server
//   server.begin();
//   Serial.println("Server avviato!");
// }

// void loop() {
//   // Mantieni il server in esecuzione
//   server.handleClient();
// }


#include <WiFi.h>
#include <WebServer.h>

#define rele 5

WebServer server(80);  // Crea un oggetto server sulla porta 80
const char* ap_ssid = "Config_AP";  // Nome AP per la configurazione
const char* ap_password = "12345678";  // Password AP

// Variabili per memorizzare le credenziali Wi-Fi ricevute
String wifi_ssid = "";
String wifi_password = "";

void setup() {
  // Avvia la seriale per il debug
  Serial.begin(9600);
  pinMode(rele, OUTPUT);
  delay(1000);

  // Avvia l'AP per permettere la configurazione Wi-Fi
  WiFi.softAP(ap_ssid, ap_password);
  Serial.println("Access Point creato");
  Serial.print("Indirizzo IP AP: ");
  Serial.println(WiFi.softAPIP());

  // Pagina per inviare le credenziali Wi-Fi
  server.on("/config_wifi", HTTP_POST, []() {
    if (server.hasArg("ssid") && server.hasArg("password")) {
      wifi_ssid = server.arg("ssid");
      wifi_password = server.arg("password");
      server.send(200, "text/html", "<html>Credenziali ricevute. Tentativo di connessione in corso...</html>");
      Serial.println("Credenziali Wi-Fi ricevute:");
      Serial.println("SSID: " + wifi_ssid);
      Serial.println("Password: " + wifi_password);

      // Prova a connettersi al Wi-Fi ricevuto
      connectToWiFi();
    } else {
      server.send(400, "text/html", "<html>Errore: Credenziali non valide.</html>");
    }
  });

  // Route per accendere il relè
  server.on("/power_on", HTTP_POST, []() {
    Serial.println("Received: POST /power_on");
    digitalWrite(rele, HIGH);
    server.send(200, "text/html", "<html>relè acceso</html>");
  });

  // Route per spegnere il relè
  server.on("/power_off", HTTP_POST, []() {
    Serial.println("Received: POST /power_off");
    digitalWrite(rele, LOW);
    server.send(200, "text/html", "<html>relè spento</html>");
  });

  // Avvia il server web
  server.begin();
  Serial.println("Server AP avviato!");
}

void loop() {
  // Mantieni il server in esecuzione
  server.handleClient();
}

void connectToWiFi() {
  // Disabilita l'AP per risparmiare risorse
  WiFi.softAPdisconnect(true);

  // Avvia la connessione alla rete Wi-Fi
  WiFi.begin(wifi_ssid.c_str(), wifi_password.c_str());
  Serial.print("Connessione a " + wifi_ssid);

  // Attende la connessione
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {  // Fino a 20 tentativi
    delay(1000);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("");
    Serial.println("Connesso al Wi-Fi!");
    Serial.print("Indirizzo IP: ");
    Serial.println(WiFi.localIP());

    // Riavvia il server web per lavorare sulla rete Wi-Fi
    server.close();
    server.begin();
    Serial.println("Server Wi-Fi avviato!");

  } else {
    Serial.println("");
    Serial.println("Connessione fallita. Riavvio AP...");
    // Se fallisce, riavvia l'AP per riprovare
    WiFi.softAP(ap_ssid, ap_password);
    Serial.println("AP riavviato");
    Serial.print("Indirizzo IP AP: ");
    Serial.println(WiFi.softAPIP());
  }
}
