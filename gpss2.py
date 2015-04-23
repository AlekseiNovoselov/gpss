# В парикмахерской, в которой принята система предварительной записи, работают три мастера.
# У каждого мастера есть свои клиенты, интенсивности прихода которых распределены по экспоненциальному закону
# и равны всреднем соответственно 45 мин, 55 мин, 60 мин.
# Квалификация мастеров примерно одинаковая, поэтому время обработки одного клиента в среднем для всех
# равно 60 30 мин (распределение времени равномерное). Иногда в парикмахерскую заходят клиенты,
# не записавшиеся заранее. Их интенсивность прихода  - 2 человека в час.
# Таких клиентов обслуживает свободный мастер.
# Парикмахерская открывается в 8 ч 30 мин, а закрывается в 17 ч. 00 мин.
# Парикмахеры обедают по очереди соответственно в 12 ч. 00 мин, в 12 ч. 30 мин и в 13 ч. 00 мин.
# Время перерыва на обед 30 мин.  Если к началу обеда парикмахер был занят, то перед тем, как устроить перерыв,
#  он заканчивает обслуживание клиента. Клиенты, которые приходят в парикмахерскую в течение перерыва,
# ждут его окончания. Выполнить моделирование парикмахерской в течение рабочего дня.
# Определить загрузку парикмахеров, среднее время, необходимое клиенту на обслуживание.
# Определить оптимальные параметры потоков клиентов для данной парикмахерской.

__author__ = 'aleksei'

import random
from random import randint

TIME = 510
CLIENT_GO = ["casual client go", "first client go", "second client go", "third client go"]
HAIRDRESSER = ["", "first hair_dresser", "second hair_dresser", "third hair_dresser"]
DINNER = ["", "dinner one", "dinner two", "dinner three"]
BREAK = [0, 210, 240, 270]
CLIENT_INTERVAL = [1/30, 1/45, 1/55, 1/60]
AVERAGE_HANDLING = 60
HANDLING_DEVIATION = 30
DINNER_BREAK_DURATION = 30


class Transact(object):
    type = ""
    description = ""
    time = 0
    time_appear = 0

    def get_type(self):
        return self.type

    def __init__(self, _time, _type, _description=""):
        self.time_appear = _time
        self.time = _time
        self.type = _type
        if _description != "":
            self.description = _description


class HairDresser(object):
    is_handling = False
    type = ""
    working_time = 0
    time_be_free = 0
    avg_client_handling_time = 0
    number_of_handled_clients = 0

    def handle_client(self, time_appear, cur_time):
        time = random.randint(AVERAGE_HANDLING-HANDLING_DEVIATION, AVERAGE_HANDLING+HANDLING_DEVIATION)
        print("handling time " + str(time))
        self.time_be_free = cur_time + time
        if self.time_be_free < TIME:
            self.working_time += time
        else:
            self.working_time += TIME - cur_time
        print("time to be free " + str(self.time_be_free))
        self.number_of_handled_clients += 1
        self.avg_client_handling_time += cur_time - time_appear + time

    def uses(self):
        work_day_time = TIME
        if self.time_be_free > TIME:
            work_day_time = self.time_be_free
        return self.working_time/(work_day_time-DINNER_BREAK_DURATION)

    def client_handle_time(self):
        return self.avg_client_handling_time/self.number_of_handled_clients

    def __init__(self, _type):
        self.clients_queue = []
        self.type = _type


class Example(object):
    main_list = []
    one = HairDresser(HAIRDRESSER[1])
    two = HairDresser(HAIRDRESSER[2])
    three = HairDresser(HAIRDRESSER[3])

    def __init__(self,):
        self.generate_transaction()

    def queue_client_go(self, _interval, _type=""):
        sum = 0
        if _type != "":
            while sum < TIME:
                sum += random.expovariate(_interval)
                a = Transact(sum, _type)
                self.main_list.append(a)
        else:
            while sum < TIME:
                sum += random.expovariate(_interval)
                _type = CLIENT_GO[randint(2, 3)]
                _description = CLIENT_GO[0]
                a = Transact(sum, _type, _description)
                self.main_list.append(a)

    def dinner_break(self, _time, _type):
        a = Transact(_time, _type)
        self.main_list.append(a)

    def generate_transaction(self):
        self.queue_client_go(CLIENT_INTERVAL[1], CLIENT_GO[1])
        self.queue_client_go(CLIENT_INTERVAL[2], CLIENT_GO[2])
        self.queue_client_go(CLIENT_INTERVAL[3], CLIENT_GO[3])
        self.queue_client_go(CLIENT_INTERVAL[0],)
        self.dinner_break(BREAK[1], DINNER[1])
        self.dinner_break(BREAK[2], DINNER[2])
        self.dinner_break(BREAK[3], DINNER[3])
        self.main_list = sorted(self.main_list, key=lambda transact: transact.time)

    def handle_client(self, transact_type, current):
        hair_dresser = 0
        if transact_type == CLIENT_GO[1]:
            hair_dresser = self.one
        if transact_type == CLIENT_GO[2]:
            hair_dresser = self.two
        if transact_type == CLIENT_GO[3]:
            hair_dresser = self.three
        if hair_dresser.time_be_free <= current.time:
            hair_dresser.handle_client(current.time_appear, current.time)
            self.main_list.pop(0)
        else:
            current.time = hair_dresser.time_be_free
        self.main_list = sorted(self.main_list, key=lambda transact: transact.time_appear)
        self.main_list = sorted(self.main_list, key=lambda transact: transact.time)

    def handle_dinner(self, transact_type):
        hair_dresser = 0
        if transact_type == DINNER[1]:
            hair_dresser = self.one
        if transact_type == DINNER[2]:
            hair_dresser = self.two
        if transact_type == DINNER[3]:
            hair_dresser = self.three
        hair_dresser.time_be_free += DINNER_BREAK_DURATION
        self.main_list.pop(0)

    def run(self):

        while self.main_list and self.main_list[0].time < TIME:
            current = self.main_list[0]
            transact_type = current.type
            if current.description == CLIENT_GO[0]:
                print("this is casual client")
            if transact_type in CLIENT_GO:
                print(str(current.time) + "  " + str(current.type))
                self.handle_client(transact_type, current)
            if transact_type in DINNER:
                print(str(current.time) + "  " + str(current.type))
                self.handle_dinner(transact_type)

        print("\n\n\tЗагрузка парикмахеров\t\t Среднее время обслуживания клиента")
        print("1\t" + str(self.one.uses()) + "\t\t\t\t" + str(self.one.client_handle_time()))
        print("2\t" + str(self.two.uses()) + "\t\t\t\t" + str(self.two.client_handle_time()))
        print("3\t" + str(self.three.uses()) + "\t\t\t\t" + str(self.three.client_handle_time()))

if __name__ == '__main__':
    Example().run()