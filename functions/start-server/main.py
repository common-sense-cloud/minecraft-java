from botocore.exceptions import ClientError
from google.cloud import compute_v1
from googleapiclient import discovery
from datetime import datetime
import time

now = datetime.now()
dt_string = now.strftime("%d-%m-%Y-%H%M%S")

instance_name = "mc-server-v1"
fw_name = 'minecraft-fw-rule-{}'.format(dt_string)
project = "terraform-basics-12"
zone = "us-east1-b"

def get_server_ip():
  try:  
    client = compute_v1.InstancesClient()
    request = compute_v1.GetInstanceRequest(
        instance = instance_name,
        project = project,
        zone = zone
    )
   
    response = client.get(request=request)
    print(response)
    server_ip = response.network_interfaces[0].access_configs[0].nat_i_p
    return server_ip
  except ClientError as e:
    print(e)
    return {
        "statusCode": 400,
        "body": e
    }

def check_server_readiness():
    server_ip = get_server_ip()
    ready = not server_ip
    return ready

def sleep(seconds):
    time.sleep(seconds)
    
def start_instance(self):
    print("checking server status...")
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
            server_ip = get_server_ip()
            print("server is already running!")
            return {
                "statusCode": 200,
                "body": "Server is already running at: {}".format(server_ip)
            }
    except ClientError as e:
        print(e)
        return {
            "statusCode": 400,
            "body": e
        }   
        
    try:
        print("About to start VM!")
        client = compute_v1.InstancesClient()
        
        request = compute_v1.StartInstanceRequest(
        instance=instance_name,
        project=project,
        zone=zone,
        )
        
        response = client.start(request=request)
        print("starting server...")
        while not check_server_readiness():
            print("server not ready, waiting 1 second")
            sleep(1)
            print("checking server readiness again...")
        print("Server is ready!")
        
    except ClientError as e:
        print(e)
        return {
            "statusCode": 400,
            "body": e
        }        
        
    try: 
        server_ip = get_server_ip()
        
        caller_ip = None
        if request.environ.get("HTTP_X_FORWARDED_FOR") is None:
          caller_ip = request.environ["REMOTE_ADDR"]
        else:
            caller_ip = request.environ['HTTP_X_FORWARDED_FOR']
        print(caller_ip)
        
        firewall_body = {
        "source_ranges": ["{}/32".format(caller_ip)],
        "direction": "INGRESS",
        "name": fw_name,
        "network": "projects/terraform-basics-12/global/networks/mc-network",
        "target_tags": ["minecraft-server"],
        "allowed": [
            {
                "I_p_protocol": "tcp",
                "ports": ["25565"]
                }
            ],
        
        }
        if ":" in caller_ip:
            return {
                "statusCode": 400,
                "body": "You are using IPv6 Protocol, this function only supports IPv4 :(. DM admin to be added to server."
            }
        request = compute_v1.InsertFirewallRequest(
            project=project,
            firewall_resource = firewall_body,
        )
        
        response = client.insert(request=request)
        print(response)
        
        return {
        "statusCode": 200,
        "body": "Minecraft Server Started! You are now spending REAL MONEY! <br />The IP address of the Minecraft server is: {}:25565<br />Your IP address is {}<br />A Firewall rule named {} has been created for you.".format(server_ip, caller_ip, fw_name)
        }
    except ClientError as e:
        print(e)
        return {
            "statusCode": 400,
            "body": e
        }