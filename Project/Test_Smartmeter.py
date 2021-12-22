from datetime import datetime, timedelta
import time

def ParseLine(In_Line):
    Out_Line = None

    try:
        if In_Line.count('*') > 0:
            Out_Line = float(In_Line[In_Line.index('(')+1:In_Line.index('*')])
        else:    
            Out_Line = float(In_Line[In_Line.index('(')+1:In_Line.index(')')])

    except Exception as e:
        print(e)

    return Out_Line

OldTime = datetime.utcnow()


Lines=["b'1-0:1.8.1(002053.081*kWh)\r\n'", "b'0-0:96.7.9(00087)\r\n'", "b'1-0:21.7.0(00.030*kW)\r\n'"]

for line in Lines:

    print(ParseLine(line))

time.sleep(3)

difference = datetime.utcnow() - OldTime

print(difference.total_seconds())