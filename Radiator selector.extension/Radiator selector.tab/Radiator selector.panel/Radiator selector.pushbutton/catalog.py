# -*- coding:utf-8 -*-

import os, csv

from models import *

def load():
    def correct_form(input_value, required_function, replace_comma_to_dot=False):    
        if input_value:
            if replace_comma_to_dot:
                value = input_value.replace(",", ".")
            else:
                value = input_value
            try:
                result_value = required_function(value)
                return result_value
            except Exception:
                return None
        else:
            return None

    catalog_loader_result = {
        "outcome": None, # "CATALOG_LOAD_SUCCESS", "CATALOG_LOAD_FAILED"
        "radiator_catalog": [],
        "issues": [],
    }
        
    script_directory = os.path.dirname(os.path.abspath(__file__))

    csv_path = os.path.join(
        script_directory,
        u"radiators.csv"
    )

    translations_dictionary = {
        "article": ["артикул", "article"],
        "heat_transfer": ["теплоотдача", "heat transfer"],
        "length": ["длина", "length"],
    }

    parameter_to_csv_name_dictionary = {
        "article": None,
        "heat_transfer": None,
        "length": None,
    }
    if os.path.isfile(csv_path):
        try:
            with open(csv_path, "r") as file:
                csv_reader = csv.DictReader(file, delimiter=";")

                headers = csv_reader.fieldnames

                radiator_parameters = ["article", "heat_transfer", "length"]

                for radiator_parameter in radiator_parameters:
                    translate_options = translations_dictionary[radiator_parameter]
                    option_found = False
                    for translate_option in translate_options:
                        for dict_characteristic_name in headers:
                            if translate_option == dict_characteristic_name.decode("utf-8-sig").lower():
                                parameter_to_csv_name_dictionary[radiator_parameter] = dict_characteristic_name.decode("utf-8-sig")
                                option_found = True
                    if not option_found:
                        catalog_loader_result["outcome"] = "CATALOG_LOAD_FAILED"
                        catalog_loader_result["issues"].append(Issue(
                            IssueCode.REQUIRED_PARAMETER_TITLE_MISSING,
                            Stage.CATALOG_LOAD,
                            Severity.ERROR,
                        ))
                        return catalog_loader_result

                problematic_radiators = []
                radiators_input_count = 0

                for radiator_input in csv_reader:
                    radiator_output = {
                        "article": None,
                        "heat_transfer": None,
                        "length": None,
                    }

                    radiators_input_count += 1

                    unicode_radiator_input = {
                        # parameter_unicode: value_unicode
                    }

                    for parameter, value in radiator_input.items():
                        if parameter and value:
                            parameter_unicode = parameter.decode("utf-8-sig")
                            value_unicode = value.decode("utf-8-sig")

                            unicode_radiator_input[parameter_unicode] = value_unicode

                    article_value = unicode_radiator_input.get(parameter_to_csv_name_dictionary["article"])
                    heat_transfer_value = unicode_radiator_input.get(parameter_to_csv_name_dictionary["heat_transfer"])
                    length_value = unicode_radiator_input.get(parameter_to_csv_name_dictionary["length"])
                    
                    if article_value:
                        radiator_output["article"] = correct_form(article_value, str) 
                    if heat_transfer_value:
                        radiator_output["heat_transfer"] = correct_form(heat_transfer_value, float, True)
                    if length_value:
                        radiator_output["length"] = correct_form(length_value, float, True)

                    if None not in radiator_output.values():
                        catalog_loader_result["radiator_catalog"].append(radiator_output)
                    else:
                        problematic_radiators.append(radiator_output)

                if len(catalog_loader_result["radiator_catalog"]) == 0 or radiators_input_count == 0:
                    catalog_loader_result["outcome"] = "CATALOG_LOAD_FAILED"
                    catalog_loader_result["issues"].append(Issue(
                        IssueCode.ALL_CATALOG_LINES_CONSIDERED_INCORRECT,
                        Stage.CATALOG_LOAD,
                        Severity.ERROR,
                    ))
                elif len(catalog_loader_result["radiator_catalog"]) == radiators_input_count:
                    catalog_loader_result["outcome"] = "CATALOG_LOAD_SUCCESS"
                else:
                    catalog_loader_result["outcome"] = "CATALOG_LOAD_SUCCESS"
                    catalog_loader_result["issues"].append(Issue(
                        IssueCode.SOME_CATALOG_LINES_INCORRECT,
                        Stage.CATALOG_LOAD,
                        Severity.WARNING,
                        IssueContext(radiators_load_success_pct=len(catalog_loader_result["radiator_catalog"])/float(radiators_input_count)*100)
                    ))

        except Exception as error:
            catalog_loader_result["outcome"] = "CATALOG_LOAD_FAILED"
            catalog_loader_result["issues"].append(Issue(
                IssueCode.UNKNOWN_ERROR_WHILE_CATALOG_LOAD,
                Stage.CATALOG_LOAD,
                Severity.ERROR,
                IssueContext(unknown_error=error)
            ))
            return catalog_loader_result
    else:
        catalog_loader_result["outcome"] = "CATALOG_LOAD_FAILED"
        catalog_loader_result["issues"].append(Issue(
            IssueCode.CATALOG_FILE_MISSING,
            Stage.CATALOG_LOAD,
            Severity.ERROR,
        ))
    return catalog_loader_result