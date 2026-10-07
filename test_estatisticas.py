import app

client = app.app.test_client()
with client.session_transaction() as sess:
    sess['usuario'] = 'superadmin'
    sess['is_superadmin'] = True

res = client.get('/superadmin/estatisticas')
print('Status Estatísticas Web:', res.status_code)

res_pdf = client.get('/superadmin/estatisticas/pdf')
print('Status Relatório PDF:', res_pdf.status_code)

if res.status_code == 200 and res_pdf.status_code == 200:
    print('✓ Módulo 1 (Estatísticas Consolidadas e PDF) validado com sucesso!')