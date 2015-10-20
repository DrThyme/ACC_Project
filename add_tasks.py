import os
from celery import Celery, group, subtask
import sys
import swiftclient.client
from flask import Flask, jsonify
from flask import request
from flask import render_template
import time
import json
import swiftclient.client
from worker_tasks import calc_lift_force

bucket_name = "G1_Project_result"

def input_form_user(min_ang,max_ang,nr):
    min_angle = min_ang # 0
    max_angle = max_ang # 30
    nr_angles = nr # 10

    incr_angle = (max_angle - min_angle) / nr_angles # 0.3

    i = min_angle
    angle_list = []
    while i < max_angle:
        angle_list.append(i)
        print "adding angle "+ str(i)
        i += incr_angle
    return angle_list



config = {'user':os.environ['OS_USERNAME'], 
          'key':os.environ['OS_PASSWORD'],
          'tenant_name':os.environ['OS_TENANT_NAME'],
          'authurl':os.environ['OS_AUTH_URL']}

conn = swiftclient.client.Connection(auth_version=2, **config)


# Clean up container in Swift
(r, ol) = conn.get_container(bucket_name)
# DELETE ALL OBJECTS
for obj in ol:
    conn.delete_object(bucket_name, obj['name'])
print "All Objects deleted..."



angle_list = input_form_user(0,3,3)
start = time.time()
print "STARTRING!!!!!!!"
tasks = [calc_lift_force.s(angle) for angle in angle_list]
task_group = group(tasks)
group_result = task_group()

print "Waiting for workers to finnish..."
while (group_result.ready() == False):
    time.sleep(2)
res = group_result.get() # list of tuples: (i,av_lift,av_drag)
end = time.time()
tot_time = end-start
print "DONE!!!!!!!"



(response, obj_list) = conn.get_container(bucket_name)
object_name_list = []
print "================ v OBJECT NAMES: v ================"
for obj in obj_list: 
    print obj['name']
print "*** Finished after "+str(tot_time)+"s ***"
