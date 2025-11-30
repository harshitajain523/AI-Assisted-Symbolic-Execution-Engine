# GitHub Setup Guide

This guide will help you push your project to GitHub.

## Step 1: Create a GitHub Repository

1. Go to [GitHub.com](https://github.com) and sign in
2. Click the **"+"** icon in the top right corner
3. Select **"New repository"**
4. Fill in the details:
   - **Repository name**: `swe_project` (or any name you prefer)
   - **Description**: "AI-Assisted Symbolic Execution Engine"
   - **Visibility**: Choose Public or Private
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
5. Click **"Create repository"**

## Step 2: Connect Your Local Repository to GitHub

After creating the repository, GitHub will show you commands. Use these commands in your terminal:

### Option A: If you haven't pushed anything yet (recommended)

```bash
# Add the remote repository (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/swe_project.git

# Rename the default branch to main (if needed)
git branch -M main

# Push your code to GitHub
git push -u origin main
```

### Option B: If you already have a repository with content

```bash
git remote add origin https://github.com/YOUR_USERNAME/swe_project.git
git branch -M main
git push -u origin main
```

## Step 3: Authentication

When you run `git push`, GitHub will ask for authentication:

- **If using HTTPS**: You'll need a Personal Access Token (not your password)
  - Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
  - Generate a new token with `repo` permissions
  - Use this token as your password when prompted

- **If using SSH**: Set up SSH keys first
  - Follow GitHub's guide: https://docs.github.com/en/authentication/connecting-to-github-with-ssh

## Step 4: Verify

After pushing, refresh your GitHub repository page. You should see all your files!

## Future Updates

Whenever you make changes to your code:

```bash
# Stage your changes
git add .

# Commit with a message
git commit -m "Description of your changes"

# Push to GitHub
git push
```

## Troubleshooting

### "Remote origin already exists"
If you get this error, remove the existing remote first:
```bash
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/swe_project.git
```

### "Authentication failed"
- Make sure you're using a Personal Access Token (not your GitHub password)
- Or set up SSH keys for easier authentication

### "Permission denied"
- Check that you have write access to the repository
- Verify the repository URL is correct

