# Spotify AI UI + Backend listo para Vercel

## 📁 Estructura

```bash
spotify-ai-pro/
│
├── frontend/
│   ├── app/
│   ├── components/
│   ├── public/
│   ├── styles/
│   ├── package.json
│   └── next.config.js
│
├── backend/
│   ├── app/
│   ├── main.py
│   ├── requirements.txt
│   └── vercel.json
│
├── docker-compose.yml
└── README.md
```

---

# 🚀 Frontend (Next.js + Tailwind)

## frontend/package.json

```json
{
  "name": "spotify-ai-ui",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start"
  },
  "dependencies": {
    "next": "latest",
    "react": "latest",
    "react-dom": "latest",
    "tailwindcss": "latest",
    "lucide-react": "latest"
  }
}
```

---

## frontend/app/page.tsx

```tsx
'use client'

import { useState } from 'react'
import { Play, Music2 } from 'lucide-react'

export default function Home() {
  const [playlist, setPlaylist] = useState([])
  const [mood, setMood] = useState('happy')

  async function generatePlaylist() {
    const res = await fetch(
      `http://localhost:8000/api/playlist?mood=${mood}`
    )

    const data = await res.json()
    setPlaylist(data.tracks)
  }

  return (
    <main className="min-h-screen bg-black text-white p-8">
      <div className="max-w-5xl mx-auto">
        <div className="flex items-center gap-3 mb-10">
          <Music2 size={40} />
          <h1 className="text-4xl font-bold">
            Spotify AI PRO MAX
          </h1>
        </div>

        <div className="bg-zinc-900 p-6 rounded-2xl mb-8">
          <h2 className="text-2xl font-semibold mb-4">
            AI Playlist Generator
          </h2>

          <div className="flex gap-4">
            <input
              value={mood}
              onChange={(e) => setMood(e.target.value)}
              className="flex-1 bg-zinc-800 p-3 rounded-xl"
              placeholder="Mood"
            />

            <button
              onClick={generatePlaylist}
              className="bg-green-500 px-6 py-3 rounded-xl font-bold hover:bg-green-400"
            >
              Generate
            </button>
          </div>
        </div>

        <div className="grid gap-4">
          {playlist.map((track: any, index: number) => (
            <div
              key={index}
              className="bg-zinc-900 rounded-2xl p-5 flex items-center justify-between"
            >
              <div>
                <h3 className="font-bold text-lg">
                  {track.title}
                </h3>
                <p className="text-zinc-400">
                  {track.artist}
                </p>
              </div>

              <button className="bg-green-500 p-3 rounded-full hover:scale-105 transition">
                <Play size={18} fill="white" />
              </button>
            </div>
          ))}
        </div>
      </div>
    </main>
  )
}
```

---

## frontend/app/globals.css

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  background: black;
}
```

---

## frontend/tailwind.config.js

```js
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}'
  ],
  theme: {
    extend: {}
  },
  plugins: []
}
```

---

# 🧠 Backend FastAPI

## backend/requirements.txt

```txt
fastapi
uvicorn
```

---

## backend/main.py

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title='Spotify AI PRO MAX')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

@app.get('/')
def root():
    return {
        'status': 'running'
    }

@app.get('/api/playlist')
def playlist(mood: str = 'happy'):
    return {
        'mood': mood,
        'tracks': [
            {
                'title': 'Neural Dreams',
                'artist': 'AI Studio'
            },
            {
                'title': 'Deep Flow',
                'artist': 'Spotify AI'
            },
            {
                'title': 'Quantum Pulse',
                'artist': 'PRO MAX'
            }
        ]
    }
```

---

# ☁️ Deploy Vercel

## backend/vercel.json

```json
{
  "version": 2,
  "builds": [
    {
      "src": "main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "main.py"
    }
  ]
}
```

---

# 🐳 Docker Compose

## docker-compose.yml

```yaml
version: '3'

services:
  backend:
    build: ./backend
    ports:
      - '8000:8000'

  frontend:
    build: ./frontend
    ports:
      - '3000:3000'
```

---

# ▶️ Ejecutar localmente

## Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

## Frontend

```bash
cd frontend
npm install
npm run dev
```

---

# 🚀 Deploy rápido

## Frontend

Sube `frontend/` a:
- Vercel

## Backend

Sube `backend/` a:
- Vercel
- Render
- Railway

---

# 🔥 Próximo nivel posible

Puedes expandir esto con:

- Auth JWT
- Stripe billing
- Streaming real
- PostgreSQL
- Redis cache
- WebSockets
- AI DJ
- OpenAI integration
- Upload de canciones
- Dashboard analytics
- SaaS multiusuario

