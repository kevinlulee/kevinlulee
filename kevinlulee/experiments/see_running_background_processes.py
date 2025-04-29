import psutil
import os
import sys

def kill_uvicorn():
    for proc in psutil.process_iter(['pid', 'name', 'username']):
        pid = proc.info['pid']
        name = proc.info['name']
        if name == 'uvicorn':
            proc.kill()
            print('killed uvicorn')
            return True

    print('uvicorn was not found')
    return 
            
