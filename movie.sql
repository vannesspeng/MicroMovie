/*
Navicat MySQL Data Transfer

Source Server         : MYSQL
Source Server Version : 50717
Source Host           : localhost:3306
Source Database       : movie

Target Server Type    : MYSQL
Target Server Version : 50717
File Encoding         : 65001

Date: 2018-10-08 11:09:33
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for `admin`
-- ----------------------------
DROP TABLE IF EXISTS `admin`;
CREATE TABLE `admin` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `pwd` varchar(100) DEFAULT NULL,
  `is_super` smallint(6) DEFAULT NULL,
  `role_id` int(11) DEFAULT NULL,
  `addtime` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `role_id` (`role_id`),
  KEY `ix_admin_addtime` (`addtime`),
  CONSTRAINT `admin_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `role` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of admin
-- ----------------------------
INSERT INTO `admin` VALUES ('1', 'admin', 'pbkdf2:sha256:50000$kwfTEBEn$008c6860174bb6db87a706e0aa76cd3b70c0c54e76f181b7271714fbfbf382f6', '1', '3', '2018-08-28 17:02:42');
INSERT INTO `admin` VALUES ('3', 'preview_admin', 'pbkdf2:sha256:50000$QE2Zy3sf$5c13be555a01c22463d8028c264e04a3f494ef2828e27c49f7f402b3305b3df7', '1', '1', '2018-09-14 11:33:08');

-- ----------------------------
-- Table structure for `adminlog`
-- ----------------------------
DROP TABLE IF EXISTS `adminlog`;
CREATE TABLE `adminlog` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `admin_id` int(11) DEFAULT NULL,
  `ip` varchar(100) DEFAULT NULL,
  `addtime` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `admin_id` (`admin_id`),
  KEY `ix_adminlog_addtime` (`addtime`),
  CONSTRAINT `adminlog_ibfk_1` FOREIGN KEY (`admin_id`) REFERENCES `admin` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of adminlog
-- ----------------------------
INSERT INTO `adminlog` VALUES ('1', '1', '127.0.0.1', '2018-09-12 16:39:15');
INSERT INTO `adminlog` VALUES ('2', '1', '127.0.0.1', '2018-09-13 09:54:06');
INSERT INTO `adminlog` VALUES ('3', '1', '127.0.0.1', '2018-09-14 09:42:58');
INSERT INTO `adminlog` VALUES ('4', '1', '127.0.0.1', '2018-09-17 15:11:02');
INSERT INTO `adminlog` VALUES ('5', '1', '127.0.0.1', '2018-09-18 11:07:38');
INSERT INTO `adminlog` VALUES ('6', '1', '127.0.0.1', '2018-09-18 11:27:40');
INSERT INTO `adminlog` VALUES ('7', '1', '127.0.0.1', '2018-09-19 09:34:19');
INSERT INTO `adminlog` VALUES ('8', '1', '127.0.0.1', '2018-09-19 14:22:36');

-- ----------------------------
-- Table structure for `auth`
-- ----------------------------
DROP TABLE IF EXISTS `auth`;
CREATE TABLE `auth` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `url` varchar(255) DEFAULT NULL,
  `addtime` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  UNIQUE KEY `url` (`url`),
  KEY `ix_auth_addtime` (`addtime`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of auth
-- ----------------------------
INSERT INTO `auth` VALUES ('9', '添加标签', '/admin/tag/add', '2018-09-13 11:48:36');
INSERT INTO `auth` VALUES ('13', '删除标签', '/admin/tag/del/<int:id>', '2018-09-13 14:57:40');
INSERT INTO `auth` VALUES ('14', '添加预告', '/admin/preview/add', '2018-09-13 14:57:51');

-- ----------------------------
-- Table structure for `comment`
-- ----------------------------
DROP TABLE IF EXISTS `comment`;
CREATE TABLE `comment` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `content` text,
  `movie_id` int(11) DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  `addtime` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `movie_id` (`movie_id`),
  KEY `user_id` (`user_id`),
  KEY `ix_comment_addtime` (`addtime`),
  CONSTRAINT `comment_ibfk_1` FOREIGN KEY (`movie_id`) REFERENCES `movie` (`id`),
  CONSTRAINT `comment_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of comment
-- ----------------------------
INSERT INTO `comment` VALUES ('3', '经典', '7', '3', '2018-09-12 09:24:46');
INSERT INTO `comment` VALUES ('4', '给力', '7', '4', '2018-09-12 09:24:46');
INSERT INTO `comment` VALUES ('5', '难看', '8', '5', '2018-09-12 09:24:46');
INSERT INTO `comment` VALUES ('6', '无聊', '8', '6', '2018-09-12 09:24:46');
INSERT INTO `comment` VALUES ('7', '乏味', '8', '7', '2018-09-12 09:24:46');
INSERT INTO `comment` VALUES ('8', '无感', '8', '8', '2018-09-12 09:24:46');
INSERT INTO `comment` VALUES ('9', '<p>圣达菲</p>', '7', '9', '2018-09-20 08:20:24');
INSERT INTO `comment` VALUES ('10', '<p>圣达菲</p>', '7', '9', '2018-09-20 08:22:21');
INSERT INTO `comment` VALUES ('11', '<p>电影不错的哦</p>', '7', '9', '2018-09-20 08:52:12');
INSERT INTO `comment` VALUES ('12', '<p>twins的表演真的很赞！</p>', '8', '9', '2018-09-21 07:09:17');

-- ----------------------------
-- Table structure for `movie`
-- ----------------------------
DROP TABLE IF EXISTS `movie`;
CREATE TABLE `movie` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(255) DEFAULT NULL,
  `url` varchar(255) DEFAULT NULL,
  `info` text,
  `logo` varchar(255) DEFAULT NULL,
  `star` smallint(6) DEFAULT NULL,
  `playnum` bigint(20) DEFAULT NULL,
  `commentnum` bigint(20) DEFAULT NULL,
  `tag_id` int(11) DEFAULT NULL,
  `area` varchar(255) DEFAULT NULL,
  `release_time` date DEFAULT NULL,
  `length` varchar(100) DEFAULT NULL,
  `addtime` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `title` (`title`),
  UNIQUE KEY `url` (`url`),
  UNIQUE KEY `logo` (`logo`),
  KEY `tag_id` (`tag_id`),
  KEY `ix_movie_addtime` (`addtime`),
  CONSTRAINT `movie_ibfk_1` FOREIGN KEY (`tag_id`) REFERENCES `tag` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of movie
-- ----------------------------
INSERT INTO `movie` VALUES ('7', '产测视频1', '20180910092341f4d5e197e2154a5fbeb783a7c70abbef.mp4', '休为btn-col 设置点击事件，获取当前的movieid，获取当前的用户。\r\n使用ajax，提交的地址。type:get,提交的数据，返回的数据类型json。\r\n成功之后的处理函数res接收返回的json对象', '201809100923411b5c6e0b2beb44bca14ac83bf1e0564d.png', '1', '59', '2', '2', '武汉', '2018-09-18', '2:00', '2018-09-07 09:03:07');
INSERT INTO `movie` VALUES ('8', '下一站天后', '20180912092403ec33084fc291443892ade42f9a000e69.mp4', 'Twins 演唱', '201809120924034bde0f0283934a648e70b0f20d4f59a6.png', '3', '10', '1', '2', '武汉', '2018-09-21', '2:00', '2018-09-12 01:24:03');

-- ----------------------------
-- Table structure for `moviecol`
-- ----------------------------
DROP TABLE IF EXISTS `moviecol`;
CREATE TABLE `moviecol` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `movie_id` int(11) DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  `addtime` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `movie_id` (`movie_id`),
  KEY `user_id` (`user_id`),
  KEY `ix_moviecol_addtime` (`addtime`),
  CONSTRAINT `moviecol_ibfk_1` FOREIGN KEY (`movie_id`) REFERENCES `movie` (`id`),
  CONSTRAINT `moviecol_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of moviecol
-- ----------------------------
INSERT INTO `moviecol` VALUES ('10', '7', '2', '2018-09-12 11:32:52');
INSERT INTO `moviecol` VALUES ('11', '7', '3', '2018-09-12 11:32:55');
INSERT INTO `moviecol` VALUES ('14', '8', '6', '2018-09-12 11:32:57');
INSERT INTO `moviecol` VALUES ('16', '7', '9', '2018-09-21 03:42:38');
INSERT INTO `moviecol` VALUES ('17', '8', '9', '2018-09-21 07:08:22');

-- ----------------------------
-- Table structure for `oplog`
-- ----------------------------
DROP TABLE IF EXISTS `oplog`;
CREATE TABLE `oplog` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `admin_id` int(11) DEFAULT NULL,
  `ip` varchar(100) DEFAULT NULL,
  `reason` varchar(600) DEFAULT NULL,
  `addtime` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `admin_id` (`admin_id`),
  KEY `ix_oplog_addtime` (`addtime`),
  CONSTRAINT `oplog_ibfk_1` FOREIGN KEY (`admin_id`) REFERENCES `admin` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of oplog
-- ----------------------------
INSERT INTO `oplog` VALUES ('1', '1', '127.0.0.1', '添加标签文艺片', '2018-09-12 16:21:14');

-- ----------------------------
-- Table structure for `preview`
-- ----------------------------
DROP TABLE IF EXISTS `preview`;
CREATE TABLE `preview` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(255) DEFAULT NULL,
  `logo` varchar(255) DEFAULT NULL,
  `addtime` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `title` (`title`),
  UNIQUE KEY `logo` (`logo`),
  KEY `ix_preview_addtime` (`addtime`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of preview
-- ----------------------------
INSERT INTO `preview` VALUES ('8', '乐见大牌', '2018091909374246b15b23bfe74da78cbd523b97ccc841.jpg', '2018-09-19 01:37:42');
INSERT INTO `preview` VALUES ('9', '周杰伦新年大礼', '201809191424209b5d59f3d9b84a9fbc45881b1c454c0c.jpg', '2018-09-19 06:24:20');
INSERT INTO `preview` VALUES ('10', '乐侃第二期', '20180919142834ec52d378b2824ad492d8cc86c5859282.jpg', '2018-09-19 06:28:34');
INSERT INTO `preview` VALUES ('11', '王力宏', '201809191606143122fc032e594c219f27ab6d3003fd87.jpg', '2018-09-19 08:06:15');
INSERT INTO `preview` VALUES ('12', '范冰冰', '201809191607388f6440b4b423436c91ffc73ffe2142d5.jpg', '2018-09-19 08:07:38');
INSERT INTO `preview` VALUES ('13', 'python', '20180919161039356ab955e5ce4560a1d11804e765549d.png', '2018-09-19 08:10:40');

-- ----------------------------
-- Table structure for `role`
-- ----------------------------
DROP TABLE IF EXISTS `role`;
CREATE TABLE `role` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `auths` varchar(600) DEFAULT NULL,
  `addtime` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `ix_role_addtime` (`addtime`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of role
-- ----------------------------
INSERT INTO `role` VALUES ('1', '预告管理员', '14', '2018-09-13 17:02:43');
INSERT INTO `role` VALUES ('3', '管理员', '9,13,14', '2018-09-13 17:07:22');

-- ----------------------------
-- Table structure for `tag`
-- ----------------------------
DROP TABLE IF EXISTS `tag`;
CREATE TABLE `tag` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `addtime` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `ix_tag_addtime` (`addtime`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of tag
-- ----------------------------
INSERT INTO `tag` VALUES ('2', '动作片', '2018-08-29 08:33:30');
INSERT INTO `tag` VALUES ('4', '灾难片', '2018-08-29 08:50:16');
INSERT INTO `tag` VALUES ('5', '喜剧片', '2018-08-29 08:51:19');
INSERT INTO `tag` VALUES ('7', '剧情片', '2018-08-29 08:53:57');
INSERT INTO `tag` VALUES ('8', '犯罪片', '2018-08-29 08:54:09');
INSERT INTO `tag` VALUES ('9', '爱情片', '2018-08-29 08:54:14');
INSERT INTO `tag` VALUES ('13', '美国大片', '2018-08-30 06:17:13');
INSERT INTO `tag` VALUES ('14', '纪录片', '2018-08-30 06:20:34');
INSERT INTO `tag` VALUES ('16', '文艺片', '2018-09-12 08:21:14');

-- ----------------------------
-- Table structure for `user`
-- ----------------------------
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `pwd` varchar(100) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `phone` varchar(11) DEFAULT NULL,
  `info` text,
  `face` varchar(255) DEFAULT NULL,
  `addtime` datetime DEFAULT NULL,
  `uuid` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `phone` (`phone`),
  UNIQUE KEY `face` (`face`),
  UNIQUE KEY `uuid` (`uuid`),
  KEY `ix_user_addtime` (`addtime`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of user
-- ----------------------------
INSERT INTO `user` VALUES ('1', '兔', '1234', '1234@123.com', '13888888884', '兔', '1f407.png', '2018-09-11 10:23:06', 'd32a72bdac524478b7e4f6dfc8394fc3');
INSERT INTO `user` VALUES ('2', '龙', '1235', '1235@123.com', '13888888885', '龙', '1f409.png', '2018-09-11 10:23:06', 'd32a72bdac524478b7e4f6dfc8394fc4');
INSERT INTO `user` VALUES ('3', '蛇', '1236', '1236@123.com', '13888888886', '蛇', '1f40d.png', '2018-09-11 10:23:06', 'd32a72bdac524478b7e4f6dfc8394fc5');
INSERT INTO `user` VALUES ('4', '马', '1237', '1237@123.com', '13888888887', '马', '1f434.png', '2018-09-11 10:23:06', 'd32a72bdac524478b7e4f6dfc8394fc6');
INSERT INTO `user` VALUES ('5', '羊', '1238', '1238@123.com', '13888888888', '羊', '1f411.png', '2018-09-11 10:23:06', 'd32a72bdac524478b7e4f6dfc8394fc7');
INSERT INTO `user` VALUES ('6', '猴', '1239', '1239@123.com', '13888888889', '猴', '1f412.png', '2018-09-11 10:23:06', 'd32a72bdac524478b7e4f6dfc8394fc8');
INSERT INTO `user` VALUES ('7', '鸡', '1240', '1240@123.com', '13888888891', '鸡', '1f413.png', '2018-09-11 10:23:06', 'd32a72bdac524478b7e4f6dfc8394fc9');
INSERT INTO `user` VALUES ('8', '狗', '1241', '1241@123.com', '13888888892', '狗', '1f415.png', '2018-09-11 10:23:06', 'd32a72bdac524478b7e4f6dfc8394fd0');
INSERT INTO `user` VALUES ('9', 'vanness', 'pbkdf2:sha256:50000$Qq9DQwS4$74d5f7bea20455e0be111d42d200f6e2fac862082c3867e58d3f27db2b9cad6a', '2222222@qq.com', '13720297499', '90年出生，属相马o  sdsdsdfsdf', '201809181448297d944863a30b417cbd3426029b8e6dd9.png', '2018-09-17 07:24:34', 'f6857796cd174531bcddbdd5ff754b71');
INSERT INTO `user` VALUES ('10', 'jack', 'pbkdf2:sha256:50000$jf7gWOTS$6a13b92e7db6461deb37b951df61329db8b7a2f0ae7230c1157bf8e204a0584e', '5446466413@qq.com', '13852266225', null, null, '2018-09-17 07:30:54', 'a552bb7682594cdeab7e9aabaa83cc4f');

-- ----------------------------
-- Table structure for `userlog`
-- ----------------------------
DROP TABLE IF EXISTS `userlog`;
CREATE TABLE `userlog` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) DEFAULT NULL,
  `ip` varchar(100) DEFAULT NULL,
  `addtime` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `ix_userlog_addtime` (`addtime`),
  CONSTRAINT `userlog_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=41 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of userlog
-- ----------------------------
INSERT INTO `userlog` VALUES ('1', '1', '192.168.4.1', '2018-09-12 16:41:31');
INSERT INTO `userlog` VALUES ('2', '2', '192.168.4.2', '2018-09-12 16:41:32');
INSERT INTO `userlog` VALUES ('3', '3', '192.168.4.3', '2018-09-12 16:41:33');
INSERT INTO `userlog` VALUES ('4', '4', '192.168.4.4', '2018-09-12 16:41:34');
INSERT INTO `userlog` VALUES ('5', '5', '192.168.4.5', '2018-09-12 16:41:35');
INSERT INTO `userlog` VALUES ('6', '6', '192.168.4.6', '2018-09-12 16:41:36');
INSERT INTO `userlog` VALUES ('7', '7', '192.168.4.7', '2018-09-12 16:41:37');
INSERT INTO `userlog` VALUES ('8', '8', '192.168.4.8', '2018-09-12 16:41:38');
INSERT INTO `userlog` VALUES ('9', '9', '127.0.0.1', '2018-09-17 08:06:46');
INSERT INTO `userlog` VALUES ('10', '9', '127.0.0.1', '2018-09-17 08:07:31');
INSERT INTO `userlog` VALUES ('11', '9', '127.0.0.1', '2018-09-17 08:38:18');
INSERT INTO `userlog` VALUES ('12', '9', '127.0.0.1', '2018-09-17 08:50:31');
INSERT INTO `userlog` VALUES ('13', '9', '127.0.0.1', '2018-09-17 09:00:27');
INSERT INTO `userlog` VALUES ('14', '9', '127.0.0.1', '2018-09-17 09:00:53');
INSERT INTO `userlog` VALUES ('15', '9', '127.0.0.1', '2018-09-18 03:07:57');
INSERT INTO `userlog` VALUES ('16', '9', '127.0.0.1', '2018-09-18 03:10:05');
INSERT INTO `userlog` VALUES ('17', '9', '127.0.0.1', '2018-09-18 03:10:26');
INSERT INTO `userlog` VALUES ('18', '9', '127.0.0.1', '2018-09-18 03:10:50');
INSERT INTO `userlog` VALUES ('19', '9', '127.0.0.1', '2018-09-18 03:11:21');
INSERT INTO `userlog` VALUES ('20', '9', '127.0.0.1', '2018-09-18 03:20:30');
INSERT INTO `userlog` VALUES ('21', '9', '127.0.0.1', '2018-09-18 03:20:35');
INSERT INTO `userlog` VALUES ('22', '9', '127.0.0.1', '2018-09-18 03:22:59');
INSERT INTO `userlog` VALUES ('23', '9', '127.0.0.1', '2018-09-18 06:29:06');
INSERT INTO `userlog` VALUES ('24', '9', '127.0.0.1', '2018-09-18 07:16:17');
INSERT INTO `userlog` VALUES ('25', '9', '127.0.0.1', '2018-09-18 07:21:24');
INSERT INTO `userlog` VALUES ('26', '9', '127.0.0.1', '2018-09-18 07:25:11');
INSERT INTO `userlog` VALUES ('27', '9', '127.0.0.1', '2018-09-18 07:25:40');
INSERT INTO `userlog` VALUES ('28', '9', '127.0.0.1', '2018-09-18 07:26:46');
INSERT INTO `userlog` VALUES ('29', '9', '127.0.0.1', '2018-09-19 01:33:28');
INSERT INTO `userlog` VALUES ('30', '9', '127.0.0.1', '2018-09-19 01:33:56');
INSERT INTO `userlog` VALUES ('31', '9', '127.0.0.1', '2018-09-20 08:01:56');
INSERT INTO `userlog` VALUES ('32', '9', '127.0.0.1', '2018-09-20 08:51:22');
INSERT INTO `userlog` VALUES ('33', '9', '127.0.0.1', '2018-09-21 01:18:02');
INSERT INTO `userlog` VALUES ('34', '9', '127.0.0.1', '2018-09-21 01:21:06');
INSERT INTO `userlog` VALUES ('35', '9', '127.0.0.1', '2018-09-21 01:22:00');
INSERT INTO `userlog` VALUES ('36', '9', '127.0.0.1', '2018-09-21 01:22:15');
INSERT INTO `userlog` VALUES ('37', '9', '127.0.0.1', '2018-09-21 01:23:30');
INSERT INTO `userlog` VALUES ('38', '9', '127.0.0.1', '2018-09-21 01:34:19');
INSERT INTO `userlog` VALUES ('39', '9', '127.0.0.1', '2018-09-21 01:35:02');
INSERT INTO `userlog` VALUES ('40', '9', '127.0.0.1', '2018-09-21 03:14:12');
