#coding:utf-8

from flask import render_template,request
import logging
from website.app import create_app

logging.basicConfig(level=logging.DEBUG)



"""
GRANT_TYPES_EXPIRES_IN = {
        'authorization_code': 864000,
        'implicit': 3600,
        'password': 864000,
        'client_credentials': 864000
    }
"""

app = create_app({
    'SECRET_KEY': 'secret',
    'OAUTH2_TOKEN_EXPIRES_IN':{'authorization_code':120},
    'OAUTH2_ACCESS_TOKEN_GENERATOR':True,
    'OAUTH2_REFRESH_TOKEN_GENERATOR': True,
    'SQLALCHEMY_TRACK_MODIFICATIONS': True,
    # 'SQLALCHEMY_DATABASE_URI': 'sqlite:///db.sqlite',
    'SQLALCHEMY_DATABASE_URI': 'mysql+pymysql://root:root@127.0.0.1:3306/oauth2?charset=utf8mb4'
})


@app.errorhandler(404)
def miss(e):
    """
    404、405错误仅会被全局错误处理函数捕捉，如区分蓝本URL下的404和405错误，
    在全局定义的404错误处理函数中使用request.path.startswith('<蓝本的URL前缀>')
    来判断请求的URL是否属于某个蓝本。
    :param e:
    :return:
    """
    if request.path.startswith('/'):
        return render_template('404.html'), 404
    return render_template('404.html'), 404

@app.errorhandler(500)
def error(e):
    """
    :param e:
    :return:
    """
    return render_template('500.html'), 500


app.run(host='127.0.0.1',
        port=5000,
        debug=True,)
        # ssl_context='adhoc')
        # ssl_context=('ca/server.crt','ca/server.key'))
