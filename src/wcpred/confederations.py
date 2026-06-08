"""Team -> confederation lookup.

Not exhaustive over all 211 FIFA members, but covers every World Cup-relevant nation and
most others. Unknown teams fall back to "Other". Extend `_CONFED` as needed.
"""
from __future__ import annotations

_CONFED: dict[str, list[str]] = {
    "UEFA": [
        "Albania", "Andorra", "Armenia", "Austria", "Azerbaijan", "Belarus", "Belgium",
        "Bosnia and Herzegovina", "Bulgaria", "Croatia", "Cyprus", "Czechia",
        "Czech Republic", "Denmark", "England", "Estonia", "Faroe Islands", "Finland",
        "France", "Georgia", "Germany", "Gibraltar", "Greece", "Hungary", "Iceland",
        "Israel", "Italy", "Kazakhstan", "Kosovo", "Latvia", "Liechtenstein", "Lithuania",
        "Luxembourg", "Malta", "Moldova", "Monaco", "Montenegro", "Netherlands",
        "North Macedonia", "Northern Ireland", "Norway", "Poland", "Portugal",
        "Republic of Ireland", "Romania", "Russia", "San Marino", "Scotland", "Serbia",
        "Slovakia", "Slovenia", "Spain", "Sweden", "Switzerland", "Turkey", "Türkiye",
        "Ukraine", "Wales", "Yugoslavia", "Soviet Union", "East Germany", "Serbia and Montenegro",
    ],
    "CONMEBOL": [
        "Argentina", "Bolivia", "Brazil", "Chile", "Colombia", "Ecuador", "Paraguay",
        "Peru", "Uruguay", "Venezuela",
    ],
    "CONCACAF": [
        "Canada", "Costa Rica", "Cuba", "Curaçao", "Curacao", "El Salvador", "Guatemala",
        "Haiti", "Honduras", "Jamaica", "Mexico", "Panama", "Trinidad and Tobago",
        "United States", "USA", "Suriname", "Guadeloupe", "Martinique", "Bermuda",
    ],
    "CAF": [
        "Algeria", "Angola", "Burkina Faso", "Cameroon", "Cape Verde", "Congo",
        "DR Congo", "Ivory Coast", "Côte d'Ivoire", "Egypt", "Equatorial Guinea",
        "Gabon", "Ghana", "Guinea", "Kenya", "Mali", "Mauritania", "Morocco",
        "Mozambique", "Namibia", "Nigeria", "Senegal", "South Africa", "Sudan",
        "Togo", "Tunisia", "Uganda", "Zambia", "Zimbabwe", "Benin", "Madagascar",
        "Comoros", "Gambia",
    ],
    "AFC": [
        "Australia", "Bahrain", "China PR", "China", "India", "Iran", "Iraq", "Japan",
        "Jordan", "Kuwait", "Lebanon", "Malaysia", "North Korea", "Oman", "Palestine",
        "Qatar", "Saudi Arabia", "South Korea", "Korea Republic", "Syria", "Thailand",
        "United Arab Emirates", "Uzbekistan", "Vietnam", "Indonesia", "Tajikistan",
        "Kyrgyzstan", "Turkmenistan", "Hong Kong",
    ],
    "OFC": [
        "New Zealand", "Fiji", "New Caledonia", "Papua New Guinea", "Solomon Islands",
        "Tahiti", "Vanuatu", "Samoa", "Tonga",
    ],
}

# Flatten to team -> confederation.
TEAM_CONFED: dict[str, str] = {
    team: confed for confed, teams in _CONFED.items() for team in teams
}


def confederation(team: str) -> str:
    return TEAM_CONFED.get(team, "Other")
