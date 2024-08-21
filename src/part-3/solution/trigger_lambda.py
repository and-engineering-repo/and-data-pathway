# in-built
import logging
import json
import traceback
from argparse import ArgumentParser
from dataclasses import dataclass
from typing import Callable

# 3rd party
import boto3
from kafka import KafkaConsumer


msg_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setFormatter(msg_formatter)
console_handler.setLevel(logging.INFO)

logger.addHandler(console_handler)


@dataclass(frozen=True, repr=True, unsafe_hash=False)
class ConsumerConfig:
    bootstrap_servers: str
    topic_name: str
    auto_offset_reset: str = 'earliest'
    enable_auto_commit: bool = True
    group_id: str = 'random_consumer_group'
    value_deserializer: Callable = lambda v: json.loads(v.decode('utf-8'))
    key_deserializer: Callable = lambda k: k.decode('utf-8') if k else None


def process_message(config: ConsumerConfig):
    consumer = KafkaConsumer(
        config.topic_name,
        bootstrap_servers=config.bootstrap_servers,
        auto_offset_reset=config.auto_offset_reset,
        group_id=config.group_id,
        enable_auto_commit=config.enable_auto_commit,
        value_deserializer=config.value_deserializer,
        key_deserializer=config.key_deserializer
    )

    logger.debug("Kafka consumer initialized")

    lambda_client = boto3.client(
        'lambda', endpoint_url="http://localhost:4566",
        region_name='eu-west-1'
    )

    logger.debug("Lambda client initialized")
    logger.info("Being Kafka listener...")

    for message in consumer:
        response = lambda_client.invoke(
            FunctionName="TestLambda",
            Payload=json.dumps({'message': message})
        )
        result = response['Payload'].read().decode('utf-8')
        logger.info(result)


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
        kafka_config: ConsumerConfig = ConsumerConfig(
            bootstrap_servers=args.host, topic_name=args.topic
        )

        logger.info(f"Kafka executed with config {kafka_config}")

        process_message(config=kafka_config)

    except Exception as e:
        logger.error("Error running application ")
        logger.critical(e)
        logger.error(traceback.format_exc())
