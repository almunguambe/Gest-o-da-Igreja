with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    conteudo = f.read()

import re

padrao_form = r'<form action="/cultos/novo" method="POST".*?</form>'

novo_form = '''<form action="/cultos/novo" method="POST" class="space-y-4">
    <!-- Linha 1: Data e Tipo de Culto -->
    <div class="grid grid-cols-2 gap-2">
        <div>
            <label class="text-[11px] font-bold text-slate-600 block mb-1">📅 Data do Culto</label>
            <input type="date" name="data_culto" required class="w-full h-10 px-2 text-sm border-2 rounded-xl bg-white font-medium">
        </div>
        <div>
            <label class="text-[11px] font-bold text-slate-600 block mb-1">⛪ Tipo de Culto</label>
            <select name="tipo_culto" class="w-full h-10 px-2 text-sm border-2 rounded-xl bg-white font-bold text-slate-800">
                <option value="Domingo Manhã">Domingo Manhã</option>
                <option value="Domingo Noite">Domingo Noite</option>
                <option value="Quarta-feira">Quarta-feira</option>
                <option value="Sexta-feira (Vigília)">Sexta-feira (Vigília)</option>
                <option value="Culto de Obreiros">Culto de Obreiros</option>
                <option value="Culto Especial">Culto Especial</option>
            </select>
        </div>
    </div>

    <!-- Bloco 1: Membros Adultos & Jovens -->
    <div class="p-3 bg-slate-50 border rounded-2xl space-y-2">
        <span class="text-[11px] font-black uppercase tracking-wider text-slate-700 block">👥 Membros por Faixa & Sexo</span>
        <div class="grid grid-cols-2 gap-2">
            <div>
                <label class="text-[11px] font-semibold text-slate-600 block mb-0.5">👨 Homens Adultos</label>
                <input type="number" min="0" name="homens" value="0" class="campo-soma w-full h-10 px-2 text-sm font-bold border-2 rounded-xl text-center">
            </div>
            <div>
                <label class="text-[11px] font-semibold text-slate-600 block mb-0.5">👩 Mulheres Adultas</label>
                <input type="number" min="0" name="mulheres" value="0" class="campo-soma w-full h-10 px-2 text-sm font-bold border-2 rounded-xl text-center">
            </div>
            <div>
                <label class="text-[11px] font-semibold text-blue-700 block mb-0.5">👦 Jovens Rapazes</label>
                <input type="number" min="0" name="jovens_homens" value="0" class="campo-soma w-full h-10 px-2 text-sm font-bold border-2 border-blue-200 rounded-xl text-center">
            </div>
            <div>
                <label class="text-[11px] font-semibold text-pink-700 block mb-0.5">👧 Jovens Moças</label>
                <input type="number" min="0" name="jovens_mulheres" value="0" class="campo-soma w-full h-10 px-2 text-sm font-bold border-2 border-pink-200 rounded-xl text-center">
            </div>
        </div>
    </div>

    <!-- Bloco 2: Crianças & Visitantes -->
    <div class="p-3 bg-slate-50 border rounded-2xl space-y-2">
        <span class="text-[11px] font-black uppercase tracking-wider text-slate-700 block">🧒 Crianças & 🤝 Visitantes</span>
        <div class="grid grid-cols-2 gap-2">
            <div>
                <label class="text-[11px] font-semibold text-slate-600 block mb-0.5">🧒 Crianças (Meninos)</label>
                <input type="number" min="0" name="criancas_meninos" value="0" class="campo-soma w-full h-10 px-2 text-sm font-bold border-2 rounded-xl text-center">
            </div>
            <div>
                <label class="text-[11px] font-semibold text-slate-600 block mb-0.5">👧 Crianças (Meninas)</label>
                <input type="number" min="0" name="criancas_meninas" value="0" class="campo-soma w-full h-10 px-2 text-sm font-bold border-2 rounded-xl text-center">
            </div>
            <div>
                <label class="text-[11px] font-semibold text-amber-700 block mb-0.5">🤝 Visitantes (Homens)</label>
                <input type="number" min="0" name="visitantes_homens" value="0" class="campo-soma w-full h-10 px-2 text-sm font-bold border-2 border-amber-200 rounded-xl text-center">
            </div>
            <div>
                <label class="text-[11px] font-semibold text-amber-700 block mb-0.5">🤝 Visitantes (Mulheres)</label>
                <input type="number" min="0" name="visitantes_mulheres" value="0" class="campo-soma w-full h-10 px-2 text-sm font-bold border-2 border-amber-200 rounded-xl text-center">
            </div>
        </div>
    </div>

    <!-- Bloco 3: Decisões & Total Geral -->
    <div class="grid grid-cols-2 gap-2 p-3 bg-emerald-50/70 border border-emerald-200 rounded-2xl">
        <div>
            <label class="text-[11px] font-black text-emerald-900 block mb-0.5">✝️ Apelos / Decisões</label>
            <input type="number" min="0" name="novos_convertidos" value="0" class="w-full h-10 px-2 text-sm font-black text-emerald-800 border-2 border-emerald-300 rounded-xl text-center bg-white">
        </div>
        <div>
            <label class="text-[11px] font-black text-indigo-900 block mb-0.5">📊 Total de Presentes</label>
            <input type="text" id="total_geral_display" readonly value="0" class="w-full h-10 px-2 text-sm font-black text-indigo-950 border-2 border-indigo-400 bg-indigo-100/60 rounded-xl text-center cursor-not-allowed">
        </div>
    </div>

    <!-- Mensageiro e Tema -->
    <div class="space-y-2">
        <input type="text" name="pregador" placeholder="Pregador (Palavra)" class="w-full h-10 px-3 text-sm border-2 rounded-xl">
        <input type="text" name="tema_mensagem" placeholder="Tema da Mensagem" class="w-full h-10 px-3 text-sm border-2 rounded-xl">
    </div>

    <button type="submit" class="w-full h-12 bg-blue-900 hover:bg-blue-800 text-white font-black text-sm rounded-2xl shadow transition">Gravar Presença</button>
</form>

<script>
document.addEventListener("DOMContentLoaded", function() {
    const inputsSoma = document.querySelectorAll(".campo-soma");
    const totalDisplay = document.getElementById("total_geral_display");

    function recalcularTotal() {
        let total = 0;
        inputsSoma.forEach(input => {
            const val = parseInt(input.value) || 0;
            total += val;
        });
        if(totalDisplay) totalDisplay.value = total;
    }

    inputsSoma.forEach(input => {
        input.addEventListener("input", recalcularTotal);
        input.addEventListener("change", recalcularTotal);
    });
});
</script>'''

conteudo = re.sub(padrao_form, novo_form, conteudo, count=1, flags=re.DOTALL)

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(conteudo)

print("✓ templates/dashboard.html atualizado com layout categorizado e soma automatica!")