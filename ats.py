#coding:utf-8

import serial
import pygame
import time
import sys
from timeout_decorator import timeout, TimeoutError
import os

PORT = '/dev/ats'

pygame.mixer.init(44100, -16, 1, 256)
bell_sound = pygame.mixer.Sound(os.path.dirname(__file__) + '/ats_bell.wav')
tekkin_sound = pygame.mixer.Sound(os.path.dirname(__file__) + '/ats_tekkin.wav')
button = serial.Serial(PORT, dsrdtr=True, rtscts=True)

button.dtr = True


def getButton(button):
    while True:
        try:
            return [button.dsr, button.cts]
        except OSError:
            print('disconnected')
            exit()

@timeout(0.1)
def isZaisen():
    zaisen = input()
    print(zaisen)
    if 'ZAISEN'in zaisen:
        print('zaisen!')
        return True
    return False

# state 1: 待機 1周目在線でstate 2へ
# state 2: 2周目待ち 復帰ボタン1秒押下によりstate 1へ戻る
# state 2: 在線によりベル鳴動
# state 3: 確認ボタンによりベル停止、鉄琴鳴動
# state 4: 復帰ボタンにより鉄琴停止、state 1へ

while True:
    state = 1
    reset_count = 0
    while state == 1 or state == 2:
        try:
            # 標準入力でZAISENと与えられると在線検知
            if isZaisen():
                state += 1
                if state == 3:
                    reset_count = 0
                    bell_sound.play(loops=-1)
        except TimeoutError:
            if getButton(button)[1]:
                reset_count += 1
            else:
                reset_count = 0
            if reset_count >= 5:
                state = 1
            time.sleep(0.01)
    
    while state == 3:
        if getButton(button)[0]:
            reset_count += 1
        else:
            reset_count = 0
        if reset_count >= 5:
            bell_sound.stop()
            tekkin_sound.play(loops=-1)
            reset_count = 0
            state += 1
        time.sleep(0.01)
    
    while state == 4:
        if getButton(button)[1]:
            reset_count += 1
        else:
            reset_count = 0
        if reset_count >= 5:
            tekkin_sound.stop()
            state += 1
        time.sleep(0.01)
        
    time.sleep(0.01)
