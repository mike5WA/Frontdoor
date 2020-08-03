#!/usr/bin/env python3

# Data stored in /home/pi/Documents/Weather_Data.csv via Weather_Data.py
# Timestamp in node-red runs Weather_Data.py every minute
# To minimize error readings the data file is updated after every 5 readings
# with the median of the last 5 readings
# Node-red charts are hidden if the doorbell is rung. When shown they reset so
# refreshing the charts from hard data maintains 24 hr chart display (24*60/5 = 288)
# Version 1.3 (Temperature Chart)

import csv
import os
from itertools import islice
from time import sleep, strftime, time

# Data files name & location
dataFile = str("/home/pi/Documents/Weather_Data.csv")

# Get current record number
with open(dataFile, "r") as log:
   reader = csv.reader(log)
   totalRows = len(list(reader))
# records < 290 start iteration at 0 else totalRows-290
if totalRows < 290:
   dataRows = 0
else :
   dataRows =(totalRows-290)

# islice = (file(),start,stop[,step])
with open(dataFile, "r") as log:
   for row in islice(csv.DictReader(log), dataRows, None):
      jsepoch = float((row['epochTime']))
# Node-red charts require JavaScript epoch time = Unix * 1,000
      jsepoch = jsepoch*1000
      print (jsepoch,",",row['TempC'])

# print ('T{0:0.1f},H{1:0.0f},P{2:.1f}'.format(temperature, humidity, my_hpa))
