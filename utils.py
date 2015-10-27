import os
from celery import Celery, group, subtask
import sys
import swiftclient.client
from flask import Flask, jsonify
from flask import request
from flask import render_template
import time
import json
from worker_tasks import calc_lift_force


def input_form_user(min_ang,max_ang,nr):
    min_angle = int(min_ang)
    max_angle = int(max_ang)
    nr_angles = int(nr)

    incr_angle = (max_angle - min_angle) / nr_angles # 0.3
    if incr_angle < 1:
        incr_angle = 1
    else:
        incr_angle = int(incr_angle)
    
    print "INCR_ANGLE: " +str(incr_angle)
    i = min_angle
    angle_list = []
    while i < max_angle:
        angle_list.append(i)
        print "adding angle "+ str(i)
        i += incr_angle
    return angle_list


def create_tasks(angle_list):
    tasks = [calc_lift_force.s(angle) for angle in angle_list]
    task_group = group(tasks)
    group_result = task_group()
    print "Waiting for workers to finnish..."
    while (group_result.ready() == False):
        time.sleep(2)
    res = group_result.get()


#   ---REST API---
apps = Flask(__name__)

@apps.route('/')
def my_form():
    return render_template("airfoil.html")


@apps.route('/', methods=['POST'])
def start():   
    maxAngle = request.form['maxAngle']
    minAngle = request.form['minAngle']
    numSamples = request.form['numSamples']
    if minAngle > maxAngle:
        return
    
    angle_list = input_form_user(minAngle,maxAngle,numSamples)
    
    start = time.time()  
    print "The process have started!"
    tasks = [calc_lift_force.s(angle) for angle in angle_list]
    task_group = group(tasks)
    group_result = task_group()
    print "Waiting for workers to finnish..."
    while (group_result.ready() == False):
        time.sleep(2)
    res = group_result.get()

    for i in res:
        print i
   
    end = time.time()
    tot_time = end-start
    return render_template("result.html",res=res,tot_time=tot_time) 

if __name__ == '__main__':
    apps.run(host='0.0.0.0',debug=True)
        
    
    
