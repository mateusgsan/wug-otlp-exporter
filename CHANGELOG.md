# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
e este projeto adere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-03-13

### Added

- Versão inicial do WhatsUp Gold OTLP Exporter
- Suporte para coleta de métricas via REST API do WhatsUp Gold
- Exportação em formato OTLP (gRPC e HTTP)
- Integração nativa com Grafana Cloud
- Batching automático de métricas
- Gerenciamento inteligente de tokens com cache
- Logging detalhado e tratamento de erros robusto
- Suporte para Docker e Docker Compose
- Documentação completa (README, GUIDE, exemplos)
- Arquivo .env.example para configuração
- Dockerfile otimizado para produção
- docker-compose.yml com OpenTelemetry Collector
- Licença MIT
- Arquivo CONTRIBUTING.md

### Métricas Exportadas

- `wug.device.up` - Número de dispositivos UP
- `wug.device.down` - Número de dispositivos DOWN
- `wug.device.maintenance` - Dispositivos em manutenção
- `wug.device.status` - Status individual de dispositivos
- `wug.device.total` - Total de dispositivos
- `wug.alerts.active` - Alertas ativos
- `wug.scrape.duration` - Tempo de scrape
- `wug.api.response_time` - Tempo de resposta da API

### Variáveis de Ambiente Suportadas

- `WUG_URL` - URL da API do WhatsUp Gold
- `WUG_USERNAME` - Username para autenticação
- `WUG_PASSWORD` - Password para autenticação
- `OTLP_ENDPOINT` - Endpoint OTLP
- `OTLP_PROTOCOL` - Protocolo OTLP (grpc ou http)
- `OTLP_HEADERS` - Headers customizados
- `SERVICE_NAME` - Nome do serviço
- `SCRAPE_INTERVAL` - Intervalo entre scrapes
- `VERIFY_SSL` - Verificar certificado SSL

## [Unreleased]

### Planned

- [ ] Suporte a traces (OpenTelemetry Traces)
- [ ] Suporte a logs (OpenTelemetry Logs)
- [ ] Métricas de performance do WhatsUp Gold
- [ ] Integração com alertas do WhatsUp Gold
- [ ] Dashboard pré-configurado para Grafana
- [ ] Suporte a múltiplas instâncias de WhatsUp Gold
- [ ] Health check endpoint
- [ ] Métricas de saúde do exporter
- [ ] Testes unitários
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Publicação em PyPI
- [ ] Helm chart para Kubernetes

---

## Notas de Versão

### v1.0.0

**Primeira versão estável do WhatsUp Gold OTLP Exporter**

Este é o lançamento inicial do projeto, oferecendo uma solução completa para exportar métricas do WhatsUp Gold em formato OTLP para Grafana Cloud.

#### O que está incluído

- ✅ Exporter Python completo
- ✅ Documentação abrangente
- ✅ Exemplos de configuração
- ✅ Suporte Docker/Docker Compose
- ✅ Licença MIT
- ✅ Guia de contribuição

#### Próximas versões

Veja a seção "Planned" acima para funcionalidades planejadas.

---

## Como Reportar Mudanças

Se você é um contribuidor, por favor siga este formato ao adicionar mudanças:

```markdown
### [X.Y.Z] - YYYY-MM-DD

### Added
- Nova feature 1
- Nova feature 2

### Changed
- Mudança 1
- Mudança 2

### Deprecated
- Feature deprecada 1

### Removed
- Feature removida 1

### Fixed
- Bug fix 1
- Bug fix 2

### Security
- Correção de segurança 1
```

Obrigado por contribuir! 🎉
