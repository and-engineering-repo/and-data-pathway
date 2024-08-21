import json
import logging
import traceback

from typing import Any, Dict
import boto3

msg_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setFormatter(msg_formatter)
console_handler.setLevel(logging.INFO)

logger.addHandler(console_handler)


# Constants
SNS_TOPIC_NAME: str = "FlightNotifications"

sns_client = boto3.client(
    'sns', region_name='eu-west-1',
    endpoint_url='http://host.docker.internal:4566'
)

cloudwatch_client = boto3.client(
    'cloudwatch', region_name='eu-west-1',
    endpoint_url='http://host.docker.internal:4566'
)

logger.debug("SNS client initialized")
topic_arn = f"arn:aws:sns:eu-west-1:000000000000:{SNS_TOPIC_NAME}"


def transform_record(raw_record: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "icao24": raw_record['icao24'],
        "callsign": raw_record['callsign'],
        "origin_country": raw_record['origin_country'],
        "time_position": raw_record['time_position'],
        "longitude": raw_record['longitude'],
        "latitude": raw_record['latitude'],
        "geo_altitude": raw_record['geo_altitude'],
        "baro_altitude": raw_record['baro_altitude'],
        "velocity": raw_record['velocity'],
        "on_ground": raw_record['on_ground']
    }


def publish_message_to_topic(record: Dict[str, Any], msg_key: str):
    sns_client.publish(
        TopicArn=topic_arn, Message=json.dumps(record),
        Subject=f"Notification for {msg_key}"
    )
    logger.debug(f"Published message for {msg_key}")


def publish_metric_to_cloudwatch():
    cloudwatch_client.put_metric_data(
        Namespace='Custom/SNS', MetricData=[
            {
                'MetricName': 'NumberOfMessagesPublished',
                'Dimensions': [
                    {
                        'Name': 'TopicName',
                        'Value': SNS_TOPIC_NAME},
                ],
                'Value': 1,
                'Unit': 'Count'
            },
        ]
    )
    logger.debug(f"Cloudwatch metrics published for {SNS_TOPIC_NAME}")


def lambda_handler(event, context):
    message = event['message']
    msg_key: str = message[5]
    record: Dict[str, Any] = message[6]
    logger.debug(record)

    try:
        # Filter columns
        transformed_record = transform_record(raw_record=record)
        logger.debug(
            f"Raw record {record} transformed into {transformed_record}"
        )

        if (
                transformed_record['geo_altitude'] < 1 or
                transformed_record['on_ground']
        ):
            return {'statusCode': 200, 'body': "Skipping grounded flights"}

        else:
            # Publish to SNS
            publish_message_to_topic(
                msg_key=msg_key, record=transformed_record
            )

            # Update logging & monitoring
            publish_metric_to_cloudwatch()

            return {'statusCode': 200, 'body': "Record published & logged"}
    except Exception as e:
        logger.error(e)
        logger.error("Failed to publish flights data to SNS")
        logger.error(traceback.format_exc())
        return {'statusCode': 500, 'body': str(e)}
