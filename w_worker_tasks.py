import os
from celery import Celery, group, subtask
import sys
import swiftclient.client
from flask import Flask, jsonify
import time
import json
import glob
from calculate_lift_drag import calc_average
from subprocess import CalledProcessError, check_output, check_call


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
    angle = str(int(ang))
    cmdx = "./ACC_Project/naca_airfoil/run.sh "+angle+" "+angle+" 1 200 0"
    print "RUN SH ON: "+angle
    print "CMD: " + cmdx
    os.system("export LC_ALL=C")
    return_code = check_call(cmdx, shell=True)
    #conv_cmd = "cd /home/ubuntu/ACC_Project;./convert_to_xml.sh /home/ubuntu/ACC_Project/naca_airfoil/msh/"
    conv_cmd = "dolfin-convert --output xml ACC_Project/naca_airfoil/msh/r0a"+angle+"n200.msh ACC_Project/naca_airfoil/msh/r0a"+angle+"n200.xml"
    print "Running CMD: "+conv_cmd
    return_code = check_call(conv_cmd, shell=True)
    
    

    directory="/home/ubuntu/ACC_Project/naca_airfoil/msh/*"
    
    #result_folder = sorted(glob.glob(directory), key=os.path.getmtime)[::-1]
    
    
    # *GET LIST OF FILENAME*
    #for fil in result_folder:
    
    
    
    cmdy="./ACC_Project/naca_airfoil/navier_stokes_solver/airfoil 10 0.0001 10. 1 ACC_Project/naca_airfoil/msh/r0a"+angle+"n200.xml"
    cmdmv = "mv ACC_Project/naca_airfoil/navier_stokes_solver/results ACC_Project/naca_airfoil/navier_stokes_solver/"+str(angle)+"_results"
    print "running cmd: "+cmdy
    print "running cmd: "+cmdmv
    #os.system(cmdy)
    return_code = check_call(cmdy, shell=True)
    os.system(cmdmv)


    # TODO: UPLOAD ALL FILES
    bucket_name = "G1_Project_result"
    fp = "/home/ubuntu/ACC_Project/naca_airfoil/navier_stokes_solver/"+str(angle)+"_results/drag_ligt.m"
    try:
        (av_l, av_d) = calc_average("/home/ubuntu/ACC_Project/naca_airfoil/navier_stokes_solver/"+str(angle)+"_results/drag_ligt.m")
    except:
        av_l = 0
        av_l = 0
        pass

    exturl = upload_result(angle,bucket_name,fp)
    #return (av_l, av_d)
    
    dl_url = "http://smog.uppmax.uu.se:8080/swift/v1/"+bucket_name+"/"+str(exturl)
    return (av_l, av_d, angle, dl_url)
    

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

    xw=filepath.replace("/home/ubuntu/ACC_Project/naca_airfoil/navier_stokes_solver/"+str(angle)+"_results/","")
    with open(filepath, 'r') as res_file:
        fnam = str(angle)+"_degrees/"+str(xw)
        conn.put_object(bucket_name, fnam,
                        contents= res_file.read(),
                        content_type='text/plain')

    return fnam






