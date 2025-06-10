// src/endpoints/users-lng.js
import express from 'express';
import fetch from 'node-fetch';

const router = express.Router();
const API_BASE = 'http://IP:2824/st';

// 注册账号接口
router.post('/register', async (req, res) => {
    try {
        console.log('注册请求参数:', req.body);
        
        // 设置5秒超时
        const controller = new AbortController();
        const timeout = setTimeout(() => {
            controller.abort();
        }, 15000);
        
        try {
            const response = await fetch(`${API_BASE}/sign`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    user_id: req.body.user_id,
                    password: req.body.password,
                    key: req.body.key
                }),
                signal: controller.signal
            });

            clearTimeout(timeout);

            if (!response.ok) {
                throw new Error(`请求错误！状态码: ${response.status}`);
            }

            const data = await response.json();
            console.log('API响应数据:', data);
            
            // 如果status是ON，说明有错误
            if (data.status === 'ON') {
                let errorMessage = data.error;
                // 直接返回API的错误信息
                console.log('错误信息:', errorMessage);
                return res.status(400).json({ error: errorMessage });
            }

            // 否则直接返回响应
            res.json(data);
        } catch (fetchError) {
            clearTimeout(timeout);
            if (fetchError.name === 'AbortError') {
                console.error('请求超时');
                return res.status(504).json({ error: '注册请求超时，请稍后重试' });
            }
            throw fetchError;
        }
    } catch (error) {
        console.error('注册错误:', error);
        res.status(500).json({ error: '注册失败，服务器错误' });
    }
});

// 续费授权接口
router.post('/add_license', async (req, res) => {
    try {
        console.log('续费请求参数:', req.body);
        
        // 设置5秒超时
        const controller = new AbortController();
        const timeout = setTimeout(() => {
            controller.abort();
        }, 15000);
        
        try {
            const response = await fetch(`${API_BASE}/add_license`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    user_id: req.body.user_id,
                    key: req.body.key
                }),
                signal: controller.signal
            });

            clearTimeout(timeout);

            if (!response.ok) {
                throw new Error(`请求错误！状态码: ${response.status}`);
            }

            const data = await response.json();
            console.log('API响应数据:', data);
            
            // 如果status是ON，说明有错误
            if (data.status === 'ON') {
                let errorMessage = data.error;
                // 直接返回API的错误信息
                console.log('错误信息:', errorMessage);
                return res.status(400).json({ error: errorMessage });
            }

            // 否则直接返回响应
            res.json(data);
        } catch (fetchError) {
            clearTimeout(timeout);
            if (fetchError.name === 'AbortError') {
                console.error('请求超时');
                return res.status(504).json({ error: '续费请求超时，请稍后重试' });
            }
            throw fetchError;
        }
    } catch (error) {
        console.error('续费错误:', error);
        res.status(500).json({ error: '续费失败，服务器错误' });
    }
});

// 修改密码接口
router.post('/change_password', async (req, res) => {
    try {
        console.log('修改密码请求参数:', req.body);
        
        // 设置5秒超时
        const controller = new AbortController();
        const timeout = setTimeout(() => {
            controller.abort();
        }, 15000);
        
        try {
            const response = await fetch(`${API_BASE}/change_password`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    user_id: req.body.user_id,
                    password: req.body.password,
                    key: req.body.key
                }),
                signal: controller.signal
            });

            clearTimeout(timeout);

            if (!response.ok) {
                throw new Error(`请求错误！状态码: ${response.status}`);
            }

            const data = await response.json();
            console.log('API响应数据:', data);
            
            // 如果status是ON，说明有错误
            if (data.status === 'ON') {
                let errorMessage = data.error;
                // 直接返回API的错误信息
                console.log('错误信息:', errorMessage);
                return res.status(400).json({ error: errorMessage });
            }

            // 否则直接返回响应
            res.json(data);
        } catch (fetchError) {
            clearTimeout(timeout);
            if (fetchError.name === 'AbortError') {
                console.error('请求超时');
                return res.status(504).json({ error: '修改密码请求超时，请稍后重试' });
            }
            throw fetchError;
        }
    } catch (error) {
        console.error('修改密码错误:', error);
        res.status(500).json({ error: '修改密码失败，服务器错误' });
    }
});

export { router }; 
