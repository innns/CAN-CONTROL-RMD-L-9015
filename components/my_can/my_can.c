#include "my_can.h"

/**
 * @brief  Torgue control A1 command 力矩控制
 * @param  uint8_t Motor_ID
 * @param  int32_t iqControl
 */
twai_message_t CAN_TorgueControl(uint8_t Motor_ID, int32_t iqControl)
{
    twai_message_t msg = {.identifier = (STD_ID + Motor_ID), .data_length_code = 8, .data = {0xA1, 0, 0, 0, *(uint8_t *)(&iqControl), *((uint8_t *)(&iqControl) + 1), 0, 0}};
    msg.rtr = 0;
    msg.extd = 0;
    return msg;
}

/**
 * @brief  speeed control A2 command 速度控制
 * @param  uint8_t Motor_ID
 * @param  int32_t speedControl
 */
twai_message_t speedControl(uint8_t Motor_ID, int32_t speedControl)
{
    twai_message_t msg = {.identifier = (STD_ID + Motor_ID), .data_length_code = 8, .data = {0xA2, 0, 0, 0, *((uint8_t *)(&speedControl)), *((uint8_t *)(&speedControl) + 1), *((uint8_t *)(&speedControl) + 2), *((uint8_t *)(&speedControl) + 3)}};
    msg.rtr = 0;
    msg.extd = 0;
    return msg;
}

/**
 * @brief  Multi_angleControl_1 A3 command
 * @param  uint8_t Motor_ID
 * @param  int32_t angleControl
 */
twai_message_t Multi_angleControl_1(uint8_t Motor_ID, int32_t angleControl)
{
    twai_message_t msg = {.identifier = (STD_ID + Motor_ID), .data_length_code = 8, .data = {0xA3, 0, 0, 0, *((uint8_t *)(&angleControl)), *((uint8_t *)(&angleControl) + 1), *((uint8_t *)(&angleControl) + 2), *((uint8_t *)(&angleControl) + 3)}};
    msg.rtr = 0;
    msg.extd = 0;
    return msg;
}

/**
 * @brief  Multi_angleControl_2 A4 command
 * @param  uint8_t Motor_ID
 * @param  uint16_t maxSpeed
 * @param  int32_t angleControl
 */
twai_message_t Multi_angleControl_2(uint8_t Motor_ID, uint16_t maxSpeed, int32_t angleControl)
{
    twai_message_t msg = {.identifier = (STD_ID + Motor_ID), .data_length_code = 8, .data = {0xA4, 0, *(uint8_t *)(&maxSpeed), *(uint8_t *)((&maxSpeed) + 1), *((uint8_t *)(&angleControl)), *((uint8_t *)(&angleControl) + 1), *((uint8_t *)(&angleControl) + 2), *((uint8_t *)(&angleControl) + 3)}};
    msg.rtr = 0;
    msg.extd = 0;
    return msg;
}

/**
 * @brief  Single_loop_angleControl_1 A5 command
 * @param  uint8_t Motor_ID
 * @param  uint8_t spinDirection
 * @param  int16_t angleControl
 */
twai_message_t Single_loop_angleControl_1(uint8_t Motor_ID, uint8_t spinDirection, uint16_t angleControl)
{
    twai_message_t msg = {.identifier = (STD_ID + Motor_ID), .data_length_code = 8, .data = {0xA5, spinDirection, 0, 0, *((uint8_t *)(&angleControl)), *((uint8_t *)(&angleControl) + 1), 0, 0}};
    msg.rtr = 0;
    msg.extd = 0;
    return msg;
}

/**
 * @brief  Single_loop_angleControl_2 A6 command
 * @param  uint8_t Motor_ID
 * @param  uint8_t spinDirection
 * @param  uint16_t maxSpeed
 * @param  int16_t angleControl
 */
twai_message_t Single_loop_angleControl_2(uint8_t Motor_ID, uint8_t spinDirection, uint16_t maxSpeed, uint16_t angleControl)
{
    twai_message_t msg = {.identifier = (STD_ID + Motor_ID), .data_length_code = 8, .data = {0xA6, spinDirection, *(uint8_t *)(&maxSpeed), *((uint8_t *)(&maxSpeed) + 1), *((uint8_t *)(&angleControl)), *((uint8_t *)(&angleControl) + 1), 0, 0}};
    msg.rtr = 0;
    msg.extd = 0;
    return msg;
}

/**
 * @brief  Motor_Off command
 * @param  uint8_t Motor_ID
 */
twai_message_t Motor_Off(uint8_t Motor_ID)
{
    twai_message_t msg = {.identifier = (STD_ID + Motor_ID), .data_length_code = 8, .data = {0x81, 0, 0, 0, 0, 0, 0, 0}};
    msg.rtr = 0;
    msg.extd = 0;
    return msg;
}

/**
 * @brief  Get_PID_DATA command
 * @param  uint8_t Motor_ID
 * Receive: Standard Data   Frame,  ID: 0x241  D0: 0x30  D1: 0x00  D2: 0x32  D3: 0x32  D4: 0x64  D5: 0x32  D6: 0x32  D7: 0x00 
 * Data[2]代表电流环KP参数，0x55十进制代表85，假设系统设置的电流环最大值为3，那么1个单位的实际值为3/256 = 0.01171875，85个单位就代表实际值为85*0.01171875 = 0.99609375，这就是系统内部电流环KP参数的实际值。
 * Data[3]代表电流环KI参数，0x19十进制代表25，假设系统设置的电流环最大值为0.1，那么1个单位的实际值为0.1/256 = 0.00039062，25个单位就代表实际值为25*0.00039062 = 0.0097656，这就是系统内部电流环KI参数的实际值。
 * Data[4]代表速度环KP参数，0x55十进制代表85，假设系统设置的速度环最大值为0.1，那么1个单位的实际值为0.1/256 = 0.00039062，85个单位就代表实际值为85*0.00039062 = 0.0332027，这就是系统内部速度环KP参数的实际值。
 * Data[5]代表速度环KI参数，0x19十进制代表25，假设系统设置的速度环最大值为0.01，那么1个单位的实际值为0.01/256 = 0.00003906，25个单位就代表实际值为25*0.00003906 = 0.0009765，这就是系统内部速度环KI参数的实际值。
 * Data[6]代表位置环KP参数，0x55十进制代表85，假设系统设置的位置环最大值为0.1，那么1个单位的实际值为0.1/256 = 0.00039062，85个单位就代表实际值为85*0.00039062 = 0.0332027，这就是系统内部位置环KP参数的实际值。
 * Data[7]代表位置环KI参数，0x19十进制代表25，假设系统设置的位置环最大值为0.01，那么1个单位的实际值为0.01/256 = 0.00003906，25个单位就代表实际值为25*0.00003906 = 0.0009765，这就是系统内部位置环KI参数的实际值。
 */
twai_message_t Get_PID_DATA(uint8_t Motor_ID)
{
    twai_message_t msg = {.identifier = (STD_ID + Motor_ID), .data_length_code = 8, .data = {0x30, 0, 0, 0, 0, 0, 0, 0}};
    msg.rtr = 0;
    msg.extd = 0;
    return msg;
}

/**
 * @brief  Get_PID_DATA command
 * @param  uint8_t Motor_ID
 * @param  uint8_t Current P
 * @param  uint8_t Current I
 * @param  uint8_t Speed P
 * @param  uint8_t Speed I
 * @param  uint8_t Position P
 * @param  uint8_t Position I
 * @param  bool save2ROM , true: save to ROM, false: save to RAM
 */
twai_message_t Set_PID_DATA(uint8_t Motor_ID, uint8_t C_P, uint8_t C_I, uint8_t S_P, uint8_t S_I, uint8_t P_P, uint8_t P_I, bool save2ROM)
{
    uint8_t CMD = 0x31; // 写入RAM
    if (save2ROM)
    {
        CMD = 0x32; // 写入ROM
    }
    twai_message_t msg = {.identifier = (STD_ID + Motor_ID), .data_length_code = 8, .data = {CMD, C_P, C_I, S_P, S_I, P_P, P_I}};
    msg.rtr = 0;
    msg.extd = 0;
    return msg;
}