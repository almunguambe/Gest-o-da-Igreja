import os

os.makedirs("static", exist_ok=True)

# Cria um emblema circular eclesiástico de alta resolução em SVG/PNG
svg_logo = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="200" height="200">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#1e3a8a"/>
      <stop offset="100%" stop-color="#0f172a"/>
    </linearGradient>
    <linearGradient id="goldGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#fbbf24"/>
      <stop offset="100%" stop-color="#d97706"/>
    </linearGradient>
  </defs>
  <circle cx="100" cy="100" r="94" fill="url(#bgGrad)" stroke="url(#goldGrad)" stroke-width="6"/>
  <circle cx="100" cy="100" r="84" fill="none" stroke="#ffffff" stroke-width="1.5" stroke-dasharray="4,4" opacity="0.6"/>
  <!-- Cruz Central -->
  <path d="M93 45 h14 v22 h20 v14 h-20 v60 h-14 v-60 h-20 v-14 h20 z" fill="url(#goldGrad)"/>
  <!-- Bíblia Aberta -->
  <path d="M50 148 c15 -8 32 -6 50 4 c18 -10 35 -12 50 -4 v-20 c-15 -8 -32 -6 -50 4 c-18 -10 -35 -12 -50 -4 z" fill="#ffffff" opacity="0.9"/>
  <line x1="100" y1="132" x2="100" y2="152" stroke="#1e3a8a" stroke-width="2"/>
</svg>
"""

with open(os.path.join("static", "logo.svg"), "w", encoding="utf-8") as f:
    f.write(svg_logo)

# Atualiza também o template para carregar SVG ou PNG com perfeição
print("✓ Logótipo provisório gerado em static/logo.svg com sucesso!")