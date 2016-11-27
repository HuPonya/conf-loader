# conf-loader
将环境变量中的值注入到项目配置中。


### 使用
进入实际部署的项目中，执行`python /this/a/app/path/conf-loader/main.py`即可。conf-loader会读取项目根目录（当前目录）下`.ci/config/config.yml`来生成配置文件。

### 配置
实例配置[sample_config.yml](sample_config.yml)。
配置类别：

 - tpl，jinjia2模板。模板中的值皆为系统环境变量。
 - gitlab，从gitlab代码库中下载配置文件。其配置文件路径由`gitlab_baseurl`和配置项name为key的系统环境变量组成。

### Docker化
conf-loader将被作为基础服务被添加到Python镜像中。路径为为`/app/conf-loader/`。
