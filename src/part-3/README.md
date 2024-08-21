# Part-3
In this part of the project we will be setting up the pipeline which connects the Kafka & the lambda.

- **Exercise-1**: Write Kafka consumer to consume all the messages from the topic
- **Exercise-2**: Extend the code to call lambda with every message we get using boto3 and print the results back from lambda
- **Exercise-3**: Optimize / Productionize the code (feel free to show off)


## Reference
- [Lambda boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda.html)
- [Kafka Consumer](https://kafka-python.readthedocs.io/en/master/apidoc/KafkaConsumer.html)

### How to run the code ?

- Before running the python code ensure docker is running and all the services are up
    ```shell
      make run # will start all the services needed to complete this exercises
    ```

### Solution
At any point in time, if you feel stuck, please feel free to refer to the fully finished
solution [trigger_lambda.py](solution/trigger_lambda.py) for reference.
