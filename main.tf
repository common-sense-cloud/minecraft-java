provider "google" {
  project     = var.project_id
  credentials = file("~/.config/gcloud/tf-sa-creds.json")
  region      = var.region
  zone        = var.zone
}

module "vpc" {
  source  = "terraform-google-modules/network/google"
  version = "~> 7.2"

  project_id              = var.project_id
  network_name            = "mc-network"
  routing_mode            = "GLOBAL"
  auto_create_subnetworks = true

  subnets = [
    {
      subnet_name   = "mc-default-east"
      subnet_region = var.region
      subnet_ip     = "10.62.0.0/20"
    },
  ]
}

data "archive_file" "gcfzip" {
  type        = "zip"
  output_path = "add-user.zip"
  source_dir  = "${path.module}/functions/add-user/"
}

data "archive_file" "gcfzip-start" {
  type        = "zip"
  output_path = "start-server.zip"
  source_dir  = "${path.module}/functions/start-server/"
}

data "archive_file" "gcfzip-stop" {
  type        = "zip"
  output_path = "stop-server.zip"
  source_dir  = "${path.module}/functions/stop-server/"
}

resource "google_compute_address" "static" {
  name = "mc-static-ip"
}

module "mc-server" {
  source          = "./modules/gce-container"
  zone            = var.zone
  project_id      = var.project_id
  image           = "itzg/minecraft-server"
  privileged_mode = true
  activate_tty    = true
  port            = 25565

  env_variables = {
    EULA : "TRUE"
    OPS : "autonomaus"
  }

  instance_name      = "mc-server-v1"
  network_name       = module.vpc.network_name
  subnetwork         = module.vpc.subnets_names[0]
  subnetwork_project = "terraform-basics-12"

  static_ip = google_compute_address.static.address

  depends_on = [module.vpc]
}

module "start-function" {
  source               = "./modules/cloud-function"
  bucket-name          = "${var.project_id}-functions"
  object-name          = "start-server.zip"
  function-path        = data.archive_file.gcfzip-start.output_path
  function-name        = "strt-server"
  function-description = "python function that starts minecraft server"
  entry-point          = "start_instance"
  runtime              = "python39"

}

module "stop-function" {
  source               = "./modules/cloud-function"
  bucket-name          = "${var.project_id}-functions"
  object-name          = "stop-server.zip"
  function-path        = data.archive_file.gcfzip-stop.output_path
  function-name        = "stop-server"
  function-description = "python function that stops minecraft server"
  entry-point          = "stop_instance"
  runtime              = "python39"
}

module "add-function" {
  source               = "./modules/cloud-function"
  bucket-name          = "${var.project_id}-functions"
  object-name          = "add-user.zip"
  function-path        = data.archive_file.gcfzip.output_path
  function-name        = "add-user"
  function-description = "python function that adds a user to minecraft server"
  entry-point          = "insert_fwRule"
  runtime              = "python39"
}