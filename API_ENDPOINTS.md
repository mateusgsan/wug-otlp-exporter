# Documentação de Endpoints da API REST do WhatsUp Gold

Este documento detalha os endpoints da API REST do WhatsUp Gold utilizados pelo `wug-otlp-exporter`, com exemplos de request/response e um guia de validação de conectividade.

## Endpoints Utilizados

O exporter utiliza os seguintes endpoints:

| Método | Endpoint | Descrição |
| :--- | :--- | :--- |
| `POST` | `/api/v1/token` | Obter ou renovar um token de acesso OAuth 2.0 |
| `GET` | `/api/v1/device-groups/0/devices` | Obter a lista de todos os dispositivos monitorados |

### 1. Autenticação — Obter Token de Acesso

**Endpoint:** `POST /api/v1/token`

Este endpoint é usado para obter um token de acesso (`access_token`) que autoriza as requisições subsequentes. A autenticação é feita via `grant_type=password`, enviando o usuário e senha do WhatsUp Gold.

#### Exemplo de Requisição (cURL)

```bash
curl -k -X POST \
  https://<seu-servidor-wug>:9644/api/v1/token \
  -d "grant_type=password&username=<seu-usuario>&password=<sua-senha>"
```

#### Exemplo de Resposta (Sucesso)

```json
{
  "access_token": "a1b2c3d4...",
  "token_type": "bearer",
  "expires_in": 86399,
  "refresh_token": "e5f6g7h8..."
}
```

### 2. Coleta de Dados — Obter Lista de Dispositivos

**Endpoint:** `GET /api/v1/device-groups/0/devices`

Este endpoint retorna uma lista de todos os dispositivos monitorados pelo WhatsUp Gold. O `0` no path representa o grupo "My Network", que contém todos os dispositivos.

#### Exemplo de Requisição (cURL)

```bash
curl -k -X GET \
  -H "Authorization: Bearer <seu-access-token>" \
  -H "Accept: application/json" \
  https://<seu-servidor-wug>:9644/api/v1/device-groups/0/devices
```

#### Exemplo de Resposta (Sucesso)

```json
{
  "paging": {
    "size": 2
  },
  "data": {
    "devices": [
      {
        "hostName": "192.168.1.1",
        "networkAddress": "192.168.1.1",
        "bestState": "Up",
        "worstState": "Up",
        "name": "Router Principal",
        "id": "1"
      },
      {
        "hostName": "servidor-web-01",
        "networkAddress": "10.0.0.10",
        "bestState": "Down",
        "worstState": "Down",
        "name": "Servidor Web 01",
        "id": "2"
      }
    ]
  }
}
```

## Guia de Validação de Conectividade

Para validar a conectividade entre o servidor onde o exporter está rodando e a API do WhatsUp Gold, siga os passos abaixo:

1. **Verifique a conectividade de rede:**

   ```bash
   ping <seu-servidor-wug>
   ```

2. **Teste a porta da API (9644):**

   ```bash
   nc -zv <seu-servidor-wug> 9644
   ```

3. **Obtenha um token de acesso:**

   Execute o comando cURL da seção de autenticação e verifique se um `access_token` é retornado.

4. **Liste os dispositivos:**

   Use o token obtido no passo anterior para executar o comando cURL da seção de coleta de dados e verifique se a lista de dispositivos é retornada.

Se todos os passos forem bem-sucedidos, o exporter está pronto para ser configurado e executado.
