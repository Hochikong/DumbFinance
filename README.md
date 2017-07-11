介绍(Introduction)
=================

这是我的个人实验性项目，使用Python3和DL完成我的自动交易工作  
This is my personal project,use Python and Deep Learning etc, make
me become a Quant(green hand :) )   

可以检查FastSolution目录中的内容，ETL.py、Model.py、Feedback.py以进行实验，但是需要部署好
MongoDB、Neo4j和Keras。  
You can check the FastSolution directory to use ETL.py,Model.py and Feedback.py.But first you should install 
and configure MongoDB and Neo4j and Keras.
 
ETL.py：读入训练数据进行预处理并存入MongoDB，数据可以从FastSolution/TrainData获得，格式为
xls。  
Model.py：从指定的数据库和表读入先前存入的数据，根据配置的参数训练模型并保存结果。  
Feedback.py：加载前面已经保存的模型，用户既可以在Python解释器里导入这个模块并实例化Analysis
类进行分析，详见文件内的Cypher语句。  
config.ini：保存着全部配置参数。  

如果想使用Splinter自动登录Neo4j的浏览器页面和使用BosonNLP的NER服务，需要提前export相关
变量：  
export BOSON_TOKEN=你的TOKEN  
export NEO4J_NAME=USERNAME  
export NEO4J_PASSWD=PASSWD  


用了什么(What,tech?)
==================

MongoDB  
Neo4j  
Keras(Tensorflow Backend)  
Docker(Deploy MongoDB and Neo4j) 

依赖(Requirements)
==================
pymongo  
jieba   
Keras  
matplotlib  
splinter  
BosonNLP  
neo4j  
h5py



