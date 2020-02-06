from Stock import Stock, Stockchain, logger1
import time
import datetime
import os
import re

def update_stock(stock):
    if stock.open_val == "0.000" or not stock.is_stock:
        return 0
    stockchain = Stockchain(stock.stock_number)
    stockchain.add_new_data(stock)
    return stockchain

def update_other(temp_stock_chain, time):
    temp_stock = temp_stock_chain
    current_data = temp_stock.get_from_sql(filters={"time": time})
    if current_data is None:
        print "init stock fail, could not get stock from sql"
        return
    i = current_data[0][0]
    EMA12 = temp_stock.EMA(12, current_data[0])
    EMA26 = temp_stock.EMA(26, current_data[0])
    DIF = temp_stock.DIF(EMA12, EMA26)
    temp_stock.update_DIF_EMA(i, EMA12, EMA26, DIF)
    current_data = temp_stock.get_from_sql(filters={"id": i})
    DEA = temp_stock.DEA(current_data[0])
    temp_stock.update_DEA(i, DEA)

def update():   
    sum=0
    for sz in [0,1]:
        for i in range(0,5000):
            stock_number=600000+i
            stock_number=str(stock_number)
            if sz==1:
                stock_number = re.sub(r'^6','0',stock_number)
            print stock_number
            stock = Stock(stock_number)
            stock.get_current_status()
            stock.data_process()
            if stock.open_val == "0.000" or not stock.is_stock:
                continue
            if update_stock(stock)==1:
                sum=sum+1

def alter_type():
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
            stock = Stock(stock_number)
            stock.get_current_status()
            stockchain=Stockchain(stock)
            stockchain.alter_stock_sql("modify", "total_val", "bigint(22)")

hours_15 = 15.5*60*60
hours_3 = 3*60*60
checkstock = Stockchain('601318')
while True:
    now = datetime.datetime.now()
    day = now.strftime('%Y-%m-%d')
    time_struct = now.timetuple()
    hour = time_struct.tm_hour
    weekday = now.weekday()+1
    if weekday == 6 or weekday==7:
        logger1.warning("today {0}, now in weekend".format(day))
        time.sleep(hours_15)
        continue
    stock = Stock('601318')
    now_time = checkstock.get_last_sql_time()
    if now_time == day:
        logger1.warning("sql data has been updated to latest, sleep 15 hours")
        time.sleep(hours_15)
    stock.get_current_status()
    stock.data_process()
    print stock.read_time
    if day != stock.read_time:
        print day
        print "sleep 15 hours"
        logger1.warning("the stock 601318 is not update, maybe today is breaking, wait 15 hours")
        time.sleep(hours_15)
        continue
    elif hour < 15:
        logger1.warning("now is early than 15 clock, wait 3 hours")
        time.sleep(hours_3)
        continue
    else:
        stock.time = stock.read_time
        update()
        time.sleep(hours_15)
        