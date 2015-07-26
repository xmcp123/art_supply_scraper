import sys
import requests
import re
from threaded_workers import ThreadPool
import copy
class MacPhersonProductList:
    product_list = None

    max_threads = None
    def __init__(self, search_result,max_threads = 20):#product_list is the result from MacPherson search
        self.max_threads = max_threads
        self.product_list = []
        self.resolve(search_result.get_results())


    def resolve(self,search_result):
        """
        Load each result page and create a dump of the products available
        :param search_result: result from macphersonsearch
        """
        tp = ThreadPool(self.max_threads)
        for entry in search_result:
            tp.add_task(self.add_product,search_result = entry)
            print "Added ",entry
        tp.finalize()
        self.product_list = []
        print "Requesting Results"
        tp.wait_completion()
    def get_availability(self,code):
        data = requests.get("http://www.macphersonart.com/cgi-bin/maclive/olc/inv-balance.w?item="+code+"&sponsor=200000&nocache=52187")
        data = data.content.replace("\n","").replace("\r","")
        table_regex = '''<table width="60%" border="0" cellspacing="0" cellpadding="5">(.*?)<\/table>'''
        table = re.findall(table_regex,data)
        if table:
            table = table[0]
            row_regex = '''<tr>(.*?)<\/tr>'''
            rows = re.findall(row_regex,table)

            if len(rows)>2:
                location_row = rows[0]
                #print "LOCATION ROW:",location_row
                locations = re.findall(">[ ]*?(.*?)[ ]*?<\/td>",location_row)
                for idx,location in enumerate(locations):
                    locations[idx] = location.strip()
                #print "LOCATIONS:",locations
                count_row = rows[2]
                counts = re.findall("<td align=\"center\">([0-9]*?)</td>",count_row)
                ret = {}
                total = 0
                for count in counts:
                    if count and len(count)>0:
                        total = total + int(count)
                if counts and len(counts) == len(locations):
                    for idx,location in enumerate(locations):
                        ret['location'] = location
                        ret['amount'] = counts[idx]
                        ret['total'] = total
                        if ret['amount'] and len(ret['amount'])>0 and total>0:
                            ret['percent']= round((int(counts[idx])*100)/total,2)
                        else:
                            ret['percent'] = 0
                        yield ret

    def add_product(self,search_result):
        print "Executing ",search_result
        try:
            data = requests.get(search_result[0])
            data = data.content.replace("\n","").replace("\r","")
            #print "RESULT FROM ",search_result[0],"\t",re.findall("<table class=\"mainTableWidth\"[^>]*?>(.*?)<\/table>",data)[0]
            rows = re.findall("<tr(.*?)<\/tr>",data)
            for entry in rows:
                if 'amed' in entry:
                    try:
                        product_code_regex = '''<td valign="top" class="searchResultLead borderLeft borderRight amed"><div align="center">(.*?)</div>'''
                        product_code = re.findall(product_code_regex,entry)
                        if not product_code:
                            product_code=re.findall(">([^<]*?)<\/a><\/td>",entry)
                        product_code = product_code[0]
                        product_name_regex = '''<td valign="top" class="searchResultLead borderRight amed"><div align="center">(.*?)<\/div><\/td>'''
                        product_name = re.findall(product_name_regex,entry)
                        if not product_name:
                            product_name=re.findall("<td class=\"amed greenBorderBott borderRight\">([^<]*?)<\/td>",entry)
                        product_name = product_name[0]

                        price_regex = '''<div class="listPrice">(.*?)<\/div>'''
                        price = re.findall(price_regex,entry)
                        if not price:
                            price = re.findall("<td [^>]*? class=\"amed greenBorderBott borderRight\">\$(.*?)<\/td>",entry)

                        price = price[0].replace(" ","")
                        product_obj = {'url':search_result[0],'parent_title':search_result[1],'title':product_name,'price':price,'product_code':product_code}
                        for geo in self.get_availability(product_code):
                            product_obj['location'] = geo['location']
                            product_obj['amount'] = geo['amount']
                            product_obj['total'] = geo['total']
                            product_obj['percent_of_total'] = geo['percent']
                            print "Product Object:",product_obj
                            self.product_list.append(copy.copy(product_obj))
                    except:
                        print "Exception locating result ",len(rows)
                        print "ENTRY:",entry
                        print len(rows)
                        raise
        except:
            raise

class MacPhersonSearch:
    keyword = None
    session = None
    results = None
    max_results = 200
    def __init__(self,keyword,max_results=200):
        self.keyword=keyword
        self.session = requests.session()
        self.results = []
        self.max_results = max_results
    def get_results(self):
        return self.results
    def search(self):
        base_u = "http://www.macphersonart.com/cgi-bin/maclive/olc/search-all.w?cartMode=&frames=no&searchtext={}&pageGroup=&secnav=no&sponsor=200000".format(self.keyword.replace(" ","%20"))
        base_u = base_u + "&page={}"
        u = base_u.format("1")
        response = self.session.get(u)
        self.results = self.extract_results(response.content)
        for i in range(2,100):
            if len(self.results)>self.max_results:
                print "Reached maximum result count after ",i, "pages"
                return

            u = base_u.format(i)
            try:
                response = self.session.get(u)
                new_results = self.extract_results(response.content)

                for result in new_results:
                    self.results.append(result)
                print "Currently has ",len(self.results)," entries"," out of a max of ",self.max_results

                if len(new_results) == 0:
                    print "Got empty page, aborting search"
                    return
            except:
                print "Exception requesting page #",i

    def extract_results(self,text):
        r = '''<a class="productLink" href="([^"]*?)">(.*?)</a>'''
        ret = []
        for result in re.findall(r, text):
            ret.append(result)
        return ret
