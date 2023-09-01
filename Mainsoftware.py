import datetime
import os
import threading
import cv2
import numpy as np
import sys
import PyQt5
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QPixmap, QImage
import time
import serial
import OpenIDS_sys
import sys
import subprocess
import KJH_SSH
import math
import random


#######camera tab을 구성하는 calss#######
class CameraTab(QWidget):

    def __init__(self):
        super().__init__()

        cent = QDesktopWidget().availableGeometry().center()  # Finds the center of the screen
        self.setStyleSheet("background-color: white;")
        self.resize(1000, 900)
        self.frameGeometry().moveCenter(cent)
        self.initWindow()
        
        change_pixmap_signal = pyqtSignal(np.ndarray)
        self.calibration_thread = OpenIDS_sys.Calibration(change_pixmap_signal)
        self.calibration_thread.start()
        self.calibration_thread.set_label(self.image_label,self.zoom_image_label)



    def initWindow(self):

        self.position_save_btn = QPushButton(self)
        self.position_save_btn.setText('save')
        self.position_save_btn.resize(70, 20)

        self.position_save_btn.move(950, 5)
        self.position_save_btn.clicked.connect(self.position_save)
        
        self.printing_position = QLineEdit(self)
        self.printing_position.resize(70, 20)

        self.printing_position.move(860, 20)
        
        self.img_btn = QPushButton(self)
        self.img_btn.setText('make img')
        self.img_btn.resize(70, 20)

        self.img_btn.move(860, 5)
        self.img_btn.clicked.connect(self.MakeIMG)

        self.ss_video = QPushButton(self)
        self.ca_video = QPushButton(self)
        self.ss_video.setText('test Printing')
        self.ca_video.setText('Calibration')


        self.angle_lbl = QLabel('ANGLE:',self)
        self.angle_lbl.move(820, 255)
        self.angle_lbl.resize(70,20)
        self.get_angle = QLineEdit(self)
        self.get_angle.move(870,250)
        self.get_angle.resize(40,30)

        self.x_move  = QLabel('X:', self)
        self.x_move.move(820, 305)
        self.x_move.resize(70,20)
        self.x_move_set = QLineEdit(self)
        self.x_move_set.move(870,300)
        self.x_move_set.resize(40,30)

        self.y_move  = QLabel('Y:', self)
        self.y_move.move(820, 355)
        self.y_move.resize(70,20)
        self.y_move_set = QLineEdit(self)
        self.y_move_set.move(870,350)
        self.y_move_set.resize(40,30)


        self.ss_video.move(820, 100)
        self.ca_video.move(820, 150)
        self.ss_video.resize(120, 40)
        self.ca_video.resize(120, 40)
        self.ss_video.clicked.connect(self.TestPrinting)
        self.ca_video.clicked.connect(self.ClickCalibration)

        self.set_size = QLineEdit(self)
        self.set_size.move(870, 200)
        self.set_size.resize(40, 30)
        self.set_size.setText('7')

        self.set_text = QLabel("SIZE:", self)
        self.set_text.move(820, 205)
        self.set_text.resize(40, 20)

        self.image_label = QLabel(self)
        self.dispaly_width = int(800)
        self.display_height = int(600)
        self.image_label.resize(self.dispaly_width, self.display_height)
        self.image_label.move(5, 5)

        self.humidity_label = QLabel(self)
        self.humidity_label.move(820,500)

        try:
            my_thread = threading.Thread(target=self.get_humidity_thread, args=())

            my_thread.daemon = True  # 프로그램 종료 시 프로세스도 종료

            my_thread.start()
        except:
            self.humidity_label.setText("humidity error")

        ################################################
        self.image_label.mousePressEvent = self.show_zoom
        self.image_label.mouseMoveEvent = self.getPos
        self.image_label.mouseReleaseEvent = self.stop_zoom
        #################################################

        self.zoom_image_label = QLabel(self)


    def get_humidity_thread(self):
        while(1):
            humidity = system.get_humidity()
            self.humidity_label(humidity)
            time.sleep(1)

    def position_save(self):
        state = open("printing_start_position.txt","w")
        state.write(self.printing_position.text())
        state.close()


    def getPos(self, event):
        
        x = int(event.pos().x())
        y = int(event.pos().y())
        self.calibration_thread.set_pos(x, y, True)
        self.zoom_image_label.resize(300, 300)

    def show_zoom(self, event):
        x = int(event.pos().x())
        y = int(event.pos().y())
        self.calibration_thread.set_pos(x, y, True)
        self.zoom_image_label.resize(300, 300)


    def stop_zoom(self, event):
        self.calibration_thread.set_pos(0, 0, False)
        self.zoom_image_label.resize(0, 0)


    def MakeIMG(self):
        print('이미지 제작')
        try:
            draw.make_img()
        except Exception as E:
            print(E)

    def TestPrinting(self):
            for i in range(0,100):
                print("now : "+str(i))
                state = open("state.txt","w")
                state.write("Print")
                state.close()
                time.sleep(10)

    def ClickCalibration(self):
        try:
            
            global main_gui
            self.ca_video.clicked.disconnect(self.ClickCalibration)
            self.ca_video.setText('Stop Calibration')

            self.calibration_thread.well_size = int(self.set_size.text())
        
            
            self.calibration_thread.main_gui = main_gui
            self.calibration_thread._run_flag = True

            
            self.ca_video.clicked.connect(self.ClickStop_CalibrationVideo)
        except Exception as E:
            print(E)


    def ClickStop_CalibrationVideo(self):
        try:
            self.ca_video.setText('Calibration')
            self.ca_video.clicked.connect(self.ClickCalibration)
            self.calibration_thread._run_flag = False
        except Exception as E:
            print(E)



#######charging tab을 구성하는 class#######
class ManualTab(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()


    def initUI(self):


#####수동 리니어 조절 관련#####
        print_btn = QPushButton('print', self)
        print_btn.move(550,120)
        print_btn.clicked.connect(self.printing_thread)

        stop_btn = QPushButton('stop', self)
        stop_btn.move(550,510)
        stop_btn.clicked.connect(self.stop_btn_clicked)

        position = QLabel('position : ', self)
        position.move(120,65)
        
        self.add_position = QLineEdit(self)
        self.add_position.move(200,60)

        move_btn = QPushButton('move', self)
        move_btn.move(390,60)
        move_btn.clicked.connect(self.move_btn_clicked)
        
        line = QLabel(' ---------------------------------------------------------------------------------------------------------------', self)
        line.move(0,160)

#####charging 관련######
        Charge_Label = QLabel('Charge : ',self)
        Charge_Label.move(30,200)

        Push_Label = QLabel('Push',self)
        Push_Label.move(50,250)

        set_position = QLineEdit(self)
        set_position.move(100,195)

        Act_Push_btn = QPushButton('Act' , self)
        Act_Push_btn.move(20,300)
        Act_Push_btn.clicked.connect(self.Act_push)
      
        A_Push_btn = QPushButton('A' , self)
        A_Push_btn.move(110,300)
        A_Push_btn.clicked.connect(self.A_push)

        T_Push_btn = QPushButton('T' , self)
        T_Push_btn.move(200,300)
        T_Push_btn.clicked.connect(self.T_push)

        C_Push_btn = QPushButton('C' , self)
        C_Push_btn.move(290,300)
        C_Push_btn.clicked.connect(self.C_push)

        ACN_Push_btn = QPushButton('ACN', self)
        ACN_Push_btn.move(380,300)
        ACN_Push_btn.clicked.connect(self.ACN_push)

        Oxidizer_Push_btn = QPushButton('Oxidizer', self)
        Oxidizer_Push_btn.move(470,300)
        Oxidizer_Push_btn.clicked.connect(self.Oxidizer_push)

        Deblock_Push_btn = QPushButton('Deblock', self)
        Deblock_Push_btn.move(560,300)
        Deblock_Push_btn.clicked.connect(self.Deblock_push)


        Blow_Push_btn = QPushButton('Blow', self)
        Blow_Push_btn.move(650,300)
        Blow_Push_btn.clicked.connect(self.Blow_push)

        waste_Push_btn = QPushButton('Waste', self)
        waste_Push_btn.move(740,300)
        waste_Push_btn.clicked.connect(self.Waste_push)

        Pull_Label = QLabel('Pull',self)
        Pull_Label.move(50,400)

        Act_Pull_btn = QPushButton('Act' , self)
        Act_Pull_btn.move(20,450)
        Act_Pull_btn.clicked.connect(self.Act_pull)

        A_Pull_btn = QPushButton('A' , self)
        A_Pull_btn.move(110,450)
        A_Pull_btn.clicked.connect(self.A_pull)

        T_Pull_btn = QPushButton('T' , self)
        T_Pull_btn.move(200,450)
        T_Pull_btn.clicked.connect(self.T_pull)

        C_Pull_btn = QPushButton('C' , self)
        C_Pull_btn.move(290,450)
        C_Pull_btn.clicked.connect(self.C_pull)

        
        Act_flush_btn = QPushButton('Act' , self)
        Act_flush_btn.move(20,600)
        Act_flush_btn.clicked.connect(self.Act_flush)

        A_flush_btn = QPushButton('A' , self)
        A_flush_btn.move(110,600)
        A_flush_btn.clicked.connect(self.A_flush)

        T_flush_btn = QPushButton('T' , self)
        T_flush_btn.move(200,600)
        T_flush_btn.clicked.connect(self.T_flush)

        




        self.show()

    def Act_flush(self):
        system.flush("Act_Flush")       

    def A_flush(self):
        system.flush("A_Flush")

    def T_flush(self):
        system.flush("T_Flush")
        


    def move_btn_clicked(self):

        system.moving(self.add_position.text())
        
        
    def stop_btn_clicked(self):
        sys.exit()


    def printing_thread(self): ##인쇄를 실행하는 쓰레드. printing 함수를 쓰레드로 실행해줌
        try:
            my_thread = threading.Thread(target=system.printing_both(-1,-1), args=())

            my_thread.daemon = True  # 프로그램 종료 시 프로세스도 종료

            my_thread.start()

        except Exception as E:
            print(E)

            
    

    def print_position(self):
        self.set_position.text()


    def ACN_push(self):
        try:
            system.wash(5,10,-1)

        except Exception as E:
            print(E)
            print('ACN 연결 확인하세요')

            
    def Deblock_push(self):
        try:
            system.detritylation(5,10,-1)

        except:
            print('Deblock 연결 확인하세요')

    def Blow_push(self):
        try:
            system.blow(10,10,-1)

        except:
            print('Blow 연결 확인하세요')

    def Waste_push(self):
        try:
            system.waste(3000,10)

        except:
            print('Waste 연결 확인하세요')
    def Oxidizer_push(self):
        try:
            system.oxidation(10,10,-1)

        except:
            print('Oxidizer 연결 확인하세요')

    def Act_push(self):
        try:
            system.ink_manual_move("aATact+;")
        except:
            print("Act 연결 확인하세요")

    def A_push(self):
        try:
            system.ink_manual_move("aATA+;")
        except:
            print("A 연결 확인하세요")

    def T_push(self):
        try:
            system.ink_manual_move("aATT+;")

        except:
            print('T 연결 확인하세요')


    def G_push(self):
        try:
            system.ink_manual_move("wGCG+;")
        except:
            print("G 연결 확인하세요")

    def C_push(self):
        try:
            system.ink_manual_move("wGCC+;")

        except:
            print('C 연결 확인하세요')


    def ACN_pull(self):
        try:
            self.ACN.write(('-x'+str(self.set_position.text())+';').encode('utf-8'))

        except:
            print('ACN 연결 확인하세요')
        
    def Deblock_pull(self):
        try:
            self.Deblock.write(('-x'+str(self.set_position.text())+';').encode('utf-8'))

        except:
            print('Deblock 연결 확인하세요')

    def Oxidizer_pull(self):
        try:
            self.Oxidizer.write(('-x'+str(self.set_position.text())+';').encode('utf-8'))

        except:
            print('Oxidizer 연결 확인하세요')


    def Act_pull(self):
        try:
            system.ink_manual_move("aATact-;")
        except Exception as E:
            print(E)
            print("Act 연결 확인하세요")

    def A_pull(self):
        try:
            system.ink_manual_move("aATA-;")
        except Exception as E:
            print(E)
            print("A 연결 확인하세요")
    def T_pull(self):
        try:
            system.ink_manual_move("aATT-;")

        except:
            print('T 연결 확인하세요')

    def G_pull(self):
        try:
            system.ink_manual_move("wGCG-;")
        except Exception as E:
            print(E)
            print("G 연결 확인하세요")
    def C_pull(self):
        try:
            system.ink_manual_move("wGCC-;")

        except:
            print('C 연결 확인하세요')

class SynthesisTab(QWidget):
    
    def __init__(self):
        super().__init__()
        self.list_protocol = []
        ####################################
        ####################################
        self.oligo_size = 15
        ####################################
        ###################################
        self.setupUI()
        self.check_system()
        
    def setupUI(self):
        #합성할 시퀀스
        self.label_sequence = QLabel('sequence:' , self)
        self.label_sequence.move(50,450)
        btn_Sequence = QPushButton('...' , self)
        btn_Sequence.move(15,445)
        btn_Sequence.resize(30,20)
        btn_Sequence.clicked.connect(self.btn_Sequence_clicked)

        
        #Syringe pump 연결표시
        label_pumps = QLabel('Fluidics connection' ,self)
        label_pumps.move(40,30)
        
        self.label_ACN_pump = QLabel('ACN pump is not connected',self)
        self.label_ACN_pump.move(50,50)
        self.label_ACN_pump.setStyleSheet('Color : red')
        
        self.label_oxidation_pump = QLabel('Oxidation pump is not connected',self)
        self.label_oxidation_pump.move(50,70)
        self.label_oxidation_pump.setStyleSheet('Color : red')
        
        self.label_deblock_pump = QLabel('Deblock pump is not connected',self)
        self.label_deblock_pump.move(50,90)
        self.label_deblock_pump.setStyleSheet('Color : red')
        
        self.label_arduino = QLabel('Arduino is not connected',self)
        self.label_arduino.move(50,110)
        self.label_arduino.setStyleSheet('Color : red')




        #합성할 oligo 길이
        self.label_oligo_size = QLabel('Oligo size: ',self)
        self.label_oligo_size.move(50,480)
        

        #합성 시작 버튼
        self.btn_run = QPushButton('Run',self)
        self.btn_run.move(500,500)
        self.btn_run.setEnabled(False)
        self.run_state = 'Ready'
        self.btn_run.clicked.connect(self.synthesis_thread)


        
        #####합성 프로토콜 영역#####
        self.label_Protocol = QLabel('-Synthesis protocol-',self)
        self.label_Protocol.move(60,175)
        self.label_Protocol_name = QLabel('',self)
        btn_protocol_load = QPushButton('...',self)
        btn_protocol_load.move(15,170)
        btn_protocol_load.resize(30,20)
        btn_protocol_load.clicked.connect(self.btn_protocol_load_clicked)

        self.table = QTableWidget(self)
        self.table.move(40,200)
        self.table.resize(340,200)
        self.table.setColumnCount(3)
        self.table.setRowCount(10)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        self.table.setHorizontalHeaderLabels(['step', 'volume', 'incubation time']) # 열 제목 지정
        self.table.setSelectionBehavior(QTableView.SelectRows)
        




        
        #self.table.resizeColumnsToContents()


        #합성 진행상황
        self.label_status = QLabel("-Status-")
        self.label_now_cycle = QLabel('Cycle: ')
        self.label_now_step = QLabel('Step: ')
        


        self.show() #창을 보여준다.

    def btn_Sequence_clicked(self):
        file_name = QFileDialog.getOpenFileName(self, self.tr("Road Data files"), "./", self.tr("Sequence Files (*.txt);; All Files(*.*)"))[0]
        print(file_name)
        if file_name == '':
            return

        self.str_sequence = system.load_sequence(file_name)

        self.label_sequence.setText('sequence: '+self.str_sequence)

        

    def btn_PRT_clicked(self):


        path = str(QFileDialog.getExistingDirectory(self, "Select PRT Directory"))
        if path == '':
            return
        self.label_PRT.setText(path)

        list_file = os.listdir(path)
        list_file = [file for file in list_file if file.endswith(".prt")] #prt만 필터링
        #빠진파일 있는지 검사
        for i in range(0,len(list_file)):
            if list_file.find(str(i+1)+'st') ==-1:
                msg = QMessageBox()
                msg.setWindow("Warning")
                msg.setText(str(i+1)+'st base file is not exist')
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
        self.oligo_size = len(list_file)
        self.label_oligo_size.setText('Oligo size: ' + str(self.oligo_size))

    def btn_protocol_edit_clicked(self):
        self.widget_protocol = Win_protocol()

        #ex = Win_protocol()


        self.widget_protocol.show()



    def btn_protocol_load_clicked(self):
        
        self.table.clear()
        file_name = QFileDialog.getOpenFileName(self, self.tr("Road Protocol files"), "./x64/Release/protocol", self.tr("Protocol Files (*.protocol);; All Files(*.*)"))[0]
        print(file_name)
        if file_name == '':
            return
        list_protocol,is_error = system.load_protocol(file_name)
        self.table.setRowCount(len(list_protocol))
        for i in range(0,self.table.rowCount()):
            for j in range(0,self.table.columnCount()):
                try:
                    self.table.setItem(i,j,QTableWidgetItem(list_protocol[i][j]))
                except:
                    pass
        print(is_error)
        #protocol에 에러가 있으면 에러 알림 띄움
        '''
        if is_error == 1:
            protocol_error_msg = QMessageBox(self,title = 'Protocol Error', message = 'step' + step_num + ' name is wrong')
        if is_error == 2:
            protocol_error_msg = QMessageBox(self,title = 'Protocol Error', message = 'step' + step_num + ' volume is wrong')
        if is_error == 3:
            protocol_error_msg = QMessageBox(self,title = 'Protocol Error', message = 'step' + step_num + ' incubation time is wrong')
        '''

        if len(list_protocol)>0:
            self.list_protocol = list_protocol
            self.btn_run.setEnabled(True)
            self.label_Protocol_name.setText(file_name)

    def synthesis_thread(self): ##합성을 실행하는 쓰레드. synthesis 함수를 쓰레드로 실행해줌
        try:
            my_thread = threading.Thread(target=self.synthesis, args=())

            my_thread.daemon = True  # 프로그램 종료 시 프로세스도 종료

            my_thread.start()

        except Exception as E:
            print(E)

    def circle(self):
        # 0~9까지 가우시안 필터로 흐리게 만들어 조절함.
        blur_img = cv2.GaussianBlur(main_gui.camera_tab.calibration_thread.cv_img, (1, 1), 0)

        # 그레이 이미지로 바꿔서 실행해야함.
        imgray = cv2.cvtColor(blur_img, cv2.COLOR_BGR2GRAY)

        circles = cv2.HoughCircles(imgray, cv2.HOUGH_GRADIENT, 1, 10, param1=50, param2=32, minRadius=0, maxRadius=0)


        if circles is not None:
            circles = np.uint16(np.around(circles))
            print('radi',circles[0][0][2])
            
            return circles[0][0]
        else:
            print('원을 찾을 수 없음')

            #return False


        

        
    def synthesis(self):
        try:
            synthesis_log_path = os.getcwd() + '\\x64\\Release\\synthesis_log\\' +time.strftime("%Y_%m_%d_%H_%M")
            os.mkdir(synthesis_log_path)

        except:
            pass

        try:
            if self.run_state == 'Ready':
                self.run_state = 'Running'
                self.btn_run.setText("Pause")
                print("시작")
                state = open("state.txt","w")
                state.write("시작")
                state.close()    
                
                #origin_circle = self.circle()
                #origin_x = int(origin_circle[0])



                self.label_now_cycle.setText('tester')
                
            

            for cycle_num in range(0,12):
                coupling_num = 0
                
                self.status_cycle_num = cycle_num
                
                self.label_now_cycle.setText('Cycle: ' + str(cycle_num+1))
                print('\n\n\nCycle: ' + str(cycle_num+1))
                

                self.status_step_num = 0
                
                
                for step_num in range(0,len(self.list_protocol)):
                    self.status_step_num = step_num
                    step = self.list_protocol[step_num]
                    step[1] = float(step[1])
                    step[2] = int(step[2])
                    self.label_now_step.setText('Step: ' + str(step_num+1) + ". " +str(step[0]))
                    
                    #self.table.setCurrentCell(step_num,0)

                    
                    #ACN_used, deblock_used, oxidation_used = DMPS_synthesis.get_used_solution()
                    #label_ACN_used.setText(ACN_used)
                    #label_deblock_used.setText(deblock_used)
                    #label_oxidation_used.setText(oxidation_used)



                    #######syringe합성을 위한 기능############
                    if step[0] == 'oxidation':
                        system.oxidation(step[1],step[2],cycle_num)
                                                      
                    if step[0] == 'wash':

                        system.wash(step[1],step[2],cycle_num)

                            
                    if step[0] == 'detritylation':

                        system.detritylation(step[1],step[2],cycle_num)
                        #cv2.imwrite(synthesis_log_path+'/' +str(cycle_num+1) +'cycle_detritylation.jpg',main_gui.camera_tab.calibration_thread.cv_img)

                    if step[0] == 'blow':
                        system.blow(step[1],step[2],cycle_num)

                    if step[0] == 'Sblow':
                        system.Sblow(step[1],step[2],cycle_num)



                    if step[0] == 'T_coupling':
                        
                        coupling_num = coupling_num + 1

                        #system.pre_wet(cycle_num)

                        
                        if coupling_num ==1:
                            '''
                            system.printing_T(cycle_num)
                            try:
                                cv2.imwrite(synthesis_log_path+'/' +str(cycle_num+1) +'cycle_'+str(coupling_num)+'_dT.jpg',main_gui.camera_tab.calibration_thread.cv_img)
                            except Exception as E:
                                print(E)

                            system.printing_Act(cycle_num)
                            try:
                                cv2.imwrite(synthesis_log_path+'/' +str(cycle_num+1) +'cycle_'+str(coupling_num)+'_Act.jpg',main_gui.camera_tab.calibration_thread.cv_img)
                            except Exception as E:
                                print(E)
                            '''

                            
                            system.printing_both(cycle_num+1,1)
                            try:
                                cv2.imwrite(synthesis_log_path+'/' +str(cycle_num+1) +'cycle_'+str(coupling_num)+'_both1.jpg',main_gui.camera_tab.calibration_thread.cv_img)
                            except Exception as E:
                                print(E)

                            

                            system.printing_both(cycle_num+1,2)
                            try:
                                cv2.imwrite(synthesis_log_path+'/' +str(cycle_num+1) +'cycle_'+str(coupling_num)+'_both2.jpg',main_gui.camera_tab.calibration_thread.cv_img)
                            except Exception as E:
                                print(E)
                            
                            system.printing_both(cycle_num+1,3)
                            try:
                                cv2.imwrite(synthesis_log_path+'/' +str(cycle_num+1) +'cycle_'+str(coupling_num)+'_both3.jpg',main_gui.camera_tab.calibration_thread.cv_img)
                            except Exception as E:
                                print(E)

                            system.printing_both(cycle_num+1,4)
                            try:
                                cv2.imwrite(synthesis_log_path+'/' +str(cycle_num+1) +'cycle_'+str(coupling_num)+'_both4.jpg',main_gui.camera_tab.calibration_thread.cv_img)
                            except Exception as E:
                                print(E)

 

                            #system.waste(200,5)

                            




                                

                        if coupling_num ==2:
                            '''
                        
                            system.printing_Act(cycle_num)
                            try:
                                cv2.imwrite(synthesis_log_path+'/' +str(cycle_num+1) +'cycle_'+str(coupling_num)+'_Act.jpg',main_gui.camera_tab.calibration_thread.cv_img)
                            except Exception as E:
                                print(E)

                            system.printing_T(cycle_num)
                            try:
                                cv2.imwrite(synthesis_log_path+'/' +str(cycle_num+1) +'cycle_'+str(coupling_num)+'_dT.jpg',main_gui.camera_tab.calibration_thread.cv_img)
                            except Exception as E:
                                print(E)

                            '''
                            system.printing_both(cycle_num+1,1)
                            try:
                                cv2.imwrite(synthesis_log_path+'/' +str(cycle_num+1) +'cycle_'+str(coupling_num)+'_both1.jpg',main_gui.camera_tab.calibration_thread.cv_img)
                            except Exception as E:
                                print(E)

                            

                            system.printing_both(cycle_num+1,2)
                            try:
                                cv2.imwrite(synthesis_log_path+'/' +str(cycle_num+1) +'cycle_'+str(coupling_num)+'_both2.jpg',main_gui.camera_tab.calibration_thread.cv_img)
                            except Exception as E:
                                print(E)
                            
                            system.printing_both(cycle_num+1,3)
                            try:
                                cv2.imwrite(synthesis_log_path+'/' +str(cycle_num+1) +'cycle_'+str(coupling_num)+'_both3.jpg',main_gui.camera_tab.calibration_thread.cv_img)
                            except Exception as E:
                                print(E)

                            system.printing_both(cycle_num+1,4)
                            try:
                                cv2.imwrite(synthesis_log_path+'/' +str(cycle_num+1) +'cycle_'+str(coupling_num)+'_both4.jpg',main_gui.camera_tab.calibration_thread.cv_img)
                            except Exception as E:
                                print(E)
                            






                        if coupling_num ==3:
                            '''
                        
                            system.printing_Act(cycle_num)
                            try:
                                cv2.imwrite(synthesis_log_path+'/' +str(cycle_num+1) +'cycle_'+str(coupling_num)+'_Act.jpg',main_gui.camera_tab.calibration_thread.cv_img)
                            except Exception as E:
                                print(E)

                            system.printing_T(cycle_num)
                            try:
                                cv2.imwrite(synthesis_log_path+'/' +str(cycle_num+1) +'cycle_'+str(coupling_num)+'_dT.jpg',main_gui.camera_tab.calibration_thread.cv_img)
                            except Exception as E:
                                print(E)

                            '''
                            system.printing_both(cycle_num+1,1)
                            try:
                                cv2.imwrite(synthesis_log_path+'/' +str(cycle_num+1) +'cycle_'+str(coupling_num)+'_both1.jpg',main_gui.camera_tab.calibration_thread.cv_img)
                            except Exception as E:
                                print(E)

                            system.printing_both(cycle_num+1,2)
                            try:
                                cv2.imwrite(synthesis_log_path+'/' +str(cycle_num+1) +'cycle_'+str(coupling_num)+'_both2.jpg',main_gui.camera_tab.calibration_thread.cv_img)
                            except Exception as E:
                                print(E)

                            system.printing_both(cycle_num+1,3)
                            try:
                                cv2.imwrite(synthesis_log_path+'/' +str(cycle_num+1) +'cycle_'+str(coupling_num)+'_both3.jpg',main_gui.camera_tab.calibration_thread.cv_img)
                            except Exception as E:
                                print(E)

                            system.printing_both(cycle_num+1,4)
                            try:
                                cv2.imwrite(synthesis_log_path+'/' +str(cycle_num+1) +'cycle_'+str(coupling_num)+'_both4.jpg',main_gui.camera_tab.calibration_thread.cv_img)
                            except Exception as E:
                                print(E)



                        
                        time.sleep(120)
                        if cycle_num ==0:
                            time.sleep(180)

                        #system.waste(6000, 10)

                            

                    if step[0] == 'Bulk_dT':

                        system.Bulk_dT(cycle_num)
                        time.sleep(120)
                        

                    if step[0] == 'x_init':
                        system.x_init()


            

            system.wash(10,0,-1)
            system.wash(10,0,-1)
            system.blow(3,0,-1)            
            system.detritylation(7,60,-1)
            system.wash(10,0,-1)
            system.wash(10,0,-1)
            system.wash(10,0,-1)
            system.blow(3,0,-1)



            
        except Exception as E:
            print(E)


                    
        #합성중일 시, 정지버튼으로 바뀜
        if self.run_state == 'Running':
            self.run_state = 'Pause'
            self.btn_run.setText("Stop")


        #정지중일 시, 재개버튼으로 바뀜
        if self.run_state == 'Pause':
            self.run_state = 'Running'
            self.btn_run.setText("Restart")
            return

        
            

    def check_system(self):
        #connection_Fluidics,connection_sensor = system.connection()
        #system.connection()
        '''
        if connection_Fluidics[0]:
            self.label_ACN_pump.setStyleSheet('Color : green')
            self.label_ACN_pump.setText('ACN pump\tOK')
        if connection_Fluidics[1]:
            self.label_oxidation_pump.setStyleSheet('Color : green')
            self.label_oxidation_pump.setText('Oxidation pump\tOK')
        if connection_Fluidics[2]:
            self.label_deblock_pump.setStyleSheet('Color : green')
            self.label_deblock_pump.setText('Deblock pump\tOK')
        if connection_Fluidics[3]:
            self.label_arduino.setStyleSheet('Color : green')
            self.label_arduino.setText('Arduino\tOK')
        if connection_sensor[0]:
            self.label_humidity.setStyleSheet('Color : green')
            self.label_humidity.setText('Humidity sensor\tOK')
        if connection_sensor[1]:
            self.label_ACN_remain.setStyleSheet('Color : green')
            self.label_ACN_remain.setText('ACN remain\tOK')
        if connection_sensor[2]:
            self.label_oxidation_remain.setStyleSheet('Color : green')
            self.label_oxidation_remain.setText('Oxidation remain\tOK')
        if connection_sensor[3]:
            self.label_deblock_remain.setStyleSheet('Color : green')
            self.label_deblock_remain.setText('Deblock remain\tOK')
        '''
    def update_bulk_used(self,ACN_volume,oxidation_volume,deblock_volume):
        self.used_ACN += ACN_volume
        self.label_ACN_used.setText('ACN: ' + str(self.used_ACN)+' ml')
        self.used_oxidation += oxidation_volume
        self.label_oxidation_used.setText('Oxidation: ' + str(self.used_oxidation)+' ml')
        self.used_deblock += deblock_volume
        self.label_deblock_used.setText('Deblock: ' + str(self.used_deblock)+' ml')





class Win_protocol(QWidget):

        def __init__(self):
            
            super().__init__()
            
            self.setupUI()
            
            
        def setupUI(self):
            self.setWindowTitle('Protocol setting') #창의 제목
            

            #table
            self.table = QTableWidget(self)
            self.table.setColumnCount(3)
            self.table.setRowCount(10)
            
            self.table.setHorizontalHeaderLabels(['step', 'volume', 'incubation time']) # 열 제목 지정


            #protocol save 버튼
            btn_save = QPushButton('Save')
            btn_save.clicked.connect(self.btn_save_clicked)

            #table clear 버튼
            btn_clear = QPushButton('Clear')
            btn_clear.clicked.connect(self.btn_clear_clicked)
       

            #procotol open 버튼

            #add 버튼
            btn_add = QPushButton('Add')
            btn_add.clicked.connect(self.btn_add_clicked)

            #delete 버튼
            btn_delete = QPushButton('Delete')
            btn_delete.clicked.connect(self.btn_delete_clicked)
            
            #step 콤보박스 초기화
            self.btn_clear_clicked()

            
            #Layout
            gbox = QGridLayout()
            gbox.addWidget(self.table, 0, 0)
            gbox.addWidget(btn_add,0,1)
            gbox.addWidget(btn_delete,1,1)
            gbox.addWidget(btn_clear, 3, 4)
            gbox.addWidget(btn_save, 4, 4)

            self.setLayout(gbox)

        def btn_add_clicked(self):
            row_count = self.table.rowCount()
            self.table.setRowCount(row_count+1)
            self.list_comboBox_step.append(QComboBox())
            self.list_comboBox_step[row_count].addItems(['blow','coupling', 'detritylation', 'oxidation', 'wash', 'bulk_blow', 'bulk_coupling', 'bulk_detritylation', 'bulk_oxidation', 'bulk_wash'])
            self.table.setCellWidget(row_count,0,self.list_comboBox_step[row_count])

        def btn_delete_clicked(self):
            row_count = self.table.rowCount()
            if row_count > 0:
                self.table.setRowCount(row_count-1)

                selected_row_count = self.table.currentRow()
                print(selected_row_count)
                del self.list_comboBox_step[row_count-1]


        def btn_save_clicked(self):
            file_name = QFileDialog.getSaveFileName(self, 'Save File')
            file_name = file_name[0]


            list_protocol= []

            for i in range(0,self.table.rowCount()):

                step = []
                for j in range(0,self.table.columnCount()):
                    try:
                        if j == 0:

                            value = self.list_comboBox_step[i].currentText()

                        else :
                            value = self.table.item(i,j).text()
                        
                            
                        step.append(value)
                    except:
                        pass
                    
                list_protocol.append(step)


            system.save_protocol(file_name,list_protocol)

            global widget_main
            
            widget_main.label_PRT.setText(file_name)
            widget_main.table = self.table


        def btn_clear_clicked(self):
            self.list_comboBox_step = []
            self.table.clearContents()
            self.table.setRowCount(0)
            self.btn_add_clicked()


class ProtocolTab(QWidget):

        def __init__(self):
            
            super().__init__()
            self.initUI()

            
        def initUI(self):
            self.setWindowTitle('Protocol setting') #창의 제목
            

            #table
            self.table = QTableWidget(self)
            self.table.setColumnCount(3)
            self.table.setRowCount(10)
            
            self.table.setHorizontalHeaderLabels(['step', 'volume', 'incubation time']) # 열 제목 지정


            #protocol save 버튼
            btn_save = QPushButton('Save')
            btn_save.clicked.connect(self.btn_save_clicked)

            #table clear 버튼
            btn_clear = QPushButton('Clear')
            btn_clear.clicked.connect(self.btn_clear_clicked)
       

            #procotol open 버튼

            #add 버튼
            btn_add = QPushButton('Add')
            btn_add.clicked.connect(self.btn_add_clicked)

            #delete 버튼
            btn_delete = QPushButton('Delete')
            btn_delete.clicked.connect(self.btn_delete_clicked)
            
            #step 콤보박스 초기화
            self.btn_clear_clicked()

            
            #Layout
            gbox = QGridLayout()
            gbox.addWidget(self.table, 0, 0)
            gbox.addWidget(btn_add,0,1)
            gbox.addWidget(btn_delete,1,1)
            gbox.addWidget(btn_clear, 3, 4)
            gbox.addWidget(btn_save, 4, 4)



            self.setLayout(gbox)
        def btn_add_clicked(self):
            row_count = self.table.rowCount()
            self.table.setRowCount(row_count+1)
            self.list_comboBox_step.append(QComboBox())
            self.list_comboBox_step[row_count].addItems(['blow','coupling', 'detritylation', 'oxidation', 'wash', 'bulk_blow', 'bulk_coupling', 'bulk_detritylation', 'bulk_oxidation', 'bulk_wash'])
            self.table.setCellWidget(row_count,0,self.list_comboBox_step[row_count])

        def btn_delete_clicked(self):
            row_count = self.table.rowCount()
            if row_count > 0:
                self.table.setRowCount(row_count-1)

                selected_row_count = self.table.currentRow()
                print(selected_row_count)
                del self.list_comboBox_step[row_count-1]


        def btn_save_clicked(self):
            file_name = QFileDialog.getSaveFileName(self, 'Save File')
            file_name = file_name[0]


            list_protocol= []

            for i in range(0,self.table.rowCount()):

                step = []
                for j in range(0,self.table.columnCount()):
                    try:
                        if j == 0:

                            value = self.list_comboBox_step[i].currentText()

                        else :
                            value = self.table.item(i,j).text()
                        
                            
                        step.append(value)
                    except:
                        pass
                    
                list_protocol.append(step)


            system.save_protocol(file_name,list_protocol)

            global widget_main
            
            widget_main.label_PRT.setText(file_name)
            widget_main.table = self.table


        def btn_clear_clicked(self):
            self.list_comboBox_step = []
            self.table.clearContents()
            self.table.setRowCount(0)
            self.btn_add_clicked()




######가장 바탕이 되는 메인 윈도우. 완성한 위젯을 이 위에다가 얹어주면 됨
class Xaar(QMainWindow): 

    def __init__(self):
        super().__init__()
        self.initUI()
        self.cycle_num = -1
        print("init")
        state = open("state.txt","w")
        state.write("init")
        state.close()
        
        system.connection()
        time.sleep(2)
        #system.syringe_init()
        
        

    def initUI(self):
        self.setWindowTitle('Xaar')
        self.resize(1000,900)


        ##########위젯 얹어 주는 부분######################

        self.camera_tab = CameraTab()
        self.manual_tab = ManualTab()
        self.protocol_tab = ProtocolTab()
        self.synthesis_tab =SynthesisTab()

        tabs = QTabWidget()
        tabs.addTab(self.synthesis_tab,'synthesis')
        tabs.addTab(self.camera_tab, 'camera')
        tabs.addTab(self.manual_tab, 'manual')
        tabs.addTab(self.protocol_tab, 'protocol')



        ###################################################

        

        vbox = QVBoxLayout()
        vbox.addWidget(tabs)
        centralWidget = QWidget()
        centralWidget.setLayout(vbox)

        self.setCentralWidget(centralWidget)
        
        self.show()


            
def get_main_gui():
    global main_gui
    print("edwaeee")
    return main_gui

   
KJH_SSH.connect("192.168.0.11","pi","1234")
time.sleep(0.1)
app = QApplication(sys.argv)

system = OpenIDS_sys.System()
draw = OpenIDS_sys.Draw()
main_gui = Xaar()
KJH_SSH.send_command("python3 test_client.py")


app.exec_()
sys.exit(app.exec_()) #파이썬 GUI를 끄면 모든 프로그램 종료(C에서 이걸 열었다면, C까지 같이 종료)

#ACN, Oxidizer, Deblock, amidite_T = system.connection()
