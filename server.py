#!/usr/bin/env python3
"""
Aplicativo Web - Download protegido por usuário e senha
"""
import os
import secrets
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
from http import cookies

# Credenciais (usuário e senha)
USERNAME = "admin"
PASSWORD = "argentina2024"

# Caminho do arquivo a ser baixado
FILE_PATH = "/home/user/app/files/EquipeArgentina.zip"
FILE_NAME = "EquipeArgentina.zip"

# Sessões ativas (em memória)
SESSIONS = set()


LOGIN_PAGE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Login - Equipe Argentina</title>
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  body {
    font-family: 'Segoe UI', Tahoma, sans-serif;
    background: linear-gradient(135deg, #75AADB 0%, #ffffff 50%, #75AADB 100%);
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
  }
  .container {
    background: #fff;
    border-radius: 16px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.2);
    padding: 40px;
    width: 100%;
    max-width: 420px;
  }
  .logo {
    text-align: center;
    font-size: 60px;
    margin-bottom: 10px;
  }
  h1 {
    text-align: center;
    color: #1d3557;
    margin-bottom: 8px;
    font-size: 24px;
  }
  .subtitle {
    text-align: center;
    color: #666;
    margin-bottom: 28px;
    font-size: 14px;
  }
  .form-group { margin-bottom: 18px; }
  label {
    display: block;
    color: #444;
    font-weight: 600;
    margin-bottom: 6px;
    font-size: 14px;
  }
  input {
    width: 100%;
    padding: 12px 14px;
    border: 2px solid #e0e0e0;
    border-radius: 8px;
    font-size: 15px;
    transition: border 0.2s;
  }
  input:focus {
    outline: none;
    border-color: #75AADB;
  }
  button {
    width: 100%;
    padding: 13px;
    background: linear-gradient(135deg, #75AADB, #1d3557);
    color: #fff;
    border: none;
    border-radius: 8px;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    margin-top: 8px;
    transition: transform 0.15s;
  }
  button:hover { transform: translateY(-2px); }
  .error {
    background: #ffe5e5;
    color: #c62828;
    padding: 10px;
    border-radius: 6px;
    margin-bottom: 16px;
    text-align: center;
    font-size: 14px;
  }
  .footer {
    text-align: center;
    margin-top: 20px;
    color: #999;
    font-size: 12px;
  }
</style>
</head>
<body>
  <div class="container">
    <div class="logo">🇦🇷</div>
    <h1>Equipe Argentina</h1>
    <p class="subtitle">Faça login para acessar o download</p>
    {ERROR}
    <form method="POST" action="/login">
      <div class="form-group">
        <label for="username">Usuário</label>
        <input type="text" id="username" name="username" required autofocus>
      </div>
      <div class="form-group">
        <label for="password">Senha</label>
        <input type="password" id="password" name="password" required>
      </div>
      <button type="submit">Entrar</button>
    </form>
    <div class="footer">© 2024 - Acesso restrito</div>
  </div>
</body>
</html>
"""


DOWNLOAD_PAGE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Download - Equipe Argentina</title>
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  body {
    font-family: 'Segoe UI', Tahoma, sans-serif;
    background: linear-gradient(135deg, #75AADB 0%, #ffffff 50%, #75AADB 100%);
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
  }
  .container {
    background: #fff;
    border-radius: 16px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.2);
    padding: 40px;
    width: 100%;
    max-width: 500px;
    text-align: center;
  }
  .icon { font-size: 70px; margin-bottom: 14px; }
  h1 { color: #1d3557; margin-bottom: 8px; }
  .welcome {
    color: #666;
    margin-bottom: 30px;
    font-size: 15px;
  }
  .file-card {
    background: #f5f9ff;
    border: 2px dashed #75AADB;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 24px;
  }
  .file-name {
    color: #1d3557;
    font-weight: 700;
    font-size: 18px;
    margin-bottom: 6px;
  }
  .file-info {
    color: #666;
    font-size: 13px;
  }
  .btn {
    display: inline-block;
    padding: 14px 32px;
    background: linear-gradient(135deg, #75AADB, #1d3557);
    color: #fff;
    border: none;
    border-radius: 8px;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    text-decoration: none;
    transition: transform 0.15s;
    margin: 4px;
  }
  .btn:hover { transform: translateY(-2px); }
  .btn-secondary {
    background: #f0f0f0;
    color: #555;
  }
</style>
</head>
<body>
  <div class="container">
    <div class="icon">📦</div>
    <h1>Bem-vindo!</h1>
    <p class="welcome">Você está autenticado. Clique abaixo para baixar o arquivo.</p>
    <div class="file-card">
      <div class="file-name">📁 EquipeArgentina.zip</div>
      <div class="file-info">Tamanho: 34.42 KB • Formato: ZIP</div>
    </div>
    <a href="/download" class="btn">⬇️ Baixar Arquivo</a>
    <a href="/logout" class="btn btn-secondary">Sair</a>
  </div>
</body>
</html>
"""


class AppHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        print(f"[LOG] {format % args}")

    def get_session(self):
        if "Cookie" in self.headers:
            c = cookies.SimpleCookie(self.headers["Cookie"])
            if "session" in c and c["session"].value in SESSIONS:
                return c["session"].value
        return None

    def send_html(self, html, status=200, headers=None):
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        if headers:
            for k, v in headers.items():
                self.send_header(k, v)
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def redirect(self, location, headers=None):
        self.send_response(302)
        self.send_header("Location", location)
        if headers:
            for k, v in headers.items():
                self.send_header(k, v)
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path

        if path == "/" or path == "/login":
            if self.get_session():
                self.redirect("/home")
                return
            self.send_html(LOGIN_PAGE.replace("{ERROR}", ""))

        elif path == "/home":
            if not self.get_session():
                self.redirect("/login")
                return
            self.send_html(DOWNLOAD_PAGE)

        elif path == "/download":
            if not self.get_session():
                self.redirect("/login")
                return
            try:
                with open(FILE_PATH, "rb") as f:
                    data = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "application/zip")
                self.send_header("Content-Disposition",
                                 f'attachment; filename="{FILE_NAME}"')
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
            except FileNotFoundError:
                self.send_html("<h1>Arquivo não encontrado</h1>", 404)

        elif path == "/logout":
            sess = self.get_session()
            if sess:
                SESSIONS.discard(sess)
            self.redirect("/login",
                          headers={"Set-Cookie": "session=; Max-Age=0; Path=/"})

        else:
            self.send_html("<h1>404 - Página não encontrada</h1>", 404)

    def do_POST(self):
        path = urlparse(self.path).path
        if path == "/login":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            data = parse_qs(body)
            user = data.get("username", [""])[0]
            pwd = data.get("password", [""])[0]

            if user == USERNAME and pwd == PASSWORD:
                token = secrets.token_hex(16)
                SESSIONS.add(token)
                self.redirect("/home",
                              headers={"Set-Cookie": f"session={token}; Path=/; HttpOnly"})
            else:
                err = '<div class="error">❌ Usuário ou senha inválidos!</div>'
                self.send_html(LOGIN_PAGE.replace("{ERROR}", err), 401)
        else:
            self.send_html("<h1>404</h1>", 404)


def main():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), AppHandler)
    print(f"✅ Servidor iniciado em http://0.0.0.0:{port}")
    print(f"   Usuário: {USERNAME}")
    print(f"   Senha:   {PASSWORD}")
    server.serve_forever()


if __name__ == "__main__":
    main()
