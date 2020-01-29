# -*- encoding:utf-8 -*-
import datetime
import urllib2
import socks
import chardet
import pickle
import re
import os
import requests
import logging
from mysql import connector
'''
proxy_srv='cn-proxy.jp.oracle.com'
proxy_port=80 
socks.setdefaultproxy(socks.PROXY_TYPE_HTTP,proxy_srv,proxy_port)
socks.wrapmodule(urllib2)
'''
from __builtin__ import int

logging.basicConfig(level=logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
logger1 = logging.getLogger(__name__)
handler1 = logging.FileHandler("log")
handler1.setLevel(logging.INFO)
handler1.setFormatter(formatter)
logger1.addHandler(handler1)

class Stock():
    def __init__(self, stock_number,time=None):
        print time
        if time == None:
            self.time = datetime.datetime.now().strftime('%Y-%m-%d')
        else:
            self.time = time
        self.week_day = datetime.datetime.strptime(self.time, "%Y-%m-%d").weekday()+1
        self.current_val = 0.0
        self.high_val = 0.0
        self.low_val = 0.0
        self.open_val = 0.0
        self.close_val = 0.0
        self.stock_number = str(stock_number)
        self.day_amount = 0.0
        self.data=[]
        self.is_stock=True
        self.current_total_val = 0.0
        if self.stock_number.startswith('6'):
            self.detailurl='http://hq.sinajs.cn/list=sh' + str(self.stock_number)
            self.url='http://hq.sinajs.cn/list=s_sh' + str(self.stock_number)
        elif self.stock_number.startswith('0'):
            self.detailurl='http://hq.sinajs.cn/list=sz' + str(self.stock_number)
            self.url='http://hq.sinajs.cn/list=s_sz' + str(self.stock_number) 
        
    def change_data(self, stock_dict):
        if isinstance(stock_dict, dict):
            self. current_val = stock_dict['close']
            self.high_val = stock_dict['high']
            self.low_val = stock_dict['low']
            self.close_val = stock_dict['close']
            self.open_val = stock_dict['open']
            self.day_amount = stock_dict['amount']
            time=stock_dict['day'].split('-')
            self.time = datetime.date(int(time[0]),int(time[1]),int(time[2]))
    
    def get_current_status(self):
        temp = requests.get(self.detailurl)
        temp_data = temp.content.decode('GB18030').split('=')[1]
        for data in temp_data.split(','):
            self.data.append(data.replace('"',''))
        if len(self.data)<2:
            self.is_stock=False

    def supplement(self,time):
        status = 0
        if self.stock_number.startswith('0'):
             site = "http://data.gtimg.cn/flashdata/hushen/latest/daily/sz"+ self.stock_number +".js?maxage=43201&visitDstTime=1"
        else:
            site = "http://data.gtimg.cn/flashdata/hushen/latest/daily/sh"+ self.stock_number +".js?maxage=43201&visitDstTime=1"
        
        try:
            temp = self.opener.open(site)
            temp_data = temp.read()
        except:
            return False
        for data in temp_data.split('\n'):
            if time in data and 'start' not in data:
                status = 1
                items = data.split(' ')
                self.open_val = items[1]
                self.close_val = items[2]
                self.high_val = items[3]
                self.low_val = items[4]
                self.current_val=stock.close_val
                self.current_total_amount = items[5].replace('\\n\\','')
        if status == 0:
            return False
        return True
        
        
    def data_process(self):
        if not self.is_stock:
            return
        self.name = self.data[0]
        self.open_val = self.data[1]
        self.yesterday_val = self.data[2]
        self.current_val = self.data[3]
        self.high_val = self.data[4]
        self.low_val = self.data[5]
        self.current_total_amount = self.data[8]
        self.current_total_val = self.data[9]
        self.buy1amount = self.data[10]
        self.buy1 = self.data[11]
        self.buy2amount = self.data[12]
        self.buy2 = self.data[13]
        self.buy3amount = self.data[14]
        self.buy3 = self.data[15]
        self.buy4amount = self.data[16]
        self.buy4 = self.data[17]
        self.buy5amount = self.data[18]
        self.buy6 = self.data[19]
        self.sell1amount = self.data[20]
        self.sell1 = self.data[21]
        self.sell2amount = self.data[22]
        self.sell2 = self.data[23]
        self.sell3amount = self.data[24]
        self.sell3 = self.data[25]
        self.sell4amount = self.data[26]
        self.sell4 = self.data[27]
        self.sell5amount = self.data[28]
        self.sell5 = self.data[29]
        self.read_time = self.data[30]

class Stockchain():
    def __init__(self, stock_number):
        self.stock_number = stock_number
        self.database = 'stock'
        self.conn = connector.connect(host='localhost',user='root',passwd='atobefuji', port=3306, db=self.database)
        self.cursor = self.conn.cursor();
        query_cmd = "select table_name from information_schema.tables where table_name='{0}' and table_schema='{1}';".format(self.stock_number, self.database)
        self.cursor.execute(query_cmd)
        result = self.cursor.fetchall()
        if len(result) == 0:
            print "create the stock table"
            create_cmd = "create table `{0}` ".format(self.stock_number) + \
                         "(id int auto_increment, time timestamp, open_val float(5,3), close_val float(5,3), high_val float(5,3), low_val float(5,3), total_val bigint(22), total_amount int(20), week_day tinyint, EMA12 float(5,3) default 0, EMA26 float(5,3) default 0, DIF float(5,3) default 0, DEA float(5,3) default 0, primary key (id));"
            print create_cmd
            try:
                self.cursor.execute(create_cmd)
                self.conn.commit()
            except Exception, e:
                print e
                print "fail to create the stock table {0}".foramt(self.stock_number)
        else:
            print "table exists"

    def get_data_count(self):
        try:
            self.cursor.execute('select max(id) from `{0}`'.format(self.stock_number))
            count = self.cursor.fetchall()
        except Exception, e:
            print e
            print 'get data count fail'
            return 0
        if len(count) == 0:
            return 0
        return count[0][0]

    def get_from_sql(self, key_word='*', filters=None):
        #filters: dict
        #key_word: list
        if isinstance(key_word, list):
            key_word = reduce(lambda x, y: "{0}, {1}".format(x,y), key_word)
        if filters is None:
            filter_cmd = ""
        else:
            filter_cmd = "where "
            filter_list = []
            for f in filters:
                filter_list.append("{0}={1}".format(f, filters[f]))
            filter_cmd = filter_cmd + reduce(lambda x, y: "{0} and {1}".format(x,y), filter_list)
        get_cmd = "select {0} from `{1}` {2};".format(key_word, self.stock_number, filter_cmd)
        try:
            self.cursor.execute(get_cmd)
            result = self.cursor.fetchall()
        except Exception, e:
            print e
            print "get stock value fail"
            return None
        return result

    def get_from_txt(self):
        number=str(self.stock_number)
        stock = Stock(number)
        if number.startswith('6'):
            file_name=os.path.join("export", "SH#"+number+".txt")
        else:
            file_name=os.path.join("export", "SZ#"+number+".txt")
        try:
            f=open(file_name)
        except:
            return
        for line in f.readlines():
            if '-' in line:
                line = line.split('\t')
                stock.time = line[0].strip()
                stock.open_val=line[1].strip()
                stock.high_val=line[2].strip()
                stock.low_val=line[3].strip()
                stock.current_val=line[4].strip()
                stock.current_total_amount=line[5].strip()
                stock.current_total_val=line[6].strip()
                if '.00' in stock.current_total_val:
                    stock.current_total_val=stock.current_total_val.replace(".00","")
                stock.week_day = datetime.datetime.strptime(stock.time, "%Y-%m-%d").weekday()+1
                self.add_new_data(stock)           

    def delete_data_for_time(self,time):
        delete_cmd="delete from `" +self.stock_number+"` where time='" + time + "';"
        try:    
            self.cursor.execute(delete_cmd)
            self.conn.commit()
        except Exception, e:
            print e

    def add_new_data(self, stock):
        now = datetime.datetime.now().strftime('%y-%m-%d')
        if not stock.time.startswith('20'):
            stock.time = "20"+stock.time
        add_data_cmd = "insert into `{0}` (time, open_val, close_val, high_val, low_val, total_val, total_amount, week_day, EMA12, EMA26, DIF, DEA) values('{1}', {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9}, {10}, {11}, {12})".format(self.stock_number, stock.time, stock.open_val, stock.current_val, stock.high_val, stock.low_val, stock.current_total_val, stock.current_total_amount, stock.week_day, 0, 0, 0, 0)
        try:
            result = self.cursor.execute(add_data_cmd)
            self.conn.commit()
            logger1.info("{0} update successfully".format(self.stock_number))
        except Exception, e:
            print add_data_cmd
            print e
            print "fail to add data"
    
    def sortchainlist(self):
        self.chainlist = sorted(self.chainlist)
    
    def chainlist2chaindict(self):
        if len(self.chainlist)>0:
            for temp in self.chainlist:
                self.chaindict[temp.keys()[0]]=temp.values()[0]
        
    def get_from_chaindict_by_time(self, time):
        temp = self.chaindict[time]
        print temp
        #Stock_selected = pickle.load(temp)
        return temp
        
    def drop_table(self):
        try:
            drop_cmd = "drop table `" + self.stock_number + "`;"
            self.cursor.execute(drop_cmd)
            self.conn.commit()
        except Exception, e:
            print e
        
    def read_chain(self, start=0, end=-1):
        self.chainlist = self.r.lrange(self.stock_number, start, end)
        for stock in self.chainlist:
            stock = pickle.load(stock)
            self.chain[stock.time] = stock
        return self.chain
    
    def push(self, stock):
        temp = pickle.dumps(stock)
        self.r.rpush(self.stock_number, temp)
        
    def write_all(self):
        for stock in self.chainlist:
            print stock.values()
    
    def alter_stock_sql(self, command, column_name, column_type):
        try:
            alter_cmd = "alter table `" + self.stock_number + "` "+ command +" " + column_name + " " + column_type +";"
            print alter_cmd
            self.cursor.execute(alter_cmd)
            self.conn.commit()
        except Exception, e:
            print e
            print(self.stock_number+"'s table exist")
    
    def update_stock_val(self, stock_dict):
        update_cmd = "update `" + self.stock_number +"` set (" + column_name + "=" + str(column_val) + ";"
        try:    
            self.cursor.execute(update_cmd)
            self.conn.commit()
        except Exception, e:
            print e
            
        
    def update_value(self, stock_dict, filter_dict):
        update_cmd = "update `{0}` set ".format(self.stock_number)
        set_cmd = []

        for key in stock_dict:
            set_cmd.append("{0}={1}".format(key, stock_dict[key]))
        set_cmd = reduce(lambda x, y: "{0}, {1}".format(x, y), set_cmd)
        filter_cmd = " where {0}={1}".format(filter_dict.keys()[0], filter_dict.values()[0])
        update_cmd= update_cmd + set_cmd + filter_cmd
        try:
            self.cursor.execute(update_cmd)
            self.conn.commit()
            logging.debug("{0} index update".format(self.stock_number))
        except Exception, e:
            print e
            print "update {0} value fail".format(self.stock_number)
    
    def MA(self,num,time=None):
        if time == None:
            query_time = self.stock.time 
        else:
            query_time=time
        target = datetime.datetime.strptime(query_time,"%y-%m-%d").date()
        sum = 0.00
        i=0
        while i!=num:
            select_cmd = "select close_val from `" + self.stock_number +"` where time='" + str(target) + "';"
            self.cursor.execute(select_cmd)
            result = self.cursor.fetchall()
            if len(result)==1:
                close_val = result[0][0]
                print close_val
            else:
                print target
                target -= datetime.timedelta(days=1)
                continue
            sum += close_val
            target -= datetime.timedelta(days=1)
            i+=1;
        return sum/num  
        
    def EMA(self,count,stock):
        '''if not time.startswith('20'):
            date = '20' + time
        now = datetime.datetime.strptime(date).date().strftime("%Y-%m-%d")
        ahead = now-datetime.timedelta(days=1)'''
        id = stock[0]
        if id == 1:
            return 0
        else:
            current_close_val = stock[3]
        ahead_id = int(id) - 1
        ahead_EMA_cmd = "select EMA{0} from `{1}` where id={2};".format(count, self.stock_number, ahead_id)
        self.cursor.execute(ahead_EMA_cmd)
        result = self.cursor.fetchall()
        if len(result)==1: 
            ahead_EMA = result[0][0]
        else:
            print "get ahead EMA fail, please check."

        now_EMA = (ahead_EMA*(count-1)/(count+1))+(current_close_val*2/(count+1))
        return now_EMA
    def DIF(self, EMA12, EMA26):
        return EMA12 - EMA26

    def DEA(self, stock):
        id = stock[0]
        if id == 1:
            return 0
        else:
            current_DIF = stock[-2]
        ahead_id = int(id) - 1
        ahead_DEA_cmd = "select DEA from `{0}` where id={1};".format(self.stock_number, ahead_id)
        self.cursor.execute(ahead_DEA_cmd)
        result = self.cursor.fetchall()
        if len(result)==1: 
            ahead_DEA = result[0][0]
        else:
            print "get ahead EMA fail, please check."
        return (ahead_DEA * 8 / 10) + (current_DIF * 2 / 10)

    def update_DIF_EMA(self, id, EMA12, EMA26, DIF):
        update_dict = {"EMA12": EMA12, 
                        "EMA26": EMA26, 
                        "DIF": DIF}
        self.update_value(update_dict, {"id": id})
        
    def update_DEA(self, id, DEA):
        update_dict = {"DEA": DEA}
        self.update_value(update_dict, {"id": id})

    def CDMA(self,time=None):
        if time==None:
            time = self.stock.time
        ma_12 = self.EMA(12,time)
        ma_26 = self.EMA(26,time)
        dif=ma_12-ma_26
        return dif
        
    def close_sql(self):
        self.cursor.close()

