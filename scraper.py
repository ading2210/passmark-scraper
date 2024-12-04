import requests
import time
import re
import datetime
import csv

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

        #Define types for the values so they can be sorted correctly
        if self.domain == "www.cpubenchmark.net":
            self.item_types = {
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
            self.item_types = {
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
            self.item_types = {
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

        #sort to get the most relevant results on top
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
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",#Header to mimic a browser request
            "Accept-Language": "en-US,en;q=0.9",
            "referrer": self.url,
            "x-requested-with": "XMLHttpRequest",
            "accept": "application/json, text/javascript, */*; q=0.01",
        }
        r1 = session.get(self.url, headers=headers)

        url2 = f"https://{self.domain}/data/?_={str(int(time.time()*1000))}"
        r2 = session.get(url2, headers=headers)

        #Diagnostic Prints
        try:
            self.items = r2.json()["data"]
            print(f"Scraped {len(self.items)} items.")
        except Exception as e:
            print("Error during scraping:", e)
            self.items = []  # Ensure items are an empty list if scraping fails 
        
        return self.items

    #get every item in the database, sorted by specific criteria
    def get_sorted_list(self, sort_by="rank", order="descending", limit=None, item_type=None):
        results = []

        if item_type == None:
            if sort_by in self.item_types:            
                item_type = self.item_types[sort_by]
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
                    result = re.sub(r"[^0123456789\.]", "", value)#Raw String Required to not cause Escape Sequence
                    if len(result) > 0:
                        results.append([item, float(result)])
            elif item_type == "bool":
                results.append([item, int(value)])
            elif item_type == "size":
                number, unit = value.split(" ")[:2]
                number = re.sub(r"[^0123456789\.]", "", number) #Raw String Required to not cause Escape Sequence
                if len(number) > 0:
                    number = float(number)
                    units = ["kb", "mb", "gb", "tb", "pb"]
                    if unit.lower() in units:
                        number *= 1000**(units.index(unit.lower())+1)
                    results.append([item, int(number)])
            elif item_type == "speed":
                number, unit = value.split(" ")[:2]
                number = re.sub(r"[^0123456789\.]", "", number)#Raw String Required to not cause Escape Sequence
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
    
    def filter_and_sort(
        self, 
        filters=None, 
        sort_by=None, 
        order=None, 
        limit=None, 
        exclude_na=None  # New parameter to handle exclusions
    ):
        """
        Filters and optionally sorts items based on dynamic filters.
        
        :param filters: A dictionary of filters where keys are item fields and values are filter values.
                        Example: {"name": "Xeon", "socket": "LGA 2011"}
        :param sort_by: The field to sort by (default is None, meaning no sorting).
        :param order: Sort order, "ascending" or "descending" (default is None, meaning no sorting).
        :param limit: Number of results to return (default is None, meaning all).
        :param exclude_na: A list of fields where items with "N/A" should be excluded.
        :return: A list of filtered and optionally sorted items.
        """
        # Initialize filtered items as all items
        filtered_items = self.items[:]

        numeric_fields = [field for field, field_type in self.item_types.items() if field_type in ["numbers"]]

        # Exclude items with "N/A" in specific fields
        if exclude_na:
            for field in exclude_na:
                filtered_items = [
                    item for item in filtered_items if str(item.get(field, "")).upper() != "NA"
                ]



        # Apply filters if provided
        if filters:
            for field, value in filters.items():
                # If the field is numeric, treat it as such
                if field in numeric_fields:
                    try:
                        value = float(value)  # Convert the filter value to float
                        filtered_items = [
                            item for item in filtered_items if self.safe_compare(item.get(field, "NA"), value)
                        ]
                    except ValueError:
                        print("Failed to Convert")  # If the value cannot be converted to float, ignore the filter
                else:
                    # For string or other non-numeric fields, perform substring match
                    filtered_items = [
                        item for item in filtered_items if value.lower() in str(item.get(field, "")).lower()
                    ]

        # Limit the number of results if a limit is specified
        if limit is not None:
            filtered_items = filtered_items[:limit]

        # If sort_by is provided, sort the filtered items
        if sort_by and sort_by in self.items[0]:
            print("Sorting")
            filtered_items = sorted(
                filtered_items, 
                key=lambda item: self.safe_sort_key(item, sort_by),
                reverse=(order == "descending")
            )        

        return filtered_items 
    
    def safe_sort_key(self, item, sort_by):
        """
        Safely handles sorting for both numeric and string fields.
        """
        value = item.get(sort_by)
        if isinstance(value, (int, float)):
            return value
        
        try:
            return float(value)
        except (ValueError, TypeError):
            pass


        if isinstance(value, str):
            if value.strip().lower() in ["na", "none","n/a", ""]:
                return(float('inf'))
            return value.lower()
        else:
            return float('inf')  # If the value is not numeric or string, place it at the end.    

        


    def safe_compare(self, field_value, filter_value):
        #Compares field values to filter values

        if isinstance(field_value, (int, float)):
            return field_value == filter_value
        
        elif isinstance(field_value, str):
            return filter_value.lower() in field_value.lower()
        
        return False

    def export_to_csv(self, data, filename="output.csv", fields=None):
        """
        Exports a list of dictionaries to a CSV file, with the option to limit columns.
        
        :param data: List of dictionaries containing the data to export.
        :param filename: The name of the CSV file to save.
        :param fields: List of field names to include in the CSV. If None, all fields are included.
        """
        if not data:
            print("No data to export.")
            return
        
        # Use specified fields or default to all keys from the first item
        if fields:
            # Ensure fields exist in the data
            headers = [field for field in fields if field in data[0]]
        else:
            headers = data[0].keys()

        try:
            with open(filename, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=headers)
                
                # Write headers
                writer.writeheader()
                
                # Write rows, only including the specified fields
                for row in data:
                    filtered_row = {key: row.get(key) for key in headers}
                    writer.writerow(filtered_row)

                print(f"Data successfully exported to {filename}")
        except Exception as e:
            print(f"Failed to export data to CSV: {e}")
