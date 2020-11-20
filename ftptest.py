#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2020-11-20 23:52:06
# @Author  : Your Name (you@example.org)
# @Link    : http://example.org
# @Version : $Id$

import os
import unittest # 单元测试用例
import os
import re
import sys
from ftplib import FTP 
# 定义了FTP类，实现ftp上传和下载
# 
# retrbinary(command,callback[,maxblocksize[,rest]]): 获取一个二进制文件，callback在收到数据块时被回调；
# 命令应该是'RETR filename'；rest参数指定文件起始的偏移字节数；

class MyFTP(FTP):
    """
    cmd:命令
    callback:回调函数
    fsize:服务器中文件总大小
    rest:已传送文件大小
    """
    def retrbinary(self, cmd, callback, fsize=0, rest=0):  
        cmpsize = rest
        self.voidcmd('TYPE I')
        #此命令实现从指定位置开始下载,以达到续传的目的
        conn = self.transfercmd(cmd, rest)
        while 1:
            if fsize: 
                if (fsize-cmpsize) >= 1024:
                    blocksize = 1024
                else:
                    blocksize = fsize - cmpsize
                ret = float(cmpsize)/fsize
                num = ret*100
                # 实现同一行打印下载进度
                print ('下载进度: %.2f%%'%num, end='\r')  
                data = conn.recv(blocksize)  
                if not data:  
                    break  
                callback(data)
            cmpsize += blocksize  
        conn.close()  
        return self.voidresp()

host = '127.0.0.1'
port = 2121
username = ''
password = ''
ftp = MyFTP()
ftp.connect(host,port)
ftp.login(username, password)

""" 
RemoteFile: 要下载的文件名（服务器中）
LocalFile: 本地文件路径
bufsize: 服务器中文件大小 
"""
def ftp_download(LocalFile, RemoteFile, bufsize):  
    # 本地是否有此文件，来确认是否启用断点续传
    if not os.path.exists(LocalFile):
        with open(LocalFile, 'wb') as f:
            ftp.retrbinary('RETR %s' % RemoteFile, f.write, bufsize)
            f.close()
            # ftp.set_debuglevel(0)             #关闭调试模式
            return True
    else:
        p = re.compile(r'\\',re.S)
        LocalFile = p.sub('/', LocalFile)
        localsize = os.path.getsize(LocalFile)
        with open(LocalFile, 'ab+') as f:
            ftp.retrbinary('RETR %s' % RemoteFile, f.write, bufsize, localsize)
            f.close()
            # ftp.set_debuglevel(0)             #关闭调试模式
            return True

# 下载整个目录下的文件
def DownLoadFileTree(LocalDir, RemoteDir):
    print("RemoteDir:", RemoteDir)

    if not os.path.exists(LocalDir):
        os.makedirs(LocalDir)
    
    # 打开该远程目录
    ftp.cwd(RemoteDir)

    # 获取该目录下所有文件名，列表形式
    RemoteNames = ftp.nlst()
    for file in RemoteNames:
        Local = os.path.join(LocalDir, file)  # 下载到当地的全路径
        print(ftp.nlst(file))  # [如test.txt]
        if file.find(".") == -1:  #是否子目录 如test.txt就非子目录
            if file.find("README") == -1:
                if not os.path.exists(Local):
                    os.makedirs(Local)
                DownLoadFileTree(Local, file)  # 下载子目录路径
            else:
                ftp.voidcmd('TYPE I') # 将传输模式改为二进制模式 ,避免提示 ftplib.error_perm: 550 SIZE not allowed in ASCII
                bufsize = ftp.size(file) #服务器里的文件总大小
                print(bufsize)
                ftp_download(Local, file, bufsize)
        else:
            ftp.voidcmd('TYPE I') # 将传输模式改为二进制模式 ,避免提示 ftplib.error_perm: 550 SIZE not allowed in ASCII
            bufsize = ftp.size(file) #服务器里的文件总大小
            print(bufsize)
            ftp_download(Local, file, bufsize)
    ftp.cwd("..")  # 返回路径最外侧
    return

class TestDownloader(unittest.TestCase):
   def setUp(self):
        print('------Start------')

   def test_download(self):
        RemoteFile = '/ftp/' #server端创建的ftp文件夹
        LocalFile = 'F:/'
        #RemoteFile = '/ftp/111.jpg'
        #LocalFile = '111.jpg'
        DownLoadFileTree(LocalFile, RemoteFile)
        #ftp_download(LocalFile,RemoteFile)



 
   #def tearDown(self):
        print('Finish!')
 
if __name__ == '__main__':





   unittest.main()