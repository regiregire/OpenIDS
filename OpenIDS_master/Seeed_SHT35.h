/*
 * Seeed_SHT35.H
 * Driver for SHT35
 *  
 * Copyright (c) 2018 Seeed Technology Co., Ltd.
 * Website    : www.seeed.cc
 * Author     : downey
 * Create Time: May 2018
 * Change Log :
 *
 * The MIT License (MIT)
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */

#ifndef _SEEED_SHT35_H
#define _SEEED_SHT35_H

#include "Arduino.h"
#include "Wire.h"


#ifndef SEEED_DN_DEFINES
#define SEEED_DN_DEFINES

#ifdef ARDUINO_SAMD_VARIANT_COMPLIANCE
  #define SERIAL_DB SerialUSB
#else
  #define SERIAL_DB Serial
#endif


typedef int            s32;
typedef long unsigned int   u32;
typedef short          s16;
typedef unsigned short u16;
typedef char           s8;
typedef unsigned char  u8;

typedef enum	
{
    NO_ERROR=0,
    ERROR_PARAM=-1,
    ERROR_COMM =-2,
    ERROR_OTHERS=-128,
}err_t;


#define CHECK_RESULT(a,b)   do{if(a=b)  {    \
                            SERIAL_DB.print(__FILE__);    \
                            SERIAL_DB.print(__LINE__);   \
                            SERIAL_DB.print(" error code =");  \
                            SERIAL_DB.println(a);                   \
                            return a;   \
                            }}while(0)

#endif


#define     DEFAULT_IIC_ADDR     0x45
#define		NACK_ON_ADDR			2


#define		CLK_STRETCH_ENABLED		0
#define		CLK_STRETCH_DISABLED	3

#define		MODE_MPS_05				6
#define		MODE_MPS_1				9
#define		MODE_MPS_2				12
#define		MODE_MPS_4				15
#define		MODE_MPS_10				18

#define		REPEAT_HIGH				0
#define		REPEAT_MED				1
#define		REPEAT_LOW				2

#define		CMD_BREAK			0x3093
#define		CMD_SOFT_RST		0x30A2
#define		CMD_ENABLE_HEAT		0x306D
#define		CMD_DISABLE_HEAT	0x3066	
#define		CMD_READ_SREG		0xF32D
#define		CMD_CLEAR_SREG		0x3041
#define		CMD_FETCH_DATA		0xE000 

#define     CMD_READ_HIGH_ALERT_LIMIT_SET_VALUE     0XE11F
#define     CMD_READ_HIGH_ALERT_LIMIT_CLEAR_VALUE   0XE114
#define     CMD_READ_LOW_ALERT_LIMIT_SET_VALUE      0XE102
#define     CMD_READ_LOW_ALERT_LIMIT_CLEAR_VALUE    0XE109

#define     CMD_WRITE_HIGH_ALERT_LIMIT_SET_VALUE    0X611D
#define     CMD_WRITE_HIGH_ALERT_LIMIT_CLEAR_VALUE  0X6116
#define     CMD_WRITE_LOW_ALERT_LIMIT_SET_VALUE     0X6100
#define     CMD_WRITE_LOW_ALERT_LIMIT_CLEAR_VALUE     0X610B

#define     HIGH_REP_WITH_STRCH      0x2C06

#define     CMD_HEATER_ON     0x306D
#define     CMD_HEATER_OFF    0x3066

typedef enum
{
    CLK_STRETCH_DISABLE,
    CLK_STRETCH_ENABLE,
}clk_skch_t;



class SHT_IIC_OPRTS
{
    public:
        void IIC_begin(){Wire.begin();}
        err_t send_command(u16 cmd);
        err_t request_bytes(u8* data,u16 data_len);
        err_t read_bytes(u8* data,u32 data_len,clk_skch_t clk_strch_stat);
        void set_scl_pin(u8 scl);
        void set_iic_addr(u8 IIC_ADDR);
        u8 crc8(const u8 *data, int len);

        err_t I2C_write_bytes(u16 cmd,u8* data,u32 len);
    private:
        u8 _IIC_ADDR;
        u8 SCK_PIN;
};


class SHT35:public SHT_IIC_OPRTS
{
    public:
        SHT35(u8 scl_pin,u8 IIC_ADDR=DEFAULT_IIC_ADDR);
        ~SHT35(){}
        err_t init();
        err_t read_reg_status(u16 *value);


        err_t heaterStatus(u16 status,bool stat);
        err_t heaterStatus(bool stat);

        err_t reset_check(u16 status,bool stat);
        err_t reset_check(bool stat);
        err_t cmd_excu_stat(u16 status,bool stat);
        err_t cmd_excu_stat(bool stat);
        err_t last_write_checksum(u16 status,bool stat);
        err_t last_write_checksum(bool stat);

        //err_t SHT35::read_meas_data(u16 cfg_cmd,float *temp,float *hum);
        err_t soft_reset();

        float get_temp(u16 temp);
        float get_hum(u16 hum);
        err_t clear_status_reg();
	err_t change_heater_status(bool stat);

        err_t read_meas_data_single_shot(u16 cfg_cmd,float *temp,float *hum);

        u16 temp_to_hex(float temp);
        u16 hum_to_hex(float hum);
        u16 convert_temp_hum_to_set_limit(float temp,float hum);
    private:
        const u16	data_commands[21] = {

		0x2C06, 0x2C0D, 0x2C10,	//Clock Stretch
		0x2400, 0x240B, 0x2416,	//No clock stretch
		0x2032, 0x2024, 0x202F,	//0.5 meas per sec
		0x2130, 0x2126, 0x212D,	//1 meas per sec
		0x2236, 0x2220, 0x222B,	//2 meas per sec	
		0x2334, 0x2322, 0x2329,	//4 meas per sec
		0x2737, 0x2721, 0x272A	//10 meas per sec
	    };
        
        clk_skch_t CLK_STRCH_STAT;
};








#endif
