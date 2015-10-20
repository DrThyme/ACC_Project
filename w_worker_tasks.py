import os
from celery import Celery, group, subtask
import sys
import swiftclient.client
from flask import Flask, jsonify
import time
import json
import glob
from calculate_lift_drag import calc_average


"""
python worker_tasks <user_name> <password> <

"""

uname = "U_NAME"
broker_ip = "BROOKER_IP_TEMP"
passw = "P_W"

celery = Celery('tasks', backend='amqp',
                      broker='amqp://W_NAME:hej123@'+broker_ip+'/cluuster')




config = {'user':uname, 
          'key':passw,
          'tenant_name':'ACC-Course',
          'authurl':'http://smog.uppmax.uu.se:5000/v2.0'}

conn = swiftclient.client.Connection(auth_version=2, **config)


@celery.task
def calc_lift_force(ang):
    # What shell-command-method should we use?
    # http://stackoverflow.com/questions/89228/calling-an-external-command-in-python
    """
    THIS WORKS IF LC_ALL IS EXPORTED
    """

    # THIS VAR IS ONLY FOR TESTING
    angle = str(ang)
    cmdx = "cd /home/ubuntu/ACC_Project/naca_airfoil;./run.sh "+angle+" "+angle+" 1 200 0"
    print "RUN SH ON: "+angle
    print "CMD: " + cmdx
    os.system("export LC_ALL=C")
    os.system(cmdx)
    #conv_cmd = "cd /home/ubuntu/ACC_Project;./convert_to_xml.sh /home/ubuntu/ACC_Project/naca_airfoil/msh/"
    conv_cmd = "cd /home/ubuntu/ACC_Project/naca_airfoil/msh;dolfin-convert --output xml r0a"+angle+"n200.msh r0a"+angle+"n200.xml"
    print "Running CMD: "+conv_cmd
    os.system(conv_cmd)
    
    

    directory="/home/ubuntu/ACC_Project/naca_airfoil/msh/*"
    
    #result_folder = sorted(glob.glob(directory), key=os.path.getmtime)[::-1]
    
    
    # *GET LIST OF FILENAME*
    #for fil in result_folder:
    
    
    
    cmdy="cd /home/ubuntu/ACC_Project/naca_airfoil/navier_stokes_solver;export LC_ALL=C;./airfoil 10 0.0001 10. 1 ../msh/r0a"+angle+"n200.xml"
    print "running cmd: "+cmdy
    os.system(cmdy)


    # TODO: UPLOAD ALL FILES
    bucket_name = "G1_Project_result"
    fp = "/home/ubuntu/ACC_Project/naca_airfoil/navier_stokes_solver/results/drag_ligt.m"
    try:
        (av_l, av_d) = calc_average("/home/ubuntu/ACC_Project/naca_airfoil/navier_stokes_solver/results/drag_ligt.m")
    except:
        pass

    upload_result(angle,bucket_name,fp)
    #return (av_l, av_d)
    return True
    

    # Function call Via shell or imported python-function?



def upload_result(angle,bucket_name,filepath):
    """
    Uploads the result folder to the bucket 'bucket'.... prepends the angle  'angle' used when solving the equation, to each filename

    This should be done at every worker 
    """
    
    config = {'user':uname, 
              'key':passw,
              'tenant_name':'ACC-Course',
              'authurl':'http://smog.uppmax.uu.se:5000/v2.0'}

    conn = swiftclient.client.Connection(auth_version=2, **config)
    
    
    (response, bucket_list) = conn.get_account()
    for bucket in bucket_list:
        if bucket['name'] == bucket_name:
            print "*** Found bucket! ***"
	    break
    else:
        conn.put_container(bucket_name)
    	print "*** Creating bucket ***"

    xw=filepath.replace("/home/ubuntu/ACC_Project/naca_airfoil/navier_stokes_solver/results/","")
    with open(filepath, 'r') as res_file:
        conn.put_object(bucket_name, str(angle)+"_degrees/"+str(xw),
                        contents= res_file.read(),
                        content_type='text/plain')

    return True






