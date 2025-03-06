provider "aws" {
  region = local.region
}

terraform {
  required_version = ">= 1.0"

}