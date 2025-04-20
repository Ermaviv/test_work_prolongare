import csv
import re
import unicodedata

STATISTIC_FILE = "financial_data.csv"
STUFF_FILE = "prolongations.csv"
WRITE_FILE = "counting_prolonging.csv"

STOP_WORDS = ['стоп', 'end']
NULL_WORDS = ['', 'в ноль']
SYMBOLS = dict((re.escape(k), v) for k, v in {",": ".", " ": ""}.items())
pattern = re.compile("|".join(SYMBOLS.keys()))


def decode_number(string):
    string = unicodedata.normalize("NFKC", string)
    string = pattern.sub(lambda m: SYMBOLS[re.escape(m.group(0))], string)
    if string in NULL_WORDS:
        string = 0
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

    # словарь, ключ - ФИО менеджера,
    # значение - список номеров его проектов в статистике
    stuff_row_nubmers = {}

    # сколько столбцов у таблицы
    length_table = len(statistic[0])

    kpi_1, kpi_2 = [], []

    head_table = statistic[0]
    head_table[0] = 'ФИО менеджера'
    del head_table[1:4]
    del head_table[-1]

    writer.writerow(head_table)
    # наполняем словарь stuff_row_nubmers
    for index in range(1, len(statistic)):
        full_name = statistic[index][-1]
        if full_name not in stuff_row_nubmers.keys():
            stuff_row_nubmers[full_name] = []
        stuff_row_nubmers[full_name].append(index)

    for manager in stuff_row_nubmers.keys():  # выбираем менеджера
        if manager == 'Федорова Марина Васильевна':
            manager = 'Федорова Марина Васильевна'
        ids_manager = stuff_row_nubmers[manager]  # номера строк в таблице для выбранного менеджера
        # добавляем ФИО менеджера для каждого КПД
        kpi_1.append(manager + ' КПД 1')
        kpi_2.append(manager + ' КПД 2')
        summ_for_pre_month = 0
        summ_for_pre_month_current_yes = 0
        summ_for_pre_pre_month_pre_no = 0
        summ_for_pre_pre_month_pre_no_current_yes = 0

        # преобразуем все "строковые" числа на float-числа
        # выбираем номер строки из statistic
        index_first_month = 2

        # приводим в порядок значения ячеек с суммами
        for id_row in ids_manager:
            # выбираем всю строку по ее номеру
            row = statistic[id_row]
            for index in range(index_first_month, length_table):
                if row[index] not in STOP_WORDS:
                    row[index] = decode_number(row[index])
                else:
                    for index_break in range(index, length_table):
                        row[index_break] = 0
                    break

        index_first_month_kpi = index_first_month + 2
        index_last_month_table = length_table-1
        for index_month in range(index_first_month_kpi, index_last_month_table):
            index_pre_month = index_first_month + 1
            index_pre_pre_month = index_first_month
            # суммируем все показатели за месяц
            for id_row in ids_manager:
                summ_for_pre_month += statistic[id_row][index_pre_month]
                if statistic[id_row][index_month] != 0:
                    summ_for_pre_month_current_yes += statistic[id_row][index_pre_month]
                # если пред-предыдущий месяц не пуст, а предыдущий месяц пуст, то...
                if (statistic[id_row][index_pre_pre_month] != 0 and
                        statistic[id_row][index_pre_month] == 0):
                    summ_for_pre_pre_month_pre_no += statistic[id_row][index_pre_pre_month]
                    if statistic[id_row][index_month] != 0:
                        summ_for_pre_pre_month_pre_no_current_yes += statistic[id_row][index_pre_pre_month]
            try:
                kpi_1.append('{:.3f}'.format(summ_for_pre_month_current_yes / summ_for_pre_month))
            except ZeroDivisionError:
                kpi_1.append(0)
            try:
                kpi_2.append('{:.3f}'.format(summ_for_pre_pre_month_pre_no_current_yes / summ_for_pre_pre_month_pre_no))
            except ZeroDivisionError:
                kpi_2.append(0)
        writer.writerow(kpi_1)
        writer.writerow(kpi_2)
        kpi_1.clear()
        kpi_2.clear()
