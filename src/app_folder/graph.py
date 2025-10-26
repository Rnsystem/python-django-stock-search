import matplotlib.pyplot as plt
import base64
from io import BytesIO

#プロットしたグラフを画像データとして出力するための関数
def Output_Graph():
	buffer = BytesIO()                   #バイナリI/O(画像や音声データを取り扱う際に利用)
	plt.savefig(buffer, format="png")    #png形式の画像データを取り扱う
	buffer.seek(0)                       #ストリーム先頭のoffset byteに変更
	img   = buffer.getvalue()            #バッファの全内容を含むbytes
	graph = base64.b64encode(img)        #画像ファイルをbase64でエンコード
	graph = graph.decode("utf-8")        #デコードして文字列から画像に変換
	buffer.close()
	return graph


#グラフをプロットするための関数
def Plot_Graph(x,y,y2,y3):
    fig, ax1 = plt.subplots( )
    fig.set_figheight(6)
    fig.set_figwidth(10)
    plt.xticks(rotation=45)
    # グラフの結合
    ax2 = ax1.twinx()
    ax3 = ax1.twinx()
    ax4 = ax1.twinx()
    # reviewCount
    # reviewAverage
    # price
    # rank
    ax1.plot(x,y,"b-",label=False)
    ax2.plot(x,y2,"r-",label=False)
    ax3.plot(x,y3,"g-",label=False)
    # ax4.plot(x,y4,"y-",label=False)
    ax3.spines["right"].set_position(("outward", 50))
    # ax4.spines["right"].set_position(("outward", 100))
    ax1.set_ylabel("レビュー数", fontname="MS Gothic")
    ax2.set_ylabel("レビュー平均", fontname="MS Gothic")
    ax3.set_ylabel("販売価格", fontname="MS Gothic")
    # ax4.set_ylabel("ランキング", fontname="MS Gothic")
    ax1.yaxis.label.set_color('#0000ff')
    ax2.yaxis.label.set_color('#ff0000')
    ax3.yaxis.label.set_color('#00ff00')
    # ax4.yaxis.label.set_color('#ffff00')
    # y軸の最小値、最大値を決める。（逆さまにするために、最大値, 最小値という順番で指定する）
    ax2.set_ylim([0, 5])
    # ax4.set_ylim([max(y4), min(y4)])
    ax4.set_ylim([999, 1])
    # 描画処理
    plt.tight_layout()
    graph = Output_Graph()
    return graph



#グラフをプロットするための関数
def Plot_Graph4(x,y,y2):
    fig = plt.figure()
    ax1 = fig.add_subplot(1, 2, 1)   #1行２列の１番目
    ax1.plot(x,y,label="reviewCount")
    ax1.set_title("reviewCount")
    plt.xticks(rotation=45)          #X軸値を45度傾けて表示
    plt.legend(fontsize=15)
    ax2 = fig.add_subplot(1, 2, 2)   #１行２列の２番目
    ax2.plot(x,y2,label="reviewAverage")
    ax2.set_title("reviewAverage")
    plt.xticks(rotation=45)          #X軸値を45度傾けて表示
    plt.legend(fontsize=15)
    plt.tight_layout()
    graph = Output_Graph()           #グラフプロット
    return graph

#グラフをプロットするための関数
def Plot_Graph3(x,y,y2):
    fig = plt.figure()
    ax1 = fig.add_subplot(1, 2, 1)   #1行２列の１番目
    ax1.plot(x,y,label="reviewCount")
    ax1.set_title("reviewCount")
    plt.xticks(rotation=45)          #X軸値を45度傾けて表示
    plt.legend(fontsize=15)
    ax2 = fig.add_subplot(1, 2, 2)   #１行２列の２番目
    ax2.plot(x,y2,label="reviewAverage")
    ax2.set_title("reviewAverage")
    plt.xticks(rotation=45)          #X軸値を45度傾けて表示
    plt.legend(fontsize=15)
    plt.tight_layout()
    graph = Output_Graph()           #グラフプロット
    return graph

#グラフをプロットするための関数
def Plot_Graph2(x,y):
    plt.switch_backend("AGG")        #スクリプトを出力させない
    plt.plot(x,y,label="reviewCount")
    plt.plot(x,y2,label="reviewAverage")
    plt.xticks(rotation=45)          #X軸値を45度傾けて表示
    plt.title("Revenue per Date")    #グラフタイトル
    plt.xlabel("Date")               #xラベル
    plt.ylabel("Reveue")             #yラベル
    plt.legend(fontsize=15)
    plt.tight_layout()               #レイアウト
    graph = Output_Graph()           #グラフプロット
    return graph