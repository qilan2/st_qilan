// src/endpoints/users-internal.js
import storage from 'node-persist';
import express from 'express';
import lodash from 'lodash';
import fetch from 'node-fetch';
import fs from 'node:fs';
import path from 'node:path';
import { jsonParser } from '../express-common.js';
import { KEY_PREFIX, toKey, getPasswordSalt, getPasswordHash, getUserDirectories, ensurePublicDirectoriesExist } from '../users.js';
import { checkForNewContent } from './content-manager.js';
import { ipWhitelistMiddleware } from '../middleware/ip-whitelist.js';

export const router = express.Router();

// 应用IP白名单中间件到所有路由
router.use(ipWhitelistMiddleware);

// // 下载QQ头像
// async function downloadQQAvatar(qqNumber, avatarPath) {
//     try {
//         const response = await fetch(`https://q.qlogo.cn/headimg_dl?dst_uin=${qqNumber}&spec=640&img_type=jpg`);
//         if (!response.ok) {
//             throw new Error(`Failed to fetch avatar: ${response.statusText}`);
//         }
//         const buffer = await response.buffer();
//         fs.writeFileSync(avatarPath, buffer);
//         return true;
//     } catch (error) {
//         console.error('Failed to download QQ avatar:', error);
//         return false;
//     }
// }

// 创建用户
router.post('/create', jsonParser, async (request, response) => {
    try {
        if (!request.body.handle || !request.body.name) {
            console.warn('Create user failed: Missing required fields');
            return response.status(400).json({ error: 'Missing required fields' });
        }

        const handles = await storage.values(x => x.key.startsWith(KEY_PREFIX));
        const existingHandles = handles.map(x => x.handle);
        const handle = lodash.kebabCase(String(request.body.handle).toLowerCase().trim());

        if (!handle) {
            console.warn('Create user failed: Invalid handle');
            return response.status(400).json({ error: 'Invalid handle' });
        }

        if (existingHandles.some(x => x === handle)) {
            console.warn('Create user failed: User with that handle already exists');
            return response.status(409).json({ error: 'User already exists' });
        }

        const salt = getPasswordSalt();
        const password = request.body.password ? getPasswordHash(request.body.password, salt) : '';

        const newUser = {
            handle: handle,
            name: request.body.name || 'Anonymous',
            created: Date.now(),
            password: password,
            salt: salt,
            admin: !!request.body.admin,
            enabled: true,
        };

        await storage.setItem(toKey(handle), newUser);

        // 创建用户目录
        await ensurePublicDirectoriesExist();
        const directories = getUserDirectories(handle);
        await checkForNewContent([directories]);
        
        // // 如果handle是QQ号，下载并设置QQ头像
        // if (/^\d+$/.test(handle)) {
        //     const avatarsDir = path.join(directories.avatars);
        //     if (!fs.existsSync(avatarsDir)) {
        //         fs.mkdirSync(avatarsDir, { recursive: true });
        //     }
        //     const avatarPath = path.join(avatarsDir, 'avatar.jpg');
        //     await downloadQQAvatar(handle, avatarPath);
        // }

        return response.json({ handle: newUser.handle });
    } catch (error) {
        console.error('User create failed:', error);
        return response.sendStatus(500);
    }
});

// 删除用户
router.post('/delete', jsonParser, async (request, response) => {
    try {
        if (!request.body.handle) {
            console.warn('Delete user failed: Missing required fields');
            return response.status(400).json({ error: 'Missing required fields' });
        }

        const user = await storage.getItem(toKey(request.body.handle));

        if (!user) {
            console.error('Delete user failed: User not found');
            return response.status(404).json({ error: 'User not found' });
        }

        // 删除用户数据
        await storage.removeItem(toKey(request.body.handle));

        // 如果指定了删除文件
        if (request.body.delete_files) {
            const directories = getUserDirectories(request.body.handle);
            // 删除用户目录
            for (const dir of Object.values(directories)) {
                if (fs.existsSync(dir)) {
                    fs.rmSync(dir, { recursive: true, force: true });
                }
            }
        }

        return response.sendStatus(204);
    } catch (error) {
        console.error('User delete failed:', error);
        return response.sendStatus(500);
    }
});

// 启用/禁用用户
router.post('/toggle-status', jsonParser, async (request, response) => {
    try {
        if (!request.body.handle) {
            console.warn('Toggle user status failed: Missing required fields');
            return response.status(400).json({ error: 'Missing required fields' });
        }

        const user = await storage.getItem(toKey(request.body.handle));

        if (!user) {
            console.error('Toggle user status failed: User not found');
            return response.status(404).json({ error: 'User not found' });
        }

        user.enabled = !user.enabled;
        await storage.setItem(toKey(request.body.handle), user);
        return response.json({ handle: user.handle, enabled: user.enabled });
    } catch (error) {
        console.error('Toggle user status failed:', error);
        return response.sendStatus(500);
    }
});

// 获取所有用户列表
router.get('/list', async (_request, response) => {
    try {
        const users = await storage.values(x => x.key.startsWith(KEY_PREFIX));
        const viewModels = users.map(user => ({
            handle: user.handle,
            name: user.name,
            admin: user.admin,
            enabled: user.enabled,
            created: user.created,
            password: !!user.password,
        }));
        
        viewModels.sort((x, y) => (x.created ?? 0) - (y.created ?? 0));
        return response.json(viewModels);
    } catch (error) {
        console.error('User list failed:', error);
        return response.sendStatus(500);
    }
});

// 获取指定用户信息
router.get('/info/:handle', async (request, response) => {
    try {
        const handle = request.params.handle;
        if (!handle) {
            console.warn('Get user info failed: Missing handle');
            return response.status(400).json({ error: 'Missing handle' });
        }

        const user = await storage.getItem(toKey(handle));
        if (!user) {
            console.error('Get user info failed: User not found');
            return response.status(404).json({ error: 'User not found' });
        }

        // 返回用户信息，但不包含敏感数据
        const userInfo = {
            handle: user.handle,
            name: user.name,
            admin: user.admin,
            enabled: user.enabled,
            created: user.created,
            hasPassword: !!user.password,
        };

        return response.json(userInfo);
    } catch (error) {
        console.error('Get user info failed:', error);
        return response.sendStatus(500);
    }
});

// 修改用户密码
router.post('/change-password', jsonParser, async (request, response) => {
    try {
        if (!request.body.handle || !request.body.newPassword) {
            console.warn('Change password failed: Missing required fields');
            return response.status(400).json({ error: 'Missing required fields' });
        }

        const user = await storage.getItem(toKey(request.body.handle));
        if (!user) {
            console.error('Change password failed: User not found');
            return response.status(404).json({ error: 'User not found' });
        }

        // 直接设置新密码
        const newSalt = getPasswordSalt();
        const newPasswordHash = getPasswordHash(request.body.newPassword, newSalt);

        // 更新用户信息
        const updatedUser = {
            ...user,
            password: newPasswordHash,
            salt: newSalt
        };

        await storage.setItem(toKey(user.handle), updatedUser);
        return response.sendStatus(200);
    } catch (error) {
        console.error('Change password failed:', error);
        return response.sendStatus(500);
    }
}); 
