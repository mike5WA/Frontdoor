#!/usr/bin/env python3

# Copyright (c) 2014 Adafruit Industries# Author: Tony DiCola
# Also Mike Garner 03/6/2019 V3.0.2
# Write data to csv file for display via node-red dashboard
# Print command = msg.payload data
# Added epoch field 31/3/2019

# 03/6/19
# Added routine to check for valid sensor data before writing to csv files
# Added formatting of data prior to writing to csv files

import Adafruit_DHT
import Adafruit_BMP.BMP085 as BMP085
from time import sleep, strftime, time
import csv
import os
import statistics
from itertools import islice

# Data files name & location
readings = str("/home/pi/Documents/Weather_Data5.csv")
dataFile = str("/home/pi/Documents/Weather_Data.csv")
dataFileTemp = str("/home/pi/Documents/Weather_Data_Temp.csv")

# Define Global variables
global Temp
global Humidity
global Hpa

# Define field/column names in data file
fieldnames = ['DateTime','TempC','Humidity','Hpa','epochTime']

# Create Weather_Data.csv if doesn't exist & write headers
exists = os.path.isfile(dataFile)
if exists is False:
  with open (dataFile, "a+") as log:
    writer = csv.DictWriter(log, fieldnames=fieldnames)
    writer.writeheader()

# Limit records depending upon needs & frequency of readings via dashboard
# As readings only recorded to Weather_Data.csv every 5 minutes 1 day =288 records
row_min = 295
row_max = 900
my_row =1

# Set DHT sensor model & GPIO pin
sensor_DHT = Adafruit_DHT.DHT22
pin = 6

#Set BMP sensor BMP180 same as BMP085 sensor is I2C connected to SDA & SCA
sensor_BMP = BMP085.BMP085()

#--------------------------------------------------------------------
# Function to get readings from  sensors
def sensorReads():
# Get readings from DHT22 (_retry makes max 15 attempts at 2secs interval 
  humidity, temperature = Adafruit_DHT.read_retry(sensor_DHT, pin)
# Get pressure reading from BMP sensor
  my_hpa = float(sensor_BMP.read_pressure()/100)
# Define and set variables
  global Temp
  Temp = float("{0:0.1f}".format(temperature))
  global Humidity
  Humidity = float("{0:0.2f}".format(humidity))
  global Hpa
  Hpa = float("{0:0.1f}".format(my_hpa))
  return (Temp, Humidity, Hpa)

#-------------------------------------------------------------------

#---------------------------------------------------------------------
# Function to calculate median of last 5 data readings to avoid errors or null
# First values = current readings
def dataMedian():
   t1 = float(Temp)
   h1 = float(Humidity)
   p1 = float(Hpa)
# Next get last 4 data readings from csv file
# print ("Latest read = ",t1,h1,p1)
   myRow = 4
   with open(readings, "r") as log:
     for row in islice(csv.DictReader(log), (2), None):
       if myRow == 4:
         t2 = float(row['TempC'])
         h2 = float(row['Humidity'])
         p2 = float(row['Hpa'])
         myRow = (myRow-1)
       if myRow == 3:
         t3 = float(row['TempC'])
         h3 = float(row['Humidity'])
         p3 = float(row['Hpa'])
         myRow = (myRow-1)
       if myRow == 2:
         t4 = float(row['TempC'])
         h4 = float(row['Humidity'])
         p4 = float(row['Hpa'])
         myRow = (myRow-1)
       if myRow == 1:
         t5 = float(row['TempC'])
         h5 = float(row['Humidity'])
         p5 = float(row['Hpa'])
         myRow = (myRow-1)

# Pass data variables to medianCalc()function
   TempC_List = [t1,t2,t3,t4,t5]
   Humidity_List = [h1,h2,h3,h4,h5]
   Hpa_List = [p1,p2,p3,p4,p5]
# Now have csv list of last 5 readings to calculate median
# Median routine
   from statistics import median
   TempM = (median(TempC_List))
   HumidityM = (median(Humidity_List))
   HpaM = (median(Hpa_List))
# print ("Median Data is ", TempM,HumidityM,HpaM)
   return (TempM, HumidityM, HpaM)
#-----------------------------------------------------------------------

# Obtain valid readings from sensors loops until valid readings 
sensorReads()
# print (Temp, Humidity, Hpa)
if Temp is not None and Humidity is not None and Hpa is not None:
  print ("DHT is recording!")
else:
  print('DHT failed. Try again!')
  sensorReads ()

# Get time of readings
epochTime = time()
#print ("epoch = ", epochTime)
DateTime = strftime("%Y-%m-%d %H:%M:%S")

# Print command = msg.payload for node-red
# Write Date_Time, TempC,Humidity, Hpa to Weather_Data5.csv file
# After 5 readings calculate median and write to Weather_Data.csv
# Check if Weather_Data5 file exists & if not create it with header = fieldnames & write data
exists = os.path.isfile(readings)
if exists is False:
  with open (readings, "a+") as log:
    writer = csv.DictWriter(log, fieldnames=fieldnames)
    writer.writeheader()
    log.write("{0},{1},{2},{3},{4}\n".format(strftime("%Y-%m-%d %H:%M:%S"), str(Temp), str(Humidity), str(Hpa), str(epochTime)))
    print ('T{0:0.1f},H{1:0.0f},P{2:.1f}'.format(Temp, Humidity, Hpa))
else:
# File exists so write readings to file
  with open(readings, "a") as log:
    log.write("{0},{1},{2},{3},{4}\n".format(strftime("%Y-%m-%d %H:%M:%S"), str(Temp), str(Humidity), str(Hpa), str(epochTime)))
    print ('T{0:0.1f},H{1:0.0f},P{2:.1f}'.format(Temp, Humidity, Hpa))

# Check to see if we have 6 records (header + 5 data)
with open(readings, "r") as log:
  reader = csv.reader(log)
  totalRows = len(list(reader))
  print ("Total rows = ",(totalRows))
  if totalRows >=6 :
# Get median of last 5 readings via dataMedian function & write to Weather_Data.csv 
    (TempM, HumidityM, HpaM) = dataMedian()
    with open(dataFile, "a+") as log:
      log.write("{0},{1},{2},{3},{4}\n".format(strftime("%Y-%m-%d %H:%M:%S"), TempM, HumidityM, HpaM, epochTime))
# Delete Weather_Data5.csv
      os.remove(readings)

# Procedure to keep Weather_Data.csv to reasonable size (max & min rows)
# Count total rows in csv file to see if max size reached
with open(dataFile, "r+") as log:
  reader = csv.reader(log)
  totalRows = len(list(reader))
if totalRows > row_max :
# Create temp csv file to take last x entries & write headers
  with open (dataFileTemp, "a+") as tempLog:
    writer = csv.DictWriter(tempLog, fieldnames=fieldnames)
    writer.writeheader()
# Roll through last row_min entries & write data to temp csv
  with open(dataFile, "r") as log:
    csv_reader = csv.DictReader(log)
    for row in islice(csv.DictReader(log), (totalRows-row_min), None):
        with open (dataFileTemp, "a+") as tempLog:
          writer = csv.DictWriter(tempLog, fieldnames=fieldnames)
          writer.writerow(row)
# We now have a reduced data file so delete old csv file and rename new
  os.remove(dataFile)
  os.rename(dataFileTemp,dataFile)

