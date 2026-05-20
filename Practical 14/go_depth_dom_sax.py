from datetime import datetime
from xml.dom import minidom
import os
import xml.sax


XML_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "go_obo.xml")
NAMESPACES = ["molecular_function", "biological_process", "cellular_component"]


def make_empty_results():
    results = {}

    for namespace in NAMESPACES:
        results[namespace] = ["", "", -1]

    return results


def get_text(parent, tag_name):
    elements = parent.getElementsByTagName(tag_name)

    if len(elements) == 0:
        return ""

    if elements[0].firstChild is None:
        return ""

    return elements[0].firstChild.data.strip()


def update_best_result(results, namespace, go_id, go_name, is_a_count):
    if namespace in results:
        if is_a_count > results[namespace][2]:
            results[namespace] = [go_id, go_name, is_a_count]


def dom_method():
    results = make_empty_results()
    doc = minidom.parse(XML_FILE)

    for term in doc.getElementsByTagName("term"):
        go_id = get_text(term, "id")
        go_name = get_text(term, "name")
        namespace = get_text(term, "namespace")
        is_a_count = len(term.getElementsByTagName("is_a"))

        update_best_result(results, namespace, go_id, go_name, is_a_count)

    doc.unlink()
    return results


class GoHandler(xml.sax.ContentHandler):
    def __init__(self):
        xml.sax.ContentHandler.__init__(self)
        self.results = make_empty_results()
        self.current_tag = ""
        self.in_term = False
        self.go_id = ""
        self.go_name = ""
        self.namespace = ""
        self.is_a_count = 0

    def startElement(self, name, attrs):
        self.current_tag = name

        if name == "term":
            self.in_term = True
            self.go_id = ""
            self.go_name = ""
            self.namespace = ""
            self.is_a_count = 0

        if self.in_term and name == "is_a":
            self.is_a_count = self.is_a_count + 1

    def characters(self, content):
        if self.in_term and self.current_tag == "id":
            self.go_id = self.go_id + content
        elif self.in_term and self.current_tag == "name":
            self.go_name = self.go_name + content
        elif self.in_term and self.current_tag == "namespace":
            self.namespace = self.namespace + content

    def endElement(self, name):
        if name == "term":
            update_best_result(
                self.results,
                self.namespace.strip(),
                self.go_id.strip(),
                self.go_name.strip(),
                self.is_a_count,
            )
            self.in_term = False

        self.current_tag = ""


def sax_method():
    handler = GoHandler()
    xml.sax.parse(XML_FILE, handler)
    return handler.results


def print_answer(title, results, time_taken):
    print(title)
    print("-" * len(title))

    for namespace in NAMESPACES:
        result = results[namespace]
        print("Namespace:", namespace)
        print("GO ID:", result[0])
        print("Name:", result[1])
        print("Number of is_a elements:", result[2])
        print()

    print("Time taken:", time_taken, "seconds")
    print()


def main():
    start_time = datetime.now()
    dom_results = dom_method()
    dom_time = (datetime.now() - start_time).total_seconds()

    start_time = datetime.now()
    sax_results = sax_method()
    sax_time = (datetime.now() - start_time).total_seconds()

    print_answer("DOM results", dom_results, dom_time)
    print_answer("SAX results", sax_results, sax_time)

    if dom_time < sax_time:
        print("DOM was quicker in this run.")
    else:
        print("SAX was quicker in this run.")


if __name__ == "__main__":
    main()
