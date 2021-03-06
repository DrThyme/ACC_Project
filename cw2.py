import os
import time
import sys
from random import randrange
from novaclient.client import Client
import paramiko
"""

uname = "U_NAME"
broker_ip = "BROOKER_IP_TEMP"
passw = "P_W"
"""

img_name = 'MOLNS_OpenStack_accpro4_1444644885'
PRIV_KEY_PATH = os.environ['PRIV_KEY']
PUB_KEY_PATH = os.environ['PUB_KEY']
KEYPAIR_NAME = os.environ['KP_NAME']

if len(sys.argv) < 1:
    sys.exit(0)
else:
    NR_OF_WORKERS = int(os.environ['NR_WORKERS']) + 1
    openstack_usrname = os.environ['OS_USERNAME']
    openstack_pw = os.environ['OS_PASSWORD']
    print(chr(27) + "[2J")
    print "*** Creation Initiated ***"

def attach_ip(cli,ins):
    """
    Attaches a floating ip to a provided instance. The function will first check
    if there are any unused floating ips available, if not one will be created.
    """
    iplist = cli.floating_ips.list()
    for ip_obj in iplist:
        if ((getattr(ip_obj,'instance_id')) == None):
            floating_ip = getattr(ip_obj, 'ip')
            break
    else:
        new_ip = cli.floating_ips.create(getattr(cli.floating_ip_pools.list()[0],'name'))
        print "Created IP: " +str(new_ip.ip)
        floating_ip = getattr(new_ip, 'ip')
    try:
        ins.add_floating_ip(floating_ip)
        return floating_ip
    except Exception as e:
        print "XXXXXXXXXX Failed to attach ip! XXXXXXXXXXX"


def start_workers(bro_ip,ip_list):
    """
    Starts the parse_file.py application on workers and broker. Also starts the celery workers on each worker instance.
    """
    x = 1
    ip_aux = ip_list
    print "IPS:"
    for i in ip_list:
        print str(i)
    for ip in ip_list:
        print "RUNNING ON IP: " +str(ip)
        
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        sshkey = paramiko.RSAKey.from_private_key_file(PRIV_KEY_PATH)
        if ip == bro_ip:
                
            worker_name = "brokerzon"
            cmd = "cd /home/ubuntu/ACC_Project/;python parse_file.py " + str(bro_ip)+" '"+str(openstack_pw)+"' "+str(worker_name)+" "+str(openstack_usrname)+";python parse_file_2.py "+ str(bro_ip)+" '"+str(openstack_pw)+"' "+str(openstack_usrname)
            
            
        else:
            worker_name = "workerzon"+str(x)
            cmd = "cd /home/ubuntu/ACC_Project/;python parse_file.py " + str(bro_ip)+" '"+str(openstack_pw)+"' "+str(worker_name)+" "+str(openstack_usrname)+";cd /home/ubuntu/ACC_Project/;export LC_ALL='en_US.utf-8';celery worker -l info --concurrency=1 -A worker_tasks &"
            
            x+=1
        try:
            
            ssh.connect(str(ip), username='ubuntu', pkey=sshkey)
            print "*** SSH Connection Established to: "+str(ip)+" ***"
            
            print "*** Running command: "+cmd+" ***"
            stdin,stdout,stderr = ssh.exec_command(cmd)
            
            
        except Exception as e:
            print e
        print "*** Closing Connection ***"
        print "******************************************************"
        ssh.close()
    return ip_aux

        
def start_broker(bro_ip):
    """
    Starts the utils.py script on the broker, which allows the broker to run the entire application.
    """
    
    
    cmd = "cd /home/ubuntu/ACC_Project/;celery flower -A worker_tasks --address=0.0.0.0 --port=5001"
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    sshkey = paramiko.RSAKey.from_private_key_file(PRIV_KEY_PATH)
    try:
        ssh.connect(str(bro_ip), username='ubuntu', pkey=sshkey)
        print "*** SSH Connection Established to: "+str(bro_ip)+" ***"
        print "*** Running command: "+cmd+" ***"
        stdin,stdout,stderr = ssh.exec_command(cmd)
    except Exception as e:
        print e
    ssh.close()
    cmd2 = "cd /home/ubuntu/ACC_Project/;python utils.py"
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    sshkey = paramiko.RSAKey.from_private_key_file(PRIV_KEY_PATH)
    try:
        ssh.connect(str(bro_ip), username='ubuntu', pkey=sshkey)
        print "*** SSH Connection Established to: "+str(bro_ip)+" ***"
        print "*** Running command: "+cmd2+" ***"
        stdin,stdout,stderr = ssh.exec_command(cmd2)
    except Exception as e:
        print e

## CREATED BY Brian Khuu
## MODIFIED BY Tim Josefsson
## update_pddrogress() : Displays or updates a console progress bar
## Accepts a float between 0 and 1. Any int will be converted to a float.
## A value under 0 represents a 'halt'.
## A value at 1 or bigger represents 100%
def update_progress(progress):
    """
    Creates and updates a progress bar.
    """
    barLength = 10 # Modify this to change the length of the progress bar
    status = ""
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        status = "error: progress var must be float\r\n"
    if progress < 0:
        progress = 0
        status = "Halt...\r\n"
    if progress >= 1:
        progress = 1
        status = "Done...\r\n"
    block = int(round(barLength*progress))
    text = "\r*** Percent: [{0}] {1}% {2} ***".format( "#"*block + "-"*(barLength-block), progress*100, status)
    sys.stdout.write(text)
    sys.stdout.flush()

############################
#### Main functionality #### 
############################

config = {'username':os.environ['OS_USERNAME'], 
          'api_key':os.environ['OS_PASSWORD'],
          'project_id':os.environ['OS_TENANT_NAME'],
          'auth_url':os.environ['OS_AUTH_URL'],
           }

nc = Client('2',**config)

# Set the parameters for the instance, if key pair does not exist
# create the key pair using the provided keys. 
if not nc.keypairs.findall(name="l3_key_r"):
    with open(os.path.expanduser(PUB_KEY_PATH)) as fpubkey:
        nc.keypairs.create(name="l3_key_r", public_key=fpubkey.read())
image = nc.images.find(name=img_name)
flavor = nc.flavors.find(name="m1.medium")



# Create instance, utilizing the provided cloud init file.
with open('broker/userdata.yml', 'r') as userdata:
    instance = nc.servers.create(name="Group1-Broker", image=image, flavor=flavor, key_name="l3_key_r",userdata=userdata)
status = instance.status
while status == 'BUILD':
    time.sleep(3)
    instance = nc.servers.get(instance.id)
    status = instance.status
print "\n*** Group1-Broker is now: %s ***" % status


# Configure security group. Opening neccessary ports.
secgroup = nc.security_groups.find(name="default")

try:
    nc.security_group_rules.create(secgroup.id,
                               ip_protocol="tcp",
                               from_port=5672,
                               to_port=5672)
except Exception as e:
    pass



try:
    nc.security_group_rules.create(secgroup.id,
                               ip_protocol="tcp",
                               from_port=5001,
                               to_port=5001)
except Exception as e:
    pass


try:
    nc.security_group_rules.create(secgroup.id,
                               ip_protocol="tcp",
                               from_port=22,
                               to_port=22)
except Exception as e:
    pass


try:
    nc.security_group_rules.create(secgroup.id,
                               ip_protocol="tcp",
                               from_port=15672,
                               to_port=15672)
except Exception as e:
    pass


# Start a number of workers as specified by the user.
worker_names = []
wimage = nc.images.find(name=img_name)
for x in range (0,NR_OF_WORKERS):
    worker_name = "Group1-Worker-"+str(x)
    worker_names.append(worker_name)
    with open('userdata.yml', 'r') as udata:
        instance = nc.servers.create(name=worker_name, image=wimage, flavor=flavor, key_name="l3_key_r", userdata=udata)
    status = instance.status
    while status == 'BUILD':
        time.sleep(5)
        instance = nc.servers.get(instance.id)
        status = instance.status
    if worker_name != "Group1-Worker-0":
        print "*** " +worker_name+ " is now running  ***"


# Assign Floating IP to Broker and workers.
ins = nc.servers.find(name='Group1-Broker')
iip = attach_ip(nc,ins)

print "Group1-Broker IP:\t "+ str(iip)

ip_details = []
wips = []
wips.append(str(iip))
for wname in worker_names:
    ins = nc.servers.find(name=wname)
    ipp = attach_ip(nc,ins)
    wips.append(str(ipp))
    if wname != "Group1-Worker-0":
        ip_details.append((wname,ipp))
    else:
        serverlist = nc.servers.list()
        for server in serverlist:
            if server.name == 'Group1-Worker-0':
                server.delete()
                wips.remove(str(ipp))
            else:
                pass
    if wname != "Group1-Worker-0":
        print wname + " IP:\t"+ str(ipp)


# Wait for all instances to successfully install all the packages in cloud init file.
print "*** Installing Packages... ***"
print "*** Estimated time: 300s   ***"
for i in range(100):
	time.sleep(3)
	x = i/100.0
	update_progress(x)
print "\n*** Packages Installed!!! ***"



new_ip_list = start_workers(str(iip),wips)
start_broker(str(iip))

for (n,i) in ip_details:
    s = nc.servers.find(name=n)
    s.pause()


print(chr(27) + "[2J")
print "================ Creation finished! ==========================="
print "Group1-Broker:\t\t"+str(iip)
for (n,i) in ip_details:
    print n + ":\t"+ str(i)
print "\nFlower dashboard available at: \thttp://" + str(iip) + ":5001"
print "\nWeb-UI available at: \thttp://" + str(iip) + ":5000"
print "==============================================================="


