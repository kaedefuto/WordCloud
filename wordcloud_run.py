import os
import MeCab
from pyknp import Juman
from wordcloud import WordCloud
import subprocess
import re

"""出力する品詞リスト"""
OUT_POS_LIST = ["名詞", "形容詞"]

"""ストップワードファイル"""
STOP_WORDS_FILE = "stop_words.txt"

"""ファイル"""
input_dir = "input"
output_dir = "output"
file_name_list = ["test"]

###########################################################

def _mecab(text, size="10000000"):
    """mecab(subprocess)"""
    #@param: text テキスト, size 最大文字数
    #@return: Mecab型テキスト
    output = subprocess.run(["mecab", "-b", size], input=text+"\n",
                            encoding="utf-8", stdout=subprocess.PIPE)
    return output.stdout


def morphological_analysis(text: str) -> list:
    """形態素解析(subprocess)"""
    #@return: double list e.g.) [["すもも", "名詞", "一般", "*", "*", "*", "*", "すもも", "スモモ", "スモモ"]]
    mData = _mecab(text)
    dataList = [re.split(r"[\t,', ']", idx) for idx in mData.split("\n")]
    dataList = [idx for idx in dataList if len(idx) > 1]  # delete EOS or None
    return dataList

def mecab_wakati(text):
    """形態素解析"""
    tagger = MeCab.Tagger("-Owakati")  # 分かち書き
    parse = tagger.parse(text)
    return parse

def juman_wakati(text):
    """形態素解析"""
    juman = Juman()
    analysis = juman.analysis(text)
    result = ""
    for m in analysis.mrph_list():
        result += str(m.midasi) +" "
    return result


class WordCloudGenerator:
    """WordCloud"""

    def __init__(self, font_path, background_color, width, height, collocations,
                 stopwords, max_words, regexp):
        self.font_path = font_path
        self.background_color = background_color
        self.width = width
        self.height = height
        self.collocations = collocations
        self.stopwords = stopwords
        self.max_words = max_words
        self.regexp = regexp

    def wordcloud_draw(self, parse):
        self.wordcloud = WordCloud(font_path=self.font_path, background_color=self.background_color, width=self.width, height=self.height,
                                   collocations=self.collocations, stopwords=self.stopwords, max_words=self.max_words, regexp=self.regexp, repeat=False)
        self.wordcloud.generate(parse)
        self.wordcloud.to_file(self.out_file_name)


def main(input_file):

    """入力"""
    input_file_path = os.path.join(input_dir, input_file + ".txt")
    with open(input_file_path, "r", encoding="utf-8") as f:
        CONTENTS = f.read().splitlines()
        CONTENTS = [content for content in CONTENTS if not content == ""]

    """形態素解析"""
    # 表層形\t品詞,品詞細分類1,品詞細分類2,品詞細分類3,活用型,活用形,原形,読み,発音
    surfaces = []
    for content in CONTENTS:
        morphologic_results = morphological_analysis(content)
        for mr in morphologic_results:
            if mr[1] in OUT_POS_LIST:
                if mr[-3] not in ["*"]:
                    surfaces.append(mr[-3])  # 基本形
    wakati_text = " ".join(surfaces)

    """
    #全単語
    for content in CONTENTS:
        wakati_text+=mecab_wakati(content)
        wakati_text+=juman_wakati(content)
    print(wakati_text)
    """

    """WORD CLOUD"""
    #WordCloudのパラメータ
    """
    デフォルトパラメータ
    width:400
    height:200
    backgraound_color:black
    colormap(文字色):None
    collocations(連語):True
    stopwords:None
    max_words:200
    regexp(表示される文字の正規表現):r"\w[\w']+"
    """
    FONT_FILE = "/System/Library/Fonts/ヒラギノ明朝 ProN.ttc"  # フォントファイルのパス
    COLOR = "white"
    WIDTH = 1000  # 出力画像の幅
    HEIGHT = 1000  # 出力画像の高さ
    MAX_WORDS = 2000  # 出力個数の上限
    COLLOCATIONS = False
    with open(STOP_WORDS_FILE, "r", encoding="utf-8") as f: # ストップワード
        STOP_WORDS = set(f.read().splitlines())

    #パラメータの設定
    wordCloudGenerator = WordCloudGenerator(font_path=FONT_FILE, background_color=COLOR, width=WIDTH, height=HEIGHT,
                                            collocations=COLLOCATIONS,stopwords=STOP_WORDS, max_words=MAX_WORDS, regexp=r"[\w']+")

    # 出力ファイルパス設定
    OUTPUT_FILE_PATH = os.path.join(output_dir, input_file + ".png")
    wordCloudGenerator.out_file_name = OUTPUT_FILE_PATH
    # 出力
    wordCloudGenerator.wordcloud_draw(wakati_text)


if __name__ == "__main__":

    for input_file in file_name_list:
        main(input_file)

    print("完了")
