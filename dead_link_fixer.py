import xml.etree.cElementTree as ET
import re
import json
import urllib
import urllib2

#----------------------------------------------------------------------
def parseXML(xml_file):
    """
    Parse XML with ElementTree
    """
    tree = ET.ElementTree(file=xml_file)
    root = tree.getroot()
    urls = root.getchildren()
    for item in urls:
        parseValid(item.find('valid'), item) 
        # parseWarnings(item.find("warnings"), item)

def parseValid(valid, item):
    results = [
        '200 OK',
        'syntax OK'
    ]

    if not valid.get('result') in results:
        url = item.find("url").text
        if url.find('archive.org') > -1:
            return
        match = re.search(r'(\d+/\d+/\d+)', item.find("parent").text)
        timestamp = match.group(1).replace('/', '')
        archive = findArchive(url, timestamp)
        if archive:
            generateReplaceCommand(url, archive)

def findArchive(url, timestamp):
    if url:
        escapedUrl = urllib.quote_plus(url)
        lookup = 'http://archive.org/wayback/available?url=%s&timestamp=%s' % (escapedUrl, timestamp)

        req = urllib2.Request(lookup)
        resp = urllib2.urlopen(req)
        raw = resp.read()
        data = json.loads(raw)     

        snapshots = data['archived_snapshots']
        archive = ''
        if 'closest' in snapshots:
            closest = snapshots['closest']
            archive = closest['url']
        return archive

def parseWarnings(warnings, item):
    if warnings:
        for warning in warnings:
            parseTags(warning.get('tag'), item)

def parseTags(tag, item):
    if tag:
        if tag == 'http-moved-permanent':
            url = item.find("url").text
            realurl = item.find('realurl').text
            generateReplaceCommand(url, realurl)

def generateReplaceCommand(url, realurl):
    if url != realurl:
        escapedUrl = url.replace("/", "\/")
        escapedRealurl = realurl.replace("/", "\/")
        print 'find ./ -type f -exec sed -i \'s/%s/%s/g\' {} \;' % (escapedUrl, escapedRealurl)
 
#----------------------------------------------------------------------
if __name__ == "__main__":
    parseXML("linkchecker-out.xml")
