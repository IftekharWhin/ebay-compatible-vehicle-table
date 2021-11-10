import time
import json
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import os
import re

try:
    from seleniumwire import webdriver
    from webdriver_manager.chrome import ChromeDriverManager
    import requests

except ImportError:
    os.system('python3 -m pip install selenium-wire')
    os.system('python3 -m pip install webdriver-manager')
    os.system('python3 -m pip install requests')

import requests
from seleniumwire import webdriver
from webdriver_manager.chrome import ChromeDriverManager

ebay_demo_link = 'https://www.ebay.com/itm/353672691115'
class ebay_bot():
    def __init__(self):
        self.collect_headers()

    def collect_headers(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(),options=chrome_options)

        driver.get(ebay_demo_link)
        time.sleep(2)

        self.header = None
        for request in driver.requests:
            authorization = request.headers.get('Authorization')
            session = request.headers.get('X-EBAY-C-CORRELATION-SESSION')
            if authorization != None and session != None:
                self.header = dict(request.headers)

                break
        driver.close()

    def request_data(self, item_no):
        r = requests.get(f'https://api.ebay.com/parts_compatibility/v1/compatible_products/listing/{item_no}?fieldgroups=full&limit=10000', headers=self.header)
        scraped_data = self.scrape_data_simplification(r.content)
        return scraped_data

    def scrape_data_simplification(self, input_data):
        data = json.loads(input_data)
        scraped_data = []

        all_products = data['compatibleProducts']['members']
        for each_procduct in all_products:
            product_properties = each_procduct['productProperties']
            make = product_properties['Make']
            year = product_properties['Year']
            model = product_properties['Model']
            trim = product_properties['Trim']
            engine = product_properties['Engine']
            comments = product_properties['FitmentComments']
            submodel = each_procduct['searchIndexedProperties']['Submodel']
            engine_litre= each_procduct['searchIndexedProperties']['Engine - Liter_Display']
            scraped_data.append((make,model,year,trim,submodel,engine,comments,engine_litre))

        return scraped_data

print("Starting the Bot. Please, Wait.")
ebay = ebay_bot()

global scraped_data
global item_no
def start_button():
    global scraped_data
    global item_no
    link = link_entry.get()
    item_no = re.search("itm/\d+", link).group()
    item_no = re.search("\d+", item_no).group()
    print("The bot is scraping the data. Please, hold on.")
    scraped_data = ebay.request_data(item_no)

    for row in scraped_table.get_children():
        scraped_table.delete(row)

    iid_id=1
    for s in scraped_data:
        vals = tuple([iid_id])+s
        scraped_table.insert(parent='',index='end',iid=iid_id,values=vals)
        iid_id += 1

    link_entry.delete(0,END)
    messagebox.showinfo('DONE', f'Scraped {len(scraped_data)} Items.')
    print(f"Scraping done for {item_no}")

    s_Export_button = Button(scraped_data_frame, text="Export", command=scrape_export,bg='gray',width=20)
    s_Export_button.grid(row=0, column=1,padx=10)

def scrape_export():
    global scraped_data
    global item_no
    file = open(f"{item_no}_scraped.csv", "w+")
    file.write("Make, Model, Year, Trim, Submodel, Engine, Fitment Comments, Engine Litre-Display\n")
    for data in scraped_data:
        file.write(",".join(data))
        file.write("\n")
    file.close()
    messagebox.showinfo("Export Done",f"Exported with filename: {item_no}_scraped.csv")

root= Tk()
root.title("Ebay Vehicle Data Scraping Bot")
iid_id = 0

link_frame = LabelFrame(root, text='',padx=10,pady=10)
link_frame.grid(row=0, column=0)

enter_link_label = Label(link_frame, text="Enter The ebay link:")
link_entry = Entry(link_frame, width=70)
start_button = Button(link_frame, text="Start Scraping",command=start_button, bg="Light Green")

enter_link_label.grid(row=0,column=0,padx=10,pady=10)
link_entry.grid(row=0, column=1,padx=10,pady=10)
start_button.grid(row=0, column=2,padx=10,pady=10)

scraped_data_frame= LabelFrame(root, text='Scraped Data', padx=10,pady=10)
scraped_data_frame.grid(row=1, column=0)

scraped_table = ttk.Treeview(scraped_data_frame)
scraped_table.grid(row=0, column=0)
scraped_table['columns']= ("Index","Make", "Model", "Year","trim",'sm','engine','comments','el')

scraped_table.column('#0',width=0,stretch=0)
scraped_table.column('Index',width=40)
scraped_table.column("Make", anchor=W)
scraped_table.column("Model", anchor=CENTER,width=100)
scraped_table.column("Year", anchor=CENTER,width=50)
scraped_table.column("trim", anchor=CENTER,width=120)
scraped_table.column("sm", anchor=CENTER,width=100)
scraped_table.column("engine", anchor=CENTER,width=100)
scraped_table.column("comments", anchor=CENTER,width=100)
scraped_table.column("el", anchor=CENTER,width=100)



scraped_table.heading("#0", text='')
scraped_table.heading("Index", text='Serial')
scraped_table.heading("Make", text="Make", anchor=CENTER)
scraped_table.heading("Model", text="Model",anchor=CENTER)
scraped_table.heading("Year", text="Year", anchor=CENTER)
scraped_table.heading("trim", text="Trim", anchor=CENTER)
scraped_table.heading("sm", text="Sub-Model", anchor=CENTER)
scraped_table.heading("engine", text="Engine", anchor=CENTER)
scraped_table.heading("comments", text="Fitment Comments", anchor=CENTER)
scraped_table.heading("el", text="Engine Litre Capacity", anchor=CENTER)


root.mainloop()

