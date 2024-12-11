#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 20 22:03:26 2022

@author: yuyuan
"""
# import wget
import os
import time
# import webbrowser as web
import requests
from selenium import webdriver


####
series = '072'
start_number = 174820
end_number = 174825
####


path = os.path.dirname(__file__) 
max_retry = 15
image_dir = os.path.join(path, series+'/image_raw')

if not os.path.exists(image_dir):
    os.makedirs(image_dir)

driver = webdriver.Chrome()

def download_file(url, download_url,file_path):
    driver.get(url)
    time.sleep(20)
    response = requests.get(download_url)
    with open(file_path, 'wb') as file:
        file.write(response.content)

for i in range(start_number, end_number + 1):
    url = f"https://eol.jsc.nasa.gov/SearchPhotos/RequestOriginalImage.pl?mission=ISS{series}&roll=E&frame={i}&file=iss{series}e{i}.NEF"
    download_url = f"https://eol.jsc.nasa.gov/OriginalImagery/iss{series}e{i}.NEF"
    file_path = os.path.join(image_dir, f"iss{series}e{i}.NEF")
    # web.open_new(url)
    
    retry_count = 0
    file_size = 0
    while file_size < 1024 * 1024 and retry_count < max_retry:
        try:
            download_file(url, download_url, file_path) # 下载文件
            driver.execute_script("window.close();")  # 关闭当前标签页
            file_size = os.path.getsize(file_path)
            if file_size < 1024 * 1024:
                print(f"File size is less than 1MB, re-downloading...")
            else:
                print(f"Downloaded: {file_path}")
            retry_count += 1
        except Exception as e:
            print(f"Error downloading {url}: {e}")
            
    if retry_count == max_retry:
       print(f"Failed to download {url} after {max_retry} retries")
driver.quit()
# https://eol.jsc.nasa.gov/OriginalImagery/iss030e50761.NEF

# https://eol.jsc.nasa.gov/OriginalImagery/iss030e115220.NEFdownload_url
# https://eol.jsc.nasa.gov/SearchPhotos/photo.pl?mission=ISS030&roll=E&frame=115211