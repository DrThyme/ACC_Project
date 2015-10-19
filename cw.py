import os
import time
import sys
from random import randrange
from novaclient.client import Client
import paramiko


"""
TODO:
* vettiga tasks i add_tasks
* paramiko -> starta workers med celery-cmd
* flask api/hemsida
* fixa flower


USAGE:
python create_workers <password>
ssh to broker -> python create_tasks
check flower


FILES CONNECTED:
create_workers.py(L) -> set_connections.py -> w_remote.py -> create_tasks.py -> userdata.yml(L) -> broker/userdata.yml(L) -> ACC... (L) -> 


TIMES:
1 workers: 
2 workers: Finished after: 222.639057875s
3 workers: Finished after: 188.239850998s
4 workers: Finished after: 173.42562604s
5 workers: 
6 workers: Finished after: 145.900032997s
7 workers:
8 workers:
"""




"""

my_str = 

string=sed -e '$!d' /var/log/cloud-init-output.log; if [[ $string == *"My long"* ]]; then echo "It's there!"; fi



"""

img_name = 'Ubuntu Server 14.04 LTS (Trusty Tahr)'
openstack_pw = sys.argv[2]
openstack_usrname = sys.argv[1]
NR_OF_WORKERS = 2
if len(sys.argv) < 2:
    print "Please provide a password!!!!!!!!!! python create_workers <password>"
    sys.exit(0)
else:
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
    try:
        ins.add_floating_ip(floating_ip)
        return floating_ip
    except Exception as e:
        print "XXXXXXXXXX Failed to attach ip! XXXXXXXXXXX"



def start_workers(bro_ip,ip_list):
    x = 0
    for ip in ip_list:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        sshkey = paramiko.RSAKey.from_private_key_file('/Users/adamruul/datormoln/cloud.key')
        try:
            if ip == bro_ip:
                cmd = "cd /home/ubuntu/ACC_Project;python parse_file.py " + str(bro_ip)+" "+str(openstack_pw) + " brokerzon "+str(openstack_usrname)
            else:
                worker_name = "workerzon"+str(x)
                cmd = "cd /home/ubuntu/ACC_Peoject/;python parse_file.py " + str(bro_ip)+" "+str(openstack_pw)+ " "+str(worker_name)+" "+str(openstack_usrname)+";celery worker -l info -A worker_tasks"
                x+=1
            ssh.connect(str(ip), username='ubuntu', pkey=sshkey)
            print "*** SSH Connection Established ***"
            #print "Running command: "+cmd
            stdin,stdout,stderr = ssh.exec_command(cmd)
            #print "Worker Started!"
            #type(stdin)
        except Exception as e:
            print e
        print "*** Closing Connection ***"
        ssh.close()

        
def start_broker(bro_ip):
    cmd = "cd /home/ubuntu/ACC_Project/;celery flower -A worker_tasks --address=0.0.0.0 --port=5000"
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    sshkey = paramiko.RSAKey.from_private_key_file('/Users/adamruul/datormoln/cloud.key')
    try:
        ssh.connect(str(bro_ip), username='ubuntu', pkey=sshkey)
        print "*** SSH Connection Established ***"
        print "*** Running command: "+cmd+" ***"
        stdin,stdout,stderr = ssh.exec_command(cmd)
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
    with open(os.path.expanduser('/Users/adamruul/datormoln/cloud.key.pub')) as fpubkey:
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
udata = open('userdata.yml', 'r')
#with open('userdata.yml', 'r') as userdata:
    # SET TO NUMBER OF WORKERS
wimage = nc.images.find(name=img_name)
for x in range (0,NR_OF_WORKERS):
    worker_name = "Adamzon-Worker-"+str(x)
    worker_names.append(worker_name)
    instance = nc.servers.create(name=worker_name, image=wimage, flavor=flavor, key_name="l3_key_r",userdata=udata)
    status = instance.status
    while status == 'BUILD':
        time.sleep(5)
        instance = nc.servers.get(instance.id)
        status = instance.status
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
    ip_details.append((wname,ipp))
    print wname + " IP:\t"+ str(ipp)


print "*** installing packages... ***"
wait_time = 450
for i in range(0,45):
    time.sleep(10)
    wait_time -= 10
    print str(wait_time)+"s remaining..."
print "*** Packages Installed!!! ***"


start_workers(str(iip),wips)
start_broker(str(iip))

print "================ DETAILS ======================================"
print "Adamzon-Broker:\t\t"+str(iip)
for (n,i) in ip_details:
    print n + ":\t"+ str(i)
print "\nFlower dashboard available at: \thttp://" + str(iip) + ":5000"
print "==============================================================="


