from botocore.exceptions import ClientError
from google.cloud import compute_v1
from googleapiclient import discovery
from datetime import datetime

now = datetime.now()
dt_string = now.strftime("%d-%m-%Y-%H%M%S")

instance_name = "mc-server-v1"
fw_name = 'minecraft-fw-rule-{}'.format(dt_string)
project = "terraform-basics-12"
zone = "us-east1-b"

def get_server_ip():
    client = compute_v1.InstancesClient()
    request = compute_v1.GetInstanceRequest(
        instance = instance_name,
        project = project,
        zone = zone
    )
   
    response = client.get(request=request)
    server_ip = response.network_interfaces[0].access_configs[0].nat_i_p
    return server_ip

def insert_fwRule(request):
    client = compute_v1.FirewallsClient()
    caller_ip = ""
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
    try:
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
    except ClientError as e:
        print(e)
        return {
            "statusCode": 400,
            "body": e
        }
    
    return {
        "statusCode": 200,
        "body": "FW added! MC server IP: {}".format(get_server_ip())
    }