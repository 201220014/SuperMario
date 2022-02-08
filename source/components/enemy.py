"""
敌人模块
__author__ = 201220014@smail.nju.edu.cn
"""

import pygame
import pygame.sprite

from .. import setup, tools
from .. import constants as C


def create_enemy(enemy_data):
    """
    根据敌人数据创建敌人对象
    :param enemy_data: 敌人数据
    :return: 敌人对象
    """
    # 获取数据
    enemy_type = enemy_data['type']
    x, y_bottom, direction, color = enemy_data['x'], enemy_data['y'], enemy_data['direction'], enemy_data['color']
    # 创建敌人
    if enemy_type == 0:  # Goomba 蘑菇怪
        enemy = Goomba(x, y_bottom, direction, 'goomba', color)
    elif enemy_type == 1:  # Koopa 乌龟
        enemy = Koopa(x, y_bottom, direction, 'koopa', color)
    # TODO: 还有更多种类的敌人需要补充
    return enemy


class Enemy(pygame.sprite.Sprite):
    """ 敌人类 """

    def __init__(self, x, y_bottom, direction, name, frame_rects):
        """
        敌人类的构造函数
        :param x: x坐标
        :param y_bottom: 底部y坐标
        :param direction: 方向
        :param name: 名称
        :param frame_rects: 帧矩形范围序列
        """
        pygame.sprite.Sprite.__init__(self)
        # 初始化基本属性
        self.direction = direction
        self.name = name
        self.frame_index = 0
        self.left_frames = []
        self.right_frames = []
        self.timer = 0
        # 初始化运动属性
        self.x_vel = -1 * C.ENEMY_SPEED if self.direction == 0 else C.ENEMY_SPEED
        self.y_vel = 0
        self.gravity = C.GRAVITY
        self.state = 'walk'
        # 载入帧图片
        self.load_frames(frame_rects)
        self.frames = self.left_frames if self.direction == 0 else self.right_frames
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.bottom = y_bottom

    def load_frames(self, frame_rects):
        """
        载入帧图片
        :param frame_rects: 帧图片矩形范围序列
        """
        for frame_rect in frame_rects:
            left_frame = tools.get_image(setup.GRAPHICS['enemies'], *frame_rect, C.ENEMY_MULTI)
            right_frame = pygame.transform.flip(left_frame, True, False)
            self.left_frames.append(left_frame)
            self.right_frames.append(right_frame)

    def update(self, level):
        """
        更新函数
        :param level: 关卡对象
        """
        self.current_time = pygame.time.get_ticks()
        self.handle_states(level)
        self.update_position(level)

    def handle_states(self, level):
        """
        状态处理器
        :param level: 关卡对象
        """
        if self.state == 'walk':
            self.walk()
        elif self.state == 'fall':
            self.fall()
        elif self.state == 'die':
            self.die()
        elif self.state == 'trampled':
            self.trampled(level)
        elif self.state == 'slide':
            self.slide()
        # 更新图片
        if self.direction:
            self.image = self.right_frames[self.frame_index]
        else:
            self.image = self.left_frames[self.frame_index]

    def walk(self):
        """ 处理行走状态 """
        if self.current_time - self.timer > 125:
            self.frame_index = (self.frame_index + 1) % 2
            self.image = self.frames[self.frame_index]
            self.timer = self.current_time

    def fall(self):
        """ 处理下落状态 """
        if self.y_vel < 10:
            self.y_vel += self.gravity

    def die(self):
        """ 处理死亡状态 """
        self.rect.x += self.x_vel
        self.rect.y += self.y_vel
        self.y_vel += self.gravity
        if self.rect.y > C.SCREEN_H:
            self.kill()

    def trampled(self, level):
        """
        被踩踏，留待子类重写
        :param level: 关卡对象
        """
        pass

    def slide(self):
        """ 滑动，留待子类重写 """
        pass

    def update_position(self, level):
        """
        更新位置
        :param level: 关卡对象
        """
        self.rect.x += self.x_vel
        self.check_x_collisions(level)
        self.rect.y += self.y_vel
        if self.state != 'die':
            self.check_y_collisions(level)
        
    def check_x_collisions(self, level):
        """
        x方向碰撞检测
        :param level: 关卡对象
        """
        # 碰壁反向的逻辑
        sprite = pygame.sprite.spritecollideany(self, level.ground_items_group)
        if sprite:
            if self.direction:  # 向右
                self.direction = 0
                self.rect.right = sprite.rect.left
            else:
                self.direction = 1
                self.rect.left = sprite.rect.right
            self.x_vel *= -1
        # 滑动的龟壳可以杀死怪物
        if self.state == 'slide':
            enemy = pygame.sprite.spritecollideany(self, level.enemy_group)
            if enemy:
                enemy.go_die('slided', self.direction)
                level.enemy_group.remove(enemy)
                level.dying_group.add(enemy)

    def check_y_collisions(self, level):
        """
        y方向的碰撞检测
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

    def go_die(self, how, direction=1):
        """
        敌人的狗带函数
        :param how: 狗带方式
        :param direction: 狗带方向
        """
        # 狗带计时器
        self.death_timer = self.current_time
        if how in ['bumped', 'slided']:  # 击飞狗带法
            self.x_vel = C.ENEMY_SPEED * direction
            self.y_vel = -8
            self.gravity = 0.6
            self.state = 'die'
            self.frame_index = 2
        elif how == 'trampled':  # 踩踏狗带法
            self.state = 'trampled'


class Goomba(Enemy):
    """ 蘑菇怪类 """

    def __init__(self, x, y_bottom, direction, name, color):
        """
        蘑菇怪类构造函数
        :param x: x坐标(窗口坐标系中对象的坐标都默认为左上角坐标)
        :param y_bottom: 底部y坐标
        :param direction: 方向
        :param name: 名称
        :param color: 颜色(地上地下颜色不同)
        """
        # 蘑菇怪帧画面的矩形区域序列
        bright_frame_rects = [(0, 16, 16, 16), (16, 16, 16, 16), (32, 16, 16, 16)]
        dark_frame_rects = [(0, 48, 16, 16), (16, 48, 16, 16), (32, 48, 16, 16)]
        # 选择合适的帧序列
        if not color:
            frame_rects = bright_frame_rects
        else:
            frame_rects = dark_frame_rects
        # 调用父类构造函数
        Enemy.__init__(self, x, y_bottom, direction, name, frame_rects)

    def trampled(self, level):
        """
        踩踏死亡的函数
        :param level:
        """
        # 踩踏死亡的动画逻辑
        self.x_vel = 0
        self.frame_index = 2
        if self.death_timer == 0:
            self.death_timer = self.current_time
        # 延时逻辑
        if self.current_time - self.death_timer > 500:
            self.kill()


class Koopa(Enemy):
    """ 乌龟类 """

    def __init__(self, x, y_bottom, direction, name, color):
        """
        乌龟类构造函数
        :param x: x坐标
        :param y_bottom: 底部y坐标
        :param direction: 方向
        :param name: 名称
        :param color: 颜色
        """
        bright_frame_rects = [(96, 9, 16, 22), (112, 9, 16, 22), (160, 9, 16, 22)]
        dark_frame_rects = [(96, 72, 16, 22), (112, 72, 16, 22), (160, 72, 16, 22)]
        if not color:
            frame_rects = bright_frame_rects
        else:
            frame_rects = dark_frame_rects
        Enemy.__init__(self, x, y_bottom, direction, name, frame_rects)
        # 龟壳计时器
        self.shell_timer = 0

    def trampled(self, level):
        """
        踩踏变龟壳的函数
        :param level: 关卡对象
        """
        self.x_vel = 0
        self.frame_index = 2
        # 变成龟壳之后5秒钟不滑动会重新变成乌龟，下面是这个功能的实现
        if self.shell_timer == 0:
            self.shell_timer = self.current_time
        if self.current_time - self.shell_timer > 5000:
            self.state = 'walk'
            self.x_vel = - C.ENEMY_SPEED if self.direction == 0 else C.ENEMY_SPEED
            level.enemy_group.add(self)
            level.shell_group.remove(self)
            self.shell_timer = 0
