# -*- coding: utf-8 -*-
import traceback

from models import *

def main():
    from pyrevit import revit
    from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, BuiltInParameter, UnitUtils, UnitTypeId, StorageType, ElementId, ElementOnPhaseStatus

    import handler, displayer

    def resolve_window_placement(window, rooms_inputs_by_id, phase):
        window_placement_result = {
            "outcome": None, # "ROOM_FOUND" / "ROOM_NOT_FOUND"
            "placement": None,
            "room": None,
            "issues": [],
            }

        from_room = window.FromRoom[phase]
        to_room = window.ToRoom[phase]

        if to_room and from_room:
            window_placement_result["outcome"] = "ROOM_NOT_FOUND"
            window_placement_result["placement"] = "BETWEEN_TWO_ROOMS"
            window_placement_result["issues"].append(Issue(
                IssueCode.INTERNAL_WINDOW,
                Stage.COLLECT_MODEL_INPUT,
                Severity.WARNING,
                IssueContext(id=window.Id.Value),
            ))
        elif (to_room and not from_room) or (not to_room and from_room):
            window_placement_result["placement"] = "ASSOCIATED_WITH_ROOM"
            window_placement_result["room"] = from_room if from_room else to_room
            room_window_id = window_placement_result["room"].Id.Value
            if room_window_id in rooms_inputs_by_id.keys():
                window_placement_result["outcome"] = "ROOM_FOUND"
            else:
                window_placement_result["outcome"] = "ROOM_NOT_FOUND"
                window_placement_result["issues"].append(Issue(
                    IssueCode.ASSOCIATED_ROOM_MISSING,
                    Stage.COLLECT_MODEL_INPUT,
                    Severity.ERROR,
                    IssueContext(id=window.Id.Value),
                ))
        else:
            window_placement_result["outcome"] = "ROOM_NOT_FOUND"
            window_placement_result["placement"] = "NO_ROOMS"
            window_placement_result["issues"].append(Issue(
                IssueCode.WINDOW_HAS_NO_ROOM,
                Stage.COLLECT_MODEL_INPUT,
                Severity.ERROR,
                IssueContext(id=window.Id.Value),
            ))
        return window_placement_result

    def resolve_window_width(window):
        window_width_result = {
            "width_mm": None,
            "issues": []
        }

        window_width_parameter = window.Symbol.get_Parameter(BuiltInParameter.WINDOW_WIDTH)
        if window_width_parameter:
            if window_width_parameter.StorageType == StorageType.Double:
                if window_width_parameter.AsDouble() > 0:
                    width_mm = UnitUtils.ConvertFromInternalUnits(
                        window_width_parameter.AsDouble(),
                        UnitTypeId.Millimeters
                        )
                    width_mm = round(width_mm, 3)
                    window_width_result["width_mm"] = width_mm
                else:
                    window_width_result["issues"].append(Issue(
                        IssueCode.WIDTH_PARAMETER_NOT_POSITIVE,
                        Stage.COLLECT_MODEL_INPUT,
                        Severity.ERROR,
                        IssueContext(id=window.Id.Value),
                    ))
            else:
                window_width_result["issues"].append(Issue(
                    IssueCode.WIDTH_PARAMETER_WRONG_TYPE,
                    Stage.COLLECT_MODEL_INPUT,
                    Severity.ERROR,
                    IssueContext(id=window.Id.Value),
                ))
        else:
            window_width_result["issues"].append(Issue(
                IssueCode.WIDTH_PARAMETER_MISSING,
                Stage.COLLECT_MODEL_INPUT,
                Severity.ERROR,
                IssueContext(id=window.Id.Value),
            ))
        return window_width_result
    
    def resolve_required_heat_power(room):
        required_heat_power_result = {
            "required_heat_power_w": None,
            "issues": []
        }
        required_heat_power_parameter = room.LookupParameter(u"Требуемая тепловая мощность")
        if required_heat_power_parameter:
            if required_heat_power_parameter.StorageType == StorageType.Double:
                if required_heat_power_parameter.AsDouble() > 0:
                    required_heat_power_w = UnitUtils.ConvertFromInternalUnits(
                        required_heat_power_parameter.AsDouble(),
                        UnitTypeId.Watts
                        )
                    required_heat_power_result["required_heat_power_w"] = required_heat_power_w
                else:
                    required_heat_power_result["issues"].append(Issue(
                        IssueCode.WRONG_VALUE_HEAT_POWER_PARAMETER,
                        Stage.COLLECT_MODEL_INPUT,
                        Severity.ERROR,
                    ))
            else:
                required_heat_power_result["issues"].append(Issue(
                    IssueCode.WRONG_TYPE_HEAT_POWER_PARAMETER,
                    Stage.COLLECT_MODEL_INPUT,
                    Severity.ERROR,
                ))
        else:
            required_heat_power_result["issues"].append(Issue(
                IssueCode.NO_HEAT_POWER_PARAMETER,
                Stage.COLLECT_MODEL_INPUT,
                Severity.ERROR,
            ))
        return required_heat_power_result

    doc = revit.doc

    rooms = (
        FilteredElementCollector(doc)
        .OfCategory(BuiltInCategory.OST_Rooms)
        .WhereElementIsNotElementType()
        .ToElements()
    )

    windows = (
        FilteredElementCollector(doc)
        .OfCategory(BuiltInCategory.OST_Windows)
        .WhereElementIsNotElementType()
        .ToElements()
        )

    active_view_phase_parameter = doc.ActiveView.get_Parameter(BuiltInParameter.VIEW_PHASE)

    if active_view_phase_parameter is None:
        print(u"Активный вид не содержит параметр фазы")
        print(u"Выполнение Radiator Selector невозможно")
        return
    
    active_view_phase_id = active_view_phase_parameter.AsElementId()

    active_view_phase = doc.GetElement(active_view_phase_id)

    model_input = {
        # room.Id.Value: room_input
    }

    for room in rooms:
        room_input = {
            "name": room.get_Parameter(BuiltInParameter.ROOM_NAME).AsString(),
            "number": room.get_Parameter(BuiltInParameter.ROOM_NUMBER).AsString(),
            "required_heat_power_w": None,
            "windows": {},
            "issues": [],
        }

        room_phase_id = room.get_Parameter(BuiltInParameter.ROOM_PHASE_ID).AsElementId()

        if not room_phase_id == active_view_phase_id:
            continue
        
        if not(room.Area > 0 and room.Location):
            room_input["issues"].append(Issue(
                IssueCode.WRONG_GEOMETRIC,
                Stage.COLLECT_MODEL_INPUT,
                Severity.ERROR,
            ))
            model_input[room.Id.Value] = room_input
            continue
        
        required_heat_power_result = resolve_required_heat_power(room)
        if required_heat_power_result["required_heat_power_w"]:
            room_input["required_heat_power_w"] = required_heat_power_result["required_heat_power_w"]
        else:
            room_input["issues"].extend(required_heat_power_result["issues"])

        model_input[room.Id.Value] = room_input

    problematic_windows = {}

    for window in windows:
        window_input = {
            "placement": None,
            "width_mm": None,
            "issues": [],
        }

        phase_status = window.GetPhaseStatus(active_view_phase_id)

        window_exists_in_active_view_phase = phase_status in (ElementOnPhaseStatus.New, ElementOnPhaseStatus.Existing)

        if not window_exists_in_active_view_phase:
            continue

        window_width_result = resolve_window_width(window)
        if window_width_result["width_mm"] is not None:
            window_input["width_mm"] = window_width_result["width_mm"]
        else:
            window_input["issues"].extend(window_width_result["issues"])
        
        window_placement_result = resolve_window_placement(window, model_input, active_view_phase)
        window_input["placement"] = window_placement_result["placement"]
        window_input["issues"].extend(window_placement_result["issues"])
        if window_placement_result["outcome"] == "ROOM_FOUND":
            model_input[window_placement_result["room"].Id.Value]["windows"][window.Id.Value] = window_input
        else:
            problematic_windows[window.Id.Value] = window_input
    
    handler_result = handler.process_model(model_input)

    displayer.run(problematic_windows, handler_result)
    
try:
    main()
except Exception:
    print(u"Radiator Selector завершился с непредвиденной ошибкой.")
    print(u"Подробности приведены ниже для диагностики:")
    print(traceback.format_exc())