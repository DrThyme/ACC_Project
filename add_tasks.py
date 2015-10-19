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

angle_list = input_form_user(0,3,3)
tasks = [calc_lift_force.s(angle) for angle in angle_list]
task_group = group(tasks)
group_result = task_group()

task_group = group(tasks)
group_result = task_group()
print "Waiting for workers to finnish..."
while (group_result.ready() == False):
    time.sleep(2)
res = group_result.get() # list of tuples: (i,av_lift,av_drag)
print "DONE!!!!!!!"
