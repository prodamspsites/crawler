# -*- coding: utf-8 -*-
import json
import requests

from bs4 import BeautifulSoup
from datetime import datetime


class Crawler(object):

    def generate_sql(self, database, table, data):
        sql = "UNLOCK TABLES;"
        sql += "\nCREATE DATABASE IF NOT EXISTS {};".format(database)
        sql += "\nUSE {};".format(database)
        sql += "\nDROP TABLE IF EXISTS `{}`;\nCREATE TABLE `{}` (".format(table, table)
        sql += "`id` int(11) NOT NULL AUTO_INCREMENT, "

        for key, value in data[0].iteritems():
            sql += "`{}` longtext, ".format(key)
        sql += "PRIMARY KEY(`id`)) ENGINE=InnoDB DEFAULT CHARSET=utf8;"
        sql += "\nLOCK TABLES `{}` WRITE;".format(table)

        if len(data) > 1:
            sql += "\nINSERT INTO `{}` VALUES ".format(table)
            for i, item in enumerate(data):
                sql += "({}, ".format(i+1)
                for ii, (key, value) in enumerate(item.iteritems()):
                    if ii == len(item)-1:
                        sql += "'{}'".format(value)
                    else:
                        sql += "'{}',".format(value)
                if i == len(data)-1:
                    sql += ");"
                else:
                    sql += "),"

        sql += "\nUNLOCK TABLES;"
        file_name = '/tmp/crawler-sql-{}-{}.sql'.format(table, datetime.now().strftime('%d-%m-%Y_%H-%M'))
        with open(file_name, 'w') as sql_file:
            sql_file.write(sql)
            sql_file.close()
        return file_name

    def get(self, url, headers=None):
        """
        Makes a GET request that returns text/html and json results or raise an exception with request status code.
        """
        response = requests.get(url, headers)
        if response.status_code == 200:
            return BeautifulSoup(response.text, 'html.parser')

        raise Exception('GET request not found! HTTP Status Code is {}'.format(response.status_code))

    def load_data_file(self, data_file):
        """
        Opens data file type like json or txt and return a python object.
        """
        with open('{}'.format(data_file)) as data:
                return json.load(data)

    def post(self, url, data=None, headers=None, session=False):
        """
        Makes a POST request with optional requests.Session param that returns tex/html and json results or raise an
        exception with request status code.
        """
        request = requests
        if session:
            request = request.Session()
        response = request.post(url, data=data, headers=headers)

        if response.status_code == 200:
            return response

        raise Exception('POST request not found! HTTP Status Code is {}'.format(response.status_code))

    def post_form(self, url=None, header=None, data=None, data_file=None, links=None, form=None, method=None):
        """
        Opens url to check some links/forms to proceed to a new step, find the html form ID to post data/data_file on
        this form.
        """

        if not data and data_file:
            data = self.load_data_file(data_file)

        if not links:
            links = []

        for link in links:
            while True:
                html = self.get(url)
                if html.find(id=form):
                    break

                if html.find(id=link):
                    url = html.find(id=link).get('href')
                    continue
                break

        for item in data:
            result = self.post(url, headers=header, data=item, session=True)
            print(BeautifulSoup(result.text, 'html.parser').prettify())
