import configs.maps

form_default = {
    "citizenship_main": "Indien",
    "count_applicants": 2,
    "live_together": "ja",
    "citizenship_partner": "Indien",
    "service_category": "Aufenthaltstitel - verlängern",
    "service": "Studium und Ausbildung",
    "type_residence_permit": "Aufenthaltserlaubnis zum Studium (§ 16b)"
}


def parse_form(form: dict):
    return {
        "code_citizenship": configs.maps.map_citizenship_code[form["citizenship_main"]],
        "count_applicants": str(form["count_applicants"]),
        "live_together": configs.maps.map_live_together[form["live_together"]],
        "code_citizenship_partner": configs.maps.map_partner_citizenship_code[form["citizenship_partner"]],
        "service_category": f"SERVICEWAHL_DE3{configs.maps.map_citizenship_code[form['citizenship_main']]}-0-{configs.maps.map_service_category[form['service_category']]}",
        "service": f"SERVICEWAHL_DE_{configs.maps.map_citizenship_code[form['citizenship_main']]}-0-{configs.maps.map_service_category[form['service_category']]}-{configs.maps.map_service[form['service']]}",
        "type_residence_permit": f"SERVICEWAHL_DE{configs.maps.map_citizenship_code[form['citizenship_main']]}-0-{configs.maps.map_service_category[form['service_category']]}-{configs.maps.map_service[form['service']]}-{configs.maps.map_residence_permit[form['type_residence_permit']]}"
    }


def display_options(field: str):
    match field:
        case "citizenship_main":
            return configs.maps.map_citizenship_code.keys()
        case "count_applicants":
            return [n for n in range(1, 9)]
        case "live_together":
            return ["ja", "nein"]
        case "citizenship_partner":
            return configs.maps.map_partner_citizenship_code.keys()
        case "service_category":
            return configs.maps.map_service_category.keys()
        case "service":
            return configs.maps.map_service.keys()
        case "type_residence_permit":
            return configs.maps.map_residence_permit.keys()
        case _:
            return None
