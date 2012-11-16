SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

CREATE TABLE IF NOT EXISTS `upload` ( `upload_basename` varchar(155) NOT NULL, `upload_modified` bigint(20) NOT NULL, PRIMARY KEY (`upload_basename`)) ENGINE=InnoDB DEFAULT CHARSET=latin1;


CREATE TABLE IF NOT EXISTS `link` ( `link_id` int(11) NOT NULL AUTO_INCREMENT, `link_parent_id` int(11) DEFAULT NULL,  `link_name` varchar(255) NOT NULL, `link_title` varchar(125) NOT NULL, `lang_key` varchar(3) NOT NULL, `link_path` varchar(125) NOT NULL, `link_target` varchar(25) NOT NULL DEFAULT '_self',  PRIMARY KEY (`link_id`),  KEY `page_key` (`link_path`),  KEY `lang_key` (`lang_key`),  KEY `link_parent_id` (`link_parent_id`)) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;


CREATE TABLE IF NOT EXISTS `page` ( `page_key` varchar(125) NOT NULL, `page_title` varchar(125) NOT NULL,  `lang_key` varchar(3) NOT NULL,  `page_modified` bigint(20) NOT NULL,  `page_text` text NOT NULL,  `page_redirect` varchar(255) DEFAULT NULL,  PRIMARY KEY (`page_key`,`lang_key`),  KEY `lang_key` (`lang_key`),  FULLTEXT KEY `page_text` (`page_text`)) ENGINE=MyISAM DEFAULT CHARSET=latin1;

