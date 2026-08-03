# -*- coding:utf-8 -*-

from models import *

def select_radiator(window_width_mm, required_heat_power, radiator_catalog):
    select_radiator_result = {
        "outcome": None, # RADIATOR_SELECTED / RADIATOR_NOT_SELECTED
        "radiator": None,
        "issues": []
    }

    HEAT_POWER_NAME = "heat_transfer"
    RADIATOR_LENGTH_NAME = "length"

    min_power_reserve_pct = 10
    max_desirable_power_reserve_pct = 15
    max_acceptable_power_reserve_pct = 20

    desirable_radiators = []
    acceptable_radiators = []

    for radiator in radiator_catalog:
        power_reserve_pct = (radiator[HEAT_POWER_NAME]-required_heat_power)/float(required_heat_power)*100

        if min_power_reserve_pct <= power_reserve_pct <= max_desirable_power_reserve_pct and (
            window_width_mm*0.5 <= radiator[RADIATOR_LENGTH_NAME] <= window_width_mm*0.85):
            desirable_radiators.append(radiator)
        elif max_desirable_power_reserve_pct < power_reserve_pct <= max_acceptable_power_reserve_pct and (
            window_width_mm*0.5 <= radiator[RADIATOR_LENGTH_NAME] <= window_width_mm*0.85):
            acceptable_radiators.append(radiator)

    if len(desirable_radiators) == 0:
        if len(acceptable_radiators) == 0:
            select_radiator_result["outcome"] = "RADIATOR_NOT_SELECTED"
            select_radiator_result["issues"].append(Issue(
                IssueCode.NO_SUITABLE_RADIATOR,
                Stage.SELECT_RADIATOR,
                Severity.ERROR,
            ))
        else:
            acceptable_radiators.sort(key=lambda radiator: radiator[HEAT_POWER_NAME])
            suitable_radiator = acceptable_radiators[0]
            actual_power_reserve_pct = (suitable_radiator[HEAT_POWER_NAME]-required_heat_power)/float(required_heat_power)*100

            select_radiator_result["outcome"] = "RADIATOR_SELECTED"
            select_radiator_result["radiator"] = suitable_radiator
            select_radiator_result["issues"].append(Issue(
                IssueCode.EXCEEDED_DESIRABLE_POWER_RESERVE,
                Stage.SELECT_RADIATOR,
                Severity.WARNING,
                IssueContext(actual_power_reserve_pct=actual_power_reserve_pct)
            ))
    else:
        desirable_radiators.sort(key=lambda radiator: radiator[HEAT_POWER_NAME])
        suitable_radiator = desirable_radiators[0]
        select_radiator_result["outcome"] = "RADIATOR_SELECTED"
        select_radiator_result["radiator"] = suitable_radiator

    return select_radiator_result