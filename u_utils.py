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
from novaclient.client import Client


uname = "U_NAME"
broker_ip = "BROOKER_IP_TEMP"
passw = "P_W"


config = {'username':uname, 
          'api_key':passw,
          'project_id':'ACC-Course',
          'auth_url':'http://smog.uppmax.uu.se:5000/v2.0',
           }

def input_form_user(min_ang,max_ang,nr):
    ''' input_from_user calculates which angles that should that 
        lies between 'min_ang' and 'max_ang' 
        when taking 'nr' or steps between them. 

    Args:
        min_ang (int) : lower limit
        max_ang (int) : upper limit
        nr (int) : number of steps between lower and upper limit
    Returns:
        angle_list (int list) : list of angles between max_ang and min_ang when taking 'nr' of steps  
    '''
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



#   ---REST API---
apps = Flask(__name__)

@apps.route('/')
def my_form():
    return render_template("airfoil.html")


def check_db(angle):
    ''' check_db checks if the key 'angle' exists in the database 

    Args:
        angle : the key (angle) that should be queried
    Returns:
        True if the key exists
        False otherwise
        
    '''
    db = pickledb.load('example.db', False)
    x = db.get(str(angle))
    if x != None:
        db.dump() 
        return True
    else:
        db.dump() 
        return False

def add_to_db(ang,(av_l, av_d, angle, dl_url)):
    ''' add_to_db adds a key/pair to the database

    Args:
        angle : the key (angle) that should be queried
        (av_l,av_d,angle,dl_rul) : the value... A tuple of avrage lift force, avrage drag force, angle calculated on and download URL
    Returns:
        None
    '''
    db = pickledb.load('example.db', False)
    db.set(str(ang), (av_l, av_d, angle, dl_url))
    db.dump()
    
def get_from_db(angle):
    ''' get_from_db returns the value of the given key 'angle'

    Args:
        angle : the key (angle) that should be queried
    Returns:
        x (tuple) : A tuple of avrage lift force, avrage drag force, angle calculated on and download URL
    '''
    db = pickledb.load('example.db', False)
    x = db.get(str(angle))
    return x

@apps.route('/result')
def start():
    worker_names = ["Group1-Worker-1","Group1-Worker-2","Group1-Worker-3","Group1-Worker-4","Group1-Worker-5","Group1-Worker-6","Group1-Worker-7","Group1-Worker-8"]
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
    
    pushed_tasks = len(a_list)
    optimal_tasks_per_worker = 2
    nr_of_workers = pushed_tasks / optimal_tasks_per_worker
    
    nc = Client('2',**config)
    servers = []
    for w in worker_names:
        try:
            server = nc.servers.find(name=w)
            servers.append(server)
            print "SERVER added: " +str(w)
        except:
            pass
        
    for s in servers:
        s.suspend()
        print "server suspended!"

    if pushed_tasks > optimal_tasks_per_worker*len(servers):
        for s in servers:
            print "Using all instances!"
            s.resume()
    else:
        i = 0:
        while pushed_tasks > 0:
            ser = servers[i]
            ser.resume()
            print "Resumed instance!"
            pushed_tasks -= optimal_tasks_per_worker
            i += 1
        
     

    


    
    tasks = [calc_lift_force.s(angle) for angle in a_list]
    task_group = group(tasks)
    group_result = task_group()
    print "Waiting for workers to finnish..."
    while (group_result.ready() == False):
        time.sleep(2)
    res = group_result.get() # (av_l, av_d, angle, dl_url)
 
    end = time.time()
    tot_time = end-start
    for (av_l,av_d,angle,dl_url) in res:
        add_to_db(angle,(av_l, av_d, angle, dl_url))

    resx = res + db_a_list
    resy = sorted(resx, key=lambda tup: int(tup[2]))
  

    chart = {"renderTo": chartID, "type": chart_type, "height": chart_height,}
    sd = [a for (a,b,c,d) in resy]
    sd2 = [b for (a,b,c,d) in resy]
 
    series = [{"name": 'Avrage drag force', "data": sd}, {"name": 'Avrage Lift force', "data":  sd2}]
   
    title = {"text": 'Result plot'}
    xd = [str(c) for (a,b,c,d) in resy]
    dls = [d for (a,b,c,d) in resy]
 
    xAxis = {"categories": xd}
    yAxis = {"title": {"text": 'Force'}}
    utasks = str(len(a_list))
    dbtasks = str(len(db_a_list))
    
    return render_template('result.html', chartID=chartID, chart=chart, series=series, title=title, xAxis=xAxis, yAxis=yAxis,maxAngle=maxAngle,minAngle=minAngle,numSamples=numSamples,tot_time=tot_time,utasks=utasks,dbtasks=dbtasks,dls=dls)
    
    #return render_template("result.html",arg1=maxAngle,arg2=minAngle,arg3=numSamples,tot_time=tot_time)
    

if __name__ == '__main__':
    apps.run(host='0.0.0.0',debug=True)
        
    
    
