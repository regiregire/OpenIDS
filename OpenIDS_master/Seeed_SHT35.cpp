/*
 * Seeed_SHT35.cpp
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

#include "Seeed_SHT35.h"


SHT35::SHT35(u8 scl_pin,u8 IIC_ADDR)
{
	set_iic_addr(IIC_ADDR);
	set_scl_pin(scl_pin);
	CLK_STRCH_STAT=CLK_STRETCH_DISABLE;
}

err_t SHT35::init()
{
	err_t ret=NO_ERROR;
	IIC_begin();
	ret=soft_reset();
	return ret;
}



err_t SHT35::soft_reset()
{
	err_t ret=NO_ERROR;
	ret=send_command(CMD_SOFT_RST);
	return ret;
}


err_t SHT35::read_meas_data_single_shot(u16 cfg_cmd,float *temp,float *hum)
{
	err_t ret=NO_ERROR;
	u8 data[6]={0};
	u16 temp_hex=0,hum_hex=0;
	CHECK_RESULT(ret,send_command(cfg_cmd));
	CHECK_RESULT(ret,read_bytes(data,sizeof(data),CLK_STRCH_STAT));

	temp_hex=(data[0] << 8) | data[1];
	hum_hex =(data[3] << 8) | data[4];

	*temp =get_temp(temp_hex);
	*hum=get_hum(hum_hex);

	return ret;
}


float SHT35::get_temp(u16 temp)
{
	return (temp / 65535.00) * 175 - 45;
}

float SHT35::get_hum(u16 hum)
{
	return (hum / 65535.0) * 100.0;
}



u16 SHT35::temp_to_hex(float temp)
{
	return (u16)((temp+45)*65535.0/175);
}

u16 SHT35::hum_to_hex(float hum)
{
	return (u16)(hum/100.0*65535);
}


/******************************************************STATUS REG**************************************************/
/******************************************************STATUS REG**************************************************/



err_t SHT35::read_reg_status(u16 *value)
{
	err_t ret=NO_ERROR;
	*value=0;
	u8 stat[3]={0};
	CHECK_RESULT(ret,send_command(CMD_READ_SREG));
	CHECK_RESULT(ret,request_bytes(stat,sizeof(stat)));
	*value |= (u16)stat[0]<<8;
	*value |= stat[1];
	return ret;
}



err_t SHT35::heaterStatus(u16 status,bool stat) 
{
	stat= ((status >> 13) & 0x01);
	return NO_ERROR;
}

err_t SHT35::heaterStatus(bool stat)
{
	err_t ret=NO_ERROR;
	u16 status=0;
	CHECK_RESULT(ret,read_reg_status(&status));
	stat= ((status >> 13) & 0x01);
	return ret;
}
/****************************************************/



err_t SHT35::reset_check(u16 status,bool stat) 
{
	stat=((stat >> 4) & 0x01);
	return NO_ERROR;
}

err_t SHT35::reset_check(bool stat) 
{
	err_t ret=NO_ERROR;
	u16 status=0;
	CHECK_RESULT(ret,read_reg_status(&status));
	stat=((stat >> 4) & 0x01);
	return ret;
}
/****************************************************/

err_t SHT35::cmd_excu_stat(u16 status,bool stat)
{
	stat=((stat >> 1) & 0x01);
	return NO_ERROR;
}

err_t SHT35::cmd_excu_stat(bool stat)
{
	err_t ret=NO_ERROR;
	u16 status=0;
	CHECK_RESULT(ret,read_reg_status(&status));
	stat=((stat >> 1) & 0x01);
	return ret;
}
/****************************************************/
err_t SHT35::last_write_checksum(u16 status,bool stat)
{
	stat=((status >> 0) & 0x01);
	return NO_ERROR;
}
err_t SHT35::last_write_checksum(bool stat)
{
	err_t ret=NO_ERROR;
	u16 status=0;
	CHECK_RESULT(ret,read_reg_status(&status));
	stat=((stat >> 0) & 0x01);
	return ret;
}

/***********************************************************************************************/
/**************************************EXEC COMMAND*********************************************/

err_t SHT35::change_heater_status(bool stat)
{
	err_t ret=NO_ERROR;

	if (stat) {
	  ret=send_command(CMD_HEATER_ON);
	} else {
	  ret=send_command(CMD_HEATER_OFF);
	}

	return ret;
}

/***********************************************************************************************/
/*****************************************IIC OPRT**********************************************/
u8 SHT_IIC_OPRTS::crc8(const u8 *data, int len)
{

  const u8 POLYNOMIAL=0x31;
  u8 crc=0xFF;
  
  for ( int j = len; j; --j ) {
      crc ^= *data++;

      for ( int i = 8; i; --i ) {
	crc = ( crc & 0x80 )
	  ? (crc << 1) ^ POLYNOMIAL
	  : (crc << 1);
      }
  }
  return crc;
}

err_t SHT_IIC_OPRTS::send_command(u16 cmd)
{
	s32 ret=0;
	Wire.beginTransmission(_IIC_ADDR);
	Wire.write((cmd >> 8) & 0xFF);
	Wire.write(cmd & 0xFF);
	ret=Wire.endTransmission();
	if(!ret)
		return NO_ERROR;
	else
		return ERROR_COMM;
}


err_t SHT_IIC_OPRTS::I2C_write_bytes(u16 cmd,u8* data,u32 len)
{
	u8 crc=0;
	s32 ret=0;
	crc=crc8(data,len);

	Wire.beginTransmission(_IIC_ADDR);
	Wire.write((cmd >> 8) & 0xFF);
	Wire.write(cmd & 0xFF);
	//Wire.beginTransmission(_IIC_ADDR);
	for(int i=0;i<len;i++)
	{
		Wire.write(data[i]);
	}
	Wire.write(crc);
	ret=Wire.endTransmission();
	if(!ret)
		return NO_ERROR;
	else
		return ERROR_COMM;
}

err_t SHT_IIC_OPRTS::request_bytes(u8* data,u16 data_len)
{
	err_t ret=NO_ERROR;
	u32 time_out_count=0;
	Wire.requestFrom(_IIC_ADDR, data_len);
	while(data_len!=Wire.available())
    {
        time_out_count++;
        if(time_out_count>10)  return ERROR_COMM;
        delay(1);
    }
    for(int i=0;i<data_len;i++)
    {
        data[i]=Wire.read();
    }
	return NO_ERROR;
} 

/*SHT3X device is different from other general IIC device.*/
err_t SHT_IIC_OPRTS::read_bytes(u8* data,u32 data_len,clk_skch_t clk_strch_stat) 
{
	err_t ret=NO_ERROR;
    u32 time_out_count=0;
	if (clk_strch_stat == CLK_STRETCH_ENABLE)
	{
		while (0 == digitalRead(SCK_PIN)) {yield();}
	}
	else {
		Wire.beginTransmission(_IIC_ADDR);
		while (Wire.endTransmission() == NACK_ON_ADDR) {
			Wire.beginTransmission(_IIC_ADDR);
		}
	}
	
	Wire.requestFrom(_IIC_ADDR, data_len);
    while(data_len!=Wire.available())
    {
        time_out_count++;
        if(time_out_count>10)  return ERROR_COMM;
        delay(1);
    }
    for(int i=0;i<data_len;i++)
    {
        data[i]=Wire.read();
    }
    return NO_ERROR;
}


void SHT_IIC_OPRTS::set_scl_pin(u8 scl)
{
	SCK_PIN=scl;
}

/**@brief change the I2C address from default.
 * @param IIC_ADDR: I2C address to be set 
 * */
void SHT_IIC_OPRTS::set_iic_addr(u8 IIC_ADDR)
{
    _IIC_ADDR=IIC_ADDR;
}
