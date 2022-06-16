# Passmark Database Scraper

This Python library can scrape the Passmark websites in order to fetch various benchmark results. It can sort the benchmark results based on varius critera, such as the score, rank, and the value of the part. It can also search through the listings for a specific search query. Additionally, this uses no external libraries outide of the ones included in Python.  

The websites that this program can scrape are:
 - cpubenchmark.net
 - videocardbenchmark.net
 - harddrivebenchmark.net

## Usage:

To use this, just download scraper.py and put it inside the same directory as your Python program.

Example usage:
```python
from scraper import Scraper

scraper = Scraper("www.videocardbenchmark.net")

#search for a specific term
search_results = scraper.search(query="rtx 3090", limit=10)
#sort the results based on their value
sorted_results = scraper.get_sorted_list(sort_by="value", order="descending", limit=20)

for result in search_results:
    print(result[1], "| ", result[0]["name"])
print("-"*20)
for result in sorted_results:
    print(result[1], "| ", result[0]["name"])
```

## Documentation:

### The Scraper class:

To use it, specifiy the domain that you want to get data from. All the other functions are contained inside this class.

Valid values:
 - `www.cpubenchmark.net` (default)
 - `www.videocardbenchmark.net`
 - `www.harddrivebenchmark.net`

Anything else will raise a ValueError.

Example: 
```python
from scraper import scraper

scraper = scraper = Scraper("www.videocardbenchmark.net")
```

### Getting all items:

You can get all the items in the database using `Scraper.items`. This returns a list containing all the results. 

If you want to refresh the cached results, use `Scraper.scrape()`.

### Searching through the results:

Simply use `Scraper.search(query)`. Optionally, you can use the `limit` argument to limit the number of results returned. This returns a list containing the results of your search. Note that this won't refresh the cached items. You'll have to use `Scraper.scrape()` to refresh it. 

### Sorting the results:

You can sort the items using `Scraper.get_sorted_list(sort_by=critera)`.

Valid search critera:
 - `www.cpubenchmark.net`: `'cat', 'cores', 'cpuCount', 'cpumark', 'date', 'href', 'id', 'logicals', 'name', 'output', 'powerPerf', 'price', 'rank', 'samples', 'socket', 'speed', 'tdp', 'thread', 'threadValue', 'turbo', 'value']`
 - `www.videocardbenchmark.net`:`'bus', 'cat', 'coreClk', 'date', 'g2d', 'g3d', 'href', 'id', 'memClk', 'memSize', 'name', 'output', 'powerPerf', 'price', 'rank', 'samples', 'tdp', 'value']`
 - `www.harddrivebenchmark.net`: `'date', 'diskmark', 'href', 'id', 'name', 'output', 'price', 'rank', 'samples', 'size', 'type', 'value']`

Optional arguments:
 - `order`: can either be "ascending" or "descending"
 - `limit`: an int, limits the amount of results returned
 - `item_type`: forces a specific value type. Valid values are: `['string', 'number', 'bool', 'size', 'speed', 'date']`

This returns a list containing all the results, sorted using the specified critera. This also doesn't refresh the cache. 

### Getting a specific item based on its id:

You can get a specific item using `Scraper.get_item(item_id)`.
