from myparser.website.biquge5200 import Biquge5200
from myparser.website.booktxt import Booktxt
from myparser.website.quanshuwang import QuanShuWang

SUPPORTED_WEBSITE = [
    Biquge5200.HOST,
    Booktxt.HOST,
    QuanShuWang.HOST
]
MAP_CLASS = {
    Biquge5200.HOST: Biquge5200,
    Booktxt.HOST: Booktxt,
    QuanShuWang.HOST: QuanShuWang
}
