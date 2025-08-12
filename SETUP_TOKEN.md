# Setting up GitHub Token for Private Repo Access

## 1. Get your GitHub Token
- Go to GitHub Settings > Developer settings > Personal access tokens
- Or use an existing token if you have one

## 2. Add to Vercel
- Go to https://vercel.com/bhuman/uncle-frank/settings/environment-variables
- Add new variable:
  - Name: `GITHUB_TOKEN`
  - Value: Your GitHub token
  - Environment: Production, Preview, Development
- Click Save

## 3. Redeploy
- Go to https://vercel.com/bhuman/uncle-frank
- Click the three dots menu on latest deployment
- Click "Redeploy"

The API will now use your token to access the private gesture_generator repo.