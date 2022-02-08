"""
游戏初始设置
__author__ = 201220014@smail.nju.edu.cn
"""

import pygame
from . import constants as C
from . import tools

pygame.init()  # 初始化游戏硬件条件

SCREEN = pygame.display.set_mode((C.SCREEN_W, C.SCREEN_H))  # 初始化游戏窗口
GRAPHICS = tools.load_graphics('resources/graphics')  # 导入游戏所需所有图片
