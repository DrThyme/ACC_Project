import os
from celery import Celery, group, subtask
import sys
import swiftclient.client
from flask import Flask, jsonify
import time
import json
import glob



"""
python worker_tasks <user_name> <password> <

"""

uname = "U_NAME"
broker_ip = "BROOKER_IP_TEMP"
passw = "P_W"

celery = Celery('tasks', backend='amqp',
                      broker='amqp://W_NAME:hej123@'+broker_ip+'/cluuster')

bucket_name = "GROUP1_RESULT"



config = {'user':uname, 
          'key':passw,
          'tenant_name':'ACC-Course',
          'authurl':'http://smog.uppmax.uu.se:5000/v2.0'}

conn = swiftclient.client.Connection(auth_version=2, **config)


@celery.task
def calc_lift_force(angle):
    # What shell-command-method should we use?
    # http://stackoverflow.com/questions/89228/calling-an-external-command-in-python
    """
    THIS WORKS IF LC_ALL IS EXPORTED
    """

    # THIS VAR IS ONLY FOR TESTING
    
    os.system("export LC_ALL=C")
    os.system("cd /home/ubuntu/ACC_Project/naca_airfoil/;./run.sh "+angle+" "+angle+" 1 200 0")
    os.system("cd /home/ubuntu/ACC_Project/;./convert_to_xml.sh naca_airfoil/msh/")

    directory="/home/ubuntu/ACC_Project/naca_airfoil/xml/*"
    result_folder = sorted(glob.glob(directory), key=os.path.getmtime)[::-1]
    
    
    # *GET LIST OF FILENAME*
    
    for fil in result_folder:
        filename, file_extension = os.path.splitext(str(fil))
        os.system("cd /home/ubuntu/ACC_Project/naca_airfoil/navier_stokes_solver;./airfoil 10 0.0001 10. 1 "+str(fil))


    # TODO: UPLOAD ALL FILES
    bucket_name = "G1_Project_result"
    upload_result(angle,bucket_name)
    

    # Function call Via shell or imported python-function?



def upload_result(angle,bucket_name):
    """
    Uploads the result folder to the bucket 'bucket'.... prepends the angle  'angle' used when solving the equation, to each filename

    This should be done at every worker 
    """
    
    config = {'user':uname, 
              'key':passw,
              'tenant_name':'ACC-Course',
              'authurl':'http://smog.uppmax.uu.se:5000/v2.0'}

    conn = swiftclient.client.Connection(auth_version=2, **config)
    angle ="0"
    
    (response, bucket_list) = conn.get_account()
    for bucket in bucket_list:
        if bucket['name'] == bucket_name:
            print "*** Found bucket! ***"
	    break
    else:
        conn.put_container(bucket_name)
    	print "*** Creating bucket ***"



    directory="/home/ubuntu/ACC_Project/naca_airfoil/navier_stokes_solver/results/*"
    dd = "/home/ubuntu/ACC_Project/naca_airfoil/navier_stokes_solver/results"
    result_folder = sorted(glob.glob(directory), key=os.path.getmtime)[::-1]
    for fil in result_folder:
        filename, file_extension = os.path.splitext(str(fil))
        xw=filename.replace(dd+"/","")
        filenamee = xw+str(file_extension)
	print "*** Uploading: '" +str(fil)+"' ***"
        with open(fil, 'r') as res_file:
            conn.put_object(bucket_name, str(angle)+"degrees/"+str(filenamee),
                            contents= res_file.read(),
                            content_type='text/plain')

    (response, obj_list) = conn.get_container(bucket_name)
    print "================ v OBJECT NAMES: v ================"
    for obj in obj_list:
        print obj['name']






