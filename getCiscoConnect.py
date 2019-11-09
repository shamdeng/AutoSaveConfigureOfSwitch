"""
    对交换机品牌进行判断特征，但是这几个特殊还没有实现，不知道要如何搞
    telnet ip 后
    H3C的交换机会有提示：Login authentication ，然后出现Password:
    CISCO的交换机会有提示： User Access Verification ， 然后出现Password:
    H3C ADB的交换机有提示：Login authentication, 然后出现Username: , 输入用户名后回车，会出现Password:
    """
import logging
import telnetlib
import re
import time

teltimeout=3
def __init__(self,
        singleCommand="",
        brand="CISCO",
):
    """
    :param singleCommand:
    :return:
    """


def sendCommand(tn: telnetlib.Telnet(), singleCommand):
    if singleCommand is not None or singleCommand is not b'\n':
        #        result = ""
        tn.write(singleCommand.encode('ascii') + b'\n')
        time.sleep(3)
        result = tn.read_very_eager().decode('ascii').strip('\r\n')
        return result


def connect(tn, _list, brand):
    """
    :param tn:  telnet()对像实例
    :param _list:  iplist([ipadr, hn, un, passwd1, passwd2, devicebrand])
    :return:
    """

    try:
        tn.open(_list[0], port=23, timeout=50)
        #tn.set_debuglevel(5)
    except:
        logging.warning('%s网络连接失败' %_list[0])
        return False
    if _list[2]:
        tn.read_until(b'Username:', teltimeout)
        tn.write(_list[2].encode('ascii') + b'\n')
    if _list[3]:   #Level 1 password
        if tn.read_until(b'Password:', teltimeout):
            tn.write(_list[3].encode('ascii') + b'\n')
            result = tn.read_until(b'>', teltimeout)
            login_failed = re.search(b">", result)
            if not login_failed:
                print("======LOGIN failed in LEVEL1====", result, end="\n")
                tn.close()
                return False
        if brand=="CISCO":
            tn.write("enable".encode('ascii') + b'\n')
            if tn.read_until(b"Password:", teltimeout):
                tn.write(_list[4].encode('ascii') + b'\n')
                enablemode = tn.read_until(b'#', teltimeout)
                login_failed2 = re.search(b"#", enablemode)
                if not login_failed2:
                    print("=====enable login error", result, end="\n")
                    tn.close()
                    return False
                else:
                    return tn
        elif brand == "H3C":
            tn.write("super".encode('ascii') + b'\n')
            if tn.read_until(b'Password:', teltimeout):
                tn.write(_list[4].encode('ascii') + b'\n')
                enablemode = tn.read_until(b'>', teltimeout)
                login_failed2 = re.search(b'>', enablemode)
                if not login_failed2:
                    print("=====H3C login error", result, end='\n')
                    return False
                else:
                    return tn



"""
for test
tn = telnetlib.Telnet()
isok = connect(tn,"172.16.144.254", "", "XmTpv!", "test!")
#print("isok=", isok)
"""
