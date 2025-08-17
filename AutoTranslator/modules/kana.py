# # TODO: 漢字の読み間違えなくしたい
# import vibrato
# import zstandard
# dctx = zstandard.ZstdDecompressor()

# tokenizer: vibrato.Vibrato = None

# with open('ipadic-mecab-2_7_0/system.dic.zst', 'rb') as fp:
#      with dctx.stream_reader(fp) as dict_reader:
#         tokenizer = vibrato.Vibrato(dict_reader.read())
        

# def kana_convert(sentence: str):
#     tokens = tokenizer.tokenize(sentence)

#     for token in tokens:
#         print(token.surface(), token.feature().split(",")[-1])

# kana_convert("私の名前はくろすけです。")

import pyopenjtalk

sentence = "こんいちは、私はくろすけです。Nice to meet you!"

convert = pyopenjtalk.g2p("")