#!/usr/bin/python

import dweepy
import time

def functionServicesDweet():
    while True:
        time.sleep(5)
        dweepy.dweet_for('InternetOfThings101DweetJR', {'Status':'1'})
        print dweepy.get_latest_dweet_for('InternetOfThings101DweetJR')
        time.sleep(5)
        print dweepy.get_latest_dweet_for('InternetOfThings101DweetJR')
        dweepy.dweet_for('InternetOfThings101DweetJR', {'Status':'0'})

if __name__ == '__main__':

    functionServicesDweet()

# End of File

