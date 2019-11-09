
from getCiscoConnect import connect
from getCiscoConnect import sendCommand
from LoadDeviceList_test import LoadData
import logging
import time
import os.path
import telnetlib
logger = logging.getLogger()
logger.setLevel(logging.INFO)  # Log等级总开关
# 第二步，创建一个handler，用于写入日志文件
rq = time.strftime(u'%Y%m%d%H%M-error', time.localtime(time.time()))
rq1 = time.strftime(u'%Y%m%d%H%M', time.localtime(time.time()))
log_path = u'LOGS/'
log_name = log_path + rq + u'.log'
logfile = log_name
fh = logging.FileHandler(logfile, mode=u'w')
fh.setLevel(logging.DEBUG)  # 输出到file的log等级的开关
 # 第三步，定义handler的输出格式
formatter = logging.Formatter(u"%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
fh.setFormatter(formatter)
# 第四步，将logger添加到handler里面
logger.addHandler(fh)
# 日志
# logger.debug(u'this is a logger debug message')
# logger.info(u'this is a logger info message')
# logger.warning(u'this is a logger warning message')
# logger.error(u'this is a logger error message')
# logger.critical(u'this is a logger critical message')
"""
从EXCEL文件中读取IP/IDRAC_IP, 主机名、用户名、第一层密码、第二层密码、品牌
filename1: 定义EXCEL格式的文件，获取数据并返回一个list
sheetname1: 工作表(sheet)中保存交换机、密码等信息的sheet名称
vlanIP_Row1： VLAN_IP: 第3列/C
idracipRow1： IDRAC_IP: 第4列/D
hostname: 主机名：第5列/E
username: 用户名：第6列/F
passwd1Row: 第一层密码：第7列/G
password2Row: 第二层密码：第8列/H
devicebrand:品牌类型：第13列/M ，目前取值仅限CISCO和H3C
程序实现LoadDeviceList.py
"""
_fpath = open("commands/device_list_file_path.txt", "r")
_filename1 = _fpath.readline()
if not os.path.exists(_filename1):
    print("device_list_path.txt文件中规定的文件不存在,路径是：%s" %_filename1)
    exit(1)
print("正在打开设备清单文件,请务必确保清单文件涵盖了全部的交换机设备：%s" %_filename1)
_sheetname1 = "SW_DEVICELIST"
_iplist = LoadData(_filename1, _sheetname1)
tn = telnetlib.Telnet()
#print(_iplist)
# LIST 格式：([ipadr, hn, un, passwd1, passwd2, devicebrand])
for ip in _iplist:
    print(ip)
    _ip1 = ip[0]
    _hostname = ip[1]
    _un = ip[2]
    _password1 = ip[3]
    _password2 = ip[4]
    _devicebrand=ip[5]
    print("Connecting %s, passwd1: %s, enablePasswd: %s, Brand: %s" % (_ip1, _password1, _password2, _devicebrand) + '\n')
    # getCiscoConnect中的connect函数如果返回false,就表示链接交换机失败，否则就返回telnet对象
    tn1 = connect(tn, ip, _devicebrand)
    if tn1:
        print("connect success,Reading command file to run")
        if _devicebrand == "CISCO":
            f = open("commands/cisco_command.txt", "r")
            exf = open("export/" + _hostname + "-" + rq1 + ".txt", "a")
            line = f.readline()
            line = line.strip('\n')
            while line:  # 直到读取完文件
                print("*正在执行命令：%s " %line, end='\n')
                result = sendCommand(tn1, line)
                result = result.replace('\r', '')
                exf.write(result)
                line = f.readline()  # 读取一行文件，包括换行符
                line = line.strip('\n')  # 去掉换行符，也可以不去
            f.close()  # 关闭文件
            exf.close()
        elif _devicebrand == "H3C":
            print("open H3C COMMAND in h3c_command.txt")
            fh3c = open("commands/h3c_command.txt", "r")
            exfh3c = open("export/" + _hostname + "-"+rq1 + ".txt",'a')
            lineh3c = fh3c.readline()
            lineh3c = lineh3c.strip("\n")
            while lineh3c:
                print("*正在执行命令: %s" %lineh3c, end='\n')
                result = sendCommand(tn1, lineh3c)
                result = result.replace('\r', '')
                exfh3c.write(result)
                lineh3c = fh3c.readline()
                lineh3c = lineh3c.strip('\n')
            fh3c.close()
            exfh3c.close()
    else:
        print("连接失败，确认IP、用户名、密码、品牌都是正确的")
        logger.debug(u'连接失败，确认IP、用户名、密码、品牌都是正确, IP:%s, 主机名：%s, level1密码：%s, enable密码：%s, 品牌：%s' %(_ip1, _hostname, _password1, _password2, _devicebrand))
        #logger.info(u'连接失败，确认IP、用户名、密码、品牌都是正确的')
        #logger.warning(u'连接失败，确认IP、用户名、密码、品牌都是正确的')
        #logger.error(u'连接失败，确认IP、用户名、密码、品牌都是正确的')
        #logger.critical(u'连接失败，确认IP、用户名、密码、品牌都是正确的')
        continue
print("已处理完成，请查看日志文件")