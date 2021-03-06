import pytest
import mock
import httpretty
import json
import grimoireebook
import collections
import os
import string
import hashlib
from PIL import Image
from grimoireebook import DestinyContentAPIClientError
from ebooklib import epub
from mock import call

__dummyGrimoireDefinition__ = {'themes': [] }
__testApiKey__ = 'testApiKey'

@mock.patch('grimoireebook.loadDestinyGrimoireDefinition', autospec = True)
@mock.patch('grimoireebook.createGrimoireEpub', autospec = True)
def test_shouldTriggerGrimoireEbookGenerationWithDefaultValues(mock_createGrimoireEpub, mock_loadDestinyGrimoireDefinition):
	mock_loadDestinyGrimoireDefinition.return_value = __dummyGrimoireDefinition__
	
	grimoireebook.generateGrimoireEbook(__testApiKey__)

	mock_loadDestinyGrimoireDefinition.assert_called_once_with(__testApiKey__)
	mock_createGrimoireEpub.assert_called_once_with(__dummyGrimoireDefinition__)

@mock.patch('grimoireebook.getDestinyGrimoireFromBungie', autospec = True)
@mock.patch('grimoireebook.getDestinyGrimoireDefinitionFromJson', autospec = True)
def test_shouldLoadDestinyGrimoireDefinition(mock_getDestinyGrimoireDefinitionFromJson, mock_getDestinyGrimoireFromBungie):
	api_key = "apiKey"
	mock_getDestinyGrimoireFromBungie.return_value = __dummyGrimoireDefinition__
	mock_getDestinyGrimoireDefinitionFromJson.return_value = __dummyGrimoireDefinition__

	grimoireDefinition = grimoireebook.loadDestinyGrimoireDefinition(__testApiKey__)

	mock_getDestinyGrimoireFromBungie.assert_called_once_with(__testApiKey__)
	mock_getDestinyGrimoireDefinitionFromJson.assert_called_once_with(__dummyGrimoireDefinition__)

	assert grimoireDefinition == __dummyGrimoireDefinition__

def test_grimoireRetrievalFromBungieShouldTriggerExceptionIfNoAPIKeyIsGiven():
	with pytest.raises(DestinyContentAPIClientError) as expectedException:
		grimoireebook.getDestinyGrimoireFromBungie(None)

	assert str(expectedException.value) == DestinyContentAPIClientError.NO_API_KEY_PROVIDED_ERROR_MSG

	with pytest.raises(DestinyContentAPIClientError) as expectedException:
		grimoireebook.getDestinyGrimoireFromBungie("")

	assert str(expectedException.value) == DestinyContentAPIClientError.NO_API_KEY_PROVIDED_ERROR_MSG

@httpretty.activate
def test_shouldRetrieveGrimoireDataFromBungie():
	httpretty.register_uri(httpretty.GET, 
					'http://www.bungie.net/Platform/Destiny/Vanguard/Grimoire/Definition/', 
					body=json.dumps(__dummyGrimoireDefinition__, ensure_ascii=False, encoding='utf8'),
					content_type='application/json',
					status=200)
	retrievedGrimoire = grimoireebook.getDestinyGrimoireFromBungie(__testApiKey__)

	assert httpretty.last_request().headers['X-API-Key'] == __testApiKey__
	assert retrievedGrimoire == __dummyGrimoireDefinition__

def generateExpectedCardHash(themeName, pageName, cardName):
	return hashlib.sha1('%s.%s.%s' % (themeName, pageName, cardName)).hexdigest()

def test_shouldExtractDestinyGrimoireDefinitionFromJsonData():
	testGrimoire = '''
		{
		  "Response": {
		    "themeCollection": [
		      {
		        "themeId": "1",
		        "themeName": "theme_1",
		        "normalResolution": {
		          "image": {
		            "rect": {
		              "x": 0,
		              "y": 0,
		              "height": 10,
		              "width": 11
		            },
		            "sheetPath": "images/themeSet01_Normal.jpg",
		            "sheetSize": {
		              "x": 0,
		              "y": 0,
		              "height": 100,
		              "width": 101
		            }
		          },
		          "smallImage": {
		            "rect": {
		              "x": 0,
		              "y": 0,
		              "height": 12,
		              "width": 13
		            },
		            "sheetPath": "images/themeSet01_NormalSmall.jpg",
		            "sheetSize": {
		              "x": 0,
		              "y": 0,
		              "height": 102,
		              "width": 103
		            }
		          }
		        },
		        "highResolution": {
		          "image": {
		            "rect": {
		              "x": 0,
		              "y": 0,
		              "height": 14,
		              "width": 15
		            },
		            "sheetPath": "images/themeSet01_High.jpg",
		            "sheetSize": {
		              "x": 0,
		              "y": 0,
		              "height": 104,
		              "width": 105
		            }
		          },
		          "smallImage": {
		            "rect": {
		              "x": 0,
		              "y": 0,
		              "height": 16,
		              "width": 17
		            },
		            "sheetPath": "images/themeSet01_HighSmall.jpg",
		            "sheetSize": {
		              "x": 0,
		              "y": 0,
		              "height": 106,
		              "width": 107
		            }
		          }
		        },
		        "pageCollection": [
		          {
		            "pageId": "1.1",
		            "pageName": "page_1.1",
		            "normalResolution": {
		              "image": {
		                "rect": {
		                  "x": 0,
		                  "y": 0,
		                  "height": 18,
		                  "width": 19
		                },
		                "sheetPath": "images/pageSet01_Normal.jpg",
		                "sheetSize": {
		                  "x": 0,
		                  "y": 0,
		                  "height": 108,
		                  "width": 109
		                }
		              },
		              "smallImage": {
		                "rect": {
		                  "x": 0,
		                  "y": 0,
		                  "height": 20,
		                  "width": 21
		                },
		                "sheetPath": "images/pageSet01_NormalSmall.jpg",
		                "sheetSize": {
		                  "x": 0,
		                  "y": 0,
		                  "height": 110,
		                  "width": 111
		                }
		              }
		            },
		            "highResolution": {
		              "image": {
		                "rect": {
		                  "x": 0,
		                  "y": 0,
		                  "height": 22,
		                  "width": 23
		                },
		                "sheetPath": "images/pageSet01_High.jpg",
		                "sheetSize": {
		                  "x": 0,
		                  "y": 0,
		                  "height": 112,
		                  "width": 113
		                }
		              },
		              "smallImage": {
		                "rect": {
		                  "x": 0,
		                  "y": 0,
		                  "height": 24,
		                  "width": 25
		                },
		                "sheetPath": "images/pageSet01_HighSmall.jpg",
		                "sheetSize": {
		                  "x": 0,
		                  "y": 0,
		                  "height": 114,
		                  "width": 115
		                }
		              }
		            },
		            "cardCollection": [
		              {
		                "cardId": 1,
		                "cardName": "card_1.1.1",
		                "cardIntro": "cardIntro_1.1.1",
		                "cardDescription": "cardDescription_1.1.1",
		                "unlockHowToText": "Unlock this card by playing Destiny.",
		                "rarity": 1,
		                "unlockFlagHash": 0,
		                "points": 0,
		                "normalResolution": {
		                  "image": {
		                    "rect": {
		                      "x": 0,
		                      "y": 0,
		                      "height": 26,
		                      "width": 27
		                    },
		                    "sheetPath": "images/cardSet01_Normal.jpg",
		                    "sheetSize": {
		                      "x": 0,
		                      "y": 0,
		                      "height": 116,
		                      "width": 117
		                    }
		                  },
		                  "smallImage": {
		                    "rect": {
		                      "x": 0,
		                      "y": 0,
		                      "height": 28,
		                      "width": 29
		                    },
		                    "sheetPath": "images/cardSet01_NormalSmall.jpg",
		                    "sheetSize": {
		                      "x": 0,
		                      "y": 0,
		                      "height": 118,
		                      "width": 119
		                    }
		                  }
		                },
		                "highResolution": {
		                  "image": {
		                    "rect": {
		                      "x": 0,
		                      "y": 0,
		                      "height": 30,
		                      "width": 31
		                    },
		                    "sheetPath": "images/cardSet01_High.jpg",
		                    "sheetSize": {
		                      "x": 0,
		                      "y": 0,
		                      "height": 120,
		                      "width": 121
		                    }
		                  },
		                  "smallImage": {
		                    "rect": {
		                      "x": 0,
		                      "y": 0,
		                      "height": 32,
		                      "width": 33
		                    },
		                    "sheetPath": "images/cardSet01_HighSmall.jpg",
		                    "sheetSize": {
		                      "x": 0,
		                      "y": 0,
		                      "height": 122,
		                      "width": 123
		                    }
		                  }
		                }
		              },
		              {
		                "cardId": 2,
		                "cardName": "card_1.1.2",
		                "cardIntro": "cardIntro_1.1.2",
		                "cardDescription": "cardDescription_1.1.2",
		                "unlockHowToText": "Unlock this card by playing Destiny.",
		                "rarity": 1,
		                "unlockFlagHash": 0,
		                "points": 0,
		                "normalResolution": {
		                  "image": {
		                    "rect": {
		                      "x": 32,
		                      "y": 33,
		                      "height": 34,
		                      "width": 35
		                    },
		                    "sheetPath": "images/cardSet01_Normal.jpg",
		                    "sheetSize": {
		                      "x": 0,
		                      "y": 0,
		                      "height": 124,
		                      "width": 125
		                    }
		                  },
		                  "smallImage": {
		                    "rect": {
		                      "x": 34,
		                      "y": 35,
		                      "height": 36,
		                      "width": 37
		                    },
		                    "sheetPath": "images/cardSet01_NormalSmall.jpg",
		                    "sheetSize": {
		                      "x": 0,
		                      "y": 0,
		                      "height": 126,
		                      "width": 127
		                    }
		                  }
		                },
		                "highResolution": {
		                  "image": {
		                    "rect": {
		                      "x": 36,
		                      "y": 37,
		                      "height": 38,
		                      "width": 39
		                    },
		                    "sheetPath": "images/cardSet01_High.jpg",
		                    "sheetSize": {
		                      "x": 0,
		                      "y": 0,
		                      "height": 128,
		                      "width": 129
		                    }
		                  },
		                  "smallImage": {
		                    "rect": {
		                      "x": 38,
		                      "y": 39,
		                      "height": 40,
		                      "width": 41
		                    },
		                    "sheetPath": "images/cardSet01_HighSmall.jpg",
		                    "sheetSize": {
		                      "x": 0,
		                      "y": 0,
		                      "height": 130,
		                      "width": 131
		                    }
		                  }
		                }
		              }
		            ]
		          },
		          {
		            "pageId": "1.2",
		            "pageName": "page_1.2",
		            "normalResolution": {
		              "image": {
		                "rect": {
		                  "x": 40,
		                  "y": 41,
		                  "height": 42,
		                  "width": 43
		                },
		                "sheetPath": "images/pageSet01_Normal.jpg",
		                "sheetSize": {
		                  "x": 0,
		                  "y": 0,
		                  "height": 132,
		                  "width": 133
		                }
		              },
		              "smallImage": {
		                "rect": {
		                  "x": 42,
		                  "y": 43,
		                  "height": 44,
		                  "width": 45
		                },
		                "sheetPath": "images/pageSet01_NormalSmall.jpg",
		                "sheetSize": {
		                  "x": 0,
		                  "y": 0,
		                  "height": 134,
		                  "width": 135
		                }
		              }
		            },
		            "highResolution": {
		              "image": {
		                "rect": {
		                  "x": 44,
		                  "y": 45,
		                  "height": 46,
		                  "width": 47
		                },
		                "sheetPath": "images/pageSet01_High.jpg",
		                "sheetSize": {
		                  "x": 0,
		                  "y": 0,
		                  "height": 136,
		                  "width": 137
		                }
		              },
		              "smallImage": {
		                "rect": {
		                  "x": 46,
		                  "y": 47,
		                  "height": 48,
		                  "width": 49
		                },
		                "sheetPath": "images/pageSet01_HighSmall.jpg",
		                "sheetSize": {
		                  "x": 0,
		                  "y": 0,
		                  "height": 138,
		                  "width": 139
		                }
		              }
		            },
		            "cardCollection": [
		              {
		                "cardId": 3,
		                "cardName": "card_1.2.1",
		                "cardIntro": "cardIntro_1.2.1",
		                "cardDescription": "cardDescription_1.2.1",
		                "unlockHowToText": "Unlock this card by playing Destiny.",
		                "rarity": 1,
		                "unlockFlagHash": 0,
		                "points": 0,
		                "normalResolution": {
		                  "image": {
		                    "rect": {
		                      "x": 0,
		                      "y": 0,
		                      "height": 50,
		                      "width": 51
		                    },
		                    "sheetPath": "images/cardSet02_Normal.jpg",
		                    "sheetSize": {
		                      "x": 0,
		                      "y": 0,
		                      "height": 140,
		                      "width": 141
		                    }
		                  },
		                  "smallImage": {
		                    "rect": {
		                      "x": 0,
		                      "y": 0,
		                      "height": 52,
		                      "width": 53
		                    },
		                    "sheetPath": "images/cardSet02_NormalSmall.jpg",
		                    "sheetSize": {
		                      "x": 0,
		                      "y": 0,
		                      "height": 142,
		                      "width": 143
		                    }
		                  }
		                },
		                "highResolution": {
		                  "image": {
		                    "rect": {
		                      "x": 0,
		                      "y": 0,
		                      "height": 54,
		                      "width": 55
		                    },
		                    "sheetPath": "images/cardSet02_High.jpg",
		                    "sheetSize": {
		                      "x": 0,
		                      "y": 0,
		                      "height": 144,
		                      "width": 145
		                    }
		                  },
		                  "smallImage": {
		                    "rect": {
		                      "x": 0,
		                      "y": 0,
		                      "height": 56,
		                      "width": 57
		                    },
		                    "sheetPath": "images/cardSet02_HighSmall.jpg",
		                    "sheetSize": {
		                      "x": 0,
		                      "y": 0,
		                      "height": 146,
		                      "width": 147
		                    }
		                  }
		                }
		              },
		              {
		                "cardId": 4,
		                "cardName": "card_1.2.2",
		                "cardIntro": "cardIntro_1.2.2",
		                "cardDescription": "cardDescription_1.2.2",
		                "unlockHowToText": "Unlock this card by playing Destiny.",
		                "rarity": 1,
		                "unlockFlagHash": 0,
		                "points": 0,
		                "normalResolution": {
		                  "image": {
		                    "rect": {
		                      "x": 56,
		                      "y": 57,
		                      "height": 58,
		                      "width": 59
		                    },
		                    "sheetPath": "images/cardSet02_Normal.jpg",
		                    "sheetSize": {
		                      "x": 0,
		                      "y": 0,
		                      "height": 148,
		                      "width": 149
		                    }
		                  },
		                  "smallImage": {
		                    "rect": {
		                      "x": 58,
		                      "y": 59,
		                      "height": 60,
		                      "width": 61
		                    },
		                    "sheetPath": "images/cardSet02_NormalSmall.jpg",
		                    "sheetSize": {
		                      "x": 0,
		                      "y": 0,
		                      "height": 150,
		                      "width": 151
		                    }
		                  }
		                },
		                "highResolution": {
		                  "image": {
		                    "rect": {
		                      "x": 60,
		                      "y": 61,
		                      "height": 62,
		                      "width": 63
		                    },
		                    "sheetPath": "images/cardSet02_High.jpg",
		                    "sheetSize": {
		                      "x": 0,
		                      "y": 0,
		                      "height": 152,
		                      "width": 153
		                    }
		                  },
		                  "smallImage": {
		                    "rect": {
		                      "x": 62,
		                      "y": 63,
		                      "height": 64,
		                      "width": 65
		                    },
		                    "sheetPath": "images/cardSet02_HighSmall.jpg",
		                    "sheetSize": {
		                      "x": 0,
		                      "y": 0,
		                      "height": 154,
		                      "width": 155
		                    }
		                  }
		                }
		              }
		            ]
		          }
		        ]
		      },
		      {
		        "themeId": "2",
		        "themeName": "theme_2",
		        "normalResolution": {
		          "image": {
		            "rect": {
		              "x": 64,
		              "y": 65,
		              "height": 66,
		              "width": 67
		            },
		            "sheetPath": "images/themeSet01_Normal.jpg",
		            "sheetSize": {
		              "x": 0,
		              "y": 0,
		              "height": 156,
		              "width": 157
		            }
		          },
		          "smallImage": {
		            "rect": {
		              "x": 66,
		              "y": 67,
		              "height": 68,
		              "width": 69
		            },
		            "sheetPath": "images/themeSet01_NormalSmall.jpg",
		            "sheetSize": {
		              "x": 0,
		              "y": 0,
		              "height": 158,
		              "width": 159
		            }
		          }
		        },
		        "highResolution": {
		          "image": {
		            "rect": {
		              "x": 68,
		              "y": 69,
		              "height": 70,
		              "width": 71
		            },
		            "sheetPath": "images/themeSet01_High.jpg",
		            "sheetSize": {
		              "x": 0,
		              "y": 0,
		              "height": 160,
		              "width": 161
		            }
		          },
		          "smallImage": {
		            "rect": {
		              "x": 70,
		              "y": 71,
		              "height": 72,
		              "width": 73
		            },
		            "sheetPath": "images/themeSet01_HighSmall.jpg",
		            "sheetSize": {
		              "x": 0,
		              "y": 0,
		              "height": 162,
		              "width": 163
		            }
		          }
		        },
		        "pageCollection": [
		          {
		            "pageId": "2.1",
		            "pageName": "page_2.1",
		            "normalResolution": {
		              "image": {
		                "rect": {
		                  "x": 0,
		                  "y": 0,
		                  "height": 74,
		                  "width": 75
		                },
		                "sheetPath": "images/pageSet02_Normal.jpg",
		                "sheetSize": {
		                  "x": 0,
		                  "y": 0,
		                  "height": 164,
		                  "width": 165
		                }
		              },
		              "smallImage": {
		                "rect": {
		                  "x": 0,
		                  "y": 0,
		                  "height": 76,
		                  "width": 77
		                },
		                "sheetPath": "images/pageSet02_NormalSmall.jpg",
		                "sheetSize": {
		                  "x": 0,
		                  "y": 0,
		                  "height": 166,
		                  "width": 167
		                }
		              }
		            },
		            "highResolution": {
		              "image": {
		                "rect": {
		                  "x": 0,
		                  "y": 0,
		                  "height": 78,
		                  "width": 79
		                },
		                "sheetPath": "images/pageSet02_High.jpg",
		                "sheetSize": {
		                  "x": 0,
		                  "y": 0,
		                  "height": 168,
		                  "width": 169
		                }
		              },
		              "smallImage": {
		                "rect": {
		                  "x": 0,
		                  "y": 0,
		                  "height": 80,
		                  "width": 81
		                },
		                "sheetPath": "images/pageSet02_HighSmall.jpg",
		                "sheetSize": {
		                  "x": 0,
		                  "y": 0,
		                  "height": 170,
		                  "width": 171
		                }
		              }
		            },
		            "cardCollection": [
		              {
		                "cardId": 5,
		                "cardName": "card_2.1.1",
		                "cardIntro": "cardIntro_2.1.1",
		                "cardDescription": "cardDescription_2.1.1",
		                "unlockHowToText": "Unlock this card by playing Destiny.",
		                "rarity": 1,
		                "unlockFlagHash": 0,
		                "points": 0,
		                "normalResolution": {
		                  "image": {
		                    "rect": {
		                      "x": 0,
		                      "y": 0,
		                      "height": 82,
		                      "width": 83
		                    },
		                    "sheetPath": "images/cardSet03_Normal.jpg",
		                    "sheetSize": {
		                      "x": 0,
		                      "y": 0,
		                      "height": 172,
		                      "width": 173
		                    }
		                  },
		                  "smallImage": {
		                    "rect": {
		                      "x": 0,
		                      "y": 0,
		                      "height": 84,
		                      "width": 85
		                    },
		                    "sheetPath": "images/cardSet03_NormalSmall.jpg",
		                    "sheetSize": {
		                      "x": 0,
		                      "y": 0,
		                      "height": 174,
		                      "width": 175
		                    }
		                  }
		                },
		                "highResolution": {
		                  "image": {
		                    "rect": {
		                      "x": 0,
		                      "y": 0,
		                      "height": 86,
		                      "width": 87
		                    },
		                    "sheetPath": "images/cardSet03_High.jpg",
		                    "sheetSize": {
		                      "x": 0,
		                      "y": 0,
		                      "height": 176,
		                      "width": 177
		                    }
		                  },
		                  "smallImage": {
		                    "rect": {
		                      "x": 0,
		                      "y": 0,
		                      "height": 88,
		                      "width": 89
		                    },
		                    "sheetPath": "images/cardSet03_HighSmall.jpg",
		                    "sheetSize": {
		                      "x": 0,
		                      "y": 0,
		                      "height": 178,
		                      "width": 179
		                    }
		                  }
		                }
		              }
		            ]
		          }
		        ]
		      },
		      {
		        "themeId": "3",
		        "themeName": "weird_cases_theme",
		        "normalResolution": {
		          "image": {
		            "rect": {
		              "x": 64,
		              "y": 65,
		              "height": 66,
		              "width": 67
		            },
		            "sheetPath": "images/weirdCasesSet01_Normal.jpg",
		            "sheetSize": {
		              "x": 0,
		              "y": 0,
		              "height": 156,
		              "width": 157
		            }
		          },
		          "smallImage": {
		            "rect": {
		              "x": 66,
		              "y": 67,
		              "height": 68,
		              "width": 69
		            },
		            "sheetPath": "images/weirdCasesSet01_NormalSmall.jpg",
		            "sheetSize": {
		              "x": 0,
		              "y": 0,
		              "height": 158,
		              "width": 159
		            }
		          }
		        },
		        "highResolution": {
		          "image": {
		            "rect": {
		              "x": 68,
		              "y": 69,
		              "height": 70,
		              "width": 71
		            },
		            "sheetPath": "images/weirdCasesSet01_High.jpg",
		            "sheetSize": {
		              "x": 0,
		              "y": 0,
		              "height": 160,
		              "width": 161
		            }
		          },
		          "smallImage": {
		            "rect": {
		              "x": 70,
		              "y": 71,
		              "height": 72,
		              "width": 73
		            },
		            "sheetPath": "images/weirdCasesSet01_HighSmall.jpg",
		            "sheetSize": {
		              "x": 0,
		              "y": 0,
		              "height": 162,
		              "width": 163
		            }
		          }
		        },
		        "pageCollection": [
		          {
		            "pageId": "3.1",
		            "pageName": "weird_cases_pages",
		            "normalResolution": {
		              "image": {
		                "rect": {
		                  "x": 0,
		                  "y": 0,
		                  "height": 74,
		                  "width": 75
		                },
		                "sheetPath": "images/weirdCasesPageSet01_Normal.jpg",
		                "sheetSize": {
		                  "x": 0,
		                  "y": 0,
		                  "height": 164,
		                  "width": 165
		                }
		              },
		              "smallImage": {
		                "rect": {
		                  "x": 0,
		                  "y": 0,
		                  "height": 76,
		                  "width": 77
		                },
		                "sheetPath": "images/weirdCasesPageSet01_NormalSmall.jpg",
		                "sheetSize": {
		                  "x": 0,
		                  "y": 0,
		                  "height": 166,
		                  "width": 167
		                }
		              }
		            },
		            "highResolution": {
		              "image": {
		                "rect": {
		                  "x": 0,
		                  "y": 0,
		                  "height": 78,
		                  "width": 79
		                },
		                "sheetPath": "images/weirdCasesPageSet01_High.jpg",
		                "sheetSize": {
		                  "x": 0,
		                  "y": 0,
		                  "height": 168,
		                  "width": 169
		                }
		              },
		              "smallImage": {
		                "rect": {
		                  "x": 0,
		                  "y": 0,
		                  "height": 80,
		                  "width": 81
		                },
		                "sheetPath": "images/weirdCasesPageSet01_HighSmall.jpg",
		                "sheetSize": {
		                  "x": 0,
		                  "y": 0,
		                  "height": 170,
		                  "width": 171
		                }
		              }
		            },
		            "cardCollection": [
		              {
		                "cardId": 6,
		                "cardName": "card_without_intro",
		                "cardDescription": "card_without_intro_description",
		                "unlockHowToText": "Unlock this card by playing Destiny.",
		                "rarity": 1,
		                "unlockFlagHash": 0,
		                "points": 0,
		                "normalResolution": {
		                  "image": {
		                    "rect": {
		                      "x": 0,
		                      "y": 0,
		                      "height": 92,
		                      "width": 93
		                    },
		                    "sheetPath": "images/weirdCasesCardSet01_Normal.jpg",
		                    "sheetSize": {
		                      "x": 0,
		                      "y": 0,
		                      "height": 172,
		                      "width": 173
		                    }
		                  },
		                  "smallImage": {
		                    "rect": {
		                      "x": 0,
		                      "y": 0,
		                      "height": 94,
		                      "width": 95
		                    },
		                    "sheetPath": "images/weirdCasesCardSet01_NormalSmall.jpg",
		                    "sheetSize": {
		                      "x": 0,
		                      "y": 0,
		                      "height": 174,
		                      "width": 175
		                    }
		                  }
		                },
		                "highResolution": {
		                  "image": {
		                    "rect": {
		                      "x": 0,
		                      "y": 0,
		                      "height": 96,
		                      "width": 97
		                    },
		                    "sheetPath": "images/weirdCasesCardSet01_High.jpg",
		                    "sheetSize": {
		                      "x": 0,
		                      "y": 0,
		                      "height": 176,
		                      "width": 177
		                    }
		                  },
		                  "smallImage": {
		                    "rect": {
		                      "x": 0,
		                      "y": 0,
		                      "height": 98,
		                      "width": 99
		                    },
		                    "sheetPath": "images/weirdCasesCardSet01_HighSmall.jpg",
		                    "sheetSize": {
		                      "x": 0,
		                      "y": 0,
		                      "height": 178,
		                      "width": 179
		                    }
		                  }
		                }
		              },
		              {
		                "cardId": 7,
		                "cardName": "card_without_description",
		                "cardIntro": "card_without_description_intro",
		                "unlockHowToText": "Unlock this card by playing Destiny.",
		                "rarity": 1,
		                "unlockFlagHash": 0,
		                "points": 0,
		                "normalResolution": {
		                  "image": {
		                    "rect": {
		                      "x": 0,
		                      "y": 0,
		                      "height": 102,
		                      "width": 103
		                    },
		                    "sheetPath": "images/weirdCasesCardSet01_Normal.jpg",
		                    "sheetSize": {
		                      "x": 0,
		                      "y": 0,
		                      "height": 172,
		                      "width": 173
		                    }
		                  },
		                  "smallImage": {
		                    "rect": {
		                      "x": 0,
		                      "y": 0,
		                      "height": 104,
		                      "width": 105
		                    },
		                    "sheetPath": "images/weirdCasesCardSet01_NormalSmall.jpg",
		                    "sheetSize": {
		                      "x": 0,
		                      "y": 0,
		                      "height": 174,
		                      "width": 175
		                    }
		                  }
		                },
		                "highResolution": {
		                  "image": {
		                    "rect": {
		                      "x": 0,
		                      "y": 0,
		                      "height": 106,
		                      "width": 107
		                    },
		                    "sheetPath": "images/weirdCasesCardSet01_High.jpg",
		                    "sheetSize": {
		                      "x": 0,
		                      "y": 0,
		                      "height": 176,
		                      "width": 177
		                    }
		                  },
		                  "smallImage": {
		                    "rect": {
		                      "x": 0,
		                      "y": 0,
		                      "height": 108,
		                      "width": 109
		                    },
		                    "sheetPath": "images/weirdCasesCardSet01_HighSmall.jpg",
		                    "sheetSize": {
		                      "x": 0,
		                      "y": 0,
		                      "height": 178,
		                      "width": 179
		                    }
		                  }
		                }
		              }
		            ]
		          }
		        ]
		      }
		    ]
		  },
		  "ErrorCode": 1,
		  "ThrottleSeconds": 0,
		  "ErrorStatus": "Success",
		  "Message": "Ok",
		  "MessageData": {}
		}
	'''

	grimoireDefinition = grimoireebook.getDestinyGrimoireDefinitionFromJson(json.loads(testGrimoire, encoding='utf8'))

	assert len(grimoireDefinition["themes"]) == 3
	assert grimoireDefinition["themes"][0]["themeName"] == "theme_1"
	assert len(grimoireDefinition["themes"][0]["pages"]) == 2
	assert grimoireDefinition["themes"][0]["pages"][0]["pageName"] == "page_1.1"
	assert len(grimoireDefinition["themes"][0]["pages"][0]["cards"]) == 2
	assert grimoireDefinition["themes"][0]["pages"][0]["cards"][0]["cardName"] == "card_1.1.1"
	assert grimoireDefinition["themes"][0]["pages"][0]["cards"][0]["cardIntro"] == "cardIntro_1.1.1"
	assert grimoireDefinition["themes"][0]["pages"][0]["cards"][0]["cardDescription"] == "cardDescription_1.1.1"
	assert grimoireDefinition["themes"][0]["pages"][0]["cards"][0]["hash"] == generateExpectedCardHash("theme_1","page_1.1", "card_1.1.1")
	assert grimoireDefinition["themes"][0]["pages"][0]["cards"][0]["image"]["sourceImage"] == "http://www.bungie.net/images/cardSet01_High.jpg"
	assert grimoireDefinition["themes"][0]["pages"][0]["cards"][0]["image"]["regionXStart"] == 0
	assert grimoireDefinition["themes"][0]["pages"][0]["cards"][0]["image"]["regionYStart"] == 0
	assert grimoireDefinition["themes"][0]["pages"][0]["cards"][0]["image"]["regionHeight"] == 30
	assert grimoireDefinition["themes"][0]["pages"][0]["cards"][0]["image"]["regionWidth"] == 31
	assert grimoireDefinition["themes"][0]["pages"][0]["cards"][1]["cardName"] == "card_1.1.2"
	assert grimoireDefinition["themes"][0]["pages"][0]["cards"][1]["cardIntro"] == "cardIntro_1.1.2"
	assert grimoireDefinition["themes"][0]["pages"][0]["cards"][1]["cardDescription"] == "cardDescription_1.1.2"
	assert grimoireDefinition["themes"][0]["pages"][0]["cards"][1]["hash"] == generateExpectedCardHash("theme_1","page_1.1", "card_1.1.2")
	assert grimoireDefinition["themes"][0]["pages"][0]["cards"][1]["image"]["sourceImage"] == "http://www.bungie.net/images/cardSet01_High.jpg"
	assert grimoireDefinition["themes"][0]["pages"][0]["cards"][1]["image"]["regionXStart"] == 36
	assert grimoireDefinition["themes"][0]["pages"][0]["cards"][1]["image"]["regionYStart"] == 37
	assert grimoireDefinition["themes"][0]["pages"][0]["cards"][1]["image"]["regionHeight"] == 38
	assert grimoireDefinition["themes"][0]["pages"][0]["cards"][1]["image"]["regionWidth"] == 39
	assert grimoireDefinition["themes"][0]["pages"][1]["pageName"] == 'page_1.2'
	assert len(grimoireDefinition["themes"][0]["pages"][1]["cards"]) == 2
	assert grimoireDefinition["themes"][0]["pages"][1]["cards"][0]["cardName"] == "card_1.2.1"
	assert grimoireDefinition["themes"][0]["pages"][1]["cards"][0]["cardIntro"] == "cardIntro_1.2.1"
	assert grimoireDefinition["themes"][0]["pages"][1]["cards"][0]["cardDescription"] == "cardDescription_1.2.1"
	assert grimoireDefinition["themes"][0]["pages"][1]["cards"][0]["hash"] == generateExpectedCardHash("theme_1","page_1.2", "card_1.2.1")
	assert grimoireDefinition["themes"][0]["pages"][1]["cards"][0]["image"]["sourceImage"] == "http://www.bungie.net/images/cardSet02_High.jpg"
	assert grimoireDefinition["themes"][0]["pages"][1]["cards"][0]["image"]["regionXStart"] == 0
	assert grimoireDefinition["themes"][0]["pages"][1]["cards"][0]["image"]["regionYStart"] == 0
	assert grimoireDefinition["themes"][0]["pages"][1]["cards"][0]["image"]["regionHeight"] == 54
	assert grimoireDefinition["themes"][0]["pages"][1]["cards"][0]["image"]["regionWidth"] == 55
	assert grimoireDefinition["themes"][0]["pages"][1]["cards"][1]["cardName"] == "card_1.2.2"
	assert grimoireDefinition["themes"][0]["pages"][1]["cards"][1]["cardIntro"] == "cardIntro_1.2.2"
	assert grimoireDefinition["themes"][0]["pages"][1]["cards"][1]["cardDescription"] == "cardDescription_1.2.2"
	assert grimoireDefinition["themes"][0]["pages"][1]["cards"][1]["hash"] == generateExpectedCardHash("theme_1","page_1.2", "card_1.2.2")
	assert grimoireDefinition["themes"][0]["pages"][1]["cards"][1]["image"]["sourceImage"] == "http://www.bungie.net/images/cardSet02_High.jpg"
	assert grimoireDefinition["themes"][0]["pages"][1]["cards"][1]["image"]["regionXStart"] == 60
	assert grimoireDefinition["themes"][0]["pages"][1]["cards"][1]["image"]["regionYStart"] == 61
	assert grimoireDefinition["themes"][0]["pages"][1]["cards"][1]["image"]["regionHeight"] == 62
	assert grimoireDefinition["themes"][0]["pages"][1]["cards"][1]["image"]["regionWidth"] == 63
	assert grimoireDefinition["themes"][1]["themeName"] == "theme_2"
	assert len(grimoireDefinition["themes"][1]["pages"]) == 1
	assert grimoireDefinition["themes"][1]["pages"][0]["pageName"] == "page_2.1"
	assert len(grimoireDefinition["themes"][1]["pages"][0]["cards"]) == 1
	assert grimoireDefinition["themes"][1]["pages"][0]["cards"][0]["cardName"] == "card_2.1.1"
	assert grimoireDefinition["themes"][1]["pages"][0]["cards"][0]["cardIntro"] == "cardIntro_2.1.1"
	assert grimoireDefinition["themes"][1]["pages"][0]["cards"][0]["cardDescription"] == "cardDescription_2.1.1"
	assert grimoireDefinition["themes"][1]["pages"][0]["cards"][0]["hash"] == generateExpectedCardHash("theme_2","page_2.1", "card_2.1.1")
	assert grimoireDefinition["themes"][1]["pages"][0]["cards"][0]["image"]["sourceImage"] == "http://www.bungie.net/images/cardSet03_High.jpg"
	assert grimoireDefinition["themes"][1]["pages"][0]["cards"][0]["image"]["regionXStart"] == 0
	assert grimoireDefinition["themes"][1]["pages"][0]["cards"][0]["image"]["regionYStart"] == 0
	assert grimoireDefinition["themes"][1]["pages"][0]["cards"][0]["image"]["regionHeight"] == 86
	assert grimoireDefinition["themes"][1]["pages"][0]["cards"][0]["image"]["regionWidth"] == 87
	assert grimoireDefinition["themes"][2]["themeName"] == "weird_cases_theme"
	assert len(grimoireDefinition["themes"][2]["pages"]) == 1
	assert grimoireDefinition["themes"][2]["pages"][0]["pageName"] == "weird_cases_pages"
	assert len(grimoireDefinition["themes"][2]["pages"][0]["cards"]) == 2
	assert grimoireDefinition["themes"][2]["pages"][0]["cards"][0]["cardName"] == "card_without_intro"
	assert grimoireDefinition["themes"][2]["pages"][0]["cards"][0]["cardIntro"] == ""
	assert grimoireDefinition["themes"][2]["pages"][0]["cards"][0]["cardDescription"] == "card_without_intro_description"
	assert grimoireDefinition["themes"][2]["pages"][0]["cards"][0]["hash"] == generateExpectedCardHash("weird_cases_theme","weird_cases_pages", "card_without_intro")
	assert grimoireDefinition["themes"][2]["pages"][0]["cards"][0]["image"]["sourceImage"] == "http://www.bungie.net/images/weirdCasesCardSet01_High.jpg"
	assert grimoireDefinition["themes"][2]["pages"][0]["cards"][0]["image"]["regionXStart"] == 0
	assert grimoireDefinition["themes"][2]["pages"][0]["cards"][0]["image"]["regionYStart"] == 0
	assert grimoireDefinition["themes"][2]["pages"][0]["cards"][0]["image"]["regionHeight"] == 96
	assert grimoireDefinition["themes"][2]["pages"][0]["cards"][0]["image"]["regionWidth"] == 97
	assert grimoireDefinition["themes"][2]["pages"][0]["cards"][1]["cardName"] == "card_without_description"
	assert grimoireDefinition["themes"][2]["pages"][0]["cards"][1]["cardIntro"] == "card_without_description_intro"
	assert grimoireDefinition["themes"][2]["pages"][0]["cards"][1]["cardDescription"] == ""
	assert grimoireDefinition["themes"][2]["pages"][0]["cards"][1]["hash"] == generateExpectedCardHash("weird_cases_theme","weird_cases_pages", "card_without_description")
	assert grimoireDefinition["themes"][2]["pages"][0]["cards"][1]["image"]["sourceImage"] == "http://www.bungie.net/images/weirdCasesCardSet01_High.jpg"
	assert grimoireDefinition["themes"][2]["pages"][0]["cards"][1]["image"]["regionXStart"] == 0
	assert grimoireDefinition["themes"][2]["pages"][0]["cards"][1]["image"]["regionYStart"] == 0
	assert grimoireDefinition["themes"][2]["pages"][0]["cards"][1]["image"]["regionHeight"] == 106
	assert grimoireDefinition["themes"][2]["pages"][0]["cards"][1]["image"]["regionWidth"] == 107

@mock.patch('os.path.exists')
@mock.patch('os.makedirs')
@mock.patch('urllib.urlretrieve')
def test_shouldDownloadAllGrimoireImagesToLocalStorage(mock_urllib, mock_makedirs, mock_pathExists):
	testGrimoireDefinition = dict()
	testGrimoireDefinition["themes"] = []
	testGrimoireDefinition["themes"].append(dict())
	testGrimoireDefinition["themes"][0]["pages"] = []
	testGrimoireDefinition["themes"][0]["pages"].append(dict())
	testGrimoireDefinition["themes"][0]["pages"][0]["cards"] = []
	testGrimoireDefinition["themes"][0]["pages"][0]["cards"].append(dict())
	testGrimoireDefinition["themes"][0]["pages"][0]["cards"][0]["image"] = dict(sourceImage = "http://www.bungie.net/images/cardSet01_High.jpg")
	testGrimoireDefinition["themes"][0]["pages"][0]["cards"].append(dict())
	testGrimoireDefinition["themes"][0]["pages"][0]["cards"][1]["image"] = dict(sourceImage = "http://www.bungie.net/images/cardSet01_High.jpg")
	testGrimoireDefinition["themes"][0]["pages"][0]["cards"].append(dict())
	testGrimoireDefinition["themes"][0]["pages"][0]["cards"][2]["image"] = dict(sourceImage = "http://www.bungie.net/images/cardSet02_High.jpg")
	testGrimoireDefinition["themes"][0]["pages"][0]["cards"].append(dict())
	testGrimoireDefinition["themes"][0]["pages"][0]["cards"][3]["image"] = dict(sourceImage = "http://www.bungie.net/images/cardSet02_High.jpg")
	testGrimoireDefinition["themes"][0]["pages"].append(dict())
	testGrimoireDefinition["themes"][0]["pages"][1]["cards"] = []
	testGrimoireDefinition["themes"][0]["pages"][1]["cards"].append(dict())
	testGrimoireDefinition["themes"][0]["pages"][1]["cards"][0]["image"] = dict(sourceImage = "http://www.bungie.net/images/cardSet03_High.jpg")
	testGrimoireDefinition["themes"][0]["pages"][1]["cards"].append(dict())
	testGrimoireDefinition["themes"][0]["pages"][1]["cards"][1]["image"] = dict(sourceImage = "http://www.bungie.net/images/cardSet03_High.jpg")
	testGrimoireDefinition["themes"][0]["pages"][1]["cards"].append(dict())
	testGrimoireDefinition["themes"][0]["pages"][1]["cards"][2]["image"] = dict(sourceImage = "http://www.bungie.net/images/cardSet04_High.jpg")
	testGrimoireDefinition["themes"][0]["pages"][1]["cards"].append(dict())
	testGrimoireDefinition["themes"][0]["pages"][1]["cards"][3]["image"] = dict(sourceImage = "http://www.bungie.net/images/cardSet04_High.jpg")
	testGrimoireDefinition["themes"].append(dict())
	testGrimoireDefinition["themes"][1]["pages"] = []
	testGrimoireDefinition["themes"][1]["pages"].append(dict())
	testGrimoireDefinition["themes"][1]["pages"][0]["cards"] = []
	testGrimoireDefinition["themes"][1]["pages"][0]["cards"].append(dict())
	testGrimoireDefinition["themes"][1]["pages"][0]["cards"][0]["image"] = dict(sourceImage = "http://www.bungie.net/images/cardSet05_High.jpg")
	testGrimoireDefinition["themes"][1]["pages"][0]["cards"].append(dict())
	testGrimoireDefinition["themes"][1]["pages"][0]["cards"][1]["image"] = dict(sourceImage = "http://www.bungie.net/images/cardSet05_High.jpg")
	testGrimoireDefinition["themes"][1]["pages"][0]["cards"].append(dict())
	testGrimoireDefinition["themes"][1]["pages"][0]["cards"][2]["image"] = dict(sourceImage = "http://www.bungie.net/images/cardSet06_High.jpg")
	testGrimoireDefinition["themes"][1]["pages"][0]["cards"].append(dict())
	testGrimoireDefinition["themes"][1]["pages"][0]["cards"][3]["image"] = dict(sourceImage = "http://www.bungie.net/images/cardSet06_High.jpg")
	testGrimoireDefinition["themes"][1]["pages"].append(dict())
	testGrimoireDefinition["themes"][1]["pages"][1]["cards"] = []
	testGrimoireDefinition["themes"][1]["pages"][1]["cards"].append(dict())
	testGrimoireDefinition["themes"][1]["pages"][1]["cards"][0]["image"] = dict(sourceImage = "http://www.bungie.net/images/cardSet07_High.jpg")
	testGrimoireDefinition["themes"][1]["pages"][1]["cards"].append(dict())
	testGrimoireDefinition["themes"][1]["pages"][1]["cards"][1]["image"] = dict(sourceImage = "http://www.bungie.net/images/cardSet07_High.jpg")
	testGrimoireDefinition["themes"][1]["pages"][1]["cards"].append(dict())
	testGrimoireDefinition["themes"][1]["pages"][1]["cards"][2]["image"] = dict(sourceImage = "http://www.bungie.net/images/cardSet08_High.jpg")
	testGrimoireDefinition["themes"][1]["pages"][1]["cards"].append(dict())
	testGrimoireDefinition["themes"][1]["pages"][1]["cards"][3]["image"] = dict(sourceImage = "http://www.bungie.net/images/cardSet08_High.jpg")

	mock_pathExists.return_value = False

	grimoireebook.dowloadGrimoireImages(testGrimoireDefinition)

	mock_makedirs.assert_called_once_with(grimoireebook.DEFAULT_IMAGE_FOLDER)
	assert mock_urllib.call_count == 8
	mock_urllib.assert_any_call("http://www.bungie.net/images/cardSet01_High.jpg", os.path.join(grimoireebook.DEFAULT_IMAGE_FOLDER, "cardSet01_High.jpg"))
	mock_urllib.assert_any_call("http://www.bungie.net/images/cardSet02_High.jpg", os.path.join(grimoireebook.DEFAULT_IMAGE_FOLDER, "cardSet02_High.jpg"))
	mock_urllib.assert_any_call("http://www.bungie.net/images/cardSet03_High.jpg", os.path.join(grimoireebook.DEFAULT_IMAGE_FOLDER, "cardSet03_High.jpg"))
	mock_urllib.assert_any_call("http://www.bungie.net/images/cardSet04_High.jpg", os.path.join(grimoireebook.DEFAULT_IMAGE_FOLDER, "cardSet04_High.jpg"))
	mock_urllib.assert_any_call("http://www.bungie.net/images/cardSet05_High.jpg", os.path.join(grimoireebook.DEFAULT_IMAGE_FOLDER, "cardSet05_High.jpg"))
	mock_urllib.assert_any_call("http://www.bungie.net/images/cardSet06_High.jpg", os.path.join(grimoireebook.DEFAULT_IMAGE_FOLDER, "cardSet06_High.jpg"))
	mock_urllib.assert_any_call("http://www.bungie.net/images/cardSet07_High.jpg", os.path.join(grimoireebook.DEFAULT_IMAGE_FOLDER, "cardSet07_High.jpg"))
	mock_urllib.assert_any_call("http://www.bungie.net/images/cardSet08_High.jpg", os.path.join(grimoireebook.DEFAULT_IMAGE_FOLDER, "cardSet08_High.jpg"))

@mock.patch('os.path.exists')
@mock.patch('os.makedirs')
@mock.patch('urllib.urlretrieve')
def test_shouldNotCreateImageFolderWhenDownloadAllGrimoireImagesToLocalStorageIfItAlreadyExists(mock_urllib, mock_makedirs, mock_pathExists):
	testGrimoireDefinition = dict()
	testGrimoireDefinition["themes"] = []
	testGrimoireDefinition["themes"].append(dict())
	testGrimoireDefinition["themes"][0]["pages"] = []
	testGrimoireDefinition["themes"][0]["pages"].append(dict())
	testGrimoireDefinition["themes"][0]["pages"][0]["cards"] = []
	testGrimoireDefinition["themes"][0]["pages"][0]["cards"].append(dict())
	testGrimoireDefinition["themes"][0]["pages"][0]["cards"][0]["image"] = dict(sourceImage = "http://www.bungie.net/images/cardSet01_High.jpg")
	testGrimoireDefinition["themes"][0]["pages"][0]["cards"].append(dict())
	testGrimoireDefinition["themes"][0]["pages"][0]["cards"][1]["image"] = dict(sourceImage = "http://www.bungie.net/images/cardSet02_High.jpg")

	mock_pathExists.return_value = True

	grimoireebook.dowloadGrimoireImages(testGrimoireDefinition)

	mock_makedirs.assert_not_called()
	assert mock_urllib.call_count == 2
	mock_urllib.assert_any_call("http://www.bungie.net/images/cardSet01_High.jpg", os.path.join(grimoireebook.DEFAULT_IMAGE_FOLDER, "cardSet01_High.jpg"))
	mock_urllib.assert_any_call("http://www.bungie.net/images/cardSet02_High.jpg", os.path.join(grimoireebook.DEFAULT_IMAGE_FOLDER, "cardSet02_High.jpg"))

@mock.patch('grimoireebook.Image.open')
@mock.patch('grimoireebook.Image')
@mock.patch('grimoireebook.Image')
def test_shouldGenerateCardImageFromGivenSheet(mock_sheetImage, mock_cardImage, mock_imageOpen):
	localImageFolder = '~/destinyGrimoire/images'
	mock_imageOpen.return_value = mock_sheetImage
	mock_sheetImage.crop.return_value = mock_cardImage

	sheetImagePath = '/home/me/sheet.jpg'
	cardName = 'test'
	dimensions_tuple = (1,2,3,4)
	expectedGeneratedImagePath = os.path.join(localImageFolder, 'test.jpg')

	generatedImagePath = grimoireebook.generateCardImageFromImageSheet(cardName, sheetImagePath, localImageFolder, dimensions_tuple)

	assert generatedImagePath == expectedGeneratedImagePath
	mock_imageOpen.assert_called_once_with(sheetImagePath)
	mock_sheetImage.crop.assert_called_once_with((dimensions_tuple[0], dimensions_tuple[1], dimensions_tuple[0] + dimensions_tuple[2], dimensions_tuple[1] + dimensions_tuple[3]))
	mock_cardImage.save.assert_called_once_with(expectedGeneratedImagePath, optimize=True)

def test_shouldGenerateGrimoirePageContent():
	pageData = {'cardName': 'NameText',
					'cardIntro': 'IntroText',
					'cardDescription': 'DescriptionText',
					'image': {
						'sourceImage': 'http://www.bungie.net/images/cardSet.jpg',
						'regionXStart': 0,
						'regionYStart': 0,
						'regionHeight': 30,
						'regionWidth': 31
					}
				}
	pageImagePath = os.path.join("images", "NameText_img.jpg")

	expectedContent = u'''<cardname">%s</cardname>
						  <cardintro>%s</cardintro>
						  <container>
							<cardimage><img src="%s"/></cardimage>
							<carddescription">%s</carddescription>
						  </container>''' % ( 'NameText', 'IntroText', pageImagePath, 'DescriptionText')

	pageContent = grimoireebook.generateGrimoirePageContent(pageData, pageImagePath)

	assert pageContent.encode('ascii', 'replace').translate(None, string.whitespace) == expectedContent.encode('ascii', 'replace').translate(None, string.whitespace)

@mock.patch('grimoireebook.generateCardImageFromImageSheet')
def test_shouldGenerateEpubImageItem(mock_card_image_gen):
	testImageData = 'DummyPictureData'

	with mock.patch('grimoireebook.open', mock.mock_open(read_data=testImageData)):
		cardName = "test"
		cardImageBaseName = '%s_img' % (cardName)
		cardImageFolder = "images"
		generatedCardImagePath = ".destinyCache/cache/%s/%s.jpg" % (cardImageFolder, cardImageBaseName)
		sheetImagePath = "images/cardSet.jpg"
		cardImageData = {
							'sourceImage': 'http://www.bungie.net/images/cardSet.jpg',
							'regionXStart': 0,
							'regionYStart': 0,
							'regionHeight': 30,
							'regionWidth': 31
						}

		mock_card_image_gen.return_value = generatedCardImagePath

		epubImageItem = grimoireebook.generateGrimoirePageImage(cardName, cardImageData, cardImageFolder)

		assert epubImageItem.id == cardImageBaseName
		assert epubImageItem.file_name == os.path.join('images','%s_img.jpg' % (cardName))
		assert epubImageItem.content == testImageData

		mock_card_image_gen.assert_called_with(cardImageBaseName, sheetImagePath, cardImageFolder, (0,0,31,30))

@mock.patch('grimoireebook.generateGrimoirePageImage')
def test_shouldCreateGrimoireEbookPage(mock_generate_grimoire_page_image):
	runCreateGrimoireEbookPageTest('NameText', 'NameText', mock_generate_grimoire_page_image)

@mock.patch('grimoireebook.generateGrimoirePageImage')
def test_shouldReplaceWhitespaceCharactersInFilenamesWhenCreatingGrimoireEbookPage(mock_generate_grimoire_page_image):
	runCreateGrimoireEbookPageTest('Name \tText', 'Name__Text', mock_generate_grimoire_page_image)

def runCreateGrimoireEbookPageTest(cardName, cardFilename, mock_generate_grimoire_page_image):
	cardImage = "%s_img.jpg" % (cardName)
	cardImagePath = os.path.join(grimoireebook.DEFAULT_IMAGE_FOLDER, cardImage)
	cardHash = '12345678890abcdef'

	cardData = {
					'cardName': cardName,
					'cardIntro': 'IntroText',
					'cardDescription': 'DescriptionText',
					'hash': cardHash,
					'image': {
						'sourceImage': 'http://www.bungie.net/images/cardSet.jpg',
						'regionXStart': 0,
						'regionYStart': 0,
						'regionHeight': 30,
						'regionWidth': 31
					}
				}
	default_css = epub.EpubItem(uid="page_style", file_name="style/page.css", media_type="text/css", content=grimoireebook.DEFAULT_PAGE_STYLE)

	mock_grimoire_page_image = mock.Mock()
	mock_grimoire_page_image.file_name= "%s/%s" % (grimoireebook.DEFAULT_IMAGE_FOLDER, cardImage)
	mock_generate_grimoire_page_image.return_value = mock_grimoire_page_image

	createdPageItems = grimoireebook.createGrimoireCardPage(cardData, default_css)

	expectedCardFilename = '%s-%s' % (cardHash, cardFilename)
	assert createdPageItems.page.title == cardName
	assert createdPageItems.page.file_name == '%s.xhtml' % (expectedCardFilename)
	assert createdPageItems.page.lang == 'en'
	assert createdPageItems.page.content == grimoireebook.generateGrimoirePageContent(cardData, cardImagePath)
	assert createdPageItems.image == mock_grimoire_page_image

	mock_generate_grimoire_page_image.assert_called_with(expectedCardFilename, cardData['image'], grimoireebook.DEFAULT_IMAGE_FOLDER)

	pageStyle = createdPageItems.page.get_links_of_type("text/css").next()
	assert pageStyle['href'] == 'style/page.css'

@mock.patch('ebooklib.epub.EpubBook')
@mock.patch('grimoireebook.createGrimoireCardPage')
def test_shouldAddPageCardsToGrimoireEbook(mock_createGrimoireCardPage, mock_ebook):
	firstCardPage = mock.Mock()
	firstCardImage = mock.Mock()
	secondCardPage = mock.Mock()
	secondCardImage = mock.Mock()

	mock_createGrimoireCardPage.side_effect = [ collections.namedtuple('GrimoirePage', ['page', 'image'])(page=firstCardPage, image=firstCardImage), collections.namedtuple('GrimoirePage', ['page', 'image'])(page=secondCardPage, image=secondCardImage) ]

	pageData = {
					'cards' : [ 'card1', 'card2' ]
				}

	pageCards = grimoireebook.addPageItemsToEbook(mock_ebook, pageData)

	assert pageCards == (firstCardPage, secondCardPage)
	mock_createGrimoireCardPage.assert_has_calls([mock.call('card1', BookStyleItemMatcher()), mock.call('card2', BookStyleItemMatcher())])
	mock_ebook.add_item.assert_has_calls([mock.call(firstCardPage), mock.call(firstCardImage), mock.call(secondCardPage), mock.call(secondCardImage)])
	mock_ebook.spine.append.assert_has_calls([mock.call(firstCardPage), mock.call(secondCardPage)])

@mock.patch('ebooklib.epub.EpubBook')
@mock.patch('grimoireebook.addPageItemsToEbook')
def test_shouldAddThemePagesToGrimoireEbook(mock_addPageItemsToEbook, mock_ebook):
	firstPageSet = ('firstPageSet',)
	secondPageSet = ('secondPageSet',)

	mock_addPageItemsToEbook.side_effect = [firstPageSet, secondPageSet]

	firstPage = {'pageName' : 'page1'}
	secondPage = {'pageName': 'page2'}

	themeData = {
					'themeName' : 'testTheme',
					'pages' : [ firstPage, secondPage ]
				}

	themePages = grimoireebook.addThemePagesToEbook(mock_ebook, themeData)

	assert type(themePages[0][0]) is epub.Section
	assert themePages[0][0].title == firstPage['pageName']
	assert themePages[0][1] == firstPageSet
	assert type(themePages[1][0]) is epub.Section
	assert themePages[1][0].title == secondPage['pageName']
	assert themePages[1][1] == secondPageSet

	mock_addPageItemsToEbook.assert_has_calls([mock.call(mock_ebook, firstPage), mock.call(mock_ebook, secondPage)])

@mock.patch('ebooklib.epub.EpubBook')
@mock.patch('grimoireebook.addThemePagesToEbook')
def test_shouldAddThemesToGrimoireBook(mock_addThemePagesToEbook, mock_ebook):
	firstThemeSet = ('firstThemeSet',)
	secondThemeSet = ('secondThemeSet',)

	mock_addThemePagesToEbook.side_effect = [firstThemeSet, secondThemeSet]

	firstTheme = { 'themeName' : 'theme_1'}
	secondTheme = { 'themeName' : 'theme_2'}

	grimoireData = {
						'themes' : [ firstTheme, secondTheme]
					}

	themeSets = grimoireebook.addThemeSetsToEbook(mock_ebook, grimoireData)

	assert type(themeSets[0][0]) is epub.Section
	assert themeSets[0][0].title == firstTheme['themeName']
	assert themeSets[0][1] == firstThemeSet
	assert type(themeSets[1][0]) is epub.Section
	assert themeSets[1][0].title == secondTheme['themeName']
	assert themeSets[1][1] == secondThemeSet

	mock_addThemePagesToEbook.assert_has_calls([mock.call(mock_ebook, firstTheme), mock.call(mock_ebook, secondTheme)])

@mock.patch('ebooklib.epub.write_epub')
@mock.patch('ebooklib.epub.EpubBook')
@mock.patch('grimoireebook.addThemeSetsToEbook')
@mock.patch('grimoireebook.dowloadGrimoireImages')
def test_shouldCreateGrimoireEpub(mock_dowloadGrimoireImages, mock_addThemeSetsToEbook, mock_ebook, mock_epubWrite):
	grimoireDefinition = {}
	mock_addThemeSetsToEbook.return_value = ()

	with mock.patch('grimoireebook.open', mock.mock_open(read_data="dummyCoverImageData")):
		grimoireebook.createGrimoireEpub(grimoireDefinition, mock_ebook)

		mock_ebook.set_identifier.assert_called_with('destinyGrimoire')
		mock_ebook.set_title.assert_called_with('Destiny Grimoire')
		mock_ebook.set_language.assert_called_with('en')
		mock_ebook.add_author.assert_called_with('Bungie')
		mock_ebook.set_cover.assert_called_with('cover.jpg', "dummyCoverImageData")

		mock_dowloadGrimoireImages.assert_called_once_with(grimoireDefinition)
		mock_addThemeSetsToEbook.assert_called_once_with(mock_ebook, grimoireDefinition)

		mock_ebook.add_item.assert_has_calls([call(BookStyleItemMatcher()), call(ItemTypeMatcher(epub.EpubNcx)), call(ItemTypeMatcher(epub.EpubNav))], any_order=True)

		mock_epubWrite.assert_called_once_with(grimoireebook.DEFAULT_BOOK_FILE, mock_ebook)

		mock_ebook.toc == mock_addThemeSetsToEbook.return_value

class BookStyleItemMatcher:
	def __eq__(self, other):
		return other.id == 'style_default' and other.file_name == 'style/default.css' and other.media_type == 'text/css' and other.content == grimoireebook.DEFAULT_PAGE_STYLE

class ItemTypeMatcher:
	def __init__(self, expectedType):
		self.expectedType = expectedType

	def __eq__(self, arg):
		return type(arg) is self.expectedType

	def __repr__(self):
		return 'Item Type Matcher for %s' % self.expectedType