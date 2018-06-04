# Epiphron
## 一、项目简介
&emsp;&emsp;本项目是一个基于事件驱动框架的量化交易回测平台。现阶段本项目以学习为目的，并不存在任何其他用途。项目本身还有很多欠缺和不足，希望能在以后不断地迭代，最终打造成一个能够进行实盘交易的量化交易平台。
## 二、系统逻辑
&emsp;&emsp;回测系统的基本逻辑是：从数据源获取数据信息，将数据信息作为market事件接收后，不断触发系统其他部分所处反应，直到事件序列为空，系统再次获取数据信息，如此循环直到结束。整个回测系统在一次循环中的流程如下图所示。  

![image](https://github.com/mai1346/Epiphron/raw/master/images/process.png)

1. 从Data（数据源）获取新的数据信息，作为Market事件推送到事件序列。（上图①）
2. 系统把Market事件推送给Strategy，Strategy生成Signal事件。（上图②、③）
3. RiskManager接收Signal事件，并根据风控发出有效的Order事件。（上图④、⑤）
4. 由Execution接收Order事件，并根据执行结果发出Fill事件。（上图⑥、⑦）
5. Portfolio根据收到的Fill事件更新portfolio信息，并触发tradelog进行记录。（上图⑧）
## 三、功能介绍
&emsp;&emsp;
