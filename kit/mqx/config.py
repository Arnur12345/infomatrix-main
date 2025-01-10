import ssl
from dataclasses import dataclass
from urllib.parse import quote

import pika  # type: ignore


@dataclass
class RabbitMQConfig:
    host: str
    username: str
    password: str
    port: int = 5672
    virtual_host: str = "/"
    heartbeat: int = 60  # Default RabbitMQ heartbeat
    connection_timeout: int = 30  # Connection timeout in seconds
    ssl_enabled: bool = True  # Enable SSL/TLS if needed

    def get_amqp_url(self) -> str:
        """Constructs an AMQP URL for aio_pika."""
        scheme = "amqps" if self.ssl_enabled else "amqp"
        credentials = f"{quote(self.username)}:{quote(self.password)}"
        return (
            f"{scheme}://{credentials}@{self.host}:{self.port}/{quote(self.virtual_host)}"
            f"?heartbeat={self.heartbeat}&blocked_connection_timeout={self.connection_timeout}"
        )

    def get_ssl_context(self) -> ssl.SSLContext | None:
        """Returns an SSL context if SSL is enabled, otherwise None."""
        if self.ssl_enabled:
            return ssl.create_default_context()
        return None

    def get_connection_params(self) -> pika.ConnectionParameters:
        """Returns pika connection parameters based on the config."""
        credentials = pika.PlainCredentials(self.username, self.password)
        return pika.ConnectionParameters(
            host=self.host,
            port=self.port,
            virtual_host=self.virtual_host,
            credentials=credentials,
            heartbeat=self.heartbeat,
            connection_attempts=3,
            retry_delay=5,
            blocked_connection_timeout=self.connection_timeout,
            ssl_options=pika.SSLOptions(ssl.create_default_context()),
        )
