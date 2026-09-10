terraform {
  backend "s3" {
    bucket       = "bookmark-tfstate-424322298651"
    key          = "bookmark/dev/terraform.tfstate"
    region       = "eu-central-1"
    encrypt      = true
    use_lockfile = true
  }
}