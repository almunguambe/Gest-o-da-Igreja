with open("templates/dashboard.html", "r", encoding="utf-8") as f:
    html = f.read()

bloco_pwa_head = '''    <!-- Configurações PWA -->
    <link rel="manifest" href="/manifest.json">
    <meta name="theme-color" content="#0d3b66">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="IEAD Chicuque">
    <link rel="apple-touch-icon" href="/static/logo.png">
    <script>
      if ('serviceWorker' in navigator) {
        window.addEventListener('load', () => {
          navigator.serviceWorker.register('/sw.js')
            .then(reg => console.log('PWA ServiceWorker registado:', reg.scope))
            .catch(err => console.log('Falha no registo PWA:', err));
        });
      }
    </script>
</head>'''

if "/manifest.json" not in html and "</head>" in html:
    html = html.replace("</head>", bloco_pwa_head, 1)

with open("templates/dashboard.html", "w", encoding="utf-8") as f:
    f.write(html)

print("✓ Meta tags e registo do Service Worker inseridos no dashboard.html!")