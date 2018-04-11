from selenium import webdriver
import os, sys, time, yaml,json, re, shutil, logging
from fabric.api import env, run, settings
#from cases import CONF
#from pages.v41.he_install_gluster_auto import *
from collections import OrderedDict
from utils.helpers import checkpoint
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from ansible.plugins.test.core import success
from utils.helpers import results_logs
#from selenium.webdriver.common.keys import Keys
logging.basicConfig(format ='%(asctime)s: %(levelname)s: %(message)s ', filename='./logs/HE_Cockpit.log', filemode='w', level=logging.INFO)

#handler to write info messages or higher to sys.stderr 
console = logging.StreamHandler()
console.setLevel(logging.INFO)

# set a format which is simpler for console use
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
# tell the handler to use this format
console.setFormatter(formatter)
# add the handler to the root logger
logging.getLogger('').addHandler(console)

#log = logging.getLogger("sherry")


results_logs.logger_name = 'check.log'
#results_logs.get_actual_logger('HE_Deploy')

__all__ = ['CONF']

CONF = list(yaml.load_all(open("./config.yml")))[0]
  
#dict1 = OrderedDict(zip(const.deployment_cases_RHHI, const.deployment_cases_RHHI_id))

host_ip, host_user, host_password, browser, ovirtmgmt_nic, rhvm_fqdn = CONF.get('common').get('host_ip'), CONF.get('common').get('host_user'), CONF.get('common').get('host_password'), CONF.get('common').get('browser'), CONF.get('common').get('ovirtmgmt_nic'), CONF.get('common').get('rhvm_fqdn')

gluster_ip, gluster_storage_path, rhvm_appliance_path, vm_mac, vm_fqdn, vm_ip, vm_user, vm_password, engine_password, auto_answer, he_vm_fqdn, he_vm_domain = CONF.get('hosted_engine').get('gluster_ip'), CONF.get('hosted_engine').get('gluster_storage_path'), CONF.get('hosted_engine').get('rhvm_appliance_path'), CONF.get('hosted_engine').get('he_vm_mac'), CONF.get('hosted_engine').get('he_vm_fqdn'), CONF.get('hosted_engine').get('he_vm_ip'), CONF.get('hosted_engine').get('he_vm_user'), CONF.get('hosted_engine').get('he_vm_password'), CONF.get('hosted_engine').get('engine_password'), CONF.get('hosted_engine').get('auto_answer'), CONF.get('hosted_engine').get('he_vm_fqdn'), CONF.get('hosted_engine').get('he_vm_domain')

gluster_data_node1, gluster_data_node2, gluster_arbiter_node, vmstore_is_arbiter, data_is_arbiter, data_disk_count, device_name_engine, device_name_data, device_name_vmstore, size_of_datastore_lv, size_of_vmstore_lv, gdeploy_conf_file_path, mount_engine_brick, mount_data_brick, mount_vmstore_brick, gluster_vg_name, gluster_pv_name, number_of_Volumes, engine_lv_name, os_variant_rhvh, bad_device_name = CONF.get(
    'gluster_details'
).get('gluster_data_node1'), CONF.get('gluster_details').get('gluster_data_node2'), CONF.get('gluster_details').get(
    'gluster_arbiter_node'), CONF.get('gluster_details').get('vmstore_is_arbiter'), CONF.get('gluster_details').get(
    'data_is_arbiter'), CONF.get('gluster_details').get('data_disk_count'), CONF.get('gluster_details').get(
    'device_name_engine'), CONF.get('gluster_details').get('device_name_data'), CONF.get('gluster_details').get(
    'device_name_vmstore'), CONF.get('gluster_details').get('size_of_datastore_lv'), CONF.get('gluster_details').get(
    'size_of_vmstore_lv'), CONF.get('gluster_details').get('gdeploy_conf_file_path'), CONF.get('gluster_details').get(
    'mount_engine_brick'), CONF.get('gluster_details').get('mount_data_brick'), CONF.get('gluster_details').get(
    'mount_vmstore_brick'), CONF.get('gluster_details').get('gluster_vg_name'), CONF.get('gluster_details').get(
    'gluster_pv_name'), CONF.get('gluster_details').get('number_of_Volumes'), CONF.get('gluster_details').get(
    'engine_lv_name'), CONF.get('gluster_details').get('os_variant_rhvh'), CONF.get('gluster_details').get(
    'bad_device_name')
    


env.host_string = host_user + '@' + rhvm_fqdn
env.password = host_password




def init_browser():
    
    
    if browser == 'firefox':
        driver = webdriver.Firefox()
        return driver
    elif browser == 'chrome':
        driver = webdriver.Chrome()
        return driver
    elif browser == 'chrome-headless':
        
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--allow-insecure-localhost')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--allow-running-insecure-content')
        capabilities = DesiredCapabilities.CHROME.copy()
        capabilities['acceptSslCerts'] = True
        capabilities['acceptInsecureCerts'] = True
        driver = webdriver.Chrome(chrome_options=chrome_options, desired_capabilities=capabilities)
        
        return driver
    elif browser == 'phantom':
        driver = webdriver.PhantomJS()
        driver.set_window_size(1440, 900)
        driver.maximize_window()
        time.sleep(20)
        return driver
    else:
        raise NotImplementedError ("The selected browser is not supported")





 
#@checkpoint(dict1)
def check_requirements():
    """
        Purpose:
            RHHI-121
            Check the package requirements before Deploying Hosted engine are met 
    """
    
    logging.info("Checking that Requirements are met and if not met installing them.")
    
#@checkpoint(dict1)
#def check_cockpitui_should_be_reachable_for_the_user():
def deploy_he_via_cockpit_w_gluster():
    """
        Purpose:
            RHHI-121
            With Gluster already configured use the Standard Configuration to deploy a 
            Hosted Engine
    """
    
 
    host_dict = {'host_ip': host_ip,
                 'host_user': host_user,
                 'host_password': host_password
                 }
    if 'cockpit_port' in host_dict:
        cockpit_port = host_dict['cockpit_port']
    else:
        cockpit_port = "9090"
    root_uri = "https://" + rhvm_fqdn + ":" + cockpit_port
    
    
      
   
    logging.info("Setting browser to %s", browser)
    
    dr = init_browser() 
    dr.maximize_window()
    time.sleep(5)
    dr.root_uri = "https://{}:9090".format(rhvm_fqdn)
    dr.get(root_uri)
    time.sleep(10)
    
   
    
    logging.info("Logging into cockpit...")
    
    dr.find_element_by_id("login-user-input").clear()
    dr.find_element_by_id("login-user-input").send_keys(host_user)
    time.sleep(2)
    dr.find_element_by_id("login-password-input").send_keys(host_password)
    time.sleep(2)
    dr.find_element_by_id("login-button").click()
    time.sleep(4)
    dr.get(root_uri + "/ovirt-dashboard")
    time.sleep(3)
    dr.switch_to_frame("cockpit1:localhost/ovirt-dashboard")
    time.sleep(3)
    dr.find_element_by_xpath("//a[@href='#/he']").click()
    time.sleep(3)
    dr.find_element_by_xpath("//input[@value='regular']").click()
    time.sleep(5)
    logging.info("During customization use CTRL-D to abort...Continue? [Yes]")
    dr.find_element_by_xpath("//button[@class='btn btn-lg btn-primary']").click()
    time.sleep(6)
    dr.get_screenshot_as_file('/home/gkimetto/errrorgk.png')
    dr.find_element_by_xpath("//input[@autocomplete='new-password']").click()
    time.sleep(4)
    dr.find_element_by_xpath("//button[@class='btn btn-default']").click()
    time.sleep(4)
    dr.find_element_by_xpath("//input[@autocomplete='new-password']").clear()
    dr.find_element_by_xpath("//input[@autocomplete='new-password']").send_keys("glusterfs")
    logging.info("Select storage type [ glusterfs ] ")
    time.sleep(4)
    dr.find_element_by_xpath("//button[@class='btn btn-default']").click()
    time.sleep(4)
    dr.find_element_by_xpath("//input[@autocomplete='new-password']").send_keys(host_ip+":/engine")
    logging.info("Specifying shared storage path : [ "+ host_ip + "/engine ]")
    time.sleep(3)
    dr.find_element_by_xpath("//button[@class='btn btn-default']").click()
    time.sleep(5)
    dr.find_element_by_xpath("//input[@autocomplete='new-password']").clear()
    dr.find_element_by_xpath("//input[@autocomplete='new-password']").send_keys("Yes")
    dr.find_element_by_xpath("//button[@class='btn btn-default']").click()
    logging.info("Configure Gluster storage?...[ Yes ]")    
    time.sleep(2)
    dr.find_element_by_xpath("//input[@autocomplete='new-password']").clear()
    dr.find_element_by_xpath("//input[@autocomplete='new-password']").send_keys("No")
    dr.find_element_by_xpath("//button[@class='btn btn-default']").click()
    logging.info("Selecting 'Configure IPtables?...[ No ]")    
    time.sleep(2)
    dr.find_element_by_xpath("//input[@autocomplete='new-password']").clear()
    dr.find_element_by_xpath("//button[@class='btn btn-default']").click()
    logging.info("Provide Gateway details...[default ]")    
    time.sleep(2)
    dr.find_element_by_xpath("//input[@autocomplete='new-password']").clear()
    dr.find_element_by_xpath("//input[@autocomplete='new-password']").send_keys(ovirtmgmt_nic)
    dr.find_element_by_xpath("//button[@class='btn btn-default']").click()
    logging.info("Providing ovirtmgmt bridge NIC details...using [ "+ ovirtmgmt_nic+" ]")    
    time.sleep(5)
    
    dr.find_element_by_xpath("//button[@class='btn btn-default']").click()
    logging.info("Selecting RHV-M Appliance image (OVA) - 4.1.20170328.1.el7ev [4.1.20170328.1.el7ev]")    
    time.sleep(40)
    dr.find_element_by_xpath("//button[@class='btn btn-default']").click()
    logging.info("Selecting VNC console to connect to the VM [VNC]")    
    time.sleep(5)
    dr.find_element_by_xpath("//button[@class='btn btn-default']").click()
    logging.info("Using cloud-init to customize the appliance on the first boot[Yes]")    
    time.sleep(2)
    dr.find_element_by_xpath("//button[@class='btn btn-default']").click()
    logging.info("Generate on-fly a cloud-init ISO image[Generate]")    
    time.sleep(5)
     
    
    dr.find_element_by_xpath("//input[@autocomplete='new-password']").clear()
    dr.find_element_by_xpath("//input[@autocomplete='new-password']").send_keys(he_vm_fqdn)
    dr.find_element_by_xpath("//button[@class='btn btn-default']").click()
    logging.info("Providing FQDN to use for the engine appliance: "+he_vm_fqdn)    
    time.sleep(5)
        
    dr.find_element_by_xpath("//input[@autocomplete='new-password']").clear()
    dr.find_element_by_xpath("//input[@autocomplete='new-password']").send_keys(he_vm_domain)
    dr.find_element_by_xpath("//button[@class='btn btn-default']").click()
    logging.info("Providing domain name to use for the engine appliance: "+ he_vm_domain)    
    time.sleep(4)   
    
    dr.find_element_by_xpath("//button[@class='btn btn-default']").click()
    logging.info("Automatically execute engine-setup on the engine appliance on first boot [Yes]")    
    time.sleep(4)  
      
    dr.find_element_by_xpath("//button[@class='btn btn-default']").click()
    logging.info("Automatically restart the engine VM as a monitored service after engine-setup [Yes]")    
    time.sleep(10)
    
    
    dr.find_element_by_xpath("//input[@autocomplete='new-password']").clear()
    dr.find_element_by_xpath("//input[@autocomplete='new-password']").send_keys(engine_password)
    dr.find_element_by_xpath("//button[@class='btn btn-default']").click()
    logging.info("Enter root password that will be used for the engine appliance: *********")
    time.sleep(10)
    dr.find_element_by_xpath("//input[@autocomplete='new-password']").clear()
    dr.find_element_by_xpath("//input[@autocomplete='new-password']").send_keys(engine_password)
    dr.find_element_by_xpath("//button[@class='btn btn-default']").click()
    logging.info("Confirm root password: *********")
    time.sleep(10)
    
    
    dr.find_element_by_xpath("//button[@class='btn btn-default']").click()
    logging.info("Enter 'root' user ssh public key for engine appliance:[]")
    time.sleep(4)
    dr.find_element_by_xpath("//button[@class='btn btn-default']").click()
    logging.info("Do you want to enable ssh access ?:[ Yes ]")
    time.sleep(4)
    dr.find_element_by_xpath("//button[@class='btn btn-default']").click()
    logging.info("Please specify the size of the VM disk in GB: [58]")
    time.sleep(4)
    
    
    dr.find_element_by_xpath("//button[@class='btn btn-default']").click()
    logging.info("Please specify the memory size of the VM in MB (Defaults to appliance OVF value): [16384]")
    time.sleep(4)
    
    dr.find_element_by_xpath("//button[@class='btn btn-default']").click()
    logging.info("Select CPU type : [ model_Broadwell ]")
    time.sleep(4)
    
    dr.find_element_by_xpath("//button[@class='btn btn-default']").click()
    logging.info("Please specify the number of virtual CPUs: [4]")
    time.sleep(4)
    
    dr.find_element_by_xpath("//input[@autocomplete='new-password']").clear()
    dr.find_element_by_xpath("//input[@autocomplete='new-password']").send_keys(vm_mac)
    dr.find_element_by_xpath("//button[@class='btn btn-default']").click()
    logging.info("specify a unicast MAC address for the VM : [ "+vm_mac+" ]")
    time.sleep(4)
    
    dr.find_element_by_xpath("//button[@class='btn btn-default']").click()
    logging.info("How should the engine VM network be configured (DHCP, Static)[DHCP]")
    time.sleep(4)
    
    
    dr.find_element_by_xpath("//input[@autocomplete='new-password']").clear()
    dr.find_element_by_xpath("//input[@autocomplete='new-password']").send_keys("Yes")
    dr.find_element_by_xpath("//button[@class='btn btn-default']").click()
    logging.info("Add lines for the appliance itself and for this host to /etc/hosts on the engine VM : [ Yes ]")
    time.sleep(4)
    
    dr.find_element_by_xpath("//input[@autocomplete='new-password']").clear()
    dr.find_element_by_xpath("//input[@autocomplete='new-password']").send_keys(vm_password)
    dr.find_element_by_xpath("//button[@class='btn btn-default']").click()
    logging.info("Enter engine admin password: *********")
    time.sleep(4)
    dr.find_element_by_xpath("//input[@autocomplete='new-password']").clear()
    dr.find_element_by_xpath("//input[@autocomplete='new-password']").send_keys(vm_password)
    dr.find_element_by_xpath("//button[@class='btn btn-default']").click()
    logging.info("Confirm engine admin password: *********")
    time.sleep(4)
    dr.find_element_by_xpath("//button[@class='btn btn-default']").click()
    logging.info("Please provide the name of the SMTP server [localhost]")
    time.sleep(4)
    dr.find_element_by_xpath("//button[@class='btn btn-default']").click()
    logging.info("Please provide the TCP port number of the SMTP server [25]")
    time.sleep(4)
    
    dr.find_element_by_xpath("//button[@class='btn btn-default']").click()
    logging.info("Please provide the email address from which notifications will be sent [root@localhost]")
    time.sleep(4)
    
    dr.find_element_by_xpath("//button[@class='btn btn-default']").click()
    logging.info("Please provide a comma-separated list of email addresses which will get notifications [root@localhost]")
    time.sleep(4)
   
   #Wait for Hosted Engine is up Message
   
    
    
    #time.sleep(4000)
    logging.info("Confirm installation settings [Yes]")
    dr.implicitly_wait(2000)
    dr.find_element_by_xpath("//button[@class='btn btn-default']").click()
    
    dr.get(root_uri + "/ovirt-dashboard")
    dr.save_screenshot("/tmp/HostedEngineComplete.png")
    logging.info("Saving screenshot to : /tmp/HostedEngineComplete.png")
   
    #check_sucessful_he_deployment()
    
    dr.quit()

#def check_sucessful_he_deployment(hosted_engine_uri, vm_user, he_vm_password):
def check_sucessful_he_deployment():  
    
    he_drv = init_browser()
    he_drv.get(rhvm_appliance_path)
    time.sleep(15)
   
    
    #Find the "Administration Portal Link" and Click it
    
    he_drv.find_element_by_link_text("Administration Portal").click()
    logging.debug ("Logging into Hosted Engine")
    time.sleep(10)
    logging.info("Logging into Hosted Engine...")
    time.sleep(5)
    #Login
    he_drv.find_element_by_id("username").clear()
    he_drv.find_element_by_id("username").send_keys(vm_user)
    
    time.sleep(5)
    
    he_drv.find_element_by_id("password").clear()
    he_drv.find_element_by_id("password").send_keys(engine_password)
    
    he_drv.find_element_by_xpath("//button[@class='btn btn-primary btn-lg']").click()
    time.sleep(5)
    #if success return success or if fail 
    
    if (he_drv.title!="Red Hat Virtualization Manager Web Administration"):
        logging.info ("Unable to SUCCESSFULLY Login to Hosted Engine.Hosted Engine was NOT Deployed.")
        print ("Hosted Engine was NOT properly Deployed. Unable to Log in")
        he_drv.quit()
        
        
    else:
        logging.info ("Hosted Engine Deployment was Successful.")
        
        he_drv.quit()
        
    
    
def main():
    init_browser()
    check_requirements()
    deploy_he_via_cockpit_w_gluster()
    check_sucessful_he_deployment()
 
    
if __name__ == '__main__':
    main()    
    