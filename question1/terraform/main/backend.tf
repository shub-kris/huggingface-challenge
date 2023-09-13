/******************************************
  Remote backend configuration
 *****************************************/

# setup of the backend s3 bucket that will keep the remote state

terraform {
  backend "s3" {
    bucket = "214065848284-terraform"
    key    = "terraform_state"
    region = "eu-north-1"
  }
}
