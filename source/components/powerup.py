"""
强化道具模块
__author__ = 201220014@smail.nju.edu.cn
"""

import pygame
from .. import setup, tools
from .. import constants as C


def create_powerup(centerx, centery, name='mushroom'):
    """
    创建一个强化道具
    :param centerx: 中心x坐标
    :param centery: 中心y坐标
    :param name: 强化道具名称
    :return: 强化道具
    """
    if name == 'mushroom':
        return Mushroom(centerx, centery)
    elif name == 'fire_flower':
        return FireFlower(centerx, centery)
    elif name == 'star':
        # TODO: 无敌星星有待完善，这里暂时用火焰花代替
        return FireFlower(centerx, centery)


class Powerup(pygame.sprite.Sprite):
    """ 强化道具类 """

    def __init__(self, centerx, centery, frame_rects):
        """
        强化道具类构造函数
        :param centerx: 中心x坐标
        :param centery: 中心y坐标
        :param frame_rects: 帧图片矩形范围
        """
        pygame.sprite.Sprite.__init__(self)
        # 初始化帧图片
        self.frames = []
        self.frame_index = 0
        for frame_rect in  frame_rects:
            frame = tools.get_image(setup.GRAPHICS['item_objects'], *frame_rect, C.POWERUP_MULTI)
            self.frames.append(frame)
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.centerx = centerx
        self.rect.centery = centery
        self.origin_y = centery - self.rect.height / 2
        # 初始化道具属性
        self.x_vel = 0
        self.direction = 1
        self.y_vel = -1
        self.gravity = 1
        self.max_y_vel = 8

    def update(self, level):
        """
        强化道具更新函数
        :param level: 关卡对象
        """
        self.current_time = pygame.time.get_ticks()
        self.update_position(level)

    def update_position(self, level):
        """
        更新位置
        :param level: 关卡对象
        """
        self.rect.x += self.x_vel
        self.check_x_collisions(level)
        self.rect.y += self.y_vel
        self.check_y_collisions(level)
        # 掉出屏幕的道具会自动消亡
        if self.rect.x < 0 or self.rect.y > C.SCREEN_H:
            self.kill()

    def check_x_collisions(self, level):
        """
        x方向碰撞检测
        :param level: 关卡对象
        """
        # 反弹逻辑
        sprite = pygame.sprite.spritecollideany(self, level.ground_items_group)
        if sprite:
            if self.direction:  # 向右
                self.direction = 0
                self.rect.right = sprite.rect.left
            else:
                self.direction = 1
                self.rect.left = sprite.rect.right
            self.x_vel *= -1

    def check_y_collisions(self, level):
        """
        y方向碰撞检测
        :param level: 关卡对象
        """
        check_group = pygame.sprite.Group(level.ground_items_group, level.box_group, level.brick_group)
        sprite = pygame.sprite.spritecollideany(self, check_group)
        if sprite:
            if self.rect.bottom > sprite.rect.top:
                self.rect.bottom = sprite.rect.top
                self.y_vel = 0
                self.state = 'walk'
        level.check_will_fall(self)


class Mushroom(Powerup):
    """ 蘑菇类，强化道具的一种，可以让马里奥变大 """

    def __init__(self, centerx, centery):
        """
        蘑菇类的构造函数
        :param centerx: 中心x坐标
        :param centery: 中心y坐标
        """
        Powerup.__init__(self, centerx, centery, [(0, 0, 16, 16)])
        self.x_vel = 2
        self.state = 'grow'
        self.name = 'mushroom'

    def update(self, level):
        """
        更新函数
        :param level: 关卡对象
        """
        if self.state == 'grow':
            self.rect.y += self.y_vel
            if self.rect.bottom < self.origin_y:
                self.state = 'walk'
        elif self.state == 'walk':
            pass  # 不需要额外处理，update_position中已经有行走的逻辑了
        elif self.state == 'fall':
            if self.y_vel < self.max_y_vel:
                self.y_vel += self.gravity
        if self.state != 'grow':
            self.update_position(level)


class FireFlower(Powerup):
    """ 火焰花类，可以让马里奥射出子弹 """

    def __init__(self, centerx, centery):
        """
        火焰花类的构造函数
        :param centerx: 中心X坐标
        :param centery: 中心y坐标
        """
        frame_rects = [(0, 32, 16, 16), (16, 32, 16, 16), (32, 32, 16, 16), (48, 32, 16, 16)]
        Powerup.__init__(self, centerx, centery, frame_rects)
        self.x_vel = 2
        self.state = 'grow'
        self.name = 'fire_flower'
        self.timer = 0

    def update(self, level):
        """
        更新函数
        :param level: 关卡对象
        """
        if self.state == 'grow':
            self.rect.y += self.y_vel
            if self.rect.bottom < self.origin_y:
                self.state = 'rest'
        self.current_time = pygame.time.get_ticks()
        if self.timer == 0:
            self.timer = self.current_time
        if self.current_time - self.timer > 30:
            self.frame_index +=1
            self.frame_index %= len(self.frames)
            self.timer = self.current_time
            self.image = self.frames[self.frame_index]


class Fireball(Powerup):
    """ 火球类，马里奥射出的子弹，可以打死怪物 """

    def __init__(self, centerx, centery, direction):
        """
        火球类的构造函数
        :param centerx: 中心x坐标
        :param centery: 中心y坐标
        :param direction: 方向
        """
        # 导入帧动画
        frame_rects = [(96, 144, 8, 8), (104, 144, 8, 8), (96, 152, 8, 8), (104, 152, 8, 8),
                       (112, 144, 16, 16), (112, 160, 16, 16), (112, 176, 16, 16)]
        Powerup.__init__(self, centerx, centery, frame_rects)
        self.name = 'fireball'
        self.state = 'fly'
        self.direction = direction
        self.x_vel = 10 if self.direction else -10
        self.y_vel = 10
        self.gravity = 1
        self.timer = 0

    def update(self, level):
        """
        更新函数
        :param level: 关卡对象
        """
        self.current_time = pygame.time.get_ticks()
        if self.state == 'fly':
            self.y_vel += self.gravity
            if self.current_time - self.timer > 200:
                self.frame_index += 1
                self.frame_index %= 4
                self.image = self.frames[self.frame_index]
                self.timer = self.current_time
            self.update_position(level)
        elif self.state == 'boom':
            if self.current_time - self.timer > 50:
                if self.frame_index < 6:
                    self.frame_index += 1
                    self.timer = self.current_time
                    self.image = self.frames[self.frame_index]
                else:
                    self.kill()

    def update_position(self, level):
        """
        更新位置
        :param level: 关卡对象
        """
        if self.state == 'fly':
            self.rect.x += self.x_vel
            self.check_x_collisions(level)
            self.rect.y += self.y_vel
            self.check_y_collisions(level)
        # 掉出屏幕的子弹自动消亡
        if self.rect.x < 0 or self.rect.y > C.SCREEN_H:
            self.kill()

    def check_x_collisions(self, level):
        """
        监测x方向碰撞
        :param level: 关卡对象
        """
        # 火球碰到障碍物爆炸
        sprite = pygame.sprite.spritecollideany(self, level.ground_items_group)
        if sprite:
            self.frame_index = 4
            self.state = 'boom'
            self.y_vel = 0
        # 火球碰到怪物之后杀死怪物并爆炸
        enemy = pygame.sprite.spritecollideany(self, level.enemy_group)
        if enemy:
            self.frame_index = 4
            self.state = 'boom'
            self.y_vel = 0
            enemy.go_die('bumped', self.direction)
            level.enemy_group.remove(enemy)
            level.dying_group.add(enemy)

    def check_y_collisions(self, level):
        """
        监测y方向碰撞
        :param level: 关卡对象
        """
        # y方向撞到障碍物反弹
        check_group = pygame.sprite.Group(level.ground_items_group, level.box_group, level.brick_group)
        sprite = pygame.sprite.spritecollideany(self, check_group)
        if sprite:
            if self.rect.bottom > sprite.rect.top:
                self.rect.bottom = sprite.rect.top
                self.y_vel = -10


class LifeMushroom(Powerup):
    # TODO: 增加生命值的蘑菇，待完善
    pass


class Star(Powerup):
    # TODO: 无敌星星，待完善
    pass

