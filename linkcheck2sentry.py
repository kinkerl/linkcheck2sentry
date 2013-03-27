# -*- coding: utf-8 -*-
#
# run the linkchecker and send output to sentry
#

import subprocess
import xml.etree.ElementTree as ET
import logging

class linkcheck2sentry:
    def __init__(self, domain, DSN):
        from raven.handlers.logging import SentryHandler
        from raven.conf import setup_logging

        self.domain = domain
        self.dsn = DSN
        
        handler = SentryHandler(self.dsn)
        setup_logging(handler)
        self.logger = logging.getLogger('linkcheck')


    def run(self):
        checkurl = ["linkchecker", self.domain, "--output=XML", "--no-status"]
        process = subprocess.Popen(checkurl, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        response =  process.stdout.read()
        root = ET.fromstring(response)
        for urldata in root:
            extra = {
                'url' : urldata.find("url").text,
                'text' : getattr(urldata.find("name"),'text', ''),
                'parent' : getattr(urldata.find("parent"), 'text', ''),
                'realurl' : getattr(urldata.find("realurl"), 'text', ''),
                'response' : urldata.find("valid").attrib.get('result'),
            } 
            if urldata.findall("infos"):
                extra_info = ''
                for infos in urldata.findall("infos"):
                    for info in infos:
                        extra_info += info.text
                extra['infos'] = extra_info
            if urldata.findall("warnings"):
                extra_warning = ''
                for warnings in urldata.findall("warnings"):
                    for warning in warnings:
                        extra_warning += warning.text
                extra['warnings'] = extra_warning
            if 'warnings' in extra:
                self.logger.warn(urldata.find("url").text, extra=extra)
            else:
                self.logger.error(urldata.find("url").text, extra=extra)
