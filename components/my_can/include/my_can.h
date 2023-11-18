/*
twai_message_t s1 = {
    .extd = 0,                         // 0-标准帧; 1-扩展帧
    .rtr = 0,                          // 0-数据帧; 1-远程帧
    .ss = 1,                           // 0-错误重发; 1-单次发送(仲裁或丢失时消息不会被重发)，对接收消息无效
    .self = 0,                         // 0-不接收自己发送的消息，1-接收自己发送的消息，对接收消息无效
    .dlc_non_comp = 0,                 // 0-数据长度不大于8(ISO 11898-1); 1-数据长度大于8(非标);
    .identifier = 0x55b,                  // 11/29位ID
    .data_length_code = 4,             // DLC数据长度4bit位宽
    .data = {0, 0, 0, 0, 0, 0, 0, 0}}; //发送数据，对远程帧无效
*/
#ifndef _MY_CAN_H
#define _MY_CAN_H
#include "driver/twai.h"
#define STD_ID 0x140

twai_message_t CAN_TorgueControl(uint8_t Motor_ID, int32_t iqControl);

twai_message_t speedControl(uint8_t Motor_ID, int32_t speedControl);

twai_message_t Multi_angleControl_1(uint8_t Motor_ID, int32_t angleControl);

twai_message_t Multi_angleControl_2(uint8_t Motor_ID, uint16_t maxSpeed, int32_t angleControl);

twai_message_t Single_loop_angleControl_1(uint8_t Motor_ID, uint8_t spinDirection, uint16_t angleControl);

twai_message_t Single_loop_angleControl_2(uint8_t Motor_ID, uint8_t spinDirection, uint16_t maxSpeed, uint16_t angleControl);

twai_message_t Motor_Off(uint8_t Motor_ID);

twai_message_t Get_PID_DATA(uint8_t Motor_ID);

twai_message_t Set_PID_DATA(uint8_t Motor_ID, uint8_t C_P, uint8_t C_I, uint8_t S_P, uint8_t S_I, uint8_t P_P, uint8_t P_I, bool save2ROM);
#endif //_MY_CAN_H