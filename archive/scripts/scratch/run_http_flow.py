import requests
import time
from argus.services.orchestrator.main import ProcessedAlertResponse
import threading
import uvicorn
from fastapi import FastAPI
import sys
import json

# We just spin up the 4 mock services on ports 8000, 8001, 8002, 8003
# And the orchestrator on 8004
# Wait, actually just querying the orchestrator which makes requests... 
# To do this correctly, we'd need to start all 5 services.
