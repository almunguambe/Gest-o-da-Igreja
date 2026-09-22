with open("templates/dashboard.html", "r", encoding="utf-8") as f:
    html = f.read()

script_pwa_botao = '''
    <!-- Script de Instalação Rápida PWA -->
    <div id="pwa-install-banner" class="fixed bottom-4 left-4 right-4 md:left-auto md:right-6 md:w-96 bg-slate-900 text-white p-4 rounded-2xl shadow-2xl border border-slate-700 z-50 flex items-center justify-between gap-3 hidden">
        <div class="flex items-center gap-3">
            <img src="/static/logo.png" class="w-10 h-10 rounded-xl bg-white p-1 object-contain" alt="Logo">
            <div>
                <h4 class="text-xs font-black uppercase text-amber-400">Instalar Aplicação</h4>
                <p class="text-[11px] text-slate-300 leading-tight">Instale no telemóvel para usar em ecrã total sem barra do navegador.</p>
            </div>
        </div>
        <button id="btn-instalar-app" class="px-3 py-2 bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs rounded-xl shadow transition whitespace-nowrap">
            Instalar
        </button>
    </div>

    <script>
      let deferredPrompt;
      window.addEventListener('beforeinstallprompt', (e) => {
        e.preventDefault();
        deferredPrompt = e;
        const banner = document.getElementById('pwa-install-banner');
        if (banner) banner.classList.remove('hidden');
      });

      const btnInstalar = document.getElementById('btn-instalar-app');
      if (btnInstalar) {
        btnInstalar.addEventListener('click', async () => {
          if (deferredPrompt) {
            deferredPrompt.prompt();
            const { outcome } = await deferredPrompt.userChoice;
            console.log('Resultado da instalação:', outcome);
            deferredPrompt = null;
            document.getElementById('pwa-install-banner').classList.add('hidden');
          }
        });
      }

      window.addEventListener('appinstalled', () => {
        const banner = document.getElementById('pwa-install-banner');
        if (banner) banner.classList.add('hidden');
        console.log('PWA da IEAD Chicuque instalada com sucesso!');
      });
    </script>
</body>
'''

if "pwa-install-banner" not in html and "</body>" in html:
    html = html.replace("</body>", script_pwa_botao, 1)

with open("templates/dashboard.html", "w", encoding="utf-8") as f:
    f.write(html)

print("✓ Botão de instalação nativa injetado com sucesso no dashboard.html!")