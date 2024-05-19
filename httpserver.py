from http.server import HTTPServer, SimpleHTTPRequestHandler, test
import socketserver

class CORSRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')  # Allow all origins
        SimpleHTTPRequestHandler.end_headers(self)

if __name__ == '__main__':
    PORT = 8000
    Handler = CORSRequestHandler

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print("serving at port", PORT)
        httpd.serve_forever()