# WhatsUp Gold OTLP Exporter

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenTelemetry](https://img.shields.io/badge/OpenTelemetry-enabled-green.svg)](https://opentelemetry.io/)

Um exporter Python que coleta métricas do **WhatsUp Gold** via REST API e as exporta em formato **OTLP (OpenTelemetry Protocol)** para integração nativa com **Grafana Cloud** e outras plataformas de observabilidade.

## 🎯 Visão Geral

Este projeto oferece uma ponte entre o WhatsUp Gold (monitoramento de infraestrutura) e o Grafana Cloud (observabilidade moderna), permitindo:

- ✅ Coleta automática de métricas do WhatsUp Gold
- ✅ Exportação em formato OTLP (gRPC e HTTP)
- ✅ Integração nativa com Grafana Cloud
- ✅ Batching automático de métricas
- ✅ Gerenciamento inteligente de tokens
- ✅ Logging detalhado e tratamento de erros
- ✅ Deployment em Docker/Kubernetes

## 📊 Comparação: OTLP vs Prometheus

| Aspecto | wug-exporter (Prometheus) | OTLP Exporter |
| :--- | :--- | :--- |
| **Formato** | Prometheus Text Format | OTLP (gRPC/HTTP) |
| **Integração Grafana Cloud** | Via Remote Write | ✅ Nativa |
| **Performance** | Pull-based | Push-based com batching |
| **Compressão** | Não | ✅ Sim (gRPC) |
| **Latência** | Média | ✅ Baixa |
| **Suporte a Traces** | Não | ✅ Preparado |

## 🚀 Quick Start

### Pré-requisitos

- Python 3.10+
- WhatsUp Gold 2019.1+ com REST API habilitada
- Acesso à Grafana Cloud (ou OpenTelemetry Collector local)

### Instalação

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/wug-otlp-exporter.git
cd wug-otlp-exporter

# Instale as dependências
pip install -r requirements_otlp.txt

# Configure as variáveis de ambiente
cp .env.example .env
# Edite .env com suas credenciais
```

### Configuração

Edite o arquivo `.env`:

```bash
# WhatsUp Gold
WUG_URL=https://seu-wug-server:9644/api/v1
WUG_USERNAME=seu_usuario_api
WUG_PASSWORD=sua_senha_api

# Grafana Cloud
OTLP_ENDPOINT=otlp-gateway-prod-us-central-1.grafana.net:443
OTLP_PROTOCOL=grpc
OTLP_HEADERS=Authorization=Bearer seu_token_grafana
```

### Executar

```bash
# Modo direto
python wug_otlp_exporter.py

# Ou com Docker
docker-compose up -d
```

## 📈 Métricas Exportadas

| Métrica | Tipo | Descrição |
| :--- | :--- | :--- |
| `wug.device.up` | Gauge | Número de dispositivos UP |
| `wug.device.down` | Gauge | Número de dispositivos DOWN |
| `wug.device.maintenance` | Gauge | Dispositivos em manutenção |
| `wug.scrape.duration` | Gauge | Tempo de scrape (segundos) |
| `wug.api.response_time` | Gauge | Tempo de resposta da API (ms) |

## 🐳 Docker

### Build

```bash
docker build -t wug-otlp-exporter:1.0 .
```

### Run

```bash
docker run -d \
  --name wug-exporter \
  --env-file .env \
  -e WUG_URL=https://wug-server:9644/api/v1 \
  -e WUG_USERNAME=admin \
  -e WUG_PASSWORD=password \
  -e OTLP_ENDPOINT=otlp-gateway-prod-us-central-1.grafana.net:443 \
  wug-otlp-exporter:1.0
```

### Docker Compose

```bash
docker-compose up -d
```

## 🔧 Configuração Avançada

### Variáveis de Ambiente

| Variável | Padrão | Descrição |
| :--- | :--- | :--- |
| `WUG_URL` | `https://localhost:9644/api/v1` | URL da API do WhatsUp Gold |
| `WUG_USERNAME` | `admin` | Username para autenticação |
| `WUG_PASSWORD` | `password` | Password para autenticação |
| `OTLP_ENDPOINT` | `localhost:4317` | Endpoint OTLP |
| `OTLP_PROTOCOL` | `grpc` | Protocolo (grpc ou http) |
| `OTLP_HEADERS` | — | Headers customizados (ex: Authorization) |
| `SERVICE_NAME` | `whatsup-gold` | Nome do serviço |
| `SCRAPE_INTERVAL` | `60` | Intervalo entre scrapes (segundos) |
| `VERIFY_SSL` | `true` | Verificar certificado SSL |

### Endpoints OTLP Grafana Cloud

```bash
# US Central
OTLP_ENDPOINT=otlp-gateway-prod-us-central-1.grafana.net:443

# EU West
OTLP_ENDPOINT=otlp-gateway-prod-eu-west-1.grafana.net:443

# US West
OTLP_ENDPOINT=otlp-gateway-prod-us-west-2.grafana.net:443
```

## 📚 Documentação

Veja o [GUIDE.md](./GUIDE.md) para documentação completa incluindo:

- Arquitetura detalhada
- Configuração do Grafana Cloud
- Exemplos de dashboards
- Troubleshooting
- Deployment em Kubernetes
- E muito mais

## 🔍 Troubleshooting

### Conexão recusada

```bash
# Testar conectividade com WhatsUp Gold
curl -k https://seu-wug-server:9644/api/v1/product
```

### Autenticação falhando

```bash
# Testar credenciais
curl -k -X POST \
  https://seu-wug-server:9644/api/v1/token \
  -d "grant_type=password&username=seu_usuario&password=sua_senha"
```

### Métricas não aparecem em Grafana

1. Verifique os logs: `docker logs wug-exporter`
2. Confirme o token OTLP em Grafana Cloud
3. Verifique a conectividade com o endpoint OTLP

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Faça um Fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🔗 Referências

- [OpenTelemetry Documentation](https://opentelemetry.io/)
- [Grafana Cloud OTLP](https://grafana.com/docs/grafana-cloud/send-data/otlp/)
- [WhatsUp Gold REST API](https://docs.ipswitch.com/nm/whatsupgold2019_1/02_Guides/rest_api/)
- [wug-exporter (Prometheus)](https://github.com/amazonsetarrr/wug-exporter)

## 📞 Suporte

Para suporte, abra uma [issue](https://github.com/seu-usuario/wug-otlp-exporter/issues) no repositório.

## 🙏 Agradecimentos

- [amazonsetarrr/wug-exporter](https://github.com/amazonsetarrr/wug-exporter) - Inspiração original
- [OpenTelemetry](https://opentelemetry.io/) - Padrão de observabilidade
- [Grafana Labs](https://grafana.com/) - Plataforma de observabilidade

---

**Desenvolvido com ❤️ para a comunidade de observabilidade**
