# В парикмахерской, в которой принята система предварительной записи, работают три мастера.
# Укаждого мастера есть свои клиенты, интенсивности прихода которых распределены по экспоненциальному закону
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
CLIENT_GO = ["first client go", "second client go", "third client go", "casual client go"]
HAIRDRESSER = ["first hair_dresser", "second hair_dresser", "third hair_dresser"]
DINNER = ["dinner one", "dinner two", "dinner three"]
FREE_HAIRDRESSER = ["free one", "free two", "free three"]
BREAK = [210, 240, 270]
CLIENT_INTERVAL = [1/45, 1/55, 1/60, 1/30]
AVERAGE_HANDLING = 60
HANDLING_DEVIATION = 30
DINNER_BREAK_DURATION = 30


class Transact(object):
    type = ""
    description = ""
    time = 0
    time_appear = 0
    num = 0

    def get_type(self):
        return self.type

    def __init__(self, _time, _type, num, _description=""):
        self.num = num
        self.time_appear = _time
        self.time = _time
        self.type = _type
        if _description != "":
            self.description = _description


class MainList(object):

    main_list = []

    def sort(self):
        self.main_list = sorted(self.main_list, key=lambda transact: transact.time)

    def generate_free_transact(self, time, num):
        self.main_list.append(Transact(time, FREE_HAIRDRESSER[num], num))

    def generate_dinner_transact(self, num):
        self.main_list.append(Transact(BREAK[num], DINNER[num], num))

    def generate_client_go_transact(self, num):
        tmp_list = []
        sum = 0
        if num < len(HAIRDRESSER):
            while sum < TIME:
                tmp_list.append(sum)
                sum += random.expovariate(CLIENT_INTERVAL[num])
                a = Transact(sum, CLIENT_GO[num], num)
                self.main_list.append(a)
        else:
            while sum < TIME:
                tmp_list.append(sum)
                sum += random.expovariate(CLIENT_INTERVAL[num])
                num = randint(0, 2)
                _type = CLIENT_GO[num]
                _description = CLIENT_GO[3]
                a = Transact(sum, _type, num, _description)
                self.main_list.append(a)


class State(object):

    def __init__(self, _time, _size, _type):
        self.time = _time
        self.size = _size
        self.type = _type


class HairDresser(object):

    def __init__(self, _type,):
        self.max_queue = 0
        self.type = _type
        self.client_queue = []
        self.is_dinner = False
        self.common_waiting_time = 0
        self.worked_time = 0
        self.dinner_start_time = 0
        self.dinner_end_time = 0
        self.day_end_time = 0
        self.states = []

    @staticmethod
    def handle_client():
        return random.randint(AVERAGE_HANDLING-HANDLING_DEVIATION, AVERAGE_HANDLING+HANDLING_DEVIATION)

    def add_client(self, transact):
        #print(str(len(self.client_queue)) + str(" peoples in queue now"))
        if len(self.client_queue) > self.max_queue:
            self.max_queue = len(self.client_queue)

        self.states.append(State(transact.time, len(self.client_queue), "add\t"))
        if len(self.client_queue) > 0:
            self.client_queue.append(transact.time)
            return 0
        else:
            handling_time = self.handle_client()
            self.worked_time += handling_time

            if self.is_dinner:
                handling_time += DINNER_BREAK_DURATION
                self.is_dinner = False

            self.client_queue.append(transact.time)

            return handling_time + transact.time

    def dinner(self):
        self.is_dinner = True

    def free(self, transact):
        #print(str("free ") + str(self.type))
        self.client_queue.pop(0)
        if len(self.client_queue) < 1:
            len_state = 0
        else:
            len_state = len(self.client_queue) - 1
        self.states.append(State(transact.time, len_state, "free\t"))

        if len(self.client_queue) > 0:
            handling_time = self.handle_client()
            self.worked_time += handling_time

            if self.is_dinner:
                handling_time += DINNER_BREAK_DURATION
                self.is_dinner = False

            if handling_time + transact.time > TIME:
                self.day_end_time = handling_time + transact.time

            return handling_time
        else:
            return 0

    def average_client_waiting_time(self):
        self.common_waiting_time = 0
        num_handled_clients = 0
        for i in range(len(self.states) - 1):
            x = self.states[i]
            next = self.states[i+1]
            #print(str(x.type) + str(x.size) + "\t" + str(x.time))
            if x.type == "free\t":
                num_handled_clients += 1
            if next.size != x.size and x.size != 0:
                self.common_waiting_time += x.size*(next.time - x.time)
        #print(str("sdfsdfsdfsdf") + str(num_handled_clients))
        return self.common_waiting_time/int(num_handled_clients)

    def hair_dresser_load(self):
        if self.day_end_time:
            return self.worked_time/self.day_end_time
        else:
            return self.worked_time/TIME


class Example(object):

    def __init__(self):
        self.main_list = MainList()
        self.hair_dressers = []

    def generate_transaction(self):
        for i in range(len(CLIENT_GO)):
            self.main_list.generate_client_go_transact(i)
        for i in range(len(DINNER)):
            self.main_list.generate_dinner_transact(i)
        self.main_list.sort()

    def create_hairdressers(self):
        for i in range(len(HAIRDRESSER)):
            self.hair_dressers.append(HairDresser(HAIRDRESSER[i]))

    def print_results(self):
        for x in self.main_list.main_list:
            print(str(x.time) + "  " + str(x.type) + " " + str(x.description))

    def run(self):
        self.create_hairdressers()
        self.generate_transaction()
        while self.main_list.main_list and self.main_list.main_list[0].time < TIME:
            current = self.main_list.main_list[0]
            transact_type = current.type

            if current.description == CLIENT_GO[3]:
                pass
                #print("this is casual client")

            if transact_type in CLIENT_GO:
                #print(str(current.time) + "  " + str(current.type))
                time_to_free = self.hair_dressers[current.num].add_client(current)
                if time_to_free > 0:
                    #print("generate free in " + str(time_to_free))
                    self.main_list.generate_free_transact(time_to_free, current.num)
                    self.main_list.sort()

            if transact_type in DINNER:
                #print(str(current.time) + "  " + str(current.type))
                self.hair_dressers[current.num].dinner()

            if transact_type in FREE_HAIRDRESSER:
                #print(str("free__ ")+str(current.time))
                time_to_free = self.hair_dressers[current.num].free(current)
                if time_to_free > 0:
                    self.main_list.generate_free_transact(time_to_free + current.time, current.num)
                    self.main_list.sort()

            self.main_list.main_list.pop(0)

        print("Парикмахер\tЗагруженность\t\t\t Время в очереди \t\t Max очередь")
        for i in range(len(HAIRDRESSER)):
            current = self.hair_dressers[i]
            print("\t" + str(i+1) + "\t\t" + str(current.hair_dresser_load()) + "\t\t" + str(current.average_client_waiting_time()) + "\t\t\t" + str(current.max_queue))


if __name__ == '__main__':
    Example().run()