# tests/unit/test_exporter.py

import pytest
import time
from freezegun import freeze_time

from wug_otlp_exporter import WhatsUpGoldOTLPExporter


@pytest.fixture
def exporter(mock_otlp_exporter, mock_meter_provider):
    """Fixture para criar uma instância do exporter com mocks."""
    return WhatsUpGoldOTLPExporter(
        wug_url="https://mock-wug-server:9644/api/v1",
        wug_username="test_user",
        wug_password="test_pass",
        otlp_endpoint="mock-otlp-endpoint:4317",
        scrape_interval=10
    )


class TestExporterInitialization:
    """Testes de inicialização do exporter."""

    def test_wug_url_is_set(self, exporter):
        """Verifica se a URL do WUG é configurada corretamente."""
        assert exporter.wug_url == "https://mock-wug-server:9644/api/v1"

    def test_credentials_are_set(self, exporter):
        """Verifica se as credenciais são configuradas corretamente."""
        assert exporter.wug_username == "test_user"
        assert exporter.wug_password == "test_pass"

    def test_scrape_interval_is_set(self, exporter):
        """Verifica se o intervalo de scrape é configurado corretamente."""
        assert exporter.scrape_interval == 10

    def test_initial_token_state(self, exporter):
        """Verifica o estado inicial do token de acesso."""
        assert exporter.access_token is None
        assert exporter.token_expires == 0

    def test_initial_scrape_data_is_empty(self, exporter):
        """Verifica que os dados iniciais de scrape estão vazios."""
        assert exporter.last_scrape_data == {}

    def test_observable_gauges_are_created(self, exporter, mock_meter_provider):
        """Verifica se os gauges observáveis foram criados."""
        assert mock_meter_provider.create_observable_gauge.call_count == 4


class TestTokenManagement:
    """Testes de gerenciamento de token de acesso."""

    @freeze_time("2026-03-13 12:00:00")
    def test_get_access_token_first_call(self, exporter, mock_wug_api):
        """Testa a obtenção do token na primeira chamada."""
        token = exporter._get_access_token()
        assert token == "mock_token"
        assert exporter.token_expires == time.time() + 3600
        assert mock_wug_api.call_count == 1

    @freeze_time("2026-03-13 12:00:00")
    def test_get_access_token_uses_cache(self, exporter, mock_wug_api):
        """Testa que o token em cache é reutilizado."""
        exporter._get_access_token()
        exporter._get_access_token()
        assert mock_wug_api.call_count == 1

    @freeze_time("2026-03-13 13:00:01")
    def test_get_access_token_renews_when_expired(self, exporter, mock_wug_api):
        """Testa a renovação do token quando expirado."""
        exporter.access_token = "old_token"
        exporter.token_expires = time.time() - 2
        token = exporter._get_access_token()
        assert token == "mock_token"
        assert mock_wug_api.call_count == 1

    def test_get_access_token_raises_on_api_error(self, exporter, requests_mock):
        """Testa que uma exceção é levantada em caso de erro da API."""
        requests_mock.post("https://mock-wug-server:9644/api/v1/token", status_code=401)
        with pytest.raises(Exception):
            exporter._get_access_token()


class TestDeviceCollection:
    """Testes de coleta de dispositivos."""

    def test_get_devices_returns_list(self, exporter, mock_wug_api):
        """Testa que a lista de dispositivos é retornada corretamente."""
        devices = exporter._get_devices()
        assert len(devices) == 4

    def test_get_devices_correct_data(self, exporter, mock_wug_api):
        """Testa que os dados dos dispositivos estão corretos."""
        devices = exporter._get_devices()
        assert devices[0]["name"] == "Device-1"
        assert devices[0]["networkAddress"] == "1.1.1.1"
        assert devices[0]["bestState"] == "Up"

    def test_get_devices_returns_empty_on_error(self, exporter, requests_mock):
        """Testa que uma lista vazia é retornada em caso de erro."""
        requests_mock.post("https://mock-wug-server:9644/api/v1/token", json={"access_token": "t", "expires_in": 3600})
        requests_mock.get("https://mock-wug-server:9644/api/v1/device-groups/0/devices", status_code=500)
        devices = exporter._get_devices()
        assert devices == []


class TestStatusMapping:
    """Testes de mapeamento de status de dispositivos."""

    @pytest.mark.parametrize("status, expected", [
        ("Up", 1),
        ("Down", 0),
        ("Maintenance", 2),
        ("Unknown", -1),
        ("InvalidStatus", -1),
        ("", -1),
    ])
    def test_map_device_status(self, exporter, status, expected):
        """Testa o mapeamento de todos os status conhecidos e desconhecidos."""
        assert exporter._map_device_status(status) == expected


class TestScrapeMetrics:
    """Testes do processo de scrape de métricas."""

    def test_scrape_populates_last_scrape_data(self, exporter, mock_wug_api):
        """Testa que o scrape popula os dados corretamente."""
        exporter.scrape_metrics()
        assert exporter.last_scrape_data["device_up"] == 1
        assert exporter.last_scrape_data["device_down"] == 1
        assert exporter.last_scrape_data["device_maintenance"] == 1
        assert exporter.last_scrape_data["scrape_duration"] > 0

    def test_scrape_no_devices_logs_warning(self, exporter, mock_wug_api, caplog):
        """Testa que um aviso é logado quando não há dispositivos."""
        mock_wug_api.get(
            "https://mock-wug-server:9644/api/v1/device-groups/0/devices",
            json={"data": {"devices": []}},
            status_code=200
        )
        exporter.scrape_metrics()
        assert "Nenhum dispositivo obtido" in caplog.text

    def test_scrape_api_error_logs_error(self, exporter, mock_wug_api, caplog):
        """Testa que um erro é logado em caso de falha na API."""
        mock_wug_api.get(
            "https://mock-wug-server:9644/api/v1/device-groups/0/devices",
            status_code=500,
            reason="Internal Server Error"
        )
        exporter.scrape_metrics()
        assert "Erro ao obter dispositivos" in caplog.text

    def test_scrape_does_not_update_data_on_empty_response(self, exporter, mock_wug_api):
        """Testa que last_scrape_data não é atualizado quando não há dispositivos."""
        exporter.last_scrape_data = {"device_up": 99}
        mock_wug_api.get(
            "https://mock-wug-server:9644/api/v1/device-groups/0/devices",
            json={"data": {"devices": []}},
            status_code=200
        )
        exporter.scrape_metrics()
        # Dados anteriores devem ser preservados
        assert exporter.last_scrape_data.get("device_up") == 99


class TestObservableCallbacks:
    """Testes dos callbacks dos gauges observáveis."""

    def test_device_up_callback(self, exporter):
        """Testa o callback do gauge de dispositivos UP."""
        exporter.last_scrape_data = {"device_up": 5}
        observations = list(exporter._device_up_callback(None))
        assert observations[0].value == 5

    def test_device_down_callback(self, exporter):
        """Testa o callback do gauge de dispositivos DOWN."""
        exporter.last_scrape_data = {"device_down": 3}
        observations = list(exporter._device_down_callback(None))
        assert observations[0].value == 3

    def test_device_maintenance_callback(self, exporter):
        """Testa o callback do gauge de dispositivos em manutenção."""
        exporter.last_scrape_data = {"device_maintenance": 2}
        observations = list(exporter._device_maintenance_callback(None))
        assert observations[0].value == 2

    def test_scrape_duration_callback(self, exporter):
        """Testa o callback do gauge de duração do scrape."""
        exporter.last_scrape_data = {"scrape_duration": 1.23}
        observations = list(exporter._scrape_duration_callback(None))
        assert observations[0].value == pytest.approx(1.23)

    def test_callbacks_return_zero_when_no_data(self, exporter):
        """Testa que os callbacks retornam zero quando não há dados."""
        exporter.last_scrape_data = {}
        assert list(exporter._device_up_callback(None))[0].value == 0
        assert list(exporter._device_down_callback(None))[0].value == 0
        assert list(exporter._device_maintenance_callback(None))[0].value == 0
        assert list(exporter._scrape_duration_callback(None))[0].value == 0
