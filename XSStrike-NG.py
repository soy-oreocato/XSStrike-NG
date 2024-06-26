# -*- coding: utf-8 -*-
from burp import IBurpExtender, IScannerCheck, IScanIssue

from modes.scan import scanDOM
from core.context import detect_context
from core.myutils import convert_to_html_entities
from core.payloadPolyglot import algoritmo_genetico


class BurpExtender(IBurpExtender):
    def registerExtenderCallbacks(self, callbacks):
        print("XSStrike-NG V2.6\n")
        
        callbacks.registerScannerCheck(ScanCheck(callbacks))

class ScanCheck(IScannerCheck):
    def __init__(self, callbacks):
        self.callbacks = callbacks
        self.helpers = callbacks.getHelpers()
        self.payload_polyglot_genetic = algoritmo_genetico(tamano_poblacion=10, longitud_individuo=6)

    def doPassiveScan(self, baseRequestResponse):
        self.callbacks.printOutput("[ ]Passive Scanning...")
                         
        ########################
        # DOM Scannning    
        ########################
        
        # Get Request Info
        httpRequested = self.helpers.analyzeRequest(baseRequestResponse.getHttpService(), baseRequestResponse.getRequest())
        #print("Request.url: " + str(httpRequested.getUrl()))
        
        # Get Response Info
        httpResponseRaw = baseRequestResponse.getResponse()
        httpResponseAnalized = self.helpers.analyzeResponse(httpResponseRaw)
        body_offset = httpResponseAnalized.getBodyOffset()
        body_bytes = httpResponseRaw[body_offset:]
        body_str = self.helpers.bytesToString(body_bytes)
        #print("Response.body: " + str(body_str))
        
        # Inspecciona el body de la respuesta
        highlighted = scanDOM(body_str)
        if highlighted:
            detailForAlert = ""
            for line in highlighted:
                detailForAlert = detailForAlert + line + "<br>"
            #print("DetailForAlert: " + detailForAlert )    
            
            # Create alerta
            alerta = CustomIssue(
                httpRequested.getUrl(),
                baseRequestResponse.getHttpService(),
                [self.callbacks.applyMarkers(baseRequestResponse, None, None)],
                "[XSStrike-NG]DOM-XSS",
                "Potencial *sources* and *sinks* identified in HTML DOM:<br><br>" + detailForAlert,
                "Medium",
                "Tentative"
            )
            
            return [alerta]

    def doActiveScan(self, baseRequestResponse, insertionPoint):
        print("[ ]Active Scanning...")

        ########################
        # Reflected XSS   
        #######################
        
        # Get EntryPoint data
        insertion_point_name = insertionPoint.getInsertionPointName()
        insertion_point_base_value = insertionPoint.getBaseValue()
        #insertion_point_type = insertionPoint.getInsertionPointType()

        ##############################
        ## Step 1. Reflection detection
        ##############################
        
        print("[Active/Reflected] EntryPoint:" + str(insertion_point_name) + " , Value: " + str(insertion_point_base_value))

        # Unique word for reflection
        reflection_word = "XsStRIke"
        insertion_point_reflected = False  
        
        # Build a new request with the modified value
        new_request = insertionPoint.buildRequest(reflection_word)
        attack = self.callbacks.makeHttpRequest(baseRequestResponse.getHttpService(), new_request)
        response = attack.getResponse()

        # Convert the response bytes to a readable format
        if response:
            response_info = self.helpers.analyzeResponse(response)
            response_body = response[response_info.getBodyOffset():].tostring()
            #response_headers = response_info.getHeaders()
            if reflection_word in response_body:
                insertion_point_reflected = True
                print("[Active/Reflected] Entrypoint reflected")
            else:
                print("[Active/Reflected] Entrypoint No reflected")
        else:
            print("No response received.")  
    
        ##############################
        ## Step 2. Detect Context
        ##############################
        if insertion_point_reflected:
            contexto = detect_context (response_body, reflection_word)
            print("Contextos identificados: ", contexto)

        ##############################
        ## Step 5. Test Polyglot Payloads and context-based
        ##############################
        payload_inserted = False 
        if insertion_point_reflected:

            # Obtain payloads from a file based on the context 
            payloads = self.readPayloadsFromFile(contexto)
            
            # Add the Polyglot Payload generated with genetic algorithms
            payloads.insert(0, self.payload_polyglot_genetic)

            for payload in payloads:
                salted_payload = payload.strip() + reflection_word # Just For easy tracking in Logger
                new_request = insertionPoint.buildRequest(salted_payload)
                attack_payload = self.callbacks.makeHttpRequest(baseRequestResponse.getHttpService(), new_request)
                response = attack_payload.getResponse()

                # Read response
                if response:
                    response_info = self.helpers.analyzeResponse(response)
                    response_body = response[response_info.getBodyOffset():].tostring()
                    #response_headers = response_info.getHeaders()
                    if salted_payload in response_body:
                        payload_inserted = True
                        payload_reflected = salted_payload
                        print("[Active/Reflected] Payload reflected: " + salted_payload)
                        break
            
            if not payload_reflected:
                print("[Active/Reflected] All payloads were tested")


        #############################
        # Alarm based on results
        #############################

        if payload_inserted:
            httpRequested = self.helpers.analyzeRequest(attack_payload.getHttpService(), attack.getRequest())
            sanitized_payload_reflected = convert_to_html_entities(salted_payload)
            alerta = CustomIssue(
                httpRequested.getUrl(),
                attack_payload.getHttpService(),
                [self.callbacks.applyMarkers(attack_payload, None, None)],
                "[XSStrike-NG]Reflected-XSS",
                "An EntryPoint was reflected and no filter were detected.<br><br>EntryPoint Name: <b>" + insertion_point_name + " </b>,Payload: <b>" + salted_payload, 
                "High",
                "Certain")
        elif insertion_point_reflected:     
            httpRequested = self.helpers.analyzeRequest(attack.getHttpService(), attack.getRequest())
            alerta = CustomIssue(
                httpRequested.getUrl(),
                attack.getHttpService(),
                [self.callbacks.applyMarkers(attack, None, None)],
                "[XSStrike-NG]EntryPoint Reflected",
                "An EntryPoint was reflected in the body but Filtered.<br><br>EntryPoint Name: " + insertion_point_name + " ,Original Value: " + insertion_point_base_value + " ,Reflected word: " + reflection_word, 
                "Information",
                "Certain")         
        else:
            alerta = None
        
        return [alerta]

    # Gets payloads from files
    def readPayloadsFromFile(self, contexto):
            
        payload_files = {
            "HTML_file": "payloads/context-html-20.txt",
            "Attribute_file": "payloads/context-attribute-html-20.txt",
            "Event_file": "payloads/context-html-event-20.txt",
            "CSS_file": "payloads/context-css-20.txt",
            "JavaScript_file": "payloads/context-javascript-20.txt",
            "Polyglot-20-file": "payloads/generic-polyglot-50.txt",
            "Polyglot-50-file": "payloads/generic-polyglot-50.txt",
            "xsstrike-file": "payloads/xsstrike-waf-bypass.txt",
            }
                    
        if "JavaScript" in contexto: 
            filename = "JavaScript_file"
            print("[Active/Reflected] Trying JavaScript context payloads...")
        elif "Attribute" in contexto: 
            filename = "Attribute_file"
            print("[Active/Reflected] Trying Attribute HTMl context payloads...")
        elif "Event" in contexto: 
            filename = "Event_file"
            print("[Active/Reflected] Trying Event HTML context payloads...")
        elif "CSS" in contexto: 
            filename = "CSS_file"
            print("[Active/Reflected] Trying CSS context payloads...")
        elif "HTML" in contexto: 
            filename = "HTML_file"
            print("[Active/Reflected] Trying HTML Tag context payloads...")
        else:
            filename = "Polyglot-20-file"
            print("[Active/Reflected] Trying Polyglot, No context...")      

        with open(payload_files[filename], 'r') as archivo:
            payloads = archivo.readlines()
        return payloads

    # Delete duplicate Issues
    def consolidateDuplicateIssues(self, existing, new):
        #self.callbacks.printOutput("[ ]Consolidate!")
        return 1


########################
# Alarm system
########################   
class CustomIssue(IScanIssue):
    def __init__(self, url, httpService, httpMessages, name, detail, severity, confidence):
        self._url = url
        self._httpService = httpService
        self._httpMessages = httpMessages
        self._name = name
        self._detail = detail
        self._severity = severity
        self._confidence = confidence

    def getUrl(self):
        return self._url

    def getIssueName(self):
        return self._name

    def getIssueType(self):
        return 0

    def getSeverity(self):
        #Expected values are "High", "Medium", "Low", "Information" or "False positive"
        return self._severity

    def getConfidence(self):
        #Expected values are "Certain", "Firm" or "Tentative".
        return self._confidence

    def getIssueBackground(self):
        return None

    def getRemediationBackground(self):
        return None

    def getIssueDetail(self):
        return self._detail

    def getRemediationDetail(self):
        return None

    def getHttpMessages(self):
        #return []
        return self._httpMessages
        
    def getHttpService(self):
        return self._httpService