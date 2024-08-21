# in-built
import json
import logging
import traceback
from uuid import uuid4
from time import sleep
from dataclasses import dataclass
from argparse import ArgumentParser
from typing import Any, Dict, Optional, Callable


# 3rd party
from kafka import KafkaProducer
from opensky_api import OpenSkyApi


msg_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setFormatter(msg_formatter)
console_handler.setLevel(logging.INFO)

logger.addHandler(console_handler)


@dataclass(frozen=True, repr=True, unsafe_hash=False)
class ProducerConfig:
    bootstrap_servers: str
    topic_name: str
    ack: str = 'all'
    retries: int = 5
    batch_size: int = 16384
    linger_ms: int = 10
    value_serializer: Callable = lambda v: json.dumps(v).encode()
    key_serializer: Callable = lambda k: k.encode()


class FlightsDataSource:
    def __init__(self, config: ProducerConfig):
        self.producer = KafkaProducer(
            bootstrap_servers=config.bootstrap_servers,
            acks=config.ack,
            retries=config.retries,
            batch_size=config.batch_size,
            linger_ms=config.linger_ms,
            value_serializer=config.value_serializer,
            key_serializer=config.key_serializer

        )
        self.api = OpenSkyApi()
        self.states = self.api.get_states()
        self.topic_name: str = config.topic_name
        self.sleep_secs: int = 3

        logger.info("Initialized states & topics")

    def consume(self):
        for idx, state_obj in enumerate(self.states.states):
            logger.debug(f"Consuming state-{idx+1}")
            state_record: Dict[str, Any] = {
                attr: getattr(state_obj, attr)
                for attr in dir(state_obj)
                if not attr.startswith('__')
            }
            self.publish_flight_message(msg=state_record)
            logger.debug(f"Sleeping for {self.sleep_secs} seconds")
            sleep(self.sleep_secs)

    def publish_flight_message(
            self, msg: Dict[str, Any],  key: Optional[str] = None
    ):
        if key is None:
            key = str(uuid4())

        self.producer.send(self.topic_name, key=key, value=msg)
        logger.debug(f"published {key}")
        self.producer.flush()
        logger.debug(f"producer flushed after {key}")


if __name__ == '__main__':
    try:
        parser = ArgumentParser()
        parser.add_argument(
            '--host', '-H', default='localhost:9092',
            required=False, help="Comma seperated kafka hostnames with port"
        )
        parser.add_argument(
            '--topic', '-t', default='aviation-data',
            required=False, help="Comma seperated kafka hostnames with port"
        )
        args = parser.parse_args()
        kafka_config: ProducerConfig = ProducerConfig(
            bootstrap_servers=args.host, topic_name=args.topic
        )

        logger.info(f"Kafka executed with config {kafka_config}")

        flight_state = FlightsDataSource(config=kafka_config)
        flight_state.consume()
    except Exception as e:
        logger.error("Error running application ")
        logger.critical(e)
        logger.error(traceback.format_exc())
