# Part-1
In this part of the project we will be exploring OpenSky API and be publishing the messages to Kafka Topic

- **Exercise-1**: Write the code to Get Familiar with `OpenSky Network API` and play with it and get a sense of our dataset, ratelimits, data schema, etc...
- **Exercise-2**: Extend the code to read data from API continuously
- **Exercise-3**: Extend the code to Publish data into kafka topic
- **Exercise-4**: Optimize / Productionize the code (feel free to show off)


## Reference
- [API Documentation](https://openskynetwork.github.io/opensky-api/index.html)
- [Kafka Producer](https://kafka-python.readthedocs.io/en/master/apidoc/KafkaProducer.html)

### How to run the code ?

- Before running the python code ensure docker is running and all the services are up
    ```shell
      make run # will start all the services needed to complete this exercises
    ```

### Solution
At any point in time, if you feel stuck, please feel free to refer to the fully finished
solution [producer.py](solution/producer.py) for reference.
