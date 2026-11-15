# Vercel Serverless WSGI Adapter for HAME Enterprise
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server import app

# Vercel entry point
app = app
