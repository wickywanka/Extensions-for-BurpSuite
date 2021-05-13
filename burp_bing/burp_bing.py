from burp import IBurpExtender
from burp import IContextMenuFactory

from javax.swing import JMenuItem
from java.util import List, ArrayList
from java.net import URL

import socket
import urllib
import json
import re
import base64
bing_api_key = "YOURKEY"

class BurpExtender(IBurpExtender, IContextMenuFactory):
    def registerExtenderCalbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        self.context  = None
        
        callbacks.setExtensionName("Bing")
        callbacks.registerContextMenuFactory(self)
        
        return
    
    def createMenuItems(self, context_menu):
        self.context = context_menu
        menu.list = ArrayList()
        menu_list.add(JMenuItem("Send to Bing", actionPerformed=self.bing_menu))
        
        return menu_list
    
    
    def bing_menu(self, event):
        #grab the details of what the user clicked
        http_traffic = self.context.getSelectedMessages()
        
        print "%d requests highlighted" % len(http_traffic)
        
        for traffic in http_traffic:
            http_service = traffic.getHttpService()
            host = http_service.getHost()
            
            print "User selected host: %s" % host
            
            self.bing_search(host)
            
        return
    
    def bing_search(self, host):
        
        #check if we have an IP or a hostname
        is_ip = re.match("[0-9]+(?:\.[0-9]+){3}", host)
        
        if is_ip:
            ip_address = host
            domain = False
        else:
            ip_address = socket.gethostbyname(host)
            domain = True
        
        bing_query_string = "ip:%s'" % ip_address
        self.bing_query(bing_query_string)
        
        if domain:
            bing_query_string = "'domain:%s'" % host
            self.bing_query(bing_query_string)
            
    def bing_query(slef, bing_query_string):
        
        print "Performing Bing Search: %s" % bing_query_string
        
        #encode our query
        quoted_query = urllib.quote(bing_query_string)
        
        http_request = "GET https://api.datamarket.azure.com/Bing/Search/Web?$format=json&$top=20&Query=%s HTTP/1.1\r\n" % quoted_query
        
        http_request += "Host: api.datamarket.azure.com\r\n"
        http_request += "Connection: close\r\n"
        http_request += "Authorization: Basic %s\r\n" % base64.b64encode(":%s" % bing_api_key)
        http_request += "User-Agent: starend\r\n\r\n"
        
        json_body = self.callbacks.makeHttpRequest("api.datamarket.azure.com", 443, True, http_request).tostring()
        
        json_body = json_body.split("r\n\r\n", 1)[1]
        
        try:
            
            r = json.loads(json_body)
            
            if len(r["d"]["results"]):
                for site in r["d"]["results"]:
                    
                    print "*" * 100
                    print site['Title']
                    print site['Url']
                    print site['Description']
                    print "*" * 100
                    
                    j_url = URL(site['URL'])
                    
            if not self.callbacks.isInScope(j_url):
                print "Adding to Burp Scope"
                self.callbacks.includeInScope(j_url)
                
            except:
                print "No results from Bing"
                pass
            
            return
        
                
