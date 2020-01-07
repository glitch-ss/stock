from Stock import *

def add_history():
    for sz in [0,1]:
        for i in range(0,5000):
            stock_number=600000+i
            stock_number=str(stock_number)
            if sz==1:
                stock_number = re.sub(r'^6','0',stock_number)
                file_name="export\SZ#" + stock_number + ".txt"
            else:
                file_name="export\SH#" + stock_number + ".txt"
            print stock_number
            if not os.path.exists(file_name):
                continue
            init_stock(stock_number)

def init_stock(number):
    temp_stock = Stockchain(number)
    temp_stock.get_from_txt()
    count = temp_stock.get_data_count()
    print "stock day count is {0}".format(count)
    for i in range(2, count+1):
        current_data = temp_stock.get_from_sql(filters={"id": i})
        if current_data is None:
            print "init stock fail, could not get stock from sql"
            return
        EMA12 = temp_stock.EMA(12, current_data[0])
        EMA26 = temp_stock.EMA(26, current_data[0])
        DIF = temp_stock.DIF(EMA12, EMA26)
        temp_stock.update_DIF_EMA(i, EMA12, EMA26, DIF)
        current_data = temp_stock.get_from_sql(filters={"id": i})
        DEA = temp_stock.DEA(current_data[0])
        temp_stock.update_DEA(i, DEA)
    temp_stock.close_sql()

add_history()
