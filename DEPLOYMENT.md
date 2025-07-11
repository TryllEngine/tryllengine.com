# GitHub Pages Deployment Guide

Since you're deploying to GitHub Pages (static hosting), here's how to set up the backend for form submissions:

## ✅ **Option 1: Formspree (Recommended)**

### Setup Steps:

1. **Create Formspree Account**
   - Go to [formspree.io](https://formspree.io)
   - Sign up for a free account
   - Free tier includes 50 submissions/month

2. **Create Form**
   - Click "New Form"
   - Name it "Tryll Engine Contact Form"
   - Copy the form endpoint URL (looks like: `https://formspree.io/f/YOUR_FORM_ID`)

3. **Update the Form**
   - In `index.html`, replace `YOUR_FORM_ID` with your actual form ID:
   ```html
   <form action="https://formspree.io/f/YOUR_ACTUAL_FORM_ID" method="POST">
   ```

4. **Update Thank You Page URL**
   - In `index.html`, replace `https://your-domain.com/thank-you.html` with your actual domain:
   ```html
   <input type="hidden" name="_next" value="https://your-squarespace-domain.com/thank-you.html">
   ```

### Features:
- ✅ **Free tier**: 50 submissions/month
- ✅ **Email notifications**: Get emails when forms are submitted
- ✅ **Spam protection**: Built-in reCAPTCHA
- ✅ **Export data**: Download submissions as CSV
- ✅ **Custom redirects**: Redirect to thank you page
- ✅ **No server needed**: Works with GitHub Pages

---

## ✅ **Option 2: Netlify Forms (Alternative)**

If you prefer Netlify:

1. **Deploy to Netlify** (instead of GitHub Pages)
   - Connect your GitHub repo to Netlify
   - Enable Netlify Forms in the dashboard

2. **Update Form**
   ```html
   <form name="contact" netlify netlify-honeypot="bot-field" hidden>
   ```

---

## 📋 **GitHub Pages Setup**

### 1. Repository Setup
```bash
# Make sure your repo is public
git add .
git commit -m "Prepare for GitHub Pages deployment"
git push origin main
```

### 2. Enable GitHub Pages
1. Go to your GitHub repository
2. Settings → Pages
3. Source: Deploy from a branch
4. Branch: `main`
5. Folder: `/ (root)`

### 3. Custom Domain (Squarespace)
1. In GitHub Pages settings, add your custom domain
2. In Squarespace:
   - Go to Settings → Domains
   - Add your GitHub Pages URL as a redirect
   - Or set up DNS records to point to GitHub Pages

### 4. Files to Deploy
Make sure these files are in your repository root:
```
├── index.html
├── team.html
├── thank-you.html
├── logo/
└── README.md
```

---

## 🔧 **Form Configuration**

### Required Updates:

1. **Replace Form ID** in `index.html`:
```html
<form action="https://formspree.io/f/YOUR_ACTUAL_FORM_ID" method="POST">
```

2. **Update Domain** in hidden field:
```html
<input type="hidden" name="_next" value="https://your-actual-domain.com/thank-you.html">
```

3. **Email Subject** (optional):
```html
<input type="hidden" name="_subject" value="New Tryll Engine Contact Form Submission">
```

---

## 📊 **Form Data Management**

### Formspree Dashboard:
- View all submissions
- Export to CSV
- Set up email notifications
- Configure spam protection
- View analytics

### Email Notifications:
- Formspree will send you an email for each submission
- Contains all form data: name, email, category
- Includes sender's IP for spam detection

---

## 🚀 **Deployment Checklist**

- [ ] Create Formspree account
- [ ] Get form endpoint URL
- [ ] Update `index.html` with correct form action
- [ ] Update `_next` field with your domain
- [ ] Test form submission
- [ ] Push to GitHub
- [ ] Enable GitHub Pages
- [ ] Configure custom domain (if using Squarespace)
- [ ] Test live form

---

## 📝 **Form Data Structure**

Each submission will include:
- **Name**: User's name
- **Email**: User's email address
- **Category**: Studio, Solo Developer, Modder, or Other
- **Timestamp**: When submitted
- **IP Address**: For spam detection

---

## 💡 **Pro Tips**

1. **Test First**: Submit a test form to make sure everything works
2. **Backup**: Export your form data regularly
3. **Monitor**: Check spam folder for legitimate submissions
4. **Upgrade**: Consider paid plan if you get more than 50 submissions/month
5. **Security**: Formspree includes reCAPTCHA for spam protection

---

## 🆘 **Troubleshooting**

### Form Not Working?
1. Check the form action URL
2. Verify domain in `_next` field
3. Test with a simple submission
4. Check browser console for errors

### Not Receiving Emails?
1. Check spam folder
2. Verify email in Formspree dashboard
3. Test with different email address

### 403 Errors?
1. Make sure form is verified in Formspree
2. Check that domain matches

---

## 📞 **Support**

- **Formspree**: [formspree.io/help](https://formspree.io/help)
- **GitHub Pages**: [docs.github.com/pages](https://docs.github.com/pages)
- **Squarespace**: [support.squarespace.com](https://support.squarespace.com)

Your contact form will be fully functional with this setup, and you'll receive all submissions directly to your email!