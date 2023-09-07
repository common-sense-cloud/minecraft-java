# Cloudology L2C(loud)L Minecraft Java Edition

## Getting Started:
- Ensure your credentials for terraform are stored in `~/.config/gcloud/tf-sa-creds.json`
- Ensure you have a GCP account with billing enabled and the following APIs enabled:
  - Cloud Functions API
  - Google Compute API
  - Cloud Storage API
- Ensure that under `./functions/start-server/main.py` line 106 under the firewall rule creation, that YOUR IP address is entered instead of mine (unless you want me to join your MC server and cause chaos)
- ~~Any changes made to the JS functions will require you to delete the existing `.zip` file and run `zip <function-name>.zip <function-name>.js package.json ./<function-dir>`~~
  - ~~*note: I know TF has a built in zip tool, however it doesn't play very nice with GCF when you attempt to zip a directory with JavaScript*~~
- Run a `terraform init` in the root directory of the project
- Run `terraform plan` and ensure 10 resources are being created
- Run `terraform apply` and enter `yes` when prompted to build the resources
- Run the add-user function to add your IP address to the firewall rule
  - *note: If you use IPv6 you will need to enter your IPv4 address manually, if you know a solution to this please feel free to open a PR!*
- Open minecraft java and join the LAN server with the GCE VMs public IP address

## Action Items:

- ~~Fix add-user.js function to pull ipv4 address, this may require refactoring to python~~
- Add Firewall rule cleanup step to stop-server function
- ~~Add new VPC network and subnets/firewall rules to terraform code, so it's not running in default network~~
- ~~Convert Functions from JS to Python~~
- Add monitoring/logging
- Set up alerting via grafana
- Figure out SSO auth so firewall rules don't need to be modified
- ~~Add autoshutdown scripts~~
- ~~Add server automated backups~~
- Migrate to K8s/GKE ($$$$)
- Migrate state from local to GCS
- ~~Scale up instance size to 2 vCPU and 8GB memory~~
- ~~Enable soft shutdown of MC server to not lose player inventory~~
- Add github actions workflow to lint, verify and plan/apply Terraform on PR


## Contributing:
I would appreciate if you would open an issue, and if you have a solution, a PR before merging. This way I can discuss it on my live stream, and do a live code review :).

