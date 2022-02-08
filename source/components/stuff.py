"""
杂项模块
__author__ = 201220014@smail.nju.edu.cn
"""

import pygame


class Item(pygame.sprite.Sprite):
    """ 物品类，各种物品的基类，继承pygame精灵类 """

    def __init__(self, x, y, w, h, name):
        """
        物品类构造函数
        :param x: x坐标
        :param y: y坐标
        :param w: 宽
        :param h: 高
        :param name: 名称
        """
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((w, h)).convert()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.name = name


class Checkpoint(Item):
    """ 检查点类，继承物品类，当马里奥触碰到检查点的时候才会刷新对应的怪物 """

    def __init__(self, x, y, w, h, checkpoint_type, enemy_groupid=None, name='checkpoint'):
        """
        检查点类
        :param x: x坐标
        :param y: y坐标
        :param w: 宽
        :param h: 高
        :param checkpoint_type: 检查点类型
        :param enemy_groupid: 敌人组序号
        :param name: 名称
        """
        Item.__init__(self, x, y, w, h, name)
        self.checkpoint_type = checkpoint_type
        self.enemy_groupid = enemy_groupid
