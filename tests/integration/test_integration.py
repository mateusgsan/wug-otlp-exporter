
# tests/integration/test_integration.py

import pytest
from unittest.mock import MagicMock

from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import InMemoryMetricReader
from opentelemetry.sdk.resources import Resource

from wug_otlp_exporter import WhatsUpGoldOTLPExporter

@pytest.fixture
def in_memory_exporter():
    """Fixture para criar um exporter OTLP em memória."""
    reader = InMemoryMetricReader()
    provider = MeterProvider(
        resource=Resource.create({"service.name": "test-exporter"}),
        metric_readers=[reader]
    )
    return reader, provider

@pytest.fixture
def integration_exporter(in_memory_exporter, mock_wug_api):
    """Fixture para criar uma instância do exporter para testes de integração."""
    reader, provider = in_memory_exporter
    
    exporter = WhatsUpGoldOTLPExporter(
        wug_url="https://mock-wug-server:9644/api/v1",
        wug_username="test_user",
        wug_password="test_pass",
        scrape_interval=10
    )
    
    # Substituir o meter_provider pelo nosso em memória
    exporter.meter_provider = provider
    exporter.meter = provider.get_meter("wug_otlp_exporter")
    exporter._create_instruments() # Recriar instrumentos com o novo meter
    
    return exporter, reader

def test_integration_scrape_and_export(integration_exporter):
    """Testa o scrape e a exportação de métricas para o exporter em memória."""
    exporter, reader = integration_exporter

    # 1. Executar o scrape para popular os dados
    exporter.scrape_metrics()

    # 2. Forçar a coleta de métricas (isso aciona os callbacks)
    reader.collect()

    # 3. Obter as métricas exportadas
    metric_data = reader.get_metrics_data()
    
    # Verificar se os dados foram coletados
    assert metric_data is not None
    assert len(metric_data.resource_metrics) == 1
    scope_metrics = metric_data.resource_metrics[0].scope_metrics[0]
    assert len(scope_metrics.metrics) > 0

    # Dicionário para facilitar a verificação
    metrics_dict = {m.name: m for m in scope_metrics.metrics}

    # Verificar os valores dos gauges observáveis
    assert "wug.device.up" in metrics_dict
    assert metrics_dict["wug.device.up"].data.data_points[0].value == 1

    assert "wug.device.down" in metrics_dict
    assert metrics_dict["wug.device.down"].data.data_points[0].value == 1

    assert "wug.device.maintenance" in metrics_dict
    assert metrics_dict["wug.device.maintenance"].data.data_points[0].value == 1

    assert "wug.scrape.duration" in metrics_dict
    assert metrics_dict["wug.scrape.duration"].data.data_points[0].value > 0

