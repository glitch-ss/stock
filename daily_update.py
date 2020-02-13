from Stock import Stock, Stockchain, logger1, logging, formatter
import traceback
import time
import datetime
import os
import re

def update_stock(stock):
    if stock.open_val == "0.000" or not stock.is_stock:
        return 0
    stockchain = Stockchain(stock.stock_number)
    now_time = stockchain.get_last_sql_time()
    if now_time == day:
        logger1.warning("sql data has been updated to latest")
        return stockchain
    stock, last_time = stockchain.calc_other(stock)
    stockchain.add_new_data(stock)
    return stockchain

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
    try:
        log_time = datetime.datetime.now().strftime('%Y-%m')
        handler1 = logging.FileHandler("log/{0}".format(log_time))
        handler1.setLevel(logging.INFO)
        handler1.setFormatter(formatter)
        logger1.addHandler(handler1)
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
        stock.get_current_status()
        stock.data_process()
        print stock.read_time
        if day != stock.read_time:
            logger1.warning("now the day is {0}, and the stock update date is {1}".format(day, stock.read_time))
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
    except Exception, e:
        logging.error(str(traceback.format_exc()))
        