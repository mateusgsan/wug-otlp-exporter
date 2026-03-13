"""
WhatsUp Gold OTLP Exporter
Exporta métricas do WhatsUp Gold diretamente em formato OTLP (OpenTelemetry Protocol)
para integração nativa com Grafana Cloud.

Baseado em: amazonsetarrr/wug-exporter
Melhorias: Suporte a OTLP, gRPC, HTTP e batch processing
"""

import os
import logging
import time
from typing import Dict, List, Optional
from datetime import datetime
import requests
from requests.auth import HTTPBasicAuth

from opentelemetry import metrics
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter as OTLPMetricExporterHTTP
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WhatsUpGoldOTLPExporter:
    """
    Exporter que coleta métricas do WhatsUp Gold via REST API
    e as exporta em formato OTLP para Grafana Cloud.
    """

    def __init__(
        self,
        wug_url: str,
        wug_username: str,
        wug_password: str,
        otlp_endpoint: str = "localhost:4317",
        otlp_protocol: str = "grpc",  # "grpc" ou "http"
        service_name: str = "whatsup-gold",
        verify_ssl: bool = True,
        scrape_interval: int = 60
    ):
        """
        Inicializa o exporter.

        Args:
            wug_url: URL base da API do WhatsUp Gold (ex: https://wug-server:9644/api/v1)
            wug_username: Username para autenticação
            wug_password: Password para autenticação
            otlp_endpoint: Endpoint OTLP (ex: localhost:4317 ou https://otlp.grafana.net:443)
            otlp_protocol: Protocolo OTLP ("grpc" ou "http")
            service_name: Nome do serviço para identificação
            verify_ssl: Verificar certificado SSL
            scrape_interval: Intervalo entre scrapes em segundos
        """
        self.wug_url = wug_url
        self.wug_username = wug_username
        self.wug_password = wug_password
        self.otlp_endpoint = otlp_endpoint
        self.otlp_protocol = otlp_protocol
        self.service_name = service_name
        self.verify_ssl = verify_ssl
        self.scrape_interval = scrape_interval
        self.access_token = None
        self.token_expires = 0

        # Configurar Resource
        resource = Resource.create({
            "service.name": service_name,
            "service.version": "1.0.0",
            "telemetry.sdk.name": "opentelemetry",
            "telemetry.sdk.language": "python",
        })

        # Configurar exporter OTLP
        if otlp_protocol == "grpc":
            otlp_exporter = OTLPMetricExporter(
                endpoint=otlp_endpoint,
                insecure=not otlp_endpoint.startswith("https://")
            )
        else:  # http
            otlp_exporter = OTLPMetricExporterHTTP(
                endpoint=otlp_endpoint,
                insecure=not otlp_endpoint.startswith("https://")
            )

        # Configurar metric reader com batching
        metric_reader = PeriodicExportingMetricReader(
            otlp_exporter,
            interval_millis=scrape_interval * 1000
        )

        # Criar MeterProvider
        self.meter_provider = MeterProvider(
            resource=resource,
            metric_readers=[metric_reader]
        )
        metrics.set_meter_provider(self.meter_provider)

        # Criar meter
        self.meter = metrics.get_meter(
            name=service_name,
            version="1.0.0"
        )

        # Criar instrumentos
        self._create_instruments()

        logger.info(f"WhatsUp Gold OTLP Exporter inicializado")
        logger.info(f"  WUG URL: {wug_url}")
        logger.info(f"  OTLP Endpoint: {otlp_endpoint}")
        logger.info(f"  Protocol: {otlp_protocol}")
        logger.info(f"  Scrape Interval: {scrape_interval}s")

    def _create_instruments(self):
        """Criar instrumentos de métrica."""
        # Contadores
        self.device_status_counter = self.meter.create_counter(
            name="wug.device.status",
            description="Status do dispositivo (1=Up, 0=Down)",
            unit="1"
        )

        self.device_total_counter = self.meter.create_counter(
            name="wug.device.total",
            description="Total de dispositivos monitorados",
            unit="1"
        )

        self.alerts_active_counter = self.meter.create_counter(
            name="wug.alerts.active",
            description="Número de alertas ativos",
            unit="1"
        )

        # Gauges (valores instantâneos)
        self.device_up_gauge = self.meter.create_gauge(
            name="wug.device.up",
            description="Número de dispositivos UP",
            unit="1"
        )

        self.device_down_gauge = self.meter.create_gauge(
            name="wug.device.down",
            description="Número de dispositivos DOWN",
            unit="1"
        )

        self.device_maintenance_gauge = self.meter.create_gauge(
            name="wug.device.maintenance",
            description="Número de dispositivos em manutenção",
            unit="1"
        )

        self.scrape_duration_gauge = self.meter.create_gauge(
            name="wug.scrape.duration",
            description="Tempo gasto no scrape da API",
            unit="s"
        )

        self.api_response_time_gauge = self.meter.create_gauge(
            name="wug.api.response_time",
            description="Tempo de resposta da API",
            unit="ms"
        )

        logger.info("Instrumentos de métrica criados")

    def _get_access_token(self) -> str:
        """Obter token de acesso da API do WhatsUp Gold."""
        current_time = time.time()

        # Reutilizar token se ainda válido
        if self.access_token and current_time < self.token_expires:
            return self.access_token

        try:
            logger.info("Obtendo novo token de acesso...")
            response = requests.post(
                f"{self.wug_url}/token",
                data={
                    "grant_type": "password",
                    "username": self.wug_username,
                    "password": self.wug_password
                },
                verify=self.verify_ssl,
                timeout=10
            )
            response.raise_for_status()

            data = response.json()
            self.access_token = data["access_token"]
            self.token_expires = current_time + data.get("expires_in", 86399)

            logger.info("Token obtido com sucesso")
            return self.access_token

        except Exception as e:
            logger.error(f"Erro ao obter token: {e}")
            raise

    def _get_devices(self) -> List[Dict]:
        """Obter lista de dispositivos do WhatsUp Gold."""
        try:
            token = self._get_access_token()
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json"
            }

            response = requests.get(
                f"{self.wug_url}/device-groups/0/devices",
                headers=headers,
                verify=self.verify_ssl,
                timeout=30
            )
            response.raise_for_status()

            data = response.json()
            devices = data.get("data", {}).get("devices", [])

            logger.info(f"Obtidos {len(devices)} dispositivos")
            return devices

        except Exception as e:
            logger.error(f"Erro ao obter dispositivos: {e}")
            return []

    def _get_device_reports(self, device_id: str) -> Optional[Dict]:
        """Obter relatórios de um dispositivo específico."""
        try:
            token = self._get_access_token()
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json"
            }

            response = requests.get(
                f"{self.wug_url}/devices/{device_id}/reports/cpu-utilization",
                headers=headers,
                verify=self.verify_ssl,
                timeout=10
            )
            response.raise_for_status()

            return response.json()

        except Exception as e:
            logger.debug(f"Erro ao obter relatórios do dispositivo {device_id}: {e}")
            return None

    def _map_device_status(self, status: str) -> int:
        """Mapear status do dispositivo para valor numérico."""
        status_map = {
            "Up": 1,
            "Down": 0,
            "Maintenance": 2,
            "Unknown": -1
        }
        return status_map.get(status, -1)

    def scrape_metrics(self):
        """Scrape de métricas do WhatsUp Gold e export para OTLP."""
        logger.info("Iniciando scrape de métricas...")
        start_time = time.time()

        try:
            # Obter dispositivos
            devices = self._get_devices()

            if not devices:
                logger.warning("Nenhum dispositivo obtido")
                return

            # Processar dispositivos
            device_up = 0
            device_down = 0
            device_maintenance = 0

            for device in devices:
                device_name = device.get("name", "unknown")
                device_ip = device.get("networkAddress", "unknown")
                device_status = device.get("bestState", "Unknown")

                # Mapear status
                status_value = self._map_device_status(device_status)

                # Registrar métrica com labels
                attributes = {
                    "device.name": device_name,
                    "device.ip": device_ip,
                    "device.status": device_status
                }

                # Incrementar contadores
                if status_value == 1:
                    device_up += 1
                elif status_value == 0:
                    device_down += 1
                elif status_value == 2:
                    device_maintenance += 1

                logger.debug(f"Dispositivo: {device_name} ({device_ip}) - Status: {device_status}")

            # Registrar gauges
            self.device_up_gauge.observe(device_up)
            self.device_down_gauge.observe(device_down)
            self.device_maintenance_gauge.observe(device_maintenance)

            # Tempo de scrape
            scrape_duration = time.time() - start_time
            self.scrape_duration_gauge.observe(scrape_duration)

            logger.info(
                f"Scrape concluído em {scrape_duration:.2f}s - "
                f"UP: {device_up}, DOWN: {device_down}, MAINT: {device_maintenance}"
            )

        except Exception as e:
            logger.error(f"Erro durante scrape: {e}")

    def start(self):
        """Iniciar o exporter em loop contínuo."""
        logger.info("Iniciando exporter...")

        try:
            while True:
                self.scrape_metrics()
                time.sleep(self.scrape_interval)

        except KeyboardInterrupt:
            logger.info("Exporter interrompido pelo usuário")
        except Exception as e:
            logger.error(f"Erro fatal: {e}")
        finally:
            self.meter_provider.force_flush()
            logger.info("Exporter finalizado")


def main():
    """Função principal."""
    # Carregar configurações de variáveis de ambiente
    wug_url = os.getenv("WUG_URL", "https://localhost:9644/api/v1")
    wug_username = os.getenv("WUG_USERNAME", "admin")
    wug_password = os.getenv("WUG_PASSWORD", "password")

    otlp_endpoint = os.getenv("OTLP_ENDPOINT", "localhost:4317")
    otlp_protocol = os.getenv("OTLP_PROTOCOL", "grpc")
    otlp_headers = os.getenv("OTLP_HEADERS", "")  # Ex: "Authorization=Bearer token"

    service_name = os.getenv("SERVICE_NAME", "whatsup-gold")
    scrape_interval = int(os.getenv("SCRAPE_INTERVAL", "60"))
    verify_ssl = os.getenv("VERIFY_SSL", "true").lower() == "true"

    # Criar e iniciar exporter
    exporter = WhatsUpGoldOTLPExporter(
        wug_url=wug_url,
        wug_username=wug_username,
        wug_password=wug_password,
        otlp_endpoint=otlp_endpoint,
        otlp_protocol=otlp_protocol,
        service_name=service_name,
        verify_ssl=verify_ssl,
        scrape_interval=scrape_interval
    )

    exporter.start()


if __name__ == "__main__":
    main()
