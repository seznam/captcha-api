#!/usr/bin/python
#
# FILE $Id:
#
# DESCRIPTION:
# Simple captcha interface
#
# AUTHOR
# Karotka <zdenek.philipp@firma.seznam.cz>
#
# Licencováno pod MIT Licencí
#
# © 2008 Seznam.cz, a.s.
# 
# Tímto se uděluje bezúplatná nevýhradní licence k oprávnění užívat Software,
# časově i místně neomezená, v souladu s příslušnými ustanoveními autorského zákona.
#
# Nabyvatel/uživatel, který obdržel kopii tohoto softwaru a další přidružené
# soubory (dále jen „software“) je oprávněn k nakládání se softwarem bez
# jakýchkoli omezení, včetně bez omezení práva software užívat, pořizovat si
# z něj kopie, měnit, sloučit, šířit, poskytovat zcela nebo zčásti třetí osobě
# (podlicence) či prodávat jeho kopie, za následujících podmínek:
#
# - výše uvedené licenční ujednání musí být uvedeno na všech kopiích nebo
# podstatných součástech Softwaru.
#
# - software je poskytován tak jak stojí a leží, tzn. autor neodpovídá
# za jeho vady, jakož i možné následky, ledaže věc nemá vlastnost, o níž autor
# prohlásí, že ji má, nebo kterou si nabyvatel/uživatel výslovně vymínil.
#
#
#
# Licenced under the MIT License
#
# Copyright (c) 2008 Seznam.cz, a.s.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# DATE 25.06.2007
#
# Example:
#
# import captcha
#
# address = "http://captcha.seznam.cz/RPC2"
# # create captcha object RPC or HTTP if you want
# c = captcha.CaptchaRPC(address = address)
# # or
# # c = captcha.CaptchaHTTP(address = address)
#
# hash = c.create()
#
# #
# # show picture whith code in the client browser
# # <img src="http://captcha.server.cz/captcha.getImage?hash=hash" />
# # client sent the code and server set the value
# # into the code variable
# #
#
# if c.check(hash, code):
#     # OK code
# else :
#     # false code
# #endif
#
# Good luck, and have fun!
#
import os

RPC_ADDRESS  = "http://captcha.seznam.cz:3410"
HTTP_ADDRESS = "http://captcha.seznam.cz"
HTTP_PROXY   = ""

class CaptchaUnexpectedResponse(Exception):

    def __repr__(self):
        return ("Unexpected response while call method <%d, %s>" %
                (self.status, self.statusMessage))
    #enddef

#endclass

class RPCCaptchaUnexpectedResponse(CaptchaUnexpectedResponse):

    def __init__(self, result):
        self.status        = result.get("status", "???")
        self.statusMessage = result.get("statusMessage", "???")
    #enddef

#endclass

class HTTPCaptchaUnexpectedResponse(CaptchaUnexpectedResponse):

    def __init__(self, htcode, errmsg):
        self.status        = htcode
        self.statusMessage = errmsg
    #enddef

#endclass


class CaptchaRPC:

    def __init__(self, *args, **kwargs):
        """
        Constructor create base Captcha object and make
        XML-RPC or FastRPC connection if module is installed.
        """
        self.__connectTimeout = kwargs.get("connectTimeout", 5000)
        self.__readTimeout    = kwargs.get("readTimeout", 5000)
        self.__writeTimeout   = kwargs.get("writeTimeout", 5000)
        self.__keepAlive      = kwargs.get("keepAlive", 0)
        self.__useBinary      = kwargs.get("useBinary", 1)
        self.__address        = kwargs.get("address", RPC_ADDRESS)
        self.__proxyVia       = kwargs.get("proxy", HTTP_PROXY)

        # set proxy for xmlrpclib
        os.environ["HTTP_PROXY"] = self.__proxyVia

        # xmlrpc or fastrpc proxy connection
        self.__proxy = None
        try:
            import fastrpc as rpc
            self.__createProxy(rpc, True)
        except ImportError, e:
            import xmlrpclib as rpc
            self.__createProxy(rpc)
        #endtry
    #enddef

    def create(self):
        """
        Create hash
        """
        result = self.__proxy.captcha.create()
        if result["status"] != 200:
            raise RPCCaptchaUnexpectedResponse(result)
        #endif
        return result["hash"]
    #enddef

    def check(self, hash, code):
        """
        Check if hash and code is valid
        """
        result = self.__proxy.captcha.check(hash, code)
        if result["status"] not in (200, 403, 404) :
            raise RPCCaptchaUnexpectedResponse(result)
        #endif
        if result["status"] == 200:
            return True
        else :
            return False
        #endif
    #enddef

    def __createProxy(self, rpc, fastRpc = False):
        """
        Create XML-RPC or FastRPC proxy
        """
        if fastRpc :
            # create ServerProxy instance
            self.__proxy = rpc.ServerProxy(
                self.__address,
                proxyVia       = self.__proxyVia,
                connectTimeout = self.__connectTimeout,
                readTimeout    = self.__readTimeout,
                writeTimeout   = self.__writeTimeout,
                keepAlive      = self.__keepAlive,
                useBinary      = self.__useBinary )
        else :
            # create ServerProxy instance
            self.__proxy = rpc.ServerProxy(self.__address)
        #endif

    #enddef

#endclass


class CaptchaHTTP:

    def __init__(self, *args, **kwargs):
        """
        Constructor create base Captcha object and make
        XML-RPC or FastRPC connection if module is instaled.
        """
        self.__address = kwargs.get("address", HTTP_ADDRESS)
    #enddef

    def create(self):
        """
        Create hash
        """
        htcode, content = self.__makeRequest(HTTP_ADDRESS, "/captcha.create")
        return content
    #enddef

    def check(self, hash, code):
        """
        Check if hash and code is valid
        """
        htcode, content = self.__makeRequest(HTTP_ADDRESS,
            "/captcha.check?hash=%s&code=%s" % (hash, code))
        if int(htcode) == 200:
            return True
        else :
            return False
        #endif
    #enddef

    def __makeRequest(self, url, path):

        from httplib import HTTP

        http = HTTP(HTTP_PROXY or url.replace("http://", ""))
        http.putrequest("GET", url + path)
        http.putheader("Accept", "text/plain")
        http.endheaders()
        htcode, errmsg, headers = http.getreply()

        if htcode not in (200, 403, 404):
            raise HTTPCaptachaUnexpectedResponse(htcode, errmsg)
        #endif

        file = http.getfile()
        content = file.read()
        file.close()

        return htcode, content
    #enddef

#endclass
