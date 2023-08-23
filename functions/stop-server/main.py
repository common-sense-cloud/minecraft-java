from botocore.exceptions import ClientError
from google.cloud import compute_v1
from googleapiclient import discovery



instance_name = "mc-server-v1"
project = "terraform-basics-12"
zone = "us-east1-b"

def stop_instance():
    print("Checking server status...")
    server_status = None
    try:
        client = compute_v1.InstancesClient()
        request = compute_v1.GetInstanceRequest(
            instance = instance_name,
            zone= zone,
            project= project
        )
        response = client.get(request=request)
        req_array = response
        print(req_array)
        server_status = req_array.status
        if server_status == "RUNNING":
            client = compute_v1.InstancesClient()

            request = compute_v1.StopInstanceRequest(
                instance=instance_name,
                project=project,
                zone=zone,
            )

            response = client.stop(request=request)

            return {
                "statusCode": 200,
                "body": "Server Stopped! Response: {}".format(response)
            }
        else:
            return {
                "statusCode": 200,
                "body": "Server is already stopped!"
            }
    except ClientError as e:
        print(e)
        return {
            "statusCode": 400,
            "body": e
        }   