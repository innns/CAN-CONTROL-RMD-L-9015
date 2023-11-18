#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/queue.h"
#include "freertos/semphr.h"
#include "esp_err.h"
#include "esp_log.h"
#include "my_pid.h"
#include "my_can.h"

#define PI (3.14159265359)
#define EXAMPLE_TAG "CAN_TEST"
#define SENDMSG 0
#define RECEIVEMSG 1
#define RX_GPIO_PIN GPIO_NUM_4 // TJA1050
#define TX_GPIO_PIN GPIO_NUM_5 // TJA1050

/* --------------------------- Tasks and Functions -------------------------- */

/// @brief 返回sin采样
/// @param amp 幅度
/// @param phase 相位 弧度
/// @param sample_hz 采样频率
/// @param sample_id 第几次采样，第一次为id = 0
double calc_sin(double amp, double phase, double sample_hz, double sample_id)
{
    return amp * sin(2 * PI * (sample_id / sample_hz) + phase);
}

/// @brief 打印 CAN 数据
void printf_msg(int flag, twai_message_t *msg) // flag：0-send 1-receive
{
    int j;
    if (flag)
        printf("Receive: ");
    else
        printf("Send   : ");
    if (msg->extd)
        printf("Extended ");
    else
        printf("Standard ");
    if (msg->rtr)
        printf("Remote Frame, ");
    else
        printf("Data   Frame,  ");
    printf("ID: 0x%lX  ", msg->identifier);
    if (msg->rtr == 0)
    {
        for (j = 0; j < msg->data_length_code; j++)
        {
            printf("D%d: 0x%02X  ", j, msg->data[j]);
        }
        printf("\n");
    }
    else
        printf("\n");
}

/// @brief 发送 CAN 数据
static void twai_transmit_task(void *arg)
{

    int i;
    // twai_message_t s0 = Get_PID_DATA(1);
    // twai_message_t s1 = Multi_angleControl_2(1, 0x258, -0x1F4);

    vTaskDelay(pdMS_TO_TICKS(1000));
    while (1)
    {
        for (i = 0; i < 400; i++) // 发送标准数据帧
        {
            // SEND DATA TO MOTOR
            twai_message_t s1 = Multi_angleControl_2(1, 0x120, (int32_t)(100 * calc_sin(30, 0, 400, i)));
            ESP_ERROR_CHECK(twai_transmit(&s1, portMAX_DELAY));
            printf("MSG_%d  \n", i);
            //printf_msg(SENDMSG, &s1);
            vTaskDelay(pdMS_TO_TICKS(25));
        }
    }
    vTaskDelete(NULL);
}

/// @brief 接受CAN数据
static void twai_receive_task(void *arg)
{
    twai_message_t r1;
    while (1) // 接受 CAN 数据
    {
        ESP_ERROR_CHECK(twai_receive(&r1, portMAX_DELAY));
        // printf_msg(RECEIVEMSG, &r1);
        vTaskDelay(pdMS_TO_TICKS(50));
    }
    vTaskDelete(NULL);
}

void app_main(void)
{
    /*
    // CAN接口基本配置
    twai_general_config_t g_config = {
        .mode = TWAI_MODE_NORMAL,            // TWAI_MODE_NORMAL / TWAI_MODE_NO_ACK / TWAI_MODE_LISTEN_ONLY
        .tx_io = 2,                          // IO号
        .rx_io = 3,                          // IO号
        .clkout_io = TWAI_IO_UNUSED,         // io号，不用为-1
        .bus_off_io = TWAI_IO_UNUSED,        // io号，不用为-1
        .tx_queue_len = 5,                   //发送队列长度，0-禁用发送队列
        .rx_queue_len = 5,                   //接收队列长度
        .alerts_enabled = TWAI_ALERT_NONE,   //警告标志 TWAI_ALERT_ALL 可开启所有警告
        .clkout_divider = 0,                 // 1 to 14 , 0-不用
        .intr_flags = ESP_INTR_FLAG_LEVEL1}; //中断优先级
    */

    // CAN接口基本配置
    twai_general_config_t g_config = TWAI_GENERAL_CONFIG_DEFAULT(TX_GPIO_PIN, RX_GPIO_PIN, TWAI_MODE_NO_ACK);
    // CAN接口时序配置官方提供了1K to 1Mbps的常用配置
    twai_timing_config_t t_config = TWAI_TIMING_CONFIG_1MBITS(); // TWAI_TIMING_CONFIG_500KBITS()

    // 过滤器配置
    twai_filter_config_t f_config = {
        .acceptance_code = 0,          // 验证代码
        .acceptance_mask = 0xFFFFFFFF, // 验证掩码 0xFFFFFFFF表示全部接收
        .single_filter = true};        // true：单过滤器模式 false：双过滤器模式

    ESP_ERROR_CHECK(twai_driver_install(&g_config, &t_config, &f_config));
    ESP_LOGI(EXAMPLE_TAG, "Driver installed");
    ESP_ERROR_CHECK(twai_start());
    ESP_LOGI(EXAMPLE_TAG, "Driver started");
    //实现任务的函数名称（task1）；任务的任何名称（“ task1”等）；分配给任务的堆栈大小，以字为单位；任务输入参数（可以为NULL）；任务的优先级（0是最低优先级）；任务句柄（可以为NULL）；任务将运行的内核ID（0或1）
    xTaskCreatePinnedToCore(twai_receive_task, "TWAI_rx", 4096, NULL, 1, NULL,  0);
    xTaskCreatePinnedToCore(twai_transmit_task, "TWAI_tx", 10000, NULL, 3, NULL,  1);

    // vTaskDelay(pdMS_TO_TICKS(30000)); // 运行10s
    vTaskDelay(pdMS_TO_TICKS(10000)); // 运行10s

    twai_status_info_t status_info;
    twai_get_status_info(&status_info);
    // while (status_info.msgs_to_tx != 0)
    // {
    //     printf("SHUTDOWN");
    //     ESP_ERROR_CHECK(twai_get_status_info(&status_info));
    // }
    while (1)
    {
        vTaskDelay(pdMS_TO_TICKS(10000)); // 运行10s
        if(twai_get_status_info(&status_info) == ESP_FAIL)
        {
            printf("ERROR\n");
            continue;
        }
    }
    ESP_ERROR_CHECK(twai_stop()); // Stop the TWAI Driver
    ESP_LOGI(EXAMPLE_TAG, "Driver stopped");
    ESP_ERROR_CHECK(twai_driver_uninstall());
    ESP_LOGI(EXAMPLE_TAG, "Driver uninstalled");
}
