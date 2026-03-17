import os
import pandas as pd
import jieba
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# 读取评论
df = pd.read_csv("bilibili_comments_BV1KxNPzSEhF.csv")

text = " ".join(df["comment"].astype(str))

# 停用词
filename = "stopwords.txt"

if not os.path.exists(filename):
    with open(filename, "w", encoding="utf-8") as f:
        f.write("的\n了\n是\n啊\n吧\n这个\n那个\n")
    print("已创建 stopwords.txt")
else:
    print("stopwords.txt 已存在")

# 停用词
with open("stopwords.txt", encoding="utf-8") as f:
    stopwords = set(f.read().splitlines())

# 分词
words = [w for w in jieba.cut(text) if w not in stopwords]

result = " ".join(words)

# 生成词云
wc = WordCloud(
    font_path="simhei.ttf",
    width=1000,
    height=500,
    background_color="white"
).generate(result)

plt.imshow(wc)
plt.axis("off")
plt.show()

wc.to_file("bilibili_wordcloud.png")
