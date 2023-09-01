import cv2
import numpy as np
from PIL import Image

x1, x2, y1, y2 = -1, -1, -1, -1
src, tmp_img = None, None
drawing = False
width, height = 242, 142
edge = 0
x_gap = 0
y_gap = 0
degree_angle=1


def image_rotate(img, degree_angle):
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



def make_img():
    degree_angle = 0
    #color_space = get_color_space(sequence_path)

    width = 24840
    height = 14840
    pixel = 137.1  # nozzle간 간격 = pixel간 간격 = 137.1um
    well = 500
    CtoC = 1000 # 1000 = 1mm
    x_blank = 1500 
    y_blank = 2500
    well_x_num = 10
    well_y_num = 18
    glass = 140000 # glass의 가로 길이 실측값
    pixel_glass = glass/pixel # glass의 가로길이를 pixel로 나눈 값

    pixel_width = width/pixel
    pixel_height = height/pixel
    pixel_well = well/pixel
    pixel_CtoC = CtoC/pixel
    pixel_x_blank = x_blank/pixel
    pixel_y_blank = y_blank/pixel
    
    x_first = edge+150 #첫 well의 시작점
    y_first = edge+150 #첫 well의 시작점
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
                x_center = int((x_blank + column * CtoC + well/2 + glass/2 - width/2) / pixel)
                y_center = int((y_blank + row * CtoC + well/2 + (128/2)*pixel - height/2) / pixel) + 3
                #img = cv2.rectangle(img, (x_center-2,y_center-2), (x_center+2,y_center+2), color_space[row][column][z], -1)
                img = cv2.rectangle(img, (x_center-100,y_center-5), (x_center,y_center+5), (0,0,0), -1) #-2,-2   +3,+4


        rotated_img = image_rotate(img, degree_angle)



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
        cv2.imwrite(str(3) + 'st_base.png', rotated_img_binary, [cv2.IMWRITE_PNG_BILEVEL, 1]) #open cv는 이미지를 bmp형식으로 저장할 수 없으므로 png로 저장

        ##### 1bit png로 저장한거를 bmp형식으로 바꿈######
        file_in = str(3) + "st_base.png"
        img = Image.open(file_in)
        img_resize = img.resize((img.width, img.height*10))

        file_out = (str('101')) + '_bmp' ".bmp" #인쇄하는데 쓸 최종 이미지
        img_resize.save(file_out)
        img.save("101.bmp")
        ##########################################

        cv2.waitKey(0)
        cv2.destroyAllWindows()

make_img()
