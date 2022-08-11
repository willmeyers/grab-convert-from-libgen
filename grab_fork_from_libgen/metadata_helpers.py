from bs4 import BeautifulSoup


def fiction_field_value(field: str, soup: BeautifulSoup):
    """
    > Given a field name and a BeautifulSoup object, find the value of the field in the html

    :param field: str - the name of the field we want to scrape
    :type field: str
    :param soup: BeautifulSoup
    :type soup: BeautifulSoup
    """

    # Since the order of elements can change when one is missing, it's not reliable to use css selectors
    # to scrape on fiction html. We search for hard-coded strings in "td" elements instead, and then find it's
    # next relevant sibling, which is usually the value of a given field.

    try:
        field_value: str = soup.find("td", string=field).next_sibling.next_sibling.text.strip()
        if field_value == "":
            return None
        return field_value
    except AttributeError:
        return None


def scitech_field_value(field: str, soup: BeautifulSoup):
    """
    > Finds a relevant field value based on the field name. Must check libgen scitech html for reference.
    :param field: str - The field name
    :type field: str
    :param soup: BeautifulSoup = BeautifulSoup(html, "html.parser")
    :type soup: BeautifulSoup
    :return: A list of dictionaries.
    """

    # Unlike in fiction scraping, this can also be done via css selectors.
    # I prefer this aproach because no matter what order the fields are in the html,
    # we always get what we are searching for, or nothing.

    try:
        # Let me show you, how deep the rabbit hole goes.
        # We usually go: field element > it's parent > the parent's parent > the next sibling >
        # the first children > the children of the first children. > it's text.
        # And there's also some edge cases...
        # Libgen is also using html elements (font) to style elements, so we search for font elements... yeah.
        if soup.find("font", string=field).parent.parent.name != "td":
            field_base = soup.find("font", string=field).parent
        else:
            field_base = soup.find("font", string=field).parent.parent

        field_value = field_base.next_sibling.text.strip()
        if field_value == "":
            return None
        return field_value
    except AttributeError:
        return None
