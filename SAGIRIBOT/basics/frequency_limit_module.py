import time
import datetime
from dateutil.relativedelta import relativedelta


def singleton(cls):
    # 单下划线的作用是这个变量只能在当前模块里访问,仅仅是一种提示作用
    # 创建一个字典用来保存类的实例对象
    _instance = {}

    def _singleton(*args, **kwargs):
        # 先判断这个类有没有对象
        if cls not in _instance:
            _instance[cls] = cls(*args, **kwargs)  # 创建一个对象,并保存到字典当中
        # 将实例对象返回
        return _instance[cls]

    return _singleton


@singleton
class GlobalFrequencyLimitDict:
    __instance = None
    __first_init = False
    __temp_blacklist = {}
    __frequency_counter = {}
    __blacklist_announced = {}
    frequency_limit_dict = None

    def __new__(cls, frequency_limit_dict: dict):
        if not cls.__instance:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(self, frequency_limit_dict: dict):
        if not self.__first_init:
            self.frequency_limit_dict = frequency_limit_dict
            GlobalFrequencyLimitDict.__first_init = True

    def get(self, group_id: int):
        if group_id in self.frequency_limit_dict:
            print(f"group {group_id} frequency: {self.frequency_limit_dict[group_id]}")
            return self.frequency_limit_dict[group_id]
        else:
            self.frequency_limit_dict[group_id] = 0
            return 0

    def set_zero(self):
        for key in self.frequency_limit_dict.keys():
            # print(f"group {key} frequency count set to 0!")
            self.frequency_limit_dict[key] = 0
        for group in self.__frequency_counter:
            for member in self.__frequency_counter[group]:
                self.__frequency_counter[group][member] = 0

    def update(self, group_id: int, weight: int):
        if group_id in self.frequency_limit_dict:
            self.frequency_limit_dict[group_id] += weight
        else:
            pass

    def add_group(self, group_id: int):
        if group_id in self.frequency_limit_dict:
            print(f"{group_id} is already in frequency limit module!")
        else:
            self.frequency_limit_dict[group_id] = 0

    def add_temp_blacklist(self, group_id: int, member_id: int):
        if group_id in self.__temp_blacklist:
            if member_id in self.__temp_blacklist[group_id]:
                if datetime.datetime.now() > self.__temp_blacklist[group_id][member_id]:
                    self.__temp_blacklist[group_id][member_id] = datetime.datetime.now() + relativedelta(hours=1)
            else:
                self.__temp_blacklist[group_id][member_id] = datetime.datetime.now() + relativedelta(hours=1)
        else:
            self.__temp_blacklist[group_id] = {}
            self.__temp_blacklist[group_id][member_id] = datetime.datetime.now() + relativedelta(hours=1)
        print(self.__temp_blacklist[group_id][member_id])

    def blacklist_judge(self, group_id: int, member_id: int) -> bool:
        if group_id in self.__temp_blacklist and member_id in self.__temp_blacklist[group_id]:
            # print(datetime.datetime.now(), self.__temp_blacklist[group_id][member_id])
            # print(datetime.datetime.now() <= self.__temp_blacklist[group_id][member_id])
            return datetime.datetime.now() <= self.__temp_blacklist[group_id][member_id]
        else:
            return False

    def add_record(self, group_id: int, member_id: int, weight: int):
        if group_id in self.__frequency_counter:
            if member_id in self.__frequency_counter[group_id]:
                # print("add_record1")
                self.__frequency_counter[group_id][member_id] += weight
            else:
                # print("add_record2")
                self.__frequency_counter[group_id][member_id] = weight
        else:
            # print("add_record3")
            self.__frequency_counter[group_id] = {}
            self.__frequency_counter[group_id][member_id] = weight
        # print("debug: ", self.__frequency_counter[group_id][member_id])
        if self.__frequency_counter[group_id][member_id] >= 13:
            self.add_temp_blacklist(group_id, member_id)
        print(self.__frequency_counter[group_id][member_id])

    def announce_judge(self, group_id: int, member_id: int):
        if group_id in self.__blacklist_announced:
            if member_id in self.__blacklist_announced[group_id]:
                # print("1__blacklist_announced: ", self.__blacklist_announced[group_id][member_id])
                return self.__blacklist_announced[group_id][member_id]
            else:
                self.__blacklist_announced[group_id][member_id] = False
                # print("2__blacklist_announced: ", self.__blacklist_announced[group_id][member_id])
                return False
        else:
            self.__blacklist_announced[group_id] = {}
            self.__blacklist_announced[group_id][member_id] = False
            # print("3__blacklist_announced: ", self.__blacklist_announced[group_id][member_id])
            return False

    def blacklist_announced(self, group_id: int, member_id: int):
        self.__blacklist_announced[group_id][member_id] = True
        # print("blacklist_announced: ", self.__blacklist_announced[group_id][member_id])


def frequency_limit(frequency_limit_instance: GlobalFrequencyLimitDict) -> None:
    """
    Frequency limit module

    Args:
        frequency_limit_instance: Frequency limit object

    Examples:
        limiter = Thread(target=frequency_limit, args=(frequency_limit_dict,))

    Return:
        None
    """
    while 1:
        time.sleep(10)
        frequency_limit_instance.set_zero()
