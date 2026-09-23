#include <WiFi.h>
#include <HTTPClient.h>

// Credenciais da rede Wi-Fi simulada do Wokwi
const char *ssid = "Wokwi-GUEST";
const char *password = "";

// URL do nosso backend exposta pelo ngrok
const char *serverUrl = "https://6606286b9d2d02.lhr.life/telemetria";
const char *apiKey = "senha123"; // Deve ser igual ao API_KEY do seu .env

void setup()
{
  Serial.begin(115200);
  delay(1000);

  // Conectando ao Wi-Fi do Wokwi
  Serial.print("Conectando ao Wi-Fi");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWi-Fi conectado com sucesso!");
  Serial.print("IP local: ");
  Serial.println(WiFi.localIP());
}

void loop()
{
  if (WiFi.status() == WL_CONNECTED)
  {
    HTTPClient http;

    Serial.println("\nEnviando telemetria CAN para o MAIA...");

    http.begin(serverUrl);

    // Cabeçalhos obrigatórios exigidos pelo nosso backend
    http.addHeader("Content-Type", "application/json");
    http.addHeader("X-API-KEY", apiKey);

    // Payload JSON com os campos exigidos pelo schema TelemetriaInput
    String payload = "{";
    payload += "\"equipamento_id\": \"EQP-SP-04\",";
    payload += "\"data_medicao\": \"2026-09-20\",";
    payload += "\"temp_coolant\": 82.5,";
    payload += "\"temp_oleo\": 92.0,";
    payload += "\"pressao_oleo\": 380.0,";
    payload += "\"torque_pct\": 72.0,";
    payload += "\"rpm\": 1850.0,";
    payload += "\"combustivel_l_h\": 15.5,";
    payload += "\"velocidade_kmh\": 8.5,";
    payload += "\"manutencao_dias\": 15";
    payload += "}";

    // Executa a requisição POST
    int httpResponseCode = http.POST(payload);

    if (httpResponseCode > 0)
    {
      String responseString = http.getString();
      Serial.printf("Sucesso! Código HTTP: %d\n", httpResponseCode);
      Serial.println("Resposta do Servidor: " + responseString);
    }
    else
    {
      Serial.printf("Erro na requisição POST. Código: %d\n", httpResponseCode);
    }

    http.end(); // Libera os recursos de conexão
  }
  else
  {
    Serial.println("Erro: Wi-Fi desconectado.");
  }

  // Envia um novo pacote a cada 10 segundos
  delay(10000);
}