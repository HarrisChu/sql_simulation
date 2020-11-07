# -*- coding: utf-8 -*-


def cache(f):
    data = {}

    def wrapper(self, list_a, list_b):
        key = (tuple(list_a), tuple(list_b))
        if key in data:
            return data[key]
        else:
            value = f(self, list_a, list_b)
            data[key] = value
            return value

    return wrapper


class Generator(object):
    def __init__(self):
        self.gen_list = []

    def add_list(self, _list):
        self.gen_list.append(_list)
        sorted(self.gen_list, key=len)

    def generate(self):
        """
        有多个列表 list1, list2, list3, 长度分别为 m, n, k，合成长度为 m+n+k 的列表 list4,
        且 list1， list2, list3 为 list4 的子列表的所有组合
        :return: 所有组合 [list4, list4',....]
        """
        # TODO 生成器，减少空间
        assert len(self.gen_list) >= 2, '需要添加大于2个 list'
        result, other = [self.gen_list[0]], self.gen_list[1:]
        for l in other:
            result = self._generate_result_list(result, l)
        return result

    def _generate_result_list(self, result_list, list_b):
        result = []
        for l in result_list:
            result.extend(self.generate_two_list(l, list_b))
        return result

    @cache
    def generate_two_list(self, list_a, list_b):
        """
        生产两个列表的组合
        如果 list_b 长度是1，插入 list_a 的 gap 间隙。
        如果 list_b 长度不是1，将 list_b 的第一个元素插入到 gap，
        然后递归 list_a[gap:] 和 list 剩下的元素
        :param list_a:
        :param list_b:
        :return:
        """
        result = []
        if len(list_b) == 1:
            for index, value in enumerate(list_a):
                result.append(list_a[:index] + list_b + list_a[index:])
            result.append(list_a + list_b)
            return result
        else:
            b, sub_list_b = list_b[0], list_b[1:]
            gap_list = self._insert_gap(list_a, b)
            for prepared_list, index in gap_list:
                parsed_list, sub_list_a = prepared_list[:index + 1], list_a[index:]
                for _list in self.generate_two_list(sub_list_a, sub_list_b):
                    result.append(parsed_list + _list)
        return result

    def _insert_gap(self, _list, data):
        result = []
        for index, value in enumerate(_list):
            result.append((_list[:index] + [data] + _list[index:], index))
        result.append((_list + [data], len(_list)))
        return result
