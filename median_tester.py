#!/usr/bin/env python3

import statistics

t1 = 0
t2 = 5
t3 = 2.2
t4 = 4
t5 = 2.1

# Sorted they should read t5,t3,t1,t4,t2
# Median of these is t1 = 19

TempC_List = [t1,t2,t3,t4,t5]
TempC_List.sort()
from statistics import median
TempM = median(TempC_List)
print ("Median = 2.2? ",TempM)
