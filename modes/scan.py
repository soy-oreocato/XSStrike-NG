#import copy
import re
#from urllib.parse import urlparse, quote, unquote

#from core.checker import checker
#from core.colors import end, green, que
#import core.config
#from core.config import xsschecker, minEfficiency
from core.dom import dom
#from core.filterChecker import filterChecker
#from core.generator import generator
#from core.htmlParser import htmlParser
#from core.requester import requester
#from core.utils import getUrl, getParams, getVar
#from core.wafDetector import wafDetector
#from core.log import setup_logger

#logger = setup_logger(__name__)

def scanDOM(response):
    print("[Passive/DOM] Analizing response...")
    highlighted = dom(response)
    if highlighted:
        print('[Passive/DOM] Potentially vulnerable objects found')
        for line in highlighted:
            print(line)
    else:
        print('[Passive/DOM] No vulnerable objects found')
        
    return highlighted