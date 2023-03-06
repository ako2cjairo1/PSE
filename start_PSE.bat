@ECHO OFF
CMDOW @ /ren "PSE Ticker" /mov 1244 -25 /siz 217 700 /top
CD C:\Users\Dave\DEVENV\Python\PSE
@ECHO PSE Ticker is initiating...
python main.py
@ECHO PSE Ticker is closing...
TIMEOUT 1
EXIT