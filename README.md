# upcloud-deploy-mxv
Scripts for MXvirtual deployment in UpCloud.
# Requirements
* Python 3.6
# Usage
This script automates the process of creating server from custom image, described in https://www.upcloud.com/support/using-your-own-server-image/.<br>
All calls are made using UpCloud API: https://www.upcloud.com/api/.<br><br>
Usage: `python upcloud_mxv_deploy.py --username USERNAME --password SECRET --zone ZONE`<br>
Arguments:
* Required
    * `--username` : UpCloud API username
    * `--password` : UpCloud API password
* Optional
    * `--zone` : Choose zone for deployment. Available choices: **de-fra1, fi-hel1, fi-hel2, nl-ams1, sg-sin1, uk-lon1, us-chi1, us-sjo1**. Default is **fi-hel1**
    * `-h` : Display help message

**Note**: Deployment time greatly varies depending on zone.
