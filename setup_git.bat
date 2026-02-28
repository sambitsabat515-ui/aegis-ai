@echo off
rem Initialize a new git repository and push to GitHub

rem Ensure you have a remote repository URL ready
set REPO_URL=https://github.com/sambitsabat515-ui/Aegis-ai.git

git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin %REPO_URL%
git push -u origin main

rem Optional: Set up upstream tracking for future pushes
rem git push --set-upstream origin main
