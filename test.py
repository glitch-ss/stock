from Stock import *
import os
def add_history():
    for sz in [0,1]:
        for i in range(0,5000):
            stock_number=600000+i
            stock_number=str(stock_number)
            if sz==1:
                stock_number = re.sub(r'^6','0',stock_number)
                file_name=os.path.join("export","SZ#" + stock_number + ".txt")
            else:
                file_name=os.path.join("export","SH#" + stock_number + ".txt")
            print stock_number
            if not os.path.exists(file_name):
                continue
            init_stock(stock_number)

def init_stock(number):
    temp_stock = Stockchain(number)
    temp_stock.get_from_txt()
    count = temp_stock.get_data_count()
    print "stock day count is {0}".format(count)

add_history()
