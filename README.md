~~~
src/endpoints/users-internal.js
src/middleware/ip-whitelist.js
src/config.default.js
~~~
### 1.主要接口文件:

~~~
src/endpoints/users-internal.js
~~~

### 2.IP白名单相关文件:

~~~
src/middleware/ip-whitelist.js
src/config.default.js
~~~

### 上传步骤

1.首先修改服务器上的 src/config.default.js，添加允许访问的IP白名单：

~~~
export const internalApiWhitelist = [
    '127.0.0.1',      // localhost
    '::1',            // localhost IPv6
    '你的服务器IP/24'  // 根据实际情况配置
];
~~~

2.确保服务器的 server.js 中已经正确引入和挂载了这个路由：

~~~
import { loadPlugins } from './src/plugin-loader.js';
import { router as usersInternalRouter } from './src/endpoints/users-internal.js';//增
import { router as usersLngRouter } from './src/endpoints/users-lng.js';//增
...
app.use(setUserDataMiddleware);
// Internal endpoints (no auth required)
app.use(bodyParser.json());//增
app.use('/api/users-internal', usersInternalRouter);//增
app.use('/api/users-lng', usersLngRouter);//增
~~~

3.上传完成后需要重启服务器使配置生效。

安全提醒：

确保在 config.default.js 中正确配置了允许访问的IP白名单

建议只允许特定的IP地址访问这个内部API

如果可能，建议配置防火墙规则作为额外的安全层

~~~

sudo cp -f /opt/SillyTavern/public/register.html /opt/a/SillyTavern/public/
sudo cp -f /opt/SillyTavern/public/login.html /opt/a/SillyTavern/public/
sudo cp -f /opt/SillyTavern/public/scripts/register.js /opt/a/SillyTavern/public/scripts/

// 登录提示
/opt/a/SillyTavern/src/endpoints/users-public.js
router.post('/login', jsonParser, async (request, response) => {
    try {
        if (!request.body.handle) {
            console.warn('Login failed: Missing required fields');
            return response.status(400).json({ error: '缺少必要用户名或密码' });
        }

        const ip = getIpFromRequest(request);
        await loginLimiter.consume(ip);

        /** @type {import('../users.js').User} */
        const user = await storage.getItem(toKey(request.body.handle));

        if (!user) {
            console.error('Login failed: User', request.body.handle, 'not found');
            return response.status(403).json({ error: '用户不存在' });
        }

        if (!user.enabled) {
            console.warn('Login failed: User', user.handle, 'is disabled');
            return response.status(403).json({ error: '用户已被禁用[已经到期]' });
        }

        if (user.password && user.password !== getPasswordHash(request.body.password, user.salt)) {
            console.warn('Login failed: Incorrect password for', user.handle);
            return response.status(403).json({ error: '密码错误' });
        }

        if (!request.session) {
            console.error('Session not available');
            return response.sendStatus(500);
        }

        await loginLimiter.delete(ip);
        request.session.handle = user.handle;
        console.info('Login successful:', user.handle, 'from', ip, 'at', new Date().toLocaleString());
        return response.json({ handle: user.handle });
    } catch (error) {
        if (error instanceof RateLimiterRes) {
            console.error('Login failed: Rate limited from', getIpFromRequest(request));
            return response.status(429).send({ error: 'Too many attempts. Try again later or recover your password.' });
        }

        console.error('Login failed:', error);
        return response.sendStatus(500);
    }
});
~~~
