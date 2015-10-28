import os
from celery import Celery, group, subtask
import sys
import swiftclient.client
from flask import Flask, jsonify
from flask import request
from flask import render_template
import pickledb
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


def check_db(angle):
    db = pickledb.load('example.db', False)
    x = db.get(str(angle))
    if x != None:
        db.dump() 
        return True
    else:
        db.dump() 
        return False

def add_to_db(ang,(av_l, av_d, angle, dl_url)):
    db = pickledb.load('example.db', False)
    db.set(str(ang), (av_l, av_d, angle, dl_url))
    db.dump()
    
def get_from_db(angle):
    db = pickledb.load('example.db', False)
    x = db.get(str(angle))
    return x

@apps.route('/result')
def start():   
    maxAngle = request.args['maxAngle']
    minAngle = request.args['minAngle']
    numSamples = request.args['numSamples']
    chartID = 'chart_ID'
    chart_type = 'line'
    chart_height = 350

    if minAngle > maxAngle:
        return
    
    angle_list = input_form_user(minAngle,maxAngle,numSamples)
    a_list = []
    db_a_list = []
    for ang in angle_list:
        a = check_db(ang)
        if a == False:
            a_list.append(ang)
        else:
            x = get_from_db(ang)
            db_a_list.append(x)

    

    start = time.time()
    print "The process have started!"
    print "Creating " + str(len(a_list)) +" tasks*******"
    tasks = [calc_lift_force.s(angle) for angle in a_list]
    task_group = group(tasks)
    group_result = task_group()
    print "Waiting for workers to finnish..."
    while (group_result.ready() == False):
        time.sleep(2)
    res = group_result.get() # (av_l, av_d, angle, dl_url)

    for i in res:
        print i
   
    end = time.time()
    tot_time = end-start
    for (av_l,av_d,angle,dl_url) in res:
        add_to_db(angle,(av_l, av_d, angle, dl_url))

    resx = res + db_a_list
    resy = sorted(resx, key=lambda tup: tup[2])
    print "sorted list of all:"
    print resy
    print "**** FOUND IN DATABSE: ****"
    for i in db_a_list:
        print i

    chart = {"renderTo": chartID, "type": chart_type, "height": chart_height,}
    sd = [a for (a,b,c,d) in resy]
    sd2 = [b for (a,b,c,d) in resy]
 
    series = [{"name": 'Avrage drag force', "data": sd}, {"name": 'Avrage Lift force', "data":  sd2}]
   
    title = {"text": 'Result plot'}
    xd = [str(c) for (a,b,c,d) in resy]
 
    xAxis = {"categories": xd}
    yAxis = {"title": {"text": 'Force'}}
    print resy
    return render_template('result.html', chartID=chartID, chart=chart, series=series, title=title, xAxis=xAxis, yAxis=yAxis)
    
    
    #return render_template("result.html",arg1=maxAngle,arg2=minAngle,arg3=numSamples,tot_time=tot_time)
    

if __name__ == '__main__':
    apps.run(host='0.0.0.0',debug=True)
        
    
    
