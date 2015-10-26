import os
import time
import sys
from random import randrange
from novaclient.client import Client
import paramiko


img_name = 'MOLNS_OpenStack_accpro4_1444644885'
"""
PRIV_KEY_PATH = '/Users/adamruul/datormoln/cloud.key'
PUB_KEY_PATH = '/Users/adamruul/datormoln/cloud.key.pub'
"""
PRIV_KEY_PATH = os.environ['PRIV_KEY']
PUB_KEY_PATH = os.environ['PUB_KEY']
if len(sys.argv) < 1:
    print "*** ERROR: wrong input!!!!!!!!!! ***"
    print "Usage:"
    print "python cw2.py <openstack_username> <openstack_password> <nr_of_workers>"
    print "EXAMPLE:"
    print "python cw2.py johndoe banana 3"
    sys.exit(0)
else:
    """
    NR_OF_WORKERS = int(sys.argv[3]) + 1
    openstack_pw = sys.argv[2]
    openstack_usrname = sys.argv[1]
    """
    NR_OF_WORKERS = int(os.environ['NR_WORKERS']) + 1
    openstack_usrname = os.environ['OS_USERNAME']
    openstack_pw = os.environ['OS_PASSWORD']
    print(chr(27) + "[2J")
    print "*** Creation Initiated ***"
    
def shell_escape(arg):
    return "'%s'" % (arg.replace(r"'", r"'\''"), )

def attach_ip(cli,ins):
    iplist = cli.floating_ips.list()
    for ip_obj in iplist:
        if ((getattr(ip_obj,'instance_id')) == None):
            floating_ip = getattr(ip_obj, 'ip')
            break
    else:
        new_ip = cli.floating_ips.create(getattr(cli.floating_ip_pools.list()[0],'name'))
        print "Created IP: " +str(new_ip)
        floating_ip = getattr(new_ip, 'ip')
    try:
        ins.add_floating_ip(floating_ip)
        return floating_ip
    except Exception as e:
        print "XXXXXXXXXX Failed to attach ip! XXXXXXXXXXX"



def start_workers(bro_ip,ip_list):
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
                #cmd = "cd /home/ubuntu/tweet_ass/task2/;python set_connection.py " + str(bro_ip)+" "+str(sys.argv[1]) + " brokerzon"
            worker_name = "brokerzon"
            cmd = "cd /home/ubuntu/ACC_Project/;python parse_file.py " + str(bro_ip)+" "+str(openstack_pw)+ " "+str(worker_name)+" "+str(openstack_usrname)
            
            
        else:
            worker_name = "workerzon"+str(x)
            cmd = "cd /home/ubuntu/ACC_Project/;python parse_file.py " + str(bro_ip)+" "+str(openstack_pw)+ " "+str(worker_name)+" "+str(openstack_usrname)+";celery worker -l info -A worker_tasks"
                #cmd = "cd /home/ubuntu/tweet_ass/task2/;python set_connection.py " + str(bro_ip)+" "+str(sys.argv[1])+ " "+str(worker_name)+";celery worker -l info -A remote"
            x+=1
        try:
            
            ssh.connect(str(ip), username='ubuntu', pkey=sshkey)
            print "*** SSH Connection Established to: "+str(ip)+" ***"
            #print "Running command: "+cmd
            print "*** Running command: "+cmd+" ***"
            stdin,stdout,stderr = ssh.exec_command(cmd)
            #print "Worker Started!"
            #type(stdin)
        except Exception as e:
            print e
        print "*** Closing Connection ***"
        print "******************************************************"
        ssh.close()
    return ip_aux

        
def start_broker(bro_ip):
    #cmd = "cd /home/ubuntu/tweet_ass/task2/;celery flower -A remote --address=0.0.0.0 --port=5000"
    
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


    

config = {'username':os.environ['OS_USERNAME'], 
          'api_key':os.environ['OS_PASSWORD'],
          'project_id':os.environ['OS_TENANT_NAME'],
          'auth_url':os.environ['OS_AUTH_URL'],
           }

nc = Client('2',**config)

# Set parameters
if not nc.keypairs.findall(name="l3_key_r"):
    with open(os.path.expanduser(PUB_KEY_PATH)) as fpubkey:
        nc.keypairs.create(name="l3_key_r", public_key=fpubkey.read())
image = nc.images.find(name=img_name) # RuulSnap is also good
flavor = nc.flavors.find(name="m1.medium")



# Create instance
with open('broker/userdata.yml', 'r') as userdata:
    instance = nc.servers.create(name="Adamzon-Broker", image=image, flavor=flavor, key_name="l3_key_r",userdata=userdata)
status = instance.status
while status == 'BUILD':
    time.sleep(3)
    instance = nc.servers.get(instance.id)
    status = instance.status
print "\n*** Adamzon-Broker is now: %s ***" % status

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

worker_names = []

#with open('userdata.yml', 'r') as userdata:
    # SET TO NUMBER OF WORKERS
wimage = nc.images.find(name=img_name)
for x in range (0,NR_OF_WORKERS):
    worker_name = "Adamzon-Worker-"+str(x)
    worker_names.append(worker_name)
    with open('userdata.yml', 'r') as udata:
        instance = nc.servers.create(name=worker_name, image=wimage, flavor=flavor, key_name="l3_key_r", userdata=udata)
    status = instance.status
    while status == 'BUILD':
        time.sleep(5)
        instance = nc.servers.get(instance.id)
        status = instance.status
    if worker_name != "Adamzon-Worker-0":
        print "*** " +worker_name+ " is now running  ***"


# Assign Floating IP
ins = nc.servers.find(name='Adamzon-Broker')
iip = attach_ip(nc,ins)

print "Adamzon-Broker IP:\t "+ str(iip)

ip_details = []
wips = []
wips.append(str(iip))
for wname in worker_names:
    ins = nc.servers.find(name=wname)
    ipp = attach_ip(nc,ins)
    wips.append(str(ipp))
    if wname != "Adamzon-Worker-0":
        ip_details.append((wname,ipp))
    else:
        serverlist = nc.servers.list()
        for server in serverlist:
            if server.name == 'Adamzon-Worker-0':
                server.delete()
                #print "Deleted aux-worker!!!!!"
                wips.remove(str(ipp))
            else:
                pass
    if wname != "Adamzon-Worker-0":
        print wname + " IP:\t"+ str(ipp)


print "*** installing packages... ***"
wait_time = 290
for i in range(0,29):
    time.sleep(10)
    wait_time -= 10
    print str(wait_time)+"s remaining..."
print "*** Packages Installed!!! ***"


    
new_ip_list = start_workers(str(iip),wips)
start_broker(str(iip))

print "================ DETAILS ======================================"
print "Adamzon-Broker:\t\t"+str(iip)
for (n,i) in ip_details:
    print n + ":\t"+ str(i)
print "\nFlower dashboard available at: \thttp://" + str(iip) + ":5001"
print "\nWeb-UI available at: \thttp://" + str(iip) + ":5000"
print "==============================================================="


