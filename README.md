# Epiphron
## 一、项目简介
&emsp;&emsp;本项目是一个基于事件驱动框架的量化交易回测平台。现阶段本项目以学习为目的，并不存在任何其他用途。项目本身还有很多欠缺和不足，希望能在以后不断地迭代，最终打造成一个能够进行实盘交易的量化交易平台。
## 二、系统逻辑
&emsp;&emsp;回测系统的基本逻辑是：从数据源获取数据信息，将数据信息作为market事件接收后，不断触发系统其他部分所处反应，直到事件序列为空，系统再次获取数据信息，如此循环直到结束。整个回测系统在一次循环中的流程如下图所示。  

![process](https://github.com/mai1346/Epiphron/raw/master/images/process.png)

1. 从Data（数据源）获取新的数据信息，作为Market事件推送到事件序列。（上图①）
2. 系统把Market事件推送给Strategy，Strategy生成Signal事件。（上图②、③）
3. RiskManager接收Signal事件，并根据风控发出有效的Order事件。（上图④、⑤）
4. 由Execution接收Order事件，并根据执行结果发出Fill事件。（上图⑥、⑦）
5. Portfolio根据收到的Fill事件更新portfolio信息，并触发tradelog进行记录。（上图⑧）
## 三、功能介绍
1. 支持从MySQL数据库、tushare获取数据进行回测。
2. 支持多个标的资产的组合。
3. 支持基础的Performance计算，包括夏普比率，sortino比率，最大回撤。
4. 资金曲线及回撤曲线的图形化展示。
5. 支持详细的trade信息记录，包括每个标的资产trade的进入日期、进入市价、交易数量、退出日期、退出市价、每笔交易盈利以及累计盈利等。
6. 支持trade summary，包括胜率、最大盈利、最大损失和平均盈利。
7. 支持trade的图形化展示。  

一个典型的回测结果图形化展示如下图，本结果是的EMA Crossing策略在600050和600233两只股票的应用。  

![equity curve](https://github.com/mai1346/Epiphron/raw/master/images/equitycurve.png)

图中绿色区域为策略表现好于基准的部分，红色为劣于基准的部分。  

![trade plot](https://github.com/mai1346/Epiphron/raw/master/images/tradeplot.png)

图中标出了针对每个标的资产的买入卖出点。
## 四、使用说明
&emsp;&emsp;一个Strategy类的初始化需要接受至少两个参数，`data_handler`以及`events`这两个类。其中`data_handler`获取symbol最新N个交易日收盘价‘close’数据的方法是`bars = self.data_handler.get_latest_bars_values(symbol, "close", N = N)`。如果要获取从回测日起开始以来所有的数据，则需令`N = 0`。`get_latest_bars_values`方法返回的是`numpy.array`。根据自己的策略来生成Signal事件，并推送到event序列（`self.events.put(signal)`）就可以了。更详细的事例请看example中的示例。
