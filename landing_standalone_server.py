import http.server, socketserver, os, sys, threading

sys.stdout.reconfigure(encoding='utf-8')

PORT = 8080
LANDING_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'public_instatic_pages')

class LandingHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        # Map /landing/slug -> public_instatic_pages/slug.html
        clean_path = path.split('?')[0].strip('/')
        if clean_path.startswith('landing/'):
            slug = clean_path.replace('landing/', '')
            if not slug.endswith('.html'):
                slug = f"{slug}.html"
            return os.path.join(LANDING_DIR, slug)
        elif clean_path == '' or clean_path == 'landing':
            return os.path.join(LANDING_DIR, 'hong-nhung-skincare-vip.html')
        return super().translate_path(path)

    def log_message(self, format, *args):
        pass # Silence verbose request logs

def start_dedicated_landing_server():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    handler = LandingHTTPRequestHandler
    
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"\n================================================ metaphysics =")
        print(f"🚀 DEDICATED LIGHTNING LANDING SERVER ACTIVE AT PORT {PORT}")
        print(f"🔗 Access Link: http://localhost:{PORT}/landing/hong-nhung-skincare-vip")
        print(f"================================================ metaphysics =\n")
        httpd.serve_forever()

if __name__ == '__main__':
    start_dedicated_landing_server()
