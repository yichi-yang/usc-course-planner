#!/usr/bin/python3
# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
from section import Section


def load_class(class_name, base_url):
    print(base_url + class_name + "/")
    response = requests.get(base_url + class_name + "/")
    if response:
        soup = BeautifulSoup(response.text, "html.parser")
        # print(soup.prettify())
        sections = soup.select("tr[data-section-id]")
        this_class = {}
        for section in sections:
            session_id = section.find("td", class_="section").get_text()[:5]
            session_type = section.find("td", class_="type").get_text()
            time = section.find("td", class_="time").get_text()
            days = section.find("td", class_="days").get_text()
            registered_tag = section.find("td", class_="registered")
            registered = registered_tag.get_text()
            closed = not (registered_tag.find("div", class_="closed") is None)
            instructor = section.find("td", class_="instructor").get_text()
            location = section.find("td", class_="location").get_text()
            current_section = Section(class_name, session_id, session_type, time,
                                      days, registered, closed, instructor, location)
            if session_type not in this_class:
                this_class[session_type] = []
            this_class[session_type].append(current_section)
        return this_class
    else:
        return None


if __name__ == '__main__':
    cs201 = load_class(
        "csci-201", "https://classes.usc.edu/term-20193/course/")
    print(cs201)
