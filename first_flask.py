from flask import Flask,request
import gongGaoDeal as gg
import os
from gensim.models import Word2Vec

'''思路
第一 ：配置工作目录 ，将xml文件和停止词放到该目录下
第二：如果没有xml文件，则设为空 ，可进行分词和训练


'''

helptext="<h4>http:/host/os 显示python的工作目录</h4> \n\
\n\
<h4>http:/host/os/chdir?dirpath=输入改变目录（不加引号）  改变python的工作目录</h4>\n\
\n\
<h4>http:/host/help 显示使用方式</h4> \n\
\n\
<h4>http:/host/deal?name=xml所在文件夹名字（不加引号） 输入xml所在路径 ，将xml文件生成为txt文本 \n\
    example: http:/127.0.0.1:5000/deal?name=test_file </h4>\n\
\n\
<h4>http:/host/deal/seg?pathtxt=准备分词的文本文件名，带后缀 对文本进行分词  \n\
    example:http:/127.0.0.1:5000/deal/seg?pathtxt=allGongGao.txt </h4>\n\
    <h5>如果没有添加停止词库，需要这样：\n\
    example:http:/127.0.0.1:5000/deal/seg?pathtxt=allGongGao.txt&stopwords=stopwords</h5>\n\
\n\
<h4>http:/host/deal/train 对分好词的文本进行训练\n\
    example:http:/127.0.0.1:5000/deal/train 默认分词文本名字为seg_words.txt\n\
    训练好的文本名字为vectors.txt，工作引擎数量为1</h4>\n\
    <h5>如果想添加分词文本，可以这样做：\n\
    example:http:/127.0.0.1:5000/deal/train?segment=seg_words1.txt</h5>\n\
    <h5>如果想修改训练好的文本名字，可选txt和bin格式，可以这样做：\n\
    example:http:/127.0.0.1:5000/deal/train?train=vectors1.txt</h5>\n\
    <h5>如果想改变工作引擎的个数，可以这样做：\n\
    example:http:/127.0.0.1:5000/deal/train?worker=2</h5>\n\
    <h5>如果想同时修改以上多个参数，用&连接\n\
    example:http:/127.0.0.1:5000/deal/train?worker=2&segment=seg_words1.txt</h5>\n\
\n\
<h4>http:/host/word2vec/file_name/word_name/num 取单个词语的前num个相似词语\n\
    example:http:/127.0.0.1:5000/word2vec/vector.txt/控股/20 </h4>\n\
\n\
<h4>http:/host/out?path=输入词语&train=训练好的文本名字&num=输出的词语个数&out=输出的文件名字（带.txt)\n\
    example: http:/127.0.0.1:5000/out?path=test.txt&train=vector.txt&num=30\n\
    num 默认为20个 参数可不填 \n\
    train默认为vector.txt，可不填\n\
    out 默认为result.txt,可不填 \n\
    path 必须提供\n\<、h4>"


    



app=Flask(__name__)
@app.route('/deal')
def begin_deal():
    '''显示文件个数，并进行txt转化'''
    name=request.args.get('name')
    tw=gg.TrainWord(name)
    if name!='':
        tw.getSentencesText()
        return '一共有{0}个文件,现在文件转化完毕，生成文件allGongGao.txt'.format(tw.len_xml)
    else:
        return '没有xml文件'
#dirpath='C:\\Users\\Administrator\\test_file'
#==============================================================================
# @app.route('/test')
# def test1():
#     name=request.args.get('name')
#     path=os.path.join(os.getcwd(),name)
#     if os.path.exists(path):
#         return '路径存在'
#     else:
#         return path
#==============================================================================
	
@app.route('/deal/seg')
def segment():
    '''对整理好的文件进行分词'''
    path_stopwords=request.args.get('stopwords','')
    path=request.args.get('pathtxt','')
    if path =='':
        path_txt=os.path.join(os.getcwd(),'allGongGao.txt')
        if not os.path.exists(path_txt):
            raise gg.NameError('文本不存在')
    else:
        path_txt=os.path.join(os.getcwd(),path)
        if not os.path.exists(path_txt):
            raise gg.NameError('文本不存在')
    tw=gg.TrainWord('')
    if path_stopwords=='':
        path_stopwords=os.path.join(os.getcwd(),'chinese_stopword.txt')
        if not os.path.exists(path_stopwords):
            raise gg.NameError('停止词库不存在')
    else:
        path_stopwords=os.path.join(os.getcwd(),path_stopwords)
        if not os.path.exists(path_stopwords):
            raise gg.NameError('停止词库不存在')

    tw.cut_words(path_stopwords,path_txt)
    return '分词结束,生成seg_words.txt'
    
#==============================================================================
@app.route('/deal/train')
def train():     
    '''对分好词的文本进行训练'''
    path_seg=request.args.get('segment','')
    path_train=request.args.get('train','')
    worker=request.args.get('worker','')
    tw=gg.TrainWord('')
    if path_seg=='':
        path_seg=os.path.join(os.getcwd(),'seg_words.txt')
        if not os.path.exists(path_seg):
            raise gg.NameError('分词文本不存在')
    else:
        path_seg=os.path.join(os.getcwd(),path_seg)
        if not os.path.exists(path_seg):
            raise gg.NameError('分词文本不存在')
    if path_train=='':
        path_train='vectors.txt'
    if worker=='':
        num=1
    else:
        num=int(worker)
    tw.train_word2vec(path_segtxt=path_seg,workers=num,path_train=path_train)
    return '训练结束，生成{0}文件'.format(path_train)
    
@app.route('/out')    
def in_out():
    '''输入一系列词语 输出文本相似度词语'''
    path=request.args.get('path','')
    train=request.args.get('train','')
    num=request.args.get('num','')
    out_file=request.args.get('out','')
    if path=='':
        raise gg.NameError('输入文本不存在')
    else:
        path=os.path.join(os.getcwd(),path)
        if not os.path.exists(path):
            raise gg.NameError('输入文本不存在')  
    if train=='':
        train=os.path.join(os.getcwd(),'vectors.txt')
        if not os.path.exists(train):
            raise gg.NameError('训练好的文本不存在')  
    else:
        train=os.path.join(os.getcwd(),train)
        if not os.path.exists(train):
            raise gg.NameError('训练好的文本不存在')   
    if num=='':
        num=20
    else:
        num=int(num)
    if out_file=='':
        out_file='result.txt'        
    gg.in_out(path,train_path=train,num=num,file_name=out_file)
    return '相似度计算完成，生成{0}文件'.format(out_file)
    
@app.route('/word2vec/<file>/<word>/<num>')
def most_similar(file,word,num):
    '''取得单个词的相似词语'''
    file=os.path.join(os.getcwd(),file)
    if not os.path.exists(file):
        raise gg.NameError('训练好的文本不存在')
    models=Word2Vec.load(file)
    list1=models.most_similar(str(word),topn=int(num))
    return str(list1)
#=======================================路径操作=====================================
@app.route('/os')
def getcwd():
    '''显示python的工作目录'''
    return '工作目录是{0}'.format(os.getcwd())
    
@app.route('/os/chdir')
def chdir():
    '''改变python的工作目录'''
    dirpath=request.args.get('dirpath','')
    os.chdir(dirpath)
    return '工作目录改变成功，现在目录是{0}'.format(os.getcwd())

@app.route('/help')
def help_deal():
    '''显示各个参数使用方法'''
    return helptext

    
if __name__ == '__main__':
    app.run(debug=True)
