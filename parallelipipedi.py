import json

import copy
import random
import sys
placed_box_list = []
placed_box_list_korobok = []
index = 0
current_lenght = 0
current_width = 0
current_heigh = 0
count = 0
row = 0
indextest = 0
class RectangularCuboid:
    # Конструктор
    def __init__(self, cargo_id, mass, sort, number, sizes):

        # GARPIX
        self.cargo_id = cargo_id
        self.mass = mass
        self.sort = sort
        # Дефолтные координаты объекта равны None(null)
        # upd - новый способ хранить центр
        self.center = {'x': None, 'y': None, 'z': None}
        # Ориентация может принимать значения от 0 до 5(картинка в беседе)
        self.orientation = 0
        self.points = {"P1": None, "P2": None, "P3": None, "P4": None, "P5": None, "P6": None, "P7": None, "P8": None}
        # Словарь координат
        self.cords = {'x_min': None, 'x_max': None, 'y_min': None, 'y_max': None, 'z_min': None, 'z_max': None}
        # Словарь узлов для каждой поверхности
        self.nodes = {"front": None, "right": None, "back": None, "left": None, "up": None, "down": None}
        # Нумерование коробки
        self.number = number
        # Обработка sizes, можно прям из json закидывать, понимает как словарь, так и список. Все измерения сразу в метрах
        if isinstance(sizes, dict):
            self.size = {'width': sizes['width'] / 1000, "height": sizes['height'] / 1000,
                         "length": sizes['length'] / 1000}
        else:
            self.size = {'width': sizes[0] / 1000, "height": sizes[1] / 1000, "length": sizes[2] / 1000}
        # Объем в м^3
        self.volume = self.size['width'] * self.size['height'] * self.size['length']
        # Словарь площадей по всем трем плоскостям
        self.square = {'xz_square': self.size['width'] * self.size['length'],
                       'xy_square': self.size['height'] * self.size['length'],
                       'yz_square': self.size['height'] * self.size['width']}
        # Значения по умолчанию для переменных ориентирования
        self.size_orientated = {'width': self.size['width'], "height": self.size['height'],
                                "length": self.size['length']}
        self.square_orientated = self.square

        self.max_square_orientated = 0
        self.id_square_orientated = ''
        for k, v in self.square_orientated.items():
            if v > self.max_square_orientated:
                self.id_square_orientated = k
                self.max_square_orientated = v

    # Функция ориентирования в пространстве, запись происходит в другие переменные с постфиксом _orientated
    # Square_orientated хранит ориентированные площади после изменение ориентации
    def orient_box(self, orient):
        self.orientation = orient
        if orient == 0:
            self.size_orientated = {'width': self.size['width'], "height": self.size['height'],
                                    "length": self.size['length']}
        if orient == 1:
            self.size_orientated = {'width': self.size['length'], "height": self.size['height'],
                                    "length": self.size['width']}
        if orient == 2:
            self.size_orientated = {'width': self.size['height'], "height": self.size['width'],
                                    "length": self.size['length']}
        if orient == 3:
            self.size_orientated = {'width': self.size['length'], "height": self.size['width'],
                                    "length": self.size['height']}
        if orient == 4:
            self.size_orientated = {'width': self.size['height'], "height": self.size['length'],
                                    "length": self.size['width']}
        if orient == 5:
            self.size_orientated = {'width': self.size['width'], "height": self.size['length'],
                                    "length": self.size['height']}
        self.square_orientated = {'xz_square': self.size_orientated['width'] * self.size_orientated['length'],
                                  'xy_square': self.size_orientated['height'] * self.size_orientated['length'],
                                  'yz_square': self.size_orientated['height'] * self.size_orientated['width']}
        for k, v in self.square_orientated.items():
            if v > self.max_square_orientated:
                self.id_square_orientated = k
                self.max_square_orientated = v

    # Установка координат центра, также минимальные и максимальные значения по всем осям
    def set_center(self, cord):
        self.center['x'] = cord['x']
        self.center['y'] = cord['y']
        self.center['z'] = cord['z']
        self.cords['x_min'] = self.center['x'] - self.size_orientated['length'] / 2
        self.cords['x_max'] = self.center['x'] + self.size_orientated['length'] / 2
        self.cords['y_min'] = self.center['y'] - self.size_orientated['height'] / 2
        self.cords['y_max'] = self.center['y'] + self.size_orientated['height'] / 2
        self.cords['z_min'] = self.center['z'] - self.size_orientated['width'] / 2
        self.cords['z_max'] = self.center['z'] + self.size_orientated['width'] / 2
        # 8 Крайних точек, снизу вверх по часовой стрелке.
        self.points['P1'] = [self.cords['x_min'], self.cords['y_min'], self.cords['z_min']]
        self.points['P2'] = [self.cords['x_max'], self.cords['y_min'], self.cords['z_min']]
        self.points['P3'] = [self.cords['x_max'], self.cords['y_min'], self.cords['z_max']]
        self.points['P4'] = [self.cords['x_min'], self.cords['y_min'], self.cords['z_max']]

        self.points['P5'] = [self.cords['x_min'], self.cords['y_max'], self.cords['z_min']]
        self.points['P6'] = [self.cords['x_max'], self.cords['y_max'], self.cords['z_min']]
        self.points['P7'] = [self.cords['x_max'], self.cords['y_max'], self.cords['z_max']]
        self.points['P8'] = [self.cords['x_min'], self.cords['y_max'], self.cords['z_max']]

    # Новая функция посмотреть на алгоритм и возможно доработать, проверка коробок реализовано ниже.
    def check_nodes(self, pallet):
        # front node line
        # if self.nodes['front'] is None:
        # print('front' + str(self.size_orientated['width']/2 + self.center['z']))
        if self.size_orientated['width'] / 2 + self.center['z'] == pallet['width']:
            self.nodes['front'] = None
        else:
            # еще должна быть проверка на постановку рядом с другими коробками
            # self.nodes['front'] = {'z' : self.size_orientated['width']/2 + self.center['z']}
            self.nodes['front'] = {'z': self.cords['z_max']}
        # back node line
        # if self.nodes['back'] is None:
        # print('back' + str(self.center['z'] - self.size_orientated['width']/2))
        if self.center['z'] - self.size_orientated['width'] / 2 == 0:
            self.nodes['back'] = None
        else:
            # еще должна быть проверка на постановку рядом с другими коробками
            self.nodes['back'] = {'z': self.center['z'] - self.size_orientated['width'] / 2}

        # left node line
        # if self.nodes['left'] is None:
        # print('left' + str(self.center['x'] - self.size_orientated['length']/2))
        if self.center['x'] - self.size_orientated['length'] / 2 == 0:
            self.nodes['left'] = None
        else:
            # еще должна быть проверка на постановку рядом с другими коробками
            self.nodes['left'] = {'x': self.center['x'] - self.size_orientated['length'] / 2}

        # right node line
        # if self.nodes['right'] is None:
        # print('right' + str(self.center['x'] - self.size_orientated['length']/2))
        if self.center['x'] + self.size_orientated['length'] / 2 == pallet['length']:
            self.nodes['right'] = None
        else:
            # еще должна быть проверка на постановку рядом с другими коробками
            # self.nodes['right'] = {'x' : self.center['x'] + self.size_orientated['length']/2}
            self.nodes['right'] = {'x': self.cords['x_max']}
        # up node line
        # if self.nodes['up'] is None:
        # print('up' + str(self.center['y'] + self.size_orientated['height']/2))
        if self.center['y'] + self.size_orientated['height'] / 2 == pallet['height']:
            self.nodes['up'] = None
        else:
            self.nodes['up'] = {'y': self.center['y'] + self.size_orientated['height'] / 2}

        # down node line
        # if self.nodes['down'] is None:
        # print('down' + str(self.center['y'] - self.size_orientated['height']/2))
        # ну вообще не может быть снизу место, нужно разобраться
        if self.center['y'] - self.size_orientated['height'] / 2 == 0:
            self.nodes['down'] = None
        else:
            self.nodes['down'] = {'y': self.center['y'] - self.size_orientated['height'] / 2}

    # Возвращает информацию обо всех переменных в виде словаря
    def get_info(self):
        info_dict = {"number": self.number, "volume": self.volume, "square": self.square, "size": self.size,
                     "orientation": self.orientation, "size_orientated": self.size_orientated,
                     "square_orientated": self.square_orientated, "center_coords": self.center, "nodes": self.nodes,
                     "cords_min_max": self.cords, "points": self.points}
        return info_dict

def check_box_placement(list_boxes, box):
    for boxes in list_boxes:
        if box.cords['x_min'] < boxes.cords['x_max'] and box.cords['x_max'] > boxes.cords['x_min'] and box.cords[
            'y_min'] < boxes.cords['y_max'] and box.cords['y_max'] > boxes.cords['y_min'] and box.cords['z_min'] < \
                boxes.cords['z_max'] and box.cords['z_max'] > boxes.cords['z_min']:
            return False
    return True

def check_box_pallet(b, s):
    if b.center['x'] + b.size_orientated['length'] / 2 <= s['length'] and b.center['y'] + b.size_orientated[
        'height'] / 2 <= s['height'] and b.center['z'] + b.size_orientated['width'] / 2 <= s['width']:
        return True
    return False

def check_left(list_boxes, box):
    x_max = 0
    for boxes in list_boxes:
        if box.cords['x_min'] < boxes.cords['x_max'] and box.cords['x_max'] > boxes.cords['x_min'] and box.cords[
            'y_min'] < boxes.cords['y_max'] and box.cords['y_max'] > boxes.cords['y_min'] and box.cords['z_min'] < \
                boxes.cords['z_max'] and box.cords['z_max'] > boxes.cords['z_min']:
            if box.cords['x_min'] < boxes.cords['x_max'] < box.cords['x_max']:
                x_max = boxes.cords['x_max'] - box.cords['x_min']

    return x_max

def sort(list_cubes, dimension):
    for i in range(len(list_cubes)):
        for j in range(len(list_cubes) - i - 1):
            if list_cubes[j].size_orientated[dimension] < list_cubes[j + 1].size_orientated[dimension]:
                list_cubes[j], list_cubes[j + 1] = list_cubes[j + 1], list_cubes[j]

def place_new_lvl(list_last_boxes,old_index,list_korobok, space,place_box_list):
    global current_heigh
    list_visot = max([i.size_orientated['height'] for i in list_last_boxes])
    #print(current_heigh)
    if(list_visot < space['height']):
        global index
        global current_lenght
        global current_width
        global placed_box_list_korobok
        global count
        global row
        old_index = index
        current_lenght = 0
        current_width = 0
        # placed_box_list_korobok = placed_box_list_korobok
        list_korobok_v_ryadu = []
        for ind in range(len(list_last_boxes)):
            current_heigh = list_last_boxes[ind].cords['y_max'] + 0.0000000001
            current_width = list_last_boxes[ind].cords['z_min'] + 0.0000000001
            current_lenght = list_last_boxes[ind].cords['x_min'] + 0.0000000001
            x_max =0
            list_korobok[old_index].set_center({'x': x_max + current_lenght + (list_korobok[old_index].size_orientated['length']) / 2,
                                     'y': current_heigh + (list_korobok[old_index].size_orientated['height']) / 2,
                                     'z': current_width + (list_korobok[old_index].size_orientated['width']) / 2})
            x_max = check_left(list_last_boxes, list_korobok[old_index])
            #print('x_max', x_max)
            if (x_max > 0):
                list_korobok[old_index].set_center(
                    {'x': x_max + current_lenght + (list_korobok[old_index].size_orientated['length']) / 2,
                     'y': current_heigh + (list_korobok[old_index].size_orientated['height']) / 2,
                     'z': current_width + (list_korobok[old_index].size_orientated['width']) / 2})
            if (check_box_placement(placed_box_list, list_korobok[old_index])) and check_box_pallet(list_korobok[old_index], space):
                placed_box_list_korobok[ind] = list_korobok[old_index]
                place_box_list.append(list_korobok[old_index])
                old_index += 1
                count+=1
                list_korobok_v_ryadu.append(list_korobok[old_index])
            else:
                list_korobok_v_ryadu = []
                if len(list_korobok_v_ryadu) !=0:
                    current_lenght = 0
                    row+=1
                    current_width += list_korobok_v_ryadu[0].size_orientated['width'] + 0.0000000001
                    list_korobok_v_ryadu = []
                else:
                    break
        index = old_index
        return place_box_list

def rasstonovka(list, space):
    global current_width
    global current_lenght
    global current_heigh
    global index
    global placed_box_list
    while (current_width <= space['width']):
        # print(current_lenght)
        # print(current_width)
        while (current_lenght <= space['length']):

            list[index].set_center({'x': current_lenght + (list[index].size_orientated['length']) / 2,
                                    'y': current_heigh + (list[index].size_orientated['height']) / 2,
                                    'z': current_width + (list[index].size_orientated['width']) / 2})
            if (check_box_placement(placed_box_list, list[index])) and check_box_pallet(list[index], space):
                placed_box_list.append(list[index])
                placed_box_list_korobok.append(list[index])
                current_lenght += list[index].size_orientated['length'] + 0.0000000001
                index += 1

            else:
                # print('a')
                break
        current_lenght = 0
        current_width += list[0].size_orientated['width'] + 0.0000000001
        # print(current_lenght)
        # print(current_width)
    for i in range(100):
        placed_box_list = place_new_lvl(placed_box_list_korobok, index, list, space, placed_box_list)
    return placed_box_list

def sort_volumes(list_cubes):
    for i in range(len(list_cubes)):
        for j in range(len(list_cubes) - i - 1):
            if list_cubes[j].volume < list_cubes[j + 1].volume:
                list_cubes[j], list_cubes[j + 1] = list_cubes[j + 1], list_cubes[j]

def create_output_json(space, list, test1, strok = ''):
    global file_name
    cargo_space = {'loading_size': {'height': space['height'], 'length': space['length'], 'width': space['width']},
                   "position": [space['length'] / 2, space['height'] / 2, space['width'] / 2], 'type': "pallet"}
    cargos_list = []
    unpacked = []
    for i in list:
        temp = {}
        temp['size'] = {'height': i.size_orientated['height'], "length": i.size_orientated['length'],
                        "width": i.size_orientated['width']}
        temp['cargo_id'] = i.cargo_id
        temp['id'] = i.number
        temp['mass'] = i.mass
        temp['position'] = i.center
        temp['calculated_size'] = i.size
        temp['sort'] = i.sort
        temp['stacking'] = True
        temp['turnover'] = True
        temp['type'] = "box"
        cargos_list.append(temp)
    z = -1
    x = -1
    for i in test1[len(list):]:
        tmp = {}
        tmp['size'] = i.size
        tmp['cargo_id'] = i.cargo_id
        tmp['id'] = i.number
        tmp['mass'] = i.mass
        tmp['position'] = {'x': x, 'y': i.size['height'], 'z': z}
        tmp['sort'] = i.sort
        tmp['stacking'] = True
        tmp['turnover'] = True
        unpacked.append(tmp)
        x -= i.size['length']
    final = {"cargoSpace": cargo_space, "cargos": cargos_list, "unpacked": unpacked}
    fil = file_name.split('/')
    with open('../output/result_output_' + fil[-1], 'w') as f:
        json.dump(final, f)
    # with open('result_output_' + fil[-1]  + strok + '.json', 'w') as f:
    #     json.dump(final, f)
    f.close()

def main(file_name):
    with open(file_name) as f:
        templates = json.load(f)
    counter = 0
    all_RectCuboid = []
    for i in templates['cargo_groups']:
        for j in range(i['count']):
            all_RectCuboid.append(RectangularCuboid(i['id'], i['mass'], i['sort'], counter, i['size']))
            counter += 1
    if isinstance(templates['cargo_space']['size'], dict):
        space = {'width': templates['cargo_space']['size']['width'] / 1000, "height": templates['cargo_space']['size'] / 1000,
                     "length": templates['cargo_space']['size'] / 1000}
    else:
        space = dict(zip(['width', 'height', 'length'],
                     [templates['cargo_space']['size'][0] / 1000, templates['cargo_space']['size'][1] / 1000,
                      templates['cargo_space']['size'][2] / 1000]))
    copyAll = copy.deepcopy(all_RectCuboid)
    sort(copyAll, 'width')
    test1 = copy.deepcopy(copyAll)
    orintation = random.randint(0, 5)
    for j in range(len(test1)):
        test1[j].orient_box(orintation)
    rasstonovka(test1, space)
    f.close()
    create_output_json(space, placed_box_list, test1)
if __name__ == '__main__':
    file_name = sys.argv[1]
    main(file_name)