import http.client
import urllib.parse
import ssl
import lxml.html
import sys

from errbot import BotPlugin, botcmd, arg_botcmd, webhook


class Michmuni(BotPlugin):
    """
    Search for Michigan municipal unit, given an address.
    """

    def _fetch_municipality(self, address):
        params = urllib.parse.urlencode({'Address': str(address)})
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        conn = http.client.HTTPSConnection("mvic.sos.state.mi.us", 443, context=ssl._create_unverified_context())
        conn.request("POST", "/Voter/SearchByAddress", params, headers)
        res = conn.getresponse()
        return self._parse_municipality(res.read())

    # Parse a municipality from an html fragment
    def _parse_municipality(self, htmlstr):
        html = lxml.html.fromstring(htmlstr)
        municipality = html.find_class('ccd-page-heading')[1].text
        return municipality.strip()

    # Passing split_args_with=None will cause arguments to be split on any kind
    # of whitespace, just like Python's split() does
    @botcmd(split_args_with="~")
    def muni(self, message, args):
        """A command which returns a Michigan municipality, given an address"""
        if args[0] == "":
            return "Please enter an address as part of your request, thanks!"
        if len(args) > 1:
            return "This doesn't look like a properly formatted address. Please check the address and try again."
        
        res = self._fetch_municipality(args[0])
        if res == "Search for your voter information":
            return """I'm sorry, I can't find a municipality that matches that address.


If you are sure that you typed it correctly, it might not be a valid address in Michigan. I'm not overly sophisticated, so you might want to try another method of verification."""
        if res.startswith('City') or res.startswith('Village'):
            res = "the " + res
        return f"That address lies within {res}"
