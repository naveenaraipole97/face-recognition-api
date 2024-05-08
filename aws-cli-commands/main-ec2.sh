{
  "MaxCount": 1,
  "MinCount": 1,
  "ImageId": "ami-0d7a109bf30624c99",
  "InstanceType": "t2.micro",
  "KeyName": "naveena_key_pair",
  "EbsOptimized": false,
  "UserData": "IyEvYmluL2Jhc2gKZG5mIGluc3RhbGwgLXkgZ2l0IHBpcApwaXAzIGluc3RhbGwgdG9yY2ggdG9yY2h2aXNpb24gdG9yY2hhdWRpbyAtLWluZGV4LXVybCBodHRwczovL2Rvd25sb2FkLnB5dG9yY2gub3JnL3dobC9jcHUKcGlwMyBpbnN0YWxsIGJvdG8zCm1rZGlyIC1wIC9hcHAKZ2l0IGNsb25lIGh0dHBzOi8vZ2l0aHViLmNvbS9uYXZlZW5hcmFpcG9sZTk3L2ZhY2VfcmVjb2duaXRpb25fcGFydDIuZ2l0Cg==",
  "NetworkInterfaces": [
    {
      "AssociatePublicIpAddress": true,
      "DeviceIndex": 0,
      "Groups": [
        "sg-088829a8df1318a1d"
      ]
    }
  ],
  "IamInstanceProfile": {
    "Arn": "arn:aws:iam::905418031675:instance-profile/s3_sqs_full_access"
  },
  "MetadataOptions": {
    "HttpTokens": "required",
    "HttpEndpoint": "enabled",
    "HttpPutResponseHopLimit": 2
  },
  "PrivateDnsNameOptions": {
    "HostnameType": "ip-name",
    "EnableResourceNameDnsARecord": true,
    "EnableResourceNameDnsAAAARecord": false
  }
}