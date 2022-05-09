import pandas as pd
import numpy as np
import folium
# from IPython.core.display import display,HTML
# display(HTML("<style>.container {width:100% !important; }</style>"))
number_of_customers = 10
number_of_terminals = 2
number_of_locations = number_of_customers + number_of_terminals
number_of_trucks = 3
number_of_compartments = 3
# what is the truck capacity?
Truck_capacity= 67
number_of_products = 4

Product = pd.DataFrame([])
Product["ProductID"] = ["Product"+str(i) for i in range(1,number_of_products+1)]
# display(Product.head())

Customer = pd.DataFrame([])
Customer["CustomerID"] = ["Customer" +str(i) for i in range(1,number_of_customers+1)]
# display(Customer)

Terminal = pd.DataFrame([])
Terminal["TerminalID"]=["Terminal" +str(i) for i in range(1,number_of_terminals+1)]
Terminal.loc[:,"Quantity"]=1000
# display(Terminal.head())

Demand = pd.DataFrame([])
Demand = pd.merge(Customer, Product, how = "cross")
Demand["Quantity"]  = [np.random.randint(1, 10) for i in range(1,number_of_products * number_of_customers+1)]
# display(Demand.head())

# Demand = pd.DataFrame([])
# Demand["CustomerID"] = ["customer"+str(i) for i in range(1,number_of_customers+1)]
# Demand["Quantity"]=[np.random.randint(1,10) for i in range(1, number_of_customers+1)]
# display(Demand.head())

Demand["CustomerID"].unique()

def get_dataframe():
    Location = pd.DataFrame([])
    Location["LocationName"] = np.concatenate([Customer["CustomerID"].values , Terminal["TerminalID"].values])
    Location["Province"]= ["ON","NS","NS","ON","QC","ON","QC","QC","QC","QC","QC","ON"]
    Location["Latitude"] = [43.7633333333333, 45.59360361, 45.15555972, 46.26468861,45.58444444,43.00332083,45.56805556,45.31973056,45.24401083,45.64136722,45.271625,43.78]
    Location["Longitude"] = [-79.70888889,-61.74130417,-64.42916861,-81.76970528,-73.28194444,-79.27030722,-73.45138889,-73.73901361,-74.10858056,-74.32831222,-74.09856111,-79.72]
    Location["PostalCode"] = ["L6T5J8","B0H 1A0","B0P1H0","P5E 1S4","J3G 0C3","L3C6H5","J3L 5X9","J6R 2A3","J6T 6T5","J8H 4H4","J6S 5K9","J3Y 3K7"]
    Location["Type"]= ["Customer" for i in range(0,number_of_customers)] + ["Terminal" for i in range(0,number_of_terminals)] 
    Location["RunOut"] =[20,35,50,22,24,55,78,89,16,29,48,55]
    return Location
# display(Location)

# Location = pd.DataFrame([])
# Location["LocationName"] = []
# Location["Province"]
# Location["Country"]c
# Location["PostalCode"]
# Location["Latitude"]
# Location["Longitude"]
# Location["Type"]

Truck = pd.DataFrame([])
Truck["TruckID"] = ["Truck" +str(i) for i in range(1,number_of_trucks+1)]
Truck["Capacity"]= Truck_capacity
# display(Truck.head())

Compartment = pd.DataFrame([])
Compartment["CompartmentID"] = ["Compartment" +str(i) for i in range(1,number_of_trucks*number_of_compartments+1)]
for i in range(0,number_of_trucks):
    Compartment.loc[3*i:3*(i+1),"TruckID"] ="Truck"+str(i+1)
# shouldn't we have a bigger capacity for the compartment?
#Compartment["Capacity"] = 20
# display(Compartment) #display(Compartment) 
