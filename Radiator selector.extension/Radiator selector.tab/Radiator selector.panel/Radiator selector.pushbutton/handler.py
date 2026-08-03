# -*- encoding: utf-8 -*-

import selector, catalog

from models import *

def process_room(room_data, radiator_catalog):
    room_result = {
        "outcome": None, # ROOM_PROCESS_SUCCESS / ROOM_PROCESS_SKIPPED / ROOM_PROCESS_FAILED
        "status": None, 
        "name": room_data["name"],
        "number": room_data["number"],
        "required_heat_power_w": room_data["required_heat_power_w"],
        "no_windows": False,
        "radiator": None,
        "issues": list(room_data["issues"])
    }

    room_windows = room_data["windows"]

    windows_issues = [issue for window in room_windows.values() for issue in window["issues"]]

    room_result["issues"].extend(windows_issues)

    has_model_errors = any(issue.severity == "ERROR" for issue in room_result["issues"])

    if has_model_errors:
        room_result["outcome"] = "ROOM_PROCESS_FAILED"
        room_result["status"] = get_status_from_issues(room_result["issues"])
        return room_result

    if len(room_windows) == 0:
        room_result["outcome"] = "ROOM_PROCESS_SKIPPED"
        room_result["no_windows"] = True
        room_result["issues"].append(Issue(
            IssueCode.ROOM_HAS_NO_WINDOWS,
            Stage.PROCESS_ROOM,
            Severity.WARNING
        ))
        room_result["status"] = get_status_from_issues(room_result["issues"])
        return room_result
    elif len(room_windows) == 1:
        for window_id in room_windows:
            window_width_mm = room_windows[window_id]["width_mm"]
        pass
    else:
        room_result["outcome"] = "ROOM_PROCESS_FAILED"
        room_result["issues"].append(Issue(
            IssueCode.INCORRECT_NUMBER_OF_WINDOWS,
            Stage.PROCESS_ROOM,
            Severity.ERROR,
        ))
        room_result["status"] = get_status_from_issues(room_result["issues"])
        return room_result
    
    required_heat_power_w = room_data["required_heat_power_w"]

    selection_result = selector.select_radiator(window_width_mm, required_heat_power_w, radiator_catalog)

    if selection_result["outcome"] == "RADIATOR_SELECTED":
        room_result["outcome"] = "ROOM_PROCESS_SUCCESS"
        room_result["radiator"] = selection_result["radiator"]
        room_result["issues"].extend(selection_result["issues"])
        room_result["status"] = get_status_from_issues(room_result["issues"])
    elif selection_result["outcome"] == "RADIATOR_NOT_SELECTED":
        room_result["outcome"] = "ROOM_PROCESS_FAILED"
        room_result["issues"].extend(selection_result["issues"])
        room_result["status"] = get_status_from_issues(room_result["issues"])
    else:
        room_result["outcome"] = "ROOM_PROCESS_FAILED"
        room_result["issues"].append(Issue(
            IssueCode.UNKNOWN_ERROR,
            Stage.PROCESS_ROOM,
            Severity.ERROR,
        ))
        room_result["status"] = get_status_from_issues(room_result["issues"])
        
    return room_result

def process_model(room_inputs_by_id):
    handler_result = {
        "outcome": None, # MODEL_PROCESS_SUCCESS / MODEL_PROCESS_FAILED
        "rooms": {
            # room.Id.Value: room_result
        },
        "issues": [],
    }

    catalog_loader = catalog.load()

    if catalog_loader["outcome"] == "CATALOG_LOAD_SUCCESS":
        handler_result["outcome"] = "MODEL_PROCESS_SUCCESS"
        radiator_catalog = catalog_loader["radiator_catalog"]
        handler_result["issues"].extend(catalog_loader["issues"])
    else:
        handler_result["outcome"] = "MODEL_PROCESS_FAILED"
        handler_result["issues"].extend(catalog_loader["issues"])
        return handler_result

    for room_id, room_input_data in room_inputs_by_id.items():
        room_result = process_room(room_input_data, radiator_catalog)
        
        handler_result["rooms"][room_id] = room_result

    return handler_result