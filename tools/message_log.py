#!/usr/bin/env python
# coding: utf-8

from pathlib import Path
import datetime
import os
import codecs
import pickle


# # 訊息寫入log文件

def write_log(text):
    """
    Write into log file.
    
    :param text: (str)
    :return: None
    """

    now = datetime.datetime.now()
    path = 'app_logs'
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
    except FileExistsError:
        # directory already exists
        pass
    
    log_name = now.strftime('%Y%m%d') + '.log'
    path = os.path.join(path, log_name)

    # In order to let json dumps chinese correctly, codecs is needed.
    # When ever use json dumps, specify ensure_ascii=False
    fp = codecs.open(path, 'a+', 'utf8')
    fp.write(now.strftime('%Y%m%d') + " " + now.strftime('%H') + ":" + now.strftime('%M') + ":" + now.strftime('%S') + "    : " + text)
    fp.close()