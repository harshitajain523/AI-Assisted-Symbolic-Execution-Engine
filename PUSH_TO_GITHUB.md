# Push to GitHub - Authentication Guide

Your repository is ready to push! Follow these steps:

## Step 1: Generate a Personal Access Token

1. Go to: https://github.com/settings/tokens
2. Click **"Generate new token"** → **"Generate new token (classic)"**
3. Give it a name (e.g., "AI-Assisted-Symbolic-Execution")
4. Select the **`repo`** scope (gives full control of private repositories)
5. Click **"Generate token"**
6. **Copy the token immediately** (you won't be able to see it again!)

## Step 2: Push Your Code

Run this command:

```bash
wsl bash -c "cd /home/harshita/swe_project && git push -u origin main"
```

When prompted:
- **Username**: `harshitajain523`
- **Password**: Paste your Personal Access Token (NOT your GitHub password)

## Alternative: Use SSH (More Secure)

If you prefer SSH authentication:

1. Generate an SSH key (if you don't have one):
   ```bash
   ssh-keygen -t ed25519 -C "your_email@example.com"
   ```

2. Add it to GitHub:
   - Copy your public key: `cat ~/.ssh/id_ed25519.pub`
   - Go to: https://github.com/settings/keys
   - Click "New SSH key" and paste it

3. Change remote to SSH:
   ```bash
   git remote set-url origin git@github.com:harshitajain523/AI-Assisted-Symbolic-Execution-Engine.git
   ```

4. Push:
   ```bash
   git push -u origin main
   ```

## What's Already Done

✅ Repository initialized  
✅ Branch renamed to `main` (industry standard)  
✅ MIT License added  
✅ README updated with authors  
✅ .gitignore enhanced  
✅ Backend integrated properly  
✅ GitHub remote configured  
✅ All files committed  

You just need to authenticate and push!
