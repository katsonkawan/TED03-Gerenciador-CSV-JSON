"""Regenera o relatório PDF depois de preencher configuracao_relatorio.json.

Uso: pip install reportlab pillow && python gerar_relatorio.py
A aplicação principal e seus testes NÃO dependem destas bibliotecas.
"""

from io import BytesIO
import json
from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    Image as RLImage, Preformatted, KeepTogether,
)

ROOT = Path(__file__).resolve().parent
CFG = json.loads((ROOT / 'configuracao_relatorio.json').read_text(encoding='utf-8'))
DESTINO = ROOT / 'TED03_Relatorio_Katson_Bonifacio_Phelype.pdf'
FONTDIR = Path('/usr/share/fonts/truetype/dejavu')
if FONTDIR.is_dir():
    pdfmetrics.registerFont(TTFont('DejaVu', str(FONTDIR / 'DejaVuSans.ttf')))
    pdfmetrics.registerFont(TTFont('DejaVu-Bold', str(FONTDIR / 'DejaVuSans-Bold.ttf')))
    pdfmetrics.registerFont(TTFont('DejaVuMono', str(FONTDIR / 'DejaVuSansMono.ttf')))
    normal, forte, mono = 'DejaVu', 'DejaVu-Bold', 'DejaVuMono'
else:
    normal, forte, mono = 'Helvetica', 'Helvetica-Bold', 'Courier'

AZUL=colors.HexColor('#184A89')
MARINHO=colors.HexColor('#152A47')
CINZA=colors.HexColor('#5A6472')
BORDA=colors.HexColor('#DFE5EE')
GELO=colors.HexColor('#F1F5FA')

styles={
 'corpo': ParagraphStyle('CorpoT', fontName=normal, fontSize=9.6, leading=15, spaceAfter=9, alignment=TA_JUSTIFY, textColor=MARINHO),
 'corpoMenor': ParagraphStyle('CorpoMenor', fontName=normal, fontSize=8.7, leading=13, spaceAfter=7, alignment=TA_LEFT, textColor=MARINHO),
 'h1': ParagraphStyle('H1T', fontName=forte, fontSize=14.2, leading=19, spaceBefore=7, spaceAfter=12, textColor=AZUL),
 'h2': ParagraphStyle('H2T', fontName=forte, fontSize=10.5, leading=15, spaceBefore=9, spaceAfter=7, textColor=MARINHO),
 'caption': ParagraphStyle('LegendaT', fontName=normal, fontSize=8.1, leading=11, spaceAfter=9, textColor=CINZA, alignment=TA_CENTER),
 'code': ParagraphStyle('CodigoT', fontName=mono, fontSize=7.65, leading=12, backColor=GELO, borderColor=BORDA, borderWidth=.6, borderPadding=9, textColor=MARINHO, spaceAfter=11),
 'celula': ParagraphStyle('CelulaT', fontName=normal, fontSize=8.4, leading=12, textColor=MARINHO),
 'cabec': ParagraphStyle('CabecT', fontName=forte, fontSize=8.4, leading=12, textColor=colors.white),
}

LARGURA=A4[0]-96
hist=[]

def p(texto,menor=False):
    hist.append(Paragraph(texto, styles['corpoMenor' if menor else 'corpo']))

def h1(t): hist.append(Paragraph(t,styles['h1']))
def h2(t): hist.append(Paragraph(t,styles['h2']))
def esp(h=8): hist.append(Spacer(1,h))
def code(t):
    bloco = Preformatted(t, styles['code'])
    caixa = Table([[bloco]], colWidths=[LARGURA], hAlign='LEFT')
    caixa.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), GELO),
        ('BOX', (0, 0), (-1, -1), 0.45, BORDA),
        ('LINEBEFORE', (0, 0), (0, -1), 3.2, AZUL),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    hist.append(caixa)
    esp(9)
def pagina(): hist.append(PageBreak())
def bold(s): return '<b>'+escape(str(s))+'</b>'

def tabela(rows, widths, first_header=True):
    data=[]
    for rownum,row in enumerate(rows):
        data.append([Paragraph(escape(str(v)),styles['cabec' if first_header and rownum==0 else 'celula']) for v in row])
    t=Table(data,colWidths=widths,hAlign='LEFT',repeatRows=1 if first_header else 0)
    cmds=[('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),('LINEBELOW',(0,0),(-1,-1),.4,BORDA)]
    if first_header:cmds += [('BACKGROUND',(0,0),(-1,0),AZUL),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,GELO])]
    else:cmds += [('ROWBACKGROUNDS',(0,0),(-1,-1),[GELO,colors.white])]
    t.setStyle(TableStyle(cmds))
    hist.append(t)
    esp(10)

def captura(nome, alto_corte, legenda):
    caminho=ROOT/'evidencias'/nome
    with PILImage.open(caminho) as figura:
        tmp=BytesIO()
        figura.crop((0,0,figura.width,min(figura.height,alto_corte))).convert('RGB').save(tmp,format='PNG')
        tmp.seek(0)
        escala=LARGURA/figura.width
        altura=min(figura.height,alto_corte)*escala
    # Reader consumes the buffer when the PDF is built, so retain it on the Image.
    elemento=RLImage(tmp,width=LARGURA,height=altura)
    elemento._buffer_persistente=tmp
    hist.append(elemento)
    esp(6)
    hist.append(Paragraph(legenda,styles['caption']))

# 1 - Capa
esp(90)
hist.append(Paragraph(escape(CFG['instituicao']).upper(),ParagraphStyle('capaInst',fontName=forte,fontSize=16,leading=24,alignment=TA_CENTER,textColor=AZUL)))
esp(14)
hist.append(Paragraph(escape(CFG['curso']),ParagraphStyle('capaCurso',fontName=normal,fontSize=11,leading=18,alignment=TA_CENTER,textColor=MARINHO)))
esp(86)
hist.append(Paragraph('RELATÓRIO TÉCNICO',ParagraphStyle('tipoCapa',fontName=forte,fontSize=12,leading=18,alignment=TA_CENTER,textColor=CINZA)))
esp(20)
hist.append(Paragraph('TED 03 - GERENCIADOR DE PERSISTÊNCIA DE DADOS EM ARQUIVOS ESTRUTURADOS (CSV E JSON)',ParagraphStyle('tituloCapa',fontName=forte,fontSize=17,leading=25,alignment=TA_CENTER,textColor=AZUL)))
esp(80)
for chave in ['integrante_1', 'integrante_2', 'integrante_3']:
    hist.append(Paragraph(escape(CFG[chave]),ParagraphStyle('integrantes'+chave,fontName=normal,fontSize=10.3,leading=20,alignment=TA_CENTER,textColor=MARINHO)))
esp(45)
hist.append(Paragraph('Disciplina: '+escape(CFG['disciplina']),ParagraphStyle('discCapa',fontName=normal,fontSize=10,leading=16,alignment=TA_CENTER)))
esp(20)
hist.append(Paragraph('31 de outubro de 2026',ParagraphStyle('dataCapa',fontName=normal,fontSize=10,alignment=TA_CENTER,textColor=CINZA)))
pagina()

# 2 - Introdução e descrição
h1('1. Identificação')
tabela([
 ('Item','Informação'),
 ('Instituição',CFG['instituicao']),
 ('Curso',CFG['curso']),
 ('Disciplina',CFG['disciplina']),
 ('Integrantes', '; '.join(CFG[chave] for chave in ['integrante_1', 'integrante_2', 'integrante_3'])),
 ('Atividade','TED 03 - Persistência de dados CSV e JSON'),
 ('Entrega',CFG['data_entrega']),
], [110,LARGURA-110])
h1('2. Introdução e objetivos')
p('A atividade propõe o desenvolvimento de um gerenciador de dados estruturados capaz de ler, converter e atualizar arquivos CSV (valores separados por vírgulas) e JSON (JavaScript Object Notation). Os arquivos permitem armazenar registros fora da memória da aplicação, viabilizando a sua recuperação em execuções posteriores.')
p('O objetivo geral é implementar persistência confiável em Python. Os objetivos específicos compreendem preservar registros na conversão entre formatos, empregar gerenciadores de contexto na manipulação de arquivos, tratar falhas de entrada/saída e proteger versões anteriores com backups automáticos.')
h1('3. Descrição da solução')
p('Foi implementada uma aplicação de linha de comando (CLI), sem dependências externas para executar suas funcionalidades. A interface centraliza três comandos: <b>ler</b>, <b>converter</b> e <b>atualizar</b>. A organização modular distribui as responsabilidades entre os componentes apresentados a seguir.')
tabela([
 ('Módulo','Responsabilidade'),
 ('io_csv.py / io_json.py','Leitura e escrita de arquivos com with open e UTF-8.'),
 ('validacao.py','Verificação de campos, tipos textuais e consistência dos registros.'),
 ('conversao.py','Controle do sentido da conversão e do caminho de destino.'),
 ('backup.py','Cópia binária dos dados antes da sobrescrita.'),
 ('persistencia.py','Atualização, gravação temporária e substituição segura.'),
 ('main.py','Comandos e mensagens claras para o usuário.'),
], [166,LARGURA-166])
pagina()

# 3 - leitura/escrita
h1('4. Implementação')
h2('4.1. Leitura de arquivos CSV e JSON')
p('A leitura do CSV utiliza <b>csv.reader</b> com <b>newline=""</b>, necessário para tratamento adequado de registros com quebras de linha internas. A codificação <b>utf-8-sig</b> reconhece UTF-8 e aceita arquivos com marca de ordem de bytes (BOM).')
code('''with open(caminho, "r", encoding="utf-8-sig", newline="") as arquivo:
    leitor = csv.reader(arquivo, strict=True)
    # Validação do cabeçalho e de cada linha lida.
    ...''')
p('O módulo JSON utiliza <b>json.load</b> e verifica chaves repetidas. Os dois leitores retornam a mesma representação interna: uma lista de dicionários cujos valores são textos.')
code('''with open(caminho, "r", encoding="utf-8-sig") as arquivo:
    registros = json.load(
        arquivo, object_pairs_hook=_objeto_sem_chaves_duplicadas
    )
return validar_registros(registros)''')
h2('4.2. Escrita e conversão sem perdas silenciosas')
p('O fluxo de conversão consiste em ler a origem, validar os registros e gravá-los no formato de destino. Para preservar os acentos, o JSON é escrito com <b>ensure_ascii=False</b>. No CSV, o DictWriter preserva a sequência dos campos e realiza corretamente o escape de aspas, vírgulas e quebras de linha.')
code('''with open(caminho, "x", encoding="utf-8") as arquivo:
    json.dump(registros, arquivo, ensure_ascii=False, indent=2)
    arquivo.write("\\n")''')
p('Há uma restrição intencional de integridade: o JSON de entrada deve conter lista não vazia de objetos, com campos uniformes e valores do tipo texto. Caso surjam números, booleanos, valores nulos, estruturas aninhadas ou campos irregulares, a aplicação informa a incompatibilidade, em vez de perder a informação de tipo sem aviso.')
h2('4.3. Atualização dos registros')
p('O comando de atualização localiza um registro pela chave <b>id</b>, exige ocorrência única e confirma a existência do campo a alterar. Caso o novo valor seja igual ao atual, não realiza gravação nem cria backup desnecessário.')
pagina()

# 4 - backup + exceptions
h1('4. Implementação (continuação)')
h2('4.4. Backup automático antes da modificação')
p('O mecanismo de backup cria, no diretório <b>backups/</b>, uma cópia binária do arquivo original com nome contendo data, hora e identificador único. O uso de <b>open(..., "xb")</b> impede que uma cópia de mesmo nome seja sobrescrita acidentalmente. O flush e o fsync são utilizados para concluir a escrita da cópia antes de prosseguir.')
code('''with open(origem, "rb") as entrada, open(copia, "xb") as saida:
    shutil.copyfileobj(entrada, saida)
    saida.flush()
    os.fsync(saida.fileno())''')
p('Na função de persistência, o backup é criado <b>antes</b> da geração e da substituição do arquivo definitivo. Se a cópia não puder ser criada, uma exceção cancela o processo, deixando o arquivo anterior inalterado.')
code('''copia = criar_backup(destino) if destino.exists() else None
temporario = destino.with_name(
    f".{destino.name}.{uuid4().hex}.tmp"
)
try:
    ESCRITORES[extensao](temporario, registros)
    os.replace(temporario, destino)
finally:
    temporario.unlink(missing_ok=True)''')
h2('4.5. Tratamento de exceções')
p('A interface captura <b>FileNotFoundError</b>, <b>PermissionError</b>, <b>UnicodeError</b>, <b>JSONDecodeError</b>, <b>csv.Error</b>, falhas gerais de <b>OSError</b> e erros próprios de validação. As falhas resultam em mensagens objetivas e código de saída 1, sem exibir rastreamentos internos ao usuário.')
code('''except FileNotFoundError as exc:
    print(f"[ERRO] Arquivo ou diretório não encontrado: {exc}",
          file=sys.stderr)
except PermissionError as exc:
    print(f"[ERRO] Permissão negada: {exc}", file=sys.stderr)''')
p('A abertura dos arquivos é realizada com <b>with open(...)</b>; assim, o fechamento é automático também quando uma exceção ocorre durante a leitura ou a escrita. O uso de arquivo temporário e <b>os.replace</b> reduz a exposição a arquivos finais parcialmente gravados.')
pagina()

# 5 - tests
h1('5. Testes e evidências de execução')
h2('5.1. Estratégia de testes automatizados')
p('Foi desenvolvida uma suíte de testes com <b>unittest</b>, executada em diretórios temporários, sem modificar os arquivos originais de exemplo. Os testes confrontam os registros convertidos com os registros de origem e verificam o conteúdo do backup byte a byte.')
tabela([
 ('Grupo de testes','Verificação realizada'),
 ('Leitura e conversão','Leitura CSV/JSON; conversão nos dois sentidos; ida e volta.'),
 ('Backup e atualização','Cópia anterior preservada; atualização CSV/JSON; valor idêntico.'),
 ('Entradas inválidas','Arquivo ausente; UTF-8 inválido; JSON malformado; CSV irregular.'),
 ('Integridade','Tipos JSON não textuais; chaves e IDs duplicados.'),
 ('Falhas simuladas','Falha no backup e falha na substituição final preservam o original.'),
], [150,LARGURA-150])
h2('5.2. Resultado observado')
p('Na execução registrada, <b>18 testes foram realizados e todos passaram</b>. O trecho de erro exibido durante o teste de arquivo ausente é intencional: faz parte da verificação da mensagem apresentada pela aplicação, não indicando falha na suíte.')
captura('05_testes_automatizados.png',220,'Figura 1 - Execução da suíte unittest: 18 testes, resultado OK. Fonte: execução do projeto.')
p('Além dos testes automatizados, foram executados quatro cenários diretamente pelo terminal. As próximas figuras apresentam os comandos, os arquivos produzidos e as mensagens observadas, permitindo verificar os requisitos da TED 03.')
pagina()

# 6 - scenario 1
h1('5.3. Evidência 1 - Leitura CSV e conversão para JSON')
p('O arquivo <b>dados/clientes.csv</b>, contendo quatro registros, foi convertido com o comando <b>python main.py converter dados/clientes.csv resultados/clientes_convertidos.json</b>. A aplicação identificou quatro registros e gravou o arquivo de saída sem erro.')
captura('01_csv_para_json.png',410,'Figura 2 - Conversão CSV para JSON, seguida da visualização do conteúdo gerado. Fonte: execução do projeto.')
h2('Análise do resultado')
p('O arquivo JSON apresenta os mesmos campos do CSV (id, nome, cidade, observacao e codigo) e preserva caracteres acentuados, aspas em observações e zeros à esquerda no código, pois os valores são tratados como texto. A mensagem de backup informa corretamente que não havia versão anterior do arquivo recém-criado.')
p('A leitura foi validada adicionalmente pela suíte automatizada. Um teste de ida e volta (CSV → JSON → CSV) confrontou o conteúdo final com a estrutura de registros original, sem diferenças nos campos ou valores.')
pagina()

# 7 - scenario 2
h1('5.4. Evidência 2 - Leitura JSON e conversão para CSV')
p('O arquivo <b>dados/clientes.json</b> foi convertido para <b>resultados/clientes_convertidos.csv</b>. A saída do terminal indica a gravação de quatro registros e a ausência de backup na criação do novo arquivo.')
captura('02_json_para_csv.png',375,'Figura 3 - Conversão JSON para CSV e exibição do arquivo CSV gerado. Fonte: execução do projeto.')
h2('Análise do resultado')
p('O cabeçalho do CSV apresenta os cinco campos de origem. Os registros contêm acentos e códigos como “000123”, mantidos sem truncamento. Valores que possuem vírgulas ou aspas são devidamente delimitados e escapados pelas rotinas do módulo csv.')
p('Essa verificação demonstra a compatibilidade entre os arquivos de exemplo dos dois formatos. Os testes automatizados abrangem ainda quebras de linha no interior de campos, tratamento que exige o uso adequado de <b>newline=""</b> no módulo CSV.')
pagina()

# 8 - scenario 3
h1('5.5. Evidência 3 - Atualização com backup anterior')
p('No arquivo CSV previamente convertido, foi executada a atualização do registro de <b>id 002</b>, modificando o campo <b>cidade</b> para “Imperatriz - MA”. Antes de substituir o CSV, o sistema gerou uma cópia de segurança com extensão <b>.bak</b>.')
captura('03_atualizacao_backup.png',403,'Figura 4 - Atualização, identificação do arquivo de backup e conferência do registro modificado. Fonte: execução do projeto.')
h2('Análise do resultado')
p('A saída informa o caminho da cópia anterior em <b>resultados/backups/</b>. Em seguida, o terminal lista o arquivo de backup e exibe a linha cujo identificador é 002, comprovando que o novo valor foi persistido. O backup retém o conteúdo existente antes da alteração.')
p('A ordem das operações é garantida pelo código: criar backup, escrever temporário e substituir o destino. A suíte também simula falha no backup e falha na troca de arquivos, verificando que o conteúdo anterior permanece íntegro em ambos os casos.')
pagina()

# 9 - errors, conclusion, references
h1('5.6. Evidência 4 - Tratamento de erro de arquivo')
p('Foi solicitada a leitura de <b>dados/arquivo_inexistente.csv</b>, inexistente no projeto. Em vez de encerrar com um rastreamento de exceção, a aplicação mostrou a causa do problema e devolveu código de saída 1, conforme esperado para uma operação não concluída.')
captura('04_erro_arquivo_ausente.png',140,'Figura 5 - Arquivo ausente: mensagem de erro legível e código de saída 1. Fonte: execução do projeto.')
h1('6. Conclusão')
p('Os objetivos propostos foram atendidos nos cenários implementados e testados. A aplicação permite leitura, conversão e atualização de registros CSV/JSON, com codificação UTF-8, gerenciadores de contexto, validação estrutural, exceções tratadas e backup prévio das versões existentes. As evidências de execução e os 18 testes automatizados sustentam os resultados observados.')
p('Entre os desafios técnicos estiveram a preservação de conteúdo textual com aspas, acentos e zeros à esquerda e o controle da ordem entre backup e atualização. Para evitar conversões semanticamente incorretas, a solução rejeita explicitamente JSON com tipos que o CSV não consegue representar de modo reversível. Como aprimoramentos futuros, podem ser incluídos formatos mais complexos e controle de gravações simultâneas.')
h1('7. Referências')
p('PYTHON SOFTWARE FOUNDATION. <b>csv - CSV File Reading and Writing</b>. Disponível em: https://docs.python.org/3/library/csv.html. Acesso em: 31 out. 2026.',menor=True)
p('PYTHON SOFTWARE FOUNDATION. <b>json - JSON encoder and decoder</b>. Disponível em: https://docs.python.org/3/library/json.html. Acesso em: 31 out. 2026.',menor=True)
p('PYTHON SOFTWARE FOUNDATION. <b>Input and Output</b>. Disponível em: https://docs.python.org/3/tutorial/inputoutput.html. Acesso em: 31 out. 2026.',menor=True)
p('PYTHON SOFTWARE FOUNDATION. <b>Built-in Exceptions</b>. Disponível em: https://docs.python.org/3/library/exceptions.html. Acesso em: 31 out. 2026.',menor=True)


def decorar(canvas,doc):
    canvas.saveState()
    w,h=A4
    canvas.setStrokeColor(BORDA)
    canvas.setLineWidth(.6)
    if doc.page!=1:
        canvas.line(48,h-40,w-48,h-40)
        canvas.setFont(normal,8)
        canvas.setFillColor(CINZA)
        canvas.drawString(48,h-32,'TED 03 | Gerenciador de persistência CSV e JSON')
    canvas.line(48,40,w-48,40)
    canvas.setFillColor(CINZA)
    canvas.setFont(normal,8)
    canvas.drawString(48,28,'Relatório técnico - 31/10/2026')
    canvas.drawRightString(w-48,28,f'Página {doc.page}')
    canvas.restoreState()

pdf=SimpleDocTemplate(str(DESTINO),pagesize=A4,rightMargin=48,leftMargin=48,topMargin=55,bottomMargin=50,
                      title='TED 03 - Gerenciador de Persistência de Dados CSV e JSON',
                      author='Katson Kawan Cardoso de Carvalho; Bonifácio Pinto Costa Neto; Phelype Rocha Marques',
                      subject='Relatorio tecnico de implementacao e testes')
pdf.build(hist,onFirstPage=decorar,onLaterPages=decorar)
print(f'PDF gerado: {DESTINO}')
