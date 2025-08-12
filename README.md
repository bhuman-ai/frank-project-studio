# 🎩 Frank Project Studio

> Talk to Uncle Frank about your project from anywhere - phone, tablet, or desktop.

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/YOUR_USERNAME/frank-project-studio)

## What is this?

Frank Project Studio is a mobile-friendly web app that lets you brainstorm your project with Uncle Frank - a no-nonsense technical advisor from Brooklyn who helps you build great software.

As you chat, Frank creates and updates three blueprint documents in real-time:
- 📄 **project.md** - Your vision and features
- ⚙️ **technical.md** - Architecture and tech stack  
- 🎨 **interface.md** - UI/UX design

## Features

- 📱 **Mobile-First Design** - Works perfectly on phones
- 💬 **Natural Conversation** - Talk to Frank like a real advisor
- 📝 **Live Documents** - Watch blueprints evolve as you chat
- 🔄 **Persistent Sessions** - Pick up where you left off
- 🌐 **Access Anywhere** - Public URL from Vercel
- 🚀 **Auto-Deploy** - Push to GitHub, auto-deploys to Vercel

## Quick Start

### 1. Fork & Deploy

1. Fork this repo
2. Connect to Vercel
3. Set environment variable:
   ```
   CODESPACE_URL = https://[your-codespace]-8080.preview.app.github.dev
   ```

### 2. Run Backend (GitHub Codespace)

In your GitHub Codespace:

```bash
# Install dependencies
pip install flask flask-cors

# Run the backend server
cd backend
python3 server.py
```

### 3. Access Your App

Visit your Vercel URL: `https://your-app.vercel.app`

## Architecture

```
📱 Your Phone
      ↓
🌐 Vercel (Frontend + API Routes)
      ↓
🖥️ GitHub Codespace (Backend)
      ↓
🤖 Claude CLI (AI)
      ↓
📄 Blueprint Documents
```

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `CODESPACE_URL` | Your GitHub Codespace URL | `https://mycodespace-8080.preview.app.github.dev` |
| `CODESPACE_TOKEN` | (Optional) Auth token | `ghp_xxxxx` |

## File Structure

```
frank-project-studio/
├── index.html          # Mobile-friendly UI
├── api/               
│   ├── chat.py        # Chat endpoint
│   └── docs.py        # Document endpoint
├── backend/
│   └── server.py      # Codespace server
├── static/
│   └── style.css      # Styles
└── vercel.json        # Vercel config
```

## Development

### Local Development
```bash
# Frontend (Vercel dev server)
vercel dev

# Backend (in Codespace)
python3 backend/server.py
```

### Deploy to Production
```bash
git push origin main
# Auto-deploys via Vercel
```

## Mobile Usage

- **Swipe** between Chat and Documents tabs
- **Pull down** to refresh documents
- **Landscape mode** shows both panels
- **Offline mode** works without backend

## Troubleshooting

### Can't connect to Frank?
1. Check Codespace is running
2. Verify port 8080 is public
3. Update `CODESPACE_URL` in Vercel

### Documents not updating?
- Refresh the page
- Check backend logs
- Verify Claude CLI works

## Contributing

Pull requests welcome! Frank likes clean, practical code.

## License

MIT - Use it, build with it, make it better.

---

Built with ❤️ by Uncle Frank from Brooklyn