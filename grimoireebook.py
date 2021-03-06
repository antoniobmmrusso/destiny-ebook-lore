#!/usr/bin/env python
import requests
import urlparse
import jsonpath_rw
import urllib
import urllib2
import os
import collections
import sys
import logging
import re
import hashlib
from PIL import Image
from sets import Set
from ebooklib import epub

DEFAULT_PAGE_STYLE = '''
	cardname {
		display: block;
		text-align: center;
		font-size:150%;
	}
	cardimage {
		float: left;
		margin-right: 5%;
		width: 40%;
		height: 40%;
	}
	cardintro {
		display: block;
		padding: 5%;
	}
	carddescription {}
	container {
		width: 100%;
		clear: both;
	}
'''

DEFAULT_IMAGE_FOLDER = os.path.join(os.path.expanduser('~'), '.destinyLore/cache/images')

DEFAULT_BOOK_FILE = os.path.join(os.path.expanduser('~'), '.destinyLore/destinyGrimoire.epub')

def generateGrimoireEbook(apiKey):
	createGrimoireEpub(loadDestinyGrimoireDefinition(apiKey))

def loadDestinyGrimoireDefinition(apiKey):
	return getDestinyGrimoireDefinitionFromJson(getDestinyGrimoireFromBungie(apiKey))

def createGrimoireEpub(destinyGrimoireDefinition, book=epub.EpubBook()):
	book.set_identifier('destinyGrimoire')
	book.set_title('Destiny Grimoire')
	book.set_language('en')
	book.add_author('Bungie')
	book.set_cover("cover.jpg", open('resources/cover.jpg', 'rb').read())

	book.add_item(epub.EpubItem(uid="style_default", file_name="style/default.css", media_type="text/css", content=DEFAULT_PAGE_STYLE))

	dowloadGrimoireImages(destinyGrimoireDefinition)
	book.toc = addThemeSetsToEbook(book, destinyGrimoireDefinition)

	book.add_item(epub.EpubNcx())
	book.add_item(epub.EpubNav())

	epub.write_epub(DEFAULT_BOOK_FILE, book)

def getDestinyGrimoireFromBungie(apiKey):
	logging.debug('Dowloading Destiny Grimoire from Bungie')
	if apiKey is None or not apiKey:
			raise DestinyContentAPIClientError(DestinyContentAPIClientError.NO_API_KEY_PROVIDED_ERROR_MSG)
	return requests.get('http://www.bungie.net/Platform/Destiny/Vanguard/Grimoire/Definition/', headers={'X-API-Key': apiKey}).json()

def getDestinyGrimoireDefinitionFromJson(grimoireJson):
	logging.debug('Extracting grimoire definitions from raw JSON: %s' % grimoireJson)
	grimoireDefinition = { "themes" : []}

	for theme in grimoireJson["Response"]["themeCollection"]:
		themeToAdd = { "themeName" : theme["themeName"] , "pages" : [] }
		for page in theme["pageCollection"]:
			pageToAdd = { "pageName" : page["pageName"], "cards" : [] }
			for card in page["cardCollection"]:
				logging.debug('Processing grimoire card data: %s' % card)
				pageToAdd["cards"].append(
					{ "cardName" : card["cardName"], 
					"cardIntro" : card.get("cardIntro", u""),
					"cardDescription" : card.get("cardDescription", u""),
					"hash": hashlib.sha1('%s.%s.%s' % (theme["themeName"], page["pageName"], card["cardName"])).hexdigest(),
					"image": { "sourceImage" : "http://www.bungie.net/" + card["highResolution"]["image"]["sheetPath"],
								"regionXStart" : card["highResolution"]["image"]["rect"]["x"],
								"regionYStart" : card["highResolution"]["image"]["rect"]["y"],
								"regionHeight" : card["highResolution"]["image"]["rect"]["height"],
								"regionWidth" : card["highResolution"]["image"]["rect"]["width"]}})
			themeToAdd["pages"].append(pageToAdd)
		grimoireDefinition["themes"].append(themeToAdd)
		
	return grimoireDefinition

def dowloadGrimoireImages(grimoireDefinition):
	logging.info('Dowloading Grimoire images')
	jsonpath_expr = jsonpath_rw.parse('themes[*].pages[*].cards[*].image.sourceImage')

	imagesToDownload = Set([match.value for match in jsonpath_expr.find(grimoireDefinition)])

	if not os.path.exists(DEFAULT_IMAGE_FOLDER):
		os.makedirs(DEFAULT_IMAGE_FOLDER)

	for imageURL in imagesToDownload:
		logging.debug("Downloading %s" % imageURL)
		urllib.urlretrieve(imageURL, os.path.join(DEFAULT_IMAGE_FOLDER, urlparse.urlsplit(imageURL).path.split('/')[-1]))

def generateCardImageFromImageSheet(imageBaseFileName, sheetImagePath, localImageFolder, dimensions_tuple):
	generatedImagePath = os.path.join(localImageFolder, '%s%s' % (imageBaseFileName, os.path.splitext(sheetImagePath)[1]))

	sheetImage = Image.open(sheetImagePath)
	cardImage = sheetImage.crop((dimensions_tuple[0], dimensions_tuple[1], dimensions_tuple[0] + dimensions_tuple[2], dimensions_tuple[1] + dimensions_tuple[3]))
	cardImage.save(generatedImagePath, optimize=True)

	return generatedImagePath

def generateGrimoirePageContent(pageData, pageImagePath):
	return u'''<cardname">%s</cardname>
			   <cardintro>%s</cardintro>
			   <container>
				<cardimage><img src="%s"/></cardimage>
				<carddescription">%s</carddescription>
			   </container>''' % ( pageData["cardName"], pageData["cardIntro"], pageImagePath, pageData["cardDescription"] )

def generateGrimoirePageImage(cardFileName, imageData, imagesFolder):
	imageBaseFileName = '%s_img' % (cardFileName)
	imagePath = generateCardImageFromImageSheet(imageBaseFileName, os.path.join(imagesFolder, os.path.basename(imageData["sourceImage"])),imagesFolder, (imageData["regionXStart"], imageData["regionYStart"], imageData["regionWidth"], imageData["regionHeight"]))
	epubImageFile = os.path.join('images', os.path.basename(imagePath))
	return epub.EpubItem(uid=imageBaseFileName, file_name=epubImageFile, content=open(imagePath, 'rb').read())

def createGrimoireCardPage(cardData, bookPageCSS):
	fileName = '%s-%s' % (cardData["hash"], re.sub(r"[^\d\w]","_", cardData["cardName"]))
	bookPage = epub.EpubHtml(title=cardData["cardName"], file_name='%s.%s' % (fileName, 'xhtml'), lang='en', content="")
	bookPage.add_item(bookPageCSS)
	pageImage = generateGrimoirePageImage(fileName, cardData["image"], DEFAULT_IMAGE_FOLDER)
	bookPage.content = generateGrimoirePageContent(cardData, pageImage.file_name)
	return collections.namedtuple('GrimoirePage', ['page', 'image'])(page=bookPage, image=pageImage)

def addPageItemsToEbook(ebook, pageData):
	pageCards = ()
	for cardData in pageData['cards']:
		cardPageData = createGrimoireCardPage(cardData, epub.EpubItem(uid="style_default", file_name="style/default.css", media_type="text/css", content=DEFAULT_PAGE_STYLE))
		ebook.add_item(cardPageData.page)
		ebook.add_item(cardPageData.image)
		ebook.spine.append(cardPageData.page)
		pageCards = pageCards + (cardPageData.page,)
	return pageCards

def addThemePagesToEbook(ebook, themeData):
	themePages = ()
	for pageData in themeData['pages']:
		themePages = themePages + ((epub.Section(pageData['pageName']), addPageItemsToEbook(ebook, pageData)),)
	return themePages

def addThemeSetsToEbook(ebook, grimoireData):
	themes = ()
	for themeData in grimoireData['themes']:
		themes = themes + ((epub.Section(themeData['themeName']), addThemePagesToEbook(ebook, themeData)),)
	return themes

class DestinyContentAPIClientError(Exception):
	NO_API_KEY_PROVIDED_ERROR_MSG = "No API key provided. One is required to refresh the content cache."

	def __init__(self, value):
		self.value = value

	def __str__(self):
		return self.value

if __name__ == "__main__":
	logging.basicConfig(level=logging.DEBUG)
	generateGrimoireEbook(sys.argv[1])