import os
import sys

# python set_connection.py <IP> 
# cd <TO_DIR>
# celery worker -l info -A remote

# python parse_file.py <ip_to_broker> <openstack_pass> <this_workers_name> <openstack_username>



ip = str(sys.argv[1])
pw = str(sys.argv[2])
us_name = str(sys.argv[3])

f = open('u_utils.py','r')
filedata = f.read()
f.close()


newdata = filedata.replace("BROOKER_IP_TEMP",ip)
nnewdata = newdata.replace("P_W",pw)
nnnewdata = nnewdata.replace("U_NAME",us_name)

# write file
with open("utils.py", "wb") as fh:
        fh.write(nnnewdata)
        fh.close()


