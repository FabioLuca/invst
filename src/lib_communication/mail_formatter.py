from __future__ import print_function
import Datas
import Format
import jinja2
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import os
import httplib2
import base64
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
import Log
import DB_Operation as DB
import requests

"""############################################################################
                                    MAILGUN
############################################################################"""


def EnviarEmail_MailGun(opParam, enderecoDestinario, enderecoRemetente, titulo,
                        corpoHTML, corpoPlain=""):
    """Envio de email pelo MailGun

    ===========================================================================
    Realiza o envio de mail pelo MailGun
    ===========================================================================
    """
    try:
        # disable ssl warning
        # requests.packages.urllib3.disable_warnings()
        # context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        # context.verify_mode = ssl.CERT_NONE

        r = requests.post(
            "https://api.mailgun.net/v3/" +
            opParam['email']['envio']['mailgun']['domain'] +
            "/messages",
            auth=("api", opParam['email']['envio']['mailgun']['api_key']),
            data={"from": enderecoRemetente,
                  "to": enderecoDestinario,
                  "subject": titulo,
                  "html": corpoHTML,
                  "text": corpoPlain})
    except Exception as e:
        status, msg, result = Log.Registro("Erro ao requisitar MailGun: " +
                                           str(e), exception=str(e),
                                           level=3, nome=__name__)
        return False, "Falha ao acessar MailGun", str(e)
    if r.status_code == 200:
        Log.Registro(texto="Envio do email com sucesso",
                     level=1, nome=__name__)
        return True, "OK", r.status_code
    else:
        Log.Registro(texto="Falha no envio de email: " + r.status_code,
                     level=3, nome=__name__)
        return False, "Falha no envio de email", r.status_code


"""############################################################################
                                    GMAIL
############################################################################"""


def PegarCredenciais_GmailAPI(opParam):
    """Faz o acesso ao Gmail API

    ===========================================================================
    Realiza o acesso ao Gmail para envio de email.

    Documentação original do Google
    ---------------------------------------------------------------------------
    Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    ---------------------------------------------------------------------------
    A variável flags era definida fora, logo no início do módulo. Aplicava-se
    a lógica abaixo. No entanto isso começou a conflitar com o ARGPARSER do
    script principal e foi removida
    # try:
    #     import argparse
    #     flags = argparse.ArgumentParser(
    #         parents=[tools.argparser]).parse_args()
    # except ImportError:
    #     flags = None
    ===========================================================================
    """
    flags = None
    SCOPES = opParam['email']['envio']['gmail']['scopes']
    CLIENT_SECRET_FILE = opParam['email']['envio']['gmail'][
        'client_secret_file']
    APPLICATION_NAME = opParam['email']['envio']['gmail']['application_name']

    home_dir = os.path.expanduser('~')
    # home_dir = FF.CaminhoScript()
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'gmail-python-quickstart.json')
    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets('.credentials/' +
                                              CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:  # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        status, msg, result = Log.Registro("Armazenando credenciais em " +
                                           credential_path,
                                           level=1, nome=__name__)

    return credentials


def EnviarEmail_GoogleAPI(opParam, endePara, endeRemetente, titulo,
                          corpoHTML, corpoPlain=""):
    """Enia um email pelo Gmail API

    ===========================================================================
    Envia um email pelo Gmail API

    Documentação original do Google
    ---------------------------------------------------------------------------
    Shows basic usage of the Gmail API.

    Creates a Gmail API service object and outputs a list of label names
    of the user's Gmail account.
    ===========================================================================
    """
    """------------------------------------------------------------------------
    Prepara o acesso ao Gmail API
    ------------------------------------------------------------------------"""
    credentials = PegarCredenciais_GmailAPI(opParam)
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    """------------------------------------------------------------------------
    Constroi o email
    ------------------------------------------------------------------------"""
    # message_text = corpo
    # message = MIMEText(message_text)
    message = MIMEMultipart('alternative')
    message['to'] = endePara
    message['from'] = endeRemetente
    message['subject'] = titulo
    message.attach(MIMEText(corpoPlain, 'plain'))
    message.attach(MIMEText(corpoHTML, 'html'))
    raw = base64.urlsafe_b64encode(message.as_bytes())
    raw = raw.decode()
    body = {'raw': raw}

    """------------------------------------------------------------------------
    Envia o email
    ------------------------------------------------------------------------"""

    end = opParam['email']['envio']['remetente']

    try:
        message = (service.users().messages().send(userId=end, body=body)
                   .execute())
        status, msg, result = Log.Registro("Email enviado com sucesso. " +
                                           "ID de envio: " + message['id'],
                                           level=1, nome=__name__)
    except errors.HttpError as error:
        status, msg, result = Log.Registro("Erro ao enviar email (HTTP): " +
                                           str(error), exception=str(error),
                                           level=3, nome=__name__)
    except Exception as e:
        status, msg, result = Log.Registro("Erro ao enviar email (Outros): " +
                                           str(e), exception=str(e),
                                           level=3, nome=__name__)
    return True, "OK", message


"""############################################################################
                        CONSTRUIR CONTEUDO HTML E ENVIO
############################################################################"""


def ConstruirEmail_RelatorioScrap(opParam, lista):
    """Constroi o conteúdo do relatório de scrap

    ===========================================================================
        Constroi e envia um email com conteúdo HTML com a listagem de sucessos
        e erros no processo de scrapping
    ===========================================================================
    """
    """------------------------------------------------------------------------
        Organiza a lista de resultados
    ------------------------------------------------------------------------"""
    list_Err = []
    list_Suc = []

    for item in lista:
        val = Format.ConvertFloat(item[2])
        if val == 0:
            list_Err.append(item)
        elif val == 1:
            list_Suc.append(item)

    """------------------------------------------------------------------------
        Monta o conteúdo HTML com um template Django
    ------------------------------------------------------------------------"""
    templateLoader = jinja2.FileSystemLoader(searchpath="/")
    templateEnv = jinja2.Environment(loader=templateLoader)

    TEMPLATE_FILE = (os.getcwd() +
                     opParam['email']['envio']['templateRelatorioScrap'])

    Modelo = templateEnv.get_template(TEMPLATE_FILE)

    Cont = ({'dia': Datas.Agora(),
             'list_erro': list_Err,
             'list_succ': list_Suc})
    HTML = Modelo.render(Cont)

    Assunto = "Status scrap [" + str(Datas.Agora())[:19] + "]"

    Resultado = {'titulo': Assunto, 'corpo': HTML}

    return True, "OK", Resultado


def EnviarRelatorio_Scrap(opParam, user_ID):
    """Constroi e envia o email

    ===========================================================================
    Primeiramente analisa a lista recebida e verifica se há valores ou não.
    Caso não haja, então irá construir uma outra lista a partir do banco de
    dados. Em seguida constroi o conteúdo HTML baseado em template e então
    envia o email
    ===========================================================================
    """
    status, msg, result = Log.Registro("Envio de e-mail com relatório " +
                                       "de scrap...",
                                       level=1, nome=__name__)

    status, msg, lista = DB.analise_relatorio_scrap(opParam=opParam,
                                                    user_ID=user_ID)
    if not status:
        return status, msg, lista

    status, msg, conteudo = ConstruirEmail_RelatorioScrap(opParam=opParam,
                                                          lista=lista)

    """------------------------------------------------------------------------
    Determina o serviço de email a ser utilizado
    ------------------------------------------------------------------------"""

    servico = opParam['email']['envio']['provedor']

    if servico in "gmail":
        status, msg, result = EnviarEmail_GoogleAPI(
            opParam=opParam,
            endePara=opParam['email']
            ['envio']['destinatario'],
            endeRemetente=opParam['email']
            ['envio']['remetente'],
            titulo=conteudo['titulo'],
            corpoHTML=conteudo['corpo'],
            corpoPlain="")
    elif servico in "mailgun":
        status, msg, result = EnviarEmail_MailGun(
            opParam=opParam,
            enderecoDestinario=opParam['email']
            ['envio']['destinatario'],
            enderecoRemetente=opParam['email']
            ['envio']['remetenteStatus'],
            titulo=conteudo['titulo'],
            corpoHTML=conteudo['corpo'],
            corpoPlain="")
    return status, msg, result














#
# def EnviarEmail_StatusScrap(opParam, lista):
#     """Envia um relatório de operação por email
#
#     ===========================================================================
#         Constroi e envia um email com conteúdo HTML com a listagem de sucessos
#         e erros no processo de scrapping
#     ===========================================================================
#     """
#     """------------------------------------------------------------------------
#         Organiza a lista de resultados
#     ------------------------------------------------------------------------"""
#     list_Err = []
#     list_Suc = []
#
#     for item in lista:
#         val = Format.ConvertFloat(item[9])
#         if val < C._INVAL_LIM:
#             list_Err.append(item)
#         else:
#             list_Suc.append(item)
#
#     """------------------------------------------------------------------------
#         Monta o conteúdo HTML com um template Django
#     ------------------------------------------------------------------------"""
#     templateLoader = jinja2.FileSystemLoader(searchpath="/")
#     templateEnv = jinja2.Environment(loader=templateLoader)
#
#     TEMPLATE_FILE = os.getcwd() + '/html_templates/template_report_scrap.html'
#
#     Modelo = templateEnv.get_template(TEMPLATE_FILE)
#
#     Cont = ({'dia': Datas.Agora(),
#              'list_erro': list_Err,
#              'list_succ': list_Suc})
#     HTML = Modelo.render(Cont)
#
#     """------------------------------------------------------------------------
#         Envia os dados por email
#     ------------------------------------------------------------------------"""
#     fromaddr = "posicaofinanceira@gmail.com"
#     toaddr = ['pantano@gmail.com']
#     pw = "D4YZeIxSuf9lVvnGk9YL"
#     assunto = "Status scrap: " + str(Datas.Agora())
#     corpoTxt = " "
#     corpoHtml = HTML
#
#     part1 = MIMEText(corpoTxt, 'plain')
#     part2 = MIMEText(corpoHtml, 'html')
#
#     msg = MIMEMultipart('alternative')
#
#     msg.attach(part1)
#     msg.attach(part2)
#
#     msg['From'] = fromaddr
#     msg['To'] = ", ".join(toaddr)
#     msg['Subject'] = assunto
#
#     server = smtplib.SMTP('smtp.gmail.com', 587)
#     server.starttls()
#     server.login(fromaddr, pw)
#     text = msg.as_string()
#     server.sendmail(fromaddr, toaddr, text)
#     server.quit()
#
#     return True, "OK", HTML


























def EnviarValores(caminhoDB):

    """------------------------------------------------------------------------
        Realiza os cálculos
    ------------------------------------------------------------------------"""

    datas, x, dadosCompletosTIP, soma, somaFilt, \
    somaGrupo, GruposIndex, somaGrupoFilt, \
    dadosInvestT, gruposT, \
    ajuste_1o_All, poly_1o_All, \
    ajuste_1o_1y, poly_1o_1y, ajuste_1o_1y_antes, \
    ajuste_1o_1m, poly_1o_1m, ajuste_1o_1m_antes, \
    ajuste_2o_All, poly_2o_All , \
    ajuste_2o_1y, poly_2o_1y, ajuste_2o_1y_antes, \
    ajusteGrupo_1o_1y, polyGrupo_1o_1y, ajusteGrupo_1o_1y_antes, \
    ajusteGrupo_1o_6m, polyGrupo_1o_6m, ajusteGrupo_1o_6m_antes, \
    ajusteGrupo_1o_1m, polyGrupo_1o_1m, ajusteGrupo_1o_1m_antes, \
    datasPrimeiro, valoresDelta, valoresFiltDelta, valoresPrimeiro, valoresFiltPrimeiro, \
    datasDelta1y, valoresDelta1y, valoresDelta1yFilt, mediaDelta1y, mediaDelta1yFilt, \
    datasDelta2y, valoresDelta2y, valoresDelta2yFilt, mediaDelta2y, mediaDelta2yFilt, \
    datasDelta4y, valoresDelta4y, valoresDelta4yFilt, mediaDelta4y, mediaDelta4yFilt, \
    mediaDeltaAno0, mediaDeltaAno1, mediaDeltaAno2, mediaDeltaAno3 = Analyze.DadosPlot(caminhoDB)

    """------------------------------------------------------------------------
        Avalia a previsao de chegada nos valores
    ------------------------------------------------------------------------"""

    vPrevVal1 = 200000
    vPrevVal2 = 500000
    vPrevVal3 = 1000000

    prev_200k_1o_All, prev_200k_1o_1y, prev_200k_2o_All, prev_200k_2o_1y = Analyze.Previsao(caminhoDB, vPrevVal1, False)
    prev_500k_1o_All, prev_500k_1o_1y, prev_500k_2o_All, prev_500k_2o_1y = Analyze.Previsao(caminhoDB, vPrevVal2, False)
    prev_1M_1o_All, prev_1M_1o_1y, prev_1M_2o_All, prev_1M_2o_1y = Analyze.Previsao(caminhoDB, vPrevVal3, False)

    """------------------------------------------------------------------------
        Gera os plots em arquivos para anexar na mensagem
    ------------------------------------------------------------------------"""

    Plot.PlotGraficos(caminhoDB, False)
    imagemGraficoSoma = 'PLOT_SOMA.png'
    imagemGraficoIndividual = 'PLOT_INDIV.png'
    imagemGraficoTipo = 'PLOT_GRUPO.png'
    imagemGraficoPizza = 'PLOT_PIE.png'
    imagemGraficoDelta1y = 'PLOT_DELTA_MES_1Y.png'
    imagemGraficoDelta4y = 'PLOT_DELTA_MES_4Y.png'

    """------------------------------------------------------------------------
        Avalia as datas chaves para pegar os valores corretos
    ------------------------------------------------------------------------"""

    datas = DT.DatasChaves (saidaVetor=False, soDiaUtil=False)

    strDataDB_D0 = DT.FormatDB(datas[0])
    strDataDB_D1 = DT.FormatDB(datas[1])
    strDataDB_D7 = DT.FormatDB(datas[2])
    strDataDB_D30 = DT.FormatDB(datas[3])
    strDataDB_D180 = DT.FormatDB(datas[4])
    strDataDB_D360 = DT.FormatDB(datas[5])

    strDataD0 = DT.FormatData(datas[0])
    strDataD1 = DT.FormatData(datas[1])
    strDataD7 = DT.FormatData(datas[2])
    strDataD30 = DT.FormatData(datas[3])
    strDataD180 = DT.FormatData(datas[4])
    strDataD360 = DT.FormatData(datas[5])

    strDiaSemana = DT.DiaSemana(datas[0])

    listValoresD0 = DB.Listar_InvestimentosValores_Dia(caminhoDB, strDataDB_D0)
    listValoresD1 = DB.Listar_InvestimentosValores_Dia(caminhoDB, strDataDB_D1)
    listValoresD7 = DB.Listar_InvestimentosValores_Dia(caminhoDB, strDataDB_D7)
    listValoresD30 = DB.Listar_InvestimentosValores_Dia(caminhoDB, strDataDB_D30)
    listValoresD180 = DB.Listar_InvestimentosValores_Dia(caminhoDB, strDataDB_D180)
    listValoresD360 = DB.Listar_InvestimentosValores_Dia(caminhoDB, strDataDB_D360)

    """------------------------------------------------------------------------
        Realiza o cálculo do total do dia. É feito separado pois cada dia
        poderá ter uma lista de ativos diferentes, assim, uma lista de
        tamanhos diferentes
    ------------------------------------------------------------------------"""

    soma = 0
    for item in listValoresD0:
        try:
            soma = soma + float(item[3])
        except:
            soma = soma + 0
    somaD0 = soma

    soma = 0
    for item in listValoresD1:
        try:
            soma = soma + float(item[3])
        except:
            soma = soma + 0
    somaD1 = soma

    soma = 0
    for item in listValoresD7:
        try:
            soma = soma + float(item[3])
        except:
            soma = soma + 0
    somaD7 = soma

    soma = 0
    for item in listValoresD30:
        try:
            soma = soma + float(item[3])
        except:
            soma = soma + 0
    somaD30 = soma

    soma = 0
    for item in listValoresD180:
        try:
            soma = soma + float(item[3])
        except:
            soma = soma + 0
    somaD180 = soma

    soma = 0
    for item in listValoresD360:
        try:
            soma = soma + float(item[3])
        except:
            soma = soma + 0
    somaD360 = soma

    """------------------------------------------------------------------------
        Realiza o cálculo das diferenças
    ------------------------------------------------------------------------"""

    somaDif = somaD0 - somaD1
    somaDif360 = somaD0 - somaD360
    somaDif180 = somaD0 - somaD180
    somaDif30 = somaD0 - somaD30
    somaDif7 = somaD0 - somaD7

    """------------------------------------------------------------------------
        Realiza o cálculo das diferenças relativas
    ------------------------------------------------------------------------"""

    try:
        somaDifR = somaDif / somaD1 * 100
    except:
        somaDifR = "-"

    try:
        somaDifR360 = somaDif360 / somaD360 * 100
    except:
        somaDifR360 = "-"

    try:
        somaDifR180 = somaDif180 / somaD180 * 100
    except:
        somaDifR180 = "-"

    try:
        somaDifR30 = somaDif30 / somaD30 * 100
    except:
        somaDifR30 = "-"

    try:
        somaDifR7 = somaDif7 / somaD7 * 100
    except:
        somaDifR7 = "-"

    """------------------------------------------------------------------------
        Monta o vetor de diferenças de cada ativo. Somente para o dia anterior
    ------------------------------------------------------------------------"""

    listDifD0 = []
    listDifD1 = []
    listDif = []
    listDifRel = []
    #somaD0 = 0
    #somaD1 = 0
    #somaD7 = 0
    #somaD30 = 0
    #somaD180 = 0
    #somaD360 = 0
    #somaDif = 0
    i = 0
    for item in listValoresD0:
        vD0 = listValoresD0[i][3]
        vD1 = listValoresD1[i][3]
        listDifD0.append(vD0)
        listDifD1.append(vD1)
        try:
            vDif = vD0 - vD1
            vDifR = vDif/vD1*100
            #somaDif = somaDif + vDif
            #somaD0 = somaD0 + vD0
            #somaD1 = somaD1 + vD1
        except:
            vDif = "-"
            vDifR = "-"
        listDif.append(vDif)
        listDifRel.append(vDifR)
        i += 1



    """------------------------------------------------------------------------
        Gera o email
    ------------------------------------------------------------------------"""

    fromaddr = "posicaofinanceira@gmail.com"
    #toaddr = "pantano@gmail.com"
    #tocc = "jgdepaula@gmail.com"
    toaddr = ['pantano@gmail.com','jgdepaula@gmail.com']
    pw = "D4YZeIxSuf9lVvnGk9YL"
    #style="width: 490px; height: 250px;"
    assunto = "Posição financeira: " + strDataD0
    corpoTxt = "Hi!\nHow are you?\nHere is the link you wanted:\nhttp://www.python.org"

    """----------------------------------------------------------------------------
        Inicia o conteúdo HTML
    ----------------------------------------------------------------------------"""

    corpoHtml = """\
                <html>
                    <head></head>
                    <body>
                        <h1>Posi&ccedil;&atilde;o financeira do dia</h1>
                        <h2>Data: """ + strDataD0 + """ (""" + strDiaSemana + """)</h2>

                        <table class="tabelaValores" cellspacing="1" cellpadding="5">
                            <col width="300px" />
                            <col width="120px" />
                            <col width="140px" />
                            <col width="140px" />
                            <col width="140px" />
                            <col width="140px" />
                            <thead>
                                <tr>
                                <td style="text-align: center;" bgcolor="#204060"><strong><font color="#ffffff">Investimento</font></strong></td>
                                <td style="text-align: center;" bgcolor="#204060"><strong><font color="#ffffff">Tipo</font></strong></td>
                                <td style="text-align: center;" bgcolor="#204060"><strong><font color="#ffffff">Pos. D-1</font></strong><br><font color="#cccccc">""" + strDataD1 + """</font></td>
                                <td style="text-align: center;" bgcolor="#204060"><strong><font color="#ffffff">Pos. D</font></strong><br><font color="#cccccc">""" + strDataD0 + """</font></td>
                                <td style="text-align: center;" bgcolor="#204060"><strong><font color="#ffffff">Variação<br>total</font></strong></td>
                                <td style="text-align: center;" bgcolor="#204060"><strong><font color="#ffffff">Variação<br>porcentual</font></strong></td>
                                </tr>
                            </thead>
                            <tbody>"""

    i = 0
    for item in listValoresD0:
        #print(item[0])
        valD0 = Format.FormatValor(listDifD0[i], casas = 2, vazio = "-", commaFormat = True, moeda = True, separadorMil = True)
        valD1 = Format.FormatValor(listDifD1[i], casas = 2, vazio = "-", commaFormat = True, moeda = True, separadorMil = True)
        valDif = Format.FormatValor(listDif[i], casas = 2, vazio = "-", commaFormat = True, moeda = True, separadorMil = True)
        valDifR = Format.FormatValor(listDifRel[i], casas = 2, vazio = "-", commaFormat = True, moeda = False, separadorMil = True)
        corpoHtml = corpoHtml + '<tr>'
        corpoHtml = corpoHtml + '<td style="text-align: left;" bgcolor="#bfbfbf"><strong><font color="#000000" size="2">' + item[1] + '</font></strong></td>'
        corpoHtml = corpoHtml + '<td style="text-align: center;" bgcolor="#bfbfbf"><font color="#000000" size="2">' + item[2] + '</font></td>'
        if valDif == "-":
            corpoHtml = corpoHtml + '<td style="text-align: center;" bgcolor="#e6e6e6"><font color="#b3b3b3" size="2">' + valD1 + '</font></td>'
            corpoHtml = corpoHtml + '<td style="text-align: center;" bgcolor="#e6e6e6"><font color="#b3b3b3" size="2">' + valD0 + '</font></td>'
            corpoHtml = corpoHtml + '<td style="text-align: center;" bgcolor="#e6e6e6"><font color="#b3b3b3" size="2">' + valDif + '</font></td>'
            corpoHtml = corpoHtml + '<td style="text-align: center;" bgcolor="#e6e6e6"><font color="#b3b3b3" size="2">' + valDifR + '</font></td>'
        elif listDif[i] > 0:
            corpoHtml = corpoHtml + '<td style="text-align: center;" bgcolor="#e6e6e6"><font color="#239023" size="2">' + valD1 + '</font></td>'
            corpoHtml = corpoHtml + '<td style="text-align: center;" bgcolor="#e6e6e6"><strong><font color="#239023" size="2">' + valD0 + '</font></strong></td>'
            corpoHtml = corpoHtml + '<td style="text-align: center;" bgcolor="#e6e6e6"><strong><font color="#239023" size="2">' + valDif + '</font></strong></td>'
            corpoHtml = corpoHtml + '<td style="text-align: center;" bgcolor="#e6e6e6"><font color="#239023" size="2">' + valDifR + '%' + '</font></td>'
        elif listDif[i] < 0:
            corpoHtml = corpoHtml + '<td style="text-align: center;" bgcolor="#e6e6e6"><font color="#990000" size="2">' + valD1 + '</font></td>'
            corpoHtml = corpoHtml + '<td style="text-align: center;" bgcolor="#e6e6e6"><strong><font color="#990000" size="2">' + valD0 + '</font></strong></td>'
            corpoHtml = corpoHtml + '<td style="text-align: center;" bgcolor="#e6e6e6"><strong><font color="#990000" size="2">' + valDif + '</font></strong></td>'
            corpoHtml = corpoHtml + '<td style="text-align: center;" bgcolor="#e6e6e6"><font color="#990000" size="2">' + valDifR + '%' + '</font></td>'
        else:
            corpoHtml = corpoHtml + '<td style="text-align: center;" bgcolor="#e6e6e6"><font color="#737373" size="2">' + valD1 + '</font></td>'
            corpoHtml = corpoHtml + '<td style="text-align: center;" bgcolor="#e6e6e6"><strong><font color="#737373" size="2">' + valD0 + '</font></strong></td>'
            corpoHtml = corpoHtml + '<td style="text-align: center;" bgcolor="#e6e6e6"><strong><font color="#737373" size="2">' + valDif + '</font></strong></td>'
            corpoHtml = corpoHtml + '<td style="text-align: center;" bgcolor="#e6e6e6"><font color="#737373" size="2">' + valDifR + '%' + '</font></td>'

        corpoHtml = corpoHtml + '</tr>'
        i += 1

    strSomaD0 = Format.FormatValor(somaD0, casas = 2, vazio = "-", commaFormat = True, moeda = True, separadorMil = True)
    strSomaD1 = Format.FormatValor(somaD1, casas = 2, vazio = "-", commaFormat = True, moeda = True, separadorMil = True)
    strSomaDif = Format.FormatValor(somaDif, casas = 2, vazio = "-", commaFormat = True, moeda = True, separadorMil = True)
    strSomaDifR = Format.FormatValor(somaDifR, casas = 2, vazio = "-", commaFormat = True, moeda = False, separadorMil = True)

    corpoHtml = corpoHtml + '<tr>'
    corpoHtml = corpoHtml + '<td style="text-align: left;" bgcolor="#ffffff"><strong><font color="#000000">' + "" + '</font></strong></td>'
    corpoHtml = corpoHtml + '<td style="text-align: center;" bgcolor="#ffffff"><font color="#000000">' + "" + '</font></td>'
    if somaDif > 0:
        corpoHtml = corpoHtml + '<td style="text-align: center;" bgcolor="#666666"><strong><font color="#99ff33" size="3">' + strSomaD1 + '</font></strong></td>'
        corpoHtml = corpoHtml + '<td style="text-align: center;" bgcolor="#666666"><strong><font color="#99ff33" size="3">' + strSomaD0 + '</font></strong></td>'
        corpoHtml = corpoHtml + '<td style="text-align: center;" bgcolor="#666666"><strong><font color="#99ff33" size="3">' + strSomaDif + '</font></strong></td>'
        corpoHtml = corpoHtml + '<td style="text-align: center;" bgcolor="#666666"><strong><font color="#99ff33" size="3">' + strSomaDifR + '%' + '</font></strong></td>'
    elif somaDif < 0:
        corpoHtml = corpoHtml + '<td style="text-align: center;" bgcolor="#666666"><strong><font color="#ff704d" size="3">' + strSomaD1 + '</font></strong></td>'
        corpoHtml = corpoHtml + '<td style="text-align: center;" bgcolor="#666666"><strong><font color="#ff704d" size="3">' + strSomaD0 + '</font></strong></td>'
        corpoHtml = corpoHtml + '<td style="text-align: center;" bgcolor="#666666"><strong><font color="#ff704d" size="3">' + strSomaDif + '</font></strong></td>'
        corpoHtml = corpoHtml + '<td style="text-align: center;" bgcolor="#666666"><strong><font color="#ff704d" size="3">' + strSomaDifR + '%' + '</font></strong></td>'
    else:
        corpoHtml = corpoHtml + '<td style="text-align: center;" bgcolor="#666666"><strong><font color="#f2f2f2" size="3">' + strSomaD1 + '</font></strong></td>'
        corpoHtml = corpoHtml + '<td style="text-align: center;" bgcolor="#666666"><strong><font color="#f2f2f2" size="3">' + strSomaD0 + '</font></strong></td>'
        corpoHtml = corpoHtml + '<td style="text-align: center;" bgcolor="#666666"><strong><font color="#f2f2f2" size="3">' + strSomaDif + '</font></strong></td>'
        corpoHtml = corpoHtml + '<td style="text-align: center;" bgcolor="#666666"><strong><font color="#f2f2f2" size="3">' + strSomaDifR + '</font></strong></td>'

    corpoHtml = corpoHtml + '</tr></table><br><br>'

    """----------------------------------------------------------------------------
        Adiciona um gráfico dos totais e previsões
    ----------------------------------------------------------------------------"""

    strSomaDif1 = Format.FormatValor(somaDif, casas=2, vazio="-", commaFormat=True, moeda=True, separadorMil = True)
    strSomaDif7 = Format.FormatValor(somaDif7, casas=2, vazio="-", commaFormat=True, moeda=True, separadorMil = True)
    strSomaDif30 = Format.FormatValor(somaDif30, casas=2, vazio="-", commaFormat=True, moeda=True, separadorMil = True)
    strSomaDif180 = Format.FormatValor(somaDif180, casas=2, vazio="-", commaFormat=True, moeda=True, separadorMil = True)
    strSomaDif360 = Format.FormatValor(somaDif360, casas=2, vazio="-", commaFormat=True, moeda=True, separadorMil = True)

    strSomaDifR1 = Format.FormatValor(somaDifR, casas=2, vazio = "-", commaFormat = True, moeda = False, separadorMil = True)
    strSomaDifR7 = Format.FormatValor(somaDifR7, casas=2, vazio = "-", commaFormat = True, moeda = False, separadorMil = True)
    strSomaDifR30 = Format.FormatValor(somaDifR30, casas=2, vazio = "-", commaFormat = True, moeda = False, separadorMil = True)
    strSomaDifR180 = Format.FormatValor(somaDifR180, casas=2, vazio = "-", commaFormat = True, moeda = False, separadorMil = True)
    strSomaDifR360 = Format.FormatValor(somaDifR360, casas=2, vazio = "-", commaFormat = True, moeda = False, separadorMil = True)

    corpoHtml = corpoHtml + '<h1>Análise de ganhos/perdas</h1>'

    corpoHtml = corpoHtml + """<br>
                            <table class="tabelaGanhosLongo" cellspacing="1" cellpadding="5">
                                <col width="120px" />
                                <col width="110px" />
                                <col width="110px" />
                                <col width="110px" />
                                <col width="110px" />
                                <col width="110px" />
                                <thead>
                                    <tr>
                                    <td style="text-align: center;" bgcolor="#204060"><strong><font color="#ffffff"></font></strong></td>
                                    <td style="text-align: center;" bgcolor="#204060"><strong><font color="#ffffff">D1</font></strong></td>
                                    <td style="text-align: center;" bgcolor="#204060"><strong><font color="#ffffff">D7</font></strong></td>
                                    <td style="text-align: center;" bgcolor="#204060"><strong><font color="#ffffff">D30</font></strong></td>
                                    <td style="text-align: center;" bgcolor="#204060"><strong><font color="#ffffff">D180</font></strong></td>
                                    <td style="text-align: center;" bgcolor="#204060"><strong><font color="#ffffff">D360</font></strong></td>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                    <td style="text-align: left;" bgcolor="#bfbfbf"><strong><font color="#000000" size="2">Valor absoluto</font></strong></td>
                                    <td style="text-align: center;" bgcolor="#e6e6e6"><strong><font color="#000000" size="2">""" + strSomaDif1 + """</font></strong></td>
                                    <td style="text-align: center;" bgcolor="#e6e6e6"><strong><font color="#000000" size="2">""" + strSomaDif7 + """</font></strong></td>
                                    <td style="text-align: center;" bgcolor="#e6e6e6"><strong><font color="#000000" size="2">""" + strSomaDif30 + """</font></strong></td>
                                    <td style="text-align: center;" bgcolor="#e6e6e6"><strong><font color="#000000" size="2">""" + strSomaDif180 + """</font></strong></td>
                                    <td style="text-align: center;" bgcolor="#e6e6e6"><strong><font color="#000000" size="2">""" + strSomaDif360 + """</font></strong></td>
                                    </tr>
                                    <tr>
                                    <td style="text-align: left;" bgcolor="#bfbfbf"><strong><font color="#000000" size="2">Valor relativo</font></strong></td>
                                    <td style="text-align: center;" bgcolor="#e6e6e6"><strong><font color="#000000" size="2">""" + strSomaDifR1 + """%</font></strong></td>
                                    <td style="text-align: center;" bgcolor="#e6e6e6"><strong><font color="#000000" size="2">""" + strSomaDifR7 + """%</font></strong></td>
                                    <td style="text-align: center;" bgcolor="#e6e6e6"><strong><font color="#000000" size="2">""" + strSomaDifR30 + """%</font></strong></td>
                                    <td style="text-align: center;" bgcolor="#e6e6e6"><strong><font color="#000000" size="2">""" + strSomaDifR180 + """%</font></strong></td>
                                    <td style="text-align: center;" bgcolor="#e6e6e6"><strong><font color="#000000" size="2">""" + strSomaDifR360 + """%</font></strong></td>
                                    </tr>
                                </tbody>
                            </table>"""

    corpoHtml = corpoHtml + '<p>Nota: Alguns valores de ganhos podem estar acima do esperado pois na data de refência (anterior), não há registro de valores, totalizando um alto ganho.</p>'

    """----------------------------------------------------------------------------
        Adiciona um gráfico de posição de cada investimento
    ----------------------------------------------------------------------------"""

    strMediaDeltaAno0 = Format.FormatValor(mediaDeltaAno0, casas=2, vazio="-",
                                           commaFormat=True, moeda=True,
                                           separadorMil=True)
    strMediaDeltaAno1 = Format.FormatValor(mediaDeltaAno1, casas=2, vazio="-",
                                           commaFormat=True, moeda=True,
                                           separadorMil=True)
    strMediaDeltaAno2 = Format.FormatValor(mediaDeltaAno2, casas=2, vazio="-",
                                           commaFormat=True, moeda=True,
                                           separadorMil=True)
    strMediaDeltaAno3 = Format.FormatValor(mediaDeltaAno3, casas=2, vazio="-",
                                           commaFormat=True, moeda=True,
                                           separadorMil=True)

    if (strMediaDeltaAno0 == 'R$ nan'):
        strMediaDeltaAno0 = '--'

    if (strMediaDeltaAno1 == 'R$ nan'):
        strMediaDeltaAno1 = '--'

    if (strMediaDeltaAno2 == 'R$ nan'):
        strMediaDeltaAno2 = '--'

    if (strMediaDeltaAno3 == 'R$ nan'):
        strMediaDeltaAno3 = '--'

    corpoHtml = corpoHtml + '<br><br>'

    corpoHtml = corpoHtml + '<h1>Ganhos efetivos mensais</h1>'

    corpoHtml = corpoHtml + '<br><img src="cid:' + imagemGraficoDelta1y + '" alt="Gráfico de ganho mensal em 1 ano" height=500>'

    corpoHtml = corpoHtml + """<br>
                            <table class="tabelaGanhosDeltaMes4anos" cellspacing="1" cellpadding="5">
                                <col width="120px" />
                                <col width="110px" />
                                <col width="110px" />
                                <col width="110px" />
                                <col width="110px" />
                                <thead>
                                    <tr>
                                    <td style="text-align: center;" bgcolor="#204060"><strong><font color="#ffffff"></font></strong></td>
                                    <td style="text-align: center;" bgcolor="#204060"><strong><font color="#ffffff">""" + str(int(strDataD0[-4:])-0) + """</font></strong></td>
                                    <td style="text-align: center;" bgcolor="#204060"><strong><font color="#ffffff">""" + str(int(strDataD0[-4:])-1) + """</font></strong></td>
                                    <td style="text-align: center;" bgcolor="#204060"><strong><font color="#ffffff">""" + str(int(strDataD0[-4:])-2) + """</font></strong></td>
                                    <td style="text-align: center;" bgcolor="#204060"><strong><font color="#ffffff">""" + str(int(strDataD0[-4:])-3) + """</font></strong></td>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                    <td style="text-align: left;" bgcolor="#bfbfbf"><strong><font color="#000000" size="2">Ganho médio mensal no ano</font></strong></td>
                                    <td style="text-align: center;" bgcolor="#e6e6e6"><strong><font color="#000000" size="2">""" + strMediaDeltaAno0 + """</font></strong></td>
                                    <td style="text-align: center;" bgcolor="#e6e6e6"><strong><font color="#000000" size="2">""" + strMediaDeltaAno1 + """</font></strong></td>
                                    <td style="text-align: center;" bgcolor="#e6e6e6"><strong><font color="#000000" size="2">""" + strMediaDeltaAno2 + """</font></strong></td>
                                    <td style="text-align: center;" bgcolor="#e6e6e6"><strong><font color="#000000" size="2">""" + strMediaDeltaAno3 + """</font></strong></td>
                                    </tr>
                                </tbody>
                            </table>"""

    corpoHtml = corpoHtml + '<br><img src="cid:' + imagemGraficoDelta4y + '" alt="Gráfico de ganho mensal em 4 anos" height=500>'

    """----------------------------------------------------------------------------
        Adiciona um gráfico dos totais e previsões
    ----------------------------------------------------------------------------"""

    corpoHtml = corpoHtml + '<h1>Previsão de posição financeira</h1>'

    corpoHtml = corpoHtml + '<br><img src="cid:' + imagemGraficoSoma + '" alt="Gráfico de posição total" height=500>'

    corpoHtml = corpoHtml + """<br><br>
                            <table class="tabelaPrevisao" cellspacing="1" cellpadding="5">
                                <col width="120px" />
                                <col width="140px" />
                                <col width="140px" />
                                <col width="140px" />
                                <col width="140px" />
                                <thead>
                                    <tr>
                                    <td style="text-align: center;" bgcolor="#204060"><strong><font color="#ffffff">Valor</font></strong></td>
                                    <td style="text-align: center;" bgcolor="#204060"><strong><font color="#ffffff">Reta<br>Todo período</font></strong></td>
                                    <td style="text-align: center;" bgcolor="#204060"><strong><font color="#ffffff">Reta<br>Último ano</font></strong></td>
                                    <td style="text-align: center;" bgcolor="#204060"><strong><font color="#ffffff">Parábola<br>Todo período</font></strong></td>
                                    <td style="text-align: center;" bgcolor="#204060"><strong><font color="#ffffff">Parábola<br>Último ano</font></strong></td>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                    <td style="text-align: left;" bgcolor="#bfbfbf"><strong><font color="#000000" size="2">""" + Format.FormatValor(vPrevVal1, 2, "-" , True, True, True) + """</font></strong></td>
                                    <td style="text-align: center;" bgcolor="#e6e6e6"><strong><font color="#000000" size="2">""" + str(prev_200k_1o_All) + """</font></strong></td>
                                    <td style="text-align: center;" bgcolor="#e6e6e6"><strong><font color="#000000" size="2">""" + str(prev_200k_1o_1y) + """</font></strong></td>
                                    <td style="text-align: center;" bgcolor="#e6e6e6"><strong><font color="#000000" size="2">""" + str(prev_200k_2o_All) + """</font></strong></td>
                                    <td style="text-align: center;" bgcolor="#e6e6e6"><strong><font color="#000000" size="2">""" + str(prev_200k_2o_1y) + """</font></strong></td>
                                    </tr>
                                    <tr>
                                    <td style="text-align: left;" bgcolor="#bfbfbf"><strong><font color="#000000" size="2">""" + Format.FormatValor(vPrevVal2, 2, "-" , True, True, True) + """</font></strong></td>
                                    <td style="text-align: center;" bgcolor="#e6e6e6"><strong><font color="#000000" size="2">""" + str(prev_500k_1o_All) + """</font></strong></td>
                                    <td style="text-align: center;" bgcolor="#e6e6e6"><strong><font color="#000000" size="2">""" + str(prev_500k_1o_1y) + """</font></strong></td>
                                    <td style="text-align: center;" bgcolor="#e6e6e6"><strong><font color="#000000" size="2">""" + str(prev_500k_2o_All) + """</font></strong></td>
                                    <td style="text-align: center;" bgcolor="#e6e6e6"><strong><font color="#000000" size="2">""" + str(prev_500k_2o_1y) + """</font></strong></td>
                                    </tr>
                                    <tr>
                                    <td style="text-align: left;" bgcolor="#bfbfbf"><strong><font color="#000000" size="2">""" + Format.FormatValor(vPrevVal3, 2, "-" , True, True, True) + """</font></strong></td>
                                    <td style="text-align: center;" bgcolor="#e6e6e6"><strong><font color="#000000" size="2">""" + str(prev_1M_1o_All) + """</font></strong></td>
                                    <td style="text-align: center;" bgcolor="#e6e6e6"><strong><font color="#000000" size="2">""" + str(prev_1M_1o_1y) + """</font></strong></td>
                                    <td style="text-align: center;" bgcolor="#e6e6e6"><strong><font color="#000000" size="2">""" + str(prev_1M_2o_All) + """</font></strong></td>
                                    <td style="text-align: center;" bgcolor="#e6e6e6"><strong><font color="#000000" size="2">""" + str(prev_1M_2o_1y) + """</font></strong></td>
                                    </tr>
                                </tbody>
                            </table>"""

    """----------------------------------------------------------------------------
        Adiciona um gráfico de posição de cada investimento
    ----------------------------------------------------------------------------"""

    corpoHtml = corpoHtml + '<br><br>'

    corpoHtml = corpoHtml + '<h1>Valores em carteira</h1>'

    corpoHtml = corpoHtml + '<br><img src="cid:' + imagemGraficoIndividual + '" alt="Gráfico de posição individual" height=500>'

    """----------------------------------------------------------------------------
        Adiciona um gráfico de pizza para os grupos
    ----------------------------------------------------------------------------"""

    corpoHtml = corpoHtml + '<br><br>'

    corpoHtml = corpoHtml + '<h1>Distribuição dos investimentos</h1>'

    corpoHtml = corpoHtml + '<br><img src="cid:' + imagemGraficoPizza + '" alt="Gráfico de distribuição dos investimentos" height=400>'

    """----------------------------------------------------------------------------
        Adiciona um gráfico de posição de tipo de investimento
    ----------------------------------------------------------------------------"""

    corpoHtml = corpoHtml + '<br><br>'

    corpoHtml = corpoHtml + '<h1>Valores em carteira por tipo de investimento</h1>'

    corpoHtml = corpoHtml + '<br><img src="cid:' + imagemGraficoTipo + '" alt="Gráfico de posição por tipo de investimento" height=500>'

    corpoHtml = corpoHtml + """<br><br>
                            <table class="tabelaInvestGroup" cellspacing="1" cellpadding="5">
                                <col width="200px" />
                                <col width="140px" />
                                <col width="140px" />
                                <col width="140px" />
                                <thead>
                                    <tr>
                                    <td style="text-align: center;" bgcolor="#204060"><strong><font color="#ffffff">Grupo</font></strong></td>
                                    <td style="text-align: center;" bgcolor="#204060"><strong><font color="#ffffff">Rendimento<br>D30</font></strong></td>
                                    <td style="text-align: center;" bgcolor="#204060"><strong><font color="#ffffff">Rendimento<br>D180</font></strong></td>
                                    <td style="text-align: center;" bgcolor="#204060"><strong><font color="#ffffff">Rendimento<br>D360</font></strong></td>
                                    </tr>
                                </thead>
                                <tbody>"""
    #print(gruposT[1,:])
    i = 0
    for item in gruposT[1,:]:
        #print(item)
        #print(item[1])
        corpoHtml = corpoHtml + """<tr>
                                      <td style="text-align: left;" bgcolor="#bfbfbf"><strong><font color="#000000" size="2">""" + item + """</font></strong></td>
                                      <td style="text-align: center;" bgcolor="#e6e6e6"><strong><font color="#000000" size="2">""" + Format.FormatValor((polyGrupo_1o_1m[i][0]/somaGrupo[i][-1]*100), commaFormat=True) + """%</font></strong></td>
                                      <td style="text-align: center;" bgcolor="#e6e6e6"><strong><font color="#000000" size="2">""" + Format.FormatValor((polyGrupo_1o_6m[i][0]/somaGrupo[i][-1]*100), commaFormat=True) + """%</font></strong></td>
                                      <td style="text-align: center;" bgcolor="#e6e6e6"><strong><font color="#000000" size="2">""" + Format.FormatValor((polyGrupo_1o_1y[i][0]/somaGrupo[i][-1]*100), commaFormat=True) + """%</font></strong></td>
                                   </tr>"""
        i += 1


    corpoHtml = corpoHtml + """</tbody>
                               </table>"""

    """----------------------------------------------------------------------------
        Fecha o conteúdo HTML
    ----------------------------------------------------------------------------"""

    corpoHtml = corpoHtml + """</body>
                               </html>"""

    part1 = MIMEText(corpoTxt, 'plain')
    part2 = MIMEText(corpoHtml, 'html')

    msg = MIMEMultipart('alternative')

    msg.attach(part1)
    msg.attach(part2)

    """----------------------------------------------------------------------------
        Adiciona as imagens
    ----------------------------------------------------------------------------"""

    fp = open(imagemGraficoSoma, 'rb')
    img = MIMEImage(fp.read())
    fp.close()
    img.add_header('Content-ID', '<{}>'.format(imagemGraficoSoma))
    msg.attach(img)

    fp = open(imagemGraficoIndividual, 'rb')
    img = MIMEImage(fp.read())
    fp.close()
    img.add_header('Content-ID', '<{}>'.format(imagemGraficoIndividual))
    msg.attach(img)

    fp = open(imagemGraficoTipo, 'rb')
    img = MIMEImage(fp.read())
    fp.close()
    img.add_header('Content-ID', '<{}>'.format(imagemGraficoTipo))
    msg.attach(img)

    fp = open(imagemGraficoPizza, 'rb')
    img = MIMEImage(fp.read())
    fp.close()
    img.add_header('Content-ID', '<{}>'.format(imagemGraficoPizza))
    msg.attach(img)

    fp = open(imagemGraficoDelta1y, 'rb')
    img = MIMEImage(fp.read())
    fp.close()
    img.add_header('Content-ID', '<{}>'.format(imagemGraficoDelta1y))
    msg.attach(img)

    fp = open(imagemGraficoDelta4y, 'rb')
    img = MIMEImage(fp.read())
    fp.close()
    img.add_header('Content-ID', '<{}>'.format(imagemGraficoDelta4y))
    msg.attach(img)

    """----------------------------------------------------------------------------
        Configura o email
    ----------------------------------------------------------------------------"""

    msg['From'] = fromaddr
    #sg['To'] = toaddr
    msg['To'] = ", ".join(toaddr)
    msg['Subject'] = assunto

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(fromaddr, pw)
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    #server.sendmail(fromaddr, [toaddr,tocc], text) #toaddr, text)
    server.quit()

    return 1
