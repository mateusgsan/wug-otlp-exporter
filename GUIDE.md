# WhatsUp Gold OTLP Exporter - Guia Completo

**Data:** 13 de Março de 2026
**Versão:** 1.0

---

## 1. Introdução

O **WhatsUp Gold OTLP Exporter** é uma solução que exporta métricas do WhatsUp Gold diretamente em formato **OTLP (OpenTelemetry Protocol)**, permitindo integração nativa com **Grafana Cloud** e outras plataformas de observabilidade.

### Vantagens sobre o wug-exporter original

| Aspecto | wug-exporter (Prometheus) | OTLP Exporter |
| :--- | :--- | :--- |
| **Formato** | Prometheus Text Format | OTLP (gRPC/HTTP) |
| **Integração Grafana Cloud** | Via Prometheus Remote Write | Nativa (OTLP) |
| **Performance** | Pull-based | Push-based com batching |
| **Semântica** | Prometheus | OpenTelemetry |
| **Suporte a Traces** | Não | Preparado para futuro |
| **Compressão** | Não | Sim (gRPC) |
| **Autenticação** | Básica | Headers customizados |

---

## 2. Arquitetura

```
┌──────────────────────┐
│  WhatsUp Gold        │
│  (On-Premises)       │
│  REST API (9644)     │
└──────────┬───────────┘
           │ HTTPS
           │ (REST API)
           ▼
┌──────────────────────────────────┐
│  OTLP Exporter                   │
│  (Python)                        │
│  • Scrape WUG API                │
│  • Transform to OTLP             │
│  • Batch metrics                 │
└──────────┬───────────────────────┘
           │ OTLP (gRPC/HTTP)
           │ (Encrypted)
           ▼
┌──────────────────────────────────┐
│  Grafana Cloud                   │
│  • OTLP Receiver                 │
│  • Metrics Storage               │
│  • Dashboards & Alerts           │
└──────────────────────────────────┘
```

---

## 3. Instalação

### 3.1. Pré-requisitos

- Python 3.10+
- WhatsUp Gold 2019.1+ com REST API habilitada
- Acesso à Grafana Cloud (ou OpenTelemetry Collector local)
- Conectividade de rede entre exporter e WhatsUp Gold
- Conectividade de rede entre exporter e Grafana Cloud

### 3.2. Instalação do Exporter

```bash
# Clone ou baixe os arquivos
git clone <seu-repositorio>/wug-otlp-exporter.git
cd wug-otlp-exporter

# Instale as dependências
pip install -r requirements_otlp.txt

# Configure as variáveis de ambiente
cp .env.example .env
# Edite .env com suas credenciais
```

### 3.3. Configuração

Edite o arquivo `.env` com as seguintes informações:

```bash
# WhatsUp Gold
WUG_URL=https://seu-wug-server:9644/api/v1
WUG_USERNAME=seu_usuario_api
WUG_PASSWORD=sua_senha_api
VERIFY_SSL=true

# OTLP - Grafana Cloud
OTLP_ENDPOINT=otlp-gateway-prod-us-central-1.grafana.net:443
OTLP_PROTOCOL=grpc
OTLP_HEADERS=Authorization=Bearer seu_token_grafana

# Configurações gerais
SERVICE_NAME=whatsup-gold
SCRAPE_INTERVAL=60
```

---

## 4. Configuração do Grafana Cloud

### 4.1. Obter Token OTLP

1. Acesse **Grafana Cloud** → **Connections** → **Data Sources**
2. Procure por **OTLP** ou **OpenTelemetry**
3. Copie o **endpoint** e o **token de autenticação**

### 4.2. Exemplo de Configuração Grafana Cloud

```bash
# Para us-central-1
OTLP_ENDPOINT=otlp-gateway-prod-us-central-1.grafana.net:443
OTLP_PROTOCOL=grpc
OTLP_HEADERS=Authorization=Bearer glc_eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Para eu-west-1
OTLP_ENDPOINT=otlp-gateway-prod-eu-west-1.grafana.net:443

# Para us-west-2
OTLP_ENDPOINT=otlp-gateway-prod-us-west-2.grafana.net:443
```

---

## 5. Uso

### 5.1. Executar o Exporter

```bash
# Linux/Mac
export $(cat .env | xargs)
python wug_otlp_exporter.py

# Windows
# Configure as variáveis de ambiente manualmente ou use:
python -m dotenv run python wug_otlp_exporter.py
```

### 5.2. Verificar Logs

```
2026-03-13 10:30:45,123 - __main__ - INFO - WhatsUp Gold OTLP Exporter inicializado
2026-03-13 10:30:45,124 - __main__ - INFO -   WUG URL: https://wug-server:9644/api/v1
2026-03-13 10:30:45,125 - __main__ - INFO -   OTLP Endpoint: otlp-gateway-prod-us-central-1.grafana.net:443
2026-03-13 10:30:45,126 - __main__ - INFO -   Protocol: grpc
2026-03-13 10:30:45,127 - __main__ - INFO -   Scrape Interval: 60s
2026-03-13 10:30:45,128 - __main__ - INFO - Instrumentos de métrica criados
2026-03-13 10:30:45,129 - __main__ - INFO - Iniciando exporter...
2026-03-13 10:30:45,130 - __main__ - INFO - Iniciando scrape de métricas...
2026-03-13 10:30:46,234 - __main__ - INFO - Obtendo novo token de acesso...
2026-03-13 10:30:46,567 - __main__ - INFO - Token obtido com sucesso
2026-03-13 10:30:46,890 - __main__ - INFO - Obtidos 42 dispositivos
2026-03-13 10:30:47,123 - __main__ - INFO - Scrape concluído em 1.99s - UP: 38, DOWN: 2, MAINT: 2
```

---

## 6. Métricas Exportadas

### 6.1. Métricas Disponíveis

| Métrica | Tipo | Descrição | Labels |
| :--- | :--- | :--- | :--- |
| `wug.device.status` | Counter | Status do dispositivo | device.name, device.ip, device.status |
| `wug.device.total` | Counter | Total de dispositivos | — |
| `wug.alerts.active` | Counter | Alertas ativos | — |
| `wug.device.up` | Gauge | Dispositivos UP | — |
| `wug.device.down` | Gauge | Dispositivos DOWN | — |
| `wug.device.maintenance` | Gauge | Dispositivos em manutenção | — |
| `wug.scrape.duration` | Gauge | Tempo de scrape | — |
| `wug.api.response_time` | Gauge | Tempo de resposta da API | — |

### 6.2. Exemplo de Métrica OTLP

```json
{
  "resourceMetrics": [
    {
      "resource": {
        "attributes": [
          {
            "key": "service.name",
            "value": {
              "stringValue": "whatsup-gold"
            }
          },
          {
            "key": "service.version",
            "value": {
              "stringValue": "1.0.0"
            }
          }
        ]
      },
      "scopeMetrics": [
        {
          "scope": {
            "name": "whatsup-gold",
            "version": "1.0.0"
          },
          "metrics": [
            {
              "name": "wug.device.up",
              "gauge": {
                "dataPoints": [
                  {
                    "asInt": "38",
                    "timeUnixNano": "1678708247123000000"
                  }
                ]
              }
            }
          ]
        }
      ]
    }
  ]
}
```

---

## 7. Dashboards Grafana

### 7.1. Criar Dashboard

1. Acesse Grafana Cloud → **Dashboards** → **Create** → **New Dashboard**
2. Adicione um painel com a seguinte query:

```promql
# Dispositivos UP
{job="whatsup-gold", metric_name="wug_device_up"}

# Dispositivos DOWN
{job="whatsup-gold", metric_name="wug_device_down"}

# Taxa de disponibilidade
rate(wug_device_up[5m]) / (rate(wug_device_up[5m]) + rate(wug_device_down[5m]))
```

### 7.2. Alertas

Configure alertas em Grafana Cloud para notificar quando:

```
# Dispositivos DOWN
wug_device_down > 0

# Scrape falhando
up{job="whatsup-gold"} == 0

# Tempo de scrape alto
wug_scrape_duration > 30
```

---

## 8. Deployment em Produção

### 8.1. Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements_otlp.txt .
RUN pip install --no-cache-dir -r requirements_otlp.txt

COPY wug_otlp_exporter.py .
COPY .env .

CMD ["python", "wug_otlp_exporter.py"]
```

```bash
# Build
docker build -t wug-otlp-exporter:1.0 .

# Run
docker run -d \
  --name wug-exporter \
  --env-file .env \
  -e WUG_URL=https://wug-server:9644/api/v1 \
  -e WUG_USERNAME=admin \
  -e WUG_PASSWORD=password \
  -e OTLP_ENDPOINT=otlp-gateway-prod-us-central-1.grafana.net:443 \
  -e OTLP_PROTOCOL=grpc \
  wug-otlp-exporter:1.0
```

### 8.2. Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: wug-otlp-exporter
  namespace: monitoring
spec:
  replicas: 1
  selector:
    matchLabels:
      app: wug-otlp-exporter
  template:
    metadata:
      labels:
        app: wug-otlp-exporter
    spec:
      containers:
      - name: exporter
        image: wug-otlp-exporter:1.0
        env:
        - name: WUG_URL
          valueFrom:
            secretKeyRef:
              name: wug-credentials
              key: url
        - name: WUG_USERNAME
          valueFrom:
            secretKeyRef:
              name: wug-credentials
              key: username
        - name: WUG_PASSWORD
          valueFrom:
            secretKeyRef:
              name: wug-credentials
              key: password
        - name: OTLP_ENDPOINT
          value: "otlp-gateway-prod-us-central-1.grafana.net:443"
        - name: OTLP_PROTOCOL
          value: "grpc"
        - name: OTLP_HEADERS
          valueFrom:
            secretKeyRef:
              name: grafana-credentials
              key: token
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 512Mi
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
```

---

## 9. Troubleshooting

### Problema: "Connection refused"

**Causa:** WhatsUp Gold não está acessível
**Solução:**
```bash
# Testar conectividade
curl -k https://seu-wug-server:9644/api/v1/product

# Verificar firewall
telnet seu-wug-server 9644
```

### Problema: "Unauthorized (401)"

**Causa:** Credenciais inválidas
**Solução:**
```bash
# Testar credenciais manualmente
curl -k -X POST \
  https://seu-wug-server:9644/api/v1/token \
  -d "grant_type=password&username=seu_usuario&password=sua_senha"
```

### Problema: "OTLP export failed"

**Causa:** Problema de conectividade com Grafana Cloud
**Solução:**
```bash
# Verificar endpoint
telnet otlp-gateway-prod-us-central-1.grafana.net 443

# Verificar token
# Acesse Grafana Cloud e confirme o token OTLP
```

### Problema: "No metrics appearing in Grafana"

**Causa:** Métricas não estão sendo exportadas
**Solução:**
1. Verifique os logs do exporter
2. Confirme que WhatsUp Gold está retornando dispositivos
3. Verifique a configuração OTLP em Grafana Cloud

---

## 10. Comparação: OTLP vs Prometheus

| Aspecto | OTLP | Prometheus |
| :--- | :--- | :--- |
| **Protocolo** | gRPC/HTTP | HTTP Text |
| **Compressão** | Sim (gRPC) | Não |
| **Push/Pull** | Push | Pull |
| **Latência** | Baixa | Média |
| **Escalabilidade** | Excelente | Boa |
| **Integração Grafana Cloud** | Nativa | Via Remote Write |
| **Suporte a Traces** | Sim | Não |
| **Overhead de Rede** | Baixo | Médio |

---

## 11. Próximos Passos

### Melhorias Futuras

- [ ] Suporte a traces (OpenTelemetry Traces)
- [ ] Suporte a logs (OpenTelemetry Logs)
- [ ] Métricas de performance do WhatsUp Gold
- [ ] Integração com alertas do WhatsUp Gold
- [ ] Dashboard pré-configurado para Grafana
- [ ] Suporte a múltiplas instâncias de WhatsUp Gold

### Contribuições

Contribuições são bem-vindas! Por favor, abra uma issue ou pull request no repositório.

---

## 12. Referências

[1] OpenTelemetry Documentation. "OpenTelemetry Protocol (OTLP)." https://opentelemetry.io/docs/specs/otel/protocol/

[2] Grafana Labs. "OTLP Receiver." https://grafana.com/docs/grafana-cloud/send-data/otlp/

[3] Progress Software. "WhatsUp Gold REST API." https://docs.ipswitch.com/nm/whatsupgold2019_1/02_Guides/rest_api/

[4] OpenTelemetry Python SDK. "Getting Started." https://opentelemetry.io/docs/instrumentation/python/

---

## Licença

MIT License

## Suporte

Para suporte, abra uma issue no repositório ou entre em contato com a equipe de desenvolvimento.
