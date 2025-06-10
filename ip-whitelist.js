// src/middleware/ip-whitelist.js
import { internalApiWhitelist } from '../config.default.js';

/**
 * 检查IP是否在白名单中的中间件
 * @param {import('express').Request} req 
 * @param {import('express').Response} res 
 * @param {import('express').NextFunction} next 
 */
export function ipWhitelistMiddleware(req, res, next) {
    const clientIp = req.ip || req.connection.remoteAddress;
    
    // 检查IP是否在白名单中
    const isWhitelisted = internalApiWhitelist.some(whitelistedIp => {
        if (whitelistedIp.includes('/')) {
            // 简单的CIDR检查 (仅支持 /24 格式)
            const [network] = whitelistedIp.split('/');
            const networkPrefix = network.split('.').slice(0, 3).join('.');
            const clientPrefix = clientIp.split('.').slice(0, 3).join('.');
            return networkPrefix === clientPrefix;
        }
        // 精确IP匹配
        return clientIp === whitelistedIp;
    });

    if (!isWhitelisted) {
        console.warn(`未经授权的访问 IP: ${clientIp}`);
        return res.status(403).json({
            error: 'Access denied: Your IP is not whitelisted'
        });
    }

    next();
} 
