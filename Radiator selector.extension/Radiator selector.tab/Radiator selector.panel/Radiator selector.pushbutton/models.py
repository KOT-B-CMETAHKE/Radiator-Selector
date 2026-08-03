def get_status_from_issues(issues):
    warning_issue_count = 0
    error_issue_count = 0
    for issue in issues:
        if issue.severity == "WARNING":
            warning_issue_count += 1
        elif issue.severity == "ERROR":
            error_issue_count += 1
    if error_issue_count > 0:
        return "ERROR"
    elif warning_issue_count > 0:
        return "WARNING"
    else:
        return "OK"

# status
STATUS_OK = "OK"
STATUS_WARNING = "WARNING"
STATUS_ERROR = "ERROR"

class Issue():
    def __init__(self, code, stage, severity, context=None):
        self.code = code
        self.stage = stage
        self.severity = severity
        self.context = context

class IssueCode():
    # script.py
    INTERNAL_WINDOW = "INTERNAL_WINDOW"
    ASSOCIATED_ROOM_MISSING = "ASSOCIATED_ROOM_MISSING"
    WINDOW_HAS_NO_ROOM = "WINDOW_HAS_NO_ROOM"

    WIDTH_PARAMETER_NOT_POSITIVE = "WIDTH_PARAMETER_NOT_POSITIVE"
    WIDTH_PARAMETER_WRONG_TYPE = "WIDTH_PARAMETER_WRONG_TYPE"
    WIDTH_PARAMETER_MISSING = "WIDTH_PARAMETER_MISSING"

    WRONG_VALUE_HEAT_POWER_PARAMETER = "WRONG_VALUE_HEAT_POWER_PARAMETER"
    WRONG_TYPE_HEAT_POWER_PARAMETER = "WRONG_TYPE_HEAT_POWER_PARAMETER"
    NO_HEAT_POWER_PARAMETER = "NO_HEAT_POWER_PARAMETER"

    WRONG_GEOMETRIC = "WRONG_GEOMETRIC"

    # handler.py
    ROOM_HAS_NO_WINDOWS = "ROOM_HAS_NO_WINDOWS"
    INCORRECT_NUMBER_OF_WINDOWS = "INCORRECT_NUMBER_OF_WINDOWS"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"

    # selector.py
    NO_SUITABLE_RADIATOR = "NO_SUITABLE_RADIATOR"
    EXCEEDED_DESIRABLE_POWER_RESERVE = "EXCEEDED_DESIRABLE_POWER_RESERVE"

    # catalog.py
    REQUIRED_PARAMETER_TITLE_MISSING = "REQUIRED_PARAMETER_TITLE_MISSING"
    ALL_CATALOG_LINES_CONSIDERED_INCORRECT = "ALL_CATALOG_LINES_CONSIDERED_INCORRECT"
    SOME_CATALOG_LINES_INCORRECT = "SOME_CATALOG_LINES_INCORRECT"
    CATALOG_FILE_MISSING = "CATALOG_FILE_MISSING"
    UNKNOWN_ERROR_WHILE_CATALOG_LOAD = "UNKNOWN_ERROR_WHILE_CATALOG_LOAD"


class Stage():
    COLLECT_MODEL_INPUT = "COLLECT_MODEL_INPUT"
    PROCESS_ROOM = "PROCESS_ROOM"
    SELECT_RADIATOR = "SELECT_RADIATOR"
    CATALOG_LOAD = "CATALOG_LOAD"

class Severity():
    WARNING = "WARNING"
    ERROR = "ERROR"

class IssueContext():
    def __init__(self, 
                id=None, 
                actual_power_reserve_pct=None, 
                radiators_load_success_pct=None, 
                unknown_error=None):
        self.id = id
        self.actual_power_reserve_pct = actual_power_reserve_pct
        self.radiators_load_success_pct = radiators_load_success_pct
        self.unknown_error = unknown_error