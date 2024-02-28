"""
We define navigation objects for each context
"""

class Nav:
    name : str 
    url : str 
    icon : str 


    def __init__(self, name : str, url : str, icon : str) -> None:
        self.name = name 
        self.url = url 
        self.icon = icon



USER_NAV = [
    Nav("Home", "/home", "fa-solid fa-home"),
    Nav("Clubs", "/clubs", "fa-sold fa-volleyball"),
    Nav("Events", "/events", "fa-sold fa-calendar-days")
]