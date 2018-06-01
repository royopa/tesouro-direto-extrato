# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.support.ui import Select
import sys
import datetime
import csv
import os
from dotenv import load_dotenv
from dotenv import find_dotenv
import calendar
import shutil

load_dotenv(find_dotenv())


def get_ultima_data_disponivel_base(path_file_base):
    with open(path_file_base, 'r', encoding='utf8') as f:
        for row in reversed(list(csv.reader(f))):
            data = row[0].split(';')[0]
            if data in ['Data', 'dt_referencia']:
                return datetime.date(2000, 1, 1)
            return datetime.datetime.strptime(data[0:10], '%Y-%m-%d').date()


def do_login(driver, user_login, pass_login):
    driver.get('https://tesourodireto.bmfbovespa.com.br/portalinvestidor/')
    driver.find_element_by_id('BodyContent_txtLogin').send_keys("", user_login)
    driver.find_element_by_id('BodyContent_txtSenha').send_keys("", user_pass)
    driver.find_element_by_id('BodyContent_btnLogar').click()
    return driver


print("Início da captura dos extratos: %s" % str(datetime.datetime.now()))

name_file_base = 'extrato_tesouro_direto.csv'
path_file_base = os.path.join(name_file_base)

if not os.path.exists(path_file_base):
    shutil.copyfile('extrato_tesouro_direto.csv.example', 'extrato_tesouro_direto.csv')

ultima_data_base = get_ultima_data_disponivel_base(path_file_base)
print('última data base:', ultima_data_base)

opts = FirefoxOptions()
opts.add_argument("--headless")
driver = webdriver.Firefox(firefox_options=opts, executable_path=r'drivers/geckodriver')

# Parâmetros
user_login = os.environ.get("LOGIN_USUARIO")
user_pass = os.environ.get("SENHA_USUARIO")

# Login
driver = do_login(driver, user_login, user_pass)

# Seleciona a página de extrato
driver.get("https://tesourodireto.bmfbovespa.com.br/portalinvestidor/extrato.aspx")
driver.find_element_by_id("BodyContent_btnConsultar").click()

initialYear = int(os.environ.get("ANO_INICIAL"))
currentYear = int(datetime.datetime.now().year)
for ano in range(initialYear, currentYear):
    for mes in range(1, 13):
        # faz nova consulta
        driver.find_element_by_id("BodyContent_btnConsultar").click()
        Select(driver.find_element_by_id('BodyContent_ddlMes')).select_by_value(str(mes))
        Select(driver.find_element_by_id('BodyContent_ddlAno')).select_by_value(str(ano))
        driver.find_element_by_id("BodyContent_btnConsultar").click()

        dia = calendar.monthrange(ano, mes)[1]
        dt_referencia = datetime.date(ano, mes, dia)

        print(dt_referencia)

        if ultima_data_base > dt_referencia:
            continue

        today = datetime.datetime.today().date()
        if dt_referencia > today:
            continue

        corretoras = driver.find_elements_by_xpath("//div[contains(@class, 'section-container')]")
        for corretora in corretoras:   
            nome_corretora = corretora.find_element_by_xpath('./section/p/a').text.split(' - ')
            table_rows = corretora.find_elements_by_xpath('./section/div/table/tbody/tr')
            nome_corretora = nome_corretora[1]
            print("Corretora: %s" % nome_corretora)

            # importa para o csv base
            with open(path_file_base, 'a', newline='') as baseFile:
                fieldnames = [
                    'dt_referencia', 
                    'corretora',
                    'titulo',
                    'dt_vencimento',
                    'vr_investido',
                    'vr_bruto',
                    'vr_liquido',
                    'qtd_total',
                    'qtd_bloqueado'
                ]
                writer = csv.DictWriter(baseFile, fieldnames=fieldnames, delimiter=';', quoting=csv.QUOTE_NONNUMERIC)

                for table_row in table_rows:
                    titulo = table_row.find_element_by_xpath('./td[1]').text
                    vencimento = datetime.datetime.strptime(table_row.find_element_by_xpath('./td[2]').text, '%d/%m/%Y').date()
                    valor_investido = (table_row.find_element_by_xpath('./td[3]').text).replace('.', '').replace(',','.')
                    valor_bruto_atual = (table_row.find_element_by_xpath('./td[4]').text).replace('.', '').replace(',','.')
                    valor_liquido_atual = (table_row.find_element_by_xpath('./td[5]').text).replace('.', '').replace(',','.')
                    quant_total = (table_row.find_element_by_xpath('./td[6]').text).replace(',', '.')
                    quant_bloqueado = (table_row.find_element_by_xpath('./td[7]').text).replace(',', '.')
                   
                    # insere cada registro na database
                    row_inserted = {
                        'dt_referencia': dt_referencia,
                        'corretora': nome_corretora,
                        'titulo': titulo,
                        'dt_vencimento': vencimento,
                        'vr_investido': valor_investido,
                        'vr_bruto': valor_bruto_atual,
                        'vr_liquido': valor_liquido_atual,
                        'qtd_total': quant_total,
                        'qtd_bloqueado': quant_bloqueado
                    }
                    writer.writerow(row_inserted)
                    print("==>    %s, %s, %s, %s, %s, %s, %s, %s, %s " % (dt_referencia, nome_corretora, titulo, vencimento, valor_investido, valor_bruto_atual, valor_liquido_atual, quant_total, quant_bloqueado))        

# Fecha navegador
driver.quit()
print("Fim da captura dos extratos (%s)" % str(datetime.datetime.now()))
