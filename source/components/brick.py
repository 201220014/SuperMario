"""
砖块和碎砖块
__author__ = 201220014@smail.nju.edu.cn
"""

import pygame

from .. import tools, setup
from .. import constants as C
from . import powerup


class Brick(pygame.sprite.Sprite):
    """ 砖块类 """

    def __init__(self, x, y, brick_type, group, level, color=None, name='brick'):
        """
        砖块类构造函数
        :param x: x坐标
        :param y: y坐标
        :param brick_type: 砖块类型
        :param group: 装载的东西所在的精灵组
        :param level: 关卡对象
        :param color: 颜色
        :param name: 名称
        """
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.brick_type = brick_type
        self.name = name
        self.group = group
        self.level = level
        # 帧图片矩形信息
        bright_frame_rects = [(16, 0, 16, 16), (48, 0, 16, 16)]
        dark_frame_rects = [(16, 32, 16, 16), (48, 32, 16, 16)]
        if not color:
            self.frame_rects = bright_frame_rects
        else:
            self.frame_rects = dark_frame_rects
        # 获取帧图片
        self.frames = []
        for frame_rect in self.frame_rects:
            self.frames.append(tools.get_image(setup.GRAPHICS['tile_set'], *frame_rect, C.BRICK_MULTI))
        self.frame_index = 0
        # 初始化砖块属性
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
        self.state = 'rest'
        self.gravity = C.GRAVITY

    def update(self):
        """ 更新函数，由pygame负责调用 """
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
        pass  # 休息状态无需处理，不过留一个空间在这里，以防以后需要进行某些操作

    def go_bumped(self):
        """ 处理被顶起状态 """
        self.y_vel = -7  # 给一个向上的初速度
        self.state = 'bumped'  # 更新状态属性

    def bumped(self):
        """ 顶起方法 """
        # 动画逻辑
        self.rect.y += self.y_vel
        self.y_vel += self.gravity
        # 结束顶起状态
        if self.rect.y > self.y + 5:
            self.rect.y = self.y
            if self.brick_type == 0:  # 空砖块
                self.state = 'rest'
            elif self.brick_type == 1:  # 藏金币的砖块
                self.state = 'open'
            else:  # 藏强化道具的砖块
                # 产生强化道具
                # TODO: 需要补充一些判断逻辑使得已经刷新过道具的砖块不再刷新道具
                if self.level.player.fire:
                    self.group.add(powerup.create_powerup(self.rect.centerx, self.rect.centery, 'star'))
                elif self.level.player.big:
                    self.group.add(powerup.create_powerup(self.rect.centerx, self.rect.centery, 'fire_flower'))
                else:
                    self.group.add(powerup.create_powerup(self.rect.centerx, self.rect.centery, 'mushroom'))
                self.state = 'rest'

    def open(self):
        """ 砖块打开 """
        self.frame_index = 1
        self.image = self.frames[self.frame_index]

    def smashed(self, group):
        """
        砖块碎裂
        :param group: 砖块所在的精灵组
        """
        debris = [(self.rect.x, self.rect.y, -2, -10), (self.rect.x, self.rect.y, 2, -10),
                  (self.rect.x, self.rect.y, -2, -5), (self.rect.x, self.rect.y, 2, -5)]
        for d in debris:
            group.add(Debris(*d))
        self.kill()


class Debris(pygame.sprite.Sprite):
    """ 砖块碎片，在砖块被大马里奥顶碎的时候用来制作动画 """

    def __init__(self, x, y, x_vel, y_vel):
        """
        碎片构造函数
        :param x: x坐标
        :param y: y坐标
        :param x_vel: x速度
        :param y_vel: y速度
        """
        pygame.sprite.Sprite.__init__(self)
        self.image = tools.get_image(setup.GRAPHICS['tile_set'], 68, 20, 8, 8, C.BRICK_MULTI, (0, 0, 0))
        self.rect = self.image.get_rect()
        self.name = 'debris'
        self.rect.x = x
        self.rect.y = y
        self.x_vel = x_vel
        self.y_vel = y_vel
        self.gravity = C.GRAVITY

    def update(self, *args):
        """ 更新状态 """
        self.rect.x += self.x_vel
        self.rect.y += self.y_vel
        self.y_vel += self.gravity
        # 碎砖块掉出屏幕的时候消亡
        if self.rect.y > C.SCREEN_H:
            self.kill()
