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
from typing import Dict, List, Optional, Iterable
from datetime import datetime
import requests
from requests.auth import HTTPBasicAuth

from opentelemetry import metrics
from opentelemetry.metrics import Observation
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
        self.last_scrape_data = {}

        resource = Resource.create({
            "service.name": service_name,
            "service.version": "1.0.0",
        })

        if otlp_protocol == "grpc":
            otlp_exporter = OTLPMetricExporter(endpoint=otlp_endpoint, insecure=not otlp_endpoint.startswith("https://"))
        else:
            otlp_exporter = OTLPMetricExporterHTTP(endpoint=otlp_endpoint, insecure=not otlp_endpoint.startswith("https://"))

        metric_reader = PeriodicExportingMetricReader(otlp_exporter, export_interval_millis=scrape_interval * 1000)
        self.meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
        metrics.set_meter_provider(self.meter_provider)
        self.meter = metrics.get_meter(name=service_name, version="1.0.0")

        self._create_instruments()

        logger.info(f"WhatsUp Gold OTLP Exporter inicializado")

    def _create_instruments(self):
        """Criar instrumentos de métrica com callbacks."""
        self.meter.create_observable_gauge(
            name="wug.device.up",
            callbacks=[self._device_up_callback],
            description="Número de dispositivos UP",
            unit="1"
        )
        self.meter.create_observable_gauge(
            name="wug.device.down",
            callbacks=[self._device_down_callback],
            description="Número de dispositivos DOWN",
            unit="1"
        )
        self.meter.create_observable_gauge(
            name="wug.device.maintenance",
            callbacks=[self._device_maintenance_callback],
            description="Número de dispositivos em manutenção",
            unit="1"
        )
        self.meter.create_observable_gauge(
            name="wug.scrape.duration",
            callbacks=[self._scrape_duration_callback],
            description="Tempo gasto no scrape da API",
            unit="s"
        )
        logger.info("Instrumentos de métrica criados")

    def _device_up_callback(self, options) -> Iterable[Observation]:
        yield Observation(self.last_scrape_data.get("device_up", 0))

    def _device_down_callback(self, options) -> Iterable[Observation]:
        yield Observation(self.last_scrape_data.get("device_down", 0))

    def _device_maintenance_callback(self, options) -> Iterable[Observation]:
        yield Observation(self.last_scrape_data.get("device_maintenance", 0))

    def _scrape_duration_callback(self, options) -> Iterable[Observation]:
        yield Observation(self.last_scrape_data.get("scrape_duration", 0))

    def _get_access_token(self) -> str:
        current_time = time.time()
        if self.access_token and current_time < self.token_expires:
            return self.access_token
        try:
            response = requests.post(
                f"{self.wug_url}/token",
                data={"grant_type": "password", "username": self.wug_username, "password": self.wug_password},
                verify=self.verify_ssl, timeout=10
            )
            response.raise_for_status()
            data = response.json()
            self.access_token = data["access_token"]
            self.token_expires = current_time + data.get("expires_in", 86399)
            return self.access_token
        except Exception as e:
            logger.error(f"Erro ao obter token: {e}")
            raise

    def _get_devices(self) -> List[Dict]:
        try:
            token = self._get_access_token()
            headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
            response = requests.get(f"{self.wug_url}/device-groups/0/devices", headers=headers, verify=self.verify_ssl, timeout=30)
            response.raise_for_status()
            return response.json().get("data", {}).get("devices", [])
        except Exception as e:
            logger.error(f"Erro ao obter dispositivos: {e}")
            return []

    def _map_device_status(self, status: str) -> int:
        return {"Up": 1, "Down": 0, "Maintenance": 2, "Unknown": -1}.get(status, -1)

    def scrape_metrics(self):
        logger.info("Iniciando scrape de métricas...")
        start_time = time.time()
        try:
            devices = self._get_devices()
            if not devices:
                logger.warning("Nenhum dispositivo obtido")
                return

            device_up = 0
            device_down = 0
            device_maintenance = 0

            for device in devices:
                status_value = self._map_device_status(device.get("bestState", "Unknown"))
                if status_value == 1:
                    device_up += 1
                elif status_value == 0:
                    device_down += 1
                elif status_value == 2:
                    device_maintenance += 1

            scrape_duration = time.time() - start_time
            self.last_scrape_data = {
                "device_up": device_up,
                "device_down": device_down,
                "device_maintenance": device_maintenance,
                "scrape_duration": scrape_duration
            }
            logger.info(f"Scrape concluído em {scrape_duration:.2f}s")
        except Exception as e:
            logger.error(f"Erro durante scrape: {e}")

    def start(self):
        logger.info("Iniciando exporter...")
        try:
            while True:
                self.scrape_metrics()
                time.sleep(self.scrape_interval)
        except KeyboardInterrupt:
            logger.info("Exporter interrompido")
        finally:
            self.meter_provider.shutdown()
            logger.info("Exporter finalizado")

def main():
    exporter = WhatsUpGoldOTLPExporter(
        wug_url=os.getenv("WUG_URL", "https://localhost:9644/api/v1"),
        wug_username=os.getenv("WUG_USERNAME", "admin"),
        wug_password=os.getenv("WUG_PASSWORD", "password"),
        otlp_endpoint=os.getenv("OTLP_ENDPOINT", "localhost:4317"),
        otlp_protocol=os.getenv("OTLP_PROTOCOL", "grpc"),
        service_name=os.getenv("SERVICE_NAME", "whatsup-gold"),
        verify_ssl=os.getenv("VERIFY_SSL", "true").lower() == "true",
        scrape_interval=int(os.getenv("SCRAPE_INTERVAL", "60"))
    )
    exporter.start()

if __name__ == "__main__":
    main()
