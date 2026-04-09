# 🚀 Comprehensive Guide to Deploying the Project Live

Deploying this full-stack application (React/Vite Frontend + FastAPI/Python Backend) to production can be done in two recommended ways. 

**Option 1: Render (Backend) + Vercel (Frontend)** (Highly Recommended for scale and ease of use).
**Option 2: Docker Compose on a VPS** (DigitalOcean, AWS EC2, etc. - Recommended if you want everything on one server).

---

## Option 1: Vercel (Frontend) + Render (Backend)

This is the easiest and most robust way to get your project live with SSL included.

### Part 1: Deploy Backend to Render
1. Create an account on [Render](https://render.com/).
2. Click **New +** and select **PostgreSQL**. Create a new production database and copy its **Internal Database URL** and **External Database URL**.
3. Click **New +** and select **Web Service**. Connect it to your GitHub repository.
4. Set the following configuration for the Web Service:
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:$PORT`
5. Click **Advanced** and add the following Environment Variables:
   - `DATABASE_URL`: Your External Database URL from step 2.
   - `SECRET_KEY`: Generate a random secure string (e.g., `openssl rand -hex 32`).
   - `OPENAI_API_KEY`: Your OpenAI key.
   - `GEMINI_API_KEY`: Your Gemini key.
   - `CORS_ORIGINS_STR`: Include the upcoming Vercel URL (e.g., `https://your-frontend.vercel.app`).
   - `FRONTEND_URL`: `https://your-frontend.vercel.app`
   - `ENVIRONMENT`: `production`
6. Click **Create Web Service**. Once deployed, copy your backend URL (e.g., `https://backend-xyz.onrender.com`).

### Part 2: Deploy Frontend to Vercel
1. Push your code to GitHub.
2. Sign up / Log in to [Vercel](https://vercel.com).
3. Click **Add New Project** and import your GitHub repository.
4. Select the **frontend** folder as your Root Directory.
5. In the **Environment Variables** section, add:
   - `VITE_API_URL`: `https://backend-xyz.onrender.com/api/v1` (Your Render URL + `/api/v1`)
6. Click **Deploy**. Vercel will build the frontend with `npm run build` and give you a live URL.

### Part 3: Connect the Two
1. Take your final Vercel frontend URL.
2. Go back to Render -> Backend Service -> Environment -> Update `FRONTEND_URL` and `CORS_ORIGINS_STR` to exactly match your Vercel URL.
3. Your application is now live!

---

## Option 2: VPS Deployment via Docker Compose

If you have a Linux VPS (Virtual Private Server) such as DigitalOcean Droplet, AWS EC2, or Hetzner:

### Prerequisites:
- A Linux server with **Docker** and **Docker Compose** installed.
- A registered domain name pointing to your server's IP address.

### Step 1: Clone the Repository
SSH into your server and clone the project:
```bash
git clone https://github.com/yourusername/new-project.git
cd new-project
```

### Step 2: Configure Environment Variables
In the `backend/` directory, create a `.env` file for your production variables:
```bash
nano backend/.env
```
Add the following:
```env
ENVIRONMENT=production
SECRET_KEY=super_secure_random_string_here
DATABASE_URL=postgresql://user:password@db:5432/resume_matching_db
OPENAI_API_KEY=your_openai_key
GEMINI_API_KEY=your_gemini_key
CORS_ORIGINS_STR=http://your-domain.com,https://your-domain.com
FRONTEND_URL=https://your-domain.com
```

### Step 3: Update `docker-compose.yml` Backend URL
By default, the `VITE_API_URL` variable in `docker-compose.yml` points to `http://localhost:8000/api/v1`. 
In your `docker-compose.yml`, update the frontend environment:
```yaml
  frontend:
    ...
    environment:
      VITE_API_URL: https://your-domain.com/api/v1
```
*(Alternatively, you can configure an NGINX reverse proxy to route `/api` to the backend container).*

### Step 4: Run the Application
Start all services in detached mode:
```bash
docker-compose up --build -d
```
Check the status of your containers:
```bash
docker-compose ps
```

### Step 5: (Optional) Expose with Nginx and SSL (Certbot)
To secure your application, install Nginx and Certbot on your host server. Set up a reverse proxy pointing to port 3000 for the frontend and port 8000 for the backend.
```bash
sudo apt install nginx certbot python3-certbot-nginx
```
Configure Nginx to route `/` to `http://127.0.0.1:3000` and `/api` to `http://127.0.0.1:8000`. Run `sudo certbot --nginx` to get HTTPS.

---

## Common Post-Deployment Tasks

1. **Test Authentication**: Google OAuth will fail in production unless you update your Google Cloud Console authorized redirect URIs to point to your new live domain.
2. **Database Migrations**: Be sure you test your application schemas to see if Alembic migrations are needed.
3. **Mailing**: Ensure SMTP configurations (in Render `.env` or `backend/.env`) are correct so OTP and Email Verification works!
