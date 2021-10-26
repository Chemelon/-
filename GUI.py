from tkinter.constants import DISABLED
import requests
import tkinter
import time
from tkinter import scrolledtext
import threading

# 请求链接
url_login = 'https://yqtb.sut.edu.cn/login'
url_getform = 'https://yqtb.sut.edu.cn/getPunchForm'
url_pushform = 'https://yqtb.sut.edu.cn/punchForm'

#############################
# 获取当前日期


def get_Date(d):
    day = int(time.strftime("%d")) + d
    if day < 10:
        day = '0' + str(day)
    year = time.strftime("%Y-%m-")
    # 格式化日期
    date = '{}{}'.format(year, day)
    # print(date)
    return date


###############################

# 文件读取 获得含有账号密码等信息的字典

temp_Zhanghao = []
temp_Mima = []
temp_Mqszd = []
temp_Dwwz = []
temp_Wz = []
temp_count = 0
file_dic = {
    '账号': temp_Zhanghao,
    '密码': temp_Mima,
    '目前所在地': temp_Mqszd,
    '定位位置': temp_Dwwz,
    '位置': temp_Wz
}
# 循环读取每一行并格式化
# 信息格式：(注意程序使用空格识别分割)
# 账号 密码 目前所在地 定位位置 位置
with open('签到.txt', 'r', encoding='utf-8') as file:
    for line in file:
        if line.strip() == '':
            break
        file_dic['账号'].append(line.strip().split(" ")[0])
        file_dic['密码'].append(line.strip().split(" ")[1])
        file_dic['目前所在地'].append(line.strip().split(" ")[2])
        file_dic['定位位置'].append(line.strip().split(" ")[3])
        file_dic['位置'].append(line.strip().split(" ")[4])

    # print(file_dic)
file.close()
# print("文件关闭 = %s" % file.closed)

del line, temp_Wz, temp_Dwwz, temp_Mima, temp_Mqszd, temp_Zhanghao
# 文件读取结束

########################################

# 请求信息
headers = {
    "Content-Type":
    "application/json",
    "User-Agent":
    "Mozilla/5.0 (Windows NT 10.0Win64x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36 Edg/93.0.961.38"
}

# Date(0)以请求到前一天的打卡信息
get_form = {"date": get_Date(0)}

# session = requests.session() 不能放在外面不然cookies一样，不能实现切换账号的功能(原理未知)

# 声明窗体
window = tkinter.Tk()


# 登录函数
def punch():
    try:
        # 打开日志文件，若没有，则创建
        file_log = open("log.txt", "a+")
        # 打卡时不能退出
        btn['state'] = 'disabled'
        exit['state'] = 'disabled'
        # 根据账号数量计算循环次数
        length = len(file_dic['账号'])
        # 特殊处理防止账号数量为 1 时不能进入循环
        # if length == 0:
        #     length = 1
        for count in range(0, length):
            time.sleep(1)
            session = requests.session()

            data = {"user_account": file_dic['账号'][count], "user_password": file_dic['密码'][count]}

            # 打印账号信息
            msg = file_dic['账号'][count]
            print(f'当前账号:{msg}')
            file_log.write(f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}  当前账号:{msg}\n')
            Msg.insert('insert', f'\n当前账号:{msg}\n')
            window.update()
            # 登录
            resp = session.post(url_login, headers=headers, json=data, verify=False)

            # 打印登录信息
            dic = resp.json()
            msg = dic['msg']
            print(f'登录状态:{msg}')
            file_log.write(f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}  登录状态:{msg}\n')
            Msg.insert('insert', f'登录状态:{msg}\n')
            window.update()

            # 请求上次打卡信息
            resp = session.post(url_getform, headers=headers, json=get_form, verify=False)

            # 打印请求状态
            dic = resp.json()
            msg = dic['msg']
            print(f'请求状态:{msg}')
            file_log.write(f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}  请求状态:{msg}\n')
            Msg.insert('insert', f'请求状态:{msg}\n')
            window.update()

            # 获得手机号信息
            # 用if处理 否则请求失败时 sjhm 和 jrlxfs 不存在而报错
            if (dic['msg'] == 'success'):
                sjhm = dic['datas']['fields'][6]['user_set_value']  # 个人手机号码
                jrlxfs = dic['datas']['fields'][7]['user_set_value']  # 家人联系方式

                # 格式化打卡信息
                punch_data = '{\"mqszd\":\"目前所在地\",\"sfybh\":\"否\",\"mqstzk\":\"良好\",\"jcryqk\":\"未接触下述五类人员\",\"glqk\":\"自行做好防护\",\"jrcltw\":\"36.5\",\"sjhm\":\"手机号码\",\"jrlxfs\":\"家人联系方式\",\"xcsj\":\"\",\"gldd\":\"\",\"zddw\":\"定位位置<@>位置\"}'

                # 插入打卡信息
                punch_data = punch_data.replace("目前所在地", file_dic['目前所在地'][count])
                punch_data = punch_data.replace("定位位置", file_dic['定位位置'][count])
                punch_data = punch_data.replace("位置", file_dic['位置'][count])
                punch_data = punch_data.replace("手机号码", sjhm)
                punch_data = punch_data.replace("家人联系方式", jrlxfs)

                push_form = {"punch_form": punch_data, "date": get_Date(1)}

                # print(push_form)

                # 打卡
                resp = session.post(url_pushform, headers=headers, json=push_form, verify=False)

                # 打印打卡信息
                dic = resp.json()
                msg = dic['msg']
                print(f'签到状态:{msg}')
                file_log.write(
                    f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}  签到状态:{msg}\n')
                Msg.insert('insert', f'提交状态:{msg}\n')
                window.update()
            # end if
            # print(resp)
            resp.close()
        print('\n打卡完成!\n')
        file_log.write(f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}  打卡完成!\n')
        file_log.close()
        Msg.insert('insert', '\n打卡完成！\n')
        btn['state'] = 'active'
        exit['state'] = 'active'
    except Exception as e:
        Msg.insert('insert', f'发生错误:{e}\n')
        btn['state'] = 'active'
        exit['state'] = 'active'
    return


def punch_thread():
    try:
        threading.Thread(target=punch, args=()).start()  # 创建打卡线程
    except Exception as e:
        Msg.insert('insert', f'发生错误:{e}\n')


# 窗体初始化
window.geometry("230x400")
window.title('每日健康打卡')

Msg = scrolledtext.ScrolledText(window, font=('黑体', 12), height=20)
Msg.pack(fill=tkinter.X, side=tkinter.TOP)

btn = tkinter.Button(window, text="重新提交", command=punch_thread, width=14, height=1, state=DISABLED)
exit = tkinter.Button(window, text="退出", command=window.destroy, width=15, height=1)
btn.pack(side=tkinter.LEFT)
exit.pack(side=tkinter.RIGHT)

# punch()
punch_thread()
window.mainloop()
