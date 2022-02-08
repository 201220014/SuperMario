"""
关卡类，整个游戏最复杂的部分
__author__ = 201220014@smail.nju.edu.cn
"""

import json  # 处理JavaScrip Object Notation数据文件的库
import os  # 标准输入输出库
import pygame

from .. import constants as C
from .. import setup
from ..components import info, player, stuff, brick, box, enemy  # 游戏的各个组件


class Level:
    """
    关卡类
    """

    def start(self, game_info):
        """
        关卡类的驱动方法，不采用构造函数是为了切换关卡的时候无需创建新的对象
        :param game_info: 游戏信息
        """
        self.game_info = game_info
        self.finished = False
        self.next = 'game_over'  # 下一个状态
        self.info = info.Info('level', self.game_info)  #游戏信息
        self.load_map_data()  # 载入地图数据
        # 游戏初始设置
        self.setup_background()
        self.setup_start_position()
        self.setup_player()
        self.setup_ground_items()
        self.setup_bricks_and_boxes()
        self.setup_enemies()
        self.setup_checkpoints()

    def load_map_data(self):
        """ 从json文件中载入地图数据，包括各个游戏组件的位置、大小等 """
        file_name = 'level_1.json'
        # TODO: 暂时只写了一个关卡，需要补充关卡之间的切换逻辑
        file_path = os.path.join('source/data/maps', file_name)
        with open(file_path) as f:
            self.map_data = json.load(f)  # 载入json文件, 相当于一个字典

    def setup_background(self):
        """ 设置背景 """
        # 根据数据文指示获取背景图
        self.image_name = self.map_data['image_name']
        self.background = setup.GRAPHICS[self.image_name]
        # 放缩背景图以适应窗口
        rect = self.background.get_rect()
        self.background = pygame.transform.scale(self.background, (int(rect.width * C.BG_MULTI),
                                                                   int(rect.height * C.BG_MULTI)))
        # 记录背景矩形信息
        self.background_rect = self.background.get_rect()
        # 游戏窗口矩形信息
        self.game_window = setup.SCREEN.get_rect()
        # 游戏场景: 背景大小的空画布
        self.game_ground = pygame.Surface((self.background_rect.width, self.background_rect.height))

    def setup_start_position(self):
        """ 设置场景 始末位置 和 玩家 初始位置 """
        self.positions = []
        for data in self.map_data['maps']:
            self.positions.append((data['start_x'], data['end_x'], data['player_x'], data['player_y']))
        # TODO: 马里奥是有可能通过特殊的管道切换地图和场景的，这个功能有待实现，我暂时只能从开始进入场景
        self.start_x, self.end_x, self.player_x, self.player_y = self.positions[0]

    def setup_player(self):
        """ 设置玩家 """
        self.player = player.Player('mario')  # 初始化玩家对象
        # TODO: 超级玛丽有两个角色:mario和luigi,当支持2P模式的时候这里需要修改
        self.player.rect.x = self.game_window.x + self.player_x  # 这么写是为了以后完善中途通过管道切入场景的功能
        self.player.rect.bottom = self.player_y  #

    def setup_ground_items(self):
        """ 设置地面障碍物 """
        # 初始化空的精灵组，使用精灵组是为了以后碰撞检测方便
        self.ground_items_group = pygame.sprite.Group()
        for name in ['ground', 'pipe', 'step']:  # 障碍物包地面、管道和台阶
            for item in self.map_data[name]:
                self.ground_items_group.add(stuff.Item(item['x'], item['y'], item['width'], item['height'], name))

    def setup_bricks_and_boxes(self):
        """ 设置砖块和宝箱 """
        self.brick_group = pygame.sprite.Group()  # 砖块组
        self.box_group = pygame.sprite.Group()  # 宝箱组
        # 硬币 和 强化道具 藏在砖块和宝箱中
        self.coin_group = pygame.sprite.Group()  # 硬币组
        self.powerup_group = pygame.sprite.Group()  # 强化道具组(蘑菇、花、星星等)
        # 设置砖块
        if 'brick' in self.map_data:
            for brick_data in self.map_data['brick']:
                x, y = brick_data['x'], brick_data['y']
                brick_type = brick_data['type']
                if brick_type == 0:  # 空砖块
                    if 'brick_num' in brick_data:
                        # TODO: 批量初始化砖块的功能有待实现
                        pass
                    else:
                        self.brick_group.add(brick.Brick(x, y, brick_type, None, self))
                elif brick_type == 1:  # 有硬币的砖块
                    self.brick_group.add(brick.Brick(x, y, brick_type, self.coin_group, self))
                else:  # 有强化道具的砖块
                    self.brick_group.add(brick.Brick(x, y, brick_type, self.powerup_group, self))
        # 设置宝箱
        if 'box' in self.map_data:
            for box_data in self.map_data['box']:
                x, y = box_data['x'], box_data['y']
                box_type = box_data['type']
                if box_type == 1:  # 硬币宝箱
                    self.box_group.add(box.Box(x, y, box_type, self.coin_group, self))
                else:  # 强化宝箱
                    self.box_group.add(box.Box(x, y, box_type, self.powerup_group, self))

    def setup_enemies(self):
        """ 设置敌人，包括怪物、火球、子弹等等 """
        self.dying_group = pygame.sprite.Group()  # 死亡组
        self.enemy_group = pygame.sprite.Group()  # 敌人组
        self.shell_group = pygame.sprite.Group()  # 龟壳组(因为乌龟壳比较特殊)
        # 根据敌人数据创建敌人对象
        self.enemy_group_dict = {}
        for enemy_group_data in self.map_data['enemy']:
            group = pygame.sprite.Group()
            for enemy_group_id, enemy_list in enemy_group_data.items():
                for enemy_data in enemy_list:
                    group.add(enemy.create_enemy(enemy_data))
                self.enemy_group_dict[enemy_group_id] = group

    def setup_checkpoints(self):
        """ 设置检查点，马里奥走到检查点的时候刷新该处对应的怪物 """
        self.checkpoint_group = pygame.sprite.Group()  # 检查点组
        # 根据检查点数据创建检查点对象
        for item in self.map_data['checkpoint']:
            x, y, w, h = item['x'], item['y'], item['width'], item['height']
            checkpoint_type = item['type']
            enemy_groupid = item.get('enemy_groupid')
            self.checkpoint_group.add(stuff.Checkpoint(x, y, w, h, checkpoint_type, enemy_groupid))

    def update(self, surface, keys):
        """
        关卡更新函数，该函数在每一帧都会被驱动程序调用
        :param surface: 供更新的画布
        :param keys: 键盘信号
        """
        # 获取当前帧数(相当于获取当前时间)
        self.current_time = pygame.time.get_ticks()
        # 玩家更新
        self.player.update(keys, self)

        if self.player.dead:
            if self.current_time - self.player.death_timer > 3000:
                self.finished = True
                self.update_game_info()
        elif self.is_frozen():
            pass  # 马里奥变身时会暂停关卡
        else:
            self.update_player_position()
            self.check_checkpoints()
            self.check_if_go_die()
            self.update_game_window()
            self.brick_group.update()
            self.box_group.update()
            self.enemy_group.update(self)
            self.dying_group.update(self)
            self.shell_group.update(self)
            self.coin_group.update()
            self.powerup_group.update(self)

        self.info.update()
        self.draw(surface)  # 将更新完的状态回显到游戏主屏幕上

    def update_game_info(self):
        """ 更新游戏信息 """
        if self.player.dead:
            self.game_info['lives'] -= 1
        if self.game_info['lives'] == 0:
            self.next = 'game_over'
        else:
            self.next = 'load_screen'

    def is_frozen(self):
        """ 判断关卡是否冻结 """
        # 在马里奥变身的时候关卡会冻结一会儿
        return self.player.state in ['small_to_big', 'big_to_fire', 'fire_to_big', 'big_to_small']

    def update_player_position(self):
        """ 更新玩家位置 """
        # x方向位置更新
        self.player.rect.x += self.player.x_vel
        if self.player.rect.x < self.start_x:
            self.player.rect.x = self.start_x
        if self.player.rect.right > self.end_x:
            self.player.rect.right = self.end_x
        # x方向碰撞检测
        self.check_x_collisions()
        if not self.player.dead:
            self.player.rect.y += self.player.y_vel  # y方向位置更新
            self.check_y_collisions()  # y方向碰撞检测

    def check_x_collisions(self):
        """ x方向碰撞检测 """
        # x方向障碍物碰撞检测，包括地面物品(地面、管道、台阶)、砖块、宝箱
        check_group = pygame.sprite.Group(self.ground_items_group, self.brick_group, self.box_group)
        collided_sprite = pygame.sprite.spritecollideany(self.player, check_group)
        if collided_sprite:
            self.adjust_player_x(collided_sprite)
        # x方向强化道具碰撞检测
        powerup = pygame.sprite.spritecollideany(self.player, self.powerup_group)
        if powerup:
            if powerup.name == 'fireball':
                # 马里奥发射的火球对马里奥自己并无影响
                pass
            elif powerup.name == 'mushroom':
                # 蘑菇让玩家变大
                self.player.state = 'small_to_big'
                powerup.kill()
            elif powerup.name == 'fire_flower':
                # 火焰花让玩家能够发射子弹
                self.player.state = 'big_to_fire'
                powerup.kill()
        if self.player.hurt_immune:
            # 伤害免疫状态的马里奥不会在x方向和敌人与龟壳碰撞，这里提前结束碰撞检测
            return
        # x方向敌人碰撞检测
        enemy = pygame.sprite.spritecollideany(self.player, self.enemy_group)
        if enemy:
            if self.player.big:
                # 变大的马里奥撞到敌人会变小
                self.player.state = 'big_to_small'
                self.player.hurt_immune = True  # 由大变小的时候有一段时间的伤害免疫
            else:
                # 小马里奥撞到敌人会直接狗带
                self.player.go_die()
        # x方向龟壳碰撞检测
        shell = pygame.sprite.spritecollideany(self.player, self.shell_group)
        if shell:
            if shell.state == 'slide':  # x方向碰到滑动的龟壳会狗带
                if self.player.big:
                    # 变大的马里奥撞到敌人会变小
                    self.player.state = 'big_to_small'
                    self.player.hurt_immune = True  # 由大变小的时候有一段时间的伤害免疫
                else:
                    # 小马里奥撞到敌人会直接狗带
                    self.player.go_die()
            else:
                # x方向碰到静止的龟壳让龟壳向反方向滑动
                if self.player.rect.x < shell.rect.x:
                    shell.x_vel = 10
                    shell.rect.x += 40
                    shell.direction = 1
                else:
                    shell.x_vel = -10
                    shell.rect.x -= 14
                    shell.direction = 0
                shell.state = 'slide'

    def adjust_player_x(self, sprite):
        """
        调整x方向的位置，阻止马里奥在被撞倒的时候继续前进
        :param sprite: 被撞到的精灵
        """
        if self.player.rect.x < sprite.rect.x:
            self.player.rect.right = sprite.rect.left
        else:
            self.player.rect.left = sprite.rect.right
        self.player.x_vel = 0

    def check_y_collisions(self):
        """ y方向的碰撞检测 """
        # 地面障碍物
        ground_item = pygame.sprite.spritecollideany(self.player, self.ground_items_group)
        # y方向上砖块和宝箱不再是障碍物，而是可以顶起来互动的
        brick = pygame.sprite.spritecollideany(self.player, self.brick_group)
        box = pygame.sprite.spritecollideany(self.player, self.box_group)
        # y方向可以击飞或踩扁敌人
        enemy = pygame.sprite.spritecollideany(self.player, self.enemy_group)

        # 砖块和宝箱通常挨得近，同时碰到的时候选择最近的触发
        if box and brick:
            to_brick = abs(self.player.rect.centerx - brick.rect.centerx)
            to_box = abs(self.player.rect.centerx - box.rect.centerx)
            if to_brick > to_box:
                brick = None
            else:
                box = None

        if ground_item:
            self.adjust_player_y(ground_item)
        elif brick:
            self.adjust_player_y(brick)
        elif box:
            self.adjust_player_y(box)
        elif enemy:
            if self.player.hurt_immune:
                return  # 伤害免疫的时候无法踩怪
            self.enemy_group.remove(enemy)
            if enemy.name == 'koopa':
                # 乌龟被踩会变龟壳
                self.shell_group.add(enemy)
            else:
                # 其他怪物被踩直接死亡
                self.dying_group.add(enemy)
            if self.player.y_vel < 0:
                how = 'bumped'
            else:
                how = 'trampled'
                self.player.state = 'jump'
                self.player.rect.bottom = enemy.rect.top
                self.player.y_vel = self.player.jump_vel * 0.8
            # 怪物有被踩和被顶两种死亡方式
            enemy.go_die(how, 1 if self.player.face_right else -1)
        # 判断玩家是否会掉落
        self.check_will_fall(self.player)

    def check_will_fall(self, sprite):
        """
        检查精灵是否会掉落
        :param sprite: 待检查的精灵
        """
        sprite.rect.y += 1  # 试探性地向下落一个像素
        check_group = pygame.sprite.Group(self.ground_items_group, self.brick_group, self.box_group)
        collided = pygame.sprite.spritecollideany(sprite, check_group)
        # 如果没有触发碰撞检测、精灵并非跳起状态且关卡未冻结，则精灵变成下落状态
        if not collided and sprite.state != 'jump' and not self.is_frozen():
            sprite.state = 'fall'
        sprite.rect.y -= 1  # 返还试探的一个像素

    def adjust_player_y(self, sprite):
        """
        调整y方向玩家位置
        :param sprite: y方向碰撞到的精灵
        """
        if self.player.rect.y < sprite.rect.y:
            self.player.y_vel = 0
            self.player.rect.bottom = sprite.rect.top
            self.player.state = 'walk'
        else:
            self.player.y_vel = 7
            self.player.rect.top = sprite.rect.bottom
            self.player.state = 'fall'
            # 被顶起
            if sprite.name == 'box':
                sprite.go_bumped()
            elif sprite.name == 'brick':
                if self.player.big:
                    sprite.smashed(self.brick_group)
                else:
                    sprite.go_bumped()
            # 顶砖块的时候如果砖块上有敌人会击杀敌人
            self.is_enemy_on(sprite)

    def is_enemy_on(self, sprite):
        """
        判断被顶的砖块是否有敌人在上面，如果有则击杀
        :param sprite: 待检测的砖块或宝箱
        """
        # 判断方式依旧是试探性地向上一个像素，并和敌人组进行碰撞检测
        sprite.rect.y -= 1
        enemy = pygame.sprite.spritecollideany(sprite, self.enemy_group)
        if enemy:
            self.enemy_group.remove(enemy)
            self.dying_group.add(enemy)
            if sprite.rect.centerx > enemy.rect.centerx:
                enemy.go_die('bumped', -1)
            else:
                enemy.go_die('bumped', 1)
        sprite.rect.y += 1

    def check_checkpoints(self):
        """ 监测检查点 """
        checkpoint = pygame.sprite.spritecollideany(self.player, self.checkpoint_group)
        if checkpoint:
            if checkpoint.checkpoint_type == 0:
                # 刷新检查点对应的敌人
                self.enemy_group.add(self.enemy_group_dict[str(checkpoint.enemy_groupid)])
            checkpoint.kill()

    def check_if_go_die(self):
        """ 检查是否死亡 """
        # 掉出屏幕底端死亡
        if self.player.rect.y > C.SCREEN_H:
            self.player.go_die()

    def update_game_window(self):
        """ 更新游戏窗口 """
        third = self.game_window.x + self.game_window.width / 3
        # 当马里奥走过窗口1/3位置的时候窗口跟着马里奥一起向前移动(相对于地图)
        if self.player.x_vel > 0 and self.player.rect.centerx > third and self.game_window.right < self.end_x:
            self.game_window.x += self.player.x_vel
            self.start_x = self.game_window.x

    def draw(self, surface):
        """ 向屏幕上绘图游戏当前帧 """
        # 绘制背景和玩家
        self.game_ground.blit(self.background, self.game_window, self.game_window)
        self.game_ground.blit(self.player.image, self.player.rect)
        # 绘制硬币和强化道具
        self.coin_group.draw(self.game_ground)
        self.powerup_group.draw(self.game_ground)
        # 绘制砖块和宝箱(覆盖在硬币和强化道具上面)
        self.brick_group.draw(self.game_ground)
        self.box_group.draw(self.game_ground)
        # 绘制各种状态的敌人
        self.enemy_group.draw(self.game_ground)
        self.dying_group.draw(self.game_ground)
        self.shell_group.draw(self.game_ground)
        # 将游戏场景整体贴在屏幕上
        surface.blit(self.game_ground, (0, 0), self.game_window)
        # 绘制游戏信息
        self.info.draw(surface)
