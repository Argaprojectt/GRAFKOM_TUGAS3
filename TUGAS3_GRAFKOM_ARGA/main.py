#!/usr/bin/env python3
"""
Aplikasi Grafis 2D - Backend Python
Author: Assistant
Version: 1.0

Backend sederhana untuk aplikasi grafis 2D yang menyediakan:
- Server HTTP untuk melayani file HTML
- API untuk menyimpan dan memuat data gambar
- Utilitas untuk ekspor gambar
"""

import json
import os
import time
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import webbrowser
import threading

class GraphicsServer(SimpleHTTPRequestHandler):
    """HTTP Server untuk aplikasi grafis 2D"""
    
    def __init__(self, *args, **kwargs):
        self.data_dir = "graphics_data"
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/api/projects':
            self.handle_get_projects()
        elif parsed_path.path.startswith('/api/project/'):
            project_id = parsed_path.path.split('/')[-1]
            self.handle_get_project(project_id)
        else:
            # Serve static files
            super().do_GET()
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/api/save':
            self.handle_save_project()
        elif parsed_path.path == '/api/export':
            self.handle_export_project()
        else:
            self.send_error(404, "Endpoint not found")
    
    def handle_get_projects(self):
        """Get list of saved projects"""
        try:
            projects = []
            for filename in os.listdir(self.data_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.data_dir, filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        project_data = json.load(f)
                        projects.append({
                            'id': filename[:-5],  # Remove .json extension
                            'name': project_data.get('name', 'Untitled'),
                            'created': project_data.get('created', ''),
                            'objects_count': len(project_data.get('objects', []))
                        })
            
            self.send_json_response({'projects': projects})
        except Exception as e:
            self.send_error(500, f"Error loading projects: {str(e)}")
    
    def handle_get_project(self, project_id):
        """Get specific project data"""
        try:
            filepath = os.path.join(self.data_dir, f"{project_id}.json")
            if not os.path.exists(filepath):
                self.send_error(404, "Project not found")
                return
            
            with open(filepath, 'r', encoding='utf-8') as f:
                project_data = json.load(f)
            
            self.send_json_response(project_data)
        except Exception as e:
            self.send_error(500, f"Error loading project: {str(e)}")
    
    def handle_save_project(self):
        """Save project data"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            project_data = json.loads(post_data.decode('utf-8'))
            
            # Generate project ID if not provided
            project_id = project_data.get('id', f"project_{int(time.time())}")
            project_data['id'] = project_id
            project_data['modified'] = datetime.now().isoformat()
            
            if 'created' not in project_data:
                project_data['created'] = project_data['modified']
            
            # Save to file
            filepath = os.path.join(self.data_dir, f"{project_id}.json")
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, indent=2, ensure_ascii=False)
            
            self.send_json_response({
                'success': True,
                'message': 'Project saved successfully',
                'project_id': project_id
            })
            
            print(f"Project '{project_data.get('name', project_id)}' saved successfully")
            
        except Exception as e:
            self.send_error(500, f"Error saving project: {str(e)}")