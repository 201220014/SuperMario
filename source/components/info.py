"""
文字信息模块
__author__ = 201220014@smail.nju.edu.cn
"""

import pygame

from .. import constants as C
from . import coin
from .. import setup, tools

pygame.font.init()  # 初始化pygame字体模块


class Info:
    """ 文字信息类 """

    def __init__(self, state, game_info):
        """
        文字信息类的构造函数
        :param state: 状态
        :param game_info: 游戏信息
        """
        self.state = state
        self.game_info = game_info
        self.create_state_labels()
        self.create_info_labels()
        self.flash_coin = coin.FlashingCoin()

    def create_state_labels(self):
        """ 根据不同的状态参数创建不同的状态标签 """
        self.state_labels = []
        if self.state == 'main_menu':
            self.state_labels.append((self.create_label('1 PLAYER GAME'), (272, 360)))
            self.state_labels.append((self.create_label('2 PLAYER GAME'), (272, 405)))
            self.state_labels.append((self.create_label('TOP - '), (290, 465)))
            self.state_labels.append((self.create_label('000000'), (400, 465)))
        elif self.state == 'load_screen':
            self.state_labels.append((self.create_label('WORLD'), (280, 200)))
            self.state_labels.append((self.create_label('1 - 1'), (430, 200)))
            self.state_labels.append((self.create_label('X    {}'.format(self.game_info['lives'])), (380, 280)))
            self.player_image = tools.get_image(setup.GRAPHICS['mario_bros'], 178, 32, 12, 16, C.BG_MULTI)
        elif self.state == 'game_over':
            self.state_labels.append((self.create_label('GAME OVER'), (280, 300)))

    def create_info_labels(self):
        """ 创建信息标签 """
        self.info_labels = []
        self.info_labels.append((self.create_label('MARIO'), (75, 30)))
        self.info_labels.append((self.create_label('WORLD'), (450, 30)))
        self.info_labels.append((self.create_label('TIME'), (625, 30)))
        self.info_labels.append((self.create_label('000000'), (75, 55)))
        self.info_labels.append((self.create_label('x00'), (300, 55)))
        self.info_labels.append((self.create_label('1 - 1'), (480, 55)))

    def create_label(self, label, size=40, width_scale=1.25, height_scale=1):
        """
        创建单个文字标签的函数
        :param label: 待创建标签的文字内容
        :param size: 字体大小
        :param width_scale: 标签宽系数
        :param height_scale: 标签高系数
        :return: 标签图片
        """
        # 初始化字体
        font = pygame.font.SysFont(C.FONT, size)
        # 创建文字对象
        label_image = font.render(label, False, (255, 255, 255))
        # 获取文字对象的矩形范围信息
        rect = label_image.get_rect()
        # 文字缩放为图片
        label_image = pygame.transform.scale(label_image, (int(rect.width * width_scale),
                                                           int(rect.height * height_scale)))
        return label_image

    def update(self):
        """ 信息更新函数 """
        # TODO: 信息的记录和更新逻辑有待补充(主要是积分逻辑)
        self.flash_coin.update()  # 金币的闪烁

    def draw(self, surface):
        """
        绘图函数
        :param surface: 绘图设备
        """
        for label in self.state_labels:
            surface.blit(label[0], label[1])
        for label in self.info_labels:
            surface.blit(label[0], label[1])
        surface.blit(self.flash_coin.image, self.flash_coin.rect)
        if self.state == 'load_screen':  # 加载界面中需要绘制马里奥图片
            surface.blit(self.player_image, (300, 270))
