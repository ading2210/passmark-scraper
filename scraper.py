import requests
import time
import re
import datetime

class Scraper:
    def __init__(self, domain="www.cpubenchmark.net"):
        #parse arguments and get a list of items
        if not domain in ["www.videocardbenchmark.net", "www.cpubenchmark.net", "www.harddrivebenchmark.net"]:
            raise ValueError("Invaid domain given.")
        self.domain = domain
        self.url = {
            "www.cpubenchmark.net": "https://www.cpubenchmark.net/CPU_mega_page.html",
            "www.videocardbenchmark.net": "https://www.videocardbenchmark.net/GPU_mega_page.html",
            "www.harddrivebenchmark.net": "https://www.harddrivebenchmark.net/hdd-mega-page.html"
        }[domain]
        self.scrape()
    
    #search through the gpu list
    def search(self, query, limit=None):
        query_split = query.lower().split(" ")

        #get number of matches for each word in the search query
        results = []
        for item in self.items:
            name_split = item["name"].lower().split(" ")
            matches = list(set(name_split)&set(query_split))
            if len(matches) > 0:
                results.append((item, len(matches)))

        #sort to get the most relavent results on top
        results = sorted(results, key=lambda x: x[1], reverse=True)

        if limit != None:
            results = results[:limit]
        return results

    #get a single item based on its id
    def get_item(self, item_id):
        for item in self.items:
            if int(item["id"]) == int(item_id):
                return item
        return None

    #download and cache the data
    def scrape(self):
        session = requests.Session()
        headers = {
            "referrer": self.url,
            "x-requested-with": "XMLHttpRequest",
            "accept": "application/json, text/javascript, */*; q=0.01",
        }
        r1 = session.get(self.url, headers=headers)
        
        url2 = f"https://{self.domain}/data/?_={str(int(time.time()*1000))}"
        r2 = session.get(url2, headers=headers)

        self.items = r2.json()["data"] 
        
        return self.items

    #get every item in the database, sorted by a specific critiera
    #valid values for 
    def get_sorted_list(self, sort_by="rank", order="descending", limit=None, item_type=None):
        results = []

        #define types for the values so that we know how to sort them
        if self.domain == "www.cpubenchmark.net":
            item_types = {
                "cat": "string",
                "cores": "number",
                "cpuCount": "number",
                "cpumark": "number",
                "date": "date",
                "href": "string",
                "id": "number",
                "logicals": "number",
                "name": "string",
                "output": "bool",
                "powerPerf": "number",
                "price": "number",
                "rank": "number",
                "samples": "number",
                "socket": "string",
                "speed": "number",
                "tdp": "number",
                "thread": "number",
                "threadValue": "number",
                "turbo": "number",
                "value": "number"
            }
        elif self.domain == "www.videocardbenchmark.net":
            item_types = {
                "bus": "string",
                "cat": "string",
                "coreClk": "number",
                "date": "date",
                "g2d": "number",
                "g3d": "number",
                "href": "string",
                "id": "number",
                "memClk": "speed",
                "memSize": "size",
                "name": "string",
                "output": "bool",
                "powerPerf": "number",
                "price": "number",
                "rank": "number",
                "samples": "number",
                "tdp": "number",
                "value": "number"
            }
        else:
            item_types = {
                "date": "date",
                "diskmark": "number",
                "href": "string",
                "id": "number",
                "name": "string",
                "output": "bool",
                "price": "number",
                "rank": "number",
                "samples": "number",
                "size": "size",
                "type": "string",
                "value": "number"
            }

        if item_type == None:
            if sort_by in item_types:            
                item_type = item_types[sort_by]
            else:
                item_type = "string"

        #filter the items and assign a number to each one, unless it is a string
        for item in self.items:
            value = item[sort_by]
            if value == "NA":
                continue

            if item_type == "string":
                results.append([item, str(value)])
            elif item_type == "number":
                if type(value) is int or type(value) is float:
                    results.append([item, float(value)])
                else:
                    result = re.sub("[^0123456789\.]", "", value)
                    if len(result) > 0:
                        results.append([item, float(result)])
            elif item_type == "bool":
                results.append([item, int(value)])
            elif item_type == "size":
                number, unit = value.split(" ")[:2]
                number = re.sub("[^0123456789\.]", "", number)
                if len(number) > 0:
                    number = float(number)
                    units = ["kb", "mb", "gb", "tb", "pb"]
                    if unit.lower() in units:
                        number *= 1000**(units.index(unit.lower())+1)
                    results.append([item, int(number)])
            elif item_type == "speed":
                number, unit = value.split(" ")[:2]
                number = re.sub("[^0123456789\.]", "", number)
                if len(number) > 0:
                    number = float(number)
                    units = ["khz", "mhz", "ghz"]
                    if unit.lower() in units:
                        number *= 1000**(units.index(unit.lower())+1)
                    results.append([item, int(number)])
            elif item_type == "date":
                months = ["jan", "feb", "mar", "apr",
                          "may", "jun", "jul", "aug",
                          "sep", "oct", "nov", "dec"]
                month, year = value.split(" ")[:2]
                month_int = months.index(month.lower())+1
                year_int = int(year)
                d = datetime.date(year_int, month_int, 1)
                unix_time = time.mktime(d.timetuple())
                results.append([item, int(unix_time)])

        #sort items
        if order == "descending":
            reverse = True
        else:
            reverse = False
        results.sort(key=lambda x: x[1], reverse=reverse)

        if limit != None:
            results = results[:limit]
        return results
