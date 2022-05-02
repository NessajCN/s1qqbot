from enum import Enum
class Board(Enum):
    # 热门新区
    VTB虚拟偶像 = 151
    VTB = 151

    手游页游 = 135
    手游 = 135

    欧美动漫 = 144
    模型玩具 = 136

    # 主论坛
    游戏区 = 4
    版务管理区 = 55
    动漫区 = 6
    漫区 = 6

    影视区 = 48

    PC数码 = 51
    数码 = 51

    百无一用 = 50

    八卦体育 = 77
    八体 = 77

    卓明谷 = 75
    外野 = 75

    二手交易 = 115

    # 网游
    炉石传说 = 132
    DOTA = 138
    LOL = 111

    # 子论坛
    内野 = 27

if __name__ == '__main__':
    board = "卓明谷"
    print(f"https://bbs.saraba1st.com/2b/fid-{Board[board].value}.html")