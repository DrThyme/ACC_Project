import os
from celery import Celery, group, subtask
import sys
import swiftclient.client
from flask import Flask, jsonify
import time
import json
import glob
from calculate_lift_drag import calc_average
from subprocess import CalledProcessError, check_output, check_call, call, Popen, PIPE, STDOUT


uname = "U_NAME"
broker_ip = "BROOKER_IP_TEMP"
passw = "P_W"
celery = Celery('tasks', backend='amqp',
                      broker='amqp://W_NAME:hej123@'+broker_ip+'/cluuster')
DEVNULL = open(os.devnull, 'wb')
config = {'user':uname, 
          'key':passw,
          'tenant_name':'ACC-Course',
          'authurl':'http://smog.uppmax.uu.se:5000/v2.0'}
conn = swiftclient.client.Connection(auth_version=2, **config)


@celery.task
def calc_lift_force(ang):
    """
    This function will do all the required work to calculate the drag and lift force for a specific angle.
    The function will run the airfoil application, convert the results from that application to a .xml file and
    calculate the average drag and lift force for that angle. Finally the function will upload the results to a bucket. 
    """

    
    angle = str(int(ang))
    cmdx = "./naca_airfoil/run.sh "+angle+" "+angle+" 1 200 0"
    print "RUN SH ON: "+angle
    print "CMD: " + cmdx
    os.system("export LC_ALL=C")
    try:
        return_code = check_call(cmdx, shell=True)
    except CalledProcessError as e:
        print e

    try:
        conv_cmd = "dolfin-convert --output xml naca_airfoil/msh/r0a"+angle+"n200.msh naca_airfoil/msh/r0a"+angle+"n200.xml"
        return_code = check_call(conv_cmd, shell=True)
    except CalledProcessError as e:
        print e
    print "Running CMD: "+conv_cmd
    

    
    
    cmdy="./naca_airfoil/navier_stokes_solver/airfoil 10 0.0001 10. 1 naca_airfoil/msh/r0a"+angle+"n200.xml"
    cmdmv = "mv /home/ubuntu/ACC_Project/results /home/ubuntu/ACC_Project/"+str(angle)+"_results"
    xmlfile = "naca_airfoil/msh/r0a"+angle+"n200.xml"
    try:
        p = check_call(["./naca_airfoil/navier_stokes_solver/airfoil","10","0.0001","10.","1",xmlfile],stdout=DEVNULL, stderr=DEVNULL)
    except CalledProcessError as e:
        print e
        
    try:
        check_call(cmdmv,shell=True)
    except CalledProcessError as e:
        print e

    try:
        (av_l, av_d) = calc_average("/home/ubuntu/ACC_Project/"+str(angle)+"_results/drag_ligt.m")
    except:
        av_l = 0
        av_l = 0
        pass

    fp = "/home/ubuntu/ACC_Project/"+str(angle)+"_results/drag_ligt.m"
    bucket_name = "G1_Project_result"
    exturl = upload_result(angle,bucket_name,fp)
    dl_url = "http://smog.uppmax.uu.se:8080/swift/v1/"+bucket_name+"/"+str(exturl)

    return (av_l, av_d, angle, dl_url)
    

    



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

    xw=filepath.replace("/home/ubuntu/ACC_Project/"+str(angle)+"_results/","")
    with open(filepath, 'r') as res_file:
        fnam = str(angle)+"_degrees/"+str(xw)
        conn.put_object(bucket_name, fnam,
                        contents= res_file.read(),
                        content_type='text/plain')

    return fnam






