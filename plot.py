from pyecharts.globals import CurrentConfig, NotebookType

CurrentConfig.NOTEBOOK_TYPE = NotebookType.NTERACT

import pyecharts.options as opts
from pyecharts.charts import Bar, Line

bar = (
    Bar()
        .add_xaxis(["衬衫", "羊毛衫", "雪纺衫", "裤子", "高跟鞋", "袜子"])
        .add_yaxis("商家A", [5, 20, 36, 10, 75, 90])
        .add_yaxis("商家B", [15, 6, 45, 20, 35, 66])
        .set_global_opts(title_opts=opts.TitleOpts(title="主标题", subtitle="副标题"))
)

bar.render()
