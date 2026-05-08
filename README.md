# 🇦🇷 App Equipe Argentina

Aplicativo web com sistema de login para download protegido do arquivo `EquipeArgentina.zip`.

## 🔐 Credenciais de Acesso
- **Usuário:** `admin`
- **Senha:** `argentina2024`

## ▶️ Como Executar
```bash
python3 server.py
```
Depois acesse no navegador: **http://localhost:8080**

## 📂 Estrutura
- `server.py` — servidor web em Python (sem dependências externas)
- `files/EquipeArgentina.zip` — arquivo disponível para download
- `README.md` — este documento

## ✨ Funcionalidades
- Tela de login com validação de usuário e senha
- Sessão protegida por cookie HttpOnly
- Página de download acessível somente após login
- Botão de logout
- Design responsivo com cores da Argentina 🇦🇷
- Bloqueio de acesso direto ao download sem autenticação

## 🛠️ Requisitos
- Python 3 (qualquer versão recente)
- Nenhuma biblioteca externa necessária
