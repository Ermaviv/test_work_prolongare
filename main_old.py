import csv
import re
import unicodedata

STATISTIC_FILE = "financial_data.csv"
STUFF_FILE = "prolongations.csv"
WRITE_FILE = "counting_prolonging.csv"
STOP_WORDS = ['', 'в ноль', 'стоп', 'end']


SYMBOLS = dict((re.escape(k), v) for k, v in {",": ".", " ": ""}.items())
pattern = re.compile("|".join(SYMBOLS.keys()))


def encode_number(string):
    try:
        string = unicodedata.normalize("NFKC", string)
    except TypeError:
        return string
    string = pattern.sub(lambda m: SYMBOLS[re.escape(m.group(0))], string)
    try:
        string = float(string)
    except ValueError:
        string = 0
    return string


with (
    open(STATISTIC_FILE, 'r', encoding='utf8') as statistic_file,
    open(STUFF_FILE, 'r', encoding='utf8') as stuff_file,
    open(WRITE_FILE, 'w', encoding='utf8') as write_file
):
    stuff = list(csv.reader(stuff_file))
    statistic = list(csv.reader(statistic_file))
    writer = csv.writer(write_file)

    # словарь, где ключ - ФИО менеджера, значение - список сумм за месяц
    stuff_money = {}

    # словарь, где ключ - ФИО менеджера, значение - список id его проектов
    sort_stuff_ids = {}

    for manager in stuff:
        try:
            manager[0] = int(manager[0])
        except ValueError:
            continue
        if manager[2] not in sort_stuff_ids.keys():
            sort_stuff_ids[manager[2]] = []
            stuff_money[manager[2]] = []
        sort_stuff_ids[manager[2]].append(manager[0])

    for manager in sort_stuff_ids.keys():  # выбираем менеджера
        # какие проекты делал менеджер (копия списка из словаря)
        ids_manager = sort_stuff_ids[manager]
        summ_for_pre_month = 0
        summ_for_pre_month_current_no = 0
        summ_for_pre_pre_month_pre_no = 0
        summ_for_pre_pre_month_pre_no_current_yes = 0
        # номера строк в statistic, соответствующие id-проектам, которыми занимался менеджер
        ids_row_in_statistic = []

        for id_1 in ids_manager:  # берем по 1-му id проекта, что делал менеджер
            for row in statistic:  # проверяем все строки из файла со статистикой...
                try:
                    row[0] = int(row[0])
                except ValueError:
                    continue

                if row[0] == id_1:  # первая колонка строки из statistic соответствует искомой
                    for index in range(2, len(row)-1):
                        if type(row[index]) is not float():  # костыль
                            row[index] = encode_number(row[index])
                    # индекс (вагонетка) у месяца
                    index_month = 4
                    while index_month < len(row):
                        # смотрим суммы за для 1-ого КПД
                        if row[index_month-1] not in STOP_WORDS:
                            summ_for_pre_month += row[index_month-1]
                            if row[index_month] in STOP_WORDS:
                                summ_for_pre_month_current_no += row[index_month-1]
                        try:
                            KPD_1 = summ_for_pre_month_current_no / summ_for_pre_month
                        except ZeroDivisionError:
                            KPD_1 = 0
                        writer.writerow(str(KPD_1))
                        # смотрим суммы за для 2-ого КПД
                        row[index_month-2] = row[index_month-2]
                        if row[index_month-2] not in STOP_WORDS and row[index_month-1] in STOP_WORDS:
                            summ_for_pre_pre_month_pre_no += row[index_month-2]
                            if row[index_month] not in STOP_WORDS:
                                summ_for_pre_pre_month_pre_no_current_yes += row[index_month-2]
                        try:
                            KPD_2 = summ_for_pre_pre_month_pre_no_current_yes / summ_for_pre_pre_month_pre_no
                        except ZeroDivisionError:
                            KPD_2 = 0
                        writer.writerow(str(KPD_2))
                        index_month += 1
