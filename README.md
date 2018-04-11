# CSS_Cockpit_HE

Project to automate the install process for Hosted Engine install 

Running Deployment Cases - Selenium + Python

This document describes about how to run deployment cases for RHHI using selenium & python.

# Prerequisites : 

Make sure that you have all the three host installed with latest RHV-H ISO , able to access at 
least front end network ips of the system and no vgs present on the system .

Clone the repo by running the command ‘git clone https://github.com/kimettog/CSS_Cockpit_HE.git’

Once clone is done run the command ‘cd CSS_Cockpit_HE’

Run the command ‘pip install -r requirements’ which will install all the requirements.

Install selenium by running the command ‘pip install selenium’
Install pages by running the command ‘pip install pages’
Install fabric by running the command ‘pip install fabric’
Install vncdotool by running the command ‘pip install vncdotool’
Install simplejson by running the command ‘pip install simplejson’
Install service_identity by running the command ‘pip install service_identity’
Install opentype by running the command ‘pip install opentype’
Upgrade pyasn1-modules by running the command ‘pip install --upgrade pyasn1-modules’

Copy geckodriver from http://rhsqe-repo.lab.eng.blr.redhat.com/sosreports/hcautomationscripts/geckodriver and put it in /usr/local/bin/ directory

Edit config.yml file and change the values below as :
 rhn_user as ‘knarra_grafton_pod’ 
rhn_password as ‘graftonqa’
host_ip as first host 1G network ip, host2_ip as second host 1G network ip, host3_ip as third host 1G network ip
rhvm_fqdn as first host fqdn
test_build as rhvh build which you are testing
rhvm_appliance_path as latest rhvm_appliance_path (copy latest appliance to rhsqe-repo.lab.eng.blr.redhat.com/rhvmappliance and specify that path)
gluster_ip as first nodes gluster network address
he_vm_mac as mac address of HE vm
he_vm_fqdn as fqdn of HE VM
he_vm_ip as ip of HE VM
he_vm_password and engine_password 
Specify all the gluster_details 

 Now run gluster tests by running the command ‘python setup_he.py’
