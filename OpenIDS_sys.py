from typing import Any, Tuple, Union

import serial
import os
import time
import threading
import winsound
import paramiko
import sys
import pyautogui
import cv2
import numpy as np
import math
import socketreceive
import test_server
from PIL import Image
from PyQt5.QtGui import QPixmap, QImage
import PyQt5
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


ink_pump1,ink_pump2, dT,xp,ACN,Oxidizer,Deblock,arduino,linear,amidite_T = None,None,None,None,None,None,None,None,None,None
command = None
try:
    sound_path = os.getcwd()+'\\x64\\Release\\alram'
    synthesis_log_path = os.getcwd() + '\\x64\\Release\\synthesis_log\\' +time.strftime("%y_%m_%d_%H시%M")
    synthesis_log_txt = open(synthesis_log_path+'.txt','w')
    sequence_path = os.getcwd() + '\\x64\\Release\\sequence.txt'

    
except Exception as E:
    print("log폴더 생성햇")

class Calibration(threading.Thread):
    
    
    
    def __init__(self,ChangePixmapSignal):
        super().__init__()
        self._run_flag = False
        #socketreceive.connect()


        self.change_pixmap_signal = ChangePixmapSignal
        self.main_gui = None
        self.degree_angle = 1
        self.well_size = 11.25
        self.x_move = -40
        self.y_move = -24
        
        
        

    def set_label(self, ImageLabel, ZoomImageLabel):
        self.image_label = ImageLabel
        #self.zoom_image_label = ZoomImageLabel
        
        
    def set_pos(self, X, Y, show):
        
        if show:
            self.x = X
            self.y = Y
            #self.zoom_image_label.move(X+20, Y+20)
            
            
        
    def update_image(self, cv_img):
        qt_img = self.convert_cv_qt(cv_img)
        self.image_label.setPixmap(qt_img)

        try:
            #qt_zoom_img=qt_img.copy(self.x, self.y, 100,100)
            #qt_zoom_img = qt_zoom_img.scaledToWidth(300)
            #self.zoom_image_label.setPixmap(qt_zoom_img)
            pass
        except Exception as E:
            pass
        


        

    def convert_cv_qt(self, cv_img):
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(800, 800, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)

    def setLabel(self,img, pts, label):
        (x, y, w, h) = cv2.boundingRect(pts)
        ptj = (x, y)
        ptw = (x + w, y + h)
        cv2.rectangle(img, ptj, ptw, (0, 255, 0), 2)
        cv2.putText(img, label, (ptj[0], ptj[1] - 3), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255))

    def detect_well(self, cv_img):

        # blur 처리
        blur1 = cv2.medianBlur(cv_img, 5)
        blur2 = cv2.bilateralFilter(blur1, 5, 75, 75)



        # noies 제거
        #denoised_img = cv2.fastNlMeansDenoisingColored(blur2, None, 5, 5, 5, 10)


        #gray = cv2.cvtColor(denoised_img, cv2.COLOR_BGR2GRAY)
        #ret, thr = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU)

        # 흑백으로 이진화
        gray = cv2.cvtColor(blur2, cv2.COLOR_BGR2GRAY)
        ret, thr = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU)

        contours, _ = cv2.findContours(thr, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        # 외곽선 검출

        L_dot = []
        for cont in contours:
            if 50 < cv2.contourArea(cont) and 200>cv2.contourArea(cont):  # 최소크기 지정
                approx = cv2.approxPolyDP(cont, cv2.arcLength(cont, True) * 0.06, True)  # 사각형 검출
                vtc = len(approx)
                if vtc == 4:
                    self.setLabel(self.cv_img, cont, 'Rec')  # Rec글자 출력
                    M = cv2.moments(cont)
                    cX = int(M['m10'] / M['m00'])
                    cY = int(M['m01'] / M['m00'])  # 중심 구하기
                    cv2.circle(cv_img, (cX, cY), 3, (255, 0, 0), -1)  # 중심점 출력
                    L_dot.append([cX, cY])  # 좌표 리스트화
        L_min_distance = []


        for i in range(0, len(L_dot)):
            now = L_dot[i]
            L_distance = []
            for j in range(0, len(L_dot)):
                if i != j:
                    target = L_dot[j]
                    distance = ((now[0] - target[0]) ** 2 + (now[1] - target[1]) ** 2) ** 0.5
                    L_distance.append(distance)
            L_distance.sort()
            try:
                L_min_distance.append(L_distance[0])
                L_min_distance.append(L_distance[1])
            except Exception as E:
                pass
                #print("Calibration : well 인식안됨")

        #AVG = sum(L_min_distance, 0.0) / len(L_min_distance)

        #print(AVG)






    def run(self):

        print("server connecting...")
        test_server.connect()
        print("server connected")
        
        while(1):


            try:
                self.degree_angle = float(self.main_gui.camera_tab.get_angle.text())

                
            except Exception as E:
                self.degree_angle = 0


            try:
                self.well_size = float(self.main_gui.camera_tab.set_size.text())

            except Exception as E:
                self.well_size = 0

            try:
                self.x_move = int(self.main_gui.camera_tab.x_move_set.text())

            except Exception as E:
                self.x_move = 0

            try:
                self.y_move = int(self.main_gui.camera_tab.y_move_set.text())

                
            except Exception as E:
                self.y_move = 0
                
            
            self.xwell_count = 16
            self.ywell_count = 9
            self.CtoC = int(self.well_size / 200 * 1371)
            self.xstarting_point = round(1.82 * self.well_size / 0.2)
            self.ystarting_point = round(1.82 * self.well_size / 0.2)
            self.xend_point = self.xstarting_point + (self.xwell_count - 1) * self.CtoC + 1
            self.yend_point = self.ystarting_point + (self.ywell_count - 1) * self.CtoC + 1
            self.CtoC = self.well_size * 5
            rotated_img = None

            try:

                #ret, cv_img = socketreceive.get_img()

                ret, self.cv_img = test_server.get_image()


                #self.detect_well(self.cv_img)


                if ret:
                    if self._run_flag:
                        
                        height, width, tmp = self.cv_img.shape

                        '''

                        wells = [(a, b, self.well_size, self.well_size) for a in np.arange(self.xstarting_point, self.xend_point, self.CtoC) for b in np.arange(self.ystarting_point, self.yend_point, self.CtoC)]
                        for well in wells:
                            
                            cv_img = cv2.rectangle(cv_img, well, (255, 255, 255), -1)

                        '''

                        for column in range(0, self.xwell_count):  # 컬럼갯수
                            for row in range(0, self.ywell_count):  # 줄 수
                                x_start = int(self.xstarting_point + column * self.CtoC) + self.x_move
                                y_start = int(self.ystarting_point + row* self.CtoC) + self.y_move
                   
                                rad = self.degree_angle * (math.pi / 180.0)
                                x_start = x_start - width/2
                                y_start = y_start - height/2
                                nx = round(math.cos(rad)*x_start - math.sin(rad)*y_start)
                                ny = round(math.sin(rad)*x_start + math.cos(rad)*y_start)
                            
                                nx = int(nx + width/2)
                                ny = int(ny + height/2)

                                self.cv_img = cv2.rectangle(self.cv_img, (nx,ny), (nx+int(self.well_size),ny+int(self.well_size)), (0,0,255), -1)

                        #matrix = cv2.getRotationMatrix2D((height / 2, height / 2), -90+self.degree_angle, 1)
                        #rotated_img = cv2.warpAffine(cv_img, matrix, (int(height), int(width)))

                        
                        
                    else:
                        pass
                #self.change_pixmap_signal.emit(cv_img)
                self.update_image(self.cv_img)

                
                

            except Exception as E:
      
                print(E)



            
            


class System():
    def connection(self):
        
        connection_Fluidics = [0, 0, 0,0]
        Current_position=0
        
        global ink_pump1,ink_pump2,dT,ACN,Oxidizer,Deblock,arduino,linear

        print("connection")
        try:
            ACN = serial.Serial("COM4", 9600, write_timeout=1, timeout=0.1)
            connection_Fluidics[0] = True
            print("ACN connect")
            
        except Exception as e:
            print(e)
            connection_Fluidics[0] = False

        try:
            Oxidizer = serial.Serial("COM3", 9600, write_timeout=1, timeout=0.1)

            connection_Fluidics[1] = True
            print("oxidizer connect")
            
        except Exception as e:
            print(e)
            connection_Fluidics[1] = False

        try:
            Deblock = serial.Serial("COM8", 9600, write_timeout=1, timeout=0.1)

            connection_Fluidics[2] = True
            print("deblock connect")
            
        except Exception as e:
            print(e)
            connection_Fluidics[2] = False

        try:
            dT = serial.Serial("COM100", 9600, write_timeout=1, timeout=0.1)
            connection_Fluidics[3] = True
            print("dT connect")

            
        except Exception as e:
            print(e)
            connection_Fluidics[3] = False

        try:
            
            ink_pump1 = serial.Serial("COM7", 9600)
            print("ink pump1 connect")

        except Exception as e:
            print(e)
            
        try:
            
            ink_pump2 = serial.Serial("COM5", 9600)
            print("ink pump2 connect")

        except Exception as e:
            print(e)
    def ink_manual_move(self, command):
        if command.find("+") > 0:
            state = open("state.txt","w")
            state.write(command)
            state.close()       

    def set_current_position(self,step_gap):
        state = open("state.txt","w")
        state.write("C"+str(step_gap))
        state.close()
        self.linear_wait()
        time.sleep(3)

    def syringe_init(self):
        global dT,ACN,Oxidizer,Deblock

        print("Syringe init")
        '''
        ACN.write(b'init;')
        Oxidizer.write(b'init;')
        Deblock.write(b'init;')
        '''
        try:
            
            state = open("state.txt","w")
            state.write("Syringe_Oxidation_init")
            
            state.close()
            
            self.linear_wait()
            print('oxidizer init')
            Oxidizer.write(b'/1ZR\r\n')
            self.syringe_wait(Oxidizer)
            

        except Exception as E:
            print(E)

        try:
            
            state = open("state.txt","w")
            state.write("Syringe_dT_init")
            state.close()
            self.linear_wait()
            print('dT init')
            dT.write(b'/1ZR\r\n')
            self.syringe_wait(dT)


        except Exception as E:
            print(E)

        try:
            state = open("state.txt","w")
            state.write("Syringe_ACN_init")
            state.close()
            self.linear_wait()
            print('ACN init')
            ACN.write(b'/1ZR\r\n')
            self.syringe_wait(ACN)
        except Exception as E:
            print(E)

            

            
        try:
            
            state = open("state.txt","w")
            state.write("Syringe_Deblock_init")
            state.close()
            self.linear_wait()
            print('deblock init')
            Deblock.write(b'/1ZR\r\n')
            self.syringe_wait(Deblock)
        except Exception as E:
            print(E)
            
            '''
            Deblock.write(b'/1V1000I5A3000R\r\n')
            self.syringe_wait(Deblock)
            Deblock.write(b'/1I6A0R\r\n')
            self.syringe_wait(Deblock)
            '''

            

        except Exception as e:
            print(e)
    '''
    def syringe_flush(self):
        ACN.write(b'/1V6000I3A6000R\r\n')f

        self.linear_wait()
        self.syringe_wait(ACN)
        ACN.write(b'/1V1000I6A0R\r\n')
        self.syringe_wait(ACN)

        ACN.write(b'/1V6000I3A6000R\r\n')

        self.linear_wait()
        self.syringe_wait(ACN)
        ACN.write(b'/1V1000I6A0R\r\n')
        self.syringe_wait(ACN)

        ACN.write(b'/1V6000I3A6000R\r\n')

        self.linear_wait()
        self.syringe_wait(ACN)
        ACN.write(b'/1V1000I6A0R\r\n')
        self.syringe_wait(ACN)

        Oxidizer.write(b'/1V3000I4A6000R\r\n')
        
        self.linear_wait()
        self.syringe_wait(Oxidizer)

        Oxidizer.write(b'/1V500I7A0R\r\n')
        self.syringe_wait(Oxidizer)
        Oxidizer.write(b'/1V3000I4A6000R\r\n')
        
        self.linear_wait()
        self.syringe_wait(Oxidizer)

        Oxidizer.write(b'/1V500I7A0R\r\n')
        self.syringe_wait(Oxidizer)
        Oxidizer.write(b'/1V3000I4A6000R\r\n')
        
        self.linear_wait()
        self.syringe_wait(Oxidizer)

        Oxidizer.write(b'/1V500I7A0R\r\n')
        self.syringe_wait(Oxidizer)

                   
        Deblock.write(b'/1V3000I3A6000R\r\n')

        self.linear_wait()

        self.syringe_wait(Deblock)
            
        Deblock.write(b'/1V500I6A0R\r\n')
        self.syringe_wait(Deblock)
        Deblock.write(b'/1V3000I3A6000R\r\n')

        self.linear_wait()

        self.syringe_wait(Deblock)
            
        Deblock.write(b'/1V500I6A0R\r\n')
        self.syringe_wait(Deblock)
        Deblock.write(b'/1V3000I3A6000R\r\n')

        self.linear_wait()

        self.syringe_wait(Deblock)
            
        Deblock.write(b'/1V500I6A0R\r\n')
        self.syringe_wait(Deblock)
        '''

    def line(self,img):
        # 이진화
        ret, img=cv2.threshold(img, 100, 255, cv2.THRESH_BINARY_INV)

        # 에지 검출
        edges = cv2.Canny(img, 50, 50)

        # 직선 성분 검출
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180., 110, minLineLength=300, maxLineGap=600)

        if lines is not None:

            x1 = int(lines[0][0][0])
            y1 = int(lines[0][0][1])  # 시작점 좌표 x,y
            x2 = int(lines[0][0][2])
            y2 = int(lines[0][0][3])  # 끝점 좌표, 가운데는 무조건 0

            if (x2 != x1):
                angle = (y2 - y1) / (x2 - x1)
                if angle != 0:
                    x = x1 - y1 / angle
                else:
                    x = x1

            else:
                x = x1

            return x, x1, y1, x2, y2


        else:
            return -1 ,-1, -1, -1, -1



    def printing_Act(self,cycle):
        threading.Thread(target=self.check_point,args = (cycle,"coupling",)).start()
        self.x_init()

        pyautogui.click(63,31)
        time.sleep(1)
        pyautogui.click(128,54)
        time.sleep(1)

        pyautogui.click(909,343)
        time.sleep(0.5)


        pyautogui.click(1045,896)
        
        print('dT')
        state = open("state.txt", "w")
        state.write("Print")
        state.close()
        time.sleep(18)

        pyautogui.click(63,31)
        time.sleep(1)
        pyautogui.click(128,54)
        time.sleep(1)

        pyautogui.click(909,343)
        time.sleep(0.5)


        pyautogui.click(1045,896)


    def printing_T(self,cycle):
        threading.Thread(target=self.check_point,args = (cycle,"coupling",)).start()
        self.x_init()

        pyautogui.click(63,31)
        time.sleep(1)
        pyautogui.click(128,54)
        time.sleep(1)

        pyautogui.click(862,343)
        time.sleep(0.5)

        pyautogui.click(1045,896)
        
        print('Act')
        state = open("state.txt", "w")
        state.write("Print")
        state.close()
        time.sleep(18)

        pyautogui.click(63,31)
        time.sleep(1)
        pyautogui.click(128,54)
        time.sleep(1)

        pyautogui.click(862,343)
        time.sleep(0.5)

        pyautogui.click(1045,896)

        
    def printing_both(self,cycle,print_num):
        threading.Thread(target=self.check_point,args = (cycle-1,"coupling",)).start()

        
        
        
        state = open("state.txt", "w")
        state.write("Print"+'C'+str(cycle)+'P'+str(print_num))
        state.close()
        time.sleep(18)
        #time.sleep(8)
        #self.waste(300, 0.5)

    

    def flush(self, mode):
        state = open("state.txt", "w")
        state.write(mode)
        state.close()

    def pre_wet(self, cycle):

        threading.Thread(target=self.check_point,args = (cycle, "pre wet",)).start()
        print("액티베이터로 미리적셔")
        #global ACN_used
        #ACN_used += volume
        state = open("state.txt","w")
        state.write("Bulk_dT")
        state.close()
        
        
        retraction = 150
        
        ##############충전##############       

        self.syringe_wait(dT)
        dT.write(b'/1I5R\r\n')
        self.syringe_wait(dT)
        #dT.write(b'/1V4000I5A1300R\r\n')
        #self.syringe_wait(dT)
        dT.write(b'/1I6R\r\n')
        self.syringe_wait(dT)
        dT.write(b'/1V4000I6A2150R\r\n')#2330#113차 2000이었
        self.syringe_wait(dT)
        ################################
        

        ##########밸브 포트 설정##########
        self.syringe_wait(dT)
        dT.write(b'/1I7R\r\n')
        ##################################

        ###############분사###############
        self.linear_wait() # linear가 분사위치에 도착할 때까지 기달
        start = time.time() 
        

            
        self.syringe_wait(dT)
        dT.write(b'/1I7V1500A0R\r\n')
        ###################################
            

        #다시 살짝 빨아들임
        self.syringe_wait(dT)
        dT.write(b'/1V300I7A'+str(int(retraction)).encode()+b'R\r\n')
        time.sleep(5)
        self.blow(1, 1, 1)
        self.blow(1, 1, 1)
        
        end = time.time()

        

    def printing_Test(self,cycle):
        threading.Thread(target=self.check_point,args = (cycle,"coupling",)).start()
        self.x_init()

        state = open("state.txt", "w")
        state.write("Print")
        state.close()
        time.sleep(18)


        
        



    def x_init(self):
        print("x_init")
        state = open("state.txt","w")
        state.write("x_init")
        state.close()
        self.linear_wait()

    
    def moving(self,distance):
        if distance == "x_init":
            self.x_init()
        else:
            state = open("state.txt", "w")
            state.write("move"+str(distance))
            state.close()


    
    def wait(self,n):
        time.sleep(n)
        

    
    def blow(self,valve_open_time, incubation, cycle):
        threading.Thread(target=self.check_point,args = (cycle, "blow",)).start()
        
        state = open("state.txt","w")
        state.write("Blow")
        state.close()
        self.linear_wait()

        

    def Sblow(self,valve_open_time, incubation, cycle):
        threading.Thread(target=self.check_point,args = (cycle, "Sblow",)).start()
        state = open("state.txt","w")
        state.write("SBlow")
        state.close()
        print("Sblow")
        self.linear_wait()
        

        
        




    ######bulk soultion syringe 사용하여 control######



    def Bulk_dT(self, cycle):
        threading.Thread(target=self.check_point,args = (cycle, "dT",)).start()
        print("벌크\n벌크\n벌크\n벌크")
        #global ACN_used
        #ACN_used += volume
        state = open("state.txt","w")
        state.write("Bulk_dT")
        state.close()
        self.linear_wait()
        
        retraction = 150
        
        ##############충전##############       

        self.syringe_wait(dT)
        dT.write(b'/1I6R\r\n')
        self.syringe_wait(dT)
        dT.write(b'/1V4000I6A300R\r\n')
        self.syringe_wait(dT)
        dT.write(b'/1I5R\r\n')
        self.syringe_wait(dT)
        dT.write(b'/1V4000I5A600R\r\n')
        self.syringe_wait(dT)
        dT.write(b'/1I6R\r\n')
        self.syringe_wait(dT)
        dT.write(b'/1V4000I6A900R\r\n')
        self.syringe_wait(dT)
        dT.write(b'/1I5R\r\n')
        self.syringe_wait(dT)
        dT.write(b'/1V4000I5A1200R\r\n')
        self.syringe_wait(dT)
        dT.write(b'/1I6R\r\n')
        self.syringe_wait(dT)
        dT.write(b'/1V4000I6A1500R\r\n')
        dT.write(b'/1I5R\r\n')
        self.syringe_wait(dT)
        dT.write(b'/1V4000I5A1800R\r\n')
        self.syringe_wait(dT)
        dT.write(b'/1I6R\r\n')
        self.syringe_wait(dT)
        dT.write(b'/1V4000I6A2100R\r\n')
        dT.write(b'/1I5R\r\n')
        self.syringe_wait(dT)
        dT.write(b'/1V4000I5A2400R\r\n')
        self.syringe_wait(dT)
        dT.write(b'/1I6R\r\n')
        self.syringe_wait(dT)
        dT.write(b'/1V4000I6A2700R\r\n')
        dT.write(b'/1I5R\r\n')
        self.syringe_wait(dT)
        dT.write(b'/1V4000I5A3000R\r\n')
        
        ################################
        

        ##########밸브 포트 설정##########
        self.syringe_wait(dT)
        dT.write(b'/1I7R\r\n')
        ##################################

        ###############분사###############
        self.linear_wait() # linear가 분사위치에 도착할 때까지 기달
        start = time.time() 
        

            
        self.syringe_wait(dT)
        dT.write(b'/1I7V1000A0R\r\n')
        ###################################
            

        #다시 살짝 빨아들임
        self.syringe_wait(dT)
        dT.write(b'/1V100I7A'+str(int(retraction)).encode()+b'R\r\n')
        end = time.time()
        try:
            self.wait(120)
            pass
        except:
            pass





    
    def wash(self, volume, incubation, cycle):
        threading.Thread(target=self.check_point,args = (cycle, "wash",)).start()
        state = open("state.txt","w")
        state.write("Wash")
        state.close()
        self.linear_wait()
        time.sleep(7)

        self.wait(incubation)

    def oxidation(self, volume, incubation, cycle):
        threading.Thread(target=self.check_point,args = (cycle, "oxidation",)).start()
        state = open("state.txt","w")
        state.write("Oxidation")
        state.close()
        self.linear_wait()
        time.sleep(7)

        self.wait(incubation)
    
    def wash_no_use(self, volume,incubation, cycle):
        threading.Thread(target=self.check_point,args = (cycle, "wash",)).start()

        #global ACN_used
        #ACN_used += volume
        
        

        retraction = 0

        ##############충전##############       
        step = int(volume*600) + retraction

        #최대 6000 step
        if step > 6000:
            step = 6000

        self.syringe_wait(ACN)
        ACN.write(b'/1I2R\r\n')
        self.syringe_wait(ACN)
        ACN.write(b'/1V4000I2A'+str(step).encode()+b'R\r\n') ###### 7월 29일. 4를 5로 바꾸세요
        ################################

        state = open("state.txt","w")
        state.write("Wash")
        state.close()
        
        #wash는 항상 1000
        speed = 1000
        
        time.sleep(1.5)
        ##########밸브 포트 설정##########
        self.syringe_wait(ACN)
        ACN.write(b'/1I6R\r\n')
        
        ##################################

        ###############분사###############
        self.linear_wait() # linear가 분사위치에 도착할 때까지 기달
        self.syringe_wait(ACN)

        ACN.write(b'/1V2000I6A0R\r\n')

        '''
        ACN.write(b'/1V500I6A800R\r\n')
        self.syringe_wait(ACN)
        self.waste(6000, 10)

        
        ACN.write(b'/1V500I6A0R\r\n')

        '''
        
        #다시 살짝 빨아들임
        self.syringe_wait(ACN)
        ACN.write(b'/1V500I6A'+str(int(retraction)).encode()+b'R\r\n')
        

        #self.waste(6000, 10)
        #self.waste(6000, 10)
        #self.waste(6000, 10)

        try:
            self.wait(1)
            pass
        except:
            pass


    
    def oxidation_no_use(self, volume,incubation, cycle):
        threading.Thread(target=self.check_point,args = (cycle, "oxidation",)).start()

        #global oxidation_used
        #oxidation_used += volume
        
        state = open("state.txt","w")
        state.write("Oxidation")
        state.close()

        retraction = 600


        
        for i in range(0,5):
            ##############충전##############       
            step = int(volume*600) + retraction

            #최대 6000 step
            if step > 6000:
                step = 3000

            step = 3000
            self.syringe_wait(Oxidizer)
            Oxidizer.write(b'/1I1R\r\n')
            self.syringe_wait(Oxidizer)
            Oxidizer.write(b'/1V3000I1A'+str(3000).encode()+b'R\r\n') ###### 7월 29일. 5를 6으로 바꾸세요
            ################################


            #incubation 시간에 맞게 속도 조절. 너무 빠르면 안되니 최대 속도는 1000
            speed = int(step/incubation)*2
            if speed > 1000:
                speed = 1000

            

            ##########밸브 포트 설정##########
            self.syringe_wait(Oxidizer)
            Oxidizer.write(b'/1I3R\r\n')
            ##################################


            ###############분사###############
            self.linear_wait() # linear가 분사위치에 도착할 때까지 기달
            start = time.time()
            
            #1000 step은 일단 빠르게 뿌림
            if step >= 1000:



                self.syringe_wait(Oxidizer)
                Oxidizer.write(b'/1I3V1000A0R\r\n')
                


            else:
                
                self.syringe_wait(Oxidizer)
                Oxidizer.write(b'/1I3V1000A0R\r\n')

            ###################################

            #self.waste(1000, 4)
            
            
            #state = open("state.txt","w")
            #state.write("Oxidation_move")
            #state.close()

        

        #다시 살짝 빨아들임
        self.syringe_wait(Oxidizer)
        Oxidizer.write(b'/1V1000I3A'+str(int(retraction)).encode()+b'R\r\n')

        
        end = time.time()
        try:
            self.wait(incubation-(end-start))
        except:
            pass

        #self.waste(6000, 10)

        


    def detritylation(self, volume,incubation, cycle):
        threading.Thread(target=self.check_point, args = (cycle, "detritylation",)).start()
        
        #global deblock_used
        #deblock_used += volume
        
        state = open("state.txt","w")
        state.write("Detritylation")
        state.close()

        retraction = 500

        
        ##############충전##############       
        step = int(volume*600) + retraction

        #최대 6000 step
        if step > 6000:
                
            step = 3000


        self.syringe_wait(Deblock)
        Deblock.write(b'/1I3R\r\n')
        self.syringe_wait(Deblock)
        Deblock.write(b'/1V1500I3A'+str(1000).encode()+b'R\r\n')
        self.wait(1)
        ################################


        #incubation 시간에 맞게 속도 조절. 너무 빠르면 안되니 최대 속도는 1000
        speed = int(step/incubation*2.5)
        if speed > 1000:
            speed = 1000

        time.sleep(1)
        ##########밸브 포트 설정##########
        self.syringe_wait(Deblock)
        Deblock.write(b'/1I4R\r\n')
        ##################################

        ###############분사###############
        self.linear_wait() # linear가 분사위치에 도착할 때까지 기달
        start = time.time()

        Deblock.write(b'/1I7V100A0R\r\n')
        '''
        self.syringe_wait(ACN)
        ACN.write(b'/1I4V1000A600R\r\n')

        self.syringe_wait(ACN)        
        self.waste(500, 5)
        ACN.write(b'/1I4V1000A300R\r\n')
        self.syringe_wait(ACN)        
        self.waste(500, 10)

        ACN.write(b'/1I4V1000A0R\r\n')
        self.syringe_wait(ACN)
        '''
        
        #다시 살짝 빨아들임
        self.syringe_wait(Deblock)
        Deblock.write(b'/1V1000I7A'+str(int(300)).encode()+b'R\r\n')
        self.syringe_wait(Deblock)
        Deblock.write(b'/1I3R\r\n')
       

        
        end = time.time()
        try:
            self.wait(incubation-(end-start))
        except:
            pass
        #self.Sblow(0,0)
        #self.linear_wait()
        #self.moving(2500)
        #self.linear_wait()
        #self.waste(6000, 10)


    ###################################################

    def syringe_wait(self, syringe):

        msg = syringe.readline()
        while (msg.find(b'`') == -1):

            syringe.write(b'/1Q\r\n')
            time.sleep(0.1)
            msg = syringe.readline()

    
    def linear_wait(self):

        while(1):
            self.wait(0.01)
            state = open("state.txt","r")
            if state.readline() == "Done":
                break
            state.close()

    
            
    def load_sequence(self,path):
        file_sequence = open(path,'r')
        _5to3_lines = file_sequence.readlines()
        _3to5_lines = _5to3_lines[1][::-1]
        return _3to5_lines
        
    
    def load_protocol(self,path):
        is_error = 0
        file_protocol = open(path,'r')
        lines = file_protocol.readlines()
        list_protocol = []
        for line in lines:
            step = line.split('\t')
            list_protocol.append(step)
            
        step_num = 0
        for step in list_protocol:
            step_num += 1
            if step[0] != 'oxidation':
                if step[0] != 'coupling':
                
                    if step[0] != 'wash':
                         if step[0] != 'blow':
                             if step[0] != 'detritylation':
                                  is_error = 1
                                  print("LOAD ERROR 1")
        
            try:
                int(step[1])
                
            except:
                is_error = 2
                print("LOAD ERROR 2")
    
            try:
                int(step[2])
                
            except:
                is_error = 3
                print("LOAD ERROR 3")
                
        return list_protocol,is_error
    
    
    
    def save_protocol(self,path,list_protocol):
        print(path)
        print(list_protocol)
        file_protocol = open(path+'.protocol','w')
    
        for step in list_protocol:
            for i in step:
                file_protocol.write(str(i)+'\t')
            file_protocol.write('\n')
    
        file_protocol.close()

    
    
    def check_point(self,cycle, step):
        global progress_step 
        progress_step = step
        print(time.strftime('%y-%m-%d\t%H:%M:%S',time.localtime(time.time())) +'\t'+ str(cycle+1) +"\t"+step)
        try:
            synthesis_log_txt = open(synthesis_log_path+'.txt','a')
            synthesis_log_txt.write(time.strftime('%y-%m-%d\t%H:%M:%S',time.localtime(time.time()))+"\t"+str(cycle+1)+'\t'+step+"\n")

            try:
                winsound.PlaySound(sound_path+'\\'+step+'.wav',winsound.SND_ALIAS)

            except Exception as e:
                print('e ', e)
                print("sound error")
                synthesis_log+txt.write("ERROR: sound error\n")
        except Exception as e:
            print('e ', e)
            print("log error")

    def get_humidity(self):
        state = open("state.txt","r")
        humidity = state.read()
        state.close()

        return humidity
        


class Draw():
    x1, x2, y1, y2 = -1, -1, -1, -1
    src, tmp_img = None, None
    drawing = False
    width, height = 242, 142
    edge = 0
    x_gap = 0
    y_gap = 0



    def move_linear_to_mouse(self,event, x, y, flags, param):

        global linear

        #linear.write(b'x_init;')
        #linear.write(b'x6500;')

        if event == cv2.EVENT_LBUTTONDOWN:
            self.x1, self.y1 = x, y
    
            x_center = 640 / 2
    
            self.x_gap = self.x1 - x_center  # 이미지 내에서 클릭한 지점과 center간의 차이 구함
    
            convert_value = 0.95  # 이미지 내의 픽셀 값과 linear아두이노의 pulse값 간의 보정계수
            distance = int(self.x_gap * convert_value)
            linear.read_all()
            linear.write(b'position;')
            now_position = int(linear.readline().decode())
            goal_position = distance + now_position
            print(now_position, goal_position)
            command = 'x' + str(goal_position) + ';'
            linear.write(command.encode())

    
    
    def draw_line_mouse(self,event, x, y, flags, param):
    
        # 마우스 클릭
        if event == cv2.EVENT_LBUTTONDOWN:
    
            self.drawing = True
            self.x1, self.y1 = x, y
    
        # 마우스 드래그
        elif event == cv2.EVENT_MOUSEMOVE:
    
            if self.drawing == True:

                cv2.line(param, (self.x1, self.y1), (x, y), (255, 255, 255), 1)
                self.angle = (self.y1 - y) / (x - self.x1)
                self.degree_angle = np.arctan2(self.angle, 1) * 180 / math.pi
                cv2.putText(param, str(self.degree_angle), (x, y), cv2.FONT_HERSHEY_COMPLEX, 0.4, (0, 255, 0), 1)

                cv2.imshow('angle manual',param)

        # 마우스 클릭 땔 때
        elif event == cv2.EVENT_LBUTTONUP:
    
            self.drawing = False
            cv2.line(param, (self.x1, self.y1), (x, y), (255, 255, 255), 1)
            self.x2, self.y2 = x, y
            self.angle = (self.y1 - y) / (x - self.x1)
            cv2.putText(param, str(self.angle), (x, y), cv2.FONT_HERSHEY_COMPLEX, 0.4, (0, 255, 0), 1)

            cv2.imshow('angle manual', param)


    
    def get_angle_manual(self,img_path):
        '''
        try:
            self.x1, self.x2, self.y1, self.y2
            cap = cv2.VideoCapture(0)
            if cap.isOpened():
                print("카메라 연결")

            while True:
                ret, fram = cap.read()
                cv2.namedWindow("angle manual")
                cv2.setMouseCallback("angle manual", self.draw_line_mouse, fram)

                if ret:
                    #cv2.imshow('angle manual', fram)
                    k = cv2.waitKey(1) & 0xFF
                    if k == 27:
                        break
                else:
                    print("error")

            cap.release()
            cv2.destroyAllWindows()
        except Exception as E:
            print(E)
            '''
        try:
            self.degree_angle = 0
            self.make_img('test.txt',self.degree_angle) #여기서 한번에
        except Exception as E:
            print(E)



    
    def move_origin_manual(self):
        try:
            global x1, y1
            print("1")
            cap = cv2.VideoCapture(1)
            print("2")
            if cap.isOpened():
                print("카메라 연결")

            while True:
                ret, fram = cap.read()
                cv2.namedWindow("origin manual")
                cv2.setMouseCallback("origin manual", self.move_linear_to_mouse, fram)

                if ret:

                    cv2.imshow('origin manual', fram)
                    k = cv2.waitKey(1) & 0xFF
                    if k == 27:
                        break
                else:
                    print("error")

            cap.release()
            cv2.destroyAllWindows()
        except Exception as E:
            print(E)

    
    def make_img(self):
        degree_angle = 0
        color_space = self.get_color_space(sequence_path)

        width = 24840  # wafer 가로 24.84mm (etching 후 실측 값)
        height = 14840  # wafer 세로 14.84mm (etching 후 실측 값)
        pixel = 137.1  # nozzle간 간격 = pixel간 간격 = 137.1um
        well = 200  # well의 크기 = 200x200um
        CtoC = 1371  # well의 중심간 간격 = 1mm
        blank = 1717.5  # wafer에서 첫 well까지의 여백 #1.7175mm
        well_x_num = 16 # wafer에서 가로쪽으로 well 갯수
        well_y_num = 9 # wafer에서 세로쪽으로 well 갯수
        glass = 75200 # glass의 가로 길이 실측값
        pixel_glass = glass/pixel # glass의 가로길이를 pixel로 나눈 값. 나중에 더 계산적으로 바꿔야지

        pixel_width = width/pixel
        pixel_height = height/pixel
        pixel_well = well/pixel
        pixel_CtoC = CtoC/pixel
        pixel_blank = blank/pixel
    
        x_first = self.edge+150 # wafer에서 첫 well의 시작점
        y_first = self.edge+150 # wafer에서 첫 well의 시작점
        #########################


        # 가운데 정렬 하는법. start = (width -컬럼갯수(줄수)*CtoC)/2
    
        img = np.zeros((128, int(glass/pixel), 3), np.uint8)
        img = cv2.rectangle(img, (0, 0), (int(glass/pixel), 128), (255, 255, 255), -1) #배경을 흰색으로
        img = cv2.rectangle(img,(0,0),(int(glass/pixel)-1,128-1),(0,0,0),2) # glass에 딱 맞는 테두리
        wafer_start = (int((glass/2 - width/2)/pixel),int(((128/2)*pixel-height/2)/pixel))
        wafer_end = (int((glass/2 + width/2)/pixel),int(((128/2)*pixel+height/2)/pixel))
        print(wafer_start,wafer_end)
        img = cv2.rectangle(img,wafer_start,wafer_end,(0,0,0), 1)

        for z in range(0, 1):  # 시퀀스 길이
            for column in range(0, well_x_num):  # 컬럼갯수
                for row in range(0, well_y_num):  # 줄 수
                    x_center = int((blank + column * CtoC + well/2 + glass/2 - width/2) / pixel)
                    y_center = int((blank + row * CtoC + well/2 + (128/2)*pixel - height/2) / pixel) + 3 # 2를 왜 더해야 중앙에 가는지는 모르겠음
                    #img = cv2.rectangle(img, (x_center-2,y_center-2), (x_center+2,y_center+2), color_space[row][column][z], -1)
                    img = cv2.rectangle(img, (x_center-1,y_center-4), (x_center+1,y_center-2), (0,0,0), -1)


            rotated_img = self.image_rotate(img, degree_angle)



            ret, rotated_img_binary = cv2.threshold(rotated_img, 150, 255, cv2.THRESH_BINARY) #이미지를 이진화

            #cv2.imshow('show',rotated_img_binary)
            '''
            #################### 십자가 만드는 코드
            img = np.zeros((128, int(glass / pixel), 3), np.uint8)
            cv2.rectangle(img,(0,0),(int(glass/pixel),128),(255,255,255),-1)
            cv2.line(img,(40,10),(40,90),(0,0,0),1)
            cv2.line(img,(10,50),(90,50),(0,0,0),1)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            ret, rotated_img_binary = cv2.threshold(img, 150, 255, cv2.THRESH_BINARY)  # 이미지를 이진화
            ####################
            '''
            cv2.imwrite(str(3) + 'st_base.png', rotated_img_binary, [cv2.IMWRITE_PNG_BILEVEL, 1]) #open cv는 이미지를 bmp형식으로 저장할 수 없음. 일단 png로 저장

            ##### 1bit png로 저장한거를 bmp형식으로 바꿈######
            file_in = str(3) + "st_base.png"
            img = Image.open(file_in)
            img_resize = img.resize((img.width, img.height*10))

            file_out = (str('T')) + '_bmp' ".bmp" #인쇄하는데 쓸 최종 이미지
            img_resize.save(file_out)
            img.save("noresize.bmp")
            ##########################################

            cv2.waitKey(0)
            cv2.destroyAllWindows()
        
        
    def image_rotate(self, img, degree_angle):
        ################색깔을 반전시킴##################
        gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) # 흑백으로 전환 코드
        cv2.imwrite('gray_image.png', gray_image)

        inverse_img = 255 - gray_image.copy()  # 색상 반전 코드

        ############카메라에서 계산한 각도 + Xaar에서 자동으로 회전하는 90도를 보상하기 위해 -90 회전#############
        height, width = inverse_img.shape


        matrix = cv2.getRotationMatrix2D((height / 2, height / 2), -90+degree_angle, 1)

        rotated_img = cv2.warpAffine(inverse_img, matrix, (int(height), int(width)))


        #다시 색깔 뒤집고
        rotated_img_out = 255 - rotated_img.copy()


        return rotated_img_out
        
        
    def get_color_space(self,sequence_file_path):
        sequence_space = self.get_sequence_space(sequence_file_path)
        color_space = []

        # clolor 설정

        cyan = (255, 255, 0, 255)
        magenta = (255, 0, 255, 255)
        yellow = (0, 255, 255)
        black = (0, 0, 0)
        white = (255, 255, 255)


        A = cyan
        T = magenta
        G = yellow
        C = black

        for sequence_list in sequence_space:
            color_list = []
            for sequence in sequence_list:
                seqTocolor = []
                for base in sequence:

                    if base == 'A':
                        seqTocolor.append(A)
                    if base == 'T':
                        seqTocolor.append(T)
                    if base == 'G':
                        seqTocolor.append(G)

                    if base == 'C':
                        seqTocolor.append(C)
                color_list.append(seqTocolor)
            color_space.append(color_list)
        return color_space


    def get_sequence_space(self,sequence_file_path):
        sequence_space = []

        file = open(sequence_file_path)

        lines = file.readlines()
        for line in lines:
            sequence_list = line.replace('\n', '').split('\t')
            sequence_space.append(sequence_list)

        return sequence_space




#test=System()
#test.syringe_init()
#test.bulk_dT(1,10)
