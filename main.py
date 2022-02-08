"""
程序入口
__author__ = 201220014@smail.nju.edu.cn
"""

from source import tools
from source.states import main_menu, load_screen, level


def main():

    """ 主程序 """
    state_dict = {
        'main_menu': main_menu.MainMenu(),
        'load_screen': load_screen.LoadScreen(),
        'level': level.Level(),
        'game_over': load_screen.GameOver()
    }  # 创建游戏的各个状态对象存放在一个字典中
    game = tools.Game(state_dict, 'main_menu')  # 创建游戏主控对象
    game.run()  # 运行游戏主控类


if __name__ == '__main__':
    main()  # 游戏入口
