import os
from celery import Celery, group, subtask
import sys
import swiftclient.client
from flask import Flask, jsonify
from flask import request
from flask import render_template
import time
import json



# ARGUMENTS
# angle_start : smallest anglemof attack (degrees)
# angle_stop  : biggest angle of attack (degrees)
# n_angles    : split angle_stop-angle_start into n_angles parts
# n_nodes     : number of nodes on one side of airfoil
# n_levels    : number of refinement steps in meshing 0=no refinement 1=one time 2=two times etc...
#
# EXAMPLE
# ./run.sh 0 30 10 200 3


#0 30 10 200 3



# SET DETAILS FOR EVERY WORKER

"""
broker_ip = "BROOKER_IP_TEMP"
celery = Celery('tasks', backend='amqp',
                      broker='amqp://W_NAME:hej123@'+broker_ip+'/cluuster')
"""



def input_form_user(min_ang,max_ang,nr):
    min_angle = min_ang # 0
    max_angle = max_ang # 30
    nr_angles = nr # 10

    incr_angle = (max_angle - min_angle) / nr_angles # 0.3

    i = min_angle
    angle_list = []
    while i < max_angle:
        angle_list.append(i)
        i += incr_angle
    return angle_list


def main(min_ang,max_ang,nr):
    angle_list = input_form_user(min_ang,max_ang,nr)
    create_tasks(angle_list)





def create_tasks(angle_list):
    tasks = [calc_lift_force.s(angle) for angle in angle_list]
    task_group = group(tasks)
    group_result = task_group()
    print "Waiting for workers to finnish..."
    while (group_result.ready() == False):
        time.sleep(2)
    res = group_result.get() # list of tuples: (i,av_lift,av_drag)
    # TODO: parse, and display the data




@celery.task
def calc_lift_force(angle):
    # What shell-command-method should we use?
    # http://stackoverflow.com/questions/89228/calling-an-external-command-in-python
    
    # SHOULD WE WAIT FOR COMMANDS TO EXECUTE BEFORE RUNNING THE NEXT ONE?
    os.system("cd /home/ubuntu/ACC_Project/naca_airfoil/;./run.sh +"angle+" "+angle+" 1 200 0")
    os.system("cd /home/ubuntu/ACC_Project/;./convert_to_xml naca_airfoil/msh/")

    # *GET LIST OF FILENAME*
    os.system("cd /home/ubuntu/ACC_Project/naca_airfoil/navier_stokes_solver;./airfoil 10 0.0001 10. 1 ../xml/"+filename)
    

    # Function call Via shell or imported python-function?
    (av_lift,av_drag) = avrage_result(drag_limit.m)
    return (angle,av_lift,av_drag)


#   ---REST API---
apps = Flask(__name__)

<<<<<<< HEAD
@app.route('/')
def my_form():
    return render_template("airfoil.html")


@apps.route('/', methods=['POST'])
=======
@apps.route('/start/<int:arg1>/<int:arg2>/<int:arg3>', methods=['GET'])
>>>>>>> e7a998e5b7931f2a886adf7eae9c9f786916051f
def start():
    maxAngle = request.form['maxAngle']
    minAngle = request.form['minAngle']
    numSamples = request.form['numSamples']

    #TODO Check if the max/min/samples are correct for input to main.
    #main(maxAngle,minAngle,numSamples)
    return "Process are now running."


@apps.route('/result', methods=['GET'])
def getResult():
    return "The tasks have all been completed. And the results are stored in the container."
  

if __name__ == '__main__':
    
    apps.run(host='0.0.0.0',debug=True)
        
    
    
