import json
import pprint

from web_scraper import Scraper


subjects = {
    "Computer Science": "CS",
    "Politic": "POL",
    "Economic": "ECO",
    "Physics": "PHY",
    "History": "HIS",
    "Visual": "VA",
    "Chemisty": "CHM",
    "Writing": "CW",
    "Math": "MAT",
    "Philosoph": "PHI",
    "Media Studies": "MS",
    "Biology": "BIO",
    "International Relation": "IR",
    "Sociology": "SOA",
    "Entrepreneur": "ENT",
    "Environment": "ES",
    "Psych": "PSY",
    "English": "ENG",
    "Performing": "PA"
}


def clean_html_artifacts(string):
    artifacts = [
        "\\t",
        "\\n",
        "<br> ",
        "<br>",
        "\\xc2",
        "\\xa0",
        "\\xc3",
        "\\xa9",
        "\\xe2",
        "\\x80",
        "\\x99",
    ]
    for element in artifacts:
        string = string.replace(element, "")
    string = string.replace(",  ", ", ").replace("\\'", "'").strip(".").strip()
    return string


def string_between(string, start, stop):
    return clean_html_artifacts((string.split(start)[1]).split(stop)[0])


def grab_html_table(scraper, url):
    html_response = scraper.scrape(url)
    html_content = str(html_response.content)
    html_table = string_between(
        html_content,
        '<div class="ashoka-wraper" id="faculty_data"',
        '<i class="fa fa-arrow',
    )
    return html_table


def get_raw_data(scraper, base_url, filter_url):
    html_tables = []
    for page_index in range(1, 22):
        page_url = base_url + str(page_index) + filter_url
        html_table = grab_html_table(scraper, page_url)
        html_tables.append(html_table)
    return html_tables


def process_faculty_html(html_tables):
    prof_objects = []
    for html_table in html_tables:
        prof_html_entries = html_table.split(
            'class="col-xl-3 col-lg-4 col-md-6 col-12 d-flex">'
        )[1:]
        for prof_html_entry in prof_html_entries:
            prof_object = {}
            prof_object["link"] = string_between(
                prof_html_entry,
                'faculty_card_item_inner"><a href="',
                '"><div class="card_profile"',
            )
            prof_object["image"] = string_between(
                prof_html_entry, '<img src="', '" alt="" />'
            )
            prof_object["name"] = string_between(
                prof_html_entry, '<div class="card_info"><h4>', "</h4><p>"
            )
            prof_object["position"] = string_between(
                prof_html_entry, "</h4><p>", "</p><small>"
            )
            prof_object["qualification"] = string_between(
                prof_html_entry, "</p><small>", "</small>"
            )
            if "mailto:" in prof_html_entry:
                prof_object["email"] = string_between(
                    prof_html_entry,
                    '</small><a href="mailto:',
                    '"><img src="https://www.ashoka.edu.in/wp-content/themes/ashoka/images/mail-icon.png',
                )
            for department in subjects.keys():
                if department in prof_object["position"]:
                    prof_object["department"] = subjects[department]
                    break
            prof_objects.append(prof_object)

    return prof_objects


if __name__ == "__main__":
    scraper_object = Scraper()
    base_link = "https://www.ashoka.edu.in/roles/faculty/page/"
    additional_link = "/?yearby=all"

    html_strings = get_raw_data(scraper_object, base_link, additional_link)
    professors = process_faculty_html(html_strings)
    pprint.pprint(professors)
    with open("temp.json", "w") as file:
        json.dump({"professors": professors}, file)