"""
工具和游戏主控逻辑
__author__ = 201220014@smail.nju.edu.cn
"""

import pygame
import os  # 操作系统标准库


class Game:
    """ 游戏主控类，控制主要游戏流程 """

    def __init__(self, state_dict, start_state):
        """
        游戏主控类构造函数
        :param state_dict: 储存游戏状态的字典
        :param start_state: 开始状态
        """
        self.screen = pygame.display.get_surface()  # 获取游戏画面
        self.clock = pygame.time.Clock()  # 时钟：计时 + 控制帧数
        self.keys = pygame.key.get_pressed()  # 捕捉键盘事件
        self.state_dict = state_dict  # 初始化状态字典
        self.state = self.state_dict[start_state]  # 初始化游戏状态

    def update(self):
        """ 主控类的更新函数，让游戏状态跟新屏幕内容。如果当前状态结束，则转入下一个状态。 """
        if self.state.finished:
            game_info = self.state.game_info  # 记录当前状态的游戏信息
            next_state = self.state.next  # 记录下一个状态
            self.state.finished = False  # 重置状态结束标记
            self.state = self.state_dict[next_state]  # 将当前状态更新为下一个状态
            self.state.start(game_info)  # 将上一个状态记录的游戏信息传入下一个状态并开启状态
        self.state.update(self.screen, self.keys)  # 让现行状态依据键盘事件更新屏幕内容

    def run(self):
        """ 游戏核心驱动程序 """
        while True:
            # 捕捉游戏事件并处理或者记录信息留待处理
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.display.quit()  # 退出显示屏
                    quit()  # 退出程序
                elif event.type == pygame.KEYDOWN:
                    self.keys = pygame.key.get_pressed()  # 捕捉按键信息
                elif event.type == pygame.KEYUP:
                    self.keys = pygame.key.get_pressed()  # 捕捉案件信息

            self.update()  # 更新游戏状态

            pygame.display.update()  # 跟新显示屏内容
            self.clock.tick(60)  # 帧数：游戏画面每秒钟变化的次数，帧数越大，游戏越快


def load_graphics(path, accept=('.jpg', '.png', '.bmp', '.gif')):
    """ 加载素材文件夹中的所有图片到一个字典中
        :param path: 文件夹路径
        :param accept: 接受的图片文件扩展名
        :return: pygame图片字典
    """
    graphics = {}
    for pic in os.listdir(path):  # listdir(path): 罗列路径下的所有条目(目录+文件)
        name, ext = os.path.splitext(pic)  # 分拆文件名和后缀
        if ext.lower() in accept:
            img = pygame.image.load(os.path.join(path, pic))
            if img.get_alpha():  # 带有alpha层，即透明底的图片
                img = img.convert_alpha()
            else:
                img = img.convert()
            # 上述转换操作可以加快游戏画面渲染，不过不是必须的
            graphics[name] = img
    return graphics


def get_image(sheet, x, y, width, height, scale, colorkey=None):
    """ 从已经加载的图片里获取某部分图片
        :param sheet: 待抠图片
        :param x: 目标区域左上角横坐标
        :param y: 目标区域左上角纵坐标
        :param width: 目标区域宽
        :param height: 目标区域高
        :param scale: 放大倍数
        :param colorkey: 抠图底色
        :return: pygame图片对象
    """
    image = pygame.Surface((width, height))  # 创建空的pygame画布
    image.blit(sheet, (0, 0), (x, y, width, height))  # (0, 0)表示画到哪个位置， (x, y, w, h)代表将sheet里哪个位置取出来
    if not colorkey:
        colorkey = image.get_at((0, 0))  # 获取图片底色
    image.set_colorkey(colorkey)  # 对底色抠图
    image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))  # 放大图片
    return image
