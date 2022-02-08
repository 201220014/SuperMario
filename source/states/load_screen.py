"""
加载屏幕
__author__ = 201220014@smail.nju.edu.cn
"""

from ..components import info
import pygame


class LoadScreen:

    def start(self, game_info):
        """
        启动方法，为了方便多次调用同一对象，没有写在构造函数中
        :param game_info: 传入的游戏信息
        """
        self.game_info = game_info
        self.finished = False
        self.next = 'level'  # 下一个状态
        self.duration = 2000  # 持续时间
        self.timer = 0  # 计时器
        self.info = info.Info('load_screen', self.game_info)  # 游戏信息对象

    def update(self, surface, keys):
        """
        更新函数
        :param surface: 更新的表面(游戏窗口/屏幕/画布)
        :param keys: 键盘信号
        """
        self.info.update()  # 更新游戏信息
        self.draw(surface)  # 绘制加载界面
        # 计时
        if self.timer == 0:
            self.timer = pygame.time.get_ticks()
        elif pygame.time.get_ticks() - self.timer > self.duration:
            self.finished = True
            self.timer = 0

    def draw(self, surface):
        """
        绘图函数
        :param surface: 绘图设备
        """
        surface.fill((0, 0, 0))  # 填充底色为黑
        self.info.draw(surface)


class GameOver(LoadScreen):
    """ 游戏结束界面，继承加载界面 """

    def start(self, game_info):
        """
        启动函数
        :param game_info: 传入的游戏信息
        """
        # 初始化信息，类似于加载界面
        self.game_info = game_info
        self.finished = False
        self.next = 'main_menu'
        self.duration = 4000
        self.timer = 0
        self.info = info.Info('game_over', self.game_info)
