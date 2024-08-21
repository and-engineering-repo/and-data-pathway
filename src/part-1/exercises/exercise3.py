from typing import Dict, Any, Optional


def consume():
    """
       * Use code from previous exercise
       * pass every message to `publish_flight_message`
    """
    raise NotImplementedError


def publish_flight_message(
        msg: Dict[str, Any], key: Optional[str] = None
):
    """
        * Publish every message we get into kafka

    :param msg: OpenSky record as Dictionary
    :param key: Optional key for kafka message
    """
    raise NotImplementedError
