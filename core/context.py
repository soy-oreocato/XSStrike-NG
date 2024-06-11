import re

# Identify the context of the payload
def detect_context(content, payload):
    contexts = {
        "HTML": re.compile(r'<[^>]*>[^<]*{}[^<]*</[^>]*>'.format(re.escape(payload))),
        	#<div>{payload}</div>
        "Attribute": re.compile(r'<[^>]*(href|src|title|alt)="[^"]*{}[^"]*"[^>]*>'.format(re.escape(payload))),
        	#<img src="{payload}" alt="{payload}">
        "Event": re.compile(r'<[^>]*on\w+="[^"]*{}[^"]*"[^>]*>'.format(re.escape(payload))),
        	#<button onclick="alert('{payload}')">Click me</button>
        "CSS": re.compile(r'<style[^>]*>[^<]*{}[^<]*</style>'.format(re.escape(payload))),
        	#<style>body {background-image: url('{payload}');}</style>
        "JavaScript": re.compile(r'<script[^>]*>[^<]*{}[^<]*</script>'.format(re.escape(payload))),
    		#<script>var data = "{payload}";</script>
    }

    detected_contexts = {}

    for context, pattern in contexts.items():
        if pattern.search(content):
            detected_contexts[context] = pattern.findall(content)
    
    return detected_contexts
