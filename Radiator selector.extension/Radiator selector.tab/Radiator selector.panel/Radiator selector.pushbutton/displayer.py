# -*- encoding: utf-8 -*-

from models import *

def display_issues(issues):
    issues_warning = []
    issues_error = []
    issues_unknown = []

    for issue in issues:
        if issue.severity == "WARNING":
            issues_warning.append(issue)
        elif issue.severity == "ERROR":
            issues_error.append(issue)
        else:
            issues_unknown.append(issue)

    for issue in issues_error:
        print(u"Ошибка: {}".format(issue.code))
        
    for issue in issues_warning:
        print(u"Предупреждение: {}".format(issue.code))
        
    for issue in issues_unknown:
        print(u"Неизвестная ошибка: {}".format(issue.code))

def run(problematic_windows, handler_result):
    if handler_result["outcome"] == "MODEL_PROCESS_SUCCESS":
        handler_status = get_status_from_issues(handler_result["issues"])
        if handler_status == "OK":
            print("Обработка модели завершена")
        elif handler_status == "WARNING":
            print("Обработка модели завершена с предупреждениями каталога")
            display_issues(handler_result["issues"])
        else:
            print(handler_result["issues"])
        print()
        print(u"Найдено комнат: {}".format(len(handler_result["rooms"])))

        room_status_ok_count = 0
        for room_data in handler_result["rooms"].values():
            if room_data["status"]=="OK":
                room_status_ok_count += 1
        print(u"Успешно обработано: {}".format(room_status_ok_count))

        room_status_warning_count = 0
        for room_data in handler_result["rooms"].values():
            if room_data["status"]=="WARNING":
                room_status_warning_count += 1
        print(u"Обработано с предупреждением: {}".format(room_status_warning_count))

        room_status_error_count = 0
        for room_data in handler_result["rooms"].values():
            if room_data["status"]=="ERROR":
                room_status_error_count += 1
        print(u"Не удалось обработать: {}".format(room_status_error_count))
        print()

        windows_issues = [issue for window in problematic_windows.values() for issue in window["issues"]]
        problematic_windows_status = get_status_from_issues(windows_issues)

        print(u"Найдено окон, для которых не удалось определить связь с помещением: {}".format(len(problematic_windows)))
        print()

        print("Результаты обработки модели:")
        print()

        for room_id, room_data in handler_result["rooms"].items():
            print(u"Помещение {} - '{}'".format(room_data["number"], room_data["name"]))
            room_heat_power = room_data["required_heat_power_w"]
            if room_data["outcome"] == "ROOM_PROCESS_SUCCESS":
                print(u"Требуемая тепловая мощность: {} Вт".format(room_heat_power))
                print(u"Подобранный радиатор: {}".format(room_data["radiator"]["article"]))
                radiator_heat_transfer = room_data["radiator"]["heat_transfer"]
                print(u"Мощность радиатора: {} Вт".format(radiator_heat_transfer))
                power_reserve_pct = round((radiator_heat_transfer-room_heat_power)/float(room_heat_power)*100, 2)
                print(u"Запас: {}%".format(power_reserve_pct))
                print(u"Статус: {}".format(get_status_from_issues(room_data["issues"])))
                display_issues(room_data["issues"])
                print()
            elif room_data["outcome"] == "ROOM_PROCESS_SKIPPED":
                if room_data["no_windows"]:
                    if room_heat_power is not None:
                        print(u"Требуемая тепловая мощность: {} Вт".format(room_heat_power))
                    print(u"Не имеет связанных наружных окон. Подбор радиатора пропущен.")
                    display_issues(room_data["issues"])
                    print()
                else:
                    if room_heat_power is not None:
                        print(u"Требуемая тепловая мощность: {} Вт".format(room_heat_power))
                    print(u"Было пропущено. Смотрите ошибки и предупреждения")
                    display_issues(room_data["issues"])
                    print()
            elif room_data["outcome"] == "ROOM_PROCESS_FAILED":
                room_heat_power = room_data["required_heat_power_w"]
                if room_heat_power is not None:
                    print(u"Требуемая тепловая мощность: {} Вт".format(room_heat_power))
                print(u"Не прошло подбор и имеет ошибки")
                display_issues(room_data["issues"])
                print()
        
        if len(problematic_windows) != 0:
            print(u"Ошибки и предупреждения окон:")
            print()
            for window_id, window_info in problematic_windows.items():
                print(u"Окно (id:{}):".format(window_id))
                display_issues(window_info["issues"])
    elif handler_result["outcome"] == "MODEL_PROCESS_FAILED":
        print(u"Обработчик помещений вернул ошибку. Изучите их и исправьте.")
        display_issues(handler_result["issues"])