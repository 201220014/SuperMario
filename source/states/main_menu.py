"""
游戏主菜单
__author__ = 201220014@smail.nju.edu.cn
"""

import pygame

from .. import constants as C
from .. import setup, tools
from ..components import info


class MainMenu:
    """ 主菜单类 """

    def __init__(self):
        """ 主菜单类构造函数 """
        game_info = {
            'score': 0,
            'coin': 0,
            'lives': 3,
            'player_state': 'small'
        }
        self.start(game_info)

    def start(self, game_info):
        """ 主菜单类初始化函数 """
        self.game_info = game_info
        self.setup_background()  # 设置背景
        self.setup_player()  # 设置玩家图片
        self.setup_cursor()  # 设置光标
        self.info = info.Info('main_menu', self.game_info)  # 游戏信息
        self.finished = False
        self.next = 'load_screen'  # 菜单的下一个状态

    def setup_background(self):
        """ 设置背景 """
        self.background = setup.GRAPHICS['level_1']  # 获取背景图片
        self.background_rect = self.background.get_rect()  # 获取背景图矩形范围
        # 背景图放缩以适应窗口
        self.background = pygame.transform.scale(self.background, (int(self.background_rect.width * C.BG_MULTI),
                                                                   int(self.background_rect.height * C.BG_MULTI)))
        self.viewport = setup.SCREEN.get_rect()  # 获取窗口矩形范围
        # 获取并设置标题图片： 截图 + 抠图 + 放缩
        self.caption = tools.get_image(setup.GRAPHICS['title_screen'], 1, 60, 176, 88, C.BG_MULTI)

    def setup_player(self):
        """ 设置玩家图片 """
        # 获取并设置玩家图片： 截图 + 抠图 + 放缩
        self.player_image = tools.get_image(setup.GRAPHICS['mario_bros'], 178, 32, 12, 16, C.PLAYER_MULTI)

    def setup_cursor(self):
        """ 设置光标 """
        # 初始化光标为pygame精灵对象
        self.cursor = pygame.sprite.Sprite()
        # 获取并设置光标图片： 截图 + 抠图 + 放缩
        self.cursor.image = tools.get_image(setup.GRAPHICS['item_objects'], 25, 160, 8, 8, C.PLAYER_MULTI)
        # 修改光标的矩形区域 - 位置， 便于之后绘制
        rect = self.cursor.image.get_rect()
        rect.x, rect.y = 220, 360
        self.cursor.rect = rect
        # 设置光标状态，这里运用了有限状态机的原理
        # 有限状态机详细本质的理论知识需要一些《离散数学》和《数字逻辑》的基础
        # 这里依照代码结构简单理解即可，这样的结构在整个游戏中经常用到，需重点留意
        self.cursor.state = '1P'

    def update(self, surface, keys):
        """
        主菜单的更新函数
        :param surface: 绘图设备 - 游戏屏幕
        :param keys: 捕捉到的键盘信号
        """
        self.update_cursor(keys)  # 更新光标状态
        # 绘制主菜单
        surface.blit(self.background, self.viewport)  # 绘制背景
        surface.blit(self.caption, (170, 100))  # 绘制标题
        surface.blit(self.player_image, (110, 490))  # 绘制玩家图片
        surface.blit(self.cursor.image, self.cursor.rect)  # 绘制光标
        # 更新并绘制信息
        self.info.update()
        self.info.draw(surface)

    def update_cursor(self, keys):
        """
        更新光标
        :param keys: 捕捉到的键盘信号
        """
        # 处理键盘信号
        if keys[pygame.K_UP]:
            self.cursor.state = '1P'
            self.cursor.rect.y = 360  # 设置光标位置
        elif keys[pygame.K_DOWN]:
            self.cursor.state = '2P'
            self.cursor.rect.y = 405  # 设置光标位置
        elif keys[pygame.K_RETURN]:  # 回车键按下开始游戏
            self.reset_game_info()  # 重置游戏信息
            if self.cursor.state == '1P':
                self.finished = True
            elif self.cursor.state == '2P':
                self.finished = True
            # TODO: 对单人模式和双人模式分别处理，我暂时未区分，1P和2P都是单人模式

    def reset_game_info(self):
        """
        重置游戏信息，在玩家死亡后会被调用
        """
        self.game_info.update({
            'score': 0,
            'coin': 0,
            'lives': 3,
            'player_state': 'small'
        })
