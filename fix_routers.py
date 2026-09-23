import os
import re

for fn in ['src/argus/api/routers/incidents.py', 'src/argus/api/routers/agents.py', 'src/argus/api/routers/tasks.py']:
    if not os.path.exists(fn): continue
    with open(fn, 'r') as f: content = f.read()
    
    # Fix incident endpoints hanging signatures
    content = re.sub(r'async def create_incident\(incident: Incident, \n    """', r'async def create_incident(incident: Incident):\n    """', content)
    content = re.sub(r'async def list_incidents\(\n    """', r'async def list_incidents():\n    """', content)
    content = re.sub(r'async def get_incident\(incident_id: str, \n    """', r'async def get_incident(incident_id: str):\n    """', content)
    content = re.sub(r'async def get_incident_timeline\(incident_id: str, \n    """', r'async def get_incident_timeline(incident_id: str):\n    """', content)
    
    # Also clean up the trailing commas / empty lines in update_incident_status and approve_incident
    content = re.sub(r'update_req: StatusUpdateRequest, \n    \n\):', r'update_req: StatusUpdateRequest):', content)
    content = re.sub(r'request: Request,\n    \n\):', r'request: Request):', content)
    content = re.sub(r'user\.sub', '"system"', content)
    
    with open(fn, 'w') as f: f.write(content)

