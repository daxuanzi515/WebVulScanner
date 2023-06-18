from bs4 import BeautifulSoup
import urllib.request
import threading

class Spider(object):
    user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
    # usefulurls=[]
    
    def __init__(self,domain) -> None:
        if domain[-1] !='/':
            domain = domain+'/'
        self.domain=domain

    def __scan(self, url, usefulurls):
        if url[-1] !='/':
            url = url+'/'
        
        headers={'User-Agent':self.user_agent,} 
        request=urllib.request.Request(url,None,headers) #The assembled request
        response = urllib.request.urlopen(request)
        html =response.read()
        soup = BeautifulSoup(html, 'html.parser')

        pageurls = soup.find_all('a')
        for link in pageurls:
            count=2
            u = link.get('href')
            if u==None:
                continue
            while u[0:3]=='../':
                count = count+1
                u=u[3:]
            if u[0:4]!='http':
                if count==2:
                    u = url+u
                else:
                    leng = len(url)-1
                    flag=0
                    for i in range(len(url)):
                        # t=leng-i
                        # print(t)
                        if url[leng-i]=='/':
                            count = count-1
                        if count == 0:
                            flag=leng-i
                            break
                    u=url[0:flag+1]+u
            if u in usefulurls:
                continue
            usefulurls.append(u)
        # return usefulurls

    def start(self, layer):
        usefulurls=[]
        self.__scan(self.domain, usefulurls)
        final=[]
        if layer==2:
            thread=[]
            i=0
            for url in usefulurls:
                thread.append(threading.Thread(target=self.__scan, args=(url, final)))
                thread[i].start()
                i=i+1

            for t in range(0,len(usefulurls)):
                thread[t].join()
        
        usefulurls.extend(final)
        return list(set(usefulurls))

# if __name__ == '__main__':
#     spi = Spider("http://localhost:8080/sqli-labs/")
#     start = time.perf_counter()
#     urls=spi.start(1)
#     for lin in urls:
#         print(lin)