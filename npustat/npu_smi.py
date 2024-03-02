#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re

sub_space_p = re.compile(r"[ ]{2,}")  # 用于将多个连续空格替换成单个空格

card_info = '''+------------------------------------------------------------------------------------------------+
| npu-smi 23.0.rc3.3               Version: 23.0.rc3.3                                           |
+---------------------------+---------------+----------------------------------------------------+
| NPU   Name                | Health        | Power(W)    Temp(C)           Hugepages-Usage(page)|
| Chip                      | Bus-Id        | AICore(%)   Memory-Usage(MB)  HBM-Usage(MB)        |
+===========================+===============+====================================================+
| 0     910B3               | OK            | 133.9       43                0    / 0             |
| 0                         | 0000:C1:00.0  | 0           0    / 0          60478/ 65536         |
+===========================+===============+====================================================+
| 1     910B3               | OK            | 147.8       41                0    / 0             |
| 0                         | 0000:C2:00.0  | 93          0    / 0          60060/ 65536         |
+===========================+===============+====================================================+
| 2     910B3               | OK            | 194.0       48                0    / 0             |
| 0                         | 0000:81:00.0  | 94          0    / 0          60059/ 65536         |
+===========================+===============+====================================================+
| 3     910B3               | OK            | 206.1       43                0    / 0             |
| 0                         | 0000:82:00.0  | 89          0    / 0          60058/ 65536         |
+===========================+===============+====================================================+
| 4     910B3               | OK            | 201.1       52                0    / 0             |
| 0                         | 0000:01:00.0  | 83          0    / 0          60059/ 65536         |
+===========================+===============+====================================================+
| 5     910B3               | OK            | 150.1       52                0    / 0             |
| 0                         | 0000:02:00.0  | 0           0    / 0          60059/ 65536         |
+===========================+===============+====================================================+
| 6     910B3               | OK            | 157.6       55                0    / 0             |
| 0                         | 0000:41:00.0  | 9           0    / 0          60058/ 65536         |
+===========================+===============+====================================================+
| 7     910B3               | OK            | 177.3       53                0    / 0             |
| 0                         | 0000:42:00.0  | 89          0    / 0          60058/ 65536         |
+===========================+===============+====================================================+
+---------------------------+---------------+----------------------------------------------------+
| NPU     Chip              | Process id    | Process name             | Process memory(MB)      |
+===========================+===============+====================================================+
| 0       0                 | 683932        | python                   | 56154                   |
+===========================+===============+====================================================+
| 1       0                 | 683933        | python                   | 55755                   |
+===========================+===============+====================================================+
| 2       0                 | 683934        | python                   | 55754                   |
+===========================+===============+====================================================+
| 3       0                 | 683935        | python                   | 55754                   |
+===========================+===============+====================================================+
| 4       0                 | 683936        | python                   | 55755                   |
+===========================+===============+====================================================+
| 5       0                 | 683937        | python                   | 55755                   |
+===========================+===============+====================================================+
| 6       0                 | 683938        | python                   | 55755                   |
+===========================+===============+====================================================+
| 7       0                 | 683939        | python                   | 55755                   |
+===========================+===============+====================================================+
'''

class GetEntryCardListV1:
    """
                +------------------------------------------------------------------------------------------------+
                | npu-smi 23.0.rc3.3               Version: 23.0.rc3.3                                           |
                +---------------------------+---------------+----------------------------------------------------+
                | NPU   Name                | Health        | Power(W)    Temp(C)           Hugepages-Usage(page)|
                | Chip                      | Bus-Id        | AICore(%)   Memory-Usage(MB)  HBM-Usage(MB)        |
                +===========================+===============+====================================================+
    line 1 ==>  | 0     910B3               | OK            | 133.9       43                0    / 0             |
    line 2 ==>  | 0                         | 0000:C1:00.0  | 0           0    / 0          60478/ 65536         |
                +===========================+===============+====================================================+
    line 1 ==>  | 1     910B3               | OK            | 147.8       41                0    / 0             |
    line 2 ==>  | 0                         | 0000:C2:00.0  | 93          0    / 0          60060/ 65536         |
                +===========================+===============+====================================================+
    """

    # card id, chip name, health, power, temp, Hugepages-Usage
    # | 0 910B3 | OK | 133.9 43 0 / 0 |
    # ('0', '910B3', 'OK', '133.9', '43', '0', '0')
    pattern = r"\| (\d+) (\w+) \| (\w+) \| (\d+\.\d+) (\d+) (\d+) / (\d+) \|"
    line_1_p = re.compile(pattern)

 
    # chip id, bus id, ai core, Memory-Usage, HBM-Usage
    # | 0 | 0000:C1:00.0 | 0 0 / 0 60478/ 65536 |
    # ('0', '0000:C1:00.0', '0', '0', '0', '60478', '65536')
    pattern = r"\| (\d+) \| ([\d:A-Z\.]+) \| (\d+) (\d+) / (\d+) (\d+)/ (\d+) \|"
    line_2_p = re.compile(pattern)

    # npu-smi info 命令返回值中没有 card_type 信息，首次展示前需要调用 npu-smi info -t product -i {card_id} 命令获取该信息
    # 对 card_type 信息举例："Atlas 300I Model 3000"
    card_id_to_card_type: dict = None

    @staticmethod
    def get_card_type(all_card_ids):
        if not GetEntryCardListV1.card_id_to_card_type:
            card_id_to_card_type = {}
            for card_id in all_card_ids:
                # cmd_result = os.popen(f"npu-smi info -t product -i {card_id}").read()
                # arr = cmd_result.split(":")
                # if len(arr) == 2:
                #     card_id_to_card_type[card_id] = arr[1].strip()
                card_id_to_card_type[card_id] = "Atlas A2"

            GetEntryCardListV1.card_id_to_card_type = card_id_to_card_type
        return GetEntryCardListV1.card_id_to_card_type

    def get_card_entry(self, atlas_card_info):
        line_1_list, line_2_list = [], []
        for line in atlas_card_info.split("\n"):
            line = sub_space_p.sub(" ", line)
            m1 = self.line_1_p.search(line)
            m2 = self.line_2_p.search(line)

            if m1 is not None and m2 is not None:
                raise RuntimeError(f"解析 npu-smi info 结果失败，同一行匹配上两个正则，"
                                   f"line: {line}")

            if m1:
                line_1_list.append(m1.groups())
            if m2:
                line_2_list.append(m2.groups())

        if len(line_1_list) != len(line_2_list):
            raise RuntimeError(f"解析 npu-smi info 结果失败，两个正则匹配上的行数不同\n"
                               f"{atlas_card_info}")

        all_card_ids = sorted(set([line[0] for line in line_1_list])) # line[0] is card_id
        card_id_to_card_type = GetEntryCardListV1.get_card_type(all_card_ids)

        card_entry_list, chip_entry_list = [], []
        card_entry = dict()

        for line1, line2 in zip(line_1_list, line_2_list):
            card_id, chip_name, health, power, temp, _, _ = line1
            chip_id, bus_id, ai_core, _, _, memory_used, memory_total = line2

            if len(chip_entry_list) > 0 and chip_entry_list[-1]["card_id"] != card_id:
                tmp_card_id = chip_entry_list[-1]["card_id"]
                card_entry["card_id"] = tmp_card_id
                card_entry["type"] = card_id_to_card_type.get(tmp_card_id, "??")
                card_entry["chip_entry_list"] = chip_entry_list
                card_entry_list.append(card_entry)

                card_entry = dict()
                chip_entry_list = []

            entry = dict()
            entry["card_id"] = card_id
            entry["chip_id"] = chip_id
            entry["device_id"] = card_id
            entry["health"] = health
            entry["chip_name"] = f"Ascend {chip_name}"
            entry["temperature"] = self.get_temperature(temp)
            entry["ai_core_usage"] = self.get_ai_core_usage(ai_core)
            entry["memory_used"] = f"{memory_used}"
            entry["memory_total"] = f"{memory_total} MB"
            entry["power"] = self.get_power(power)
            entry["bus_id"] = bus_id
            chip_entry_list.append(entry)

        if len(chip_entry_list) > 0:
            tmp_card_id = chip_entry_list[-1]["card_id"]
            card_entry["card_id"] = tmp_card_id
            card_entry["type"] = card_id_to_card_type.get(tmp_card_id, "??")
            card_entry["chip_entry_list"] = chip_entry_list
            card_entry_list.append(card_entry)

        return card_entry_list

    def get_ai_core_usage(self, ai_core_usage):
        s = str(ai_core_usage).strip()
        if isinstance(s, str) and s.isdigit():
            s = int(s)
        return s

    def get_temperature(self, temp):
        if temp.endswith("C"):
            temp = temp[:-1].strip()
        if isinstance(temp, str) and temp.isdigit():
            temp = int(temp)
        return temp

    def get_power(self, power):
        power = power.strip()
        if power.endswith("W"):
            power = power[:-1].strip()
        try:
            power = float(power)
            return f"{power:.2f} W"
        except Exception:
            return f"{power} W"


class GetCardStatusWithNpuSmi:
    # 下面这个正则中：第一个版本是npu-smi的版本，第二个版本是驱动版本
    version_p = re.compile(r"\| npu-smi ([0-9a-z.]{2,20}?) Version: [0-9a-z.]{2,20}? \|")

    version2func = {
        "23.0.rc3.3": GetEntryCardListV1,

        # 默认
        "default": GetEntryCardListV1,
    }

    def new_query(self):
        atlas_card_info = os.popen("npu-smi info").read()
        # atlas_card_info = card_info
        version = self.get_version(atlas_card_info)

        if version in self.version2func:
            my_class = self.version2func[version]()
        else:
            my_class = self.version2func["default"]()

        entry_list = my_class.get_card_entry(atlas_card_info)
        return f"npu-smi version : {version}", entry_list

    def get_version(self, atlas_card_info):
        result_list = []
        for line in atlas_card_info.split("\n"):
            line = sub_space_p.sub(" ", line)
            my_match = self.version_p.search(line)
            if my_match:
                result_list.append(my_match)

        if len(result_list) == 1:
            return result_list[0].groups()[0]
        return None

if __name__ == "__main__":
    my_class = GetCardStatusWithNpuSmi()
    result = my_class.new_query()
    print(result)