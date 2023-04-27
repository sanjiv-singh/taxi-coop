# Taxi Coop - Taxi Aggregator App

## Overview

A taxi aggregator app for enabling customers to find taxis for commute and drivers to reach their customers.

### Backend
The app backend has three  main components as follows:-

* A non relational database for storing details of taxies and users (customers) along with near real time location information for each taxi.
* IoT data processing infrastructure for handling near real time location data being generated by taxis.
* A set of APIs for handling various client requests from taxis and users.

### Frontend
The backend has been designed to support client front ends such as web apps or mobile apps that are completely independent of the backend infrastructure. The taxi clients interact with the backend using a pubsub message broker (MQTT) and the user clients interact using the web APIs.

As the focus of the project lies in backend design and implementation, the frontend functionality are simulated using standalone python applications.

## Infrastructure

The backend of the application is designed to be hosted on AWS Cloud Infrastructure. The following AWS services are being used:-

#### Amazon DocumentDB

The datastore for the application is hosted on Amazon DocumentDB (with MongoDB 4.0 compatibility). The salient aspects are:-

* Fully managed by AWS including instance maintenance, patching, data backups / snapshots.
* Excellent performance due to separation of compute and storage managed by AWS.
* Provisioned in a separate VPC with network isolation for enhanced security.
* Supports queries and aggregations with MongoDB 4.0 compatibility.
* Supports GeoIndexing and location based queries.

Code related to deployment and updation of the database is located in the `taxi-db` folder. It contains the following:-

* `taxidb.yml` - Cloudformation template for provisioning of the DB Cluster and DB instances.
* `taxidb_lambda.py` - Lambda function for ingestion of data into DocumentDB cluster. This lambda function is provisioned in the same VPC as the db cluster to allow access.
* Shell scripts for deployment  of cloudformation template and lambda function.


#### AWS IoT Core

Used for ingestion of taxi data including location updates in near real time. The salient aspects are:-

* Fully managed service
* Can easily scale with increased workloads (hundreds of thousands of taxis)
* Pub/Sub Architecture allows message routing to multiple clients (e.g. multiple taxis receiving user requests)
* X.509 certificate based registration and authentication for each taxi.

Scripts for provisioning of IoT Core infrastructure can be found in the `taxi-iot` folder.

* `setup.sh` - Script for provisiong IoT Thing Group and Type along with IAM role and IoT policy.
* `cleanup.sh` - Script for cleaning up all IoT Core resources including certificates.
* The `setup.sh` script also provisions the Message Routing Rule for routing data to the `taxidb_lambda` function for ingestion into DocumentDB.

#### API Gateway and Lambda Functions

The entire backend API is designed using serverless architecture for cost-effectiveness and ease of post deployment management. The serverless components are deployed using AWS SAM (Serverless Application Model). The various serverless modules are located in the `taxi-api` folder. Their functionalities are as follows:-

* `tc_geocoder` - Uses Google Maps API for conversion of location address to location coordinates (latitude/longitude). This enables the client to specify the destination as address rather than lat long coordinates.
* `tc_directions` - Uses Google Maps API to find driving directions from origin to destination. Returns an array of steps with lat long coordinates. These coordinates are to be used by the taxi client for navigating from origin to destination.
* `tc_change_status` - Updates status of taxi to `AVL`, `NAVL`, `BOOKED` or `TRIP`.
* `tc_request_ride` - Enables the user to request a ride from his/her current location to a destination address or lat long location.
* `tc_accept_ride` - Enables a taxi to respond to a ride request.
* `tc_book` - Enables user to book one of the taxis that have accepted the ride request. Changes the status of taxi from `AVL` to `BOOKED` by calling `tc_change_status` and triggers a drive from current location to user's location.
* `tc_trip_start` - Used by taxi to indicate commencement of trip. Calls `tc_chnage_status` to change status from `BOOKED` to `TRIP`. Triggers a drive from current location to destination.
* `tc_trip_end` - Called by taxi after reaching destination. Triggers `tc_change_status` to 'AVL'. Also updates user's location to current location.

## Setup

The setup process involves the following steps.

1.   Make sure AWS Cli is installed and properly configured (`aws configure`). Also make sure your accound has adequate previleges for provisioning cloud infrastructure.

2.   Install SAM Cli (refer AWS documentation)

3.   Install the following python dependencies:-

```bash
    $ pip3 install boto3
    $ pip3 install AWSIoTPythonSDK
    $ pip3 install awsiotsdk
    $ pip3 install bson
    $ pip3 install aws-sam-cli
```

4.   Change directory to `taxi-db` and run the following commands:-

```bash
    $ cd taxi-db

    $ export DB_USER=<dbuser>

    $ export DB_PASSWORD=<password>

    $ ./create_db.sh
    
    $  ./create_lambda.sh
```
5.    Change directory to `taxi-iot` and run these commands:-

```bash
    $ cd ../taxi-iot

    $ ./setup.sh
```
6.    Change directory to `taxi-api` folder and run this command to deploy the APIs and Lambda functions:-

```bash
    $ cd ..taxi-api
    $ export DB_USER=<dbuser>
    $ export DB_PASSWORD=<password>
    $ ./setup_apis.sh
```

The API end point for TCGetTaxis should be in the output. Copy the URL and open it in browser.

7.    Change directory back to `taxi-iot` and start the taxi simulator

```bash
    $ cd ../taxi-iot
    $ python main.py
```

Now refresh the bowser page opened above and if everything went well, you should see taxi data in JSON format in your browser.


## Cleanup

To clean up the cloud infrastructure, follow these steps:-

1.    In the `taxi-iot` folder run the command. It deletes the thing type,
thing group, IAM roles, custom policies, all things and all certificates
on AWS IoT Core. Finally, it deletes local copies of certificates and
 private keys in the `../simulation/.certs` folder.
```bash
    $ ./cleanup.sh
```

2.    In the taxi-db folder, run the following commands:-

```bash
    $ cd ../taxi-db
    $ ./delete.sh
```

3.    In the `taxi-api` folder, run the following command:-

```bash
    $ cd ../taxi-api
    $ sam delete
```

## Credits

Sanjiv Singh

Sesha Reddy Koilkonda

Kishore Kaluri

The project was undertaken as part of course on Software Engineering for Cloud Computing, IoI and Blockchain by Great Learning in collaboration with Indian Institute of Technology, Madras

