"""
玩家类，处理玩家相关事宜
__author__ = 201220014@smail.nju.edu.cn
"""

import pygame
import json
import os

from .. import tools, setup
from .. import constants as C
from . import powerup


class Player(pygame.sprite.Sprite):
    """ 玩家类，继承pygame精灵类"""

    def __init__(self, name):
        """
        玩家类构造函数
        :param name: 玩家名称
        """
        pygame.sprite.Sprite.__init__(self)  # python继承需要主动调用父类的构造函数
        # 初始化基本属性
        self.name = name
        self.big = False
        self.fire = False
        self.hurt_immune = False
        self.load_data()
        self.setup_states()
        self.setup_velocities()
        self.setup_timers()
        self.load_images()

    def load_data(self):
        """ 导入数据 """
        file_name = self.name + '.json'
        file_path = os.path.join('source/data/player', file_name)
        with open(file_path) as f:
            self.player_data = json.load(f)

    def setup_states(self):
        """ 设置状态 """
        self.state = 'stand'
        self.face_right = True
        self.dead = False
        self.big = False
        self.can_jump = True  # 能否跳跃，为了限制马里奥只有一段跳而设置
        self.can_shoot = True  # 能否射击
        self.hurt_immune = False  # 伤害免疫

    def setup_velocities(self):
        """ 设置速度 """
        # 取出文件中的速度数据
        speed = self.player_data['speed']
        # 设置初始速度
        self.x_vel = 0
        self.y_vel = 0
        # 根据数据文件设置各种运动学参数
        self.max_walk_vel = speed['max_walk_speed']
        self.max_run_vel = speed['max_run_speed']
        self.max_y_vel = speed['max_y_velocity']
        self.jump_vel = speed['jump_velocity']
        self.walk_accel = speed['walk_accel']
        self.run_accel = speed['run_accel']
        self.turn_accel = speed['turn_accel']
        self.gravity = C.GRAVITY
        self.anti_gravity = C.ANTI_GRAVITY
        # 设置x方向的初始最大速度和初始加速度
        self.max_x_vel = self.max_walk_vel
        self.x_accel = self.walk_accel

    def setup_timers(self):
        """ 设置计时器 """
        self.walking_timer = 0  # 行走计时器
        self.transition_timer = 0  # 状态转变计时器
        self.death_timer = 0  # 死亡计时器
        self.hurt_immune_timer = 0  # 伤害免疫计时器
        self.last_fireball_timer = 0  # 射击计时器(为了防止射击频率过快而设置)

    def load_images(self):
        """ 载入图片 """
        sheet = setup.GRAPHICS['mario_bros']
        frame_rects = self.player_data['image_frames']
        # 将各种状态下的各种帧图片分类
        self.right_small_normal_frames = []
        self.right_big_normal_frames = []
        self.right_big_fire_frames = []
        self.left_small_normal_frames = []
        self.left_big_normal_frames = []
        self.left_big_fire_frames = []
        # 帧图片列表分组
        self.small_normal_frames = [self.right_small_normal_frames, self.left_small_normal_frames]
        self.big_normal_frames = [self.right_big_normal_frames, self.left_big_normal_frames]
        self.big_fire_frames = [self.right_big_fire_frames, self.left_big_fire_frames]
        # 帧图片汇总
        self.all_frames = [
            self.right_small_normal_frames,
            self.right_big_normal_frames,
            self.right_big_fire_frames,
            self.left_small_normal_frames,
            self.left_big_normal_frames,
            self.left_big_fire_frames
        ]
        # 初始化现行使用的帧图片
        self.right_frames = self.right_small_normal_frames
        self.left_frames = self.left_small_normal_frames
        # 依据数据文件从图片文件中截取各种状态对应的帧图片
        for group, group_frame_rects in frame_rects.items():
            for frame_rect in group_frame_rects:
                right_image = tools.get_image(sheet, frame_rect['x'], frame_rect['y'],
                                              frame_rect['width'], frame_rect['height'], C.PLAYER_MULTI)
                left_image = pygame.transform.flip(right_image, True, False)
                if group == 'right_small_normal':
                    self.right_small_normal_frames.append(right_image)
                    self.left_small_normal_frames.append(left_image)
                elif group == 'right_big_normal':
                    self.right_big_normal_frames.append(right_image)
                    self.left_big_normal_frames.append(left_image)
                elif group == 'right_big_fire':
                    self.right_big_fire_frames.append(right_image)
                    self.left_big_fire_frames.append(left_image)
        # 初始化帧序号和当前帧序列
        self.frame_index = 0
        self.frames = self.right_frames
        # 初始化当前图片和矩形范围
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()

    def update(self, keys, level):
        """
        更新玩家
        :param keys: 键盘信号
        :param level: 关卡对象
        """
        self.current_time = pygame.time.get_ticks()  # 获取当前时间
        self.handle_states(keys, level)  # 处理当前状态
        self.is_hurt_immune()  # 判断是否免疫伤害

    def is_hurt_immune(self):
        """ 判断是否伤害免疫并处理 """
        # 下面主要是一段动画逻辑，马里奥免伤的时候会闪烁
        if self.hurt_immune:
            if self.hurt_immune_timer == 0:
                self.hurt_immune_timer = self.current_time
                self.blank_image = pygame.Surface((1, 1))
            elif self.current_time - self.hurt_immune_timer < 2000:
                if (self.current_time - self.hurt_immune_timer) % 100 < 50:
                    self.image = self.blank_image
            else:
                self.hurt_immune = False
                self.hurt_immune_timer = 0

    def handle_states(self, keys, level):
        """
        不同状态的处理函数
        :param keys: 键盘信号
        :param level: 关卡对象
        """
        self.can_jump_or_not(keys)
        self.can_shoot_or_not(keys)
        # 处理不同的状态
        if self.state == 'stand':
            self.stand(keys, level)
        elif self.state == 'walk':
            self.walk(keys, level)
        elif self.state == 'jump':
            self.jump(keys, level)
        elif self.state == 'fall':
            self.fall(keys, level)
        elif self.state == 'die':
            self.die(keys)
        elif self.state == 'small_to_big':
            self.small_to_big(keys)
        elif self.state == 'big_to_small':
            self.big_to_small(keys)
        elif self.state == 'big_to_fire':
            self.big_to_fire(keys)
        # 根据朝向选择相应的帧
        if self.face_right:
            self.image = self.right_frames[self.frame_index]
        else:
            self.image = self.left_frames[self.frame_index]

    def can_jump_or_not(self, keys):
        """ 判断是否能够跳跃 """
        # 主要是为了防止一直按着导致一直跳跃，避免多段跳
        if not keys[pygame.K_a]:
            self.can_jump = True

    def can_shoot_or_not(self, keys):
        """ 判断是否能够射击 """
        # 主要是为了防止连射
        if not keys[pygame.K_s]:
            self.can_shoot = True

    def stand(self, keys, level):
        """
        处理站立状态
        :param keys: 键盘信号
        :param level: 关卡对象
        """
        # 状态属性设置
        self.frame_index = 0
        self.x_vel = 0
        self.y_vel = 0
        # 根据按键信号作出操作并切换状态
        if keys[pygame.K_RIGHT]:
            self.face_right = True
            self.state = 'walk'
        elif keys[pygame.K_LEFT]:
            self.face_right = False
            self.state = 'walk'
        elif keys[pygame.K_a] and self.can_jump:
            self.state = 'jump'
            self.y_vel = self.jump_vel
        elif keys[pygame.K_s] and self.fire and self.can_shoot:
            self.shoot_fireball(level)

    def walk(self, keys, level):
        """
        处理行走状态
        :param keys: 键盘信号
        :param level: 关卡对象
        """
        # 处理不同的按键信号
        if keys[pygame.K_s]:  # 发射键具有加速效果
            self.max_x_vel = self.max_run_vel
            self.x_accel = self.run_accel
            if self.fire and self.can_shoot:
                self.shoot_fireball(level)
        else:
            self.max_x_vel = self.max_walk_vel
            self.x_accel = self.walk_accel
        if keys[pygame.K_a] and self.can_jump:  # 跳跃键
            self.state = 'jump'
            self.y_vel = self.jump_vel
        # 帧动画，实现行走动画效果
        if self.current_time - self.walking_timer > self.calc_frame_duration():
            if self.frame_index < 3:
                self.frame_index += 1
            else:
                self.frame_index = 1
            self.walking_timer = self.current_time
        # 左右键调整方向
        if keys[pygame.K_RIGHT]:
            self.face_right = True
            if self.x_vel < 0:
                self.frame_index = 5
                self.x_accel = self.turn_accel
            self.x_vel = self.calc_vel(self.x_vel, self.x_accel, self.max_x_vel, True)
        elif keys[pygame.K_LEFT]:
            self.face_right = False
            if self.x_vel > 0:
                self.frame_index = 5
                self.x_accel = self.turn_accel
            self.x_vel = self.calc_vel(self.x_vel, self.x_accel, self.max_x_vel, False)
        else:  # 松开左右键回到站立状态
            if self.face_right:
                self.x_vel -= self.x_accel
                if self.x_vel < 0:
                    self.x_vel = 0
                    self.state = 'stand'
            else:
                self.x_vel += self.x_accel
                if self.x_vel > 0:
                    self.x_vel = 0
                    self.state = 'stand'

    def calc_frame_duration(self):
        """ 计算持续时间，实现速度越快摆臂(帧切换)越快的效果 """
        duration = 80 - 60 / self.max_run_vel * abs(self.x_vel) + 80
        return duration

    def jump(self, keys, level):
        """
        处理跳跃状态
        :param keys: 键盘信号
        :param level:  关卡对象
        """
        self.frame_index = 4  # 切换到跳跃对应的帧图片
        self.y_vel += self.anti_gravity  # 更新速度
        self.can_jump = False  # 拒绝多段跳
        # 处理键盘信号
        if self.y_vel >= 0:  # 速度向下的时候切换为下落状态
            self.state = 'fall'
        if keys[pygame.K_RIGHT]:
            self.x_vel = self.calc_vel(self.x_vel, self.x_accel, self.max_x_vel, True)
        elif keys[pygame.K_LEFT]:
            self.x_vel = self.calc_vel(self.x_vel, self.x_accel, self.max_x_vel, False)
        elif keys[pygame.K_s] and self.fire and self.can_shoot:
            self.shoot_fireball(level)
        if not keys[pygame.K_a]:
            self.state = 'fall'

    def fall(self, keys, level):
        """
        处理下落状态
        :param keys: 键盘信号
        :param level:  关卡对象
        """
        # 更新y方向速度
        self.y_vel = self.calc_vel(self.y_vel, self.gravity, self.max_y_vel)
        # 处理键盘事件
        if keys[pygame.K_RIGHT]:
            self.x_vel = self.calc_vel(self.x_vel, self.x_accel, self.max_x_vel, True)
        elif keys[pygame.K_LEFT]:
            self.x_vel = self.calc_vel(self.x_vel, self.x_accel, self.max_x_vel, False)
        elif keys[pygame.K_s] and self.fire and self.can_shoot:
            self.shoot_fireball(level)

    def die(self, keys):
        """
        处理死亡状态
        :param keys: 键盘信号
        """
        # TODO: 偷偷地设置一个秘密按键，让马里奥原地复活 -- 手写外挂
        self.rect.y += self.y_vel
        self.y_vel += self.anti_gravity

    def small_to_big(self, keys):
        """
        处理由小变大状态
        :param keys: 键盘信号
        """
        # 下面主要是一段动画逻辑
        frame_dur = 65
        sizes = [1, 0, 1, 0, 1, 2, 0, 1, 2, 0, 2]
        frames_and_idx = [(self.small_normal_frames, 0), (self.small_normal_frames, 7), (self.big_normal_frames, 0)]
        if self.transition_timer == 0:
            self.big = True
            self.transition_timer = self.current_time
            self.changing_idx = 0
        elif self.current_time - self.transition_timer > frame_dur:
            self.transition_timer = self.current_time
            frames, idx = frames_and_idx[sizes[self.changing_idx]]
            self.change_player_image(frames, idx)
            self.changing_idx += 1
            if self.changing_idx == len(sizes):
                self.transition_timer = 0
                self.state = 'walk'
                self.right_frames = self.right_big_normal_frames
                self.left_frames = self.left_big_normal_frames

    def big_to_small(self, keys):
        """
        处理由大到小状态
        :param keys: 键盘信号
        """
        # 下面主要是一段动画逻辑
        frame_dur = 65
        sizes = [2, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]
        frames_and_idx = [(self.small_normal_frames, 8), (self.big_normal_frames, 8), (self.big_normal_frames, 4)]
        if self.transition_timer == 0:
            self.big = False
            self.fire = False
            self.transition_timer = self.current_time
            self.changing_idx = 0
        elif self.current_time - self.transition_timer > frame_dur:
            self.transition_timer = self.current_time
            frames, idx = frames_and_idx[sizes[self.changing_idx]]
            self.change_player_image(frames, idx)
            self.changing_idx += 1
            if self.changing_idx == len(sizes):
                self.transition_timer = 0
                self.state = 'walk'
                self.right_frames = self.right_small_normal_frames
                self.left_frames = self.left_small_normal_frames

    def big_to_fire(self, keys):
        """
        处理由大到火状态
        :param keys: 键盘信号
        """
        # 下面主要是一段动画逻辑
        frame_dur = 65
        sizes = [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]
        frames_and_idx = [(self.big_fire_frames, 3), (self.big_normal_frames, 3)]
        if self.transition_timer == 0:
            self.fire = True
            self.transition_timer = self.current_time
            self.changing_idx = 0
        elif self.current_time - self.transition_timer > frame_dur:
            self.transition_timer = self.current_time
            frames, idx = frames_and_idx[sizes[self.changing_idx]]
            self.change_player_image(frames, idx)
            self.changing_idx += 1
            if self.changing_idx == len(sizes):
                self.transition_timer = 0
                self.state = 'walk'
                self.right_frames = self.right_big_fire_frames
                self.left_frames = self.left_big_fire_frames

    def change_player_image(self, frames, idx):
        """
        状态转化的时候被调用来切换人物图片帧的帮助函数
        :param frames: 帧列表
        :param idx: 帧序号
        """
        self.frame_index = idx
        if self.face_right:
            self.right_frames = frames[0]
            self.image = self.right_frames[self.frame_index]
        else:
            self.left_frames = frames[1]
            self.image = self.left_frames[self.frame_index]
        last_frame_bottom = self.rect.bottom
        last_frame_centerx = self.rect.centerx
        self.rect = self.image.get_rect()
        self.rect.bottom = last_frame_bottom
        self.rect.centerx = last_frame_centerx

    def calc_vel(self, vel, accel, max_vel, is_positive=True):
        """
        计算速度(实现变速运动)
        :param vel: 初速度
        :param accel: 加速度
        :param max_vel: 最大速度
        :param is_positive: 方向
        """
        if is_positive:
            return min(vel + accel, max_vel)
        return max(vel - accel, -max_vel)

    def shoot_fireball(self, level):
        """
        发射火球
        :param level:
        """
        if self.current_time - self.last_fireball_timer > 300:  # 控制发射频率
            self.frame_index = 6
            fireball = powerup.Fireball(self.rect.centerx, self.rect.centery, self.face_right)
            level.powerup_group.add(fireball)
            self.can_shoot = False
            self.last_fireball_timer = self.current_time

    def go_die(self):
        """ 角色死亡，留待关卡类在合适的时候调用 """
        self.dead = True
        self.y_vel = self.jump_vel
        self.frame_index = 6
        self.state = 'die'
        self.death_timer = self.current_time
