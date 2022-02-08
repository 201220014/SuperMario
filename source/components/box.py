"""
宝箱模块
__author__ = 201220014@smail.nju.edu.cn
"""

import pygame

from .. import tools, setup
from .. import constants as C
from . import powerup


class Box(pygame.sprite.Sprite):
    """ 宝箱类 """

    def __init__(self, x, y, box_type, group, level, name='box'):
        """
        宝箱类的构造函数
        :param x: x坐标
        :param y: y坐标
        :param box_type: 宝箱类型
        :param group: 宝箱装载内容对应的精灵组，比如硬币组、强化道具组
        :param level 关卡对象
        :param name: 名称
        """
        pygame.sprite.Sprite.__init__(self)
        # 属性初始化
        self.x = x
        self.y = y
        self.box_type = box_type
        self.group = group
        self.level = level
        self.name = name
        self.gravity = C.GRAVITY
        # 帧矩形范围
        self.frame_rects = [(384, 0, 16, 16), (400, 0, 16, 16), (416, 0, 16, 16), (432, 0, 16, 16)]
        # 获取帧图片
        self.frames = []
        for frame_rect in self.frame_rects:
            self.frames.append(tools.get_image(setup.GRAPHICS['tile_set'], *frame_rect, C.BRICK_MULTI))
        # 宝箱外观初始化
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
        # 宝箱状态初始化
        self.state = 'rest'
        self.timer = 0  # 计时器

    def update(self):
        """ 更新函数 """
        self.current_time = pygame.time.get_ticks()
        self.handle_states()

    def handle_states(self):
        """ 状态处理函数 """
        if self.state == 'rest':
            self.rest()
        elif self.state == 'bumped':
            self.bumped()
        elif self.state == 'open':
            self.open()

    def rest(self):
        """ 处理休息状态 """
        frame_durations = [400, 100, 100, 50]
        if self.current_time - self.timer > frame_durations[self.frame_index]:
            self.frame_index = (self.frame_index + 1) % 4
            self.timer = self.current_time
        self.image = self.frames[self.frame_index]

    def go_bumped(self):
        """ 顶起函数，由关卡类调用 """
        self.y_vel = -7
        self.state = 'bumped'

    def bumped(self):
        """ 处理顶起状态 """
        self.rect.y += self.y_vel
        self.y_vel += self.gravity

        if self.rect.y > self.y + 10:
            self.rect.y = self.y
            self.state = 'open'
            if self.box_type == 1:
                # TODO: 金币宝箱有待处理
                pass
            else:
                # 产生强化道具
                if self.level.player.fire:
                    self.group.add(powerup.create_powerup(self.rect.centerx, self.rect.centery, 'star'))
                elif self.level.player.big:
                    self.group.add(powerup.create_powerup(self.rect.centerx, self.rect.centery, 'fire_flower'))
                else:
                    self.group.add(powerup.create_powerup(self.rect.centerx, self.rect.centery, 'mushroom'))

    def open(self):
        """ 处理打状态 """
        self.frame_index = 3
        self.image = self.frames[self.frame_index]
