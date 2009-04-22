# -*- coding: utf-8 -*-

# for creating WSSE header
import time, random, datetime, base64, sha

from xml.dom import minidom
from google.appengine.api import urlfetch

class HatenaBookmarkClient():
  post_uri = 'http://b.hatena.ne.jp/atom/post'

  def __init__(self, username, password):
    self.username = username
    self.password = password
    self.wsse_token = None

  def createBookmarkPayload(self, url='', title=u'', summary=u''):
    impl = minidom.getDOMImplementation()
    doc = impl.createDocument(None, 'entry', None)
    root = doc.documentElement
    root.attributes['xmlns'] = 'http://purl.org/atom/ns#'
    if url:
      elem = doc.createElement('link')
      elem.setAttribute('rel', 'related')
      elem.setAttribute('type', 'text/html')
      elem.setAttribute('href', url)
      root.appendChild(elem)
    if title:
      elem = doc.createElement('title')
      elem.appendChild(doc.createTextNode(title))
      root.appendChild(elem)
    if summary:
      elem = doc.createElement('summary')
      elem.setAttribute('type', 'text/plain')
      elem.appendChild(doc.createTextNode(summary))
      root.appendChild(elem)
    payload = doc.toxml(encoding='utf-8')
    doc.unlink()
    return payload

  def createWSSEToken(self):
    nonce = sha.sha(str(time.time() + random.random())).digest()
    nonce_enc = base64.encodestring(nonce).strip()
    created = datetime.datetime.now().isoformat() + 'Z'
    password_digest = sha.sha(nonce + created + self.password).digest()
    password_digest_enc = base64.encodestring(password_digest).strip()
    self.wsse_token = 'UsernameToken Username="%s", PasswordDigest="%s", Nonce="%s", Created="%s"' % (self.username, password_digest_enc, nonce_enc, created)

  def makeRequest(self, url, payload='', method='GET', content_type='text/xml'):
    self.createWSSEToken()
    res = urlfetch.fetch(
      url,
      payload = payload,
      method = method,
      headers = {
        'X-WSSE': self.wsse_token,
        'Content-Type': content_type,
        'Authorization': 'WSSE profile="UsernameToken"',
        'User-Agent': 'Python-HatenaBookmarkClient/1.0'
        }
      )
    if (res.status_code != 200) and (res.status_code != 201):
      raise Exception('Failed to access Hatena Bookmark API')
    return res

  def postBookmark(self, url, summary=u''):
    payload = self.createBookmarkPayload(url=url, summary=summary)
    res = self.makeRequest(self.post_uri, method='POST', payload=payload)

    doc = minidom.parseString(res.content.lstrip())
    entry = doc.getElementsByTagName('entry').item(0)
    links = entry.getElementsByTagName('link')
    for link in links:
      if link.getAttribute('rel') == 'service.edit':
        return link.getAttribute('href')

  def getBookmark(self, edit_uri):
    res = self.makeRequest(edit_uri, method='GET')
    """ do something here """
    return res.content

  def updateBookmark(self, edit_uri, title=u'', summary=u''):
    if len(title) == 0 and len(summary) == 0:
      raise Exception('Both of title and summary are not defined')
    payload = self.createBookmarkPayload(title=title, summary=summary)
    res = self.makeRequest(edit_uri, method='PUT', payload=payload)
    """ do something here """
    return res.content

  def deleteBookmark(self, edit_uri):
    res = self.makeRequest(edit_uri, method='DELETE')
    """ do something here """
    return res.content
