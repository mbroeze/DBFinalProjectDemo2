import time

from demo.D00_init_server_setup import TOR_ROUTER, MON_ROUTER, WIN_ROUTER, \
    ON_REPLSET, ON_REPL_MON
from demo.simple_data import insert_sample_data, clear_data, \
    query_from_windsor, query_from_cornwall, print_demo_title

"""
Demo notes:
Data is simplified for the purposes of demonstration
- we load sample data from two locations and two times
    - OTTAWA/TORONTO
    - TODAY/YESTERDAY
- the data is loaded using the Python REST API
- the queries find the most recent data from the nearest weather station
    - based on timestamp/geolocation fields
    - we add location/dateTime for readability 
        - these fields have different values in the actual data
- we use the Python REST API to search from the latitude/longitude 
    - CORNWALL/WINDSOR
- expect that 
    - querying from WINDSOR returns TORONTO data
    - querying from CORNWALL returns OTTAWA data
"""


# 1. Insert/query data with all servers running
"""
Demo notes
- this is to verify the querying works as expected (see notes at top)
"""

print_demo_title(1, "get the weather")
insert_sample_data(detailed=True)

query_from_windsor()
query_from_cornwall()

clear_data()

# 2. Bringing down routers
"""
Demo notes:
- we bring two routers offline and verify the REST API still works
- then bring down the router that was online, bring up one of the offline 
routers, and verify the REST API still works
"""

print_demo_title(2, "bringing down routers")

print("Bringing Toronto and Montreal routers offline")
TOR_ROUTER.shutdown()
MON_ROUTER.shutdown()
while TOR_ROUTER.healthy() or MON_ROUTER.healthy():
    time.sleep(2)
print("  Toronto and Montreal routers offline")
input("Press enter to continue")

insert_sample_data(detailed=True)

query_from_windsor()

print("Bringing Winnipeg router offline and Montreal router online")
WIN_ROUTER.shutdown()
MON_ROUTER.startup()
while WIN_ROUTER.healthy() or not MON_ROUTER.healthy():
    time.sleep(2)
print("  Winnipeg router offline and Montreal router online")
input("Press enter to continue")

query_from_cornwall()

print("Bringing routers online")
TOR_ROUTER.startup()
WIN_ROUTER.startup()
while not TOR_ROUTER.healthy() or not WIN_ROUTER.healthy():
    time.sleep(2)
print("  Routers online")

clear_data()

# 3. Bringing down data servers

"""
Demo Notes:
- bring down the primary data server
    - confirm writes still work
- bring down another data server
    - confirm reads still work

Note: Bringing down config servers is the same (replica set), so we won't bother
"""
print_demo_title(3, "bringing down data servers")

print(f"Bringing down primary data server "
      f"{ON_REPLSET.pref_primary.container_name}")
ON_REPLSET.pref_primary.shutdown()
while ON_REPLSET.pref_primary.healthy():
    time.sleep(1)
print("  Data server is down")
input("Press enter to continue")

insert_sample_data()

print("Pausing for ")
time.sleep(4)

print(f"Bringing down Montreal data server")
ON_REPL_MON.shutdown()
while ON_REPL_MON.healthy():
    time.sleep(1)
print("  Brought down Montreal data server")

query_from_cornwall()
query_from_windsor()

print("Bringing up Montreal data server for writes")
ON_REPL_MON.startup()
while not ON_REPL_MON.healthy():
    time.sleep(1)
print("  Montreal data server is up")
input("Press enter to continue")
clear_data()
