#!/usr/bin/python3
# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
from section import Section
from class_tree_node import ClassTreeNode


def load_class(url, class_name):  
    try:
        response = requests.get(url)
    except requests.exceptions.ConnectionError:
        return None
    if response:
        soup = BeautifulSoup(response.text, "html.parser")
        sections = soup.select("tr[data-section-id]")
        this_class = {}
        for section in sections:
            session_id = section.find("td", class_="section").get_text()
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
        
        if not this_class:
            return None
        
        class_tree_node = ClassTreeNode(class_name, None)
        for key, val in this_class.items():
            component_node = ClassTreeNode(key, class_tree_node)
            component_node.data = [ClassTreeNode(
                section.section_id, component_node, section) for section in val]
            class_tree_node.data.append(component_node)
        return class_tree_node
    else:
        return None


if __name__ == '__main__':
    cs201 = load_class(
        "csci-201", "https://classes.usc.edu/term-20193/course/")
    print(cs201)
