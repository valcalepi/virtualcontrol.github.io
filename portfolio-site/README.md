# Michael Hayes - VCF 9 Infrastructure Engineer Portfolio

Professional portfolio site for Michael Hayes, VCF 9 Infrastructure Engineer at Virtual Control LLC.

## Live Site

Deploy this repository as a GitHub Pages site to view the portfolio at:

```
https://valcalepi.github.io/<repository-name>/
```

## Quick Start

### Deploy to GitHub Pages

1. Create a new repository on GitHub (e.g., `portfolio` or `valcalepi.github.io` for a user site).

2. Push this directory to the repository:

   ```bash
   cd portfolio-site
   git init
   git add .
   git commit -m "Initial portfolio site"
   git branch -M main
   git remote add origin https://github.com/valcalepi/<repository-name>.git
   git push -u origin main
   ```

3. Enable GitHub Pages:
   - Go to **Settings** > **Pages** in your repository.
   - Under **Source**, select **Deploy from a branch**.
   - Select the **main** branch and **/ (root)** directory.
   - Click **Save**.

4. Your site will be live at `https://valcalepi.github.io/<repository-name>/` within a few minutes.

### User Site (Optional)

To make this your primary GitHub Pages site at `https://valcalepi.github.io/`:

1. Name the repository `valcalepi.github.io`.
2. Follow the same steps above. GitHub will automatically serve it as your user site.

### Local Preview

Open `index.html` directly in a browser, or use a local server:

```bash
# Python 3
python -m http.server 8000

# Then open http://localhost:8000
```

## File Structure

```
portfolio-site/
  index.html    - Main portfolio page (single-page layout)
  style.css     - All styling (responsive, dark theme, animations)
  README.md     - This file
```

## Customization

### Update LinkedIn URL

Find the LinkedIn placeholder links in `index.html` and replace `#` with your actual LinkedIn profile URL:

```html
<a href="https://www.linkedin.com/in/your-profile" ...>
```

### Add Certifications

In the Certifications section of `index.html`, duplicate an existing `.cert-card` block and update the name, issuer, and description.

### Update Contact Information

All contact details are in the Contact section near the bottom of `index.html`.

### Color Scheme

All colors are defined as CSS custom properties at the top of `style.css`:

```css
:root {
  --bg-primary: #0f1923;     /* Dark navy background */
  --bg-secondary: #1a2a3a;   /* Section alternate background */
  --accent: #00b4d8;         /* Tech blue accent */
  --text-primary: #e0e0e0;   /* Body text */
  --text-heading: #ffffff;   /* Headings */
}
```

## Technical Details

- **No JavaScript frameworks** - Pure HTML, CSS, and minimal vanilla JS for navigation and scroll effects.
- **Mobile responsive** - Fully responsive design with breakpoints at 900px, 768px, and 480px.
- **Fast loading** - No external dependencies beyond Google Fonts (Inter and JetBrains Mono).
- **Print-friendly** - Includes print stylesheet for clean printed output.
- **Accessible** - Semantic HTML structure, proper heading hierarchy, and aria labels.
- **CSS animations** - Subtle section reveal on scroll using IntersectionObserver, status pulse indicators in the lab section.

## License

All rights reserved. This portfolio site and its content are the property of Michael Hayes / Virtual Control LLC.
