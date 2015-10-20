import sys
import csv

def calc_average(parse_file):
  # zip the file contents into a list of three lists, each containing
  # one column. The first row of the file is ignored
  with open(parse_file) as input:
  next(input)
  output = zip(*(line.strip().split('\t') for line in input))

  # calculate the average lift force by summing all values in the
  # second list
  sum_temp = 0
  for j in output[1]:
    sum_temp += float(j)
    sum_avg_lift = sum_temp/len(output[1])

  # calculate the average drag force by summing all values in the
  # third list
  sum_temp = 0
  for j in output[2]:
    sum_temp += float(j)
    sum_avg_drag = sum_temp/len(output[2])

    print 'Average lift: ',sum_avg_lift
    print 'Average drag: ',sum_avg_drag
  return (sum_avg_lift,sum_avg_drag)
