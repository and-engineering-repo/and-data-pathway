# Part-2
In this part of the project we will writing the processing logic which goes into lambda 

- **Exercise-1**: Write the code to filter out grounded flights
- **Exercise-2**: Extend the code to include publishing to SNS topic
- **Exercise-3**: Extend the code to include cloudwatch metric so that we can count number of messages in the topic
- **Exercise-4**: Optimize / Productionize the code (feel free to show off)


## Reference
- [Boto3 SNS](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns.html)
- [Cloudwatch](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudwatch.html)

### How to run the code ?
- Before running the python code ensure docker is running and all the services are up
    ```shell
      make run # will start all the services needed to complete this exercises 
    ```
  
- Before running the code ensure SNS topic is deployed in AWS/localstack
    ```shell
      make create-sns-topic 
    ```
  - Once published, use the following command to check number of messages in topic
    ```shell
      make create-sns-topic 
    ```

### Testing the lambda locally 
Once the logic has been developed, we can test the lambda code locally before deploying.

```python

# ensure you have the code entry point as follows
def lambda_handler(event, context):
    pass


if __name__ == '__main__':
  sample_record = {
    "baro_altitude": 9144,
    "callsign": "SWR3CG  ",
    "category": 0,
    "geo_altitude": 9639.3,
    "icao24": "4b1816",
    "keys": [
        "icao24",
        "callsign",
        "origin_country",
        "time_position",
        "last_contact",
        "longitude",
        "latitude",
        "baro_altitude",
        "on_ground",
        "velocity",
        "true_track",
        "vertical_rate",
        "sensors",
        "geo_altitude",
        "squawk",
        "spi",
        "position_source",
        "category"
    ],
    "last_contact": 1723719351,
    "latitude": 40.7834,
    "longitude": 0.3517,
    "on_ground": False,
    "origin_country": "Switzerland",
    "position_source": 0,
    "sensors": "None",
    "spi": False,
    "squawk": "1053",
    "time_position": 1723719351,
    "true_track": 16.16,
    "velocity": 221.75,
    "vertical_rate": 0.33
}
  msg_key: str = "5741e738-142c-496d-8276-bb4b4f738d08"
  sample_event = {
    'message': [
      None, None, None, None, None, msg_key, sample_record 
    ]
  }
  lambda_handler(event=sample_event, context=None)

# This will allow you to test your logic locally before deploying it into AWS/Localstack
```

### Localstack Networking assumptions

In the code whenever we create BOTO3 objects, like sns client, cloudwatch client

in normal AWS we will create the client like 

```python

sns_client = boto3.client('sns', region_name='eu-west-1')

cloudwatch_client = boto3.client('cloudwatch', region_name='eu-west-1')
```
But since we are using `localstack`, we need to include `endpoint_url='http://localhost:4566'`

This will work for running the code locally, from our machine. But when we deploy it to Localstack
this code will be running in AWS inside docker image so 'localhost' will not be accssible
so to mitigate this before deploying the code we have to create the clients as follows

```python
# All resources in entire project will be deployed into 'eu-west-1'

sns_client = boto3.client(
    'sns', region_name='eu-west-1',
    endpoint_url='http://host.docker.internal:4566'
)

cloudwatch_client = boto3.client(
    'cloudwatch', region_name='eu-west-1',
    endpoint_url='http://host.docker.internal:4566'
)

```


### Deploying the lambda code

- We just need to point the lambda code from provided solution into your code in the Makefile
  - Change
    ```shell
      export LAMBDA_FILE_DIRECTORY ?= ./src/part-2/solution/
      export LAMBDA_FILE_NAME ?= event_processor.py
    ```
    into 
    ```shell
        export LAMBDA_FILE_DIRECTORY ?= ./src/part-2/exercises/
        export LAMBDA_FILE_NAME ?= exercise4.py
        # assuming this is the file that has the finished code
      ```
  
  - Once the change has been made you can simply execute `make deploy-lambda` to deploy the lambda into AWS/localstack.


### Solution 
At any point in time, if you feel stuck, please feel free to refer to the fully finished
solution [event_processor.py](solution/event_processor.py) for reference.