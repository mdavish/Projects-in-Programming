#!/usr/bin/python3
# coding: utf-8
def GetHTML(urL):
    import requests
    from lxml import html 
    return html.fromstring((requests.get(url)).text)

url = "http://www.gallup.com/home.aspx"
gallup_html = GetHTML(url)

unemployment_xp = '//*[@id="rbnSection323SECTION-526"]/table/tbody/tr[1]/td[2]'
unemployment = gallup_html.xpath(unemployment_xp)[0].text_content()

goodjobs_xp = '//*[@id="rbnSection323SECTION-526"]/table/tbody/tr[2]/td[2]'
goodjobs = gallup_html.xpath(goodjobs_xp)[0].text_content()

engaged_xp = '//*[@id="rbnSection323SECTION-526"]/table/tbody/tr[3]/td[2]'
engaged = gallup_html.xpath(engaged_xp)[0].text_content()

econfidence_xp = '//*[@id="rbnSection323SECTION-526"]/table/tbody/tr[4]/td[2]'
econfidence = gallup_html.xpath(econfidence_xp)[0].text_content()

consumerspend_xp = '//*[@id="rbnSection323SECTION-526"]/table/tbody/tr[5]/td[2]'
consumerspend = gallup_html.xpath(consumerspend_xp)[0].text_content()

trumpapprove_xp = '//*[@id="rbnSection323SECTION-526"]/table/tbody/tr[6]/td[2]'
trumpapprove = gallup_html.xpath(trumpapprove_xp)[0].text_content()

def percent_to_number(percent):
    return float(percent.strip('%'))/100
def dollar_to_number(dollar):
    return float(dollar.strip('$'))


unemployment = (percent_to_number(unemployment))
goodjobs = percent_to_number(goodjobs)
econfidence = float(econfidence)
engaged = percent_to_number(engaged)
consumerspend = dollar_to_number(consumerspend)
trumpapprove = percent_to_number(trumpapprove)

import MySQLdb as mdb
import sys

con = mdb.connect(host = 'localhost', 
                  user = 'root', 
                  passwd = 'dwdstudent2015', 
                  charset='utf8', use_unicode=True);

from datetime import date, datetime, timedelta
timestamp = datetime.now()

cursor = con.cursor()
insert_query = '''INSERT INTO MaxDavish_GallupDailyData.GallupDailyData
                    (timestamp,
                    unemployment,
                    goodjobs,
                    engaged,
                    econfidence,
                    consumerspend,
                    trumpapprove)
                    VALUES (%s, %s, %s, %s, %s, %s, %s);'''
parameters = (timestamp, unemployment, goodjobs, engaged, econfidence, consumerspend, trumpapprove)
cursor.execute(insert_query,parameters)
con.commit()
cursor.close()