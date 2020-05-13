#### 依赖库:Authlib
```
https://github.com/lepture/authlib
python3 -m pip install Authlib==0.14.2
```

#### 服务端支持模式
1. 授权码授权模式（Authorization code Grant）
2. 隐式授权模式（Implicit Grant）
3. 密码模式（Resource Owner Password Credentials Grant）
4. 客户端凭证模式（Client Credentials Grant）
5. 其中授权码模式最常用,使用也是最复杂,推荐使用


### 例子:
###### tip: 在本地测试:必须配置域名 /etc/hosts 
##### 授权码模式：
##### 使用授权服务，需要申请 client_id,client_secret

具体配置可以参考:[https://user-images.githubusercontent.com/290496/38811988-081814d4-41c6-11e8-88e1-cb6c25a6f82e.png]

- Client Name[客户端名称]:可以任意字符串
- Client URI[服务端的url]: http://example.com/   #/etc/hosts 中配置的 127.0.0.1 example.com
- Allowed Scope[服务端资源的权限]: profile user email 多个资源用空格
- Redirect URIs[授权后重定向到客户端的url]: http://example.com/authorize
- Allowed Grant Types[授权模式]: authorization_code(必填项)  refresh_token(可选)
- Allowed Response Types[返回类型]: code
- Token Endpoint Auth Method[验证的算法]:client_secret_basic


需要用到的表:
1. 用户表自定义
```
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True)
    
    def __str__(self):
        return self.username

    def get_user_id(self):
        return self.id

    def check_password(self, password):
        return password == 'valid'
```
2. 客户端配置表,用来存储客户端的配置信息
```
class OAuth2Client(db.Model, OAuth2ClientMixin):
    __tablename__ = 'oauth2_client'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    user = db.relationship('User')
```

3. 服务端报保存中间结果code的表,code 只能使用一次
```
class OAuth2AuthorizationCode(db.Model, OAuth2AuthorizationCodeMixin):
    __tablename__ = 'oauth2_code'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    user = db.relationship('User')
```

4. 服务保存 token 的表,最终的令牌保存的地方
```
class OAuth2Token(db.Model, OAuth2TokenMixin):
    __tablename__ = 'oauth2_token'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    user = db.relationship('User')
    def is_refresh_token_active(self):
        if self.revoked:
            return False
        expires_at = self.issued_at + self.expires_in * 2
        return expires_at >= time.time()
```

