#!/usr/bin/env python3
import platform
import sys
import os
import shutil
import ctypes
import time
from ctypes import  cdll,c_double,c_int,c_bool,c_char,c_wchar,c_char_p,c_wchar_p,Structure,pointer,create_string_buffer,c_byte
from struct import *
from math import pi
from visual_kinematics.RobotSerial import *
import numpy as np
from math import pi
import time

DLL_NAME = "./libnrc_host.so"

class Yuil_robot(object):
    def __init__(self,robot_name='aaa'):

        np.set_printoptions(precision=3, suppress=True)
    
        dh_params = np.array([[0.138, 0.,  0.5*pi, 0],
                              [0., 0.42135, 0., 0.5 * pi],
                              [0., 0.40315, 0., -0.5 * pi],
                              [0.123, 0., 0.5 * pi, 0.5 * pi],
                              [0.098, 0., -0.5 * pi, 0.5 * pi],
                              [0.082, 0.,  0., 0.5*pi]])

        self.robot_sim = RobotSerial(dh_params)
        
        dll_name = os.path.abspath(DLL_NAME)
        self.nrc_lib = ctypes.CDLL(dll_name)
        self.robot_name = bytes(robot_name, 'utf-8')
        self.robot_connect()

    def robot_connect(self):         # 连接控制器
        ip = '192.168.1.13'
        port = "6001"
        if platform.architecture()[0].lower() == "64bit":
            ip = bytes(ip, 'utf-8')
            port = bytes(port, 'utf-8')
        else:
            ip = bytes(ip)
            port = bytes(port)
        state = self.nrc_lib.connect_robot(ip,port,self.robot_name)
        if state:
            print("robot connected")
            return True
        else:
            print("robot connect failed")
            return False

    def robot_servo_on(self):               # 示教模式伺服器使能
        try:
            #self.nrc_lib.set_servo_state(1,self.robot_name);
            if self.nrc_lib.set_servo_poweron(self.robot_name):
                print("robot servo on")
            else:
                print("robot servo on failed")
            #self.nrc_lib.set_servo_state(3,self.robot_name);
        except Exception as e:
            print(e)

    def robot_servo_off(self):            # 示教模式伺服器使能关闭
        run_state = self.nrc_lib.get_robot_running_state(self.robot_name)
        print("a-running_state: ",run_state)
        servo_state = self.nrc_lib.get_servo_state(self.robot_name)
        print("servo_state: ",servo_state)
        try:
            self.nrc_lib.set_servo_poweroff(self.robot_name);
            print("伺服器关闭！")
        except Exception as e:
            print(e)

    def robot_movl(self, pos, speed=10, coord=0):       # 示教模式直线运动
        print("now go",pos)
        try:
            self.nrc_lib.robot_movl(pos, speed, coord,self.robot_name)
        except Exception as e:
            print(e)

    def robot_select_coord(self, coord):         # 选择机器人坐标系
        try:
            self.nrc_lib.set_current_coord(coord)
        except Exception as e:
            print(e)

    def robot_get_current_coord(self):      # 设置机器人坐标系
        try:
            return self.nrc_lib.get_current_coord()
        except Exception as e:
            print(e)

    def robot_get_current_position(self):  # 获取机器人当前坐标
        data = c_double*6
        pos = data()
        self.nrc_lib.get_current_position(pos,0,self.robot_name);
        return pos

    def robot_start_jogging(self, axis, direction):  # 点动
        try:
            self.nrc_lib.start_jogging(axis, direction)
        except Exception as e:
            print(e)

    def robot_movj(self, pos_sim, speed=10, coord=0):         # 示教模式关节运动
        data = c_double*7
        pos = data()
        #self.nrc_lib.get_current_position(pos,0,self.robot_name);
        pos[0] = pos_sim[0] * 180/pi
        pos[1] = pos_sim[1] * 180/pi
        pos[2] = pos_sim[2] * 180/pi
        pos[3] = pos_sim[3] * 180/pi
        pos[4] = pos_sim[4] * 180/pi
        pos[5] = pos_sim[5] * 180/pi
        #pos[0] = 45
        #pos[1] = -45
        #pos[2] = 45
        #pos[3] = 45
        #pos[4] = 45
        #pos[5] = 45
        #print(type(pos[5]))
        print(pos[0],pos[1],pos[2],pos[3],pos[4],pos[5])
        run_state = self.nrc_lib.get_robot_running_state(self.robot_name)
        #print("a-running_state: ",run_state)
        servo_state = self.nrc_lib.get_servo_state(self.robot_name)
        #print("servo_state: ",servo_state)
        try:
            #time.sleep(20)
            self.nrc_lib.robot_movej(pos,50,0,80,80,self.robot_name)
            
            test = self.nrc_lib.set_current_mode(1,self.robot_name)
            run_state = self.nrc_lib.get_robot_running_state(self.robot_name)
            #print("a-running_state: ",run_state)
            servo_state = self.nrc_lib.get_servo_state(self.robot_name)
            #print("servo_state: ",servo_state)
        except Exception as e:
            print(e)

    def robot_movc(self, pos1, pos2, pos3, speed, coord):    # 示教模式整圆运动
        try:
            self.nrc_lib.robot_movc(pos1, pos2, pos3, speed, coord)
        except Exception as e:
            print(e)

    def robot_movca(self, pos1, pos2, pos3, speed, coord):   # 示教模式整圆弧运动
        try:
            self.nrc_lib.robot_movca(pos1, pos2, pos3, speed, coord)
        except Exception as e:
            print(e)

    def robot_upload_job(self, path):
        self.nrc_lib.upload_job(bytes(path, encoding="utf8"))

    def robot_run(self, recipe):
        print("run" + recipe)
        self.nrc_lib.job_run(bytes(recipe, encoding="utf8"),self.robot_name)

    def robot_stop(self):
        self.nrc_lib.stop_job()

    def robot_get_state(self):              # 获机器人状态
        try:
            state = self.nrc_lib.get_robot_running_state(self.robot_name)
            return state
        except Exception as e:
            print(e)

    def robot_get_current_mode(self):       # 设置机器人模式
        try:
            return self.nrc_lib.get_current_mode()
        except Exception as e:
            print(e)

    def robot_set_runspeed(self, speed):     # 设置机器人运行模式速度
        try:
            self.nrc_lib.set_jogging_speed(speed)
        except Exception as e:
            print(e)

    def robot_set_jogspeed(self, speed):     # 设置机器人调试速度
        try:
            self.nrc_lib.set_jogging_speed(speed)
        except Exception as e:
            print(e)

    def robot_joging(self, axis, direction=False):    # 调试模式轴运动
        try:
            self.nrc_lib.start_jogging(axis, direction)
        except Exception as e:
            print(e)

    def robot_jogstop(self, axis):                   # 调试模式轴运动停止
        try:
            self.nrc_lib.stop_jogging(axis)
        except Exception as e:
            print(e)

    def robot_select_mode(self, mode):          # 选择机器人模式
        try:
            self.nrc_lib.set_current_mode(mode)
        except Exception as e:
            print(e)

    def robot_set_dout(self, port, value):           # port端口号 Value 0,1
        self.nrc_lib.set_dout(port, value)

    def robot_get_dout(self):  # 查询数字输出
        data = c_double*16
        dout = data()
        try:
            self.nrc_lib.get_dout(dout)
            return dout

        except Exception as e:
            print(e)

    def robot_get_din(self):                        # 查询数字输入
        data = c_double*16
        din = data()
        self.nrc_lib.get_din(din)
        return din

    def continuous_motion_mode(self, on):            # 连续轨迹运动设置
        try:
            self.nrc_lib.continuous_motion_mode(on)      # on ：0 关闭；- 1 开启
        except Exception as e:
            print(e)

    def send_continuous_motion_queue(self, cmd, size):     # param cmd 指令数组  size 指令数组长度
        try:
            self.nrc_lib.send_continuous_motion_queue(cmd, size)
        except Exception as e:
            print(e)

    def continuous_motion_start(self):         # 开始连续运动
        print("try continuous_motion_start")
        try:
            self.nrc_lib.continuous_motion_start()
        except Exception as e:
            print(e)

    def continuous_motion_suspend(self):       # 暂停连续运动
        try:
            self.nrc_lib.continuous_motion_suspend()
        except Exception as e:
            print(e)

    def continuous_motion_stop(self):          # 停止连续运动
        try:
            self.nrc_lib.continuous_motion_stop()
        except Exception as e:
            print(e)

    def set_axis_zero_position(self, axis):      # 设置零点位置
        try:
            self.nrc_lib.set_axis_zero_position(axis)
        except Exception as e:
            print(e)

    def clear_error(self):                      # 伺服错误信息
        try:
            self.nrc_lib.clear_error()
        except Exception as e:
            print(e)

    def set_user_coord_number(self, num):        # 切换用户坐标系
        try:
            self.nrc_lib.set_user_coord_number(num)
        except Exception as e:
            print(e)

    def get_single_cycle(self, single_cycle):   # 获取单圈值
        single_cycle = c_double*6
        single_cycle = single_cycle()
        try:
            self.nrc_lib.get_single_cycle(single_cycle)
            return single_cycle
        except Exception as e:
            print(e)
            return

    def get_global_var(self, varname):       # 获取变量数值
        try:
            return self.nrc_lib.get_global_var(varname)
        except Exception as e:
            print(e)
            return
    def move_test_joint_base(self,sleep_t):
        try:
            print("go go go")
            self.nrc_lib.robot_stop_jogging(1,self.robot_name);
            time.sleep(1)
            self.nrc_lib.robot_start_jogging(1,True,self.robot_name);
            time.sleep(sleep_t)
            self.nrc_lib.robot_stop_jogging(1,self.robot_name);
            time.sleep(sleep_t)
            self.nrc_lib.robot_start_jogging(1,False,self.robot_name);
            time.sleep(sleep_t)
            self.nrc_lib.robot_stop_jogging(1,self.robot_name);
        except Exception as e:
            print(e)
            return
    def xyz_to_joint_move(self,xyz,abc):
        #xyz = np.array([[0.801], [-0.123], [0.177]])
        #abc = np.array([-3.14, 0.0, -3.142])
        #xyz = np.array([[0.601], [-0.323], [0.377]])
        #abc = np.array([-3.14, 0.0, 1.571])
        end = Frame.from_euler_3(abc, xyz)
        self.robot_sim.inverse(end)
        pos = self.robot_get_current_position()
        print(pos[0],pos[1],pos[2],pos[3],pos[4],pos[5])
        print(self.robot_sim.axis_values)
        print("state",self.robot_get_state())
        if self.robot_sim.is_reachable_inverse:
            print("inverse is successful: {0}".format(self.robot_sim.is_reachable_inverse))
            self.robot_movj(self.robot_sim.axis_values)
    def gripper_open(self):
        self.robot_run("UCLAMP") # open gripper
    def gripper_close(self):
        self.robot_run("CLAMP") # close gripper
    def go_home(self):
        data = c_double*7
        pos = data()
        try:
            self.nrc_lib.robot_movej(pos,100,0,80,80,self.robot_name)
        except Exception as e:
            print(e)
