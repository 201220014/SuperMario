"""
硬币模块
__author__ = 201220014@smail.nju.edu.cn
"""

import pygame

from .. import tools, setup
from .. import constants as C


class FlashingCoin(pygame.sprite.Sprite):
    """ 闪烁的硬币，用在游戏信息中，主要是动画逻辑 """

    def __init__(self):
        """ 闪烁硬币的构造函数 """
        pygame.sprite.Sprite.__init__(self)
        # 初始化帧图片
        self.frames = []
        self.frame_index = 0
        frame_rects = [(1, 160, 5, 8), (9, 160, 5, 8), (17, 160, 5, 8), (9, 160, 5, 8)]  # 四元组为位置+大小
        self.load_frames(frame_rects)
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.x = 280
        self.rect.y = 58
        self.timer = 0

    def load_frames(self, frame_rects):
        """
        根据帧矩形范围载入帧图片
        :param frame_rects: 帧图片对应的矩形范围
        """
        sheet = setup.GRAPHICS['item_objects']
        for frame_rect in frame_rects:
            self.frames.append(tools.get_image(sheet, *frame_rect, C.BG_MULTI))  # * means decouple

    def update(self):
        """ 更新函数 """
        # 下面主要是一些动画逻辑
        self.current_time = pygame.time.get_ticks()
        frame_durations = [375, 125, 125, 125]
        if self.timer == 0:
            self.timer = self.current_time
        elif self.current_time - self.timer > frame_durations[self.frame_index]:
            self.frame_index += 1
            self.frame_index %= 4
            self.timer = self.current_time
        self.image = self.frames[self.frame_index]


class PointCoin(pygame.sprite.Sprite):
    # TODO: 积分用的硬币还有待实现，动画逻辑可以复用上面的，积分逻辑需要新写
    pass
