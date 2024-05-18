import cv2
import numpy as np
import pyzbar.pyzbar as pyzbar
import urllib.request
import requests
import datetime
#cap = cv2.VideoCapture(0)
font = cv2.FONT_HERSHEY_PLAIN
 
url='http://192.168.40.1/'
cv2.namedWindow("live transmission", cv2.WINDOW_AUTOSIZE)
URLx = 'http://127.0.0.1:2000/'
prev=""
pres=""
while True:
    img_resp=urllib.request.urlopen(url+'cam-hi.jpg')
    imgnp=np.array(bytearray(img_resp.read()),dtype=np.uint8)
    frame=cv2.imdecode(imgnp,-1)
    #_, frame = cap.read()
 
    decodedObjects = pyzbar.decode(frame)
    for obj in decodedObjects:
        pres=obj.data
        pres = pres.decode('utf-8')
        if prev == pres:
            pass
        else:
            print("Type:",obj.type)
            print("Data: ",pres)
            prev=pres
            data = {
                "data": obj.data.decode("utf-8"),  # Assuming UTF-8 encoded data in QR code
                "time": datetime.datetime.now().isoformat()
            }
            response = requests.post(URLx, json = data)
            print(response)
            
        cv2.putText(frame, str(obj.data), (50, 50), font, 2,
                    (255, 0, 0), 3)
 
    cv2.imshow("live transmission", frame)
 
    key = cv2.waitKey(1)
    if key == 27:
        break
cv2.destroyAllWindows()