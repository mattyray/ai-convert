# 🚀 AI Viral App

A lightweight, viral web app that lets users upload a photo and receive an AI-transformed output (e.g., “Me as a [X]”), with easy sharing and optional monetization — no logins or upfront payment required.

---

## ✅ Phase 1: Core MVP (Local / Development)

### Backend (Django + DRF)

- Set up Django project with split settings (`dev`, `prod`)
- REST API Endpoints:
  - `POST /api/upload/`: Upload user image + input
  - `GET /api/result/{uuid}/`: Retrieve processed image
- Token authentication with `authtoken` (optional for future secured routes)
- Add Celery for background task queue (optional but future-proofing)

### Frontend (React + Vite + Tailwind CSS)

- UI for uploading image + prompt input
- Loading animation while image is processed
- Result display + download/share buttons
- Live in `/frontend/` directory with clean component structure

---

## 🧠 Image Generation

**Replace OpenAI / DALL·E with:**

- ✅ Replicate.com SDXL model via REST API
  - Cost: ~$0.002–$0.005 per image (vs $0.10 with DALL·E)
  - More customizable, open source
  - Optional: Migrate to RunPod or self-host SDXL

---

## 💸 Monetization Strategy

### ✅ Phase 1: Free Tier
- AI result includes watermark
- CTA to share on socials
- Stripe donation/tip button

### ✅ Phase 2: Premium Unlock
- `POST /api/purchase/` → Stripe Checkout
- Removes watermark, HD or alternate download

### ✅ Phase 3: Ad Unlock
- Rewarded ads to remove watermark
- Use AdSense (web) or AdMob (native)

---

## 🧪 Testing Checklist

- API endpoints (`/api/upload/`, `/api/result/`)
- Image storage integration (Cloudinary/local/S3)
- Frontend UX flow (upload → loading → reveal)
- Error handling: invalid input, missing fields, timeouts

---

## 🔁 Migration Plan (DALL·E → SDXL)

### Why:
- DALL·E = $0.10/image → unsustainable
- SDXL = cheaper, more flexible, open source

### How:
- Replace OpenAI calls with Replicate:
  ```
  POST https://api.replicate.com/v1/predictions
  Authorization: Token <your_replicate_token>
  ```
- Move logic to `ai/` module (inside backend)
- Use async background jobs (DRF async views or Celery)
- Save generated output to DB or Cloudinary

---

## 🗂 Directory Structure

```
/ai-convert/
├── backend/
│   ├── django_project/
│   ├── accounts/
│   ├── api/
│   ├── ai/              ← NEW (image generation logic)
│   ├── media/
│   ├── static/
│   └── templates/
├── frontend/            ← React frontend
│   ├── src/
│   └── public/
├── .env
├── Dockerfile
├── docker-compose.yml
└── README.md            ← You are here
```

---

## 🛠 Tech Stack

- **Frontend:** React, Vite, Tailwind CSS
- **Backend:** Django, Django REST Framework
- **Image Generation:** Replicate SDXL (or RunPod)
- **Deployment:** Fly.io (backend), Netlify (frontend)
- **Media:** Cloudinary
- **Auth:** Token-based (Django authtoken)
- **CI/CD:** GitHub Actions

---

## ✅ Next Steps

- [ ] Finalize SDXL integration via Replicate
- [ ] Test async generation or webhook approach
- [ ] Deploy backend to Fly.io and frontend to Netlify
- [ ] Add donation & ad unlock options

---

Want help with any of these? Just ask.
