/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19-11.8.3-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: db    Database: mclass_manager_db
-- ------------------------------------------------------
-- Server version	8.0.44

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*M!100616 SET @OLD_NOTE_VERBOSITY=@@NOTE_VERBOSITY, NOTE_VERBOSITY=0 */;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
set autocommit=0;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
set autocommit=0;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=153 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `auth_permission` VALUES
(1,'Can add log entry',1,'add_logentry'),
(2,'Can change log entry',1,'change_logentry'),
(3,'Can delete log entry',1,'delete_logentry'),
(4,'Can view log entry',1,'view_logentry'),
(5,'Can add permission',2,'add_permission'),
(6,'Can change permission',2,'change_permission'),
(7,'Can delete permission',2,'delete_permission'),
(8,'Can view permission',2,'view_permission'),
(9,'Can add group',3,'add_group'),
(10,'Can change group',3,'change_group'),
(11,'Can delete group',3,'delete_group'),
(12,'Can view group',3,'view_group'),
(13,'Can add user',4,'add_user'),
(14,'Can change user',4,'change_user'),
(15,'Can delete user',4,'delete_user'),
(16,'Can view user',4,'view_user'),
(17,'Can add content type',5,'add_contenttype'),
(18,'Can change content type',5,'change_contenttype'),
(19,'Can delete content type',5,'delete_contenttype'),
(20,'Can view content type',5,'view_contenttype'),
(21,'Can add session',6,'add_session'),
(22,'Can change session',6,'change_session'),
(23,'Can delete session',6,'delete_session'),
(24,'Can view session',6,'view_session'),
(25,'Can add 교재',7,'add_book'),
(26,'Can change 교재',7,'change_book'),
(27,'Can delete 교재',7,'delete_book'),
(28,'Can view 교재',7,'view_book'),
(29,'Can add 은행',8,'add_bank'),
(30,'Can change 은행',8,'change_bank'),
(31,'Can delete 은행',8,'delete_bank'),
(32,'Can view 은행',8,'view_bank'),
(33,'Can add 출판사',9,'add_publisher'),
(34,'Can change 출판사',9,'change_publisher'),
(35,'Can delete 출판사',9,'delete_publisher'),
(36,'Can view 출판사',9,'view_publisher'),
(37,'Can add 교재 구입처',10,'add_purchaselocation'),
(38,'Can change 교재 구입처',10,'change_purchaselocation'),
(39,'Can delete 교재 구입처',10,'delete_purchaselocation'),
(40,'Can view 교재 구입처',10,'view_purchaselocation'),
(41,'Can add 학교',11,'add_school'),
(42,'Can change 학교',11,'change_school'),
(43,'Can delete 학교',11,'delete_school'),
(44,'Can view 학교',11,'view_school'),
(45,'Can add 과목',12,'add_subject'),
(46,'Can change 과목',12,'change_subject'),
(47,'Can delete 과목',12,'delete_subject'),
(48,'Can view 과목',12,'view_subject'),
(49,'Can add 교사',13,'add_teacher'),
(50,'Can change 교사',13,'change_teacher'),
(51,'Can delete 교사',13,'delete_teacher'),
(52,'Can view 교사',13,'view_teacher'),
(53,'Can add 출근기록',14,'add_attendance'),
(54,'Can change 출근기록',14,'change_attendance'),
(55,'Can delete 출근기록',14,'delete_attendance'),
(56,'Can view 출근기록',14,'view_attendance'),
(57,'Can add 급여',15,'add_salary'),
(58,'Can change 급여',15,'change_salary'),
(59,'Can delete 급여',15,'delete_salary'),
(60,'Can view 급여',15,'view_salary'),
(61,'Can add 학생',16,'add_student'),
(62,'Can change 학생',16,'change_student'),
(63,'Can delete 학생',16,'delete_student'),
(64,'Can view 학생',16,'view_student'),
(65,'Can add 학생 파일',17,'add_studentfile'),
(66,'Can change 학생 파일',17,'change_studentfile'),
(67,'Can delete 학생 파일',17,'delete_studentfile'),
(68,'Can view 학생 파일',17,'view_studentfile'),
(69,'Can add 관리비',18,'add_maintenance'),
(70,'Can change 관리비',18,'change_maintenance'),
(71,'Can delete 관리비',18,'delete_maintenance'),
(72,'Can view 관리비',18,'view_maintenance'),
(73,'Can add 호실 정보',19,'add_room'),
(74,'Can change 호실 정보',19,'change_room'),
(75,'Can delete 호실 정보',19,'delete_room'),
(76,'Can view 호실 정보',19,'view_room'),
(77,'Can add 도서 판매',20,'add_bookdistribution'),
(78,'Can change 도서 판매',20,'change_bookdistribution'),
(79,'Can delete 도서 판매',20,'delete_bookdistribution'),
(80,'Can view 도서 판매',20,'view_bookdistribution'),
(81,'Can add 도서 출고',21,'add_bookissue'),
(82,'Can change 도서 출고',21,'change_bookissue'),
(83,'Can delete 도서 출고',21,'delete_bookissue'),
(84,'Can view 도서 출고',21,'view_bookissue'),
(85,'Can add 도서 반품',22,'add_bookreturn'),
(86,'Can change 도서 반품',22,'change_bookreturn'),
(87,'Can delete 도서 반품',22,'delete_bookreturn'),
(88,'Can view 도서 반품',22,'view_bookreturn'),
(89,'Can add 도서 재고',23,'add_bookstock'),
(90,'Can change 도서 재고',23,'change_bookstock'),
(91,'Can delete 도서 재고',23,'delete_bookstock'),
(92,'Can view 도서 재고',23,'view_bookstock'),
(93,'Can add 결제',24,'add_payment'),
(94,'Can change 결제',24,'change_payment'),
(95,'Can delete 결제',24,'delete_payment'),
(96,'Can view 결제',24,'view_payment'),
(97,'Can add 교재 결제',25,'add_bookpayment'),
(98,'Can change 교재 결제',25,'change_bookpayment'),
(99,'Can delete 교재 결제',25,'delete_bookpayment'),
(100,'Can view 교재 결제',25,'view_bookpayment'),
(101,'Can add 결제 이력',26,'add_paymenthistory'),
(102,'Can change 결제 이력',26,'change_paymenthistory'),
(103,'Can delete 결제 이력',26,'delete_paymenthistory'),
(104,'Can view 결제 이력',26,'view_paymenthistory'),
(105,'Can add 교재',27,'add_book'),
(106,'Can change 교재',27,'change_book'),
(107,'Can delete 교재',27,'delete_book'),
(108,'Can view 교재',27,'view_book'),
(109,'Can add 구매처',28,'add_booksupplier'),
(110,'Can change 구매처',28,'change_booksupplier'),
(111,'Can delete 구매처',28,'delete_booksupplier'),
(112,'Can view 구매처',28,'view_booksupplier'),
(113,'Can add 교재 판매 내역',29,'add_booksale'),
(114,'Can change 교재 판매 내역',29,'change_booksale'),
(115,'Can delete 교재 판매 내역',29,'delete_booksale'),
(116,'Can view 교재 판매 내역',29,'view_booksale'),
(117,'Can add 재고 기록',30,'add_bookstocklog'),
(118,'Can change 재고 기록',30,'change_bookstocklog'),
(119,'Can delete 재고 기록',30,'delete_bookstocklog'),
(120,'Can view 재고 기록',30,'view_bookstocklog'),
(121,'Can add 과목',31,'add_subject'),
(122,'Can change 과목',31,'change_subject'),
(123,'Can delete 과목',31,'delete_subject'),
(124,'Can view 과목',31,'view_subject'),
(125,'Can add 성적',32,'add_grade'),
(126,'Can change 성적',32,'change_grade'),
(127,'Can delete 성적',32,'delete_grade'),
(128,'Can view 성적',32,'view_grade'),
(129,'Can add 교재 문제',33,'add_bookproblem'),
(130,'Can change 교재 문제',33,'change_bookproblem'),
(131,'Can delete 교재 문제',33,'delete_bookproblem'),
(132,'Can view 교재 문제',33,'view_bookproblem'),
(133,'Can add 학생 진도표',34,'add_studentprogress'),
(134,'Can change 학생 진도표',34,'change_studentprogress'),
(135,'Can delete 학생 진도표',34,'delete_studentprogress'),
(136,'Can view 학생 진도표',34,'view_studentprogress'),
(137,'Can add 진도 항목',35,'add_progressentry'),
(138,'Can change 진도 항목',35,'change_progressentry'),
(139,'Can delete 진도 항목',35,'delete_progressentry'),
(140,'Can view 진도 항목',35,'view_progressentry'),
(141,'Can add 문제 유형',36,'add_problemtype'),
(142,'Can change 문제 유형',36,'change_problemtype'),
(143,'Can delete 문제 유형',36,'delete_problemtype'),
(144,'Can view 문제 유형',36,'view_problemtype'),
(145,'Can add 출근 불가 일정',37,'add_teacherunavailability'),
(146,'Can change 출근 불가 일정',37,'change_teacherunavailability'),
(147,'Can delete 출근 불가 일정',37,'delete_teacherunavailability'),
(148,'Can view 출근 불가 일정',37,'view_teacherunavailability'),
(149,'Can add 교사-학생 배정',38,'add_teacherstudentassignment'),
(150,'Can change 교사-학생 배정',38,'change_teacherstudentassignment'),
(151,'Can delete 교사-학생 배정',38,'delete_teacherstudentassignment'),
(152,'Can view 교사-학생 배정',38,'view_teacherstudentassignment');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user`
--

LOCK TABLES `auth_user` WRITE;
/*!40000 ALTER TABLE `auth_user` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `auth_user` VALUES
(1,'pbkdf2_sha256$1000000$0IiEFr9KIgbxjDwlzxzrTr$0cYbR9GZQiVo54uzk3Wsr6gNEj9hiIZ6hHoXOQFl8w8=','2026-01-12 23:35:57.282050',1,'admin','','','jjangdm@mclass.co.kr',1,1,'2024-10-13 00:29:21.374000');
/*!40000 ALTER TABLE `auth_user` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `auth_user_groups`
--

DROP TABLE IF EXISTS `auth_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user_groups` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`),
  CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_groups`
--

LOCK TABLES `auth_user_groups` WRITE;
/*!40000 ALTER TABLE `auth_user_groups` DISABLE KEYS */;
set autocommit=0;
/*!40000 ALTER TABLE `auth_user_groups` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `auth_user_user_permissions`
--

DROP TABLE IF EXISTS `auth_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user_user_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_user_permissions`
--

LOCK TABLES `auth_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `auth_user_user_permissions` DISABLE KEYS */;
set autocommit=0;
/*!40000 ALTER TABLE `auth_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `books_book`
--

DROP TABLE IF EXISTS `books_book`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `books_book` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL,
  `isbn` varchar(13) DEFAULT NULL,
  `difficulty_level` int unsigned DEFAULT NULL,
  `memo` longtext,
  `publisher_id` bigint DEFAULT NULL,
  `subject_id` bigint DEFAULT NULL,
  `spare1` varchar(200) DEFAULT NULL,
  `spare2` varchar(200) DEFAULT NULL,
  `spare3` varchar(200) DEFAULT NULL,
  `barcode` varchar(100) DEFAULT NULL,
  `qr_code` varchar(100) DEFAULT NULL,
  `unique_code` varchar(36) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_code` (`unique_code`),
  KEY `books_book_publisher_id_189e6c56_fk_common_publisher_id` (`publisher_id`),
  KEY `books_book_subject_id_407e81ef_fk_common_subject_id` (`subject_id`),
  CONSTRAINT `books_book_publisher_id_189e6c56_fk_common_publisher_id` FOREIGN KEY (`publisher_id`) REFERENCES `common_publisher` (`id`),
  CONSTRAINT `books_book_subject_id_407e81ef_fk_common_subject_id` FOREIGN KEY (`subject_id`) REFERENCES `common_subject` (`id`),
  CONSTRAINT `books_book_chk_4` CHECK ((`difficulty_level` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `books_book`
--

LOCK TABLES `books_book` WRITE;
/*!40000 ALTER TABLE `books_book` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `books_book` VALUES
(14,'15개정 최고득점수학 3-1','9791162279915',8,NULL,7,7,NULL,NULL,NULL,'books/barcodes/barcode_9791162279915.png','books/qrcodes/qr_1b02aa96-f16f-4749-957e-f451883d31c1.png','1b02aa96-f16f-4749-957e-f451883d31c1'),
(15,'이투스 신 수학의 바이블 중등 유형 2-2','9791164424535',6,NULL,6,6,NULL,NULL,NULL,'books/barcodes/barcode_9791164424535.png','books/qrcodes/qr_bbf844c9-4826-49bb-8c04-947de3b1db0b.png','bbf844c9-4826-49bb-8c04-947de3b1db0b'),
(16,'이투스 고쟁이 유형심화 중등 2-2 수학','9791165987718',8,NULL,6,6,NULL,NULL,NULL,'books/barcodes/barcode_9791165987718.png','books/qrcodes/qr_3c9abd92-9930-435b-a548-bfbbea81407f.png','3c9abd92-9930-435b-a548-bfbbea81407f'),
(17,'22개정 개념+유형 공통수학1','9791169404419',5,'',7,16,NULL,NULL,NULL,'books/barcodes/barcode_9791169404419.png','books/qrcodes/qr_3c90d12d-8bab-4453-8a37-48aa671dc4a1.png','3c90d12d-8bab-4453-8a37-48aa671dc4a1'),
(18,'25 오투 중등과학 1-1','9791169409308',6,'',7,18,NULL,NULL,NULL,'books/barcodes/barcode_9791169409308.png','books/qrcodes/qr_009f0769-5d8a-44cf-8498-547a696cd251.png','009f0769-5d8a-44cf-8498-547a696cd251'),
(19,'15개정 최고득점수학 2-2','9791162278215',8,'',7,6,NULL,NULL,NULL,'books/barcodes/barcode_9791162278215.png','books/qrcodes/qr_dc650733-5448-4006-abc2-db02fab78770.png','dc650733-5448-4006-abc2-db02fab78770'),
(20,'15개정 최고득점수학 2-1','9791162276686',8,'',7,6,NULL,NULL,NULL,'books/barcodes/barcode_9791162276686.png','books/qrcodes/qr_32c9d3f1-d986-47e9-8fa9-d4703e05460a.png','32c9d3f1-d986-47e9-8fa9-d4703e05460a'),
(21,'이투스 신 수학의 바이블 중등 개념 2-1','9791164429806',5,'',6,6,NULL,NULL,NULL,'books/barcodes/barcode_9791164429806.png','books/qrcodes/qr_50070524-5d78-4ddd-a46a-0ee8ee65e281.png','50070524-5d78-4ddd-a46a-0ee8ee65e281'),
(22,'이투스 신 수학의 바이블 중등 유형 2-1','9791164429820',6,'',6,6,NULL,NULL,NULL,'books/barcodes/barcode_9791164429820.png','books/qrcodes/qr_b35275eb-712d-4c10-bb4f-0da0f6530c47.png','b35275eb-712d-4c10-bb4f-0da0f6530c47'),
(23,'이투스 신 수학의 바이블 중등 개념 3-1','9791164422777',5,'',6,7,NULL,NULL,NULL,'books/barcodes/barcode_9791164422777.png','books/qrcodes/qr_df84977d-ff80-4214-bbf8-d6a96fb6df73.png','df84977d-ff80-4214-bbf8-d6a96fb6df73'),
(24,'메가)완쏠유형입문공통수학1(24)','9791129712240',3,'',8,16,NULL,NULL,NULL,'books/barcodes/barcode_9791129712240.png','books/qrcodes/qr_6851ca42-31e6-46d9-8d8f-686cce9d8a60.png','6851ca42-31e6-46d9-8d8f-686cce9d8a60');
/*!40000 ALTER TABLE `books_book` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `bookstore_book`
--

DROP TABLE IF EXISTS `bookstore_book`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `bookstore_book` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `title` varchar(200) NOT NULL,
  `isbn` varchar(50) NOT NULL,
  `author` varchar(100) DEFAULT NULL,
  `publisher` varchar(100) DEFAULT NULL,
  `original_price` int unsigned NOT NULL,
  `cost_price` int unsigned NOT NULL,
  `price` int unsigned NOT NULL,
  `stock` int unsigned NOT NULL,
  `memo` longtext,
  `created_at` datetime(6) NOT NULL,
  `supplier_id` bigint DEFAULT NULL,
  `subject_id` bigint DEFAULT NULL,
  `book_code` varchar(7) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `isbn` (`isbn`),
  UNIQUE KEY `book_code` (`book_code`),
  KEY `bookstore_book_supplier_id_6421ff9e_fk_bookstore_booksupplier_id` (`supplier_id`),
  KEY `bookstore_book_subject_id_99ef6f74_fk_subjects_id` (`subject_id`),
  CONSTRAINT `bookstore_book_subject_id_99ef6f74_fk_subjects_id` FOREIGN KEY (`subject_id`) REFERENCES `subjects` (`id`),
  CONSTRAINT `bookstore_book_supplier_id_6421ff9e_fk_bookstore_booksupplier_id` FOREIGN KEY (`supplier_id`) REFERENCES `bookstore_booksupplier` (`id`),
  CONSTRAINT `bookstore_book_chk_1` CHECK ((`original_price` >= 0)),
  CONSTRAINT `bookstore_book_chk_2` CHECK ((`cost_price` >= 0)),
  CONSTRAINT `bookstore_book_chk_3` CHECK ((`price` >= 0)),
  CONSTRAINT `bookstore_book_chk_4` CHECK ((`stock` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bookstore_book`
--

LOCK TABLES `bookstore_book` WRITE;
/*!40000 ALTER TABLE `bookstore_book` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `bookstore_book` VALUES
(5,'수학의 바이블 유형 on 라이트 공통수학. 1','9791138932981','이투스에듀,이투스북 [편]','이투스에듀 : 이투스북',18000,13500,15000,2,'','2026-01-02 00:00:00.000000',1,184,'8932981'),
(6,'(新) 수학의 바이블 : 개념 : 중학. 3-2','9791164425068','저자: 강해기,권영기,김보현,김숙영,노솔,박성복,신지영,이서진,임상현,장이지,정란,천태선,이투스 중학 수학 연구회','이투스에듀 : 이투스북',15000,11250,12000,2,'','2026-01-02 00:00:00.000000',1,189,'4425068'),
(7,'22개정 수력충전 대수','9791162408391','장철희','(주)수경출판사',18500,13875,14500,1,'','2026-01-02 00:00:00.000000',1,186,'2408391'),
(10,'수학의 바이블 개념 on : 공통수학','9791138919036','이투스에듀,이투스북 [편]','이투스에듀 : 이투스북',21000,15750,16000,1,'실제로는 9권, 배부는 장현정,송은채,박주하,김민관,김수근,안유솔,김승호,최보영','2025-11-21 00:00:00.000000',1,186,'8919036'),
(11,'수학의 바이블 개념 on : 대수','9791138923989','이투스에듀,이투스북 [편]','이투스에듀 : 이투스북',21000,15750,17000,0,'','2026-01-12 00:00:00.000000',1,186,'8923989'),
(12,'수력충전 : 확률과 통계','9791162400661','수경출판사 [편]','수경출판사',11500,8625,9000,0,'','2026-01-12 00:00:00.000000',1,33,'2400661'),
(13,'심플 자이스토리 SIMPLE Xistory 미적분 (2026년용)','9791162400821','김민수 등저','(주)수경출판사',13000,9750,10000,1,'','2026-01-12 00:00:00.000000',1,32,'2400821'),
(14,'신 수학의 바이블 개념 중학 수학 3-1 (2026년용)','9791164422777','강해기, 이투스 중학 수학 연구회 등저','이투스에듀 : 이투스북',15000,11250,12000,1,'','2026-01-02 00:00:00.000000',1,189,'4422777'),
(15,'수학의 바이블 개념on 중학수학. 1-1','9791138923910','이투스에듀,이투스북 [편]','이투스에듀 : 이투스북',19000,14250,15000,0,'','2026-01-02 00:00:00.000000',1,187,'8923910'),
(16,'수학의 바이블 개념ON 중학수학 2-2 (2026년)','9791138930567','이투스에듀','이투스에듀 : 이투스북',19000,14250,15000,1,'','2026-01-12 00:00:00.000000',1,188,'8930567'),
(17,'수학의 바이블 개념on 중학수학. 2-1','9791138930543','이투스에듀,이투스북 [편]','이투스에듀 : 이투스북',19000,14250,15000,1,'','2025-12-19 00:00:00.000000',1,188,'8930543'),
(18,'블랙라벨 중학 수학 3-2 (2026년용)','9788960764583','이문호, 김원중, 김숙영, 강희윤 공저','진학사',12000,9000,10000,1,'','2025-12-19 00:00:00.000000',1,189,'0764583'),
(19,'어삼쉬사 수학I : 240제','9791138918053','집필진: 강정우,김명석,김상철,김성준,김원일,김의석,김정배,김형균,김형정,박상윤,박원균,유병범,이경진,이대원,이병하,이종일,정연석,차순규,최현탁','이투스에듀 : 이투스북',15000,11250,12000,2,'','2026-12-23 00:00:00.000000',1,30,'8918053'),
(20,'어삼쉬사 수학II : 240제','9791138918060','집필진: 강정우,김명석,김상철,김성준,김원일,김의석,김정배,김형균,김형정,박상윤,박원균,유병범,이경진,이대원,이병하,이종일,정연석,차순규,최현탁','이투스에듀 : 이투스북',15000,11250,12000,11,'','2026-12-23 00:00:00.000000',1,31,'8918060'),
(21,'짱 중요한 유형 수학1 (2025년)','9791191229936','이창주','아름다운샘',16000,12000,13000,3,'','2026-12-26 00:00:00.000000',1,30,'1229936'),
(22,'짱 중요한 유형 수학2 (2025년)','9791191229950','이창주','아름다운샘',16000,12000,13000,5,'','2026-12-26 00:00:00.000000',1,31,'1229950'),
(23,'메가스터디 N제 통합과학1','9791129714206','집필해 주신 선생님: 김연귀,노동규,박종웅,이진우,장풍,정성원,조현재,채규선,권태현','메가스터디 : 메가스터디books',16000,12000,13000,2,'','2025-12-26 00:00:00.000000',2,107,'9714206'),
(24,'메가스터디 N제 통합과학2','9791129714374','집필해 주신 선생님: 김연귀,노동규,박종웅,이진우,장풍,정성원,조현재,채규선,권태현','메가스터디 : 메가스터디books',16000,12000,13000,8,'','2025-12-26 00:00:00.000000',2,107,'9714374'),
(25,'블랙라벨 중학 수학 2-2 (2025년용)','9788960764408','이문호, 김원중, 김숙영, 강희윤 공저','진학사',13000,9750,12000,0,'','2025-11-25 00:00:00.000000',1,188,'0764408');
/*!40000 ALTER TABLE `bookstore_book` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `bookstore_bookdistribution`
--

DROP TABLE IF EXISTS `bookstore_bookdistribution`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `bookstore_bookdistribution` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `sold_date` date NOT NULL,
  `quantity` int unsigned NOT NULL,
  `notes` longtext NOT NULL,
  `student_id` bigint NOT NULL,
  `book_stock_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `bookstore_bookdistri_student_id_fa0fdc00_fk_students_` (`student_id`),
  KEY `bookstore_bookdistri_book_stock_id_634a656b_fk_bookstore` (`book_stock_id`),
  CONSTRAINT `bookstore_bookdistri_book_stock_id_634a656b_fk_bookstore` FOREIGN KEY (`book_stock_id`) REFERENCES `bookstore_bookstock` (`id`),
  CONSTRAINT `bookstore_bookdistri_student_id_fa0fdc00_fk_students_` FOREIGN KEY (`student_id`) REFERENCES `students_student` (`id`),
  CONSTRAINT `bookstore_bookdistribution_chk_1` CHECK ((`quantity` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bookstore_bookdistribution`
--

LOCK TABLES `bookstore_bookdistribution` WRITE;
/*!40000 ALTER TABLE `bookstore_bookdistribution` DISABLE KEYS */;
set autocommit=0;
/*!40000 ALTER TABLE `bookstore_bookdistribution` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `bookstore_bookissue`
--

DROP TABLE IF EXISTS `bookstore_bookissue`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `bookstore_bookissue` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `quantity` int unsigned NOT NULL,
  `issued_date` date NOT NULL,
  `memo` longtext,
  `student_id` bigint NOT NULL,
  `book_stock_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `bookstore_bookissue_student_id_805fad7c_fk_students_student_id` (`student_id`),
  KEY `bookstore_bookissue_book_stock_id_f4a76fb6_fk_bookstore` (`book_stock_id`),
  CONSTRAINT `bookstore_bookissue_book_stock_id_f4a76fb6_fk_bookstore` FOREIGN KEY (`book_stock_id`) REFERENCES `bookstore_bookstock` (`id`),
  CONSTRAINT `bookstore_bookissue_student_id_805fad7c_fk_students_student_id` FOREIGN KEY (`student_id`) REFERENCES `students_student` (`id`),
  CONSTRAINT `bookstore_bookissue_chk_1` CHECK ((`quantity` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bookstore_bookissue`
--

LOCK TABLES `bookstore_bookissue` WRITE;
/*!40000 ALTER TABLE `bookstore_bookissue` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `bookstore_bookissue` VALUES
(21,1,'2024-12-13','',56,7),
(22,1,'2024-12-13','',60,7);
/*!40000 ALTER TABLE `bookstore_bookissue` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `bookstore_bookreturn`
--

DROP TABLE IF EXISTS `bookstore_bookreturn`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `bookstore_bookreturn` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `quantity` int unsigned NOT NULL,
  `return_date` date NOT NULL,
  `book_stock_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `bookstore_bookreturn_book_stock_id_900a5e2d_fk_bookstore` (`book_stock_id`),
  CONSTRAINT `bookstore_bookreturn_book_stock_id_900a5e2d_fk_bookstore` FOREIGN KEY (`book_stock_id`) REFERENCES `bookstore_bookstock` (`id`),
  CONSTRAINT `bookstore_bookreturn_chk_1` CHECK ((`quantity` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bookstore_bookreturn`
--

LOCK TABLES `bookstore_bookreturn` WRITE;
/*!40000 ALTER TABLE `bookstore_bookreturn` DISABLE KEYS */;
set autocommit=0;
/*!40000 ALTER TABLE `bookstore_bookreturn` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `bookstore_booksale`
--

DROP TABLE IF EXISTS `bookstore_booksale`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `bookstore_booksale` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `sale_date` date NOT NULL,
  `price` int unsigned NOT NULL,
  `quantity` int unsigned NOT NULL,
  `is_paid` tinyint(1) NOT NULL,
  `payment_date` date DEFAULT NULL,
  `memo` varchar(255) DEFAULT NULL,
  `book_id` bigint NOT NULL,
  `student_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `bookstore_booksale_book_id_706cf94c_fk_bookstore_book_id` (`book_id`),
  KEY `bookstore_booksale_student_id_935672df_fk_students_student_id` (`student_id`),
  CONSTRAINT `bookstore_booksale_book_id_706cf94c_fk_bookstore_book_id` FOREIGN KEY (`book_id`) REFERENCES `bookstore_book` (`id`),
  CONSTRAINT `bookstore_booksale_student_id_935672df_fk_students_student_id` FOREIGN KEY (`student_id`) REFERENCES `students_student` (`id`),
  CONSTRAINT `bookstore_booksale_chk_1` CHECK ((`price` >= 0)),
  CONSTRAINT `bookstore_booksale_chk_2` CHECK ((`quantity` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=48 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bookstore_booksale`
--

LOCK TABLES `bookstore_booksale` WRITE;
/*!40000 ALTER TABLE `bookstore_booksale` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `bookstore_booksale` VALUES
(4,'2026-01-12',17000,1,0,NULL,NULL,11,101),
(5,'2026-01-12',17000,1,0,NULL,NULL,11,102),
(6,'2026-01-12',10000,1,1,'2026-01-17',NULL,13,103),
(7,'2026-01-16',10000,1,0,NULL,NULL,13,109),
(8,'2026-01-12',10000,1,1,'2026-01-17',NULL,13,105),
(9,'2026-01-12',10000,1,1,'2026-01-17',NULL,13,111),
(10,'2026-01-12',10000,1,0,NULL,NULL,13,107),
(11,'2026-01-12',9000,1,0,NULL,NULL,12,108),
(12,'2026-01-12',9000,1,0,NULL,NULL,12,107),
(13,'2026-01-12',9000,1,0,NULL,NULL,12,106),
(14,'2026-01-12',9000,1,1,'2026-01-17',NULL,12,105),
(15,'2026-01-12',9000,1,1,'2026-01-17',NULL,12,110),
(16,'2026-01-12',9000,1,1,'2026-01-17',NULL,12,104),
(17,'2026-01-03',14500,1,1,'2026-01-17',NULL,7,101),
(18,'2026-01-03',14500,1,1,'2026-01-17',NULL,7,97),
(19,'2026-01-03',14500,1,1,'2026-01-17',NULL,7,99),
(20,'2026-01-03',14500,1,1,'2026-01-17',NULL,7,102),
(21,'2026-01-03',14500,1,1,'2026-01-17',NULL,7,100),
(23,'2026-01-12',12000,1,0,NULL,NULL,6,71),
(24,'2026-01-07',15000,1,1,'2026-01-17',NULL,5,93),
(25,'2026-01-02',15000,1,1,'2026-01-17',NULL,15,83),
(26,'2026-01-12',12000,1,1,'2026-01-17',NULL,14,84),
(27,'2026-01-02',12000,1,1,'2026-01-17',NULL,14,69),
(28,'2026-01-16',15000,1,0,NULL,NULL,16,75),
(29,'2026-12-26',12000,1,1,'2026-01-17',NULL,19,104),
(30,'2026-01-16',12000,1,0,NULL,NULL,19,112),
(31,'2026-12-26',12000,1,0,NULL,NULL,19,106),
(32,'2026-12-26',12000,1,1,'2026-01-17',NULL,19,103),
(33,'2026-12-26',12000,1,1,'2026-01-17',NULL,19,109),
(34,'2026-12-26',12000,1,1,'2026-01-17',NULL,19,105),
(35,'2026-12-26',12000,1,1,'2026-01-17',NULL,19,110),
(36,'2026-12-26',12000,1,0,NULL,NULL,19,108),
(37,'2026-12-26',12000,1,1,'2026-01-17',NULL,19,111),
(38,'2025-12-26',13000,1,0,NULL,NULL,21,107),
(39,'2025-12-26',13000,1,1,'2026-01-17',NULL,21,110),
(40,'2025-12-27',13000,1,1,'2026-01-17',NULL,23,89),
(42,'2026-01-10',13000,1,0,NULL,NULL,23,85),
(43,'2025-12-27',13000,1,1,'2026-01-17',NULL,23,90),
(44,'2025-12-27',13000,1,1,'2026-01-17',NULL,23,88),
(45,'2025-12-27',13000,1,1,'2026-01-17',NULL,23,96),
(46,'2025-12-27',13000,1,1,'2026-01-17',NULL,23,79),
(47,'2026-01-02',12000,1,0,NULL,NULL,25,79);
/*!40000 ALTER TABLE `bookstore_booksale` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `bookstore_bookstock`
--

DROP TABLE IF EXISTS `bookstore_bookstock`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `bookstore_bookstock` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `quantity` int unsigned NOT NULL,
  `list_price` int unsigned NOT NULL,
  `unit_price` int unsigned NOT NULL,
  `selling_price` int unsigned NOT NULL,
  `memo` longtext NOT NULL,
  `received_date` date NOT NULL,
  `book_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `bookstore_bookstock_book_id_d9d5441a_fk_books_book_id` (`book_id`),
  CONSTRAINT `bookstore_bookstock_book_id_d9d5441a_fk_books_book_id` FOREIGN KEY (`book_id`) REFERENCES `books_book` (`id`),
  CONSTRAINT `bookstore_bookstock_chk_1` CHECK ((`quantity` >= 0)),
  CONSTRAINT `bookstore_bookstock_chk_2` CHECK ((`list_price` >= 0)),
  CONSTRAINT `bookstore_bookstock_chk_3` CHECK ((`unit_price` >= 0)),
  CONSTRAINT `bookstore_bookstock_chk_4` CHECK ((`selling_price` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bookstore_bookstock`
--

LOCK TABLES `bookstore_bookstock` WRITE;
/*!40000 ALTER TABLE `bookstore_bookstock` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `bookstore_bookstock` VALUES
(7,6,15000,11250,12000,'','2024-12-13',24);
/*!40000 ALTER TABLE `bookstore_bookstock` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `bookstore_bookstocklog`
--

DROP TABLE IF EXISTS `bookstore_bookstocklog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `bookstore_bookstocklog` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `quantity` int NOT NULL,
  `cost_price` int unsigned NOT NULL,
  `total_payment` int unsigned NOT NULL,
  `payment_date` date DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `memo` varchar(255) DEFAULT NULL,
  `is_paid` tinyint(1) NOT NULL,
  `book_id` bigint NOT NULL,
  `supplier_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `bookstore_bookstocklog_book_id_f52ff955_fk_bookstore_book_id` (`book_id`),
  KEY `bookstore_bookstockl_supplier_id_64fabdf4_fk_bookstore` (`supplier_id`),
  CONSTRAINT `bookstore_bookstockl_supplier_id_64fabdf4_fk_bookstore` FOREIGN KEY (`supplier_id`) REFERENCES `bookstore_booksupplier` (`id`),
  CONSTRAINT `bookstore_bookstocklog_book_id_f52ff955_fk_bookstore_book_id` FOREIGN KEY (`book_id`) REFERENCES `bookstore_book` (`id`),
  CONSTRAINT `bookstore_bookstocklog_chk_1` CHECK ((`cost_price` >= 0)),
  CONSTRAINT `bookstore_bookstocklog_chk_2` CHECK ((`total_payment` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bookstore_bookstocklog`
--

LOCK TABLES `bookstore_bookstocklog` WRITE;
/*!40000 ALTER TABLE `bookstore_bookstocklog` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `bookstore_bookstocklog` VALUES
(5,3,13500,40500,NULL,'2026-01-15 00:00:00.000000','신규 도서 등록 (초기 재고)',0,5,1),
(6,3,11250,33750,NULL,'2026-01-15 00:00:00.000000','신규 도서 등록 (초기 재고)',0,6,1),
(7,6,13875,83250,NULL,'2026-01-02 00:00:00.000000','신규 도서 등록 (초기 재고)',0,7,1),
(10,1,15750,15750,NULL,'2025-11-21 00:00:00.000000','신규 도서 등록 (초기 재고)',0,10,1),
(11,2,15750,31500,NULL,'2026-01-12 00:00:00.000000','신규 도서 등록 (초기 재고)',0,11,1),
(12,6,8625,51750,NULL,'2026-01-12 00:00:00.000000','신규 도서 등록 (초기 재고)',0,12,1),
(13,6,9750,58500,NULL,'2026-01-12 00:00:00.000000','신규 도서 등록 (초기 재고)',0,13,1),
(14,3,11250,33750,NULL,'2026-01-02 00:00:00.000000','신규 도서 등록 (초기 재고)',0,14,1),
(15,1,14250,14250,NULL,'2026-01-02 00:00:00.000000','신규 도서 등록 (초기 재고)',0,15,1),
(16,2,14250,28500,NULL,'2026-01-12 00:00:00.000000','신규 도서 등록 (초기 재고)',0,16,1),
(17,1,14250,14250,NULL,'2025-12-19 00:00:00.000000','신규 도서 등록 (초기 재고)',0,17,1),
(18,1,9000,9000,NULL,'2025-12-19 00:00:00.000000','신규 도서 등록 (초기 재고)',0,18,1),
(19,11,11250,123750,NULL,'2026-12-23 00:00:00.000000','신규 도서 등록 (초기 재고)',0,19,1),
(20,11,11250,123750,NULL,'2026-12-23 00:00:00.000000','신규 도서 등록 (초기 재고)',0,20,1),
(21,5,12000,60000,NULL,'2026-01-17 00:00:00.000000','신규 도서 등록 (초기 재고)',0,21,1),
(22,5,12000,60000,NULL,'2026-12-26 00:00:00.000000','신규 도서 등록 (초기 재고)',0,22,1),
(23,8,12000,96000,NULL,'2025-12-26 00:00:00.000000','신규 도서 등록 (초기 재고)',0,23,2),
(24,8,12000,96000,NULL,'2025-12-26 00:00:00.000000','신규 도서 등록 (초기 재고)',0,24,2),
(25,1,9750,9750,NULL,'2025-11-25 00:00:00.000000','신규 도서 등록 (초기 재고)',0,25,1);
/*!40000 ALTER TABLE `bookstore_bookstocklog` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `bookstore_booksupplier`
--

DROP TABLE IF EXISTS `bookstore_booksupplier`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `bookstore_booksupplier` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `registration_number` varchar(50) DEFAULT NULL,
  `phone` varchar(50) DEFAULT NULL,
  `address` varchar(255) DEFAULT NULL,
  `bank_name` varchar(50) DEFAULT NULL,
  `account_number` varchar(100) DEFAULT NULL,
  `account_owner` varchar(50) DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bookstore_booksupplier`
--

LOCK TABLES `bookstore_booksupplier` WRITE;
/*!40000 ALTER TABLE `bookstore_booksupplier` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `bookstore_booksupplier` VALUES
(1,'(주)미래미디어','172-87-002','031-416-1355','경기도 안산시 단원구 대쟁이길 18-2(선부동)','국민은행','802001-04-255823','(주)미래미디어','2025-12-26 01:34:23.887953'),
(2,'오늘도서','134-92-65825','031-411-3360','경기도 안산시 상록구 방아고개길 37-6 (장하동)','기업은행','409-094880-04-015','홍귀범','2025-12-27 00:37:59.728805');
/*!40000 ALTER TABLE `bookstore_booksupplier` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `common_bank`
--

DROP TABLE IF EXISTS `common_bank`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `common_bank` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `common_bank`
--

LOCK TABLES `common_bank` WRITE;
/*!40000 ALTER TABLE `common_bank` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `common_bank` VALUES
(6,'국민은행'),
(2,'농협은행'),
(1,'신한은행'),
(7,'우리은행'),
(4,'카카오뱅크'),
(5,'케이뱅크'),
(8,'토스'),
(3,'하나은행');
/*!40000 ALTER TABLE `common_bank` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `common_publisher`
--

DROP TABLE IF EXISTS `common_publisher`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `common_publisher` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `common_publisher`
--

LOCK TABLES `common_publisher` WRITE;
/*!40000 ALTER TABLE `common_publisher` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `common_publisher` VALUES
(8,'메가스터디BOOKS'),
(7,'비상'),
(6,'이투스북');
/*!40000 ALTER TABLE `common_publisher` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `common_school`
--

DROP TABLE IF EXISTS `common_school`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `common_school` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `phone` varchar(15) DEFAULT NULL,
  `address` longtext,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=48 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `common_school`
--

LOCK TABLES `common_school` WRITE;
/*!40000 ALTER TABLE `common_school` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `common_school` VALUES
(4,'양지중학교',NULL,''),
(5,'해양중학교',NULL,''),
(6,'해솔중학교',NULL,''),
(7,'초지중학교',NULL,''),
(8,'송호중학교',NULL,''),
(9,'별망중학교',NULL,''),
(10,'본오중학교',NULL,''),
(11,'시곡중학교',NULL,''),
(12,'고잔고등학교',NULL,''),
(13,'양지고등학교',NULL,''),
(14,'송호고등학교',NULL,''),
(15,'초지고등학교',NULL,''),
(16,'부곡고등학교',NULL,''),
(17,'동산고등학교',NULL,''),
(18,'광덕고등학교',NULL,''),
(19,'원곡고등학교',NULL,''),
(20,'성포고등학교',NULL,''),
(21,'신길고등학교',NULL,''),
(22,'선부고등학교',NULL,''),
(23,'초지초등학교',NULL,''),
(24,'디지털미디어고등학교',NULL,''),
(25,'슬기초등학교',NULL,''),
(27,'송호초등학교',NULL,''),
(28,'안산고등학교',NULL,NULL),
(29,'경안고등학교',NULL,NULL),
(30,'성안고등학교',NULL,NULL),
(31,'해양중',NULL,NULL),
(32,'양지중',NULL,NULL),
(33,'송호중',NULL,NULL),
(34,'초지중',NULL,NULL),
(35,'양지초',NULL,NULL),
(36,'초지초',NULL,NULL),
(37,'청석초',NULL,NULL),
(38,'성안중',NULL,NULL),
(39,'별망중',NULL,NULL),
(40,'중앙중',NULL,NULL),
(41,'양지고',NULL,NULL),
(42,'성안고',NULL,NULL),
(43,'고잔고',NULL,NULL),
(44,'경안고',NULL,NULL),
(45,'송호고',NULL,NULL),
(46,'광덕고',NULL,NULL),
(47,'안산고',NULL,NULL);
/*!40000 ALTER TABLE `common_school` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `common_subject`
--

DROP TABLE IF EXISTS `common_subject`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `common_subject` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `common_subject`
--

LOCK TABLES `common_subject` WRITE;
/*!40000 ALTER TABLE `common_subject` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `common_subject` VALUES
(9,'고등수학(상)'),
(10,'고등수학(하)'),
(16,'공통수학1'),
(17,'공통수학2'),
(13,'기하'),
(14,'미적분'),
(11,'수학1'),
(12,'수학2'),
(18,'중1과학'),
(8,'중1수학'),
(6,'중2수학'),
(7,'중3수학'),
(15,'확률과 통계');
/*!40000 ALTER TABLE `common_subject` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `django_admin_log_chk_1` CHECK ((`action_flag` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=39 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `django_admin_log` VALUES
(1,'2024-12-13 23:52:16.750032','8','메가스터디BOOKS',1,'[{\"added\": {}}]',9,1),
(2,'2024-12-13 23:53:51.545396','5','오늘도서',1,'[{\"added\": {}}]',10,1),
(3,'2024-12-13 23:54:04.628359','5','오늘도서',2,'[{\"changed\": {\"fields\": [\"\\uc804\\ud654\\ubc88\\ud6381\"]}}]',10,1),
(4,'2024-12-13 23:55:42.135404','5','오늘도서',2,'[{\"changed\": {\"fields\": [\"\\uc0ac\\uc5c5\\uc790 \\ubc88\\ud638\"]}}]',10,1),
(5,'2024-12-14 00:30:05.090824','4','(주)미래미디어',2,'[{\"changed\": {\"fields\": [\"\\uc0ac\\uc5c5\\uc790 \\ubc88\\ud638\"]}}]',10,1),
(6,'2024-12-20 05:31:30.922622','2','메가)완쏠유형입문공통수학1(24) - 7권',3,'',23,1),
(7,'2024-12-20 05:32:18.639405','1','메가)완쏠유형입문공통수학1(24) - 8권',2,'[{\"changed\": {\"fields\": [\"\\uc218\\ub7c9\"]}}]',23,1),
(8,'2024-12-20 05:57:33.171793','1','메가)완쏠유형입문공통수학1(24) - 0권',2,'[{\"changed\": {\"fields\": [\"\\uc218\\ub7c9\"]}}]',23,1),
(9,'2024-12-20 05:58:04.468090','1','메가)완쏠유형입문공통수학1(24) - 8권',2,'[{\"changed\": {\"fields\": [\"\\uc218\\ub7c9\"]}}]',23,1),
(10,'2024-12-20 06:00:59.909833','1','메가)완쏠유형입문공통수학1(24) - 8권',3,'',23,1),
(11,'2024-12-20 06:03:29.167999','3','22개정 개념+유형 공통수학1 - 2권',3,'',23,1),
(12,'2024-12-20 22:42:12.021809','4','메가)완쏠유형입문공통수학1(24) - 3권',3,'',23,1),
(13,'2024-12-20 23:53:24.459486','6','이투스 신 수학의 바이블 중등 개념 3-1 - 3권',3,'',23,1),
(14,'2024-12-20 23:53:24.459486','5','메가)완쏠유형입문공통수학1(24) - 2권',3,'',23,1),
(15,'2025-02-22 00:46:30.653419','686','이찬혁 - 2025-02-22',3,'',14,1),
(16,'2025-02-22 00:46:30.653419','685','강연우 - 2025-02-22',3,'',14,1),
(17,'2025-02-22 00:46:30.653419','684','김동근 - 2025-02-22',3,'',14,1),
(18,'2025-02-22 00:46:30.653419','683','김지원 - 2025-02-22',3,'',14,1),
(19,'2025-02-22 00:46:30.653419','682','손정연 - 2025-02-22',3,'',14,1),
(20,'2025-02-22 00:46:30.653419','681','이시민 - 2025-02-22',3,'',14,1),
(21,'2025-02-22 00:46:30.653419','680','최예원 - 2025-02-22',3,'',14,1),
(22,'2025-02-22 00:46:30.653419','679','박주아 - 2025-02-22',3,'',14,1),
(23,'2025-02-22 00:46:30.654423','678','이동준 - 2025-02-22',3,'',14,1),
(24,'2025-02-22 00:46:30.654423','677','신유민 - 2025-02-22',3,'',14,1),
(25,'2025-07-30 00:16:45.935084','44','임시쌤',3,'',13,1),
(26,'2025-07-30 00:16:45.935118','43','김동근2nd',3,'',13,1),
(27,'2025-07-30 00:16:45.935132','42','박주아2nd',3,'',13,1),
(28,'2026-01-01 01:41:19.153934','47','JJANGDM',3,'',13,1),
(29,'2026-01-01 02:22:18.398606','32','이시민2nd',3,'',13,1),
(30,'2026-01-03 00:45:27.957718','1','얼음의 나이 : 자연의 온도계에서 찾아낸 기후변화의 메커니즘',3,'',27,1),
(31,'2026-01-09 00:18:37.853172','27','이시민',2,'[{\"changed\": {\"fields\": [\"\\ud1f4\\uc0ac\\uc77c\"]}}]',13,1),
(32,'2026-01-10 02:03:13.299664','18','박주아 - 2026-02-09 (개인 사유)',2,'[{\"changed\": {\"fields\": [\"\\uba54\\ubaa8\"]}}]',37,1),
(33,'2026-01-10 02:03:19.939187','19','박주아 - 2026-02-10 (개인 사유)',2,'[{\"changed\": {\"fields\": [\"\\uba54\\ubaa8\"]}}]',37,1),
(34,'2026-01-15 22:40:09.295843','3','(新) 수학의 바이블 : 개념 : 중학. 3-2',3,'',27,1),
(35,'2026-01-15 22:40:09.295928','2','수학의 바이블 유형 on 라이트 공통수학. 1',3,'',27,1),
(36,'2026-01-17 00:16:28.144777','9','수경 심플 자이스토리 미적분',3,'',27,1),
(37,'2026-01-17 00:25:12.555051','4','이투스 신 수학의 바이블 중등 개념 3-1',3,'',27,1),
(38,'2026-01-17 00:33:31.644255','8','수학의 바이블 개념ON 중 2-2',3,'',27,1);
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=39 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `django_content_type` VALUES
(1,'admin','logentry'),
(3,'auth','group'),
(2,'auth','permission'),
(4,'auth','user'),
(7,'books','book'),
(27,'bookstore','book'),
(20,'bookstore','bookdistribution'),
(21,'bookstore','bookissue'),
(22,'bookstore','bookreturn'),
(29,'bookstore','booksale'),
(23,'bookstore','bookstock'),
(30,'bookstore','bookstocklog'),
(28,'bookstore','booksupplier'),
(8,'common','bank'),
(9,'common','publisher'),
(10,'common','purchaselocation'),
(11,'common','school'),
(12,'common','subject'),
(5,'contenttypes','contenttype'),
(32,'grades','grade'),
(18,'maintenance','maintenance'),
(19,'maintenance','room'),
(25,'payment','bookpayment'),
(24,'payment','payment'),
(26,'payment','paymenthistory'),
(33,'progress','bookproblem'),
(36,'progress','problemtype'),
(35,'progress','progressentry'),
(34,'progress','studentprogress'),
(6,'sessions','session'),
(16,'students','student'),
(17,'students','studentfile'),
(31,'subjects','subject'),
(14,'teachers','attendance'),
(15,'teachers','salary'),
(13,'teachers','teacher'),
(38,'teachers','teacherstudentassignment'),
(37,'teachers','teacherunavailability');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=84 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `django_migrations` VALUES
(1,'contenttypes','0001_initial','2024-12-08 23:03:16.803422'),
(2,'auth','0001_initial','2024-12-08 23:03:17.664249'),
(3,'admin','0001_initial','2024-12-08 23:03:17.835535'),
(4,'admin','0002_logentry_remove_auto_add','2024-12-08 23:03:17.845333'),
(5,'admin','0003_logentry_add_action_flag_choices','2024-12-08 23:03:17.854630'),
(6,'contenttypes','0002_remove_content_type_name','2024-12-08 23:03:17.979210'),
(7,'auth','0002_alter_permission_name_max_length','2024-12-08 23:03:18.060652'),
(8,'auth','0003_alter_user_email_max_length','2024-12-08 23:03:18.110375'),
(9,'auth','0004_alter_user_username_opts','2024-12-08 23:03:18.118929'),
(10,'auth','0005_alter_user_last_login_null','2024-12-08 23:03:18.192487'),
(11,'auth','0006_require_contenttypes_0002','2024-12-08 23:03:18.196604'),
(12,'auth','0007_alter_validators_add_error_messages','2024-12-08 23:03:18.207486'),
(13,'auth','0008_alter_user_username_max_length','2024-12-08 23:03:18.259350'),
(14,'auth','0009_alter_user_last_name_max_length','2024-12-08 23:03:18.308758'),
(15,'auth','0010_alter_group_name_max_length','2024-12-08 23:03:18.360701'),
(16,'auth','0011_update_proxy_permissions','2024-12-08 23:03:18.370467'),
(17,'auth','0012_alter_user_first_name_max_length','2024-12-08 23:03:18.419981'),
(18,'common','0001_initial','2024-12-08 23:03:18.566387'),
(19,'common','0002_alter_purchaselocation_business_number_and_more','2024-12-08 23:03:18.884450'),
(20,'books','0001_initial','2024-12-08 23:03:19.131911'),
(21,'books','0002_purchaselocation_remove_book_spare1_and_more','2024-12-08 23:03:20.236325'),
(22,'books','0003_alter_book_purchase_location_and_more','2024-12-08 23:03:21.405744'),
(23,'books','0004_book_barcode_book_qr_code_book_unique_code','2024-12-08 23:03:21.574622'),
(24,'books','0005_alter_book_qr_code_alter_book_unique_code','2024-12-08 23:03:21.818445'),
(25,'books','0006_remove_book_original_price_and_more','2024-12-08 23:03:21.964981'),
(26,'books','0007_remove_book_entry_date_remove_book_purchase_location','2024-12-08 23:03:22.338036'),
(27,'students','0001_initial','2024-12-08 23:03:22.543611'),
(29,'bookstore','0002_initial','2024-12-08 23:03:23.120331'),
(30,'maintenance','0001_initial','2024-12-08 23:03:23.151134'),
(31,'maintenance','0002_room_alter_maintenance_room_and_more','2024-12-08 23:03:23.584158'),
(32,'maintenance','0003_remove_maintenance_maintenance_room_id_681cd3_idx_and_more','2024-12-08 23:03:24.653331'),
(33,'maintenance','0004_alter_maintenance_room','2024-12-08 23:03:24.890947'),
(34,'maintenance','0005_alter_room_number','2024-12-08 23:03:24.897445'),
(35,'sessions','0001_initial','2024-12-08 23:03:24.975672'),
(36,'teachers','0001_initial','2024-12-08 23:03:25.221868'),
(37,'teachers','0002_alter_teacher_account_number_alter_teacher_bank_and_more','2024-12-08 23:03:25.924257'),
(38,'teachers','0003_rename_phone_teacher_phone_number_monthlysalary_and_more','2024-12-08 23:03:26.299278'),
(39,'teachers','0004_delete_yearlysalary','2024-12-08 23:03:26.330785'),
(40,'teachers','0005_alter_monthlysalary_year_month','2024-12-08 23:03:26.406021'),
(41,'teachers','0006_alter_monthlysalary_bonus_and_more','2024-12-08 23:03:26.668680'),
(42,'teachers','0007_alter_monthlysalary_base_salary','2024-12-08 23:03:26.677185'),
(43,'teachers','0008_remove_teacher_id_number_teacher_additional_salary_and_more','2024-12-08 23:03:27.470219'),
(44,'teachers','0009_alter_teacher_options_alter_salary_additional_amount_and_more','2024-12-08 23:03:27.930245'),
(45,'teachers','0010_alter_teacher_options_alter_salary_month_and_more','2024-12-08 23:03:28.397640'),
(46,'teachers','0011_alter_attendance_options_alter_attendance_check_in_and_more','2024-12-08 23:03:28.576882'),
(47,'teachers','0012_alter_attendance_options_remove_attendance_check_in_and_more','2024-12-08 23:03:28.873604'),
(48,'teachers','0013_alter_attendance_options_attendance_end_time_and_more','2024-12-08 23:03:28.980218'),
(49,'teachers','0014_alter_teacher_hire_date_alter_teacher_is_active','2024-12-08 23:03:28.992418'),
(50,'teachers','0015_alter_attendance_options_alter_teacher_hire_date','2024-12-08 23:03:29.004369'),
(51,'teachers','0016_alter_salary_month','2024-12-08 23:03:29.011670'),
(52,'teachers','0017_alter_salary_month','2024-12-08 23:03:29.021565'),
(53,'payment','0001_initial','2024-12-20 00:37:38.792518'),
(54,'payment','0002_alter_payment_options_remove_payment_amount_and_more','2024-12-20 01:07:53.071569'),
(55,'payment','0003_alter_payment_payment_date','2024-12-20 01:11:00.760257'),
(56,'payment','0004_alter_payment_options_remove_payment_total_amount_and_more','2024-12-20 01:17:08.348532'),
(57,'payment','0005_alter_payment_payment_date','2024-12-20 01:24:48.894609'),
(58,'teachers','0018_fix_phone_validator','2025-07-29 23:53:00.291124'),
(59,'teachers','0019_alter_teacher_phone_number','2025-07-29 23:58:58.129610'),
(60,'teachers','0020_remove_teacher_additional_salary_alter_salary_month_and_more','2025-12-03 02:27:54.981581'),
(61,'bookstore','0001_initial','2025-12-24 03:40:27.172337'),
(62,'students','0002_student_unpaid_amount','2025-12-25 22:27:39.811473'),
(63,'subjects','0001_initial','2025-12-28 18:30:44.532703'),
(64,'grades','0001_initial','2025-12-28 19:26:17.143821'),
(65,'grades','0002_alter_grade_credits_alter_grade_score_and_more','2025-12-28 19:47:23.822250'),
(66,'subjects','0002_subject_category_code','2025-12-28 21:18:31.959323'),
(67,'grades','0003_grade_achievement_level_grade_distribution_a_and_more','2025-12-30 18:39:36.627057'),
(68,'bookstore','0002_add_phone2_email_to_booksupplier','2026-01-03 00:38:44.429320'),
(69,'common','0003_remove_purchaselocation','2026-01-03 00:38:44.539443'),
(70,'teachers','0021_alter_salary_month_alter_salary_year','2026-01-03 00:38:44.566481'),
(71,'progress','0001_initial','2026-01-03 00:38:48.609523'),
(72,'progress','0002_problemtype_alter_bookproblem_options_and_more','2026-01-03 00:38:50.894731'),
(73,'progress','0003_separate_difficulty_field','2026-01-04 00:24:45.090759'),
(74,'bookstore','0002_add_subject_to_book','2026-01-04 01:56:24.305575'),
(75,'bookstore','0003_merge_20260104_0155','2026-01-04 01:56:24.330209'),
(76,'bookstore','0004_add_book_code','2026-01-04 03:05:57.734891'),
(77,'bookstore','0005_populate_book_codes','2026-01-04 03:05:57.814413'),
(78,'progress','0004_update_code_number_to_20_digits','2026-01-04 03:05:57.902010'),
(79,'bookstore','0006_remove_booksupplier_email_remove_booksupplier_phone2_and_more','2026-01-05 16:55:01.898907'),
(80,'teachers','0022_teacherunavailability','2026-01-09 01:22:59.237931'),
(81,'teachers','0023_teacherstudentassignment','2026-01-09 02:17:03.802858'),
(82,'teachers','0024_add_assignment_type','2026-01-17 20:02:33.879990'),
(83,'teachers','0025_add_director_assignment_type','2026-01-17 23:15:51.081814');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `django_session` VALUES
('12a3pyb30mkfnr1x1ucetcdylo6vwbev','.eJxVjEEOwiAQRe_C2hCmA53i0r1nIANMpWpoUtqV8e7apAvd_vfef6nA21rC1mQJU1ZnBer0u0VOD6k7yHeut1mnua7LFPWu6IM2fZ2zPC-H-3dQuJVv3SUwDjyRt4bJuCR5QHEI2Y4yUsJuYOPBpgiChpBizyjRZnK-N07U-wPDpTc9:1tdsQ3:tPuHz-YqqE-l1LinurI8R-X-ks94G5rmx5Wskq3QxmA','2025-02-14 23:54:55.396676'),
('16imy382ah53uxzftoh1q723y3c9hvnc','.eJxVjEEOwiAQRe_C2hCmA53i0r1nIANMpWpoUtqV8e7apAvd_vfef6nA21rC1mQJU1ZnBer0u0VOD6k7yHeut1mnua7LFPWu6IM2fZ2zPC-H-3dQuJVv3SUwDjyRt4bJuCR5QHEI2Y4yUsJuYOPBpgiChpBizyjRZnK-N07U-wPDpTc9:1tawff:-iiuTX_WqGfqUH311-9xDXxPQXtbuWWONoSOSTezqY8','2025-02-06 21:50:55.243353'),
('23ht97s5yservbn69g0aks8j2p2txnib','.eJxVjEEOwiAQRe_C2hCmA53i0r1nIANMpWpoUtqV8e7apAvd_vfef6nA21rC1mQJU1ZnBer0u0VOD6k7yHeut1mnua7LFPWu6IM2fZ2zPC-H-3dQuJVv3SUwDjyRt4bJuCR5QHEI2Y4yUsJuYOPBpgiChpBizyjRZnK-N07U-wPDpTc9:1uXfoq:9dynYU75FuCzC8527SicJDO0pCoXrlh-CqhBhJ82gkU','2025-07-18 21:47:08.416482'),
('2hznl8s8jxdhquaefs9i49egv0687wnx','.eJxVjEEOwiAQRe_C2pAKDgwu3XsGMgODVA1NSrsy3l2bdKHb_977LxVpXWpcu8xxzOqsjurwuzGlh7QN5Du126TT1JZ5ZL0peqddX6csz8vu_h1U6vVbp-AYIMiACZIngy4AgCEDxXp0LL6AdXwyNhtncwgongMJDmi5EKn3B8swN5g:1v3ElG:QWyiiP5-NOvqYrlfmYTj8ImhKL4gofLhIRmPZfaewUE','2025-10-13 23:21:54.315309'),
('33a30sne04pfj8jgibiq29uo6wli3de0','.eJxVjEEOwiAQRe_C2pAKDgwu3XsGMgODVA1NSrsy3l2bdKHb_977LxVpXWpcu8xxzOqsjurwuzGlh7QN5Du126TT1JZ5ZL0peqddX6csz8vu_h1U6vVbp-AYIMiACZIngy4AgCEDxXp0LL6AdXwyNhtncwgongMJDmi5EKn3B8swN5g:1vDPyF:qvlcGxj1gRSIq0g_-cLkTfQWPYwxLFXyGO-VgSReBmY','2025-11-11 01:21:23.751422'),
('3v9ej4yw76v9gyoksqdxgg4kuqikevf9','.eJxVjEEOwiAQRe_C2pAKDgwu3XsGMgODVA1NSrsy3l2bdKHb_977LxVpXWpcu8xxzOqsjurwuzGlh7QN5Du126TT1JZ5ZL0peqddX6csz8vu_h1U6vVbp-AYIMiACZIngy4AgCEDxXp0LL6AdXwyNhtncwgongMJDmi5EKn3B8swN5g:1vMSTg:-kCJjSm4qaASUG4MjXfImmpVPiySEPptRPcI3LAk3UI','2025-12-05 23:51:12.350503'),
('5crr8ebzzvme9laukl2rk73o19qkhz0b','.eJxVjEEOwiAQRe_C2pAKDgwu3XsGMgODVA1NSrsy3l2bdKHb_977LxVpXWpcu8xxzOqsjurwuzGlh7QN5Du126TT1JZ5ZL0peqddX6csz8vu_h1U6vVbp-AYIMiACZIngy4AgCEDxXp0LL6AdXwyNhtncwgongMJDmi5EKn3B8swN5g:1vSbXg:XlclBRaac3tgjkJp6vvrtdpNCA-oUkScBwWsOAWnemc','2025-12-22 22:44:44.054333'),
('5xkboo7semej1rywqc7zsujnurh62hk8','.eJxVjEEOwiAQRe_C2pAKDgwu3XsGMgODVA1NSrsy3l2bdKHb_977LxVpXWpcu8xxzOqsjurwuzGlh7QN5Du126TT1JZ5ZL0peqddX6csz8vu_h1U6vVbp-AYIMiACZIngy4AgCEDxXp0LL6AdXwyNhtncwgongMJDmi5EKn3B8swN5g:1vY5pU:bafhXR1Xik1KambqgnslM8XaQwch9VcOyjZznpJUcig','2026-01-07 02:05:48.364584'),
('61n1xj715rdo1do0g7uddb6jouqakak0','.eJxVjEEOwiAQRe_C2hCmA53i0r1nIANMpWpoUtqV8e7apAvd_vfef6nA21rC1mQJU1ZnBer0u0VOD6k7yHeut1mnua7LFPWu6IM2fZ2zPC-H-3dQuJVv3SUwDjyRt4bJuCR5QHEI2Y4yUsJuYOPBpgiChpBizyjRZnK-N07U-wPDpTc9:1uLjdl:fhWUvwJqACfE-SdVbGIlBh6yBXOSly2ILn7Ndlpbl4g','2025-06-15 23:26:21.569819'),
('802xjy8d4oakzcrd1fuv11i4xcg2ahob','.eJxVjEEOwiAQRe_C2pAKDgwu3XsGMgODVA1NSrsy3l2bdKHb_977LxVpXWpcu8xxzOqsjurwuzGlh7QN5Du126TT1JZ5ZL0peqddX6csz8vu_h1U6vVbp-AYIMiACZIngy4AgCEDxXp0LL6AdXwyNhtncwgongMJDmi5EKn3B8swN5g:1vRBdI:-q1ovjUdxHlDtCpRI84L44BukeOLs-lgF_yPFqbe5Bs','2025-12-19 00:52:40.778545'),
('89ctcrgbyvojvqqiljpetn2zpoglj25c','.eJxVjEEOwiAQRe_C2hCmA53i0r1nIANMpWpoUtqV8e7apAvd_vfef6nA21rC1mQJU1ZnBer0u0VOD6k7yHeut1mnua7LFPWu6IM2fZ2zPC-H-3dQuJVv3SUwDjyRt4bJuCR5QHEI2Y4yUsJuYOPBpgiChpBizyjRZnK-N07U-wPDpTc9:1toi8Q:ymLama2ud8o9z9YZtvkq_ti5Fs_VmOrVND2HGR38_cU','2025-03-16 21:09:30.923822'),
('8pech06ukjahtmjqp833bku2a9luqtbs','.eJxVjEEOwiAQRe_C2pAKDgwu3XsGMgODVA1NSrsy3l2bdKHb_977LxVpXWpcu8xxzOqsjurwuzGlh7QN5Du126TT1JZ5ZL0peqddX6csz8vu_h1U6vVbp-AYIMiACZIngy4AgCEDxXp0LL6AdXwyNhtncwgongMJDmi5EKn3B8swN5g:1vfJ1P:3C-Eu6y_CKu202dTNjw6YgqczqzmM-bb_73up7uAhWI','2026-01-26 23:35:55.979312'),
('abf22z1gtv5sf34866itn3r7fiiqx5cz','.eJxVjEEOwiAQRe_C2hCmA53i0r1nIANMpWpoUtqV8e7apAvd_vfef6nA21rC1mQJU1ZnBer0u0VOD6k7yHeut1mnua7LFPWu6IM2fZ2zPC-H-3dQuJVv3SUwDjyRt4bJuCR5QHEI2Y4yUsJuYOPBpgiChpBizyjRZnK-N07U-wPDpTc9:1tWEVn:JX8L5Oaw6wDWcy_i_KkSffXsaIBC3Y8bTRqgzE5iU4c','2025-01-24 21:53:15.482160'),
('abgt5c5p0vzevhwggsbwznftaiooltma','.eJxVjEEOwiAQRe_C2hCmA53i0r1nIANMpWpoUtqV8e7apAvd_vfef6nA21rC1mQJU1ZnBer0u0VOD6k7yHeut1mnua7LFPWu6IM2fZ2zPC-H-3dQuJVv3SUwDjyRt4bJuCR5QHEI2Y4yUsJuYOPBpgiChpBizyjRZnK-N07U-wPDpTc9:1uRDca:bt_WUCIJoqy4txxAGt9ltt163b3S3VVSzckhSKmq6NQ','2025-07-01 02:27:48.862661'),
('aufeouvird3ug46abhaomy7fa8uryjq0','.eJxVjEEOwiAQRe_C2hCmA53i0r1nIANMpWpoUtqV8e7apAvd_vfef6nA21rC1mQJU1ZnBer0u0VOD6k7yHeut1mnua7LFPWu6IM2fZ2zPC-H-3dQuJVv3SUwDjyRt4bJuCR5QHEI2Y4yUsJuYOPBpgiChpBizyjRZnK-N07U-wPDpTc9:1tXfLe:DGUJDDVZCmXoIvUB7aPSr16ogzwP02JT0reornLKBnM','2025-01-28 20:44:42.076660'),
('bcfautbqs89e1jp3cjj6f93h3kuz1o9c','.eJxVjEEOwiAQRe_C2pAKDgwu3XsGMgODVA1NSrsy3l2bdKHb_977LxVpXWpcu8xxzOqsjurwuzGlh7QN5Du126TT1JZ5ZL0peqddX6csz8vu_h1U6vVbp-AYIMiACZIngy4AgCEDxXp0LL6AdXwyNhtncwgongMJDmi5EKn3B8swN5g:1vQT5L:8XQmm60-ceIUds1YpGGDUBkcmZ2WuWy_FXBxRMannSI','2025-12-17 01:18:39.912283'),
('bgqueq92hnzgwnzs4zwezpeo9oqe6wt0','.eJxVjEEOwiAQRe_C2pAKDgwu3XsGMgODVA1NSrsy3l2bdKHb_977LxVpXWpcu8xxzOqsjurwuzGlh7QN5Du126TT1JZ5ZL0peqddX6csz8vu_h1U6vVbp-AYIMiACZIngy4AgCEDxXp0LL6AdXwyNhtncwgongMJDmi5EKn3B8swN5g:1vRVn3:2oI_Mp6Vo2ImdMI9ynd9wI5th3RAF3MryLO5373nC5Q','2025-12-19 22:24:05.647357'),
('byah1ekxoz07im3s7zjbx2nymve4twq9','.eJxVjEEOwiAQRe_C2hCmA53i0r1nIANMpWpoUtqV8e7apAvd_vfef6nA21rC1mQJU1ZnBer0u0VOD6k7yHeut1mnua7LFPWu6IM2fZ2zPC-H-3dQuJVv3SUwDjyRt4bJuCR5QHEI2Y4yUsJuYOPBpgiChpBizyjRZnK-N07U-wPDpTc9:1tbJq3:Jg91ngVKjZEl_GEPxorck3V-PJ9FG3_yOLyolBzI_vU','2025-02-07 22:35:11.168817'),
('camzx2mdu35rtycoluhjqp3ffa3ixo1g','.eJxVjEEOwiAQRe_C2pAKDgwu3XsGMgODVA1NSrsy3l2bdKHb_977LxVpXWpcu8xxzOqsjurwuzGlh7QN5Du126TT1JZ5ZL0peqddX6csz8vu_h1U6vVbp-AYIMiACZIngy4AgCEDxXp0LL6AdXwyNhtncwgongMJDmi5EKn3B8swN5g:1us17m:wYms6xfLOo31B_3LzVclBdrI_nExi_mpwyuFNhrVjpA','2025-09-13 00:34:46.704784'),
('cjfetv2gbtrjva7ivc2ywnkkr5tt74gf','.eJxVjEEOwiAQRe_C2pAKDgwu3XsGMgODVA1NSrsy3l2bdKHb_977LxVpXWpcu8xxzOqsjurwuzGlh7QN5Du126TT1JZ5ZL0peqddX6csz8vu_h1U6vVbp-AYIMiACZIngy4AgCEDxXp0LL6AdXwyNhtncwgongMJDmi5EKn3B8swN5g:1ugPhn:liOu3njf5ZEUdpzMiph_bWThNYBur1oigMRT2hoZR0c','2025-08-12 00:23:59.957558'),
('cmf1vx33n98x4485gxurqlo4d9bh8ple','.eJxVjEEOwiAQRe_C2pAKDgwu3XsGMgODVA1NSrsy3l2bdKHb_977LxVpXWpcu8xxzOqsjurwuzGlh7QN5Du126TT1JZ5ZL0peqddX6csz8vu_h1U6vVbp-AYIMiACZIngy4AgCEDxXp0LL6AdXwyNhtncwgongMJDmi5EKn3B8swN5g:1v8Jaj:TTJ3NZXio--yfKlNpXj45k3SKboVaBjsvrsKTWMQPj0','2025-10-27 23:32:01.528915'),
('cw0lwu58c5mp1aoxe2nxk5uuhb46hlma','.eJxVjEEOwiAQRe_C2pAKDgwu3XsGMgODVA1NSrsy3l2bdKHb_977LxVpXWpcu8xxzOqsjurwuzGlh7QN5Du126TT1JZ5ZL0peqddX6csz8vu_h1U6vVbp-AYIMiACZIngy4AgCEDxXp0LL6AdXwyNhtncwgongMJDmi5EKn3B8swN5g:1vOgXG:T8Ydrq3EreD_-Ad0Ex4CDoKzoCZ9FhV6BPgJ2k5r0s0','2025-12-12 03:16:06.525670'),
('dw91yn9o6vrg13qaqxguu2pmuafy8n28','.eJxVjEEOwiAQRe_C2hCmA53i0r1nIANMpWpoUtqV8e7apAvd_vfef6nA21rC1mQJU1ZnBer0u0VOD6k7yHeut1mnua7LFPWu6IM2fZ2zPC-H-3dQuJVv3SUwDjyRt4bJuCR5QHEI2Y4yUsJuYOPBpgiChpBizyjRZnK-N07U-wPDpTc9:1tV583:lCEIXgC2qcbOjEkkvl_O-dGgkUb8CnDCmoG1R9XoHDQ','2025-01-21 17:39:59.528321'),
('e0ankfiowxuml1eqptp9jc0yuu334lzt','.eJxVjEEOwiAQRe_C2pAKDgwu3XsGMgODVA1NSrsy3l2bdKHb_977LxVpXWpcu8xxzOqsjurwuzGlh7QN5Du126TT1JZ5ZL0peqddX6csz8vu_h1U6vVbp-AYIMiACZIngy4AgCEDxXp0LL6AdXwyNhtncwgongMJDmi5EKn3B8swN5g:1vIVDY:baQMvw-1zuVKJh-XxvxpCcYQjYWIsKBDqKWrnqfK0Bo','2025-11-25 01:58:12.645170'),
('e90som17536l6hgcmceh8coma3dnsqxu','.eJxVjEEOwiAQRe_C2hCmA53i0r1nIANMpWpoUtqV8e7apAvd_vfef6nA21rC1mQJU1ZnBer0u0VOD6k7yHeut1mnua7LFPWu6IM2fZ2zPC-H-3dQuJVv3SUwDjyRt4bJuCR5QHEI2Y4yUsJuYOPBpgiChpBizyjRZnK-N07U-wPDpTc9:1tRtxY:O-tUFWNvI9KFLyZfZFnSe_rrfBK8j2dWyMD9VPhr9MY','2025-01-12 23:08:00.681887'),
('f4yea1n69104ffv4e2rirrdxa25nj9c5','.eJxVjEEOwiAQRe_C2hCmA53i0r1nIANMpWpoUtqV8e7apAvd_vfef6nA21rC1mQJU1ZnBer0u0VOD6k7yHeut1mnua7LFPWu6IM2fZ2zPC-H-3dQuJVv3SUwDjyRt4bJuCR5QHEI2Y4yUsJuYOPBpgiChpBizyjRZnK-N07U-wPDpTc9:1twd3W:k8HUinm3LTxzc7olgMVXMLjWoG0Qh-nnguXt8dQTABE','2025-04-07 17:21:10.906537'),
('f92pp17z1ruyt9egyhzmf3ahbs8fitl7','.eJxVjEEOwiAQRe_C2hCmA53i0r1nIANMpWpoUtqV8e7apAvd_vfef6nA21rC1mQJU1ZnBer0u0VOD6k7yHeut1mnua7LFPWu6IM2fZ2zPC-H-3dQuJVv3SUwDjyRt4bJuCR5QHEI2Y4yUsJuYOPBpgiChpBizyjRZnK-N07U-wPDpTc9:1uX0TA:nHDt8SWN-de3Nib_aoQPIfsWhsaohenZQt3wB59_qho','2025-07-17 01:38:00.586608'),
('fhk8kxr8s8q8p3ksxd9n1fhg3gtsf5uk','.eJxVjEEOwiAQRe_C2hCmA53i0r1nIANMpWpoUtqV8e7apAvd_vfef6nA21rC1mQJU1ZnBer0u0VOD6k7yHeut1mnua7LFPWu6IM2fZ2zPC-H-3dQuJVv3SUwDjyRt4bJuCR5QHEI2Y4yUsJuYOPBpgiChpBizyjRZnK-N07U-wPDpTc9:1u7ST7:g-HfQ8RB1Z8xHkJaFrXrKvWqFwtFt5vpyyELMSOt_7g','2025-05-07 14:16:21.430125'),
('gfoxl4nm8uvsz1mcj357oz7xvmn81osd','.eJxVjEEOwiAQRe_C2pAKDgwu3XsGMgODVA1NSrsy3l2bdKHb_977LxVpXWpcu8xxzOqsjurwuzGlh7QN5Du126TT1JZ5ZL0peqddX6csz8vu_h1U6vVbp-AYIMiACZIngy4AgCEDxXp0LL6AdXwyNhtncwgongMJDmi5EKn3B8swN5g:1vSbJL:8XTNnagGSLyA8NnDF4f9lWulrAa9aJFFuYuBtlZdPZ0','2025-12-22 22:29:55.262800'),
('hixmk628ufhixkgem5mdd0worub6ryq9','.eJxVjEEOwiAQRe_C2hCmA53i0r1nIANMpWpoUtqV8e7apAvd_vfef6nA21rC1mQJU1ZnBer0u0VOD6k7yHeut1mnua7LFPWu6IM2fZ2zPC-H-3dQuJVv3SUwDjyRt4bJuCR5QHEI2Y4yUsJuYOPBpgiChpBizyjRZnK-N07U-wPDpTc9:1tKILd:KPgaG2DQKVtGebgUhfjINn7-9agu0X9vZTyUtHNqA40','2024-12-22 23:33:25.275218'),
('huepjwzcg3gzf9fzo30tjo1u6mwcq3m0','.eJxVjEEOwiAQRe_C2hCmA53i0r1nIANMpWpoUtqV8e7apAvd_vfef6nA21rC1mQJU1ZnBer0u0VOD6k7yHeut1mnua7LFPWu6IM2fZ2zPC-H-3dQuJVv3SUwDjyRt4bJuCR5QHEI2Y4yUsJuYOPBpgiChpBizyjRZnK-N07U-wPDpTc9:1tR8sS:PoSSgmlpYah2_oA0gJ_G9bA1chq8rzjIutGcix92BaU','2025-01-10 20:51:36.882967'),
('i38mfoo08kuylzocvrclk2pcrmmb1ise','.eJxVjEEOwiAQRe_C2pAKDgwu3XsGMgODVA1NSrsy3l2bdKHb_977LxVpXWpcu8xxzOqsjurwuzGlh7QN5Du126TT1JZ5ZL0peqddX6csz8vu_h1U6vVbp-AYIMiACZIngy4AgCEDxXp0LL6AdXwyNhtncwgongMJDmi5EKn3B8swN5g:1umCkB:aEXPjRxkZ2zQdMSX6WWieUCqN3pr4vOsWZt4bZ4vGq0','2025-08-27 23:46:23.263929'),
('irk9eizp182d475gu0uhe4rd3oxqev46','.eJxVjEEOwiAQRe_C2pAKDgwu3XsGMgODVA1NSrsy3l2bdKHb_977LxVpXWpcu8xxzOqsjurwuzGlh7QN5Du126TT1JZ5ZL0peqddX6csz8vu_h1U6vVbp-AYIMiACZIngy4AgCEDxXp0LL6AdXwyNhtncwgongMJDmi5EKn3B8swN5g:1vLhzk:1vYC3roZ9A_g_IGP1fi8TWdJIOl7ILdzlg7N_2roT2Y','2025-12-03 22:13:12.001790'),
('ld5u6ocxyezqcukulwao2xjlixxfafkk','.eJxVjEEOwiAQRe_C2hCmA53i0r1nIANMpWpoUtqV8e7apAvd_vfef6nA21rC1mQJU1ZnBer0u0VOD6k7yHeut1mnua7LFPWu6IM2fZ2zPC-H-3dQuJVv3SUwDjyRt4bJuCR5QHEI2Y4yUsJuYOPBpgiChpBizyjRZnK-N07U-wPDpTc9:1uaFKR:B-cGBmrUNhbzsyHh3cBvT92UdEa8Xr3vQMGizKJfvws','2025-07-26 00:06:23.647948'),
('m2a7jd7fubqs27gspwf6ug9qgz4qw1ne','.eJxVjEEOwiAQRe_C2pAKDgwu3XsGMgODVA1NSrsy3l2bdKHb_977LxVpXWpcu8xxzOqsjurwuzGlh7QN5Du126TT1JZ5ZL0peqddX6csz8vu_h1U6vVbp-AYIMiACZIngy4AgCEDxXp0LL6AdXwyNhtncwgongMJDmi5EKn3B8swN5g:1vfJ1R:TdSuJO4YkfxNLdCc_F0GaGzG1FaljvFSMNRKMQ5in_Y','2026-01-26 23:35:57.322276'),
('mrgi1ab8wzl2zosfazj8qav3ag9c69rk','.eJxVjEEOwiAQRe_C2pAKDgwu3XsGMgODVA1NSrsy3l2bdKHb_977LxVpXWpcu8xxzOqsjurwuzGlh7QN5Du126TT1JZ5ZL0peqddX6csz8vu_h1U6vVbp-AYIMiACZIngy4AgCEDxXp0LL6AdXwyNhtncwgongMJDmi5EKn3B8swN5g:1vTMue:OvTVMdzNcy166JMaYKKL1H4e-Ee_VZ9fJF0VOqYFhCk','2025-12-25 01:19:36.431297'),
('n84l48djdi2rvups1gf5cfrl8get085t','.eJxVjEEOwiAQRe_C2pAKDgwu3XsGMgODVA1NSrsy3l2bdKHb_977LxVpXWpcu8xxzOqsjurwuzGlh7QN5Du126TT1JZ5ZL0peqddX6csz8vu_h1U6vVbp-AYIMiACZIngy4AgCEDxXp0LL6AdXwyNhtncwgongMJDmi5EKn3B8swN5g:1ux6SL:KVvxM_mCXckft0cCF5OgEL7iANmOLcuq275La7qE01A','2025-09-27 01:17:01.879692'),
('o3tyzno1u6eakzkjiuotwzz4t20mbzjj','.eJxVjEEOwiAQRe_C2hCmA53i0r1nIANMpWpoUtqV8e7apAvd_vfef6nA21rC1mQJU1ZnBer0u0VOD6k7yHeut1mnua7LFPWu6IM2fZ2zPC-H-3dQuJVv3SUwDjyRt4bJuCR5QHEI2Y4yUsJuYOPBpgiChpBizyjRZnK-N07U-wPDpTc9:1tYmgu:_hr69GO-97myqLN_URKNX2iBxecQzIPJNHpWUbi2bVQ','2025-01-31 22:47:16.805706'),
('o4v8p94rbduc2vpiz5mh0uioc92ccaqp','.eJxVjEEOwiAQRe_C2pAKDgwu3XsGMgODVA1NSrsy3l2bdKHb_977LxVpXWpcu8xxzOqsjurwuzGlh7QN5Du126TT1JZ5ZL0peqddX6csz8vu_h1U6vVbp-AYIMiACZIngy4AgCEDxXp0LL6AdXwyNhtncwgongMJDmi5EKn3B8swN5g:1vOGmA:WbQEwQDQ9xmO1Jja9_5iSyfEluGpLP27c_PcPIcDm5Q','2025-12-10 23:45:46.648766'),
('obauss27q6x28ysoor9tnbcnb1obbzsr','.eJxVjEEOwiAQRe_C2hCmA53i0r1nIANMpWpoUtqV8e7apAvd_vfef6nA21rC1mQJU1ZnBer0u0VOD6k7yHeut1mnua7LFPWu6IM2fZ2zPC-H-3dQuJVv3SUwDjyRt4bJuCR5QHEI2Y4yUsJuYOPBpgiChpBizyjRZnK-N07U-wPDpTc9:1tkm9z:yGbKOtCMAIzmxgV00YsHC-alkQ6O94UV6YWJP1_xuWA','2025-03-06 00:38:51.093188'),
('oqoz7qpq4b7htrbe8vq1i6yyeopu20sn','.eJxVjEEOwiAQRe_C2hCmA53i0r1nIANMpWpoUtqV8e7apAvd_vfef6nA21rC1mQJU1ZnBer0u0VOD6k7yHeut1mnua7LFPWu6IM2fZ2zPC-H-3dQuJVv3SUwDjyRt4bJuCR5QHEI2Y4yUsJuYOPBpgiChpBizyjRZnK-N07U-wPDpTc9:1tiDvl:2Q31orH6vs-Ep45MyAMd7Mi2AwFy_E-ytlbMj9PvUgk','2025-02-26 23:41:37.321088'),
('osq3h7v1repmosf4zw1v331eiy7ybvkk','.eJxVjEEOwiAQRe_C2hCmA53i0r1nIANMpWpoUtqV8e7apAvd_vfef6nA21rC1mQJU1ZnBer0u0VOD6k7yHeut1mnua7LFPWu6IM2fZ2zPC-H-3dQuJVv3SUwDjyRt4bJuCR5QHEI2Y4yUsJuYOPBpgiChpBizyjRZnK-N07U-wPDpTc9:1tk3e2:bZUeuyeL_J42KU-P3lcD6Ds-rZImAGB8K3ArPpC3E9Q','2025-03-04 01:06:54.621902'),
('pl0ealsqyki4e9jvxr89sfn8v2ebvz4h','.eJxVjEEOwiAQRe_C2pAKDgwu3XsGMgODVA1NSrsy3l2bdKHb_977LxVpXWpcu8xxzOqsjurwuzGlh7QN5Du126TT1JZ5ZL0peqddX6csz8vu_h1U6vVbp-AYIMiACZIngy4AgCEDxXp0LL6AdXwyNhtncwgongMJDmi5EKn3B8swN5g:1vPNVg:MdHeFgQYDwMetMDoNRIwy1EyZzkBt0vuX8PMyBVheTY','2025-12-14 01:09:20.232725'),
('q19m3bge1p5rfucmn5tqjvmnn3vupqaj','.eJxVjEEOwiAQRe_C2pAKDgwu3XsGMgODVA1NSrsy3l2bdKHb_977LxVpXWpcu8xxzOqsjurwuzGlh7QN5Du126TT1JZ5ZL0peqddX6csz8vu_h1U6vVbp-AYIMiACZIngy4AgCEDxXp0LL6AdXwyNhtncwgongMJDmi5EKn3B8swN5g:1vZpJm:S1BT6FGxU45W3UAIvEP0jWEFpdQd3UzV-3NSwFqhcw4','2026-01-11 20:52:14.384941'),
('q5it07h4ve46g1mzusw7qpshnbur6x6k','.eJxVjEEOwiAQRe_C2pAKDgwu3XsGMgODVA1NSrsy3l2bdKHb_977LxVpXWpcu8xxzOqsjurwuzGlh7QN5Du126TT1JZ5ZL0peqddX6csz8vu_h1U6vVbp-AYIMiACZIngy4AgCEDxXp0LL6AdXwyNhtncwgongMJDmi5EKn3B8swN5g:1vR91Y:dPKs-3cx5LnW9KDc6p9or1IW3R1vHlCDvSygqxg87Rs','2025-12-18 22:05:32.886428'),
('qi4qz9qqnl7cokx6i5ywido2xywxhar4','.eJxVjEEOwiAQRe_C2hCmA53i0r1nIANMpWpoUtqV8e7apAvd_vfef6nA21rC1mQJU1ZnBer0u0VOD6k7yHeut1mnua7LFPWu6IM2fZ2zPC-H-3dQuJVv3SUwDjyRt4bJuCR5QHEI2Y4yUsJuYOPBpgiChpBizyjRZnK-N07U-wPDpTc9:1u249X:D0yiseDqZE-rKQOeytKdWaSQzsjF-eXpzWsAv-_H740','2025-04-22 17:17:51.044770'),
('r2usda90xno5o4gtscqibzqm94xutqwj','.eJxVjEEOwiAQRe_C2hCmA53i0r1nIANMpWpoUtqV8e7apAvd_vfef6nA21rC1mQJU1ZnBer0u0VOD6k7yHeut1mnua7LFPWu6IM2fZ2zPC-H-3dQuJVv3SUwDjyRt4bJuCR5QHEI2Y4yUsJuYOPBpgiChpBizyjRZnK-N07U-wPDpTc9:1tLO4B:gAk0PLW-rlKmabqkx7n1_qiwoQ0xGw-4KevzhqrKgso','2024-12-25 23:51:55.615985'),
('rie9jgcfa1uaynnka301rywha89d9z31','.eJxVjEEOwiAQRe_C2hCmA53i0r1nIANMpWpoUtqV8e7apAvd_vfef6nA21rC1mQJU1ZnBer0u0VOD6k7yHeut1mnua7LFPWu6IM2fZ2zPC-H-3dQuJVv3SUwDjyRt4bJuCR5QHEI2Y4yUsJuYOPBpgiChpBizyjRZnK-N07U-wPDpTc9:1tTlUg:7RNcIR-MgKbSFq8afuz3r3td1QXu8Zcrrio-vkrselE','2025-01-18 02:29:54.266260'),
('siqlou5h7zu2fnrijb7xhijbf0417xc0','.eJxVjEEOwiAQRe_C2pAKDgwu3XsGMgODVA1NSrsy3l2bdKHb_977LxVpXWpcu8xxzOqsjurwuzGlh7QN5Du126TT1JZ5ZL0peqddX6csz8vu_h1U6vVbp-AYIMiACZIngy4AgCEDxXp0LL6AdXwyNhtncwgongMJDmi5EKn3B8swN5g:1vSvAB:Bz5AuCFoM2OeSzr5-c2TvnrpR8xepCkny9MCsseR8KY','2025-12-23 19:41:47.262010'),
('sj8pmg38dt2r7amsubzk9ok4ueopcknm','.eJxVjEEOwiAQRe_C2hCmA53i0r1nIANMpWpoUtqV8e7apAvd_vfef6nA21rC1mQJU1ZnBer0u0VOD6k7yHeut1mnua7LFPWu6IM2fZ2zPC-H-3dQuJVv3SUwDjyRt4bJuCR5QHEI2Y4yUsJuYOPBpgiChpBizyjRZnK-N07U-wPDpTc9:1thB3Y:zPeJ1TA94NFQUXI4qSITMHOFpgqvy4RhS4Uen9PO4rY','2025-02-24 02:25:20.976338'),
('sljhvy5ifta1kkemkxd73aqq2hdrjmvg','.eJxVjEEOwiAQRe_C2hCmA53i0r1nIANMpWpoUtqV8e7apAvd_vfef6nA21rC1mQJU1ZnBer0u0VOD6k7yHeut1mnua7LFPWu6IM2fZ2zPC-H-3dQuJVv3SUwDjyRt4bJuCR5QHEI2Y4yUsJuYOPBpgiChpBizyjRZnK-N07U-wPDpTc9:1tYJC4:A9LFKKPvV2AwHC-mLJYMvI3glm_-Qtd5w6vx1mCwbrE','2025-01-30 15:17:28.184166'),
('t0h3lr0i1y9k709h2cfczyhu6hzfwjcy','.eJxVjEEOwiAQRe_C2hCmA53i0r1nIANMpWpoUtqV8e7apAvd_vfef6nA21rC1mQJU1ZnBer0u0VOD6k7yHeut1mnua7LFPWu6IM2fZ2zPC-H-3dQuJVv3SUwDjyRt4bJuCR5QHEI2Y4yUsJuYOPBpgiChpBizyjRZnK-N07U-wPDpTc9:1uDR2E:sTR5695-3NqHXO4-wZ_O_q_KJE_Z8k9rAYSXLPhP2Zw','2025-05-24 01:57:18.437198'),
('u5jdhr0ul0m9s5ovjuyfigha41z7mhxn','.eJxVjEEOwiAQRe_C2pAKDgwu3XsGMgODVA1NSrsy3l2bdKHb_977LxVpXWpcu8xxzOqsjurwuzGlh7QN5Du126TT1JZ5ZL0peqddX6csz8vu_h1U6vVbp-AYIMiACZIngy4AgCEDxXp0LL6AdXwyNhtncwgongMJDmi5EKn3B8swN5g:1vPRzw:a329a-fGI7kMacOUhmLFZRVUYz5BhXnofFzdIw8AIPI','2025-12-14 05:56:52.422133'),
('wqsd6nq1yz624aqhti8bc95mlhnwsa2s','.eJxVjEEOwiAQRe_C2hCmA53i0r1nIANMpWpoUtqV8e7apAvd_vfef6nA21rC1mQJU1ZnBer0u0VOD6k7yHeut1mnua7LFPWu6IM2fZ2zPC-H-3dQuJVv3SUwDjyRt4bJuCR5QHEI2Y4yUsJuYOPBpgiChpBizyjRZnK-N07U-wPDpTc9:1tg1Bl:OBBmfBmbcIuwfC74QAEX5vlNO7JEQXIdrdDUS94eeBw','2025-02-20 21:41:01.267952'),
('xz8wb9386utpzt1cg7fxhdd94qt652dm','.eJxVjEEOwiAQRe_C2pAKDgwu3XsGMgODVA1NSrsy3l2bdKHb_977LxVpXWpcu8xxzOqsjurwuzGlh7QN5Du126TT1JZ5ZL0peqddX6csz8vu_h1U6vVbp-AYIMiACZIngy4AgCEDxXp0LL6AdXwyNhtncwgongMJDmi5EKn3B8swN5g:1vY3of:hLHdVMjp5ZJKioaqjE0v4vll0sT2R7k_hNUTo6_PxbA','2026-01-06 23:56:49.779030'),
('xzyxb9nvh5334k6pd4a5m8wcpn5aak2m','.eJxVjEEOwiAQRe_C2pAKDgwu3XsGMgODVA1NSrsy3l2bdKHb_977LxVpXWpcu8xxzOqsjurwuzGlh7QN5Du126TT1JZ5ZL0peqddX6csz8vu_h1U6vVbp-AYIMiACZIngy4AgCEDxXp0LL6AdXwyNhtncwgongMJDmi5EKn3B8swN5g:1vNZ7t:jUqthsXzXp21tSXxBxVLxCZhliQMcjLBb-5ppEsFnn8','2025-12-09 01:09:17.303826'),
('y1902920ovojiuh1hj4e58lcsmnud7vy','.eJxVjEEOwiAQRe_C2pAKDgwu3XsGMgODVA1NSrsy3l2bdKHb_977LxVpXWpcu8xxzOqsjurwuzGlh7QN5Du126TT1JZ5ZL0peqddX6csz8vu_h1U6vVbp-AYIMiACZIngy4AgCEDxXp0LL6AdXwyNhtncwgongMJDmi5EKn3B8swN5g:1vJCB9:QUaaWb37v5i7BIMYRD8pMK_y44ypo3PmEKkR3iCYwDc','2025-11-26 23:50:35.244150');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `grades`
--

DROP TABLE IF EXISTS `grades`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `grades` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `grade_type` varchar(10) NOT NULL,
  `year` int NOT NULL,
  `score` decimal(5,2) NOT NULL,
  `subject_average` decimal(5,2) NOT NULL,
  `subject_stddev` decimal(5,2) DEFAULT NULL,
  `grade_rank` int DEFAULT NULL,
  `semester` int DEFAULT NULL,
  `credits` int DEFAULT NULL,
  `is_elective` tinyint(1) NOT NULL,
  `exam_year` int DEFAULT NULL,
  `exam_month` int DEFAULT NULL,
  `exam_name` varchar(100) DEFAULT NULL,
  `percentile` decimal(5,2) DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `student_id` bigint NOT NULL,
  `subject_id` bigint NOT NULL,
  `achievement_level` varchar(1) DEFAULT NULL,
  `distribution_a` decimal(5,2) DEFAULT NULL,
  `distribution_b` decimal(5,2) DEFAULT NULL,
  `distribution_c` decimal(5,2) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `grades_subject_id_f420c12a_fk_subjects_id` (`subject_id`),
  KEY `grades_student_03b05e_idx` (`student_id`,`grade_type`),
  KEY `grades_student_2ab3e0_idx` (`student_id`,`year`),
  CONSTRAINT `grades_student_id_b4547c24_fk_students_student_id` FOREIGN KEY (`student_id`) REFERENCES `students_student` (`id`),
  CONSTRAINT `grades_subject_id_f420c12a_fk_subjects_id` FOREIGN KEY (`subject_id`) REFERENCES `subjects` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=720 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `grades`
--

LOCK TABLES `grades` WRITE;
/*!40000 ALTER TABLE `grades` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `grades` VALUES
(284,'internal',1,89.00,58.40,19.10,1,1,4,0,NULL,NULL,NULL,NULL,'2025-12-30 18:51:52.528165','2025-12-30 18:51:52.528190',41,1,NULL,NULL,NULL,NULL),
(285,'internal',1,84.00,55.80,20.70,2,1,4,0,NULL,NULL,NULL,NULL,'2025-12-30 18:51:52.532321','2025-12-30 18:51:52.532342',41,29,NULL,NULL,NULL,NULL),
(286,'internal',1,95.00,58.00,22.80,2,1,4,0,NULL,NULL,NULL,NULL,'2025-12-30 18:51:52.539465','2025-12-30 18:51:52.539496',41,53,NULL,NULL,NULL,NULL),
(287,'internal',1,90.00,64.70,20.30,2,1,3,0,NULL,NULL,NULL,NULL,'2025-12-30 18:51:52.547918','2025-12-30 18:51:52.547961',41,80,NULL,NULL,NULL,NULL),
(288,'internal',1,90.00,63.60,18.50,2,1,3,0,NULL,NULL,NULL,NULL,'2025-12-30 18:51:52.554864','2025-12-30 18:51:52.554899',41,107,NULL,NULL,NULL,NULL),
(289,'internal',1,95.00,76.30,14.20,2,1,2,0,NULL,NULL,NULL,NULL,'2025-12-30 18:51:52.567524','2025-12-30 18:51:52.567547',41,133,NULL,NULL,NULL,NULL),
(290,'internal',1,97.00,61.10,23.70,1,1,3,0,NULL,NULL,NULL,NULL,'2025-12-30 18:51:52.573920','2025-12-30 18:51:52.573942',41,132,NULL,NULL,NULL,NULL),
(291,'internal',1,93.00,64.90,22.80,2,2,4,0,NULL,NULL,NULL,NULL,'2025-12-30 18:51:52.582367','2025-12-30 18:51:52.582409',41,1,NULL,NULL,NULL,NULL),
(292,'internal',1,82.00,54.30,21.30,3,2,4,0,NULL,NULL,NULL,NULL,'2025-12-30 18:51:52.588346','2025-12-30 18:51:52.588369',41,29,NULL,NULL,NULL,NULL),
(293,'internal',1,98.00,57.10,25.40,1,2,4,0,NULL,NULL,NULL,NULL,'2025-12-30 18:51:52.597021','2025-12-30 18:51:52.597065',41,53,NULL,NULL,NULL,NULL),
(294,'internal',1,93.00,57.40,22.60,2,2,3,0,NULL,NULL,NULL,NULL,'2025-12-30 18:51:52.604871','2025-12-30 18:51:52.604896',41,80,NULL,NULL,NULL,NULL),
(295,'internal',1,95.00,61.80,20.60,2,2,3,0,NULL,NULL,NULL,NULL,'2025-12-30 18:51:52.613313','2025-12-30 18:51:52.613337',41,107,NULL,NULL,NULL,NULL),
(296,'internal',1,92.00,76.30,15.50,3,2,2,0,NULL,NULL,NULL,NULL,'2025-12-30 18:51:52.624785','2025-12-30 18:51:52.624809',41,133,NULL,NULL,NULL,NULL),
(297,'internal',1,93.00,60.80,24.30,2,2,3,0,NULL,NULL,NULL,NULL,'2025-12-30 18:51:52.632502','2025-12-30 18:51:52.632536',41,132,NULL,NULL,NULL,NULL),
(298,'internal',2,91.00,63.00,21.80,2,1,4,0,NULL,NULL,NULL,NULL,'2025-12-30 18:51:52.639884','2025-12-30 18:51:52.639918',41,3,NULL,NULL,NULL,NULL),
(299,'internal',2,90.00,49.80,21.10,1,1,4,0,NULL,NULL,NULL,NULL,'2025-12-30 18:51:52.647629','2025-12-30 18:51:52.647653',41,30,NULL,NULL,NULL,NULL),
(300,'internal',2,98.00,47.20,23.30,1,1,2,0,NULL,NULL,NULL,NULL,'2025-12-30 18:51:52.659342','2025-12-30 18:51:52.659365',41,57,NULL,NULL,NULL,NULL),
(301,'internal',2,99.00,57.30,24.70,1,1,4,0,NULL,NULL,NULL,NULL,'2025-12-30 18:51:52.666063','2025-12-30 18:51:52.666085',41,54,NULL,NULL,NULL,NULL),
(302,'internal',2,96.00,57.40,19.80,1,1,3,0,NULL,NULL,NULL,NULL,'2025-12-30 18:51:52.672758','2025-12-30 18:51:52.672783',41,82,NULL,NULL,NULL,NULL),
(303,'internal',2,96.00,64.50,21.80,1,1,3,0,NULL,NULL,NULL,NULL,'2025-12-30 18:51:52.679708','2025-12-30 18:51:52.679732',41,86,NULL,NULL,NULL,NULL),
(304,'internal',2,97.00,69.30,19.70,1,1,2,0,NULL,NULL,NULL,NULL,'2025-12-30 18:51:52.687720','2025-12-30 18:51:52.687746',41,134,NULL,NULL,NULL,NULL),
(305,'internal',2,89.00,68.50,17.20,2,1,2,0,NULL,NULL,NULL,NULL,'2025-12-30 18:51:52.694953','2025-12-30 18:51:52.694980',41,147,NULL,NULL,NULL,NULL),
(306,'internal',2,95.00,60.50,24.30,2,2,4,0,NULL,NULL,NULL,NULL,'2025-12-30 18:51:52.722903','2025-12-30 18:51:52.722926',41,4,NULL,NULL,NULL,NULL),
(307,'internal',2,93.00,49.60,23.50,1,2,4,0,NULL,NULL,NULL,NULL,'2025-12-30 18:51:52.748734','2025-12-30 18:51:52.748759',41,31,NULL,NULL,NULL,NULL),
(308,'internal',2,99.00,56.80,22.80,1,2,2,0,NULL,NULL,NULL,NULL,'2025-12-30 18:51:52.759972','2025-12-30 18:51:52.759996',41,57,NULL,NULL,NULL,NULL),
(309,'internal',2,94.00,56.00,24.20,1,2,4,0,NULL,NULL,NULL,NULL,'2025-12-30 18:51:52.766689','2025-12-30 18:51:52.766716',41,55,NULL,NULL,NULL,NULL),
(310,'internal',2,93.00,56.30,21.20,1,2,3,0,NULL,NULL,NULL,NULL,'2025-12-30 18:51:52.773879','2025-12-30 18:51:52.773904',41,82,NULL,NULL,NULL,NULL),
(311,'internal',2,98.00,56.20,24.70,1,2,3,0,NULL,NULL,NULL,NULL,'2025-12-30 18:51:52.780491','2025-12-30 18:51:52.780515',41,86,NULL,NULL,NULL,NULL),
(312,'internal',2,93.00,53.60,21.20,2,2,2,0,NULL,NULL,NULL,NULL,'2025-12-30 18:51:52.788075','2025-12-30 18:51:52.788100',41,134,NULL,NULL,NULL,NULL),
(313,'internal',2,91.00,67.20,18.20,2,2,2,0,NULL,NULL,NULL,NULL,'2025-12-30 18:51:52.796125','2025-12-30 18:51:52.796150',41,147,NULL,NULL,NULL,NULL),
(314,'internal',3,95.00,62.40,23.20,2,1,3,0,NULL,NULL,NULL,NULL,'2025-12-30 18:51:52.802990','2025-12-30 18:51:52.803017',41,2,NULL,NULL,NULL,NULL),
(315,'internal',3,94.00,53.40,24.70,2,1,3,0,NULL,NULL,NULL,NULL,'2025-12-30 18:51:52.810438','2025-12-30 18:51:52.810462',41,5,NULL,NULL,NULL,NULL),
(316,'internal',3,95.00,58.00,21.00,1,1,3,0,NULL,NULL,NULL,NULL,'2025-12-30 18:51:52.817662','2025-12-30 18:51:52.817685',41,56,NULL,NULL,NULL,NULL),
(317,'internal',3,96.00,48.70,25.60,1,1,3,0,NULL,NULL,NULL,NULL,'2025-12-30 18:51:52.825782','2025-12-30 18:51:52.825805',41,81,NULL,NULL,NULL,NULL),
(318,'internal',2,95.00,80.20,NULL,NULL,1,3,1,NULL,NULL,NULL,NULL,'2025-12-30 18:51:52.831680','2025-12-30 18:51:52.831713',41,90,'A',67.30,19.60,13.10),
(319,'internal',2,81.00,75.10,NULL,NULL,1,1,1,NULL,NULL,NULL,NULL,'2025-12-30 18:51:52.839374','2025-12-30 18:51:52.839397',41,165,'A',35.40,55.80,8.80),
(320,'internal',2,97.00,76.10,NULL,NULL,1,2,1,NULL,NULL,NULL,NULL,'2025-12-30 18:51:52.848483','2025-12-30 18:51:52.848506',41,171,'A',46.30,38.80,15.00),
(321,'internal',2,93.00,72.90,NULL,NULL,2,3,1,NULL,NULL,NULL,NULL,'2025-12-30 18:51:52.856669','2025-12-30 18:51:52.856691',41,90,'A',51.40,22.90,25.70),
(322,'internal',2,91.00,77.50,NULL,NULL,2,1,1,NULL,NULL,NULL,NULL,'2025-12-30 18:51:52.864176','2025-12-30 18:51:52.864199',41,165,'A',44.90,46.20,9.00),
(323,'internal',2,97.00,72.10,NULL,NULL,2,2,1,NULL,NULL,NULL,NULL,'2025-12-30 18:51:52.876309','2025-12-30 18:51:52.876344',41,171,'A',43.40,31.70,24.80),
(324,'internal',3,98.00,55.80,NULL,NULL,1,3,1,NULL,NULL,NULL,NULL,'2025-12-30 18:51:52.883632','2025-12-30 18:51:52.883655',41,35,'A',23.10,33.30,43.70),
(325,'internal',3,95.00,77.80,NULL,NULL,1,3,1,NULL,NULL,NULL,NULL,'2025-12-30 18:51:52.894287','2025-12-30 18:51:52.894329',41,59,'A',65.10,11.60,23.30),
(326,'internal',3,91.00,73.80,NULL,NULL,1,3,1,NULL,NULL,NULL,NULL,'2025-12-30 18:51:52.905704','2025-12-30 18:51:52.905739',41,91,'A',55.60,16.70,27.80),
(327,'internal',3,95.00,61.30,NULL,NULL,1,3,1,NULL,NULL,NULL,NULL,'2025-12-30 18:51:52.912980','2025-12-30 18:51:52.913009',41,183,'A',20.80,29.70,49.50),
(374,'internal',1,94.00,80.10,13.60,3,1,4,0,NULL,NULL,NULL,NULL,'2025-12-30 19:20:05.046625','2025-12-30 19:20:05.046649',39,1,NULL,NULL,NULL,NULL),
(375,'internal',1,96.00,77.60,10.60,1,1,4,0,NULL,NULL,NULL,NULL,'2025-12-30 19:20:05.053644','2025-12-30 19:20:05.053669',39,29,NULL,NULL,NULL,NULL),
(376,'internal',1,97.00,72.70,16.50,2,1,4,0,NULL,NULL,NULL,NULL,'2025-12-30 19:20:05.060019','2025-12-30 19:20:05.060065',39,53,NULL,NULL,NULL,NULL),
(377,'internal',1,95.00,75.50,13.90,2,1,3,0,NULL,NULL,NULL,NULL,'2025-12-30 19:20:05.067936','2025-12-30 19:20:05.067973',39,80,NULL,NULL,NULL,NULL),
(378,'internal',1,91.00,73.10,16.00,3,1,4,0,NULL,NULL,NULL,NULL,'2025-12-30 19:20:05.075981','2025-12-30 19:20:05.076018',39,107,NULL,NULL,NULL,NULL),
(379,'internal',1,89.00,70.30,15.40,3,1,2,0,NULL,NULL,NULL,NULL,'2025-12-30 19:20:05.084814','2025-12-30 19:20:05.084838',39,134,NULL,NULL,NULL,NULL),
(380,'internal',1,95.00,71.40,15.00,2,1,3,0,NULL,NULL,NULL,NULL,'2025-12-30 19:20:05.093468','2025-12-30 19:20:05.093493',39,132,NULL,NULL,NULL,NULL),
(381,'internal',1,89.00,70.20,14.60,1,2,4,0,NULL,NULL,NULL,NULL,'2025-12-30 19:20:05.100105','2025-12-30 19:20:05.100140',39,1,NULL,NULL,NULL,NULL),
(382,'internal',1,91.00,75.70,12.40,2,2,4,0,NULL,NULL,NULL,NULL,'2025-12-30 19:20:05.108983','2025-12-30 19:20:05.109008',39,29,NULL,NULL,NULL,NULL),
(383,'internal',1,96.00,70.90,15.80,2,2,4,0,NULL,NULL,NULL,NULL,'2025-12-30 19:20:05.116605','2025-12-30 19:20:05.116629',39,53,NULL,NULL,NULL,NULL),
(384,'internal',1,99.00,78.40,16.30,1,2,3,0,NULL,NULL,NULL,NULL,'2025-12-30 19:20:05.124623','2025-12-30 19:20:05.124652',39,80,NULL,NULL,NULL,NULL),
(385,'internal',1,97.00,75.70,15.90,2,2,4,0,NULL,NULL,NULL,NULL,'2025-12-30 19:20:05.132717','2025-12-30 19:20:05.132743',39,107,NULL,NULL,NULL,NULL),
(386,'internal',1,82.00,64.90,17.40,3,2,2,0,NULL,NULL,NULL,NULL,'2025-12-30 19:20:05.140192','2025-12-30 19:20:05.140216',39,134,NULL,NULL,NULL,NULL),
(387,'internal',1,99.00,71.10,15.20,1,2,3,0,NULL,NULL,NULL,NULL,'2025-12-30 19:20:05.147797','2025-12-30 19:20:05.147821',39,132,NULL,NULL,NULL,NULL),
(388,'internal',2,96.00,80.20,13.30,1,1,4,0,NULL,NULL,NULL,NULL,'2025-12-30 19:20:05.153926','2025-12-30 19:20:05.153952',39,3,NULL,NULL,NULL,NULL),
(389,'internal',2,94.00,68.30,18.30,1,1,4,0,NULL,NULL,NULL,NULL,'2025-12-30 19:20:05.161348','2025-12-30 19:20:05.161395',39,30,NULL,NULL,NULL,NULL),
(390,'internal',2,91.00,64.90,14.00,1,1,4,0,NULL,NULL,NULL,NULL,'2025-12-30 19:20:05.169364','2025-12-30 19:20:05.169405',39,54,NULL,NULL,NULL,NULL),
(391,'internal',2,89.00,66.50,16.80,3,1,4,0,NULL,NULL,NULL,NULL,'2025-12-30 19:20:05.177837','2025-12-30 19:20:05.177865',39,112,NULL,NULL,NULL,NULL),
(392,'internal',2,86.00,70.10,14.20,3,1,4,0,NULL,NULL,NULL,NULL,'2025-12-30 19:20:05.185809','2025-12-30 19:20:05.185839',39,109,NULL,NULL,NULL,NULL),
(393,'internal',2,81.00,73.80,13.30,4,1,4,0,NULL,NULL,NULL,NULL,'2025-12-30 19:20:05.193880','2025-12-30 19:20:05.193906',39,146,NULL,NULL,NULL,NULL),
(394,'internal',2,90.00,75.20,13.70,3,2,4,0,NULL,NULL,NULL,NULL,'2025-12-30 19:20:05.201805','2025-12-30 19:20:05.201830',39,4,NULL,NULL,NULL,NULL),
(395,'internal',2,92.00,64.90,20.50,2,2,4,0,NULL,NULL,NULL,NULL,'2025-12-30 19:20:05.209779','2025-12-30 19:20:05.209817',39,31,NULL,NULL,NULL,NULL),
(396,'internal',2,90.00,66.10,13.20,2,2,4,0,NULL,NULL,NULL,NULL,'2025-12-30 19:20:05.218194','2025-12-30 19:20:05.218219',39,55,NULL,NULL,NULL,NULL),
(397,'internal',2,94.00,60.30,18.00,1,2,4,0,NULL,NULL,NULL,NULL,'2025-12-30 19:20:05.227564','2025-12-30 19:20:05.227600',39,110,NULL,NULL,NULL,NULL),
(398,'internal',2,92.00,65.90,15.70,1,2,4,0,NULL,NULL,NULL,NULL,'2025-12-30 19:20:05.234731','2025-12-30 19:20:05.234755',39,111,NULL,NULL,NULL,NULL),
(399,'internal',3,81.00,66.60,20.30,4,1,3,0,NULL,NULL,NULL,NULL,'2025-12-30 19:20:05.242887','2025-12-30 19:20:05.242916',39,5,NULL,NULL,NULL,NULL),
(400,'internal',3,89.00,72.80,20.50,4,1,3,0,NULL,NULL,NULL,NULL,'2025-12-30 19:20:05.250066','2025-12-30 19:20:05.250091',39,32,NULL,NULL,NULL,NULL),
(401,'internal',3,88.00,62.60,18.80,2,1,3,0,NULL,NULL,NULL,NULL,'2025-12-30 19:20:05.257739','2025-12-30 19:20:05.257806',39,33,NULL,NULL,NULL,NULL),
(402,'internal',3,92.00,70.10,19.30,3,1,3,0,NULL,NULL,NULL,NULL,'2025-12-30 19:20:05.266159','2025-12-30 19:20:05.266184',39,56,NULL,NULL,NULL,NULL),
(403,'internal',3,92.00,70.20,19.60,3,1,3,0,NULL,NULL,NULL,NULL,'2025-12-30 19:20:05.274559','2025-12-30 19:20:05.274599',39,88,NULL,NULL,NULL,NULL),
(404,'internal',2,100.00,97.90,NULL,NULL,1,4,1,NULL,NULL,NULL,NULL,'2025-12-30 19:20:05.286980','2025-12-30 19:20:05.287005',39,59,'A',98.60,1.40,0.00),
(405,'internal',2,100.00,87.20,NULL,NULL,1,2,1,NULL,NULL,NULL,NULL,'2025-12-30 19:20:05.297996','2025-12-30 19:20:05.298020',39,164,'A',83.60,14.80,1.60),
(406,'internal',2,95.00,75.20,NULL,NULL,2,4,1,NULL,NULL,NULL,NULL,'2025-12-30 19:20:05.304212','2025-12-30 19:20:05.304237',39,35,'A',42.60,41.00,16.40),
(407,'internal',2,100.00,100.00,NULL,NULL,2,3,1,NULL,NULL,NULL,NULL,'2025-12-30 19:20:05.314069','2025-12-30 19:20:05.314092',39,130,'A',100.00,0.00,0.00),
(408,'internal',2,98.00,87.20,NULL,NULL,2,2,1,NULL,NULL,NULL,NULL,'2025-12-30 19:20:05.325243','2025-12-30 19:20:05.325277',39,164,'A',76.80,17.70,5.50),
(409,'internal',3,89.00,79.40,NULL,NULL,1,3,1,NULL,NULL,NULL,NULL,'2025-12-30 19:20:05.332968','2025-12-30 19:20:05.332994',39,114,'A',60.00,30.00,10.00),
(410,'internal',3,92.00,83.80,NULL,NULL,1,3,1,NULL,NULL,NULL,NULL,'2025-12-30 19:20:05.340015','2025-12-30 19:20:05.340041',39,115,'A',82.50,7.00,10.50),
(411,'internal',3,96.00,87.60,NULL,NULL,1,2,1,NULL,NULL,NULL,NULL,'2025-12-30 19:20:05.347286','2025-12-30 19:20:05.347313',39,170,'A',79.20,12.50,8.30),
(412,'internal',1,94.00,80.10,13.60,3,1,4,0,NULL,NULL,NULL,NULL,'2025-12-30 19:35:47.711357','2025-12-30 19:35:47.711380',43,1,NULL,NULL,NULL,NULL),
(413,'internal',1,96.00,77.60,10.60,1,1,4,0,NULL,NULL,NULL,NULL,'2025-12-30 19:35:47.719851','2025-12-30 19:35:47.719894',43,29,NULL,NULL,NULL,NULL),
(414,'internal',1,97.00,72.70,16.50,2,1,4,0,NULL,NULL,NULL,NULL,'2025-12-30 19:35:47.726810','2025-12-30 19:35:47.726842',43,53,NULL,NULL,NULL,NULL),
(415,'internal',1,95.00,75.50,13.90,2,1,3,0,NULL,NULL,NULL,NULL,'2025-12-30 19:35:47.733858','2025-12-30 19:35:47.733894',43,80,NULL,NULL,NULL,NULL),
(416,'internal',1,91.00,73.10,16.00,3,1,4,0,NULL,NULL,NULL,NULL,'2025-12-30 19:35:47.741710','2025-12-30 19:35:47.741731',43,107,NULL,NULL,NULL,NULL),
(417,'internal',1,89.00,70.30,15.40,3,1,2,0,NULL,NULL,NULL,NULL,'2025-12-30 19:35:47.750588','2025-12-30 19:35:47.750611',43,134,NULL,NULL,NULL,NULL),
(418,'internal',1,95.00,71.40,15.00,2,1,3,0,NULL,NULL,NULL,NULL,'2025-12-30 19:35:47.757253','2025-12-30 19:35:47.757274',43,132,NULL,NULL,NULL,NULL),
(419,'internal',1,89.00,70.20,14.60,1,2,4,0,NULL,NULL,NULL,NULL,'2025-12-30 19:35:47.763845','2025-12-30 19:35:47.763878',43,1,NULL,NULL,NULL,NULL),
(420,'internal',1,91.00,75.70,12.40,2,2,4,0,NULL,NULL,NULL,NULL,'2025-12-30 19:35:47.772419','2025-12-30 19:35:47.772452',43,29,NULL,NULL,NULL,NULL),
(421,'internal',1,96.00,70.90,15.80,2,2,4,0,NULL,NULL,NULL,NULL,'2025-12-30 19:35:47.780077','2025-12-30 19:35:47.780150',43,53,NULL,NULL,NULL,NULL),
(422,'internal',1,99.00,78.40,16.30,1,2,3,0,NULL,NULL,NULL,NULL,'2025-12-30 19:35:47.787378','2025-12-30 19:35:47.787405',43,80,NULL,NULL,NULL,NULL),
(423,'internal',1,97.00,75.70,15.90,2,2,4,0,NULL,NULL,NULL,NULL,'2025-12-30 19:35:47.794863','2025-12-30 19:35:47.794892',43,107,NULL,NULL,NULL,NULL),
(424,'internal',1,82.00,64.90,17.40,3,2,2,0,NULL,NULL,NULL,NULL,'2025-12-30 19:35:47.804311','2025-12-30 19:35:47.804357',43,134,NULL,NULL,NULL,NULL),
(425,'internal',1,99.00,71.10,15.20,1,2,3,0,NULL,NULL,NULL,NULL,'2025-12-30 19:35:47.811448','2025-12-30 19:35:47.811473',43,132,NULL,NULL,NULL,NULL),
(426,'internal',2,96.00,80.20,13.30,1,1,4,0,NULL,NULL,NULL,NULL,'2025-12-30 19:35:47.818150','2025-12-30 19:35:47.818182',43,3,NULL,NULL,NULL,NULL),
(427,'internal',2,94.00,68.30,18.30,1,1,4,0,NULL,NULL,NULL,NULL,'2025-12-30 19:35:47.825694','2025-12-30 19:35:47.825718',43,30,NULL,NULL,NULL,NULL),
(428,'internal',2,91.00,64.90,14.00,1,1,4,0,NULL,NULL,NULL,NULL,'2025-12-30 19:35:47.833098','2025-12-30 19:35:47.833122',43,54,NULL,NULL,NULL,NULL),
(429,'internal',2,89.00,66.50,16.80,3,1,4,0,NULL,NULL,NULL,NULL,'2025-12-30 19:35:47.840680','2025-12-30 19:35:47.840703',43,112,NULL,NULL,NULL,NULL),
(430,'internal',2,86.00,70.10,14.20,3,1,4,0,NULL,NULL,NULL,NULL,'2025-12-30 19:35:47.847276','2025-12-30 19:35:47.847311',43,109,NULL,NULL,NULL,NULL),
(431,'internal',2,81.00,73.80,13.30,4,1,4,0,NULL,NULL,NULL,NULL,'2025-12-30 19:35:47.854245','2025-12-30 19:35:47.854284',43,146,NULL,NULL,NULL,NULL),
(432,'internal',2,90.00,75.20,13.70,3,2,4,0,NULL,NULL,NULL,NULL,'2025-12-30 19:35:47.861780','2025-12-30 19:35:47.861814',43,4,NULL,NULL,NULL,NULL),
(433,'internal',2,92.00,64.90,20.50,2,2,4,0,NULL,NULL,NULL,NULL,'2025-12-30 19:35:47.870211','2025-12-30 19:35:47.870247',43,31,NULL,NULL,NULL,NULL),
(434,'internal',2,90.00,66.10,13.20,2,2,4,0,NULL,NULL,NULL,NULL,'2025-12-30 19:35:47.878354','2025-12-30 19:35:47.878386',43,55,NULL,NULL,NULL,NULL),
(435,'internal',2,94.00,60.30,18.00,1,2,4,0,NULL,NULL,NULL,NULL,'2025-12-30 19:35:47.885928','2025-12-30 19:35:47.886081',43,110,NULL,NULL,NULL,NULL),
(436,'internal',2,92.00,65.90,15.70,1,2,4,0,NULL,NULL,NULL,NULL,'2025-12-30 19:35:47.893769','2025-12-30 19:35:47.893793',43,111,NULL,NULL,NULL,NULL),
(437,'internal',3,81.00,66.60,20.30,4,1,3,0,NULL,NULL,NULL,NULL,'2025-12-30 19:35:47.900721','2025-12-30 19:35:47.900744',43,5,NULL,NULL,NULL,NULL),
(438,'internal',3,89.00,72.80,20.50,4,1,3,0,NULL,NULL,NULL,NULL,'2025-12-30 19:35:47.907649','2025-12-30 19:35:47.907671',43,32,NULL,NULL,NULL,NULL),
(439,'internal',3,88.00,62.60,18.80,2,1,3,0,NULL,NULL,NULL,NULL,'2025-12-30 19:35:47.914798','2025-12-30 19:35:47.914842',43,33,NULL,NULL,NULL,NULL),
(440,'internal',3,92.00,70.10,19.30,3,1,3,0,NULL,NULL,NULL,NULL,'2025-12-30 19:35:47.923428','2025-12-30 19:35:47.923453',43,56,NULL,NULL,NULL,NULL),
(441,'internal',3,92.00,70.20,19.60,3,1,3,0,NULL,NULL,NULL,NULL,'2025-12-30 19:35:47.930461','2025-12-30 19:35:47.930485',43,88,NULL,NULL,NULL,NULL),
(442,'internal',2,100.00,97.90,NULL,NULL,1,4,1,NULL,NULL,NULL,NULL,'2025-12-30 19:35:47.942451','2025-12-30 19:35:47.942483',43,59,'A',98.60,1.40,0.00),
(443,'internal',2,100.00,87.20,NULL,NULL,1,2,1,NULL,NULL,NULL,NULL,'2025-12-30 19:35:47.952445','2025-12-30 19:35:47.952469',43,164,'A',83.60,14.80,1.60),
(444,'internal',2,95.00,75.20,NULL,NULL,2,4,1,NULL,NULL,NULL,NULL,'2025-12-30 19:35:47.959889','2025-12-30 19:35:47.959913',43,35,'A',42.60,41.00,16.40),
(445,'internal',2,100.00,100.00,NULL,NULL,2,3,1,NULL,NULL,NULL,NULL,'2025-12-30 19:35:47.970394','2025-12-30 19:35:47.970431',43,130,'A',100.00,0.00,0.00),
(446,'internal',2,98.00,87.20,NULL,NULL,2,2,1,NULL,NULL,NULL,NULL,'2025-12-30 19:35:47.981421','2025-12-30 19:35:47.981443',43,164,'A',76.80,17.70,5.50),
(447,'internal',3,89.00,79.40,NULL,NULL,1,3,1,NULL,NULL,NULL,NULL,'2025-12-30 19:35:47.989082','2025-12-30 19:35:47.989105',43,114,'A',60.00,30.00,10.00),
(448,'internal',3,92.00,83.80,NULL,NULL,1,3,1,NULL,NULL,NULL,NULL,'2025-12-30 19:35:47.997427','2025-12-30 19:35:47.997460',43,115,'A',82.50,7.00,10.50),
(449,'internal',3,96.00,87.60,NULL,NULL,1,2,1,NULL,NULL,NULL,NULL,'2025-12-30 19:35:48.005601','2025-12-30 19:35:48.005637',43,170,'A',79.20,12.50,8.30),
(518,'internal',1,89.00,60.90,16.60,1,1,4,0,NULL,NULL,NULL,NULL,'2026-01-05 16:42:44.535255','2026-01-05 16:42:44.535305',44,1,NULL,NULL,NULL,NULL),
(519,'internal',1,55.00,60.50,19.90,6,1,4,0,NULL,NULL,NULL,NULL,'2026-01-05 16:42:44.551436','2026-01-05 16:42:44.551461',44,30,NULL,NULL,NULL,NULL),
(520,'internal',1,52.00,58.90,23.70,5,1,4,0,NULL,NULL,NULL,NULL,'2026-01-05 16:42:44.559802','2026-01-05 16:42:44.559825',44,53,NULL,NULL,NULL,NULL),
(521,'internal',1,78.00,58.60,17.10,3,1,3,0,NULL,NULL,NULL,NULL,'2026-01-05 16:42:44.568666','2026-01-05 16:42:44.568701',44,132,NULL,NULL,NULL,NULL),
(522,'internal',1,89.00,68.50,18.20,3,1,3,0,NULL,NULL,NULL,NULL,'2026-01-05 16:42:44.577425','2026-01-05 16:42:44.577448',44,80,NULL,NULL,NULL,NULL),
(523,'internal',1,98.00,68.20,17.90,1,1,3,0,NULL,NULL,NULL,NULL,'2026-01-05 16:42:44.583714','2026-01-05 16:42:44.583737',44,107,NULL,NULL,NULL,NULL),
(524,'internal',1,81.00,61.80,17.70,3,1,2,0,NULL,NULL,NULL,NULL,'2026-01-05 16:42:44.590902','2026-01-05 16:42:44.590927',44,133,NULL,NULL,NULL,NULL),
(525,'internal',1,93.00,64.00,19.90,2,2,4,0,NULL,NULL,NULL,NULL,'2026-01-05 16:42:44.598061','2026-01-05 16:42:44.598093',44,1,NULL,NULL,NULL,NULL),
(526,'internal',1,57.00,60.40,19.80,6,2,4,0,NULL,NULL,NULL,NULL,'2026-01-05 16:42:44.609925','2026-01-05 16:42:44.609949',44,30,NULL,NULL,NULL,NULL),
(527,'internal',1,57.00,59.40,24.70,5,2,4,0,NULL,NULL,NULL,NULL,'2026-01-05 16:42:44.616327','2026-01-05 16:42:44.616352',44,53,NULL,NULL,NULL,NULL),
(528,'internal',1,88.00,61.20,18.40,2,2,3,0,NULL,NULL,NULL,NULL,'2026-01-05 16:42:44.622894','2026-01-05 16:42:44.622920',44,132,NULL,NULL,NULL,NULL),
(529,'internal',1,90.00,62.80,19.10,2,2,3,0,NULL,NULL,NULL,NULL,'2026-01-05 16:42:44.629346','2026-01-05 16:42:44.629371',44,80,NULL,NULL,NULL,NULL),
(530,'internal',1,93.00,69.80,16.30,2,2,3,0,NULL,NULL,NULL,NULL,'2026-01-05 16:42:44.637168','2026-01-05 16:42:44.637190',44,107,NULL,NULL,NULL,NULL),
(531,'internal',1,92.00,63.30,19.90,2,2,2,0,NULL,NULL,NULL,NULL,'2026-01-05 16:42:44.643238','2026-01-05 16:42:44.643263',44,133,NULL,NULL,NULL,NULL),
(532,'internal',2,92.00,61.80,19.80,1,1,4,0,NULL,NULL,NULL,NULL,'2026-01-05 16:42:44.650458','2026-01-05 16:42:44.650482',44,3,NULL,NULL,NULL,NULL),
(533,'internal',2,72.00,57.30,21.50,4,1,4,0,NULL,NULL,NULL,NULL,'2026-01-05 16:42:44.657723','2026-01-05 16:42:44.657748',44,30,NULL,NULL,NULL,NULL),
(534,'internal',2,57.00,63.90,23.60,5,1,4,0,NULL,NULL,NULL,NULL,'2026-01-05 16:42:44.664453','2026-01-05 16:42:44.664496',44,54,NULL,NULL,NULL,NULL),
(535,'internal',2,91.00,64.70,23.30,3,1,3,0,NULL,NULL,NULL,NULL,'2026-01-05 16:42:44.677558','2026-01-05 16:42:44.677580',44,87,NULL,NULL,NULL,NULL),
(536,'internal',2,88.00,57.40,23.00,3,1,3,0,NULL,NULL,NULL,NULL,'2026-01-05 16:42:44.686118','2026-01-05 16:42:44.686143',44,109,NULL,NULL,NULL,NULL),
(537,'internal',2,82.00,60.30,20.80,3,1,3,0,NULL,NULL,NULL,NULL,'2026-01-05 16:42:44.691904','2026-01-05 16:42:44.691945',44,110,NULL,NULL,NULL,NULL),
(538,'internal',2,93.00,60.80,22.40,2,1,3,0,NULL,NULL,NULL,NULL,'2026-01-05 16:42:44.699969','2026-01-05 16:42:44.699995',44,111,NULL,NULL,NULL,NULL),
(539,'internal',2,92.00,67.50,20.90,3,1,2,0,NULL,NULL,NULL,NULL,'2026-01-05 16:42:44.706881','2026-01-05 16:42:44.706903',44,148,NULL,NULL,NULL,NULL),
(540,'internal',2,80.00,60.60,21.30,3,2,4,0,NULL,NULL,NULL,NULL,'2026-01-05 16:42:44.713978','2026-01-05 16:42:44.714073',44,4,NULL,NULL,NULL,NULL),
(541,'internal',2,65.00,57.90,22.30,5,2,4,0,NULL,NULL,NULL,NULL,'2026-01-05 16:42:44.721350','2026-01-05 16:42:44.721372',44,31,NULL,NULL,NULL,NULL),
(542,'internal',2,76.00,65.60,22.30,5,2,4,0,NULL,NULL,NULL,NULL,'2026-01-05 16:42:44.728270','2026-01-05 16:42:44.728306',44,55,NULL,NULL,NULL,NULL),
(543,'internal',2,79.00,62.90,18.30,3,2,3,0,NULL,NULL,NULL,NULL,'2026-01-05 16:42:44.738869','2026-01-05 16:42:44.738893',44,87,NULL,NULL,NULL,NULL),
(544,'internal',2,76.00,56.40,22.70,4,2,3,0,NULL,NULL,NULL,NULL,'2026-01-05 16:42:44.746527','2026-01-05 16:42:44.746583',44,109,NULL,NULL,NULL,NULL),
(545,'internal',2,87.00,60.50,23.60,3,2,3,0,NULL,NULL,NULL,NULL,'2026-01-05 16:42:44.754589','2026-01-05 16:42:44.754611',44,110,NULL,NULL,NULL,NULL),
(546,'internal',2,89.00,60.70,21.90,2,2,3,0,NULL,NULL,NULL,NULL,'2026-01-05 16:42:44.761406','2026-01-05 16:42:44.761430',44,111,NULL,NULL,NULL,NULL),
(547,'internal',2,98.00,64.60,21.80,1,2,2,0,NULL,NULL,NULL,NULL,'2026-01-05 16:42:44.768361','2026-01-05 16:42:44.768387',44,148,NULL,NULL,NULL,NULL),
(548,'internal',1,80.00,68.50,16.10,4,1,4,0,NULL,NULL,NULL,NULL,'2026-01-05 22:35:24.570600','2026-01-05 22:35:24.570630',48,1,NULL,NULL,NULL,NULL),
(549,'internal',1,78.00,70.90,18.80,5,1,4,0,NULL,NULL,NULL,NULL,'2026-01-05 22:35:24.597870','2026-01-05 22:35:24.597894',48,30,NULL,NULL,NULL,NULL),
(550,'internal',1,79.00,69.50,20.40,5,1,3,0,NULL,NULL,NULL,NULL,'2026-01-05 22:35:24.607814','2026-01-05 22:35:24.607840',48,53,NULL,NULL,NULL,NULL),
(551,'internal',1,79.00,56.20,21.40,3,1,3,0,NULL,NULL,NULL,NULL,'2026-01-05 22:35:24.614669','2026-01-05 22:35:24.614695',48,132,NULL,NULL,NULL,NULL),
(552,'internal',1,88.00,68.00,18.90,3,1,3,0,NULL,NULL,NULL,NULL,'2026-01-05 22:35:24.625256','2026-01-05 22:35:24.625283',48,80,NULL,NULL,NULL,NULL),
(553,'internal',1,78.00,69.30,18.00,4,1,4,0,NULL,NULL,NULL,NULL,'2026-01-05 22:35:24.632762','2026-01-05 22:35:24.632789',48,107,NULL,NULL,NULL,NULL),
(554,'internal',1,81.00,74.00,12.90,4,1,2,0,NULL,NULL,NULL,NULL,'2026-01-05 22:35:24.642650','2026-01-05 22:35:24.642678',48,133,NULL,NULL,NULL,NULL),
(555,'internal',1,83.00,60.90,19.00,3,2,3,0,NULL,NULL,NULL,NULL,'2026-01-05 22:35:24.650904','2026-01-05 22:35:24.650937',48,1,NULL,NULL,NULL,NULL),
(556,'internal',1,72.00,65.00,19.30,5,2,4,0,NULL,NULL,NULL,NULL,'2026-01-05 22:35:24.663737','2026-01-05 22:35:24.663761',48,30,NULL,NULL,NULL,NULL),
(557,'internal',1,74.00,64.90,21.10,5,2,4,0,NULL,NULL,NULL,NULL,'2026-01-05 22:35:24.671170','2026-01-05 22:35:24.671202',48,53,NULL,NULL,NULL,NULL),
(558,'internal',1,83.00,64.10,19.90,4,2,3,0,NULL,NULL,NULL,NULL,'2026-01-05 22:35:24.679071','2026-01-05 22:35:24.679097',48,132,NULL,NULL,NULL,NULL),
(559,'internal',1,78.00,63.30,19.80,4,2,3,0,NULL,NULL,NULL,NULL,'2026-01-05 22:35:24.686867','2026-01-05 22:35:24.686892',48,80,NULL,NULL,NULL,NULL),
(560,'internal',1,89.00,66.20,19.60,3,2,4,0,NULL,NULL,NULL,NULL,'2026-01-05 22:35:24.695096','2026-01-05 22:35:24.695120',48,107,NULL,NULL,NULL,NULL),
(561,'internal',1,84.00,73.60,14.80,4,2,2,0,NULL,NULL,NULL,NULL,'2026-01-05 22:35:24.702081','2026-01-05 22:35:24.702107',48,133,NULL,NULL,NULL,NULL),
(562,'internal',2,84.00,68.00,18.10,3,1,4,0,NULL,NULL,NULL,NULL,'2026-01-05 22:35:24.709331','2026-01-05 22:35:24.709369',48,3,NULL,NULL,NULL,NULL),
(563,'internal',2,53.00,56.50,21.40,5,1,4,0,NULL,NULL,NULL,NULL,'2026-01-05 22:35:24.716529','2026-01-05 22:35:24.716554',48,30,NULL,NULL,NULL,NULL),
(564,'internal',2,84.00,65.50,23.60,4,1,4,0,NULL,NULL,NULL,NULL,'2026-01-05 22:35:24.723599','2026-01-05 22:35:24.723624',48,54,NULL,NULL,NULL,NULL),
(565,'internal',2,58.00,59.20,16.60,5,1,3,0,NULL,NULL,NULL,NULL,'2026-01-05 22:35:24.730372','2026-01-05 22:35:24.730400',48,109,NULL,NULL,NULL,NULL),
(566,'internal',2,73.00,68.20,17.60,5,1,2,0,NULL,NULL,NULL,NULL,'2026-01-05 22:35:24.737457','2026-01-05 22:35:24.737487',48,110,NULL,NULL,NULL,NULL),
(567,'internal',2,85.00,64.00,18.70,3,1,3,0,NULL,NULL,NULL,NULL,'2026-01-05 22:35:24.746366','2026-01-05 22:35:24.746397',48,111,NULL,NULL,NULL,NULL),
(568,'internal',2,78.00,59.50,18.90,3,1,2,0,NULL,NULL,NULL,NULL,'2026-01-05 22:35:24.752359','2026-01-05 22:35:24.752389',48,112,NULL,NULL,NULL,NULL),
(569,'internal',2,70.00,67.50,19.00,5,1,2,0,NULL,NULL,NULL,NULL,'2026-01-05 22:35:24.760807','2026-01-05 22:35:24.760835',48,134,NULL,NULL,NULL,NULL),
(570,'internal',2,65.00,64.80,18.30,5,1,2,0,NULL,NULL,NULL,NULL,'2026-01-05 22:35:24.768380','2026-01-05 22:35:24.768523',48,148,NULL,NULL,NULL,NULL),
(571,'internal',2,85.00,66.40,22.50,4,2,4,0,NULL,NULL,NULL,NULL,'2026-01-05 22:35:24.776171','2026-01-05 22:35:24.776196',48,4,NULL,NULL,NULL,NULL),
(572,'internal',2,65.00,56.70,21.90,5,2,4,0,NULL,NULL,NULL,NULL,'2026-01-05 22:35:24.782617','2026-01-05 22:35:24.782649',48,31,NULL,NULL,NULL,NULL),
(573,'internal',2,80.00,61.50,24.60,4,2,4,0,NULL,NULL,NULL,NULL,'2026-01-05 22:35:24.790636','2026-01-05 22:35:24.790664',48,55,NULL,NULL,NULL,NULL),
(574,'internal',2,58.00,62.70,15.00,5,2,2,0,NULL,NULL,NULL,NULL,'2026-01-05 22:35:24.796883','2026-01-05 22:35:24.796908',48,109,NULL,NULL,NULL,NULL),
(575,'internal',2,83.00,65.90,20.30,4,2,3,0,NULL,NULL,NULL,NULL,'2026-01-05 22:35:24.803893','2026-01-05 22:35:24.803919',48,110,NULL,NULL,NULL,NULL),
(576,'internal',2,79.00,55.80,18.10,3,2,2,0,NULL,NULL,NULL,NULL,'2026-01-05 22:35:24.810979','2026-01-05 22:35:24.811005',48,111,NULL,NULL,NULL,NULL),
(577,'internal',2,89.00,59.60,20.70,2,2,3,0,NULL,NULL,NULL,NULL,'2026-01-05 22:35:24.816609','2026-01-05 22:35:24.816636',48,112,NULL,NULL,NULL,NULL),
(578,'internal',2,88.00,67.80,21.60,3,2,2,0,NULL,NULL,NULL,NULL,'2026-01-05 22:35:24.823631','2026-01-05 22:35:24.823657',48,134,NULL,NULL,NULL,NULL),
(579,'internal',2,54.00,53.80,21.60,5,2,2,0,NULL,NULL,NULL,NULL,'2026-01-05 22:35:24.829288','2026-01-05 22:35:24.829313',48,148,NULL,NULL,NULL,NULL),
(580,'internal',2,95.00,88.30,NULL,NULL,1,1,1,NULL,NULL,NULL,NULL,'2026-01-05 22:35:24.841358','2026-01-05 22:35:24.841385',48,169,'A',87.00,9.90,3.10),
(581,'internal',2,81.00,85.00,NULL,NULL,2,1,1,NULL,NULL,NULL,NULL,'2026-01-05 22:35:24.850658','2026-01-05 22:35:24.850684',48,169,'A',77.10,16.80,6.10),
(604,'internal',1,56.00,63.40,17.20,6,1,4,0,NULL,NULL,NULL,NULL,'2026-01-09 22:31:03.717027','2026-01-09 22:31:03.717049',67,1,NULL,NULL,NULL,NULL),
(605,'internal',1,72.00,68.10,16.70,5,1,4,0,NULL,NULL,NULL,NULL,'2026-01-09 22:31:03.729751','2026-01-09 22:31:03.729778',67,30,NULL,NULL,NULL,NULL),
(606,'internal',1,45.00,62.40,21.80,6,1,4,0,NULL,NULL,NULL,NULL,'2026-01-09 22:31:03.736657','2026-01-09 22:31:03.736689',67,53,NULL,NULL,NULL,NULL),
(607,'internal',1,32.00,61.50,19.40,8,1,3,0,NULL,NULL,NULL,NULL,'2026-01-09 22:31:03.744130','2026-01-09 22:31:03.744152',67,107,NULL,NULL,NULL,NULL),
(608,'internal',1,71.00,71.40,16.40,5,1,4,0,NULL,NULL,NULL,NULL,'2026-01-09 22:31:03.748364','2026-01-09 22:31:03.748387',67,80,NULL,NULL,NULL,NULL),
(609,'internal',1,52.00,69.70,16.00,7,1,3,0,NULL,NULL,NULL,NULL,'2026-01-09 22:31:03.755297','2026-01-09 22:31:03.755323',67,132,NULL,NULL,NULL,NULL),
(610,'internal',1,50.00,61.80,20.10,6,2,4,0,NULL,NULL,NULL,NULL,'2026-01-09 22:31:03.762459','2026-01-09 22:31:03.762483',67,1,NULL,NULL,NULL,NULL),
(611,'internal',1,73.00,65.70,16.20,4,2,4,0,NULL,NULL,NULL,NULL,'2026-01-09 22:31:03.774361','2026-01-09 22:31:03.774389',67,30,NULL,NULL,NULL,NULL),
(612,'internal',1,64.00,65.30,20.90,5,2,4,0,NULL,NULL,NULL,NULL,'2026-01-09 22:31:03.782430','2026-01-09 22:31:03.782452',67,53,NULL,NULL,NULL,NULL),
(613,'internal',1,52.00,68.30,18.10,7,2,3,0,NULL,NULL,NULL,NULL,'2026-01-09 22:31:03.790321','2026-01-09 22:31:03.790344',67,107,NULL,NULL,NULL,NULL),
(614,'internal',1,57.00,70.20,15.20,7,2,4,0,NULL,NULL,NULL,NULL,'2026-01-09 22:31:03.797402','2026-01-09 22:31:03.797427',67,80,NULL,NULL,NULL,NULL),
(615,'internal',1,64.00,70.10,16.50,6,2,3,0,NULL,NULL,NULL,NULL,'2026-01-09 22:31:03.804443','2026-01-09 22:31:03.804543',67,132,NULL,NULL,NULL,NULL),
(616,'internal',2,62.00,66.70,19.50,6,1,4,0,NULL,NULL,NULL,NULL,'2026-01-09 22:31:03.811727','2026-01-09 22:31:03.811752',67,3,NULL,NULL,NULL,NULL),
(617,'internal',2,58.00,55.90,19.40,5,1,4,0,NULL,NULL,NULL,NULL,'2026-01-09 22:31:03.819541','2026-01-09 22:31:03.819564',67,30,NULL,NULL,NULL,NULL),
(618,'internal',2,73.00,59.50,23.50,4,1,4,0,NULL,NULL,NULL,NULL,'2026-01-09 22:31:03.826719','2026-01-09 22:31:03.826843',67,54,NULL,NULL,NULL,NULL),
(619,'internal',2,53.00,67.60,17.30,6,1,3,0,NULL,NULL,NULL,NULL,'2026-01-09 22:31:03.834467','2026-01-09 22:31:03.834489',67,81,NULL,NULL,NULL,NULL),
(620,'internal',2,71.00,64.70,21.80,5,1,3,0,NULL,NULL,NULL,NULL,'2026-01-09 22:31:03.842019','2026-01-09 22:31:03.842043',67,111,NULL,NULL,NULL,NULL),
(621,'internal',2,50.00,57.70,19.50,5,1,3,0,NULL,NULL,NULL,NULL,'2026-01-09 22:31:03.849591','2026-01-09 22:31:03.849613',67,112,NULL,NULL,NULL,NULL),
(622,'internal',2,67.00,74.20,15.90,6,1,2,0,NULL,NULL,NULL,NULL,'2026-01-09 22:31:03.856860','2026-01-09 22:31:03.856884',67,148,NULL,NULL,NULL,NULL),
(623,'internal',2,67.00,67.40,19.60,5,2,4,0,NULL,NULL,NULL,NULL,'2026-01-09 22:31:03.863360','2026-01-09 22:31:03.863383',67,4,NULL,NULL,NULL,NULL),
(624,'internal',2,69.00,51.60,23.20,4,2,4,0,NULL,NULL,NULL,NULL,'2026-01-09 22:31:03.871311','2026-01-09 22:31:03.871338',67,31,NULL,NULL,NULL,NULL),
(625,'internal',2,70.00,54.60,23.90,4,2,4,0,NULL,NULL,NULL,NULL,'2026-01-09 22:31:03.878363','2026-01-09 22:31:03.878387',67,55,NULL,NULL,NULL,NULL),
(626,'internal',2,45.00,58.40,21.00,6,2,3,0,NULL,NULL,NULL,NULL,'2026-01-09 22:31:03.885191','2026-01-09 22:31:03.885226',67,81,NULL,NULL,NULL,NULL),
(627,'internal',2,58.00,60.00,23.30,5,2,3,0,NULL,NULL,NULL,NULL,'2026-01-09 22:31:03.893045','2026-01-09 22:31:03.893069',67,111,NULL,NULL,NULL,NULL),
(628,'internal',2,38.00,53.10,20.10,6,2,3,0,NULL,NULL,NULL,NULL,'2026-01-09 22:31:03.899764','2026-01-09 22:31:03.899807',67,112,NULL,NULL,NULL,NULL),
(629,'internal',2,56.00,64.50,21.50,5,2,2,0,NULL,NULL,NULL,NULL,'2026-01-09 22:31:03.907205','2026-01-09 22:31:03.907233',67,148,NULL,NULL,NULL,NULL),
(630,'internal',1,56.00,63.40,17.20,6,1,4,0,NULL,NULL,NULL,NULL,'2026-01-15 22:27:45.532666','2026-01-15 22:27:45.532694',105,1,NULL,NULL,NULL,NULL),
(631,'internal',1,72.00,68.10,16.70,5,1,4,0,NULL,NULL,NULL,NULL,'2026-01-15 22:27:45.557506','2026-01-15 22:27:45.557533',105,30,NULL,NULL,NULL,NULL),
(632,'internal',1,45.00,62.40,21.80,6,1,4,0,NULL,NULL,NULL,NULL,'2026-01-15 22:27:45.566982','2026-01-15 22:27:45.567009',105,53,NULL,NULL,NULL,NULL),
(633,'internal',1,32.00,61.50,19.40,8,1,3,0,NULL,NULL,NULL,NULL,'2026-01-15 22:27:45.574627','2026-01-15 22:27:45.574651',105,107,NULL,NULL,NULL,NULL),
(634,'internal',1,71.00,71.40,16.40,5,1,4,0,NULL,NULL,NULL,NULL,'2026-01-15 22:27:45.584742','2026-01-15 22:27:45.584768',105,80,NULL,NULL,NULL,NULL),
(635,'internal',1,52.00,69.70,16.00,7,1,3,0,NULL,NULL,NULL,NULL,'2026-01-15 22:27:45.594461','2026-01-15 22:27:45.594506',105,132,NULL,NULL,NULL,NULL),
(636,'internal',1,50.00,61.80,20.10,6,2,4,0,NULL,NULL,NULL,NULL,'2026-01-15 22:27:45.608991','2026-01-15 22:27:45.609093',105,1,NULL,NULL,NULL,NULL),
(637,'internal',1,73.00,65.70,16.20,4,2,4,0,NULL,NULL,NULL,NULL,'2026-01-15 22:27:45.631413','2026-01-15 22:27:45.631443',105,30,NULL,NULL,NULL,NULL),
(638,'internal',1,64.00,65.30,20.90,5,2,4,0,NULL,NULL,NULL,NULL,'2026-01-15 22:27:45.642908','2026-01-15 22:27:45.642958',105,53,NULL,NULL,NULL,NULL),
(639,'internal',1,52.00,68.30,18.10,7,2,3,0,NULL,NULL,NULL,NULL,'2026-01-15 22:27:45.654671','2026-01-15 22:27:45.654711',105,107,NULL,NULL,NULL,NULL),
(640,'internal',1,57.00,70.20,15.20,7,2,4,0,NULL,NULL,NULL,NULL,'2026-01-15 22:27:45.666227','2026-01-15 22:27:45.666265',105,80,NULL,NULL,NULL,NULL),
(641,'internal',1,64.00,70.10,16.50,6,2,3,0,NULL,NULL,NULL,NULL,'2026-01-15 22:27:45.680360','2026-01-15 22:27:45.680401',105,132,NULL,NULL,NULL,NULL),
(642,'internal',2,62.00,66.70,19.50,6,1,4,0,NULL,NULL,NULL,NULL,'2026-01-15 22:27:45.692818','2026-01-15 22:27:45.692874',105,3,NULL,NULL,NULL,NULL),
(643,'internal',2,58.00,55.90,19.40,5,1,4,0,NULL,NULL,NULL,NULL,'2026-01-15 22:27:45.706001','2026-01-15 22:27:45.706081',105,30,NULL,NULL,NULL,NULL),
(644,'internal',2,73.00,59.50,23.50,4,1,4,0,NULL,NULL,NULL,NULL,'2026-01-15 22:27:45.725034','2026-01-15 22:27:45.725085',105,54,NULL,NULL,NULL,NULL),
(645,'internal',2,53.00,67.60,17.30,6,1,3,0,NULL,NULL,NULL,NULL,'2026-01-15 22:27:45.737252','2026-01-15 22:27:45.737292',105,81,NULL,NULL,NULL,NULL),
(646,'internal',2,71.00,64.70,21.80,5,1,3,0,NULL,NULL,NULL,NULL,'2026-01-15 22:27:45.753261','2026-01-15 22:27:45.753308',105,111,NULL,NULL,NULL,NULL),
(647,'internal',2,50.00,57.70,19.50,5,1,3,0,NULL,NULL,NULL,NULL,'2026-01-15 22:27:45.765622','2026-01-15 22:27:45.765658',105,112,NULL,NULL,NULL,NULL),
(648,'internal',2,67.00,74.20,15.90,6,1,2,0,NULL,NULL,NULL,NULL,'2026-01-15 22:27:45.780737','2026-01-15 22:27:45.780790',105,148,NULL,NULL,NULL,NULL),
(649,'internal',2,67.00,67.40,19.60,5,2,4,0,NULL,NULL,NULL,NULL,'2026-01-15 22:27:45.792155','2026-01-15 22:27:45.792375',105,4,NULL,NULL,NULL,NULL),
(650,'internal',2,69.00,51.60,23.20,4,2,4,0,NULL,NULL,NULL,NULL,'2026-01-15 22:27:45.803069','2026-01-15 22:27:45.803113',105,31,NULL,NULL,NULL,NULL),
(651,'internal',2,70.00,54.60,23.90,4,2,4,0,NULL,NULL,NULL,NULL,'2026-01-15 22:27:45.813566','2026-01-15 22:27:45.813595',105,55,NULL,NULL,NULL,NULL),
(652,'internal',2,45.00,58.40,21.00,6,2,3,0,NULL,NULL,NULL,NULL,'2026-01-15 22:27:45.823320','2026-01-15 22:27:45.823350',105,81,NULL,NULL,NULL,NULL),
(653,'internal',2,58.00,60.00,23.30,5,2,3,0,NULL,NULL,NULL,NULL,'2026-01-15 22:27:45.832470','2026-01-15 22:27:45.832504',105,111,NULL,NULL,NULL,NULL),
(654,'internal',2,38.00,53.10,20.10,6,2,3,0,NULL,NULL,NULL,NULL,'2026-01-15 22:27:45.844420','2026-01-15 22:27:45.844464',105,112,NULL,NULL,NULL,NULL),
(655,'internal',2,56.00,64.50,21.50,5,2,2,0,NULL,NULL,NULL,NULL,'2026-01-15 22:27:45.853906','2026-01-15 22:27:45.853945',105,148,NULL,NULL,NULL,NULL),
(656,'internal',1,89.00,60.90,16.60,1,1,4,0,NULL,NULL,NULL,NULL,'2026-01-15 22:35:32.183035','2026-01-15 22:35:32.183070',106,1,NULL,NULL,NULL,NULL),
(657,'internal',1,55.00,60.50,19.90,6,1,4,0,NULL,NULL,NULL,NULL,'2026-01-15 22:35:32.200424','2026-01-15 22:35:32.200451',106,30,NULL,NULL,NULL,NULL),
(658,'internal',1,52.00,58.90,23.70,5,1,4,0,NULL,NULL,NULL,NULL,'2026-01-15 22:35:32.211317','2026-01-15 22:35:32.211360',106,53,NULL,NULL,NULL,NULL),
(659,'internal',1,78.00,58.60,17.10,3,1,3,0,NULL,NULL,NULL,NULL,'2026-01-15 22:35:32.221646','2026-01-15 22:35:32.221672',106,132,NULL,NULL,NULL,NULL),
(660,'internal',1,89.00,68.50,18.20,3,1,3,0,NULL,NULL,NULL,NULL,'2026-01-15 22:35:32.228413','2026-01-15 22:35:32.228435',106,80,NULL,NULL,NULL,NULL),
(661,'internal',1,98.00,68.20,17.90,1,1,3,0,NULL,NULL,NULL,NULL,'2026-01-15 22:35:32.236919','2026-01-15 22:35:32.236950',106,107,NULL,NULL,NULL,NULL),
(662,'internal',1,81.00,61.80,17.70,3,1,2,0,NULL,NULL,NULL,NULL,'2026-01-15 22:35:32.245904','2026-01-15 22:35:32.245972',106,133,NULL,NULL,NULL,NULL),
(663,'internal',1,93.00,64.00,19.90,2,2,4,0,NULL,NULL,NULL,NULL,'2026-01-15 22:35:32.255970','2026-01-15 22:35:32.255996',106,1,NULL,NULL,NULL,NULL),
(664,'internal',1,57.00,60.40,19.80,6,2,4,0,NULL,NULL,NULL,NULL,'2026-01-15 22:35:32.271593','2026-01-15 22:35:32.271635',106,30,NULL,NULL,NULL,NULL),
(665,'internal',1,57.00,59.40,24.70,5,2,4,0,NULL,NULL,NULL,NULL,'2026-01-15 22:35:32.279148','2026-01-15 22:35:32.279177',106,53,NULL,NULL,NULL,NULL),
(666,'internal',1,88.00,61.20,18.40,2,2,3,0,NULL,NULL,NULL,NULL,'2026-01-15 22:35:32.287564','2026-01-15 22:35:32.287589',106,132,NULL,NULL,NULL,NULL),
(667,'internal',1,90.00,62.80,19.10,2,2,3,0,NULL,NULL,NULL,NULL,'2026-01-15 22:35:32.295428','2026-01-15 22:35:32.295464',106,80,NULL,NULL,NULL,NULL),
(668,'internal',1,93.00,69.80,16.30,2,2,3,0,NULL,NULL,NULL,NULL,'2026-01-15 22:35:32.303585','2026-01-15 22:35:32.303609',106,107,NULL,NULL,NULL,NULL),
(669,'internal',1,92.00,63.30,19.90,2,2,2,0,NULL,NULL,NULL,NULL,'2026-01-15 22:35:32.310628','2026-01-15 22:35:32.310652',106,133,NULL,NULL,NULL,NULL),
(670,'internal',2,92.00,61.80,19.80,1,1,4,0,NULL,NULL,NULL,NULL,'2026-01-15 22:35:32.319561','2026-01-15 22:35:32.319587',106,3,NULL,NULL,NULL,NULL),
(671,'internal',2,72.00,57.30,21.50,4,1,4,0,NULL,NULL,NULL,NULL,'2026-01-15 22:35:32.326619','2026-01-15 22:35:32.326647',106,30,NULL,NULL,NULL,NULL),
(672,'internal',2,57.00,63.90,23.60,5,1,4,0,NULL,NULL,NULL,NULL,'2026-01-15 22:35:32.334564','2026-01-15 22:35:32.334607',106,54,NULL,NULL,NULL,NULL),
(673,'internal',2,91.00,64.70,23.30,3,1,3,0,NULL,NULL,NULL,NULL,'2026-01-15 22:35:32.346114','2026-01-15 22:35:32.346139',106,87,NULL,NULL,NULL,NULL),
(674,'internal',2,88.00,57.40,23.00,3,1,3,0,NULL,NULL,NULL,NULL,'2026-01-15 22:35:32.355444','2026-01-15 22:35:32.355469',106,109,NULL,NULL,NULL,NULL),
(675,'internal',2,82.00,60.30,20.80,3,1,3,0,NULL,NULL,NULL,NULL,'2026-01-15 22:35:32.363380','2026-01-15 22:35:32.363413',106,110,NULL,NULL,NULL,NULL),
(676,'internal',2,93.00,60.80,22.40,2,1,3,0,NULL,NULL,NULL,NULL,'2026-01-15 22:35:32.372093','2026-01-15 22:35:32.372129',106,111,NULL,NULL,NULL,NULL),
(677,'internal',2,92.00,67.50,20.90,3,1,2,0,NULL,NULL,NULL,NULL,'2026-01-15 22:35:32.409781','2026-01-15 22:35:32.409813',106,148,NULL,NULL,NULL,NULL),
(678,'internal',2,80.00,60.60,21.30,3,2,4,0,NULL,NULL,NULL,NULL,'2026-01-15 22:35:32.424013','2026-01-15 22:35:32.424041',106,4,NULL,NULL,NULL,NULL),
(679,'internal',2,65.00,57.90,22.30,5,2,4,0,NULL,NULL,NULL,NULL,'2026-01-15 22:35:32.433619','2026-01-15 22:35:32.433649',106,31,NULL,NULL,NULL,NULL),
(680,'internal',2,76.00,65.60,22.30,5,2,4,0,NULL,NULL,NULL,NULL,'2026-01-15 22:35:32.442556','2026-01-15 22:35:32.442584',106,55,NULL,NULL,NULL,NULL),
(681,'internal',2,79.00,62.90,18.30,3,2,3,0,NULL,NULL,NULL,NULL,'2026-01-15 22:35:32.455666','2026-01-15 22:35:32.455693',106,87,NULL,NULL,NULL,NULL),
(682,'internal',2,76.00,56.40,22.70,4,2,3,0,NULL,NULL,NULL,NULL,'2026-01-15 22:35:32.464412','2026-01-15 22:35:32.464463',106,109,NULL,NULL,NULL,NULL),
(683,'internal',2,87.00,60.50,23.60,3,2,3,0,NULL,NULL,NULL,NULL,'2026-01-15 22:35:32.473742','2026-01-15 22:35:32.473768',106,110,NULL,NULL,NULL,NULL),
(684,'internal',2,89.00,60.70,21.90,2,2,3,0,NULL,NULL,NULL,NULL,'2026-01-15 22:35:32.484525','2026-01-15 22:35:32.484573',106,111,NULL,NULL,NULL,NULL),
(685,'internal',2,98.00,64.60,21.80,1,2,2,0,NULL,NULL,NULL,NULL,'2026-01-15 22:35:32.492682','2026-01-15 22:35:32.492709',106,148,NULL,NULL,NULL,NULL),
(686,'internal',1,80.00,68.50,16.10,4,1,4,0,NULL,NULL,NULL,NULL,'2026-01-15 22:36:59.130893','2026-01-15 22:36:59.130921',109,1,NULL,NULL,NULL,NULL),
(687,'internal',1,78.00,70.90,18.80,5,1,4,0,NULL,NULL,NULL,NULL,'2026-01-15 22:36:59.147809','2026-01-15 22:36:59.147847',109,30,NULL,NULL,NULL,NULL),
(688,'internal',1,79.00,69.50,20.40,5,1,3,0,NULL,NULL,NULL,NULL,'2026-01-15 22:36:59.157836','2026-01-15 22:36:59.157862',109,53,NULL,NULL,NULL,NULL),
(689,'internal',1,79.00,56.20,21.40,3,1,3,0,NULL,NULL,NULL,NULL,'2026-01-15 22:36:59.167006','2026-01-15 22:36:59.167038',109,132,NULL,NULL,NULL,NULL),
(690,'internal',1,88.00,68.00,18.90,3,1,3,0,NULL,NULL,NULL,NULL,'2026-01-15 22:36:59.177618','2026-01-15 22:36:59.177648',109,80,NULL,NULL,NULL,NULL),
(691,'internal',1,78.00,69.30,18.00,4,1,4,0,NULL,NULL,NULL,NULL,'2026-01-15 22:36:59.188475','2026-01-15 22:36:59.188541',109,107,NULL,NULL,NULL,NULL),
(692,'internal',1,81.00,74.00,12.90,4,1,2,0,NULL,NULL,NULL,NULL,'2026-01-15 22:36:59.197614','2026-01-15 22:36:59.197639',109,133,NULL,NULL,NULL,NULL),
(693,'internal',1,83.00,60.90,19.00,3,2,3,0,NULL,NULL,NULL,NULL,'2026-01-15 22:36:59.206520','2026-01-15 22:36:59.206545',109,1,NULL,NULL,NULL,NULL),
(694,'internal',1,72.00,65.00,19.30,5,2,4,0,NULL,NULL,NULL,NULL,'2026-01-15 22:36:59.218894','2026-01-15 22:36:59.218917',109,30,NULL,NULL,NULL,NULL),
(695,'internal',1,74.00,64.90,21.10,5,2,4,0,NULL,NULL,NULL,NULL,'2026-01-15 22:36:59.226641','2026-01-15 22:36:59.226664',109,53,NULL,NULL,NULL,NULL),
(696,'internal',1,83.00,64.10,19.90,4,2,3,0,NULL,NULL,NULL,NULL,'2026-01-15 22:36:59.233798','2026-01-15 22:36:59.233821',109,132,NULL,NULL,NULL,NULL),
(697,'internal',1,78.00,63.30,19.80,4,2,3,0,NULL,NULL,NULL,NULL,'2026-01-15 22:36:59.241606','2026-01-15 22:36:59.241632',109,80,NULL,NULL,NULL,NULL),
(698,'internal',1,89.00,66.20,19.60,3,2,4,0,NULL,NULL,NULL,NULL,'2026-01-15 22:36:59.249669','2026-01-15 22:36:59.249693',109,107,NULL,NULL,NULL,NULL),
(699,'internal',1,84.00,73.60,14.80,4,2,2,0,NULL,NULL,NULL,NULL,'2026-01-15 22:36:59.258267','2026-01-15 22:36:59.258290',109,133,NULL,NULL,NULL,NULL),
(700,'internal',2,84.00,68.00,18.10,3,1,4,0,NULL,NULL,NULL,NULL,'2026-01-15 22:36:59.265397','2026-01-15 22:36:59.265421',109,3,NULL,NULL,NULL,NULL),
(701,'internal',2,53.00,56.50,21.40,5,1,4,0,NULL,NULL,NULL,NULL,'2026-01-15 22:36:59.273059','2026-01-15 22:36:59.273088',109,30,NULL,NULL,NULL,NULL),
(702,'internal',2,84.00,65.50,23.60,4,1,4,0,NULL,NULL,NULL,NULL,'2026-01-15 22:36:59.280963','2026-01-15 22:36:59.280992',109,54,NULL,NULL,NULL,NULL),
(703,'internal',2,58.00,59.20,16.60,5,1,3,0,NULL,NULL,NULL,NULL,'2026-01-15 22:36:59.289849','2026-01-15 22:36:59.289879',109,109,NULL,NULL,NULL,NULL),
(704,'internal',2,73.00,68.20,17.60,5,1,2,0,NULL,NULL,NULL,NULL,'2026-01-15 22:36:59.297792','2026-01-15 22:36:59.297816',109,110,NULL,NULL,NULL,NULL),
(705,'internal',2,85.00,64.00,18.70,3,1,3,0,NULL,NULL,NULL,NULL,'2026-01-15 22:36:59.306860','2026-01-15 22:36:59.306887',109,111,NULL,NULL,NULL,NULL),
(706,'internal',2,78.00,59.50,18.90,3,1,2,0,NULL,NULL,NULL,NULL,'2026-01-15 22:36:59.314567','2026-01-15 22:36:59.314592',109,112,NULL,NULL,NULL,NULL),
(707,'internal',2,70.00,67.50,19.00,5,1,2,0,NULL,NULL,NULL,NULL,'2026-01-15 22:36:59.324221','2026-01-15 22:36:59.324251',109,134,NULL,NULL,NULL,NULL),
(708,'internal',2,65.00,64.80,18.30,5,1,2,0,NULL,NULL,NULL,NULL,'2026-01-15 22:36:59.331442','2026-01-15 22:36:59.331466',109,148,NULL,NULL,NULL,NULL),
(709,'internal',2,85.00,66.40,22.50,4,2,4,0,NULL,NULL,NULL,NULL,'2026-01-15 22:36:59.339617','2026-01-15 22:36:59.339645',109,4,NULL,NULL,NULL,NULL),
(710,'internal',2,65.00,56.70,21.90,5,2,4,0,NULL,NULL,NULL,NULL,'2026-01-15 22:36:59.347856','2026-01-15 22:36:59.347882',109,31,NULL,NULL,NULL,NULL),
(711,'internal',2,80.00,61.50,24.60,4,2,4,0,NULL,NULL,NULL,NULL,'2026-01-15 22:36:59.357679','2026-01-15 22:36:59.357705',109,55,NULL,NULL,NULL,NULL),
(712,'internal',2,58.00,62.70,15.00,5,2,2,0,NULL,NULL,NULL,NULL,'2026-01-15 22:36:59.365877','2026-01-15 22:36:59.365903',109,109,NULL,NULL,NULL,NULL),
(713,'internal',2,83.00,65.90,20.30,4,2,3,0,NULL,NULL,NULL,NULL,'2026-01-15 22:36:59.374717','2026-01-15 22:36:59.374745',109,110,NULL,NULL,NULL,NULL),
(714,'internal',2,79.00,55.80,18.10,3,2,2,0,NULL,NULL,NULL,NULL,'2026-01-15 22:36:59.383071','2026-01-15 22:36:59.383100',109,111,NULL,NULL,NULL,NULL),
(715,'internal',2,89.00,59.60,20.70,2,2,3,0,NULL,NULL,NULL,NULL,'2026-01-15 22:36:59.416673','2026-01-15 22:36:59.416702',109,112,NULL,NULL,NULL,NULL),
(716,'internal',2,88.00,67.80,21.60,3,2,2,0,NULL,NULL,NULL,NULL,'2026-01-15 22:36:59.449418','2026-01-15 22:36:59.449447',109,134,NULL,NULL,NULL,NULL),
(717,'internal',2,54.00,53.80,21.60,5,2,2,0,NULL,NULL,NULL,NULL,'2026-01-15 22:36:59.458797','2026-01-15 22:36:59.458834',109,148,NULL,NULL,NULL,NULL),
(718,'internal',2,95.00,88.30,NULL,NULL,1,1,1,NULL,NULL,NULL,NULL,'2026-01-15 22:36:59.470182','2026-01-15 22:36:59.470215',109,169,'A',87.00,9.90,3.10),
(719,'internal',2,81.00,85.00,NULL,NULL,2,1,1,NULL,NULL,NULL,NULL,'2026-01-15 22:36:59.481996','2026-01-15 22:36:59.482034',109,169,'A',77.10,16.80,6.10);
/*!40000 ALTER TABLE `grades` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `maintenance_maintenance`
--

DROP TABLE IF EXISTS `maintenance_maintenance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `maintenance_maintenance` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `room_id` bigint NOT NULL,
  `date` date NOT NULL,
  `charge` int NOT NULL,
  `date_paid` date DEFAULT NULL,
  `memo` longtext NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `maintenance_maintenance_room_id_75f8318d` (`room_id`),
  CONSTRAINT `maintenance_maintenance_room_id_75f8318d_fk_maintenance_room_id` FOREIGN KEY (`room_id`) REFERENCES `maintenance_room` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=120 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `maintenance_maintenance`
--

LOCK TABLES `maintenance_maintenance` WRITE;
/*!40000 ALTER TABLE `maintenance_maintenance` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `maintenance_maintenance` VALUES
(1,1,'2024-10-01',285940,'2024-10-30','','2024-10-24 03:04:05.478000','2024-10-30 23:46:48.099000'),
(2,2,'2024-10-01',232210,'2024-10-30','','2024-10-24 03:05:11.201000','2024-10-30 23:47:05.500000'),
(3,3,'2024-10-01',482970,'2024-10-30','','2024-10-24 03:05:56.502000','2024-10-30 23:47:14.615000'),
(4,2,'2024-09-01',256490,'2024-09-30','','2024-10-24 03:10:47.132000','2024-10-24 03:38:13.991000'),
(5,1,'2024-09-01',349220,'2024-09-30','','2024-10-24 03:23:23.041000','2024-10-24 03:23:23.041000'),
(10,3,'2024-09-01',635990,'2024-09-30','','2024-10-24 03:36:29.064000','2024-10-24 03:38:50.429000'),
(14,1,'2024-08-01',350810,'2024-08-30','','2024-10-24 03:48:51.435000','2024-10-24 03:48:51.435000'),
(15,2,'2024-08-01',232600,'2024-08-30','','2024-10-24 03:49:32.755000','2024-10-24 03:49:32.755000'),
(16,3,'2024-08-01',688700,'2024-08-30','','2024-10-24 03:50:02.804000','2024-10-24 03:50:02.804000'),
(17,1,'2024-07-01',342600,'2024-07-31','','2024-10-24 03:52:39.379000','2024-10-24 03:52:39.392000'),
(19,2,'2024-07-01',242230,'2024-07-31','','2024-10-24 03:55:31.344000','2024-10-24 03:55:31.372000'),
(20,3,'2024-07-01',550550,'2024-07-31','','2024-10-24 03:58:44.711000','2024-10-24 03:58:44.739000'),
(21,1,'2024-06-01',287900,'2024-06-30','','2024-10-24 04:00:35.922000','2024-10-24 04:00:35.937000'),
(22,2,'2024-06-01',232720,'2024-06-30','','2024-10-24 04:04:36.898000','2024-10-24 04:04:36.913000'),
(23,3,'2024-06-01',449430,'2024-06-30','','2024-10-24 04:05:02.329000','2024-10-24 04:05:02.341000'),
(24,1,'2024-05-01',272890,'2024-05-31','','2024-10-24 04:16:51.398000','2024-10-24 04:16:51.425000'),
(25,2,'2024-05-01',231210,'2024-05-31','','2024-10-24 04:17:25.781000','2024-10-24 04:17:25.810000'),
(26,3,'2024-05-01',408430,'2024-05-31','','2024-10-24 04:17:55.531000','2024-10-24 04:17:55.544000'),
(27,1,'2024-04-01',287750,'2024-04-30','','2024-10-24 06:35:35.528000','2024-10-24 06:35:35.557000'),
(28,2,'2024-04-01',231260,'2024-04-30','','2024-10-24 06:35:59.839000','2024-10-24 06:35:59.868000'),
(29,3,'2024-04-01',456000,'2024-04-30','','2024-10-24 06:36:23.782000','2024-10-24 06:36:23.812000'),
(30,1,'2024-03-01',362300,'2024-03-26','','2024-10-24 06:37:21.872000','2024-10-24 06:37:21.895000'),
(31,2,'2024-03-01',230550,'2024-03-26','','2024-10-24 06:37:46.398000','2024-10-24 06:37:46.410000'),
(32,3,'2024-03-01',556770,'2024-03-26','','2024-10-24 06:38:15.339000','2024-10-24 06:38:15.354000'),
(33,1,'2024-02-01',485760,'2024-02-29','','2024-10-24 06:39:01.805000','2024-10-24 06:39:01.820000'),
(34,2,'2024-02-01',242380,'2024-02-29','','2024-10-24 06:39:24.316000','2024-10-24 06:39:24.344000'),
(35,3,'2024-02-01',692410,'2024-02-29','','2024-10-24 06:39:49.474000','2024-10-24 06:39:49.488000'),
(36,1,'2024-01-01',383240,'2024-01-28','','2024-10-24 06:40:43.070000','2024-10-24 06:40:43.098000'),
(37,2,'2024-01-01',225620,'2024-12-08','','2024-10-24 06:41:08.343000','2024-10-24 06:41:08.357000'),
(38,3,'2024-01-01',590520,'2024-01-28','','2024-10-24 06:41:37.791000','2024-10-24 06:41:37.822000'),
(39,1,'2022-12-01',319140,'2022-12-27','','2024-10-24 17:06:34.186000','2024-10-24 17:06:34.199000'),
(40,2,'2022-12-01',217640,'2022-12-27','','2024-10-24 17:07:01.115000','2024-10-24 17:07:01.128000'),
(41,1,'2023-01-01',428290,'2023-01-27','','2024-10-24 17:10:07.149000','2024-10-24 17:10:07.175000'),
(42,2,'2023-01-01',221120,'2023-01-27','','2024-10-24 17:11:40.822000','2024-10-24 17:11:40.849000'),
(43,3,'2023-01-01',511620,'2023-01-27','','2024-10-24 17:12:09.833000','2024-10-24 17:12:09.859000'),
(44,1,'2023-02-01',472350,'2023-02-28','','2024-10-24 17:13:03.712000','2024-10-24 17:13:03.725000'),
(45,3,'2023-02-01',553930,'2023-02-28','','2024-10-24 17:14:00.891000','2024-10-24 17:14:00.903000'),
(46,2,'2023-02-01',234860,'2023-02-28','','2024-10-24 17:19:27.703000','2024-10-24 17:19:27.732000'),
(47,1,'2023-03-01',347950,'2023-03-29','','2024-10-24 17:20:31.681000','2024-10-24 17:20:31.710000'),
(48,2,'2023-03-01',222260,'2023-03-29','','2024-10-24 17:21:01.283000','2024-10-24 17:21:01.295000'),
(49,3,'2023-03-01',470100,'2023-03-29','','2024-10-24 17:21:29.305000','2024-10-24 17:21:29.318000'),
(50,1,'2023-04-01',275680,'2023-04-30','','2024-10-24 17:22:06.751000','2024-10-24 17:22:06.764000'),
(51,2,'2023-04-01',217500,'2023-04-30','','2024-10-24 17:22:27.616000','2024-10-24 17:22:27.643000'),
(52,3,'2023-04-01',411240,'2023-04-30','','2024-10-24 17:23:03.145000','2024-10-24 17:23:03.173000'),
(53,1,'2023-05-01',266340,'2023-05-28','','2024-10-24 17:23:44.560000','2024-10-24 17:23:44.582000'),
(54,2,'2023-05-01',219340,'2023-05-28','','2024-10-24 17:24:08.496000','2024-10-24 17:24:08.524000'),
(55,3,'2023-05-01',399390,'2023-05-28','','2024-10-24 17:24:38.636000','2024-10-24 17:24:38.650000'),
(56,1,'2023-06-01',282390,'2023-06-30','','2024-10-24 17:25:14.690000','2024-10-24 17:25:14.703000'),
(57,2,'2023-06-01',232160,'2023-06-30','','2024-10-24 17:25:49.866000','2024-10-24 17:25:49.895000'),
(58,3,'2023-06-01',460890,'2023-06-30','','2024-10-24 17:28:27.625000','2024-10-24 17:28:27.639000'),
(59,1,'2023-07-01',327600,'2023-07-26','','2024-10-24 17:29:14.852000','2024-10-24 17:29:14.878000'),
(60,2,'2023-07-01',231180,'2023-07-26','','2024-10-24 17:29:34.730000','2024-10-24 17:29:34.747000'),
(61,3,'2023-07-01',554230,'2023-07-26','','2024-10-24 17:29:59.253000','2024-10-24 17:29:59.280000'),
(62,1,'2023-08-01',377180,'2023-08-31','','2024-10-24 17:30:38.087000','2024-10-24 17:30:38.114000'),
(63,2,'2023-08-01',245210,'2023-08-31','','2024-10-24 17:31:03.727000','2024-10-24 17:31:03.739000'),
(64,3,'2023-08-01',698020,'2023-08-31','','2024-10-24 17:31:28.511000','2024-10-24 17:31:28.536000'),
(65,1,'2023-09-01',316530,'2023-09-28','','2024-10-24 17:32:05.650000','2024-10-24 17:32:05.677000'),
(66,2,'2023-09-01',230860,'2023-09-28','','2024-10-24 17:32:37.838000','2024-10-24 17:32:37.865000'),
(67,3,'2023-09-01',605950,'2023-09-28','','2024-10-24 17:33:02.159000','2024-10-24 17:33:02.187000'),
(68,1,'2023-10-01',284520,'2023-10-31','','2024-10-24 17:33:57.074000','2024-10-24 17:33:57.085000'),
(69,2,'2023-10-01',231680,'2023-10-31','','2024-10-24 17:34:19.515000','2024-10-24 17:34:19.542000'),
(70,3,'2023-10-01',453580,'2023-10-31','','2024-10-24 17:34:42.596000','2024-10-24 17:34:42.608000'),
(71,1,'2023-11-01',261480,'2023-11-30','','2024-10-24 17:35:20.975000','2024-10-24 17:35:21.002000'),
(72,2,'2023-11-01',226020,'2023-11-30','','2024-10-24 17:35:47.708000','2024-10-24 17:35:47.722000'),
(73,3,'2023-11-01',406610,'2023-11-30','','2024-10-24 17:36:09.977000','2024-10-24 17:36:10.003000'),
(74,1,'2023-12-01',383700,'2023-12-29','','2024-10-24 17:36:43.378000','2024-10-24 17:38:50.137000'),
(75,2,'2023-12-01',234310,'2023-12-29','','2024-10-24 17:37:03.167000','2024-10-24 17:39:44.703000'),
(76,3,'2023-12-01',514350,'2023-12-29','','2024-10-24 17:38:00.620000','2024-10-24 17:38:00.649000'),
(77,3,'2022-12-01',438760,'2022-12-27','','2024-10-24 17:41:46.216000','2024-10-24 17:41:46.243000'),
(84,1,'2024-11-01',284190,'2024-11-29','','2024-11-22 16:27:00.051000','2024-11-29 17:13:40.775000'),
(85,2,'2024-11-01',232880,'2024-11-29','','2024-11-22 16:27:00.067000','2024-11-29 17:13:46.157000'),
(86,3,'2024-11-01',426270,'2024-11-29','','2024-11-22 16:27:00.082000','2024-11-29 17:13:53.237000'),
(87,1,'2024-12-01',296520,'2024-12-29','','2024-12-23 22:51:14.590944','2024-12-29 23:22:56.278508'),
(88,2,'2024-12-01',243390,'2024-12-29','','2024-12-23 22:51:14.609887','2024-12-29 23:23:02.287771'),
(89,3,'2024-12-01',519970,'2024-12-29','','2024-12-23 22:51:14.614337','2024-12-29 23:23:09.216441'),
(90,1,'2025-01-01',371450,'2025-01-28','','2025-01-22 23:49:32.025666','2025-01-28 01:48:25.592558'),
(91,2,'2025-01-01',250560,'2025-01-28','','2025-01-22 23:49:32.030179','2025-01-28 01:48:31.577633'),
(92,3,'2025-01-01',577730,'2025-01-28','','2025-01-22 23:49:32.033968','2025-01-28 01:48:37.032503'),
(93,1,'2025-02-01',389870,'2025-02-28','','2025-02-22 01:02:18.800241','2025-03-02 21:10:03.783356'),
(94,2,'2025-02-01',248190,'2025-02-28','','2025-02-22 01:02:18.804770','2025-03-02 21:10:09.635197'),
(95,3,'2025-02-01',636040,'2025-02-28','','2025-02-22 01:02:18.808769','2025-03-02 21:10:16.462927'),
(96,1,'2025-03-01',373190,'2025-03-28','','2025-03-25 00:44:29.088732','2025-03-28 23:12:18.819189'),
(97,2,'2025-03-01',242290,'2025-03-28','','2025-03-25 00:44:29.092719','2025-03-28 23:12:24.702867'),
(98,3,'2025-03-01',573660,'2025-03-28','','2025-03-25 00:44:29.096712','2025-03-28 23:12:29.923604'),
(99,1,'2025-06-01',265260,'2025-06-30','','2025-06-30 23:46:47.402805','2025-06-30 23:46:47.402805'),
(100,2,'2025-06-01',233240,'2025-06-30','','2025-06-30 23:46:47.408131','2025-06-30 23:46:47.408131'),
(101,3,'2025-06-01',422580,'2025-06-30','','2025-06-30 23:46:47.412626','2025-06-30 23:46:47.412626'),
(102,1,'2025-07-01',311760,'2025-07-31','','2025-07-24 02:21:49.662759','2025-08-01 23:00:54.697681'),
(103,2,'2025-07-01',242750,'2025-07-31','','2025-07-24 02:21:49.670509','2025-08-01 23:01:00.674919'),
(104,3,'2025-07-01',527370,'2025-07-31','','2025-07-24 02:21:49.675356','2025-08-01 23:01:06.730114'),
(105,1,'2025-08-01',338410,'2025-08-29','','2025-09-30 17:51:00.871499','2025-09-30 17:51:00.871509'),
(106,2,'2025-08-01',247730,'2025-08-29','','2025-09-30 17:51:00.878271','2025-09-30 17:51:00.878287'),
(107,3,'2025-08-01',694660,'2025-08-29','','2025-09-30 17:51:00.883270','2025-09-30 17:51:00.883292'),
(108,1,'2025-09-01',311160,'2025-09-30','','2025-09-30 17:54:27.626556','2025-09-30 17:54:27.626579'),
(109,2,'2025-09-01',251030,'2025-09-30','','2025-09-30 17:54:27.630812','2025-09-30 17:54:27.630824'),
(110,3,'2025-09-01',600340,'2025-09-30','','2025-09-30 17:54:27.634769','2025-09-30 17:54:27.634782'),
(111,1,'2025-10-01',261530,'2025-10-31','','2025-10-31 16:21:05.209888','2025-10-31 16:21:05.209906'),
(112,2,'2025-10-01',233200,'2025-10-31','','2025-10-31 16:21:05.229858','2025-10-31 16:21:05.229888'),
(113,3,'2025-10-01',463710,'2025-10-31','','2025-10-31 16:21:05.234499','2025-10-31 16:21:05.234521'),
(114,1,'2025-11-01',258430,'2025-11-30','','2025-12-03 02:53:21.706547','2025-12-03 02:53:21.706559'),
(115,2,'2025-11-01',237740,'2025-11-30','','2025-12-03 02:53:21.713473','2025-12-03 02:53:21.713490'),
(116,3,'2025-11-01',433350,'2025-11-30','','2025-12-03 02:53:21.717591','2025-12-03 02:53:21.717610'),
(117,1,'2025-12-01',282820,'2025-12-31','','2025-12-24 00:13:06.990203','2025-12-31 00:44:21.513727'),
(118,2,'2025-12-01',242390,'2025-12-31','','2025-12-24 00:13:07.014560','2025-12-31 00:44:27.419533'),
(119,3,'2025-12-01',502870,'2025-12-31','','2025-12-24 00:13:07.035683','2025-12-31 00:44:35.058637');
/*!40000 ALTER TABLE `maintenance_maintenance` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `maintenance_room`
--

DROP TABLE IF EXISTS `maintenance_room`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `maintenance_room` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `number` int NOT NULL,
  `contract_start_date` date NOT NULL,
  `contract_end_date` date DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `number` (`number`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `maintenance_room`
--

LOCK TABLES `maintenance_room` WRITE;
/*!40000 ALTER TABLE `maintenance_room` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `maintenance_room` VALUES
(1,512,'2023-03-01',NULL,1,'2024-10-24 02:50:35.934000','2024-10-24 02:50:35.934000'),
(2,515,'2023-08-01',NULL,1,'2024-10-24 02:50:58.338000','2024-10-24 02:50:58.338000'),
(3,516,'2023-04-25',NULL,1,'2024-10-24 02:51:25.413000','2024-10-24 02:51:25.413000');
/*!40000 ALTER TABLE `maintenance_room` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `payment_bookpayment`
--

DROP TABLE IF EXISTS `payment_bookpayment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `payment_bookpayment` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `original_price` int unsigned NOT NULL,
  `discounted_price` int unsigned NOT NULL,
  `book_distribution_id` bigint NOT NULL,
  `payment_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `book_distribution_id` (`book_distribution_id`),
  KEY `payment_bookpayment_payment_id_5d2e470e_fk_payment_payment_id` (`payment_id`),
  CONSTRAINT `payment_bookpayment_book_distribution_id_f07020b7_fk_bookstore` FOREIGN KEY (`book_distribution_id`) REFERENCES `bookstore_bookdistribution` (`id`),
  CONSTRAINT `payment_bookpayment_payment_id_5d2e470e_fk_payment_payment_id` FOREIGN KEY (`payment_id`) REFERENCES `payment_payment` (`id`),
  CONSTRAINT `payment_bookpayment_chk_1` CHECK ((`original_price` >= 0)),
  CONSTRAINT `payment_bookpayment_chk_2` CHECK ((`discounted_price` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payment_bookpayment`
--

LOCK TABLES `payment_bookpayment` WRITE;
/*!40000 ALTER TABLE `payment_bookpayment` DISABLE KEYS */;
set autocommit=0;
/*!40000 ALTER TABLE `payment_bookpayment` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `payment_payment`
--

DROP TABLE IF EXISTS `payment_payment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `payment_payment` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `payment_date` date DEFAULT NULL,
  `payment_method` varchar(10) DEFAULT NULL,
  `student_id` bigint NOT NULL,
  `memo` longtext,
  `paid_amount` int unsigned DEFAULT NULL,
  `status` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `payment_payment_student_id_873ead1d_fk_students_student_id` (`student_id`),
  CONSTRAINT `payment_payment_student_id_873ead1d_fk_students_student_id` FOREIGN KEY (`student_id`) REFERENCES `students_student` (`id`),
  CONSTRAINT `payment_payment_chk_1` CHECK ((`paid_amount` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payment_payment`
--

LOCK TABLES `payment_payment` WRITE;
/*!40000 ALTER TABLE `payment_payment` DISABLE KEYS */;
set autocommit=0;
/*!40000 ALTER TABLE `payment_payment` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `payment_paymenthistory`
--

DROP TABLE IF EXISTS `payment_paymenthistory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `payment_paymenthistory` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `amount` int unsigned NOT NULL,
  `payment_method` varchar(10) NOT NULL,
  `paid_at` datetime(6) NOT NULL,
  `receipt_no` varchar(50) NOT NULL,
  `payment_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `payment_paymenthistory_payment_id_4bdec8c7_fk_payment_payment_id` (`payment_id`),
  CONSTRAINT `payment_paymenthistory_payment_id_4bdec8c7_fk_payment_payment_id` FOREIGN KEY (`payment_id`) REFERENCES `payment_payment` (`id`),
  CONSTRAINT `payment_paymenthistory_chk_1` CHECK ((`amount` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payment_paymenthistory`
--

LOCK TABLES `payment_paymenthistory` WRITE;
/*!40000 ALTER TABLE `payment_paymenthistory` DISABLE KEYS */;
set autocommit=0;
/*!40000 ALTER TABLE `payment_paymenthistory` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `progress_bookproblem`
--

DROP TABLE IF EXISTS `progress_bookproblem`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `progress_bookproblem` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `problem_type_id` bigint NOT NULL,
  `page` int unsigned DEFAULT NULL,
  `order` int unsigned NOT NULL,
  `memo` varchar(255) NOT NULL,
  `book_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `progress_bookproblem_book_id_problem_type_id_297c3f3e_uniq` (`book_id`,`problem_type_id`),
  KEY `progress_bookproblem_book_id_23e22fc1` (`book_id`),
  KEY `progress_bookproblem_problem_type_id_9573340a` (`problem_type_id`),
  CONSTRAINT `progress_bookproblem_book_id_23e22fc1_fk_bookstore_book_id` FOREIGN KEY (`book_id`) REFERENCES `bookstore_book` (`id`),
  CONSTRAINT `progress_bookproblem_problem_type_id_9573340a_fk_progress_` FOREIGN KEY (`problem_type_id`) REFERENCES `progress_problemtype` (`id`),
  CONSTRAINT `progress_bookproblem_chk_1` CHECK ((`page` >= 0)),
  CONSTRAINT `progress_bookproblem_chk_2` CHECK ((`order` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `progress_bookproblem`
--

LOCK TABLES `progress_bookproblem` WRITE;
/*!40000 ALTER TABLE `progress_bookproblem` DISABLE KEYS */;
set autocommit=0;
/*!40000 ALTER TABLE `progress_bookproblem` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `progress_problemtype`
--

DROP TABLE IF EXISTS `progress_problemtype`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `progress_problemtype` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `code_number` varchar(20) NOT NULL,
  `title` varchar(200) NOT NULL,
  `memo` longtext NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `difficulty` int unsigned NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code_number` (`code_number`),
  CONSTRAINT `progress_problemtype_chk_1` CHECK ((`difficulty` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `progress_problemtype`
--

LOCK TABLES `progress_problemtype` WRITE;
/*!40000 ALTER TABLE `progress_problemtype` DISABLE KEYS */;
set autocommit=0;
/*!40000 ALTER TABLE `progress_problemtype` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `progress_progressentry`
--

DROP TABLE IF EXISTS `progress_progressentry`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `progress_progressentry` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `is_assigned` tinyint(1) NOT NULL,
  `study_date` date DEFAULT NULL,
  `understanding` int unsigned DEFAULT NULL,
  `homework` varchar(255) NOT NULL,
  `memo` varchar(255) NOT NULL,
  `book_problem_id` bigint NOT NULL,
  `teacher_id` bigint DEFAULT NULL,
  `progress_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `progress_progressentry_progress_id_book_problem_id_84c23586_uniq` (`progress_id`,`book_problem_id`),
  KEY `progress_progressent_book_problem_id_62177e1e_fk_progress_` (`book_problem_id`),
  KEY `progress_progressent_teacher_id_5daf9cd9_fk_teachers_` (`teacher_id`),
  CONSTRAINT `progress_progressent_book_problem_id_62177e1e_fk_progress_` FOREIGN KEY (`book_problem_id`) REFERENCES `progress_bookproblem` (`id`),
  CONSTRAINT `progress_progressent_progress_id_6ac8a516_fk_progress_` FOREIGN KEY (`progress_id`) REFERENCES `progress_studentprogress` (`id`),
  CONSTRAINT `progress_progressent_teacher_id_5daf9cd9_fk_teachers_` FOREIGN KEY (`teacher_id`) REFERENCES `teachers_teacher` (`id`),
  CONSTRAINT `progress_progressentry_chk_1` CHECK ((`understanding` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `progress_progressentry`
--

LOCK TABLES `progress_progressentry` WRITE;
/*!40000 ALTER TABLE `progress_progressentry` DISABLE KEYS */;
set autocommit=0;
/*!40000 ALTER TABLE `progress_progressentry` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `progress_studentprogress`
--

DROP TABLE IF EXISTS `progress_studentprogress`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `progress_studentprogress` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `memo` longtext NOT NULL,
  `book_id` bigint NOT NULL,
  `book_sale_id` bigint NOT NULL,
  `student_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `book_sale_id` (`book_sale_id`),
  KEY `progress_studentprogress_book_id_e74f34ba_fk_bookstore_book_id` (`book_id`),
  KEY `progress_studentprog_student_id_accd3bf3_fk_students_` (`student_id`),
  CONSTRAINT `progress_studentprog_book_sale_id_055df84b_fk_bookstore` FOREIGN KEY (`book_sale_id`) REFERENCES `bookstore_booksale` (`id`),
  CONSTRAINT `progress_studentprog_student_id_accd3bf3_fk_students_` FOREIGN KEY (`student_id`) REFERENCES `students_student` (`id`),
  CONSTRAINT `progress_studentprogress_book_id_e74f34ba_fk_bookstore_book_id` FOREIGN KEY (`book_id`) REFERENCES `bookstore_book` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `progress_studentprogress`
--

LOCK TABLES `progress_studentprogress` WRITE;
/*!40000 ALTER TABLE `progress_studentprogress` DISABLE KEYS */;
set autocommit=0;
/*!40000 ALTER TABLE `progress_studentprogress` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `students_student`
--

DROP TABLE IF EXISTS `students_student`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `students_student` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `grade` varchar(3) DEFAULT NULL,
  `phone_number` varchar(15) DEFAULT NULL,
  `email` varchar(254) DEFAULT NULL,
  `gender` varchar(1) DEFAULT NULL,
  `parent_phone` varchar(15) DEFAULT NULL,
  `receipt_number` varchar(15) DEFAULT NULL,
  `interview_date` date DEFAULT NULL,
  `interview_score` int DEFAULT NULL,
  `interview_info` longtext,
  `first_class_date` date DEFAULT NULL,
  `quit_date` date DEFAULT NULL,
  `student_id` varchar(8) NOT NULL,
  `personal_file` varchar(100) DEFAULT NULL,
  `etc` longtext,
  `extra1` varchar(100) DEFAULT NULL,
  `extra2` varchar(100) DEFAULT NULL,
  `extra3` varchar(100) DEFAULT NULL,
  `extra4` varchar(100) DEFAULT NULL,
  `extra5` varchar(100) DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL,
  `school_id` bigint DEFAULT NULL,
  `unpaid_amount` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `student_id` (`student_id`),
  KEY `students_student_school_id_be4a7ab9_fk_common_school_id` (`school_id`),
  CONSTRAINT `students_student_school_id_be4a7ab9_fk_common_school_id` FOREIGN KEY (`school_id`) REFERENCES `common_school` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=113 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `students_student`
--

LOCK TABLES `students_student` WRITE;
/*!40000 ALTER TABLE `students_student` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `students_student` VALUES
(68,'임수영','K7','010-9943-7830',NULL,'F','010-9910-7830',NULL,NULL,NULL,NULL,NULL,NULL,'11858021','',NULL,NULL,NULL,NULL,NULL,NULL,1,31,0),
(69,'이은서','K7',NULL,NULL,'F','010-3531-7017',NULL,NULL,NULL,NULL,NULL,NULL,'45396216','',NULL,NULL,NULL,NULL,NULL,NULL,1,32,0),
(70,'백승윤','K8','010-9969-3014',NULL,'M','010-2475-2800',NULL,NULL,NULL,NULL,NULL,NULL,'38025079','',NULL,NULL,NULL,NULL,NULL,NULL,1,33,0),
(71,'구도현','K8',NULL,NULL,'M','010-8974-3153','010-8974-3153',NULL,NULL,NULL,NULL,NULL,'10230562','',NULL,NULL,NULL,NULL,NULL,NULL,1,33,12000),
(72,'이찬','K8','010-9316-3507',NULL,'M','010-6329-3507','010-6239-3507',NULL,NULL,NULL,NULL,NULL,'45629572','',NULL,NULL,NULL,NULL,NULL,NULL,1,33,0),
(73,'김용민','K8','010-6216-1324',NULL,'M','010-8969-2722',NULL,NULL,NULL,NULL,NULL,NULL,'14789871','',NULL,NULL,NULL,NULL,NULL,NULL,1,33,0),
(74,'황수아','K8','010-5380-3698',NULL,'F','010-4125-7172',NULL,NULL,NULL,NULL,NULL,NULL,'20543767','',NULL,NULL,NULL,NULL,NULL,NULL,1,34,0),
(75,'유지원','K7','010-9582-7805',NULL,'F','010-6582-7805','010-6582-7805',NULL,NULL,NULL,NULL,NULL,'53495914','',NULL,NULL,NULL,NULL,NULL,NULL,1,33,15000),
(76,'선시우','K8',NULL,NULL,'M','010-2781-0082',NULL,NULL,NULL,NULL,NULL,NULL,'51077520','',NULL,NULL,NULL,NULL,NULL,NULL,1,33,0),
(77,'정하경','K6',NULL,NULL,'M','010-3439-8915',NULL,NULL,NULL,NULL,NULL,NULL,'64890751','',NULL,NULL,NULL,NULL,NULL,NULL,1,35,0),
(78,'신시윤','K7',NULL,NULL,'F','010-2609-7218',NULL,NULL,NULL,NULL,NULL,NULL,'56226226','',NULL,NULL,NULL,NULL,NULL,NULL,1,32,0),
(79,'이은성','K6','010-7794-3516',NULL,'M','010-8654-3516','010-8654-3516',NULL,NULL,NULL,NULL,NULL,'64610469','',NULL,NULL,NULL,NULL,NULL,NULL,1,36,12000),
(80,'강지유','K7','010-5283-2720',NULL,'F','010-7118-3347',NULL,NULL,NULL,NULL,NULL,NULL,'84933730','',NULL,NULL,NULL,NULL,NULL,NULL,1,32,0),
(81,'윤희성','K8','010-3651-9316',NULL,'M','010-8947-9316',NULL,NULL,NULL,NULL,NULL,NULL,'24436927','',NULL,NULL,NULL,NULL,NULL,NULL,1,32,0),
(82,'김서윤','K6',NULL,NULL,'F','010-5524-6928',NULL,NULL,NULL,NULL,NULL,NULL,'59918230','',NULL,NULL,NULL,NULL,NULL,NULL,1,37,0),
(83,'김에녹','K6',NULL,NULL,'M','010-5039-2774',NULL,NULL,NULL,NULL,NULL,NULL,'17318596','',NULL,NULL,NULL,NULL,NULL,NULL,1,36,0),
(84,'이단비','K8',NULL,NULL,'F','010-9990-5644',NULL,NULL,NULL,NULL,NULL,NULL,'14933625','',NULL,NULL,NULL,NULL,NULL,NULL,1,38,0),
(85,'김수근','K9','010-4287-3537',NULL,'M','010-2949-3537','010-2949-3537',NULL,NULL,NULL,NULL,NULL,'76062072','',NULL,NULL,NULL,NULL,NULL,NULL,1,38,13000),
(86,'장현정','K9','010-5601-7274',NULL,'F','010-3209-7705',NULL,NULL,NULL,NULL,NULL,NULL,'23042470','',NULL,NULL,NULL,NULL,NULL,NULL,1,34,0),
(87,'안유솔','K9','010-6565-0464',NULL,'F','010-8927-0310',NULL,NULL,NULL,NULL,NULL,NULL,'10637205','',NULL,NULL,NULL,NULL,NULL,NULL,1,32,0),
(88,'송은채','K9','010-3461-3487',NULL,'F','010-2883-3487',NULL,NULL,NULL,NULL,NULL,NULL,'28491203','',NULL,NULL,NULL,NULL,NULL,NULL,1,31,0),
(89,'김민관','K9','010-4198-9240',NULL,'M','010-7160-0622',NULL,NULL,NULL,NULL,NULL,NULL,'96792167','',NULL,NULL,NULL,NULL,NULL,NULL,1,32,0),
(90,'김승호','K9','010-8244-4748',NULL,'M','010-8244-4747',NULL,NULL,NULL,NULL,NULL,NULL,'91625767','',NULL,NULL,NULL,NULL,NULL,NULL,1,32,0),
(91,'장수빈','K9','010-8574-6621',NULL,'F','010-2521-8312',NULL,NULL,NULL,NULL,NULL,NULL,'25494618','',NULL,NULL,NULL,NULL,NULL,NULL,1,34,0),
(92,'김노아','K9',NULL,NULL,'M','010-5039-2774',NULL,NULL,NULL,NULL,NULL,NULL,'23245816','',NULL,NULL,NULL,NULL,NULL,NULL,1,34,0),
(93,'배은준','K9',NULL,NULL,'M','010-7126-4243',NULL,NULL,NULL,NULL,NULL,NULL,'66275157','',NULL,NULL,NULL,NULL,NULL,NULL,1,39,0),
(94,'국도연','K9','010-4639-8079',NULL,'F','010-4587-8079',NULL,NULL,NULL,NULL,NULL,NULL,'08800338','',NULL,NULL,NULL,NULL,NULL,NULL,1,31,0),
(95,'최보영','K9',NULL,NULL,'F','010-9026-4492',NULL,NULL,NULL,NULL,NULL,NULL,'20888561','',NULL,NULL,NULL,NULL,NULL,NULL,1,40,0),
(96,'임호경','K9','010-9913-7830',NULL,'F','010-9910-7830',NULL,NULL,NULL,NULL,NULL,NULL,'65781602','',NULL,NULL,NULL,NULL,NULL,NULL,1,31,0),
(97,'소지영','K10','010-4931-8411',NULL,'F','010-5013-8411',NULL,NULL,NULL,NULL,NULL,NULL,'40887306','',NULL,NULL,NULL,NULL,NULL,NULL,1,41,0),
(98,'김승근','K10','010-9295-3537',NULL,'M','010-2949-3537',NULL,NULL,NULL,NULL,NULL,NULL,'22661670','',NULL,NULL,NULL,NULL,NULL,NULL,1,42,0),
(99,'이성연','K10',NULL,NULL,'M','010-6322-9397',NULL,NULL,NULL,NULL,NULL,NULL,'06152535','',NULL,NULL,NULL,NULL,NULL,NULL,1,42,0),
(100,'정아영','K10','010-4675-0907',NULL,'F','010-3764-0422',NULL,NULL,NULL,NULL,NULL,NULL,'80501611','',NULL,NULL,NULL,NULL,NULL,NULL,1,41,0),
(101,'김미정','K10','010-2928-4175',NULL,'F','010-6204-7096','010-6204-7096',NULL,NULL,NULL,NULL,NULL,'93754480','',NULL,NULL,NULL,NULL,NULL,NULL,1,43,17000),
(102,'이하윤','K10',NULL,NULL,'F','010-2314-5685','010-2314-5685',NULL,NULL,NULL,NULL,NULL,'08525493','',NULL,NULL,NULL,NULL,NULL,NULL,1,44,17000),
(103,'김재엽','K11','010-7106-9109',NULL,'M','010-2459-9109',NULL,NULL,NULL,NULL,NULL,NULL,'84909924','',NULL,NULL,NULL,NULL,NULL,NULL,1,45,0),
(104,'강현준','K11','010-8514-2324',NULL,'M','010-3396-2314',NULL,NULL,NULL,NULL,NULL,NULL,'79903906','',NULL,NULL,NULL,NULL,NULL,NULL,1,43,0),
(105,'박준성','K11',NULL,NULL,'M','010-2035-5529',NULL,NULL,NULL,NULL,NULL,NULL,'64026559','',NULL,NULL,NULL,NULL,NULL,NULL,1,46,0),
(106,'김율','K11','010-6270-7457',NULL,'F','010-4956-7213','010-4956-7213',NULL,NULL,NULL,NULL,NULL,'56627867','',NULL,NULL,NULL,NULL,NULL,NULL,1,45,21000),
(107,'김채은','K11','010-2541-7096',NULL,'F','010-6204-7096','010-6204-7096',NULL,NULL,NULL,NULL,NULL,'94222465','',NULL,NULL,NULL,NULL,NULL,NULL,1,47,32000),
(108,'배서은','K11','010-3749-0965',NULL,'F','010-7126-4243','010-7126-4243',NULL,NULL,NULL,NULL,NULL,'20500986','',NULL,NULL,NULL,NULL,NULL,NULL,1,41,21000),
(109,'박주원','K11','010-4964-5270',NULL,'M','010-4586-5270','010-4586-5270',NULL,NULL,NULL,NULL,NULL,'72569342','',NULL,NULL,NULL,NULL,NULL,NULL,1,41,10000),
(110,'박지후','K11','010-8782-3832',NULL,'F','010-5204-1154',NULL,NULL,NULL,NULL,NULL,NULL,'02336888','',NULL,NULL,NULL,NULL,NULL,NULL,1,42,0),
(111,'정지민','K11','010-5856-2311',NULL,'F','010-8636-1450',NULL,NULL,NULL,NULL,NULL,NULL,'61507594','',NULL,NULL,NULL,NULL,NULL,NULL,1,45,0),
(112,'김민채','K11','010-4650-8297',NULL,'F','010-5011-6234','010-5011-6234',NULL,NULL,NULL,NULL,NULL,'35433987','',NULL,NULL,NULL,NULL,NULL,NULL,1,43,12000);
/*!40000 ALTER TABLE `students_student` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `students_studentfile`
--

DROP TABLE IF EXISTS `students_studentfile`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `students_studentfile` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `file` varchar(100) NOT NULL,
  `file_name` varchar(255) NOT NULL,
  `description` longtext,
  `uploaded_at` datetime(6) NOT NULL,
  `student_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `students_studentfile_student_id_99ee67e1_fk_students_student_id` (`student_id`),
  CONSTRAINT `students_studentfile_student_id_99ee67e1_fk_students_student_id` FOREIGN KEY (`student_id`) REFERENCES `students_student` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `students_studentfile`
--

LOCK TABLES `students_studentfile` WRITE;
/*!40000 ALTER TABLE `students_studentfile` DISABLE KEYS */;
set autocommit=0;
/*!40000 ALTER TABLE `students_studentfile` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `subjects`
--

DROP TABLE IF EXISTS `subjects`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `subjects` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `subject_code` varchar(10) NOT NULL,
  `name` varchar(100) NOT NULL,
  `special_code` varchar(50) DEFAULT NULL,
  `memo` longtext,
  `extra` varchar(200) DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `category_code` varchar(2) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `subject_code` (`subject_code`)
) ENGINE=InnoDB AUTO_INCREMENT=190 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `subjects`
--

LOCK TABLES `subjects` WRITE;
/*!40000 ALTER TABLE `subjects` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `subjects` VALUES
(1,'1001','국어',NULL,NULL,NULL,1,'2025-12-28 18:37:37.557761','2025-12-28 18:37:37.557790',NULL),
(2,'1002','화법과 작문',NULL,NULL,NULL,1,'2025-12-28 18:37:37.598331','2025-12-28 18:37:37.598354',NULL),
(3,'1003','문학',NULL,NULL,NULL,1,'2025-12-28 18:37:37.628489','2025-12-28 18:37:37.628524',NULL),
(4,'1004','독서',NULL,NULL,NULL,1,'2025-12-28 18:37:37.656302','2025-12-28 18:37:37.656358',NULL),
(5,'1005','언어와 매체',NULL,NULL,NULL,1,'2025-12-28 18:37:37.688479','2025-12-28 18:37:37.688515',NULL),
(6,'1006','실용 국어',NULL,NULL,NULL,1,'2025-12-28 18:37:37.714278','2025-12-28 18:37:37.714302',NULL),
(7,'1007','심화 국어',NULL,NULL,NULL,1,'2025-12-28 18:37:37.744049','2025-12-28 18:37:37.744072',NULL),
(8,'1008','고전 읽기',NULL,NULL,NULL,1,'2025-12-28 18:37:37.772526','2025-12-28 18:37:37.772557',NULL),
(9,'1009','문예 창작 입문',NULL,NULL,NULL,1,'2025-12-28 18:37:37.802168','2025-12-28 18:37:37.802193',NULL),
(10,'1010','문학 개론',NULL,NULL,NULL,1,'2025-12-28 18:37:37.829299','2025-12-28 18:37:37.829324',NULL),
(11,'1011','문장론',NULL,NULL,NULL,1,'2025-12-28 18:37:37.859615','2025-12-28 18:37:37.859649',NULL),
(12,'1012','문학과 매체',NULL,NULL,NULL,1,'2025-12-28 18:37:37.886454','2025-12-28 18:37:37.886490',NULL),
(13,'1013','고전 문학 감상',NULL,NULL,NULL,1,'2025-12-28 18:37:37.912532','2025-12-28 18:37:37.912566',NULL),
(14,'1014','현대 문학 감상',NULL,NULL,NULL,1,'2025-12-28 18:37:37.940493','2025-12-28 18:37:37.940529',NULL),
(15,'1015','시 창작',NULL,NULL,NULL,1,'2025-12-28 18:37:37.968528','2025-12-28 18:37:37.968553',NULL),
(16,'1016','소설 창작',NULL,NULL,NULL,1,'2025-12-28 18:37:37.994936','2025-12-28 18:37:37.994959',NULL),
(17,'1017','극 창작',NULL,NULL,NULL,1,'2025-12-28 18:37:38.018788','2025-12-28 18:37:38.018815',NULL),
(18,'1018','국어1',NULL,NULL,NULL,1,'2025-12-28 18:37:38.047006','2025-12-28 18:37:38.047031',NULL),
(19,'1019','국어2',NULL,NULL,NULL,1,'2025-12-28 18:37:38.075791','2025-12-28 18:37:38.075816',NULL),
(20,'1020','문학1',NULL,NULL,NULL,1,'2025-12-28 18:37:38.106061','2025-12-28 18:37:38.106089',NULL),
(21,'1021','문학2',NULL,NULL,NULL,1,'2025-12-28 18:37:38.134440','2025-12-28 18:37:38.134502',NULL),
(22,'1022','독서와 문법',NULL,NULL,NULL,1,'2025-12-28 18:37:38.163364','2025-12-28 18:37:38.163405',NULL),
(23,'1023','독서와 문법1',NULL,NULL,NULL,1,'2025-12-28 18:37:38.190301','2025-12-28 18:37:38.190325',NULL),
(24,'1024','화법과 작문1',NULL,NULL,NULL,1,'2025-12-28 18:37:38.218132','2025-12-28 18:37:38.218171',NULL),
(25,'1025','화법과 작문2',NULL,NULL,NULL,1,'2025-12-28 18:37:38.246136','2025-12-28 18:37:38.246160',NULL),
(26,'1026','고전',NULL,NULL,NULL,1,'2025-12-28 18:37:38.274349','2025-12-28 18:37:38.274387',NULL),
(27,'1027','문학의 이해',NULL,NULL,NULL,1,'2025-12-28 18:37:38.301728','2025-12-28 18:37:38.301762',NULL),
(28,'1028','논술',NULL,NULL,NULL,1,'2025-12-28 18:37:38.340550','2025-12-28 18:37:38.340582',NULL),
(29,'2001','수학',NULL,'',NULL,0,'2025-12-28 18:37:38.378908','2026-01-04 01:21:48.132001',NULL),
(30,'2002','수학1',NULL,NULL,NULL,1,'2025-12-28 18:37:38.424427','2025-12-28 18:37:38.424451',NULL),
(31,'2003','수학2',NULL,NULL,NULL,1,'2025-12-28 18:37:38.461544','2025-12-28 18:37:38.461585',NULL),
(32,'2004','미적분',NULL,NULL,NULL,1,'2025-12-28 18:37:38.500031','2025-12-28 18:37:38.500073',NULL),
(33,'2005','확률과 통계',NULL,NULL,NULL,1,'2025-12-28 18:37:38.536487','2025-12-28 18:37:38.536520',NULL),
(34,'2006','실용 수학',NULL,NULL,NULL,1,'2025-12-28 18:37:38.561558','2025-12-28 18:37:38.561581',NULL),
(35,'2007','기하',NULL,NULL,NULL,1,'2025-12-28 18:37:38.590471','2025-12-28 18:37:38.590508',NULL),
(36,'2008','경제수학',NULL,NULL,NULL,1,'2025-12-28 18:37:38.617640','2025-12-28 18:37:38.617676',NULL),
(37,'2009','수학과제탐구',NULL,NULL,NULL,1,'2025-12-28 18:37:38.647355','2025-12-28 18:37:38.647379',NULL),
(38,'2010','심화 수학1',NULL,NULL,NULL,1,'2025-12-28 18:37:38.674894','2025-12-28 18:37:38.674932',NULL),
(39,'2011','심화 수학2',NULL,NULL,NULL,1,'2025-12-28 18:37:38.702276','2025-12-28 18:37:38.702311',NULL),
(40,'2012','고급 수학1',NULL,NULL,NULL,1,'2025-12-28 18:37:38.727494','2025-12-28 18:37:38.727530',NULL),
(41,'2013','고급 수학2',NULL,NULL,NULL,1,'2025-12-28 18:37:38.754401','2025-12-28 18:37:38.754442',NULL),
(42,'2014','인문 통합 수학',NULL,NULL,NULL,1,'2025-12-28 18:37:38.784092','2025-12-28 18:37:38.784132',NULL),
(43,'2015','자연 통합 수학',NULL,NULL,NULL,1,'2025-12-28 18:37:38.810510','2025-12-28 18:37:38.810546',NULL),
(44,'2016','기초 수학',NULL,NULL,NULL,1,'2025-12-28 18:37:38.835031','2025-12-28 18:37:38.835057',NULL),
(45,'2017','수학 연습',NULL,NULL,NULL,1,'2025-12-28 18:37:38.863226','2025-12-28 18:37:38.863251',NULL),
(46,'2018','수학의 활용',NULL,NULL,NULL,1,'2025-12-28 18:37:38.889558','2025-12-28 18:37:38.889604',NULL),
(47,'2019','미적분과 통계 기본',NULL,NULL,NULL,1,'2025-12-28 18:37:38.916180','2025-12-28 18:37:38.916228',NULL),
(48,'2020','미적분1',NULL,NULL,NULL,1,'2025-12-28 18:37:38.955521','2025-12-28 18:37:38.955544',NULL),
(49,'2021','미적분2',NULL,NULL,NULL,1,'2025-12-28 18:37:38.978711','2025-12-28 18:37:38.978736',NULL),
(50,'2022','기하와 벡터',NULL,NULL,NULL,1,'2025-12-28 18:37:39.007573','2025-12-28 18:37:39.007626',NULL),
(51,'2023','이산수학',NULL,NULL,NULL,1,'2025-12-28 18:37:39.032952','2025-12-28 18:37:39.032979',NULL),
(52,'2024','적분과 통계',NULL,NULL,NULL,1,'2025-12-28 18:37:39.059573','2025-12-28 18:37:39.059610',NULL),
(53,'3001','영어',NULL,NULL,NULL,1,'2025-12-28 18:37:39.090242','2025-12-28 18:37:39.090269',NULL),
(54,'3002','영어1',NULL,NULL,NULL,1,'2025-12-28 18:37:39.115199','2025-12-28 18:37:39.115244',NULL),
(55,'3003','영어2',NULL,NULL,NULL,1,'2025-12-28 18:37:39.142197','2025-12-28 18:37:39.142233',NULL),
(56,'3004','영어독해와 작문',NULL,NULL,NULL,1,'2025-12-28 18:37:39.172423','2025-12-28 18:37:39.172461',NULL),
(57,'3005','영어 회화',NULL,NULL,NULL,1,'2025-12-28 18:37:39.203169','2025-12-28 18:37:39.203204',NULL),
(58,'3006','실용 영어',NULL,NULL,NULL,1,'2025-12-28 18:37:39.229241','2025-12-28 18:37:39.229323',NULL),
(59,'3007','영어권 문화',NULL,NULL,NULL,1,'2025-12-28 18:37:39.256458','2025-12-28 18:37:39.256494',NULL),
(60,'3008','진로 영어',NULL,NULL,NULL,1,'2025-12-28 18:37:39.286405','2025-12-28 18:37:39.286430',NULL),
(61,'3009','영미 문학 읽기',NULL,NULL,NULL,1,'2025-12-28 18:37:39.313493','2025-12-28 18:37:39.313518',NULL),
(62,'3010','심화 영어 회화1',NULL,NULL,NULL,1,'2025-12-28 18:37:39.343979','2025-12-28 18:37:39.344008',NULL),
(63,'3011','심화 영어 회화2',NULL,NULL,NULL,1,'2025-12-28 18:37:39.368732','2025-12-28 18:37:39.368767',NULL),
(64,'3012','심화 영어1',NULL,NULL,NULL,1,'2025-12-28 18:37:39.396320','2025-12-28 18:37:39.396342',NULL),
(65,'3013','심화 영어2',NULL,NULL,NULL,1,'2025-12-28 18:37:39.422953','2025-12-28 18:37:39.423045',NULL),
(66,'3014','심화 영어 독해1',NULL,NULL,NULL,1,'2025-12-28 18:37:39.447531','2025-12-28 18:37:39.447558',NULL),
(67,'3015','심화 영어 독해2',NULL,NULL,NULL,1,'2025-12-28 18:37:39.473800','2025-12-28 18:37:39.473837',NULL),
(68,'3016','심화 영어 작문1',NULL,NULL,NULL,1,'2025-12-28 18:37:39.503962','2025-12-28 18:37:39.504003',NULL),
(69,'3017','심화 영어 작문2',NULL,NULL,NULL,1,'2025-12-28 18:37:39.532410','2025-12-28 18:37:39.532433',NULL),
(70,'3018','기초 영어',NULL,NULL,NULL,1,'2025-12-28 18:37:39.555521','2025-12-28 18:37:39.555547',NULL),
(71,'3019','영어 독해',NULL,NULL,NULL,1,'2025-12-28 18:37:39.584362','2025-12-28 18:37:39.584403',NULL),
(72,'3020','영어 작문',NULL,NULL,NULL,1,'2025-12-28 18:37:39.611784','2025-12-28 18:37:39.611810',NULL),
(73,'3021','영어 문법',NULL,NULL,NULL,1,'2025-12-28 18:37:39.642585','2025-12-28 18:37:39.642620',NULL),
(74,'3022','영어 청해',NULL,NULL,NULL,1,'2025-12-28 18:37:39.667332','2025-12-28 18:37:39.667367',NULL),
(75,'3023','실용 영어2',NULL,NULL,NULL,1,'2025-12-28 18:37:39.695381','2025-12-28 18:37:39.695403',NULL),
(76,'3024','영어 회화2',NULL,NULL,NULL,1,'2025-12-28 18:37:39.722127','2025-12-28 18:37:39.722153',NULL),
(77,'3025','아카데믹 영어',NULL,NULL,NULL,1,'2025-12-28 18:37:39.752671','2025-12-28 18:37:39.752709',NULL),
(78,'3026','영어 비평적 읽기와 쓰기',NULL,NULL,NULL,1,'2025-12-28 18:37:39.781979','2025-12-28 18:37:39.782001',NULL),
(79,'3027','응용 영문법',NULL,NULL,NULL,1,'2025-12-28 18:37:39.811159','2025-12-28 18:37:39.811194',NULL),
(80,'4001','통합사회',NULL,NULL,NULL,1,'2025-12-28 18:37:39.835883','2025-12-28 18:37:39.835919',NULL),
(81,'4002','한국지리',NULL,NULL,NULL,1,'2025-12-28 18:37:39.857667','2025-12-28 18:37:39.857691',NULL),
(82,'4003','세계지리',NULL,NULL,NULL,1,'2025-12-28 18:37:39.888233','2025-12-28 18:37:39.888260',NULL),
(83,'4004','세계사',NULL,NULL,NULL,1,'2025-12-28 18:37:39.914110','2025-12-28 18:37:39.914133',NULL),
(84,'4005','동아시아사',NULL,NULL,NULL,1,'2025-12-28 18:37:39.940310','2025-12-28 18:37:39.940338',NULL),
(85,'4006','경제',NULL,NULL,NULL,1,'2025-12-28 18:37:39.970216','2025-12-28 18:37:39.970254',NULL),
(86,'4007','정치와 법',NULL,NULL,NULL,1,'2025-12-28 18:37:39.996985','2025-12-28 18:37:39.997018',NULL),
(87,'4008','사회 문화',NULL,NULL,NULL,1,'2025-12-28 18:37:40.022741','2025-12-28 18:37:40.022776',NULL),
(88,'4009','생활과 윤리',NULL,NULL,NULL,1,'2025-12-28 18:37:40.050155','2025-12-28 18:37:40.050180',NULL),
(89,'4010','윤리와 사상',NULL,NULL,NULL,1,'2025-12-28 18:37:40.080112','2025-12-28 18:37:40.080149',NULL),
(90,'4011','여행지리',NULL,NULL,NULL,1,'2025-12-28 18:37:40.109261','2025-12-28 18:37:40.109285',NULL),
(91,'4012','사회문제 탐구',NULL,NULL,NULL,1,'2025-12-28 18:37:40.140143','2025-12-28 18:37:40.140180',NULL),
(92,'4013','고전과 윤리',NULL,NULL,NULL,1,'2025-12-28 18:37:40.170015','2025-12-28 18:37:40.170038',NULL),
(93,'4014','국제정치',NULL,NULL,NULL,1,'2025-12-28 18:37:40.202417','2025-12-28 18:37:40.202443',NULL),
(94,'4015','국제경제',NULL,NULL,NULL,1,'2025-12-28 18:37:40.232816','2025-12-28 18:37:40.232841',NULL),
(95,'4016','국제법',NULL,NULL,NULL,1,'2025-12-28 18:37:40.263474','2025-12-28 18:37:40.263508',NULL),
(96,'4017','지역이해',NULL,NULL,NULL,1,'2025-12-28 18:37:40.290094','2025-12-28 18:37:40.290119',NULL),
(97,'4018','한국사회의 이해',NULL,NULL,NULL,1,'2025-12-28 18:37:40.319797','2025-12-28 18:37:40.319822',NULL),
(98,'4019','비교 문화',NULL,NULL,NULL,1,'2025-12-28 18:37:40.350131','2025-12-28 18:37:40.350158',NULL),
(99,'4020','세계문제와 미래사회',NULL,NULL,NULL,1,'2025-12-28 18:37:40.375829','2025-12-28 18:37:40.375854',NULL),
(100,'4021','국제관계와 국제기구',NULL,NULL,NULL,1,'2025-12-28 18:37:40.400179','2025-12-28 18:37:40.400203',NULL),
(101,'4022','현대 세계의 변화',NULL,NULL,NULL,1,'2025-12-28 18:37:40.426468','2025-12-28 18:37:40.426498',NULL),
(102,'4023','사회 탐구 방법',NULL,NULL,NULL,1,'2025-12-28 18:37:40.451718','2025-12-28 18:37:40.451744',NULL),
(103,'4024','사회 과제 연구',NULL,NULL,NULL,1,'2025-12-28 18:37:40.475871','2025-12-28 18:37:40.475907',NULL),
(104,'4025','사회',NULL,NULL,NULL,1,'2025-12-28 18:37:40.512407','2025-12-28 18:37:40.512433',NULL),
(105,'4026','정치',NULL,NULL,NULL,1,'2025-12-28 18:37:40.538105','2025-12-28 18:37:40.538171',NULL),
(106,'4027','한국 근현대사',NULL,NULL,NULL,1,'2025-12-28 18:37:40.563727','2025-12-28 18:37:40.563752',NULL),
(107,'5001','통합과학',NULL,NULL,NULL,1,'2025-12-28 18:37:40.589607','2025-12-28 18:37:40.589636',NULL),
(108,'5002','과학 탐구 실험',NULL,NULL,NULL,1,'2025-12-28 18:37:40.621319','2025-12-28 18:37:40.621366',NULL),
(109,'5003','물리학1',NULL,NULL,NULL,1,'2025-12-28 18:37:40.651329','2025-12-28 18:37:40.651354',NULL),
(110,'5004','화학1',NULL,NULL,NULL,1,'2025-12-28 18:37:40.675862','2025-12-28 18:37:40.675923',NULL),
(111,'5005','생명과학1',NULL,NULL,NULL,1,'2025-12-28 18:37:40.703480','2025-12-28 18:37:40.703505',NULL),
(112,'5006','지구과학1',NULL,NULL,NULL,1,'2025-12-28 18:37:40.732107','2025-12-28 18:37:40.732132',NULL),
(113,'5007','물리학2',NULL,NULL,NULL,1,'2025-12-28 18:37:40.755174','2025-12-28 18:37:40.755201',NULL),
(114,'5008','화학2',NULL,NULL,NULL,1,'2025-12-28 18:37:40.785483','2025-12-28 18:37:40.785518',NULL),
(115,'5009','생명과학2',NULL,NULL,NULL,1,'2025-12-28 18:37:40.817843','2025-12-28 18:37:40.817931',NULL),
(116,'5010','지구과학2',NULL,NULL,NULL,1,'2025-12-28 18:37:40.843220','2025-12-28 18:37:40.843318',NULL),
(117,'5011','과학사',NULL,NULL,NULL,1,'2025-12-28 18:37:40.869352','2025-12-28 18:37:40.869377',NULL),
(118,'5012','생활과 과학',NULL,NULL,NULL,1,'2025-12-28 18:37:40.895512','2025-12-28 18:37:40.895546',NULL),
(119,'5013','융합과학',NULL,NULL,NULL,1,'2025-12-28 18:37:40.922354','2025-12-28 18:37:40.922383',NULL),
(120,'5014','고급 물리학',NULL,NULL,NULL,1,'2025-12-28 18:37:40.951404','2025-12-28 18:37:40.951447',NULL),
(121,'5015','고급 화학',NULL,NULL,NULL,1,'2025-12-28 18:37:40.978106','2025-12-28 18:37:40.978133',NULL),
(122,'5016','고급 생명과학',NULL,NULL,NULL,1,'2025-12-28 18:37:41.005948','2025-12-28 18:37:41.005982',NULL),
(123,'5017','고급 지구과학',NULL,NULL,NULL,1,'2025-12-28 18:37:41.031474','2025-12-28 18:37:41.031500',NULL),
(124,'5018','물리학 실험',NULL,NULL,NULL,1,'2025-12-28 18:37:41.055378','2025-12-28 18:37:41.055414',NULL),
(125,'5019','화학 실험',NULL,NULL,NULL,1,'2025-12-28 18:37:41.083334','2025-12-28 18:37:41.083369',NULL),
(126,'5020','생명과학 실험',NULL,NULL,NULL,1,'2025-12-28 18:37:41.108164','2025-12-28 18:37:41.108193',NULL),
(127,'5021','지구과학 실험',NULL,NULL,NULL,1,'2025-12-28 18:37:41.131057','2025-12-28 18:37:41.131091',NULL),
(128,'5022','정보과학',NULL,NULL,NULL,1,'2025-12-28 18:37:41.155539','2025-12-28 18:37:41.155567',NULL),
(129,'5023','융합과학 탐구',NULL,NULL,NULL,1,'2025-12-28 18:37:41.179224','2025-12-28 18:37:41.179265',NULL),
(130,'5024','과학 과제연구',NULL,NULL,NULL,1,'2025-12-28 18:37:41.206753','2025-12-28 18:37:41.206778',NULL),
(131,'5025','생태와 환경',NULL,NULL,NULL,1,'2025-12-28 18:37:41.229437','2025-12-28 18:37:41.229483',NULL),
(132,'6001','한국사',NULL,NULL,NULL,1,'2025-12-28 18:37:41.256445','2025-12-28 18:37:41.256471',NULL),
(133,'7001','기술 가정',NULL,NULL,NULL,1,'2025-12-28 18:37:41.282999','2025-12-28 18:37:41.283035',NULL),
(134,'7002','정보',NULL,NULL,NULL,1,'2025-12-28 18:37:41.311066','2025-12-28 18:37:41.311100',NULL),
(135,'7003','농업 생명 과학',NULL,NULL,NULL,1,'2025-12-28 18:37:41.335475','2025-12-28 18:37:41.335500',NULL),
(136,'7004','공학 일반',NULL,NULL,NULL,1,'2025-12-28 18:37:41.362616','2025-12-28 18:37:41.362650',NULL),
(137,'7005','창의 경영',NULL,NULL,NULL,1,'2025-12-28 18:37:41.391285','2025-12-28 18:37:41.391308',NULL),
(138,'7006','해양문화와 기술',NULL,NULL,NULL,1,'2025-12-28 18:37:41.411913','2025-12-28 18:37:41.411948',NULL),
(139,'7007','가정과학',NULL,NULL,NULL,1,'2025-12-28 18:37:41.433413','2025-12-28 18:37:41.433437',NULL),
(140,'7008','지식재산 일반',NULL,NULL,NULL,1,'2025-12-28 18:37:41.456967','2025-12-28 18:37:41.456990',NULL),
(141,'7009','정보사회와 컴퓨터',NULL,NULL,NULL,1,'2025-12-28 18:37:41.477475','2025-12-28 18:37:41.477518',NULL),
(142,'7010','해양과학',NULL,NULL,NULL,1,'2025-12-28 18:37:41.501218','2025-12-28 18:37:41.501242',NULL),
(143,'7011','영상 일반',NULL,NULL,NULL,1,'2025-12-28 18:37:41.524257','2025-12-28 18:37:41.524290',NULL),
(144,'8001','독일어1',NULL,NULL,NULL,1,'2025-12-28 18:37:41.546355','2025-12-28 18:37:41.546403',NULL),
(145,'8002','프랑스어1',NULL,NULL,NULL,1,'2025-12-28 18:37:41.568573','2025-12-28 18:37:41.568596',NULL),
(146,'8003','스페인어1',NULL,NULL,NULL,1,'2025-12-28 18:37:41.591325','2025-12-28 18:37:41.591367',NULL),
(147,'8004','중국어1',NULL,NULL,NULL,1,'2025-12-28 18:37:41.615117','2025-12-28 18:37:41.615141',NULL),
(148,'8005','일본어1',NULL,NULL,NULL,1,'2025-12-28 18:37:41.640543','2025-12-28 18:37:41.640566',NULL),
(149,'8006','러시아어1',NULL,NULL,NULL,1,'2025-12-28 18:37:41.664225','2025-12-28 18:37:41.664260',NULL),
(150,'8007','아랍어1',NULL,NULL,NULL,1,'2025-12-28 18:37:41.685302','2025-12-28 18:37:41.685324',NULL),
(151,'8008','베트남어1',NULL,NULL,NULL,1,'2025-12-28 18:37:41.714761','2025-12-28 18:37:41.714786',NULL),
(152,'8009','독일어2',NULL,NULL,NULL,1,'2025-12-28 18:37:41.737819','2025-12-28 18:37:41.738007',NULL),
(153,'8010','프랑스어2',NULL,NULL,NULL,1,'2025-12-28 18:37:41.760581','2025-12-28 18:37:41.760632',NULL),
(154,'8011','스페인어2',NULL,NULL,NULL,1,'2025-12-28 18:37:41.787276','2025-12-28 18:37:41.787313',NULL),
(155,'8012','중국어2',NULL,NULL,NULL,1,'2025-12-28 18:37:41.816196','2025-12-28 18:37:41.816218',NULL),
(156,'8013','일본어2',NULL,NULL,NULL,1,'2025-12-28 18:37:41.841274','2025-12-28 18:37:41.841301',NULL),
(157,'8014','러시아어2',NULL,NULL,NULL,1,'2025-12-28 18:37:41.868718','2025-12-28 18:37:41.868745',NULL),
(158,'8015','아랍어2',NULL,NULL,NULL,1,'2025-12-28 18:37:41.894500','2025-12-28 18:37:41.894535',NULL),
(159,'8016','베트남어2',NULL,NULL,NULL,1,'2025-12-28 18:37:41.918706','2025-12-28 18:37:41.918741',NULL),
(160,'9001','한문1',NULL,NULL,NULL,1,'2025-12-28 18:37:41.938773','2025-12-28 18:37:41.938798',NULL),
(161,'9002','한문2',NULL,NULL,NULL,1,'2025-12-28 18:37:41.959066','2025-12-28 18:37:41.959101',NULL),
(162,'9101','체육',NULL,'',NULL,1,'2025-12-28 18:37:41.979360','2025-12-28 22:08:20.103198',NULL),
(163,'9102','운동과 건강',NULL,NULL,NULL,1,'2025-12-28 18:37:42.004729','2025-12-28 22:11:35.038916','91'),
(164,'9103','스포츠 생활',NULL,NULL,NULL,1,'2025-12-28 18:37:42.029316','2025-12-28 22:11:35.075541','91'),
(165,'9104','체육탐구',NULL,NULL,NULL,1,'2025-12-28 18:37:42.054147','2025-12-28 22:11:35.112204','91'),
(166,'9201','음악',NULL,NULL,NULL,1,'2025-12-28 18:37:42.078236','2025-12-28 22:11:35.131814','92'),
(167,'9202','미술',NULL,NULL,NULL,1,'2025-12-28 18:37:42.100135','2025-12-28 22:11:35.148990','92'),
(168,'9203','연극',NULL,NULL,NULL,1,'2025-12-28 18:37:42.122206','2025-12-28 22:11:35.172737','92'),
(169,'9204','음악 연주',NULL,NULL,NULL,1,'2025-12-28 18:37:42.145798','2025-12-28 22:11:35.189060','92'),
(170,'9205','음악감상과 비평',NULL,NULL,NULL,1,'2025-12-28 18:37:42.166604','2025-12-28 22:11:35.214282','92'),
(171,'9206','미술 창작',NULL,NULL,NULL,1,'2025-12-28 18:37:42.191760','2025-12-28 22:11:35.233074','92'),
(172,'9207','미술감상과 비평',NULL,NULL,NULL,1,'2025-12-28 18:37:42.212650','2025-12-28 22:11:35.250899','92'),
(173,'9301','철학',NULL,NULL,NULL,1,'2025-12-28 18:37:42.237774','2025-12-28 22:11:35.272649','93'),
(174,'9302','논리학',NULL,NULL,NULL,1,'2025-12-28 18:37:42.261763','2025-12-28 22:11:35.297023','93'),
(175,'9303','심리학',NULL,NULL,NULL,1,'2025-12-28 18:37:42.288900','2025-12-28 22:11:35.314835','93'),
(176,'9304','교육학',NULL,NULL,NULL,1,'2025-12-28 18:37:42.318563','2025-12-28 22:11:35.336026','93'),
(177,'9305','종교학',NULL,NULL,NULL,1,'2025-12-28 18:37:42.341821','2025-12-28 22:11:35.356736','93'),
(178,'9306','진로와 직업',NULL,NULL,NULL,1,'2025-12-28 18:37:42.363041','2025-12-28 22:11:35.377689','93'),
(179,'9307','보건',NULL,NULL,NULL,1,'2025-12-28 18:37:42.389841','2025-12-28 22:11:35.404365','93'),
(180,'9308','환경',NULL,NULL,NULL,1,'2025-12-28 18:37:42.417168','2025-12-28 22:11:35.422497','93'),
(181,'9309','실용 경제',NULL,NULL,NULL,1,'2025-12-28 18:37:42.441579','2025-12-28 22:11:35.440572','93'),
(182,'9310','논술',NULL,NULL,NULL,1,'2025-12-28 18:37:42.464698','2025-12-28 22:11:35.458168','93'),
(183,'7012','프로그래밍',NULL,'',NULL,1,'2025-12-30 18:50:38.153342','2025-12-30 18:50:38.153366',NULL),
(184,'2025','공통수학1',NULL,'',NULL,1,'2026-01-04 00:52:48.240974','2026-01-04 00:52:48.241005',NULL),
(185,'2026','공통수학2',NULL,'',NULL,1,'2026-01-04 01:03:27.056961','2026-01-04 01:03:27.056988',NULL),
(186,'2027','대수',NULL,'',NULL,1,'2026-01-04 01:03:39.460719','2026-01-04 01:03:39.460772',NULL),
(187,'2701','중1수학',NULL,'',NULL,1,'2026-01-04 01:20:33.372975','2026-01-04 01:20:33.373022',NULL),
(188,'2801','중2수학',NULL,'',NULL,1,'2026-01-04 01:20:55.140452','2026-01-04 01:20:55.140489',NULL),
(189,'2901','중3수학',NULL,'',NULL,1,'2026-01-04 01:21:08.193840','2026-01-04 01:21:08.193892',NULL);
/*!40000 ALTER TABLE `subjects` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `teachers_attendance`
--

DROP TABLE IF EXISTS `teachers_attendance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `teachers_attendance` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `date` date NOT NULL,
  `teacher_id` bigint NOT NULL,
  `is_present` tinyint(1) NOT NULL,
  `end_time` time(6) DEFAULT NULL,
  `start_time` time(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `teachers_attendance_teacher_id_date_60e57648_uniq` (`teacher_id`,`date`),
  CONSTRAINT `teachers_attendance_teacher_id_19e2227d_fk_teachers_teacher_id` FOREIGN KEY (`teacher_id`) REFERENCES `teachers_teacher` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1726 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `teachers_attendance`
--

LOCK TABLES `teachers_attendance` WRITE;
/*!40000 ALTER TABLE `teachers_attendance` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `teachers_attendance` VALUES
(43,'2024-10-02',10,1,'20:00:00.000000','18:00:00.000000'),
(44,'2024-10-02',11,1,'20:00:00.000000','18:00:00.000000'),
(45,'2024-10-02',12,1,'20:00:00.000000','18:00:00.000000'),
(46,'2024-10-02',14,1,'20:00:00.000000','18:00:00.000000'),
(47,'2024-10-02',15,1,'20:00:00.000000','18:00:00.000000'),
(48,'2024-10-04',10,1,'20:00:00.000000','18:00:00.000000'),
(49,'2024-10-04',11,1,'20:00:00.000000','18:00:00.000000'),
(50,'2024-10-04',12,1,'20:00:00.000000','18:00:00.000000'),
(51,'2024-10-04',13,1,'20:00:00.000000','18:00:00.000000'),
(52,'2024-10-04',14,1,'20:00:00.000000','18:00:00.000000'),
(53,'2024-10-04',15,1,'20:00:00.000000','18:00:00.000000'),
(54,'2024-10-07',10,1,'20:00:00.000000','18:00:00.000000'),
(55,'2024-10-07',11,1,'20:00:00.000000','18:00:00.000000'),
(56,'2024-10-07',12,1,'20:00:00.000000','18:00:00.000000'),
(57,'2024-10-07',13,1,'20:00:00.000000','18:00:00.000000'),
(58,'2024-10-07',14,1,'20:00:00.000000','18:00:00.000000'),
(59,'2024-10-07',15,1,'20:00:00.000000','18:00:00.000000'),
(60,'2024-10-07',16,1,'20:00:00.000000','18:00:00.000000'),
(61,'2024-10-07',17,1,'20:00:00.000000','18:00:00.000000'),
(62,'2024-10-09',10,1,'20:00:00.000000','18:00:00.000000'),
(63,'2024-10-09',11,1,'20:00:00.000000','18:00:00.000000'),
(64,'2024-10-09',12,1,'20:00:00.000000','18:00:00.000000'),
(65,'2024-10-09',13,1,'20:00:00.000000','18:00:00.000000'),
(66,'2024-10-09',14,1,'20:00:00.000000','18:00:00.000000'),
(67,'2024-10-09',15,1,'20:00:00.000000','18:00:00.000000'),
(68,'2024-10-11',10,1,'20:00:00.000000','18:00:00.000000'),
(69,'2024-10-11',11,1,'20:00:00.000000','18:00:00.000000'),
(70,'2024-10-11',12,1,'20:00:00.000000','18:00:00.000000'),
(71,'2024-10-11',13,1,'20:00:00.000000','18:00:00.000000'),
(72,'2024-10-11',14,1,'20:00:00.000000','18:00:00.000000'),
(73,'2024-10-11',15,1,'20:00:00.000000','18:00:00.000000'),
(74,'2024-10-14',10,1,'20:00:00.000000','18:00:00.000000'),
(75,'2024-10-14',11,1,'20:00:00.000000','18:00:00.000000'),
(76,'2024-10-14',12,1,'20:00:00.000000','18:00:00.000000'),
(77,'2024-10-14',13,1,'20:00:00.000000','18:00:00.000000'),
(78,'2024-10-14',14,1,'20:00:00.000000','18:00:00.000000'),
(79,'2024-10-14',15,1,'20:00:00.000000','18:00:00.000000'),
(80,'2024-10-14',16,1,'20:00:00.000000','18:00:00.000000'),
(81,'2024-10-14',17,1,'20:00:00.000000','18:00:00.000000'),
(82,'2024-09-02',10,1,'20:00:00.000000','18:00:00.000000'),
(83,'2024-09-02',11,1,'20:00:00.000000','18:00:00.000000'),
(84,'2024-09-02',12,1,'20:00:00.000000','18:00:00.000000'),
(85,'2024-09-02',13,1,'20:00:00.000000','18:00:00.000000'),
(86,'2024-09-02',17,1,'20:00:00.000000','18:00:00.000000'),
(87,'2024-09-04',10,1,'20:00:00.000000','18:00:00.000000'),
(88,'2024-09-04',11,1,'20:00:00.000000','18:00:00.000000'),
(89,'2024-09-04',13,1,'20:00:00.000000','18:00:00.000000'),
(90,'2024-09-04',14,1,'20:00:00.000000','18:00:00.000000'),
(91,'2024-09-04',15,1,'20:00:00.000000','18:00:00.000000'),
(92,'2024-09-06',10,1,'20:00:00.000000','18:00:00.000000'),
(93,'2024-09-06',11,1,'20:00:00.000000','18:00:00.000000'),
(94,'2024-09-06',12,1,'20:00:00.000000','18:00:00.000000'),
(95,'2024-09-06',13,1,'20:00:00.000000','18:00:00.000000'),
(96,'2024-09-06',14,1,'20:00:00.000000','18:00:00.000000'),
(97,'2024-09-06',15,1,'20:00:00.000000','18:00:00.000000'),
(98,'2024-09-09',10,1,'20:00:00.000000','18:00:00.000000'),
(99,'2024-09-09',11,1,'20:00:00.000000','18:00:00.000000'),
(100,'2024-09-09',12,1,'20:00:00.000000','18:00:00.000000'),
(101,'2024-09-09',13,1,'20:00:00.000000','18:00:00.000000'),
(102,'2024-09-09',14,1,'20:00:00.000000','18:00:00.000000'),
(103,'2024-09-09',15,1,'20:00:00.000000','18:00:00.000000'),
(104,'2024-09-09',16,1,'20:00:00.000000','18:00:00.000000'),
(105,'2024-09-09',17,1,'20:00:00.000000','18:00:00.000000'),
(106,'2024-09-11',10,1,'20:00:00.000000','18:00:00.000000'),
(107,'2024-09-11',11,1,'20:00:00.000000','18:00:00.000000'),
(108,'2024-09-11',12,1,'20:00:00.000000','18:00:00.000000'),
(109,'2024-09-11',13,1,'20:00:00.000000','18:00:00.000000'),
(110,'2024-09-11',14,1,'20:00:00.000000','18:00:00.000000'),
(111,'2024-09-11',15,1,'20:00:00.000000','18:00:00.000000'),
(112,'2024-09-13',11,1,'20:00:00.000000','18:00:00.000000'),
(113,'2024-09-13',12,1,'20:00:00.000000','18:00:00.000000'),
(114,'2024-09-13',13,1,'20:00:00.000000','18:00:00.000000'),
(115,'2024-09-13',15,1,'20:00:00.000000','18:00:00.000000'),
(116,'2024-09-20',10,1,'20:00:00.000000','18:00:00.000000'),
(117,'2024-09-20',11,1,'20:00:00.000000','18:00:00.000000'),
(118,'2024-09-20',12,1,'20:00:00.000000','18:00:00.000000'),
(119,'2024-09-20',13,1,'20:00:00.000000','18:00:00.000000'),
(120,'2024-09-20',14,1,'20:00:00.000000','18:00:00.000000'),
(121,'2024-09-20',15,1,'20:00:00.000000','18:00:00.000000'),
(122,'2024-09-23',10,1,'20:00:00.000000','18:00:00.000000'),
(123,'2024-09-23',11,1,'20:00:00.000000','18:00:00.000000'),
(124,'2024-09-23',12,1,'20:00:00.000000','18:00:00.000000'),
(125,'2024-09-23',13,1,'20:00:00.000000','18:00:00.000000'),
(126,'2024-09-23',14,1,'20:00:00.000000','18:00:00.000000'),
(127,'2024-09-23',16,1,'20:00:00.000000','18:00:00.000000'),
(128,'2024-09-23',17,1,'20:00:00.000000','18:00:00.000000'),
(129,'2024-09-25',10,1,'20:00:00.000000','18:00:00.000000'),
(130,'2024-09-25',11,1,'20:00:00.000000','18:00:00.000000'),
(131,'2024-09-25',12,1,'20:00:00.000000','18:00:00.000000'),
(132,'2024-09-25',13,1,'20:00:00.000000','18:00:00.000000'),
(133,'2024-09-25',14,1,'20:00:00.000000','18:00:00.000000'),
(134,'2024-09-25',15,1,'20:00:00.000000','18:00:00.000000'),
(135,'2024-09-27',10,1,'20:00:00.000000','18:00:00.000000'),
(136,'2024-09-27',11,1,'20:00:00.000000','18:00:00.000000'),
(137,'2024-09-27',12,1,'20:00:00.000000','18:00:00.000000'),
(138,'2024-09-27',13,1,'20:00:00.000000','18:00:00.000000'),
(139,'2024-09-27',14,1,'20:00:00.000000','18:00:00.000000'),
(140,'2024-09-27',15,1,'20:00:00.000000','18:00:00.000000'),
(141,'2024-09-30',10,1,'20:00:00.000000','18:00:00.000000'),
(142,'2024-09-30',11,1,'20:00:00.000000','18:00:00.000000'),
(143,'2024-09-30',12,1,'20:00:00.000000','18:00:00.000000'),
(144,'2024-09-30',13,1,'20:00:00.000000','18:00:00.000000'),
(145,'2024-09-30',14,1,'20:00:00.000000','18:00:00.000000'),
(146,'2024-09-30',15,1,'20:00:00.000000','18:00:00.000000'),
(147,'2024-09-30',16,1,'20:00:00.000000','18:00:00.000000'),
(148,'2024-09-30',17,1,'20:00:00.000000','18:00:00.000000'),
(149,'2024-10-16',10,1,'20:00:00.000000','18:00:00.000000'),
(150,'2024-10-16',11,1,'20:00:00.000000','18:00:00.000000'),
(151,'2024-10-16',12,1,'20:00:00.000000','18:00:00.000000'),
(152,'2024-10-16',13,1,'20:00:00.000000','18:00:00.000000'),
(153,'2024-10-16',14,1,'20:00:00.000000','18:00:00.000000'),
(154,'2024-10-16',15,1,'20:00:00.000000','18:00:00.000000'),
(155,'2024-10-18',10,1,'20:00:00.000000','18:00:00.000000'),
(156,'2024-10-18',11,1,'20:00:00.000000','18:00:00.000000'),
(157,'2024-10-18',12,1,'20:00:00.000000','18:00:00.000000'),
(158,'2024-10-18',13,1,'20:00:00.000000','18:00:00.000000'),
(159,'2024-10-18',14,1,'20:00:00.000000','18:00:00.000000'),
(160,'2024-10-21',10,1,'20:00:00.000000','18:00:00.000000'),
(161,'2024-10-21',11,1,'20:00:00.000000','18:00:00.000000'),
(162,'2024-10-21',12,1,'20:00:00.000000','18:00:00.000000'),
(163,'2024-10-21',14,1,'20:00:00.000000','18:00:00.000000'),
(164,'2024-10-21',15,1,'20:00:00.000000','18:00:00.000000'),
(165,'2024-10-21',17,1,'20:00:00.000000','18:00:00.000000'),
(167,'2024-10-21',22,1,'20:00:00.000000','18:00:00.000000'),
(168,'2024-10-23',10,1,'20:00:00.000000','18:00:00.000000'),
(169,'2024-10-23',11,1,'20:00:00.000000','18:00:00.000000'),
(170,'2024-10-23',12,1,'20:00:00.000000','18:00:00.000000'),
(171,'2024-10-23',13,1,'20:00:00.000000','18:00:00.000000'),
(172,'2024-10-23',14,1,'20:00:00.000000','18:00:00.000000'),
(173,'2024-10-23',15,1,'20:00:00.000000','18:00:00.000000'),
(174,'2024-10-23',22,1,'20:00:00.000000','18:00:00.000000'),
(175,'2024-10-25',10,1,'20:00:00.000000','18:00:00.000000'),
(176,'2024-10-25',11,1,'20:00:00.000000','18:00:00.000000'),
(177,'2024-10-25',12,1,'20:00:00.000000','18:00:00.000000'),
(178,'2024-10-25',13,1,'20:00:00.000000','18:00:00.000000'),
(179,'2024-10-25',15,1,'20:00:00.000000','18:00:00.000000'),
(180,'2024-10-28',10,1,'20:00:00.000000','18:00:00.000000'),
(181,'2024-10-28',11,1,'20:00:00.000000','18:00:00.000000'),
(182,'2024-10-28',12,1,'20:00:00.000000','18:00:00.000000'),
(183,'2024-10-28',13,1,'20:00:00.000000','18:00:00.000000'),
(184,'2024-10-28',14,1,'20:00:00.000000','18:00:00.000000'),
(185,'2024-10-28',15,1,'20:00:00.000000','18:00:00.000000'),
(186,'2024-10-28',16,1,'20:00:00.000000','18:00:00.000000'),
(187,'2024-10-28',22,1,'20:00:00.000000','18:00:00.000000'),
(188,'2024-10-30',10,1,'20:00:00.000000','18:00:00.000000'),
(189,'2024-10-30',11,1,'20:00:00.000000','18:00:00.000000'),
(190,'2024-10-30',12,1,'20:00:00.000000','18:00:00.000000'),
(191,'2024-10-30',13,1,'20:00:00.000000','18:00:00.000000'),
(192,'2024-10-30',14,1,'20:00:00.000000','18:00:00.000000'),
(193,'2024-10-30',15,1,'20:00:00.000000','18:00:00.000000'),
(194,'2024-10-30',22,1,'20:00:00.000000','18:00:00.000000'),
(195,'2024-11-01',10,1,'20:00:00.000000','18:00:00.000000'),
(196,'2024-11-01',11,1,'20:00:00.000000','18:00:00.000000'),
(197,'2024-11-01',12,1,'20:00:00.000000','18:00:00.000000'),
(198,'2024-11-01',13,1,'20:00:00.000000','18:00:00.000000'),
(199,'2024-11-01',14,1,'20:00:00.000000','18:00:00.000000'),
(200,'2024-11-01',15,1,'20:00:00.000000','18:00:00.000000'),
(201,'2024-11-01',22,1,'20:00:00.000000','18:00:00.000000'),
(202,'2024-11-04',10,1,'20:00:00.000000','18:00:00.000000'),
(203,'2024-11-04',12,1,'20:00:00.000000','18:00:00.000000'),
(204,'2024-11-04',13,1,'20:00:00.000000','18:00:00.000000'),
(205,'2024-11-04',14,1,'20:00:00.000000','18:00:00.000000'),
(206,'2024-11-04',15,1,'20:00:00.000000','18:00:00.000000'),
(207,'2024-11-04',22,1,'20:00:00.000000','18:00:00.000000'),
(208,'2024-11-06',10,1,'20:00:00.000000','18:00:00.000000'),
(209,'2024-11-06',12,1,'20:00:00.000000','18:00:00.000000'),
(210,'2024-11-06',13,1,'20:00:00.000000','18:00:00.000000'),
(211,'2024-11-06',14,1,'20:00:00.000000','18:00:00.000000'),
(212,'2024-11-06',15,1,'20:00:00.000000','18:00:00.000000'),
(213,'2024-11-06',22,1,'20:00:00.000000','18:00:00.000000'),
(214,'2024-11-08',10,1,'20:00:00.000000','18:00:00.000000'),
(215,'2024-11-08',12,1,'20:00:00.000000','18:00:00.000000'),
(216,'2024-11-08',13,1,'20:00:00.000000','18:00:00.000000'),
(217,'2024-11-08',14,1,'20:00:00.000000','18:00:00.000000'),
(218,'2024-11-08',22,1,'20:00:00.000000','18:00:00.000000'),
(219,'2024-11-11',10,1,'20:00:00.000000','18:00:00.000000'),
(220,'2024-11-11',12,1,'20:00:00.000000','18:00:00.000000'),
(221,'2024-11-11',13,1,'20:00:00.000000','18:00:00.000000'),
(222,'2024-11-11',14,1,'20:00:00.000000','18:00:00.000000'),
(223,'2024-11-11',15,1,'20:00:00.000000','18:00:00.000000'),
(224,'2024-11-11',22,1,'20:00:00.000000','18:00:00.000000'),
(225,'2024-11-13',10,1,'20:00:00.000000','18:00:00.000000'),
(226,'2024-11-13',12,1,'20:00:00.000000','18:00:00.000000'),
(227,'2024-11-13',13,1,'20:00:00.000000','18:00:00.000000'),
(228,'2024-11-13',14,1,'20:00:00.000000','18:00:00.000000'),
(229,'2024-11-13',15,1,'20:00:00.000000','18:00:00.000000'),
(230,'2024-11-13',22,1,'20:00:00.000000','18:00:00.000000'),
(231,'2024-11-15',10,1,'20:00:00.000000','18:00:00.000000'),
(232,'2024-11-15',12,1,'20:00:00.000000','18:00:00.000000'),
(233,'2024-11-15',13,1,'20:00:00.000000','18:00:00.000000'),
(234,'2024-11-15',14,1,'20:00:00.000000','18:00:00.000000'),
(235,'2024-11-15',15,1,'20:00:00.000000','18:00:00.000000'),
(236,'2024-11-15',22,1,'20:00:00.000000','18:00:00.000000'),
(237,'2024-11-18',10,1,'20:00:00.000000','18:00:00.000000'),
(238,'2024-11-18',12,1,'20:00:00.000000','18:00:00.000000'),
(239,'2024-11-18',13,1,'20:00:00.000000','18:00:00.000000'),
(240,'2024-11-18',14,1,'20:00:00.000000','18:00:00.000000'),
(241,'2024-11-18',15,1,'20:00:00.000000','18:00:00.000000'),
(242,'2024-11-18',22,1,'20:00:00.000000','18:00:00.000000'),
(243,'2024-11-20',10,1,'20:00:00.000000','18:00:00.000000'),
(244,'2024-11-20',12,1,'20:00:00.000000','18:00:00.000000'),
(245,'2024-11-20',13,1,'20:00:00.000000','18:00:00.000000'),
(246,'2024-11-20',14,1,'20:00:00.000000','18:00:00.000000'),
(247,'2024-11-20',15,1,'20:00:00.000000','18:00:00.000000'),
(248,'2024-11-20',22,1,'20:00:00.000000','18:00:00.000000'),
(249,'2024-11-22',10,1,'20:00:00.000000','18:00:00.000000'),
(250,'2024-11-22',12,1,'20:00:00.000000','18:00:00.000000'),
(251,'2024-11-22',13,1,'20:00:00.000000','18:00:00.000000'),
(252,'2024-11-22',14,1,'20:00:00.000000','18:00:00.000000'),
(253,'2024-11-22',22,1,'20:00:00.000000','18:00:00.000000'),
(254,'2024-11-22',25,1,'20:00:00.000000','18:00:00.000000'),
(255,'2024-11-25',10,1,'20:00:00.000000','18:00:00.000000'),
(256,'2024-11-25',12,1,'20:00:00.000000','18:00:00.000000'),
(257,'2024-11-25',13,1,'20:00:00.000000','18:00:00.000000'),
(258,'2024-11-25',14,1,'20:00:00.000000','18:00:00.000000'),
(259,'2024-11-25',15,1,'20:00:00.000000','18:00:00.000000'),
(260,'2024-11-25',22,1,'20:00:00.000000','18:00:00.000000'),
(261,'2024-11-28',12,1,'20:00:00.000000','18:00:00.000000'),
(262,'2024-11-28',13,1,'20:00:00.000000','18:00:00.000000'),
(263,'2024-11-28',14,1,'20:00:00.000000','18:00:00.000000'),
(264,'2024-11-28',15,1,'20:00:00.000000','18:00:00.000000'),
(265,'2024-11-28',22,1,'20:00:00.000000','18:00:00.000000'),
(266,'2024-11-28',26,1,'20:00:00.000000','18:00:00.000000'),
(267,'2024-11-29',10,1,'20:00:00.000000','18:00:00.000000'),
(268,'2024-11-29',12,1,'20:00:00.000000','18:00:00.000000'),
(269,'2024-11-29',13,1,'20:00:00.000000','18:00:00.000000'),
(270,'2024-11-29',14,1,'20:00:00.000000','18:00:00.000000'),
(271,'2024-11-29',15,1,'20:00:00.000000','18:00:00.000000'),
(272,'2024-11-29',22,1,'20:00:00.000000','18:00:00.000000'),
(273,'2024-11-29',26,1,'20:00:00.000000','18:00:00.000000'),
(274,'2024-12-02',10,1,'20:00:00.000000','18:00:00.000000'),
(275,'2024-12-02',12,1,'20:00:00.000000','18:00:00.000000'),
(276,'2024-12-02',14,1,'20:00:00.000000','18:00:00.000000'),
(277,'2024-12-02',15,1,'20:00:00.000000','18:00:00.000000'),
(278,'2024-12-02',22,1,'20:00:00.000000','18:00:00.000000'),
(279,'2024-12-02',25,1,'20:00:00.000000','18:00:00.000000'),
(280,'2024-12-02',26,1,'20:00:00.000000','18:00:00.000000'),
(281,'2024-12-02',27,1,'20:00:00.000000','18:00:00.000000'),
(282,'2024-12-04',12,1,'20:00:00.000000','18:00:00.000000'),
(283,'2024-12-04',14,1,'20:00:00.000000','18:00:00.000000'),
(284,'2024-12-04',15,1,'20:00:00.000000','18:00:00.000000'),
(285,'2024-12-04',22,1,'20:00:00.000000','18:00:00.000000'),
(286,'2024-12-04',25,1,'20:00:00.000000','18:00:00.000000'),
(287,'2024-12-04',26,1,'20:00:00.000000','18:00:00.000000'),
(288,'2024-12-04',27,1,'20:00:00.000000','18:00:00.000000'),
(289,'2024-12-06',10,1,'20:00:00.000000','18:00:00.000000'),
(290,'2024-12-06',12,1,'20:00:00.000000','18:00:00.000000'),
(291,'2024-12-06',14,1,'20:00:00.000000','18:00:00.000000'),
(292,'2024-12-06',15,1,'20:00:00.000000','18:00:00.000000'),
(293,'2024-12-06',25,1,'20:00:00.000000','18:00:00.000000'),
(294,'2024-12-06',26,1,'20:00:00.000000','18:00:00.000000'),
(295,'2024-12-06',27,1,'20:00:00.000000','18:00:00.000000'),
(296,'2024-12-06',28,1,'20:00:00.000000','18:00:00.000000'),
(297,'2024-12-09',10,1,'20:00:00.000000','18:00:00.000000'),
(298,'2024-12-09',12,1,'20:00:00.000000','18:00:00.000000'),
(299,'2024-12-09',14,1,'20:00:00.000000','18:00:00.000000'),
(300,'2024-12-09',15,1,'20:00:00.000000','18:00:00.000000'),
(301,'2024-12-09',22,1,'20:00:00.000000','18:00:00.000000'),
(302,'2024-12-09',25,1,'20:00:00.000000','18:00:00.000000'),
(303,'2024-12-09',26,1,'20:00:00.000000','18:00:00.000000'),
(304,'2024-12-09',27,1,'20:00:00.000000','18:00:00.000000'),
(305,'2024-12-09',28,1,'20:00:00.000000','18:00:00.000000'),
(306,'2024-12-11',10,1,'20:00:00.000000','18:00:00.000000'),
(307,'2024-12-11',12,1,'20:00:00.000000','18:00:00.000000'),
(308,'2024-12-11',14,1,'20:00:00.000000','18:00:00.000000'),
(309,'2024-12-11',15,1,'20:00:00.000000','18:00:00.000000'),
(310,'2024-12-11',22,1,'20:00:00.000000','18:00:00.000000'),
(311,'2024-12-11',25,1,'20:00:00.000000','18:00:00.000000'),
(312,'2024-12-11',26,1,'20:00:00.000000','18:00:00.000000'),
(313,'2024-12-11',27,1,'20:00:00.000000','18:00:00.000000'),
(314,'2024-12-11',28,1,'20:00:00.000000','18:00:00.000000'),
(315,'2024-12-13',10,1,'20:00:00.000000','18:00:00.000000'),
(316,'2024-12-13',12,1,'20:00:00.000000','18:00:00.000000'),
(317,'2024-12-13',14,1,'20:00:00.000000','18:00:00.000000'),
(318,'2024-12-13',15,1,'20:00:00.000000','18:00:00.000000'),
(319,'2024-12-13',22,1,'20:00:00.000000','18:00:00.000000'),
(320,'2024-12-13',25,1,'20:00:00.000000','18:00:00.000000'),
(321,'2024-12-13',26,1,'20:00:00.000000','18:00:00.000000'),
(322,'2024-12-13',27,1,'20:00:00.000000','18:00:00.000000'),
(323,'2024-12-13',28,1,'20:00:00.000000','18:00:00.000000'),
(324,'2024-12-16',10,1,'20:00:00.000000','18:00:00.000000'),
(325,'2024-12-16',12,1,'20:00:00.000000','18:00:00.000000'),
(326,'2024-12-16',14,1,'20:00:00.000000','18:00:00.000000'),
(327,'2024-12-16',15,1,'20:00:00.000000','18:00:00.000000'),
(328,'2024-12-16',22,1,'20:00:00.000000','18:00:00.000000'),
(329,'2024-12-16',25,1,'20:00:00.000000','18:00:00.000000'),
(330,'2024-12-16',26,1,'20:00:00.000000','18:00:00.000000'),
(331,'2024-12-16',27,1,'20:00:00.000000','18:00:00.000000'),
(332,'2024-12-16',28,1,'20:00:00.000000','18:00:00.000000'),
(333,'2024-12-18',10,1,'20:00:00.000000','18:00:00.000000'),
(334,'2024-12-18',12,1,'20:00:00.000000','18:00:00.000000'),
(335,'2024-12-18',14,1,'20:00:00.000000','18:00:00.000000'),
(336,'2024-12-18',15,1,'20:00:00.000000','18:00:00.000000'),
(337,'2024-12-18',22,1,'20:00:00.000000','18:00:00.000000'),
(338,'2024-12-18',25,1,'20:00:00.000000','18:00:00.000000'),
(339,'2024-12-18',26,1,'20:00:00.000000','18:00:00.000000'),
(340,'2024-12-18',27,1,'20:00:00.000000','18:00:00.000000'),
(341,'2024-12-18',28,1,'20:00:00.000000','18:00:00.000000'),
(342,'2024-12-20',10,1,'20:00:00.000000','18:00:00.000000'),
(343,'2024-12-20',12,1,'20:00:00.000000','18:00:00.000000'),
(344,'2024-12-20',14,1,'20:00:00.000000','18:00:00.000000'),
(345,'2024-12-20',15,1,'20:00:00.000000','18:00:00.000000'),
(346,'2024-12-20',22,1,'20:00:00.000000','18:00:00.000000'),
(347,'2024-12-20',25,1,'20:00:00.000000','18:00:00.000000'),
(348,'2024-12-20',26,1,'20:00:00.000000','18:00:00.000000'),
(349,'2024-12-20',27,1,'20:00:00.000000','18:00:00.000000'),
(350,'2024-12-20',28,1,'20:00:00.000000','18:00:00.000000'),
(351,'2024-12-23',10,1,'20:00:00.000000','18:00:00.000000'),
(352,'2024-12-23',12,1,'20:00:00.000000','18:00:00.000000'),
(353,'2024-12-23',15,1,'20:00:00.000000','18:00:00.000000'),
(354,'2024-12-23',22,1,'20:00:00.000000','18:00:00.000000'),
(355,'2024-12-23',25,1,'20:00:00.000000','18:00:00.000000'),
(356,'2024-12-23',26,1,'20:00:00.000000','18:00:00.000000'),
(357,'2024-12-23',27,1,'20:00:00.000000','18:00:00.000000'),
(358,'2024-12-23',28,1,'20:00:00.000000','18:00:00.000000'),
(359,'2024-12-23',29,1,'20:00:00.000000','18:00:00.000000'),
(360,'2024-12-27',10,1,'20:00:00.000000','18:00:00.000000'),
(361,'2024-12-27',12,1,'20:00:00.000000','18:00:00.000000'),
(362,'2024-12-27',22,1,'20:00:00.000000','18:00:00.000000'),
(363,'2024-12-27',25,1,'20:00:00.000000','18:00:00.000000'),
(364,'2024-12-27',27,1,'20:00:00.000000','18:00:00.000000'),
(365,'2024-12-27',28,1,'20:00:00.000000','18:00:00.000000'),
(366,'2024-12-27',29,1,'20:00:00.000000','18:00:00.000000'),
(367,'2024-12-30',10,1,'20:00:00.000000','18:00:00.000000'),
(368,'2024-12-30',12,1,'20:00:00.000000','18:00:00.000000'),
(369,'2024-12-30',15,1,'20:00:00.000000','18:00:00.000000'),
(370,'2024-12-30',22,1,'20:00:00.000000','18:00:00.000000'),
(371,'2024-12-30',25,1,'20:00:00.000000','18:00:00.000000'),
(372,'2024-12-30',26,1,'20:00:00.000000','18:00:00.000000'),
(373,'2024-12-30',27,1,'20:00:00.000000','18:00:00.000000'),
(374,'2024-12-30',28,1,'20:00:00.000000','18:00:00.000000'),
(375,'2024-12-30',29,1,'20:00:00.000000','18:00:00.000000'),
(376,'2025-01-03',10,1,'20:00:00.000000','18:00:00.000000'),
(377,'2025-01-03',12,1,'20:00:00.000000','18:00:00.000000'),
(378,'2025-01-03',15,1,'20:00:00.000000','18:00:00.000000'),
(379,'2025-01-03',22,1,'20:00:00.000000','18:00:00.000000'),
(380,'2025-01-03',25,1,'20:00:00.000000','18:00:00.000000'),
(381,'2025-01-03',26,1,'20:00:00.000000','18:00:00.000000'),
(382,'2025-01-03',27,1,'20:00:00.000000','18:00:00.000000'),
(383,'2025-01-03',28,1,'20:00:00.000000','18:00:00.000000'),
(384,'2025-01-03',29,1,'20:00:00.000000','18:00:00.000000'),
(385,'2025-01-06',10,1,'20:00:00.000000','18:00:00.000000'),
(386,'2025-01-06',22,1,'20:00:00.000000','18:00:00.000000'),
(387,'2025-01-06',25,1,'20:00:00.000000','18:00:00.000000'),
(388,'2025-01-06',26,1,'20:00:00.000000','18:00:00.000000'),
(389,'2025-01-06',27,1,'20:00:00.000000','18:00:00.000000'),
(390,'2025-01-06',28,1,'20:00:00.000000','18:00:00.000000'),
(391,'2025-01-06',29,1,'20:00:00.000000','18:00:00.000000'),
(392,'2025-01-08',10,1,'20:00:00.000000','18:00:00.000000'),
(393,'2025-01-08',12,1,'20:00:00.000000','18:00:00.000000'),
(394,'2025-01-08',15,1,'20:00:00.000000','18:00:00.000000'),
(395,'2025-01-08',22,1,'20:00:00.000000','18:00:00.000000'),
(396,'2025-01-08',25,1,'20:00:00.000000','18:00:00.000000'),
(397,'2025-01-08',26,1,'20:00:00.000000','18:00:00.000000'),
(398,'2025-01-08',27,1,'20:00:00.000000','18:00:00.000000'),
(399,'2025-01-08',28,1,'20:00:00.000000','18:00:00.000000'),
(400,'2025-01-08',29,1,'20:00:00.000000','18:00:00.000000'),
(401,'2025-01-10',10,1,'20:00:00.000000','18:00:00.000000'),
(402,'2025-01-10',12,1,'20:00:00.000000','18:00:00.000000'),
(403,'2025-01-10',15,1,'20:00:00.000000','18:00:00.000000'),
(404,'2025-01-10',22,1,'20:00:00.000000','18:00:00.000000'),
(405,'2025-01-10',26,1,'20:00:00.000000','18:00:00.000000'),
(406,'2025-01-10',27,1,'20:00:00.000000','18:00:00.000000'),
(407,'2025-01-10',28,1,'20:00:00.000000','18:00:00.000000'),
(408,'2025-01-10',29,1,'20:00:00.000000','18:00:00.000000'),
(409,'2025-01-10',30,1,'20:00:00.000000','18:00:00.000000'),
(410,'2025-01-13',10,1,'20:00:00.000000','18:00:00.000000'),
(411,'2025-01-13',12,1,'20:00:00.000000','18:00:00.000000'),
(412,'2025-01-13',15,1,'20:00:00.000000','18:00:00.000000'),
(413,'2025-01-13',22,1,'20:00:00.000000','18:00:00.000000'),
(414,'2025-01-13',26,1,'20:00:00.000000','18:00:00.000000'),
(415,'2025-01-13',27,1,'20:00:00.000000','18:00:00.000000'),
(416,'2025-01-13',28,1,'20:00:00.000000','18:00:00.000000'),
(417,'2025-01-13',29,1,'14:00:00.000000','12:00:00.000000'),
(418,'2025-01-13',30,1,'20:00:00.000000','18:00:00.000000'),
(419,'2025-01-14',12,1,'14:00:00.000000','12:00:00.000000'),
(420,'2025-01-14',22,1,'14:00:00.000000','12:00:00.000000'),
(421,'2025-01-14',26,1,'14:00:00.000000','12:00:00.000000'),
(422,'2025-01-14',27,1,'14:00:00.000000','12:00:00.000000'),
(423,'2025-01-14',28,1,'14:00:00.000000','12:00:00.000000'),
(424,'2025-01-14',29,1,'14:00:00.000000','12:00:00.000000'),
(425,'2025-01-14',30,1,'14:00:00.000000','12:00:00.000000'),
(426,'2025-01-14',31,1,'14:00:00.000000','12:00:00.000000'),
(427,'2025-01-15',10,1,'20:00:00.000000','18:00:00.000000'),
(428,'2025-01-15',12,1,'20:00:00.000000','18:00:00.000000'),
(429,'2025-01-15',22,1,'20:00:00.000000','18:00:00.000000'),
(430,'2025-01-15',26,1,'20:00:00.000000','18:00:00.000000'),
(431,'2025-01-15',27,1,'20:00:00.000000','18:00:00.000000'),
(432,'2025-01-15',28,1,'20:00:00.000000','18:00:00.000000'),
(433,'2025-01-15',29,1,'14:00:00.000000','12:00:00.000000'),
(434,'2025-01-15',30,1,'20:00:00.000000','18:00:00.000000'),
(435,'2025-01-16',12,1,'14:00:00.000000','12:00:00.000000'),
(436,'2025-01-16',22,1,'14:00:00.000000','12:00:00.000000'),
(437,'2025-01-16',26,1,'14:00:00.000000','12:00:00.000000'),
(438,'2025-01-16',27,1,'14:00:00.000000','12:00:00.000000'),
(439,'2025-01-16',28,1,'14:00:00.000000','12:00:00.000000'),
(440,'2025-01-16',30,1,'14:00:00.000000','12:00:00.000000'),
(441,'2025-01-17',10,1,'20:00:00.000000','18:00:00.000000'),
(442,'2025-01-17',12,1,'20:00:00.000000','18:00:00.000000'),
(443,'2025-01-17',22,1,'20:00:00.000000','18:00:00.000000'),
(444,'2025-01-17',26,1,'20:00:00.000000','18:00:00.000000'),
(445,'2025-01-17',27,1,'20:00:00.000000','18:00:00.000000'),
(446,'2025-01-17',28,1,'20:00:00.000000','18:00:00.000000'),
(447,'2025-01-17',30,1,'20:00:00.000000','18:00:00.000000'),
(461,'2025-01-21',12,1,'14:00:00.000000','12:00:00.000000'),
(462,'2025-01-21',22,1,'14:00:00.000000','12:00:00.000000'),
(463,'2025-01-21',26,1,'14:00:00.000000','12:00:00.000000'),
(464,'2025-01-21',27,1,'14:00:00.000000','12:00:00.000000'),
(465,'2025-01-21',28,1,'14:00:00.000000','12:00:00.000000'),
(466,'2025-01-21',29,1,'14:00:00.000000','12:00:00.000000'),
(467,'2025-01-21',30,1,'14:00:00.000000','12:00:00.000000'),
(476,'2025-01-23',12,1,'14:00:00.000000','12:00:00.000000'),
(477,'2025-01-23',15,1,'14:00:00.000000','12:00:00.000000'),
(478,'2025-01-23',22,1,'14:00:00.000000','12:00:00.000000'),
(479,'2025-01-23',25,1,'14:00:00.000000','12:00:00.000000'),
(480,'2025-01-23',26,1,'14:00:00.000000','12:00:00.000000'),
(481,'2025-01-23',27,1,'14:00:00.000000','12:00:00.000000'),
(482,'2025-01-23',28,1,'14:00:00.000000','12:00:00.000000'),
(483,'2025-01-23',29,1,'14:00:00.000000','12:00:00.000000'),
(484,'2025-01-23',30,1,'14:00:00.000000','12:00:00.000000'),
(494,'2025-01-27',22,1,'14:00:00.000000','12:00:00.000000'),
(495,'2025-01-27',27,1,'14:00:00.000000','12:00:00.000000'),
(496,'2025-01-27',28,1,'14:00:00.000000','12:00:00.000000'),
(497,'2025-01-27',29,1,'14:00:00.000000','12:00:00.000000'),
(498,'2025-01-31',12,1,'20:00:00.000000','18:00:00.000000'),
(499,'2025-01-31',15,1,'20:00:00.000000','18:00:00.000000'),
(500,'2025-01-31',22,1,'20:00:00.000000','18:00:00.000000'),
(501,'2025-01-31',25,1,'20:00:00.000000','18:00:00.000000'),
(502,'2025-01-31',26,1,'20:00:00.000000','18:00:00.000000'),
(503,'2025-01-31',28,1,'20:00:00.000000','18:00:00.000000'),
(504,'2025-01-31',29,1,'14:00:00.000000','12:00:00.000000'),
(508,'2025-01-20',10,1,'20:00:00.000000','18:00:00.000000'),
(509,'2025-01-20',12,1,'20:00:00.000000','18:00:00.000000'),
(510,'2025-01-20',22,1,'20:00:00.000000','18:00:00.000000'),
(511,'2025-01-20',26,1,'20:00:00.000000','18:00:00.000000'),
(512,'2025-01-20',27,1,'20:00:00.000000','18:00:00.000000'),
(513,'2025-01-20',28,1,'20:00:00.000000','18:00:00.000000'),
(514,'2025-01-20',30,1,'20:00:00.000000','18:00:00.000000'),
(515,'2025-01-22',10,1,'20:00:00.000000','18:00:00.000000'),
(516,'2025-01-22',15,1,'20:00:00.000000','18:00:00.000000'),
(517,'2025-01-22',22,1,'20:00:00.000000','18:00:00.000000'),
(518,'2025-01-22',25,1,'20:00:00.000000','18:00:00.000000'),
(519,'2025-01-22',26,1,'20:00:00.000000','18:00:00.000000'),
(520,'2025-01-22',27,1,'20:00:00.000000','18:00:00.000000'),
(521,'2025-01-22',29,1,'14:00:00.000000','12:00:00.000000'),
(522,'2025-01-22',30,1,'20:00:00.000000','18:00:00.000000'),
(523,'2025-01-24',12,1,'20:00:00.000000','18:00:00.000000'),
(524,'2025-01-24',15,1,'20:00:00.000000','18:00:00.000000'),
(525,'2025-01-24',22,1,'20:00:00.000000','18:00:00.000000'),
(526,'2025-01-24',25,1,'20:00:00.000000','18:00:00.000000'),
(527,'2025-01-24',26,1,'20:00:00.000000','18:00:00.000000'),
(528,'2025-01-24',27,1,'20:00:00.000000','18:00:00.000000'),
(529,'2025-01-24',28,1,'20:00:00.000000','18:00:00.000000'),
(530,'2025-01-24',29,1,'14:00:00.000000','12:00:00.000000'),
(531,'2025-01-24',30,1,'20:00:00.000000','18:00:00.000000'),
(532,'2025-01-31',30,1,'20:00:00.000000','18:00:00.000000'),
(533,'2025-02-03',10,1,'20:00:00.000000','18:00:00.000000'),
(534,'2025-02-03',12,1,'20:00:00.000000','18:00:00.000000'),
(535,'2025-02-03',15,1,'20:00:00.000000','18:00:00.000000'),
(536,'2025-02-03',25,1,'20:00:00.000000','18:00:00.000000'),
(537,'2025-02-03',26,1,'20:00:00.000000','18:00:00.000000'),
(538,'2025-02-03',28,1,'20:00:00.000000','18:00:00.000000'),
(539,'2025-02-03',29,1,'14:00:00.000000','12:00:00.000000'),
(540,'2025-02-03',30,1,'20:00:00.000000','18:00:00.000000'),
(541,'2025-02-03',33,1,'20:00:00.000000','18:00:00.000000'),
(542,'2025-02-03',34,1,'18:00:00.000000','16:00:00.000000'),
(543,'2025-02-04',12,1,'20:00:00.000000','18:00:00.000000'),
(544,'2025-02-04',15,1,'20:00:00.000000','18:00:00.000000'),
(545,'2025-02-04',25,1,'20:00:00.000000','18:00:00.000000'),
(546,'2025-02-04',26,1,'20:00:00.000000','18:00:00.000000'),
(547,'2025-02-04',28,1,'20:00:00.000000','18:00:00.000000'),
(548,'2025-02-04',29,1,'20:00:00.000000','18:00:00.000000'),
(549,'2025-02-04',30,1,'20:00:00.000000','18:00:00.000000'),
(550,'2025-02-04',33,1,'20:00:00.000000','18:00:00.000000'),
(551,'2025-02-04',34,1,'20:00:00.000000','18:00:00.000000'),
(552,'2025-02-05',10,1,'20:00:00.000000','18:00:00.000000'),
(553,'2025-02-05',12,1,'20:00:00.000000','18:00:00.000000'),
(554,'2025-02-05',15,1,'20:00:00.000000','18:00:00.000000'),
(555,'2025-02-05',25,1,'20:00:00.000000','18:00:00.000000'),
(556,'2025-02-05',26,1,'20:00:00.000000','18:00:00.000000'),
(557,'2025-02-05',27,1,'20:00:00.000000','18:00:00.000000'),
(558,'2025-02-05',28,1,'20:00:00.000000','18:00:00.000000'),
(559,'2025-02-05',29,1,'14:00:00.000000','12:00:00.000000'),
(560,'2025-02-05',30,1,'20:00:00.000000','18:00:00.000000'),
(561,'2025-02-05',34,1,'16:00:00.000000','14:00:00.000000'),
(562,'2025-02-06',12,1,'14:00:00.000000','12:00:00.000000'),
(563,'2025-02-06',25,1,'14:00:00.000000','12:00:00.000000'),
(564,'2025-02-06',26,1,'14:00:00.000000','12:00:00.000000'),
(565,'2025-02-06',27,1,'14:00:00.000000','12:00:00.000000'),
(566,'2025-02-06',28,1,'14:00:00.000000','12:00:00.000000'),
(567,'2025-02-06',29,1,'14:00:00.000000','12:00:00.000000'),
(568,'2025-02-06',30,1,'14:00:00.000000','12:00:00.000000'),
(569,'2025-02-06',33,1,'14:00:00.000000','12:00:00.000000'),
(570,'2025-02-06',34,1,'18:00:00.000000','16:00:00.000000'),
(571,'2025-02-07',10,1,'20:00:00.000000','18:00:00.000000'),
(572,'2025-02-07',12,1,'20:00:00.000000','18:00:00.000000'),
(573,'2025-02-07',25,1,'20:00:00.000000','18:00:00.000000'),
(574,'2025-02-07',26,1,'20:00:00.000000','18:00:00.000000'),
(575,'2025-02-07',27,1,'20:00:00.000000','18:00:00.000000'),
(576,'2025-02-07',28,1,'20:00:00.000000','18:00:00.000000'),
(577,'2025-02-07',29,1,'14:00:00.000000','12:00:00.000000'),
(578,'2025-02-07',30,1,'20:00:00.000000','18:00:00.000000'),
(579,'2025-02-07',33,1,'20:00:00.000000','18:00:00.000000'),
(580,'2025-02-07',34,1,'18:00:00.000000','16:00:00.000000'),
(581,'2025-02-10',10,1,'20:00:00.000000','18:00:00.000000'),
(582,'2025-02-10',12,1,'20:00:00.000000','18:00:00.000000'),
(583,'2025-02-10',15,1,'20:00:00.000000','18:00:00.000000'),
(584,'2025-02-10',22,1,'20:00:00.000000','18:00:00.000000'),
(585,'2025-02-10',26,1,'20:00:00.000000','18:00:00.000000'),
(586,'2025-02-10',27,1,'20:00:00.000000','18:00:00.000000'),
(587,'2025-02-10',28,1,'20:00:00.000000','18:00:00.000000'),
(588,'2025-02-10',29,1,'14:00:00.000000','12:00:00.000000'),
(589,'2025-02-10',30,1,'20:00:00.000000','18:00:00.000000'),
(590,'2025-02-10',33,1,'20:00:00.000000','18:00:00.000000'),
(591,'2025-02-10',34,1,'16:00:00.000000','14:00:00.000000'),
(592,'2025-02-11',12,1,'14:00:00.000000','12:00:00.000000'),
(593,'2025-02-11',15,1,'14:00:00.000000','12:00:00.000000'),
(594,'2025-02-11',22,1,'14:00:00.000000','12:00:00.000000'),
(595,'2025-02-11',25,1,'14:00:00.000000','12:00:00.000000'),
(596,'2025-02-11',26,1,'14:00:00.000000','12:00:00.000000'),
(597,'2025-02-11',27,1,'14:00:00.000000','12:00:00.000000'),
(598,'2025-02-11',28,1,'14:00:00.000000','12:00:00.000000'),
(599,'2025-02-11',29,1,'14:00:00.000000','12:00:00.000000'),
(600,'2025-02-11',30,1,'14:00:00.000000','12:00:00.000000'),
(601,'2025-02-11',33,1,'14:00:00.000000','12:00:00.000000'),
(602,'2025-02-11',34,1,'16:00:00.000000','14:00:00.000000'),
(603,'2025-02-12',10,1,'20:00:00.000000','18:00:00.000000'),
(604,'2025-02-12',12,1,'20:00:00.000000','18:00:00.000000'),
(605,'2025-02-12',15,1,'20:00:00.000000','18:00:00.000000'),
(606,'2025-02-12',22,1,'20:00:00.000000','18:00:00.000000'),
(607,'2025-02-12',25,1,'20:00:00.000000','18:00:00.000000'),
(608,'2025-02-12',26,1,'20:00:00.000000','18:00:00.000000'),
(609,'2025-02-12',27,1,'20:00:00.000000','18:00:00.000000'),
(610,'2025-02-12',28,1,'20:00:00.000000','18:00:00.000000'),
(611,'2025-02-12',29,1,'14:00:00.000000','12:00:00.000000'),
(612,'2025-02-12',30,1,'20:00:00.000000','18:00:00.000000'),
(613,'2025-02-12',34,1,'16:00:00.000000','14:00:00.000000'),
(614,'2025-02-13',12,1,'14:00:00.000000','12:00:00.000000'),
(615,'2025-02-13',15,1,'14:00:00.000000','12:00:00.000000'),
(616,'2025-02-13',22,1,'14:00:00.000000','12:00:00.000000'),
(617,'2025-02-13',25,1,'14:00:00.000000','12:00:00.000000'),
(618,'2025-02-13',26,1,'14:00:00.000000','12:00:00.000000'),
(619,'2025-02-13',27,1,'14:00:00.000000','12:00:00.000000'),
(620,'2025-02-13',28,1,'14:00:00.000000','12:00:00.000000'),
(621,'2025-02-13',29,1,'14:00:00.000000','12:00:00.000000'),
(622,'2025-02-13',30,1,'14:00:00.000000','12:00:00.000000'),
(623,'2025-02-13',33,1,'14:00:00.000000','12:00:00.000000'),
(624,'2025-02-13',34,1,'16:00:00.000000','14:00:00.000000'),
(625,'2025-02-14',10,1,'20:00:00.000000','18:00:00.000000'),
(626,'2025-02-14',12,1,'20:00:00.000000','18:00:00.000000'),
(627,'2025-02-14',15,1,'20:00:00.000000','18:00:00.000000'),
(628,'2025-02-14',22,1,'20:00:00.000000','18:00:00.000000'),
(629,'2025-02-14',25,1,'20:00:00.000000','18:00:00.000000'),
(630,'2025-02-14',26,1,'20:00:00.000000','18:00:00.000000'),
(631,'2025-02-14',27,1,'20:00:00.000000','18:00:00.000000'),
(632,'2025-02-14',28,1,'20:00:00.000000','18:00:00.000000'),
(633,'2025-02-14',29,1,'14:00:00.000000','12:00:00.000000'),
(634,'2025-02-14',33,1,'20:00:00.000000','18:00:00.000000'),
(635,'2025-02-14',34,1,'16:00:00.000000','14:00:00.000000'),
(636,'2025-02-17',10,1,'20:00:00.000000','18:00:00.000000'),
(637,'2025-02-17',12,1,'20:00:00.000000','18:00:00.000000'),
(638,'2025-02-17',15,1,'20:00:00.000000','18:00:00.000000'),
(639,'2025-02-17',22,1,'20:00:00.000000','18:00:00.000000'),
(640,'2025-02-17',25,1,'20:00:00.000000','18:00:00.000000'),
(641,'2025-02-17',26,1,'20:00:00.000000','18:00:00.000000'),
(642,'2025-02-17',27,1,'20:00:00.000000','18:00:00.000000'),
(643,'2025-02-17',29,1,'14:00:00.000000','12:00:00.000000'),
(644,'2025-02-17',30,1,'20:00:00.000000','18:00:00.000000'),
(645,'2025-02-17',33,1,'20:00:00.000000','18:00:00.000000'),
(646,'2025-02-17',34,1,'16:30:00.000000','14:30:00.000000'),
(647,'2025-02-18',12,1,'14:00:00.000000','12:00:00.000000'),
(648,'2025-02-18',15,1,'14:00:00.000000','12:00:00.000000'),
(649,'2025-02-18',22,1,'14:00:00.000000','12:00:00.000000'),
(650,'2025-02-18',25,1,'14:00:00.000000','12:00:00.000000'),
(651,'2025-02-18',26,1,'14:00:00.000000','12:00:00.000000'),
(652,'2025-02-18',27,1,'14:00:00.000000','12:00:00.000000'),
(653,'2025-02-18',29,1,'14:00:00.000000','12:00:00.000000'),
(654,'2025-02-18',30,1,'14:00:00.000000','12:00:00.000000'),
(655,'2025-02-18',33,1,'14:00:00.000000','12:00:00.000000'),
(656,'2025-02-19',10,1,'20:00:00.000000','18:00:00.000000'),
(657,'2025-02-19',12,1,'20:00:00.000000','18:00:00.000000'),
(658,'2025-02-19',15,1,'20:00:00.000000','18:00:00.000000'),
(659,'2025-02-19',22,1,'20:00:00.000000','18:00:00.000000'),
(660,'2025-02-19',25,1,'20:00:00.000000','18:00:00.000000'),
(661,'2025-02-19',26,1,'20:00:00.000000','18:00:00.000000'),
(662,'2025-02-19',28,1,'20:00:00.000000','18:00:00.000000'),
(663,'2025-02-19',30,1,'20:00:00.000000','18:00:00.000000'),
(664,'2025-02-19',33,1,'20:00:00.000000','18:00:00.000000'),
(665,'2025-02-19',34,1,'16:00:00.000000','14:00:00.000000'),
(666,'2025-02-20',12,1,'14:00:00.000000','12:00:00.000000'),
(667,'2025-02-20',15,1,'14:00:00.000000','12:00:00.000000'),
(668,'2025-02-20',22,1,'14:00:00.000000','12:00:00.000000'),
(669,'2025-02-20',25,1,'14:00:00.000000','12:00:00.000000'),
(670,'2025-02-20',26,1,'14:00:00.000000','12:00:00.000000'),
(671,'2025-02-20',27,1,'14:00:00.000000','12:00:00.000000'),
(672,'2025-02-20',28,1,'14:00:00.000000','12:00:00.000000'),
(673,'2025-02-20',29,1,'14:00:00.000000','12:00:00.000000'),
(674,'2025-02-20',30,1,'14:00:00.000000','12:00:00.000000'),
(675,'2025-02-20',33,1,'14:00:00.000000','12:00:00.000000'),
(676,'2025-02-20',34,1,'16:00:00.000000','14:00:00.000000'),
(687,'2025-02-21',10,1,'20:00:00.000000','18:00:00.000000'),
(688,'2025-02-21',12,1,'20:00:00.000000','18:00:00.000000'),
(689,'2025-02-21',25,1,'20:00:00.000000','18:00:00.000000'),
(690,'2025-02-21',26,1,'20:00:00.000000','18:00:00.000000'),
(691,'2025-02-21',27,1,'20:00:00.000000','18:00:00.000000'),
(692,'2025-02-21',28,1,'20:00:00.000000','18:00:00.000000'),
(693,'2025-02-21',29,1,'14:00:00.000000','12:00:00.000000'),
(694,'2025-02-21',30,1,'20:00:00.000000','18:00:00.000000'),
(695,'2025-02-21',33,1,'20:00:00.000000','18:00:00.000000'),
(696,'2025-02-21',34,1,'16:00:00.000000','14:00:00.000000'),
(697,'2025-02-26',10,1,'20:00:00.000000','18:00:00.000000'),
(698,'2025-02-26',12,1,'20:00:00.000000','18:00:00.000000'),
(699,'2025-02-26',22,1,'20:00:00.000000','18:00:00.000000'),
(700,'2025-02-26',25,1,'20:00:00.000000','18:00:00.000000'),
(701,'2025-02-26',28,1,'20:00:00.000000','18:00:00.000000'),
(702,'2025-02-28',10,1,'20:00:00.000000','18:00:00.000000'),
(703,'2025-02-28',15,1,'20:00:00.000000','18:00:00.000000'),
(704,'2025-02-28',22,1,'20:00:00.000000','18:00:00.000000'),
(705,'2025-02-28',25,1,'20:00:00.000000','18:00:00.000000'),
(706,'2025-02-28',28,1,'20:00:00.000000','18:00:00.000000'),
(707,'2025-02-28',30,1,'20:00:00.000000','18:00:00.000000'),
(708,'2025-03-03',10,1,'20:00:00.000000','18:00:00.000000'),
(709,'2025-03-03',12,1,'20:00:00.000000','18:00:00.000000'),
(710,'2025-03-03',15,1,'20:00:00.000000','18:00:00.000000'),
(711,'2025-03-03',28,1,'22:00:00.000000','18:00:00.000000'),
(712,'2025-03-03',35,1,'20:00:00.000000','18:00:00.000000'),
(713,'2025-03-05',10,1,'20:00:00.000000','18:00:00.000000'),
(714,'2025-03-05',12,1,'20:00:00.000000','18:00:00.000000'),
(715,'2025-03-05',28,1,'20:00:00.000000','18:00:00.000000'),
(716,'2025-03-05',35,1,'20:00:00.000000','18:00:00.000000'),
(717,'2025-03-05',36,1,'20:00:00.000000','18:00:00.000000'),
(718,'2025-03-07',10,1,'20:00:00.000000','18:00:00.000000'),
(719,'2025-03-07',12,1,'20:00:00.000000','18:00:00.000000'),
(720,'2025-03-07',28,1,'22:00:00.000000','18:00:00.000000'),
(721,'2025-03-07',36,1,'20:00:00.000000','18:00:00.000000'),
(722,'2025-03-07',37,1,'20:00:00.000000','18:00:00.000000'),
(723,'2025-03-10',10,1,'20:00:00.000000','18:00:00.000000'),
(724,'2025-03-10',12,1,'20:00:00.000000','18:00:00.000000'),
(725,'2025-03-10',15,1,'20:00:00.000000','18:00:00.000000'),
(726,'2025-03-10',35,1,'20:00:00.000000','18:00:00.000000'),
(727,'2025-03-10',37,1,'20:00:00.000000','18:00:00.000000'),
(728,'2025-03-10',38,1,'20:00:00.000000','18:00:00.000000'),
(729,'2025-03-10',39,1,'20:00:00.000000','18:00:00.000000'),
(730,'2025-03-12',12,1,'20:00:00.000000','18:00:00.000000'),
(731,'2025-03-12',15,1,'20:00:00.000000','18:00:00.000000'),
(732,'2025-03-12',28,1,'20:00:00.000000','18:00:00.000000'),
(733,'2025-03-12',36,1,'20:00:00.000000','18:00:00.000000'),
(734,'2025-03-12',37,1,'20:00:00.000000','18:00:00.000000'),
(735,'2025-03-12',38,1,'20:00:00.000000','18:00:00.000000'),
(736,'2025-03-12',39,1,'20:00:00.000000','18:00:00.000000'),
(737,'2025-03-14',10,1,'20:00:00.000000','18:00:00.000000'),
(738,'2025-03-14',28,1,'20:00:00.000000','18:00:00.000000'),
(739,'2025-03-14',35,1,'20:00:00.000000','18:00:00.000000'),
(740,'2025-03-14',36,1,'20:00:00.000000','18:00:00.000000'),
(741,'2025-03-14',37,1,'20:00:00.000000','18:00:00.000000'),
(742,'2025-03-14',38,1,'20:00:00.000000','18:00:00.000000'),
(743,'2025-03-14',39,1,'20:00:00.000000','18:00:00.000000'),
(744,'2025-03-17',10,1,'20:00:00.000000','18:00:00.000000'),
(745,'2025-03-17',12,1,'20:00:00.000000','18:00:00.000000'),
(746,'2025-03-17',15,1,'20:00:00.000000','18:00:00.000000'),
(747,'2025-03-17',37,1,'20:00:00.000000','18:00:00.000000'),
(748,'2025-03-17',38,1,'20:00:00.000000','18:00:00.000000'),
(749,'2025-03-17',39,1,'20:00:00.000000','18:00:00.000000'),
(750,'2025-03-19',10,1,'20:00:00.000000','18:00:00.000000'),
(751,'2025-03-19',12,1,'20:00:00.000000','18:00:00.000000'),
(752,'2025-03-19',15,1,'20:00:00.000000','18:00:00.000000'),
(753,'2025-03-19',28,1,'20:00:00.000000','18:00:00.000000'),
(754,'2025-03-19',36,1,'20:00:00.000000','18:00:00.000000'),
(755,'2025-03-19',37,1,'20:00:00.000000','18:00:00.000000'),
(756,'2025-03-19',38,1,'20:00:00.000000','18:00:00.000000'),
(757,'2025-03-19',39,1,'20:00:00.000000','18:00:00.000000'),
(758,'2025-03-19',40,1,'20:00:00.000000','18:00:00.000000'),
(759,'2025-03-21',12,1,'20:00:00.000000','18:00:00.000000'),
(760,'2025-03-21',28,1,'20:00:00.000000','18:00:00.000000'),
(761,'2025-03-21',36,1,'20:00:00.000000','18:00:00.000000'),
(762,'2025-03-21',37,1,'20:00:00.000000','18:00:00.000000'),
(763,'2025-03-21',38,1,'20:00:00.000000','18:00:00.000000'),
(764,'2025-03-21',39,1,'20:00:00.000000','18:00:00.000000'),
(765,'2025-03-21',40,1,'20:00:00.000000','18:00:00.000000'),
(766,'2025-03-24',10,1,'20:00:00.000000','18:00:00.000000'),
(767,'2025-03-24',12,1,'20:00:00.000000','18:00:00.000000'),
(768,'2025-03-24',15,1,'20:00:00.000000','18:00:00.000000'),
(769,'2025-03-24',28,1,'20:00:00.000000','18:00:00.000000'),
(770,'2025-03-24',37,1,'20:00:00.000000','18:00:00.000000'),
(771,'2025-03-24',38,1,'20:00:00.000000','18:00:00.000000'),
(772,'2025-03-24',39,1,'20:00:00.000000','18:00:00.000000'),
(773,'2025-03-24',40,1,'20:00:00.000000','18:00:00.000000'),
(774,'2025-03-26',10,1,'20:00:00.000000','18:00:00.000000'),
(775,'2025-03-26',12,1,'20:00:00.000000','18:00:00.000000'),
(776,'2025-03-26',15,1,'20:00:00.000000','18:00:00.000000'),
(777,'2025-03-26',28,1,'20:00:00.000000','18:00:00.000000'),
(778,'2025-03-26',36,1,'20:00:00.000000','18:00:00.000000'),
(779,'2025-03-26',37,1,'20:00:00.000000','18:00:00.000000'),
(780,'2025-03-26',38,1,'20:00:00.000000','18:00:00.000000'),
(781,'2025-03-26',39,1,'20:00:00.000000','18:00:00.000000'),
(782,'2025-03-28',10,1,'20:00:00.000000','18:00:00.000000'),
(783,'2025-03-28',12,1,'20:00:00.000000','18:00:00.000000'),
(785,'2025-03-28',36,1,'20:00:00.000000','18:00:00.000000'),
(786,'2025-03-28',37,1,'20:00:00.000000','18:00:00.000000'),
(787,'2025-03-28',38,1,'20:00:00.000000','18:00:00.000000'),
(788,'2025-03-28',39,1,'20:00:00.000000','18:00:00.000000'),
(789,'2025-03-28',40,1,'20:00:00.000000','18:00:00.000000'),
(790,'2025-03-31',10,1,'20:00:00.000000','18:00:00.000000'),
(791,'2025-03-31',12,1,'20:00:00.000000','18:00:00.000000'),
(792,'2025-03-31',15,1,'20:00:00.000000','18:00:00.000000'),
(793,'2025-03-31',37,1,'20:00:00.000000','18:00:00.000000'),
(794,'2025-03-31',38,1,'20:00:00.000000','18:00:00.000000'),
(795,'2025-03-31',39,1,'20:00:00.000000','18:00:00.000000'),
(796,'2025-03-31',40,1,'20:00:00.000000','18:00:00.000000'),
(797,'2025-04-02',10,1,'20:00:00.000000','18:00:00.000000'),
(798,'2025-04-02',12,1,'20:00:00.000000','18:00:00.000000'),
(799,'2025-04-02',15,1,'20:00:00.000000','18:00:00.000000'),
(800,'2025-04-02',28,1,'20:00:00.000000','18:00:00.000000'),
(801,'2025-04-02',36,1,'20:00:00.000000','18:00:00.000000'),
(802,'2025-04-02',37,1,'20:00:00.000000','18:00:00.000000'),
(803,'2025-04-02',38,1,'20:00:00.000000','18:00:00.000000'),
(804,'2025-04-02',40,1,'20:00:00.000000','18:00:00.000000'),
(805,'2025-04-04',10,1,'20:00:00.000000','18:00:00.000000'),
(806,'2025-04-04',12,1,'20:00:00.000000','18:00:00.000000'),
(807,'2025-04-04',28,1,'20:00:00.000000','18:00:00.000000'),
(808,'2025-04-04',37,1,'20:00:00.000000','18:00:00.000000'),
(809,'2025-04-04',39,1,'20:00:00.000000','18:00:00.000000'),
(810,'2025-04-04',40,1,'20:00:00.000000','18:00:00.000000'),
(811,'2025-04-07',10,1,'20:00:00.000000','18:00:00.000000'),
(812,'2025-04-07',12,1,'20:00:00.000000','18:00:00.000000'),
(813,'2025-04-07',15,1,'20:00:00.000000','18:00:00.000000'),
(814,'2025-04-07',37,1,'20:00:00.000000','18:00:00.000000'),
(815,'2025-04-07',38,1,'20:00:00.000000','18:00:00.000000'),
(816,'2025-04-07',39,1,'20:00:00.000000','18:00:00.000000'),
(817,'2025-04-07',40,1,'20:00:00.000000','18:00:00.000000'),
(818,'2025-04-09',10,1,'20:00:00.000000','18:00:00.000000'),
(819,'2025-04-09',12,1,'20:00:00.000000','18:00:00.000000'),
(820,'2025-04-09',15,1,'20:00:00.000000','18:00:00.000000'),
(821,'2025-04-09',28,1,'20:00:00.000000','18:00:00.000000'),
(822,'2025-04-09',36,1,'20:00:00.000000','18:00:00.000000'),
(823,'2025-04-09',37,1,'20:00:00.000000','18:00:00.000000'),
(824,'2025-04-09',38,1,'20:00:00.000000','18:00:00.000000'),
(825,'2025-04-09',39,1,'20:00:00.000000','18:00:00.000000'),
(826,'2025-04-09',40,1,'20:00:00.000000','18:00:00.000000'),
(827,'2025-04-11',10,1,'20:00:00.000000','18:00:00.000000'),
(828,'2025-04-11',12,1,'20:00:00.000000','18:00:00.000000'),
(829,'2025-04-11',28,1,'20:00:00.000000','18:00:00.000000'),
(830,'2025-04-11',36,1,'20:00:00.000000','18:00:00.000000'),
(831,'2025-04-11',37,1,'20:00:00.000000','18:00:00.000000'),
(832,'2025-04-11',38,1,'20:00:00.000000','18:00:00.000000'),
(833,'2025-04-11',39,1,'20:00:00.000000','18:00:00.000000'),
(834,'2025-04-11',40,1,'20:00:00.000000','18:00:00.000000'),
(835,'2025-04-14',10,1,'20:00:00.000000','18:00:00.000000'),
(836,'2025-04-14',12,1,'20:00:00.000000','18:00:00.000000'),
(837,'2025-04-14',15,1,'20:00:00.000000','18:00:00.000000'),
(838,'2025-04-14',37,1,'20:00:00.000000','18:00:00.000000'),
(839,'2025-04-14',38,1,'20:00:00.000000','18:00:00.000000'),
(840,'2025-04-14',39,1,'20:00:00.000000','18:00:00.000000'),
(841,'2025-04-14',40,1,'20:00:00.000000','18:00:00.000000'),
(842,'2025-04-16',10,1,'20:00:00.000000','18:00:00.000000'),
(843,'2025-04-16',12,1,'20:00:00.000000','18:00:00.000000'),
(844,'2025-04-16',15,1,'20:00:00.000000','18:00:00.000000'),
(845,'2025-04-16',36,1,'20:00:00.000000','18:00:00.000000'),
(846,'2025-04-16',38,1,'20:00:00.000000','18:00:00.000000'),
(847,'2025-04-16',39,1,'20:00:00.000000','18:00:00.000000'),
(848,'2025-04-16',40,1,'20:00:00.000000','18:00:00.000000'),
(849,'2025-04-18',10,1,'20:00:00.000000','18:00:00.000000'),
(850,'2025-04-18',12,1,'20:00:00.000000','18:00:00.000000'),
(851,'2025-04-18',28,1,'20:00:00.000000','18:00:00.000000'),
(852,'2025-04-18',36,1,'20:00:00.000000','18:00:00.000000'),
(853,'2025-04-18',37,1,'20:00:00.000000','18:00:00.000000'),
(854,'2025-04-18',38,1,'20:00:00.000000','18:00:00.000000'),
(855,'2025-04-18',39,1,'20:00:00.000000','18:00:00.000000'),
(856,'2025-04-18',40,1,'20:00:00.000000','18:00:00.000000'),
(857,'2025-04-21',10,1,'20:00:00.000000','18:00:00.000000'),
(858,'2025-04-21',12,1,'20:00:00.000000','18:00:00.000000'),
(859,'2025-04-21',15,1,'20:00:00.000000','18:00:00.000000'),
(860,'2025-04-21',28,1,'22:00:00.000000','18:00:00.000000'),
(861,'2025-04-21',39,1,'20:00:00.000000','18:00:00.000000'),
(862,'2025-04-21',40,1,'20:00:00.000000','18:00:00.000000'),
(863,'2025-04-23',10,1,'20:00:00.000000','18:00:00.000000'),
(864,'2025-04-23',12,1,'20:00:00.000000','18:00:00.000000'),
(865,'2025-04-23',15,1,'20:00:00.000000','18:00:00.000000'),
(866,'2025-04-23',28,1,'20:00:00.000000','18:00:00.000000'),
(867,'2025-04-23',36,1,'20:00:00.000000','18:00:00.000000'),
(868,'2025-04-23',38,1,'20:00:00.000000','18:00:00.000000'),
(869,'2025-04-23',39,1,'20:00:00.000000','18:00:00.000000'),
(870,'2025-04-23',40,1,'20:00:00.000000','18:00:00.000000'),
(871,'2025-04-25',10,1,'20:00:00.000000','18:00:00.000000'),
(872,'2025-04-25',12,1,'20:00:00.000000','18:00:00.000000'),
(873,'2025-04-25',28,1,'20:00:00.000000','18:00:00.000000'),
(874,'2025-04-25',36,1,'20:00:00.000000','18:00:00.000000'),
(875,'2025-04-25',37,1,'20:00:00.000000','18:00:00.000000'),
(876,'2025-04-25',38,1,'20:00:00.000000','18:00:00.000000'),
(877,'2025-04-25',39,1,'20:00:00.000000','18:00:00.000000'),
(878,'2025-04-25',40,1,'20:00:00.000000','18:00:00.000000'),
(879,'2025-04-28',10,1,'20:00:00.000000','18:00:00.000000'),
(880,'2025-04-28',12,1,'20:00:00.000000','18:00:00.000000'),
(881,'2025-04-28',15,1,'20:00:00.000000','18:00:00.000000'),
(882,'2025-04-28',37,1,'20:00:00.000000','18:00:00.000000'),
(883,'2025-04-28',38,1,'20:00:00.000000','18:00:00.000000'),
(884,'2025-04-28',39,1,'20:00:00.000000','18:00:00.000000'),
(885,'2025-04-28',40,1,'20:00:00.000000','18:00:00.000000'),
(886,'2025-04-30',10,1,'20:00:00.000000','18:00:00.000000'),
(887,'2025-04-30',15,1,'20:00:00.000000','18:00:00.000000'),
(888,'2025-04-30',28,1,'20:00:00.000000','18:00:00.000000'),
(889,'2025-04-30',38,1,'20:00:00.000000','18:00:00.000000'),
(890,'2025-04-30',39,1,'20:00:00.000000','18:00:00.000000'),
(891,'2025-04-30',40,1,'20:00:00.000000','18:00:00.000000'),
(892,'2025-05-02',10,1,'20:00:00.000000','18:00:00.000000'),
(893,'2025-05-02',12,1,'20:00:00.000000','18:00:00.000000'),
(894,'2025-05-02',28,1,'20:00:00.000000','18:00:00.000000'),
(895,'2025-05-02',36,1,'20:00:00.000000','18:00:00.000000'),
(896,'2025-05-02',37,1,'20:00:00.000000','18:00:00.000000'),
(897,'2025-05-02',38,1,'20:00:00.000000','18:00:00.000000'),
(898,'2025-05-02',39,1,'20:00:00.000000','18:00:00.000000'),
(899,'2025-05-02',40,1,'20:00:00.000000','18:00:00.000000'),
(900,'2025-05-02',41,1,'20:00:00.000000','18:00:00.000000'),
(901,'2025-05-07',10,1,'20:00:00.000000','18:00:00.000000'),
(902,'2025-05-07',12,1,'20:00:00.000000','18:00:00.000000'),
(903,'2025-05-07',28,1,'20:00:00.000000','18:00:00.000000'),
(904,'2025-05-07',36,1,'20:00:00.000000','18:00:00.000000'),
(905,'2025-05-07',37,1,'20:00:00.000000','18:00:00.000000'),
(906,'2025-05-07',38,1,'20:00:00.000000','18:00:00.000000'),
(907,'2025-05-07',39,1,'20:00:00.000000','18:00:00.000000'),
(908,'2025-05-07',40,1,'20:00:00.000000','18:00:00.000000'),
(909,'2025-05-07',41,1,'20:00:00.000000','18:00:00.000000'),
(910,'2025-05-09',10,1,'20:00:00.000000','18:00:00.000000'),
(911,'2025-05-09',12,1,'20:00:00.000000','18:00:00.000000'),
(912,'2025-05-09',28,1,'20:00:00.000000','18:00:00.000000'),
(913,'2025-05-09',36,1,'20:00:00.000000','18:00:00.000000'),
(914,'2025-05-09',37,1,'20:00:00.000000','18:00:00.000000'),
(915,'2025-05-09',38,1,'20:00:00.000000','18:00:00.000000'),
(916,'2025-05-09',41,1,'20:00:00.000000','18:00:00.000000'),
(917,'2025-05-12',10,1,'20:00:00.000000','18:00:00.000000'),
(918,'2025-05-12',12,1,'20:00:00.000000','18:00:00.000000'),
(919,'2025-05-12',28,1,'20:00:00.000000','18:00:00.000000'),
(920,'2025-05-12',37,1,'20:00:00.000000','18:00:00.000000'),
(921,'2025-05-12',38,1,'20:00:00.000000','18:00:00.000000'),
(922,'2025-05-12',39,1,'20:00:00.000000','18:00:00.000000'),
(923,'2025-05-12',40,1,'20:00:00.000000','18:00:00.000000'),
(924,'2025-05-12',41,1,'20:00:00.000000','18:00:00.000000'),
(925,'2025-05-14',10,1,'20:00:00.000000','18:00:00.000000'),
(926,'2025-05-14',12,1,'20:00:00.000000','18:00:00.000000'),
(927,'2025-05-14',28,1,'20:00:00.000000','18:00:00.000000'),
(928,'2025-05-14',36,1,'20:00:00.000000','18:00:00.000000'),
(929,'2025-05-14',37,1,'20:00:00.000000','18:00:00.000000'),
(930,'2025-05-14',38,1,'20:00:00.000000','18:00:00.000000'),
(931,'2025-05-14',39,1,'20:00:00.000000','18:00:00.000000'),
(932,'2025-05-14',40,1,'20:00:00.000000','18:00:00.000000'),
(933,'2025-05-14',41,1,'20:00:00.000000','18:00:00.000000'),
(934,'2025-05-16',12,1,'20:00:00.000000','18:00:00.000000'),
(935,'2025-05-16',28,1,'20:00:00.000000','18:00:00.000000'),
(936,'2025-05-16',37,1,'20:00:00.000000','18:00:00.000000'),
(937,'2025-05-16',38,1,'20:00:00.000000','18:00:00.000000'),
(938,'2025-05-16',39,1,'20:00:00.000000','18:00:00.000000'),
(939,'2025-05-16',40,1,'20:00:00.000000','18:00:00.000000'),
(940,'2025-05-16',41,1,'20:00:00.000000','18:00:00.000000'),
(941,'2025-05-19',10,1,'20:00:00.000000','18:00:00.000000'),
(942,'2025-05-19',12,1,'20:00:00.000000','18:00:00.000000'),
(943,'2025-05-19',28,1,'20:00:00.000000','18:00:00.000000'),
(944,'2025-05-19',37,1,'20:00:00.000000','18:00:00.000000'),
(945,'2025-05-19',38,1,'20:00:00.000000','18:00:00.000000'),
(946,'2025-05-19',39,1,'20:00:00.000000','18:00:00.000000'),
(947,'2025-05-19',40,1,'20:00:00.000000','18:00:00.000000'),
(948,'2025-05-21',10,1,'20:00:00.000000','18:00:00.000000'),
(949,'2025-05-21',12,1,'20:00:00.000000','18:00:00.000000'),
(950,'2025-05-21',28,1,'20:00:00.000000','18:00:00.000000'),
(951,'2025-05-21',36,1,'20:00:00.000000','18:00:00.000000'),
(952,'2025-05-21',37,1,'20:00:00.000000','18:00:00.000000'),
(953,'2025-05-21',38,1,'20:00:00.000000','18:00:00.000000'),
(954,'2025-05-21',39,1,'20:00:00.000000','18:00:00.000000'),
(955,'2025-05-21',40,1,'20:00:00.000000','18:00:00.000000'),
(956,'2025-05-21',41,1,'20:00:00.000000','18:00:00.000000'),
(957,'2025-05-23',10,1,'20:00:00.000000','18:00:00.000000'),
(958,'2025-05-23',12,1,'20:00:00.000000','18:00:00.000000'),
(959,'2025-05-23',28,1,'20:00:00.000000','18:00:00.000000'),
(960,'2025-05-23',36,1,'20:00:00.000000','18:00:00.000000'),
(961,'2025-05-23',37,1,'20:00:00.000000','18:00:00.000000'),
(962,'2025-05-23',39,1,'20:00:00.000000','18:00:00.000000'),
(963,'2025-05-23',40,1,'20:00:00.000000','18:00:00.000000'),
(964,'2025-05-23',41,1,'20:00:00.000000','18:00:00.000000'),
(965,'2025-05-26',10,1,'20:00:00.000000','18:00:00.000000'),
(966,'2025-05-26',12,1,'20:00:00.000000','18:00:00.000000'),
(967,'2025-05-26',37,1,'20:00:00.000000','18:00:00.000000'),
(968,'2025-05-26',38,1,'20:00:00.000000','18:00:00.000000'),
(969,'2025-05-26',39,1,'20:00:00.000000','18:00:00.000000'),
(970,'2025-05-26',40,1,'20:00:00.000000','18:00:00.000000'),
(971,'2025-05-26',41,1,'20:00:00.000000','18:00:00.000000'),
(972,'2025-05-28',10,1,'20:00:00.000000','18:00:00.000000'),
(973,'2025-05-28',12,1,'20:00:00.000000','18:00:00.000000'),
(974,'2025-05-28',28,1,'20:00:00.000000','18:00:00.000000'),
(975,'2025-05-28',36,1,'20:00:00.000000','18:00:00.000000'),
(976,'2025-05-28',37,1,'20:00:00.000000','18:00:00.000000'),
(977,'2025-05-28',38,1,'20:00:00.000000','18:00:00.000000'),
(978,'2025-05-28',39,1,'20:00:00.000000','18:00:00.000000'),
(979,'2025-05-28',40,1,'20:00:00.000000','18:00:00.000000'),
(980,'2025-05-28',41,1,'20:00:00.000000','18:00:00.000000'),
(981,'2025-05-30',10,1,'20:00:00.000000','18:00:00.000000'),
(982,'2025-05-30',12,1,'20:00:00.000000','18:00:00.000000'),
(983,'2025-05-30',28,1,'20:00:00.000000','18:00:00.000000'),
(984,'2025-05-30',36,1,'20:00:00.000000','18:00:00.000000'),
(985,'2025-05-30',38,1,'20:00:00.000000','18:00:00.000000'),
(986,'2025-05-30',39,1,'20:00:00.000000','18:00:00.000000'),
(987,'2025-05-30',40,1,'20:00:00.000000','18:00:00.000000'),
(988,'2025-05-30',41,1,'20:00:00.000000','18:00:00.000000'),
(989,'2025-06-02',10,1,'20:00:00.000000','18:00:00.000000'),
(990,'2025-06-02',12,1,'20:00:00.000000','18:00:00.000000'),
(991,'2025-06-02',28,1,'20:00:00.000000','18:00:00.000000'),
(992,'2025-06-02',37,1,'20:00:00.000000','18:00:00.000000'),
(993,'2025-06-02',38,1,'20:00:00.000000','18:00:00.000000'),
(994,'2025-06-02',39,1,'20:00:00.000000','18:00:00.000000'),
(995,'2025-06-02',40,1,'20:00:00.000000','18:00:00.000000'),
(996,'2025-06-04',10,1,'20:00:00.000000','18:00:00.000000'),
(997,'2025-06-04',12,1,'20:00:00.000000','18:00:00.000000'),
(998,'2025-06-04',28,1,'20:00:00.000000','18:00:00.000000'),
(999,'2025-06-04',36,1,'20:00:00.000000','18:00:00.000000'),
(1000,'2025-06-04',37,1,'20:00:00.000000','18:00:00.000000'),
(1001,'2025-06-04',38,1,'20:00:00.000000','18:00:00.000000'),
(1002,'2025-06-04',41,1,'20:00:00.000000','18:00:00.000000'),
(1003,'2025-06-06',10,1,'20:00:00.000000','18:00:00.000000'),
(1004,'2025-06-06',12,1,'20:00:00.000000','18:00:00.000000'),
(1005,'2025-06-06',28,1,'20:00:00.000000','18:00:00.000000'),
(1006,'2025-06-06',36,1,'20:00:00.000000','18:00:00.000000'),
(1007,'2025-06-06',37,1,'20:00:00.000000','18:00:00.000000'),
(1008,'2025-06-09',10,1,'20:00:00.000000','18:00:00.000000'),
(1009,'2025-06-09',12,1,'20:00:00.000000','18:00:00.000000'),
(1010,'2025-06-09',37,1,'20:00:00.000000','18:00:00.000000'),
(1011,'2025-06-09',38,1,'20:00:00.000000','18:00:00.000000'),
(1012,'2025-06-09',39,1,'20:00:00.000000','18:00:00.000000'),
(1013,'2025-06-09',40,1,'20:00:00.000000','18:00:00.000000'),
(1014,'2025-06-09',41,1,'20:00:00.000000','18:00:00.000000'),
(1015,'2025-06-11',10,1,'20:00:00.000000','18:00:00.000000'),
(1016,'2025-06-11',12,1,'20:00:00.000000','18:00:00.000000'),
(1017,'2025-06-11',28,1,'20:00:00.000000','18:00:00.000000'),
(1018,'2025-06-11',36,1,'20:00:00.000000','18:00:00.000000'),
(1019,'2025-06-11',37,1,'20:00:00.000000','18:00:00.000000'),
(1020,'2025-06-11',39,1,'20:00:00.000000','18:00:00.000000'),
(1021,'2025-06-11',40,1,'20:00:00.000000','18:00:00.000000'),
(1022,'2025-06-11',41,1,'20:00:00.000000','18:00:00.000000'),
(1023,'2025-06-13',10,1,'20:00:00.000000','18:00:00.000000'),
(1024,'2025-06-13',12,1,'20:00:00.000000','18:00:00.000000'),
(1025,'2025-06-13',28,1,'20:00:00.000000','18:00:00.000000'),
(1026,'2025-06-13',36,1,'20:00:00.000000','18:00:00.000000'),
(1027,'2025-06-13',37,1,'20:00:00.000000','18:00:00.000000'),
(1028,'2025-06-13',38,1,'20:00:00.000000','18:00:00.000000'),
(1029,'2025-06-13',39,1,'20:00:00.000000','18:00:00.000000'),
(1030,'2025-06-13',40,1,'20:00:00.000000','18:00:00.000000'),
(1031,'2025-06-13',41,1,'20:00:00.000000','18:00:00.000000'),
(1032,'2025-06-16',10,1,'20:00:00.000000','18:00:00.000000'),
(1033,'2025-06-16',37,1,'20:00:00.000000','18:00:00.000000'),
(1034,'2025-06-16',38,1,'20:00:00.000000','18:00:00.000000'),
(1035,'2025-06-16',39,1,'20:00:00.000000','18:00:00.000000'),
(1036,'2025-06-16',40,1,'20:00:00.000000','18:00:00.000000'),
(1037,'2025-06-18',10,1,'20:00:00.000000','18:00:00.000000'),
(1038,'2025-06-18',12,1,'20:00:00.000000','18:00:00.000000'),
(1039,'2025-06-18',28,1,'20:00:00.000000','18:00:00.000000'),
(1040,'2025-06-18',36,1,'20:00:00.000000','18:00:00.000000'),
(1041,'2025-06-18',37,1,'20:00:00.000000','18:00:00.000000'),
(1042,'2025-06-18',38,1,'20:00:00.000000','18:00:00.000000'),
(1043,'2025-06-18',39,1,'20:00:00.000000','18:00:00.000000'),
(1044,'2025-06-18',40,1,'20:00:00.000000','18:00:00.000000'),
(1045,'2025-06-20',10,1,'20:00:00.000000','18:00:00.000000'),
(1046,'2025-06-20',12,1,'20:00:00.000000','18:00:00.000000'),
(1047,'2025-06-20',28,1,'20:00:00.000000','18:00:00.000000'),
(1048,'2025-06-20',36,1,'20:00:00.000000','18:00:00.000000'),
(1049,'2025-06-20',37,1,'20:00:00.000000','18:00:00.000000'),
(1050,'2025-06-20',38,1,'20:00:00.000000','18:00:00.000000'),
(1051,'2025-06-20',39,1,'20:00:00.000000','18:00:00.000000'),
(1052,'2025-06-20',40,1,'20:00:00.000000','18:00:00.000000'),
(1053,'2025-06-20',41,1,'20:00:00.000000','18:00:00.000000'),
(1054,'2025-06-23',10,1,'20:00:00.000000','18:00:00.000000'),
(1055,'2025-06-23',12,1,'20:00:00.000000','18:00:00.000000'),
(1056,'2025-06-23',28,1,'20:00:00.000000','18:00:00.000000'),
(1057,'2025-06-23',36,1,'20:00:00.000000','18:00:00.000000'),
(1058,'2025-06-23',38,1,'20:00:00.000000','18:00:00.000000'),
(1059,'2025-06-23',39,1,'20:00:00.000000','18:00:00.000000'),
(1060,'2025-06-23',40,1,'20:00:00.000000','18:00:00.000000'),
(1061,'2025-06-23',41,1,'20:00:00.000000','18:00:00.000000'),
(1062,'2025-06-25',10,1,'20:00:00.000000','18:00:00.000000'),
(1063,'2025-06-25',12,1,'20:00:00.000000','18:00:00.000000'),
(1064,'2025-06-25',38,1,'20:00:00.000000','18:00:00.000000'),
(1065,'2025-06-25',39,1,'20:00:00.000000','18:00:00.000000'),
(1066,'2025-06-25',40,1,'20:00:00.000000','18:00:00.000000'),
(1067,'2025-06-25',41,1,'20:00:00.000000','18:00:00.000000'),
(1068,'2025-06-27',10,1,'20:00:00.000000','18:00:00.000000'),
(1069,'2025-06-27',12,1,'20:00:00.000000','18:00:00.000000'),
(1070,'2025-06-27',28,1,'20:00:00.000000','18:00:00.000000'),
(1071,'2025-06-27',36,1,'20:00:00.000000','18:00:00.000000'),
(1072,'2025-06-27',38,1,'20:00:00.000000','18:00:00.000000'),
(1073,'2025-06-27',39,1,'20:00:00.000000','18:00:00.000000'),
(1074,'2025-06-27',40,1,'20:00:00.000000','18:00:00.000000'),
(1075,'2025-06-27',41,1,'20:00:00.000000','18:00:00.000000'),
(1076,'2025-06-30',10,1,'20:00:00.000000','18:00:00.000000'),
(1077,'2025-06-30',12,1,'20:00:00.000000','18:00:00.000000'),
(1078,'2025-06-30',38,1,'20:00:00.000000','18:00:00.000000'),
(1079,'2025-06-30',39,1,'20:00:00.000000','18:00:00.000000'),
(1080,'2025-06-30',40,1,'20:00:00.000000','18:00:00.000000'),
(1081,'2025-06-30',41,1,'20:00:00.000000','18:00:00.000000'),
(1082,'2025-07-02',10,1,'20:00:00.000000','18:00:00.000000'),
(1083,'2025-07-02',12,1,'20:00:00.000000','18:00:00.000000'),
(1084,'2025-07-02',36,1,'20:00:00.000000','18:00:00.000000'),
(1085,'2025-07-02',38,1,'20:00:00.000000','18:00:00.000000'),
(1086,'2025-07-02',39,1,'20:00:00.000000','18:00:00.000000'),
(1087,'2025-07-02',41,1,'20:00:00.000000','18:00:00.000000'),
(1088,'2025-07-04',10,1,'20:00:00.000000','18:00:00.000000'),
(1089,'2025-07-04',12,1,'20:00:00.000000','18:00:00.000000'),
(1090,'2025-07-04',27,1,'20:00:00.000000','18:00:00.000000'),
(1091,'2025-07-04',36,1,'20:00:00.000000','18:00:00.000000'),
(1092,'2025-07-04',39,1,'20:00:00.000000','18:00:00.000000'),
(1093,'2025-07-07',10,1,'20:00:00.000000','18:00:00.000000'),
(1094,'2025-07-07',12,1,'20:00:00.000000','18:00:00.000000'),
(1095,'2025-07-07',36,1,'20:00:00.000000','18:00:00.000000'),
(1096,'2025-07-07',38,1,'20:00:00.000000','18:00:00.000000'),
(1097,'2025-07-07',39,1,'20:00:00.000000','18:00:00.000000'),
(1098,'2025-07-07',41,1,'20:00:00.000000','18:00:00.000000'),
(1099,'2025-07-11',10,1,'20:00:00.000000','18:00:00.000000'),
(1100,'2025-07-11',12,1,'20:00:00.000000','18:00:00.000000'),
(1101,'2025-07-11',27,1,'20:00:00.000000','18:00:00.000000'),
(1102,'2025-07-11',36,1,'20:00:00.000000','18:00:00.000000'),
(1103,'2025-07-11',38,1,'20:00:00.000000','18:00:00.000000'),
(1104,'2025-07-11',39,1,'20:00:00.000000','18:00:00.000000'),
(1105,'2025-07-11',41,1,'20:00:00.000000','18:00:00.000000'),
(1106,'2025-07-14',10,1,'20:00:00.000000','18:00:00.000000'),
(1107,'2025-07-14',12,1,'20:00:00.000000','18:00:00.000000'),
(1108,'2025-07-14',36,1,'20:00:00.000000','18:00:00.000000'),
(1109,'2025-07-14',38,1,'20:00:00.000000','18:00:00.000000'),
(1110,'2025-07-14',39,1,'20:00:00.000000','18:00:00.000000'),
(1111,'2025-07-14',41,1,'20:00:00.000000','18:00:00.000000'),
(1112,'2025-07-16',10,1,'20:00:00.000000','18:00:00.000000'),
(1113,'2025-07-16',12,1,'20:00:00.000000','18:00:00.000000'),
(1114,'2025-07-16',27,1,'20:00:00.000000','18:00:00.000000'),
(1115,'2025-07-16',36,1,'20:00:00.000000','18:00:00.000000'),
(1116,'2025-07-16',38,1,'20:00:00.000000','18:00:00.000000'),
(1117,'2025-07-16',39,1,'20:00:00.000000','18:00:00.000000'),
(1118,'2025-07-16',41,1,'20:00:00.000000','18:00:00.000000'),
(1119,'2025-07-21',10,1,'20:00:00.000000','18:00:00.000000'),
(1120,'2025-07-21',12,1,'20:00:00.000000','18:00:00.000000'),
(1121,'2025-07-21',27,1,'20:00:00.000000','18:00:00.000000'),
(1122,'2025-07-21',36,1,'20:00:00.000000','18:00:00.000000'),
(1123,'2025-07-21',38,1,'20:00:00.000000','18:00:00.000000'),
(1124,'2025-07-21',39,1,'20:00:00.000000','18:00:00.000000'),
(1125,'2025-07-21',41,1,'20:00:00.000000','18:00:00.000000'),
(1126,'2025-07-09',10,1,'20:00:00.000000','18:00:00.000000'),
(1127,'2025-07-09',12,1,'20:00:00.000000','18:00:00.000000'),
(1128,'2025-07-09',27,1,'20:00:00.000000','18:00:00.000000'),
(1129,'2025-07-09',36,1,'20:00:00.000000','18:00:00.000000'),
(1130,'2025-07-09',38,1,'20:00:00.000000','18:00:00.000000'),
(1131,'2025-07-09',39,1,'20:00:00.000000','18:00:00.000000'),
(1132,'2025-07-09',41,1,'20:00:00.000000','18:00:00.000000'),
(1133,'2025-07-18',10,1,'20:00:00.000000','18:00:00.000000'),
(1134,'2025-07-18',12,1,'20:00:00.000000','18:00:00.000000'),
(1135,'2025-07-18',27,1,'20:00:00.000000','18:00:00.000000'),
(1136,'2025-07-18',36,1,'20:00:00.000000','18:00:00.000000'),
(1137,'2025-07-18',38,1,'20:00:00.000000','18:00:00.000000'),
(1138,'2025-07-18',39,1,'20:00:00.000000','18:00:00.000000'),
(1139,'2025-07-18',41,1,'20:00:00.000000','18:00:00.000000'),
(1140,'2025-07-23',10,1,'20:00:00.000000','18:00:00.000000'),
(1141,'2025-07-23',12,1,'20:00:00.000000','18:00:00.000000'),
(1142,'2025-07-23',27,1,'20:00:00.000000','18:00:00.000000'),
(1143,'2025-07-23',36,1,'20:00:00.000000','18:00:00.000000'),
(1144,'2025-07-23',38,1,'20:00:00.000000','18:00:00.000000'),
(1145,'2025-07-23',39,1,'20:00:00.000000','18:00:00.000000'),
(1146,'2025-07-23',41,1,'20:00:00.000000','18:00:00.000000'),
(1147,'2025-07-25',10,1,'20:00:00.000000','18:00:00.000000'),
(1148,'2025-07-25',12,1,'20:00:00.000000','18:00:00.000000'),
(1149,'2025-07-25',27,1,'20:00:00.000000','18:00:00.000000'),
(1150,'2025-07-25',36,1,'20:00:00.000000','18:00:00.000000'),
(1151,'2025-07-25',38,1,'20:00:00.000000','18:00:00.000000'),
(1152,'2025-07-25',39,1,'20:00:00.000000','18:00:00.000000'),
(1153,'2025-07-25',41,1,'20:00:00.000000','18:00:00.000000'),
(1154,'2025-07-28',10,1,'20:00:00.000000','18:00:00.000000'),
(1155,'2025-07-28',12,1,'20:00:00.000000','18:00:00.000000'),
(1156,'2025-07-28',27,1,'20:00:00.000000','18:00:00.000000'),
(1157,'2025-07-28',36,1,'20:00:00.000000','18:00:00.000000'),
(1158,'2025-07-28',38,1,'20:00:00.000000','18:00:00.000000'),
(1159,'2025-07-28',39,1,'20:00:00.000000','18:00:00.000000'),
(1160,'2025-07-28',41,1,'20:00:00.000000','18:00:00.000000'),
(1161,'2025-07-29',12,1,'14:00:00.000000','12:00:00.000000'),
(1162,'2025-07-29',38,1,'14:00:00.000000','12:00:00.000000'),
(1163,'2025-07-29',39,1,'14:00:00.000000','12:00:00.000000'),
(1164,'2025-07-29',41,1,'14:00:00.000000','12:00:00.000000'),
(1167,'2025-07-29',25,1,'14:00:00.000000','12:00:00.000000'),
(1168,'2025-07-29',30,1,'14:00:00.000000','12:00:00.000000'),
(1169,'2025-07-30',10,1,'20:00:00.000000','18:00:00.000000'),
(1170,'2025-07-30',12,1,'20:00:00.000000','18:00:00.000000'),
(1171,'2025-07-30',25,1,'20:00:00.000000','18:00:00.000000'),
(1172,'2025-07-30',27,1,'20:00:00.000000','18:00:00.000000'),
(1173,'2025-07-30',36,1,'20:00:00.000000','18:00:00.000000'),
(1174,'2025-07-30',39,1,'20:00:00.000000','18:00:00.000000'),
(1175,'2025-07-30',41,1,'20:00:00.000000','18:00:00.000000'),
(1176,'2025-07-31',12,1,'14:00:00.000000','12:00:00.000000'),
(1177,'2025-07-31',25,1,'14:00:00.000000','12:00:00.000000'),
(1178,'2025-07-31',27,1,'14:00:00.000000','12:00:00.000000'),
(1179,'2025-07-31',30,1,'14:00:00.000000','12:00:00.000000'),
(1180,'2025-07-31',39,1,'14:00:00.000000','12:00:00.000000'),
(1181,'2025-07-31',41,1,'14:00:00.000000','12:00:00.000000'),
(1182,'2025-08-01',10,1,'20:00:00.000000','18:00:00.000000'),
(1183,'2025-08-01',12,1,'20:00:00.000000','18:00:00.000000'),
(1184,'2025-08-01',25,1,'20:00:00.000000','18:00:00.000000'),
(1185,'2025-08-01',27,1,'20:00:00.000000','18:00:00.000000'),
(1186,'2025-08-01',36,1,'20:00:00.000000','18:00:00.000000'),
(1187,'2025-08-01',38,1,'20:00:00.000000','18:00:00.000000'),
(1188,'2025-08-01',39,1,'20:00:00.000000','18:00:00.000000'),
(1189,'2025-08-01',41,1,'20:00:00.000000','18:00:00.000000'),
(1190,'2025-08-04',10,1,'20:00:00.000000','18:00:00.000000'),
(1191,'2025-08-04',12,1,'20:00:00.000000','18:00:00.000000'),
(1192,'2025-08-04',25,1,'20:00:00.000000','18:00:00.000000'),
(1193,'2025-08-04',27,1,'20:00:00.000000','18:00:00.000000'),
(1194,'2025-08-04',36,1,'20:00:00.000000','18:00:00.000000'),
(1195,'2025-08-04',38,1,'20:00:00.000000','18:00:00.000000'),
(1196,'2025-08-04',39,1,'20:00:00.000000','18:00:00.000000'),
(1197,'2025-08-04',41,1,'20:00:00.000000','18:00:00.000000'),
(1198,'2025-08-05',12,1,'14:00:00.000000','12:00:00.000000'),
(1199,'2025-08-05',25,1,'14:00:00.000000','12:00:00.000000'),
(1200,'2025-08-05',30,1,'14:00:00.000000','12:00:00.000000'),
(1201,'2025-08-05',38,1,'14:00:00.000000','12:00:00.000000'),
(1202,'2025-08-05',39,1,'14:00:00.000000','12:00:00.000000'),
(1203,'2025-08-05',41,1,'14:00:00.000000','12:00:00.000000'),
(1204,'2025-08-06',10,1,'20:00:00.000000','18:00:00.000000'),
(1205,'2025-08-06',12,1,'20:00:00.000000','18:00:00.000000'),
(1206,'2025-08-06',25,1,'20:00:00.000000','18:00:00.000000'),
(1207,'2025-08-06',27,1,'20:00:00.000000','18:00:00.000000'),
(1208,'2025-08-06',36,1,'20:00:00.000000','18:00:00.000000'),
(1209,'2025-08-06',38,1,'20:00:00.000000','18:00:00.000000'),
(1210,'2025-08-06',39,1,'20:00:00.000000','18:00:00.000000'),
(1211,'2025-08-06',41,1,'20:00:00.000000','18:00:00.000000'),
(1212,'2025-08-07',12,1,'14:00:00.000000','12:00:00.000000'),
(1213,'2025-08-07',25,1,'14:00:00.000000','12:00:00.000000'),
(1214,'2025-08-07',27,1,'14:00:00.000000','12:00:00.000000'),
(1215,'2025-08-07',30,1,'14:00:00.000000','12:00:00.000000'),
(1216,'2025-08-07',38,1,'14:00:00.000000','12:00:00.000000'),
(1217,'2025-08-07',39,1,'14:00:00.000000','12:00:00.000000'),
(1218,'2025-08-07',41,1,'14:00:00.000000','12:00:00.000000'),
(1219,'2025-08-08',10,1,'20:00:00.000000','18:00:00.000000'),
(1220,'2025-08-08',12,1,'20:00:00.000000','18:00:00.000000'),
(1221,'2025-08-08',25,1,'20:00:00.000000','18:00:00.000000'),
(1222,'2025-08-08',27,1,'20:00:00.000000','18:00:00.000000'),
(1223,'2025-08-08',36,1,'20:00:00.000000','18:00:00.000000'),
(1224,'2025-08-08',38,1,'20:00:00.000000','18:00:00.000000'),
(1225,'2025-08-08',39,1,'20:00:00.000000','18:00:00.000000'),
(1226,'2025-08-08',41,1,'20:00:00.000000','18:00:00.000000'),
(1227,'2025-08-11',10,1,'20:00:00.000000','18:00:00.000000'),
(1228,'2025-08-11',12,1,'20:00:00.000000','18:00:00.000000'),
(1229,'2025-08-11',25,1,'20:00:00.000000','18:00:00.000000'),
(1230,'2025-08-11',36,1,'20:00:00.000000','18:00:00.000000'),
(1231,'2025-08-11',38,1,'20:00:00.000000','18:00:00.000000'),
(1232,'2025-08-11',39,1,'20:00:00.000000','18:00:00.000000'),
(1233,'2025-08-11',41,1,'20:00:00.000000','18:00:00.000000'),
(1234,'2025-08-13',10,1,'20:00:00.000000','18:00:00.000000'),
(1235,'2025-08-13',12,1,'20:00:00.000000','18:00:00.000000'),
(1236,'2025-08-13',25,1,'20:00:00.000000','18:00:00.000000'),
(1237,'2025-08-13',27,1,'20:00:00.000000','18:00:00.000000'),
(1238,'2025-08-13',36,1,'20:00:00.000000','18:00:00.000000'),
(1239,'2025-08-13',38,1,'20:00:00.000000','18:00:00.000000'),
(1240,'2025-08-13',39,1,'20:00:00.000000','18:00:00.000000'),
(1241,'2025-08-13',41,1,'20:00:00.000000','18:00:00.000000'),
(1242,'2025-08-15',12,1,'14:00:00.000000','12:00:00.000000'),
(1243,'2025-08-18',12,1,'20:00:00.000000','18:00:00.000000'),
(1244,'2025-08-18',25,1,'20:00:00.000000','18:00:00.000000'),
(1245,'2025-08-18',27,1,'20:00:00.000000','18:00:00.000000'),
(1246,'2025-08-18',36,1,'20:00:00.000000','18:00:00.000000'),
(1247,'2025-08-18',38,1,'20:00:00.000000','18:00:00.000000'),
(1248,'2025-08-18',39,1,'20:00:00.000000','18:00:00.000000'),
(1249,'2025-08-18',41,1,'20:00:00.000000','18:00:00.000000'),
(1250,'2025-08-20',10,1,'20:00:00.000000','18:00:00.000000'),
(1251,'2025-08-20',12,1,'20:00:00.000000','18:00:00.000000'),
(1252,'2025-08-20',25,1,'20:00:00.000000','18:00:00.000000'),
(1253,'2025-08-20',27,1,'20:00:00.000000','18:00:00.000000'),
(1254,'2025-08-20',36,1,'20:00:00.000000','18:00:00.000000'),
(1255,'2025-08-20',38,1,'20:00:00.000000','18:00:00.000000'),
(1256,'2025-08-20',41,1,'20:00:00.000000','18:00:00.000000'),
(1257,'2025-08-22',10,1,'20:00:00.000000','18:00:00.000000'),
(1258,'2025-08-22',12,1,'20:00:00.000000','18:00:00.000000'),
(1259,'2025-08-22',25,1,'20:00:00.000000','18:00:00.000000'),
(1260,'2025-08-22',36,1,'20:00:00.000000','18:00:00.000000'),
(1261,'2025-08-22',38,1,'20:00:00.000000','18:00:00.000000'),
(1262,'2025-08-22',39,1,'20:00:00.000000','18:00:00.000000'),
(1263,'2025-08-25',10,1,'20:00:00.000000','18:00:00.000000'),
(1264,'2025-08-25',12,1,'20:00:00.000000','18:00:00.000000'),
(1265,'2025-08-25',25,1,'20:00:00.000000','18:00:00.000000'),
(1266,'2025-08-25',36,1,'20:00:00.000000','18:00:00.000000'),
(1267,'2025-08-25',38,1,'20:00:00.000000','18:00:00.000000'),
(1268,'2025-08-25',39,1,'20:00:00.000000','18:00:00.000000'),
(1269,'2025-08-25',41,1,'20:00:00.000000','18:00:00.000000'),
(1270,'2025-08-27',10,1,'20:00:00.000000','18:00:00.000000'),
(1271,'2025-08-27',12,1,'20:00:00.000000','18:00:00.000000'),
(1272,'2025-08-27',25,1,'20:00:00.000000','18:00:00.000000'),
(1273,'2025-08-27',36,1,'20:00:00.000000','18:00:00.000000'),
(1274,'2025-08-27',38,1,'20:00:00.000000','18:00:00.000000'),
(1275,'2025-08-27',39,1,'20:00:00.000000','18:00:00.000000'),
(1276,'2025-08-27',41,1,'20:00:00.000000','18:00:00.000000'),
(1277,'2025-08-29',10,1,'20:00:00.000000','18:00:00.000000'),
(1278,'2025-08-29',12,1,'20:00:00.000000','18:00:00.000000'),
(1279,'2025-08-29',25,1,'20:00:00.000000','18:00:00.000000'),
(1280,'2025-08-29',36,1,'20:00:00.000000','18:00:00.000000'),
(1281,'2025-08-29',38,1,'20:00:00.000000','18:00:00.000000'),
(1282,'2025-08-29',39,1,'20:00:00.000000','18:00:00.000000'),
(1283,'2025-08-29',41,1,'20:00:00.000000','18:00:00.000000'),
(1284,'2025-09-01',10,1,'20:00:00.000000','18:00:00.000000'),
(1285,'2025-09-01',12,1,'20:00:00.000000','18:00:00.000000'),
(1286,'2025-09-01',36,1,'20:00:00.000000','18:00:00.000000'),
(1287,'2025-09-01',38,1,'20:00:00.000000','18:00:00.000000'),
(1288,'2025-09-01',39,1,'20:00:00.000000','18:00:00.000000'),
(1289,'2025-09-01',41,1,'20:00:00.000000','18:00:00.000000'),
(1290,'2025-09-03',10,1,'20:00:00.000000','18:00:00.000000'),
(1291,'2025-09-03',12,1,'20:00:00.000000','18:00:00.000000'),
(1292,'2025-09-03',25,1,'20:00:00.000000','18:00:00.000000'),
(1293,'2025-09-03',36,1,'20:00:00.000000','18:00:00.000000'),
(1294,'2025-09-03',38,1,'20:00:00.000000','18:00:00.000000'),
(1295,'2025-09-03',39,1,'20:00:00.000000','18:00:00.000000'),
(1296,'2025-09-03',41,1,'20:00:00.000000','18:00:00.000000'),
(1297,'2025-09-05',10,1,'20:00:00.000000','18:00:00.000000'),
(1298,'2025-09-05',12,1,'20:00:00.000000','18:00:00.000000'),
(1299,'2025-09-05',25,1,'20:00:00.000000','18:00:00.000000'),
(1300,'2025-09-05',36,1,'20:00:00.000000','18:00:00.000000'),
(1301,'2025-09-05',38,1,'20:00:00.000000','18:00:00.000000'),
(1302,'2025-09-05',39,1,'20:00:00.000000','18:00:00.000000'),
(1303,'2025-09-05',41,1,'20:00:00.000000','18:00:00.000000'),
(1304,'2025-09-08',10,1,'20:00:00.000000','18:00:00.000000'),
(1305,'2025-09-08',12,1,'20:00:00.000000','17:00:00.000000'),
(1306,'2025-09-08',25,1,'20:00:00.000000','18:00:00.000000'),
(1307,'2025-09-08',36,1,'20:00:00.000000','18:00:00.000000'),
(1308,'2025-09-08',38,1,'20:00:00.000000','18:00:00.000000'),
(1309,'2025-09-08',39,1,'20:00:00.000000','18:00:00.000000'),
(1310,'2025-09-08',41,1,'20:00:00.000000','18:00:00.000000'),
(1311,'2025-09-10',10,1,'20:00:00.000000','18:00:00.000000'),
(1312,'2025-09-10',12,1,'20:00:00.000000','17:00:00.000000'),
(1313,'2025-09-10',25,1,'20:00:00.000000','18:00:00.000000'),
(1314,'2025-09-10',36,1,'20:00:00.000000','18:00:00.000000'),
(1315,'2025-09-10',38,1,'20:00:00.000000','18:00:00.000000'),
(1316,'2025-09-10',39,1,'20:00:00.000000','18:00:00.000000'),
(1317,'2025-09-10',41,1,'20:00:00.000000','18:00:00.000000'),
(1318,'2025-09-12',10,1,'20:00:00.000000','18:00:00.000000'),
(1319,'2025-09-12',12,1,'20:00:00.000000','17:00:00.000000'),
(1320,'2025-09-12',25,1,'20:00:00.000000','18:00:00.000000'),
(1321,'2025-09-12',36,1,'20:00:00.000000','18:00:00.000000'),
(1322,'2025-09-12',38,1,'20:00:00.000000','18:00:00.000000'),
(1323,'2025-09-12',39,1,'20:00:00.000000','18:00:00.000000'),
(1324,'2025-09-12',41,1,'20:00:00.000000','18:00:00.000000'),
(1325,'2025-09-15',10,1,'20:00:00.000000','18:00:00.000000'),
(1326,'2025-09-15',12,1,'20:00:00.000000','17:00:00.000000'),
(1327,'2025-09-15',25,1,'20:00:00.000000','18:00:00.000000'),
(1328,'2025-09-15',36,1,'20:00:00.000000','18:00:00.000000'),
(1329,'2025-09-15',38,1,'20:00:00.000000','18:00:00.000000'),
(1330,'2025-09-15',39,1,'20:00:00.000000','18:00:00.000000'),
(1331,'2025-09-17',10,1,'20:00:00.000000','18:00:00.000000'),
(1332,'2025-09-17',12,1,'20:00:00.000000','17:00:00.000000'),
(1333,'2025-09-17',25,1,'20:00:00.000000','18:00:00.000000'),
(1334,'2025-09-17',36,1,'20:00:00.000000','18:00:00.000000'),
(1335,'2025-09-17',38,1,'20:00:00.000000','18:00:00.000000'),
(1336,'2025-09-17',39,1,'20:00:00.000000','18:00:00.000000'),
(1337,'2025-09-19',10,1,'20:00:00.000000','18:00:00.000000'),
(1338,'2025-09-19',12,1,'20:00:00.000000','17:00:00.000000'),
(1339,'2025-09-19',25,1,'20:00:00.000000','18:00:00.000000'),
(1340,'2025-09-19',36,1,'20:00:00.000000','18:00:00.000000'),
(1341,'2025-09-19',38,1,'20:00:00.000000','18:00:00.000000'),
(1342,'2025-09-19',39,1,'20:00:00.000000','18:00:00.000000'),
(1343,'2025-09-22',10,1,'20:00:00.000000','18:00:00.000000'),
(1344,'2025-09-22',12,1,'20:00:00.000000','17:00:00.000000'),
(1345,'2025-09-22',25,1,'20:00:00.000000','18:00:00.000000'),
(1346,'2025-09-22',36,1,'20:00:00.000000','18:00:00.000000'),
(1347,'2025-09-22',38,1,'20:00:00.000000','18:00:00.000000'),
(1348,'2025-09-22',39,1,'20:00:00.000000','18:00:00.000000'),
(1349,'2025-09-22',41,1,'20:00:00.000000','18:00:00.000000'),
(1350,'2025-09-24',10,1,'20:00:00.000000','18:00:00.000000'),
(1351,'2025-09-24',12,1,'20:00:00.000000','17:00:00.000000'),
(1352,'2025-09-24',36,1,'20:00:00.000000','18:00:00.000000'),
(1353,'2025-09-24',38,1,'20:00:00.000000','18:00:00.000000'),
(1354,'2025-09-24',39,1,'20:00:00.000000','18:00:00.000000'),
(1355,'2025-09-24',41,1,'20:00:00.000000','18:00:00.000000'),
(1356,'2025-09-26',10,1,'20:00:00.000000','18:00:00.000000'),
(1357,'2025-09-26',12,1,'20:00:00.000000','17:00:00.000000'),
(1358,'2025-09-26',25,1,'20:00:00.000000','18:00:00.000000'),
(1359,'2025-09-26',36,1,'20:00:00.000000','18:00:00.000000'),
(1360,'2025-09-26',38,1,'20:00:00.000000','18:00:00.000000'),
(1361,'2025-09-26',41,1,'20:00:00.000000','18:00:00.000000'),
(1362,'2025-09-29',10,1,'20:00:00.000000','18:00:00.000000'),
(1363,'2025-09-29',12,1,'20:00:00.000000','17:00:00.000000'),
(1364,'2025-09-29',25,1,'20:00:00.000000','18:00:00.000000'),
(1365,'2025-09-29',36,1,'20:00:00.000000','18:00:00.000000'),
(1366,'2025-09-29',38,1,'20:00:00.000000','18:00:00.000000'),
(1367,'2025-09-29',39,1,'20:00:00.000000','18:00:00.000000'),
(1368,'2025-09-29',41,1,'20:00:00.000000','18:00:00.000000'),
(1369,'2025-10-01',10,1,'20:00:00.000000','18:00:00.000000'),
(1370,'2025-10-01',12,1,'20:00:00.000000','17:00:00.000000'),
(1371,'2025-10-01',25,1,'20:00:00.000000','18:00:00.000000'),
(1372,'2025-10-01',36,1,'20:00:00.000000','18:00:00.000000'),
(1373,'2025-10-01',38,1,'20:00:00.000000','18:00:00.000000'),
(1374,'2025-10-01',39,1,'20:00:00.000000','18:00:00.000000'),
(1375,'2025-10-01',41,1,'20:00:00.000000','18:00:00.000000'),
(1376,'2025-10-03',12,1,'20:00:00.000000','17:00:00.000000'),
(1377,'2025-10-03',36,1,'20:00:00.000000','18:00:00.000000'),
(1378,'2025-10-03',38,1,'20:00:00.000000','18:00:00.000000'),
(1379,'2025-10-03',39,1,'20:00:00.000000','18:00:00.000000'),
(1380,'2025-10-03',41,1,'20:00:00.000000','18:00:00.000000'),
(1381,'2025-10-10',10,1,'20:00:00.000000','18:00:00.000000'),
(1382,'2025-10-10',12,1,'20:00:00.000000','17:00:00.000000'),
(1383,'2025-10-10',25,1,'20:00:00.000000','18:00:00.000000'),
(1384,'2025-10-10',36,1,'20:00:00.000000','18:00:00.000000'),
(1385,'2025-10-10',38,1,'20:00:00.000000','18:00:00.000000'),
(1386,'2025-10-10',39,1,'20:00:00.000000','18:00:00.000000'),
(1387,'2025-10-13',10,1,'20:00:00.000000','18:00:00.000000'),
(1388,'2025-10-13',12,1,'20:00:00.000000','17:00:00.000000'),
(1389,'2025-10-13',25,1,'20:00:00.000000','18:00:00.000000'),
(1390,'2025-10-13',36,1,'20:00:00.000000','18:00:00.000000'),
(1391,'2025-10-13',38,1,'20:00:00.000000','18:00:00.000000'),
(1392,'2025-10-13',39,1,'20:00:00.000000','18:00:00.000000'),
(1393,'2025-10-13',41,1,'20:00:00.000000','18:00:00.000000'),
(1394,'2025-10-15',10,1,'20:00:00.000000','18:00:00.000000'),
(1395,'2025-10-15',12,1,'20:00:00.000000','17:00:00.000000'),
(1396,'2025-10-15',25,1,'20:00:00.000000','18:00:00.000000'),
(1397,'2025-10-15',36,1,'20:00:00.000000','18:00:00.000000'),
(1398,'2025-10-15',38,1,'20:00:00.000000','18:00:00.000000'),
(1399,'2025-10-15',39,1,'20:00:00.000000','18:00:00.000000'),
(1400,'2025-10-15',41,1,'20:00:00.000000','18:00:00.000000'),
(1401,'2025-10-17',10,1,'20:00:00.000000','18:00:00.000000'),
(1402,'2025-10-17',25,1,'20:00:00.000000','18:00:00.000000'),
(1403,'2025-10-17',36,1,'20:00:00.000000','18:00:00.000000'),
(1404,'2025-10-17',38,1,'20:00:00.000000','18:00:00.000000'),
(1405,'2025-10-17',39,1,'20:00:00.000000','18:00:00.000000'),
(1406,'2025-10-17',41,1,'20:00:00.000000','18:00:00.000000'),
(1407,'2025-10-20',10,1,'20:00:00.000000','18:00:00.000000'),
(1408,'2025-10-20',12,1,'20:00:00.000000','18:00:00.000000'),
(1409,'2025-10-20',25,1,'20:00:00.000000','18:00:00.000000'),
(1410,'2025-10-20',36,1,'20:00:00.000000','18:00:00.000000'),
(1411,'2025-10-20',38,1,'20:00:00.000000','18:00:00.000000'),
(1412,'2025-10-20',39,1,'20:00:00.000000','18:00:00.000000'),
(1413,'2025-10-20',41,1,'20:00:00.000000','18:00:00.000000'),
(1414,'2025-10-22',10,1,'20:00:00.000000','18:00:00.000000'),
(1415,'2025-10-22',12,1,'20:00:00.000000','18:00:00.000000'),
(1416,'2025-10-22',25,1,'20:00:00.000000','18:00:00.000000'),
(1417,'2025-10-22',36,1,'20:00:00.000000','18:00:00.000000'),
(1418,'2025-10-22',39,1,'20:00:00.000000','18:00:00.000000'),
(1419,'2025-10-22',41,1,'20:00:00.000000','18:00:00.000000'),
(1420,'2025-10-24',10,1,'20:00:00.000000','18:00:00.000000'),
(1421,'2025-10-24',12,1,'20:00:00.000000','18:00:00.000000'),
(1422,'2025-10-24',36,1,'20:00:00.000000','18:00:00.000000'),
(1423,'2025-10-24',38,1,'20:00:00.000000','18:00:00.000000'),
(1424,'2025-10-24',39,1,'20:00:00.000000','18:00:00.000000'),
(1425,'2025-10-24',41,1,'20:00:00.000000','18:00:00.000000'),
(1426,'2025-10-27',10,1,'20:00:00.000000','18:00:00.000000'),
(1427,'2025-10-27',12,1,'20:00:00.000000','18:00:00.000000'),
(1428,'2025-10-27',25,1,'20:00:00.000000','18:00:00.000000'),
(1429,'2025-10-27',36,1,'20:00:00.000000','18:00:00.000000'),
(1430,'2025-10-27',38,1,'20:00:00.000000','18:00:00.000000'),
(1431,'2025-10-27',39,1,'20:00:00.000000','18:00:00.000000'),
(1432,'2025-10-27',41,1,'20:00:00.000000','18:00:00.000000'),
(1433,'2025-10-29',10,1,'20:00:00.000000','18:00:00.000000'),
(1434,'2025-10-29',25,1,'20:00:00.000000','18:00:00.000000'),
(1435,'2025-10-29',36,1,'20:00:00.000000','18:00:00.000000'),
(1436,'2025-10-29',38,1,'20:00:00.000000','18:00:00.000000'),
(1437,'2025-10-29',39,1,'20:00:00.000000','18:00:00.000000'),
(1438,'2025-10-29',41,1,'20:00:00.000000','18:00:00.000000'),
(1439,'2025-10-31',10,1,'20:00:00.000000','18:00:00.000000'),
(1440,'2025-10-31',12,1,'20:00:00.000000','18:00:00.000000'),
(1441,'2025-10-31',25,1,'20:00:00.000000','18:00:00.000000'),
(1442,'2025-10-31',36,1,'20:00:00.000000','18:00:00.000000'),
(1443,'2025-10-31',38,1,'20:00:00.000000','18:00:00.000000'),
(1444,'2025-10-31',39,1,'20:00:00.000000','18:00:00.000000'),
(1445,'2025-10-31',41,1,'20:00:00.000000','18:00:00.000000'),
(1446,'2025-11-03',10,1,'20:00:00.000000','18:00:00.000000'),
(1447,'2025-11-03',12,1,'20:00:00.000000','18:00:00.000000'),
(1448,'2025-11-03',25,1,NULL,NULL),
(1449,'2025-11-03',36,1,'20:00:00.000000','18:00:00.000000'),
(1450,'2025-11-03',38,1,'20:00:00.000000','18:00:00.000000'),
(1451,'2025-11-03',39,1,'20:00:00.000000','18:00:00.000000'),
(1452,'2025-11-03',41,1,'20:00:00.000000','18:00:00.000000'),
(1453,'2025-11-05',10,1,'20:00:00.000000','18:00:00.000000'),
(1454,'2025-11-05',12,1,'20:00:00.000000','18:00:00.000000'),
(1455,'2025-11-05',25,1,'20:00:00.000000','18:00:00.000000'),
(1456,'2025-11-05',36,1,'20:00:00.000000','18:00:00.000000'),
(1457,'2025-11-05',38,1,'20:00:00.000000','18:00:00.000000'),
(1458,'2025-11-05',39,1,'20:00:00.000000','18:00:00.000000'),
(1459,'2025-11-05',41,1,'20:00:00.000000','18:00:00.000000'),
(1460,'2025-11-07',10,1,'20:00:00.000000','18:00:00.000000'),
(1461,'2025-11-07',12,1,'20:00:00.000000','18:00:00.000000'),
(1462,'2025-11-07',25,1,'20:00:00.000000','18:00:00.000000'),
(1463,'2025-11-07',36,1,'20:00:00.000000','18:00:00.000000'),
(1464,'2025-11-07',38,1,'20:00:00.000000','18:00:00.000000'),
(1465,'2025-11-07',39,1,'20:00:00.000000','18:00:00.000000'),
(1466,'2025-11-07',41,1,'20:00:00.000000','18:00:00.000000'),
(1467,'2025-11-10',10,1,'20:00:00.000000','18:00:00.000000'),
(1468,'2025-11-10',12,1,'20:00:00.000000','18:00:00.000000'),
(1469,'2025-11-10',25,1,'20:00:00.000000','18:00:00.000000'),
(1470,'2025-11-10',36,1,'20:00:00.000000','18:00:00.000000'),
(1471,'2025-11-10',38,1,'20:00:00.000000','18:00:00.000000'),
(1472,'2025-11-10',39,1,'20:00:00.000000','18:00:00.000000'),
(1473,'2025-11-10',41,1,'20:00:00.000000','18:00:00.000000'),
(1474,'2025-11-12',10,1,'20:00:00.000000','18:00:00.000000'),
(1475,'2025-11-12',12,1,'20:00:00.000000','18:00:00.000000'),
(1476,'2025-11-12',25,1,'20:00:00.000000','18:00:00.000000'),
(1477,'2025-11-12',36,1,'20:00:00.000000','18:00:00.000000'),
(1478,'2025-11-12',38,1,'20:00:00.000000','18:00:00.000000'),
(1479,'2025-11-12',39,1,'20:00:00.000000','18:00:00.000000'),
(1480,'2025-11-12',41,1,'20:00:00.000000','18:00:00.000000'),
(1481,'2025-11-14',10,1,'20:00:00.000000','18:00:00.000000'),
(1482,'2025-11-14',12,1,'20:00:00.000000','18:00:00.000000'),
(1483,'2025-11-14',25,1,'20:00:00.000000','18:00:00.000000'),
(1484,'2025-11-14',36,1,'20:00:00.000000','18:00:00.000000'),
(1485,'2025-11-14',38,1,'20:00:00.000000','18:00:00.000000'),
(1486,'2025-11-14',39,1,'20:00:00.000000','18:00:00.000000'),
(1487,'2025-11-14',41,1,'20:00:00.000000','18:00:00.000000'),
(1488,'2025-11-17',10,1,'20:00:00.000000','18:00:00.000000'),
(1489,'2025-11-17',12,1,'20:00:00.000000','18:00:00.000000'),
(1490,'2025-11-17',25,1,'20:00:00.000000','18:00:00.000000'),
(1491,'2025-11-17',36,1,'20:00:00.000000','18:00:00.000000'),
(1492,'2025-11-17',38,1,'20:00:00.000000','18:00:00.000000'),
(1493,'2025-11-17',39,1,'20:00:00.000000','18:00:00.000000'),
(1494,'2025-11-17',41,1,'20:00:00.000000','18:00:00.000000'),
(1495,'2025-11-19',10,1,'20:00:00.000000','18:00:00.000000'),
(1496,'2025-11-19',12,1,'20:00:00.000000','18:00:00.000000'),
(1497,'2025-11-19',25,1,'20:00:00.000000','18:00:00.000000'),
(1498,'2025-11-19',36,1,'20:00:00.000000','18:00:00.000000'),
(1499,'2025-11-19',38,1,'20:00:00.000000','18:00:00.000000'),
(1500,'2025-11-19',39,1,'20:00:00.000000','18:00:00.000000'),
(1501,'2025-11-19',41,1,'20:00:00.000000','18:00:00.000000'),
(1502,'2025-11-21',10,1,'20:00:00.000000','18:00:00.000000'),
(1503,'2025-11-21',12,1,'20:00:00.000000','18:00:00.000000'),
(1504,'2025-11-21',25,1,'20:00:00.000000','18:00:00.000000'),
(1505,'2025-11-21',28,1,'20:00:00.000000','18:00:00.000000'),
(1506,'2025-11-21',30,1,'20:00:00.000000','18:00:00.000000'),
(1507,'2025-11-21',38,1,'20:00:00.000000','18:00:00.000000'),
(1508,'2025-11-21',39,1,'20:00:00.000000','18:00:00.000000'),
(1509,'2025-11-21',41,1,'20:00:00.000000','18:00:00.000000'),
(1510,'2025-11-24',10,1,'20:00:00.000000','18:00:00.000000'),
(1511,'2025-11-24',12,1,'20:00:00.000000','18:00:00.000000'),
(1512,'2025-11-24',25,1,'20:00:00.000000','18:00:00.000000'),
(1513,'2025-11-24',28,1,'20:00:00.000000','18:00:00.000000'),
(1514,'2025-11-24',36,1,'20:00:00.000000','18:00:00.000000'),
(1515,'2025-11-24',38,1,'20:00:00.000000','18:00:00.000000'),
(1516,'2025-11-24',39,1,'20:00:00.000000','18:00:00.000000'),
(1517,'2025-11-24',41,1,'20:00:00.000000','18:00:00.000000'),
(1518,'2025-11-26',10,1,'20:00:00.000000','18:00:00.000000'),
(1519,'2025-11-26',25,1,'20:00:00.000000','18:00:00.000000'),
(1520,'2025-11-26',28,1,'20:00:00.000000','18:00:00.000000'),
(1521,'2025-11-26',36,1,NULL,NULL),
(1522,'2025-11-26',38,1,'20:00:00.000000','18:00:00.000000'),
(1523,'2025-11-26',41,1,'20:00:00.000000','18:00:00.000000'),
(1524,'2025-11-28',10,1,'20:00:00.000000','18:00:00.000000'),
(1525,'2025-11-28',25,1,'20:00:00.000000','18:00:00.000000'),
(1526,'2025-11-28',29,1,'20:00:00.000000','18:00:00.000000'),
(1527,'2025-11-28',30,1,'20:00:00.000000','18:00:00.000000'),
(1528,'2025-11-28',36,1,'20:00:00.000000','18:00:00.000000'),
(1529,'2025-11-28',38,1,'20:00:00.000000','18:00:00.000000'),
(1530,'2025-11-28',39,1,'20:00:00.000000','18:00:00.000000'),
(1531,'2025-11-28',41,1,'20:00:00.000000','18:00:00.000000'),
(1532,'2025-11-29',30,1,'18:00:00.000000','16:00:00.000000'),
(1534,'2025-12-01',10,1,'20:00:00.000000','18:00:00.000000'),
(1535,'2025-12-01',25,1,'20:00:00.000000','18:00:00.000000'),
(1536,'2025-12-01',28,1,'20:00:00.000000','18:00:00.000000'),
(1537,'2025-12-01',36,1,'20:00:00.000000','18:00:00.000000'),
(1538,'2025-12-01',38,1,'20:00:00.000000','18:00:00.000000'),
(1539,'2025-12-01',39,1,'20:00:00.000000','18:00:00.000000'),
(1540,'2025-12-01',41,1,'20:00:00.000000','18:00:00.000000'),
(1541,'2025-12-03',10,1,'20:00:00.000000','18:00:00.000000'),
(1542,'2025-12-03',25,1,'20:00:00.000000','18:00:00.000000'),
(1543,'2025-12-03',28,1,'20:00:00.000000','18:00:00.000000'),
(1544,'2025-12-03',36,1,'20:00:00.000000','18:00:00.000000'),
(1545,'2025-12-03',38,1,'20:00:00.000000','18:00:00.000000'),
(1546,'2025-12-03',39,1,'20:00:00.000000','18:00:00.000000'),
(1547,'2025-12-03',41,1,'20:00:00.000000','18:00:00.000000'),
(1548,'2025-12-03',45,1,'20:00:00.000000','18:00:00.000000'),
(1549,'2025-12-05',10,1,'20:00:00.000000','18:00:00.000000'),
(1550,'2025-12-05',12,1,'20:00:00.000000','18:00:00.000000'),
(1551,'2025-12-05',25,1,'20:00:00.000000','18:00:00.000000'),
(1552,'2025-12-05',28,1,'20:00:00.000000','18:00:00.000000'),
(1553,'2025-12-05',30,1,'20:00:00.000000','18:00:00.000000'),
(1554,'2025-12-05',36,1,'20:00:00.000000','18:00:00.000000'),
(1555,'2025-12-05',38,1,'20:00:00.000000','18:00:00.000000'),
(1556,'2025-12-05',39,1,'20:00:00.000000','18:00:00.000000'),
(1557,'2025-12-05',41,1,'20:00:00.000000','18:00:00.000000'),
(1558,'2025-12-08',10,1,'20:00:00.000000','18:00:00.000000'),
(1559,'2025-12-08',25,1,'20:00:00.000000','18:00:00.000000'),
(1560,'2025-12-08',28,1,'20:00:00.000000','18:00:00.000000'),
(1561,'2025-12-08',36,1,'20:00:00.000000','18:00:00.000000'),
(1562,'2025-12-08',38,1,'20:00:00.000000','18:00:00.000000'),
(1563,'2025-12-08',39,1,'20:00:00.000000','18:00:00.000000'),
(1564,'2025-12-08',41,1,'20:00:00.000000','18:00:00.000000'),
(1565,'2025-12-08',45,1,'20:00:00.000000','18:00:00.000000'),
(1566,'2025-12-10',10,1,'20:00:00.000000','18:00:00.000000'),
(1567,'2025-12-10',25,1,'20:00:00.000000','18:00:00.000000'),
(1568,'2025-12-10',28,1,'20:00:00.000000','18:00:00.000000'),
(1569,'2025-12-10',36,1,'20:00:00.000000','18:00:00.000000'),
(1570,'2025-12-10',38,1,'20:00:00.000000','18:00:00.000000'),
(1571,'2025-12-10',39,1,'20:00:00.000000','18:00:00.000000'),
(1572,'2025-12-12',10,1,'20:00:00.000000','18:00:00.000000'),
(1573,'2025-12-12',25,1,'20:00:00.000000','18:00:00.000000'),
(1574,'2025-12-12',28,1,'20:00:00.000000','18:00:00.000000'),
(1575,'2025-12-12',30,1,'20:00:00.000000','18:00:00.000000'),
(1576,'2025-12-12',36,1,'20:00:00.000000','18:00:00.000000'),
(1577,'2025-12-12',39,1,'20:00:00.000000','18:00:00.000000'),
(1578,'2025-12-12',41,1,'20:00:00.000000','18:00:00.000000'),
(1579,'2025-12-15',12,1,'20:00:00.000000','18:00:00.000000'),
(1580,'2025-12-15',28,1,'20:00:00.000000','18:00:00.000000'),
(1581,'2025-12-15',36,1,'20:00:00.000000','18:00:00.000000'),
(1582,'2025-12-15',41,1,'20:00:00.000000','18:00:00.000000'),
(1583,'2025-12-15',45,1,'20:00:00.000000','18:00:00.000000'),
(1584,'2025-12-17',10,1,'20:00:00.000000','18:00:00.000000'),
(1585,'2025-12-17',12,1,'20:00:00.000000','18:00:00.000000'),
(1586,'2025-12-17',28,1,'20:00:00.000000','18:00:00.000000'),
(1587,'2025-12-17',36,1,'20:00:00.000000','18:00:00.000000'),
(1588,'2025-12-17',38,1,'20:00:00.000000','18:00:00.000000'),
(1589,'2025-12-17',39,1,'20:00:00.000000','18:00:00.000000'),
(1590,'2025-12-17',41,1,'20:00:00.000000','18:00:00.000000'),
(1591,'2025-12-17',45,1,'20:00:00.000000','18:00:00.000000'),
(1592,'2025-12-19',10,1,'20:00:00.000000','18:00:00.000000'),
(1593,'2025-12-19',12,1,'20:00:00.000000','18:00:00.000000'),
(1594,'2025-12-19',25,1,'20:00:00.000000','18:00:00.000000'),
(1595,'2025-12-19',28,1,'20:00:00.000000','18:00:00.000000'),
(1596,'2025-12-19',36,1,'20:00:00.000000','18:00:00.000000'),
(1597,'2025-12-19',38,1,'20:00:00.000000','18:00:00.000000'),
(1598,'2025-12-19',39,1,'20:00:00.000000','18:00:00.000000'),
(1599,'2025-12-19',41,1,'20:00:00.000000','18:00:00.000000'),
(1600,'2025-12-22',10,1,'20:00:00.000000','18:00:00.000000'),
(1601,'2025-12-22',12,1,'20:00:00.000000','18:00:00.000000'),
(1602,'2025-12-22',25,1,'20:00:00.000000','18:00:00.000000'),
(1603,'2025-12-22',28,1,'20:00:00.000000','18:00:00.000000'),
(1604,'2025-12-22',36,1,'20:00:00.000000','18:00:00.000000'),
(1605,'2025-12-22',39,1,'20:00:00.000000','18:00:00.000000'),
(1606,'2025-12-22',41,1,'20:00:00.000000','18:00:00.000000'),
(1607,'2025-12-22',45,1,'20:00:00.000000','18:00:00.000000'),
(1608,'2025-12-24',10,1,'20:00:00.000000','18:00:00.000000'),
(1609,'2025-12-24',12,1,'20:00:00.000000','18:00:00.000000'),
(1610,'2025-12-24',25,1,'20:00:00.000000','18:00:00.000000'),
(1611,'2025-12-24',28,1,'20:00:00.000000','18:00:00.000000'),
(1612,'2025-12-24',38,1,'20:00:00.000000','18:00:00.000000'),
(1613,'2025-12-24',39,1,'20:00:00.000000','18:00:00.000000'),
(1614,'2025-12-24',41,1,'20:00:00.000000','18:00:00.000000'),
(1615,'2025-12-24',45,1,'20:00:00.000000','18:00:00.000000'),
(1616,'2025-12-24',46,1,'20:00:00.000000','18:00:00.000000'),
(1617,'2025-12-26',10,1,'20:00:00.000000','18:00:00.000000'),
(1618,'2025-12-26',12,1,'20:00:00.000000','18:00:00.000000'),
(1619,'2025-12-26',25,1,'20:00:00.000000','18:00:00.000000'),
(1620,'2025-12-26',28,1,'20:00:00.000000','18:00:00.000000'),
(1621,'2025-12-26',30,1,'20:00:00.000000','18:00:00.000000'),
(1622,'2025-12-26',38,1,'20:00:00.000000','18:00:00.000000'),
(1623,'2025-12-26',39,1,'20:00:00.000000','18:00:00.000000'),
(1624,'2025-12-26',41,1,'20:00:00.000000','18:00:00.000000'),
(1625,'2025-12-26',46,1,'20:00:00.000000','18:00:00.000000'),
(1626,'2025-12-29',10,1,'20:00:00.000000','18:00:00.000000'),
(1627,'2025-12-29',12,1,'20:00:00.000000','18:00:00.000000'),
(1628,'2025-12-29',28,1,'20:00:00.000000','18:00:00.000000'),
(1629,'2025-12-29',29,1,'20:00:00.000000','18:00:00.000000'),
(1630,'2025-12-29',38,1,'20:00:00.000000','18:00:00.000000'),
(1631,'2025-12-29',39,1,'20:00:00.000000','18:00:00.000000'),
(1632,'2025-12-29',41,1,'20:00:00.000000','18:00:00.000000'),
(1633,'2025-12-29',45,1,'20:00:00.000000','18:00:00.000000'),
(1634,'2025-12-29',46,1,'20:00:00.000000','18:00:00.000000'),
(1635,'2025-12-31',10,1,'20:00:00.000000','18:00:00.000000'),
(1636,'2025-12-31',12,1,'20:00:00.000000','18:00:00.000000'),
(1637,'2025-12-31',25,1,'20:00:00.000000','18:00:00.000000'),
(1638,'2025-12-31',28,1,'20:00:00.000000','18:00:00.000000'),
(1640,'2025-12-31',39,1,'20:00:00.000000','18:00:00.000000'),
(1641,'2025-12-31',41,1,'20:00:00.000000','18:00:00.000000'),
(1642,'2025-12-31',45,1,'20:00:00.000000','18:00:00.000000'),
(1643,'2025-12-31',46,1,'20:00:00.000000','18:00:00.000000'),
(1644,'2026-01-02',10,1,'20:00:00.000000','18:00:00.000000'),
(1645,'2026-01-02',25,1,'20:00:00.000000','18:00:00.000000'),
(1646,'2026-01-02',28,1,'20:00:00.000000','18:00:00.000000'),
(1647,'2026-01-02',30,1,'20:00:00.000000','18:00:00.000000'),
(1648,'2026-01-02',38,1,'20:00:00.000000','18:00:00.000000'),
(1649,'2026-01-02',39,1,'20:00:00.000000','18:00:00.000000'),
(1650,'2026-01-02',41,1,'20:00:00.000000','18:00:00.000000'),
(1651,'2026-01-02',46,1,'20:00:00.000000','18:00:00.000000'),
(1652,'2026-01-05',10,1,'20:00:00.000000','18:00:00.000000'),
(1653,'2026-01-05',12,1,'20:00:00.000000','18:00:00.000000'),
(1654,'2026-01-05',28,1,'20:00:00.000000','18:00:00.000000'),
(1655,'2026-01-05',29,1,'20:00:00.000000','18:00:00.000000'),
(1656,'2026-01-05',38,1,'20:00:00.000000','18:00:00.000000'),
(1657,'2026-01-05',39,1,'20:00:00.000000','18:00:00.000000'),
(1658,'2026-01-05',41,1,'20:00:00.000000','18:00:00.000000'),
(1659,'2026-01-05',45,1,'20:00:00.000000','18:00:00.000000'),
(1660,'2026-01-05',46,1,'20:00:00.000000','18:00:00.000000'),
(1661,'2026-01-07',10,1,'20:00:00.000000','18:00:00.000000'),
(1662,'2026-01-07',12,1,'20:00:00.000000','18:00:00.000000'),
(1663,'2026-01-07',28,1,'20:00:00.000000','18:00:00.000000'),
(1664,'2026-01-07',29,1,'20:00:00.000000','18:00:00.000000'),
(1665,'2026-01-07',38,1,'20:00:00.000000','18:00:00.000000'),
(1666,'2026-01-07',39,1,'20:00:00.000000','18:00:00.000000'),
(1667,'2026-01-07',41,1,'20:00:00.000000','18:00:00.000000'),
(1668,'2026-01-07',45,1,'20:00:00.000000','18:00:00.000000'),
(1669,'2026-01-07',46,1,'20:00:00.000000','18:00:00.000000'),
(1670,'2026-01-09',10,1,'20:00:00.000000','18:00:00.000000'),
(1671,'2026-01-09',12,1,'20:00:00.000000','18:00:00.000000'),
(1672,'2026-01-09',28,1,'20:00:00.000000','18:00:00.000000'),
(1673,'2026-01-09',29,1,'20:00:00.000000','18:00:00.000000'),
(1674,'2026-01-09',30,1,'20:00:00.000000','18:00:00.000000'),
(1675,'2026-01-09',39,1,'20:00:00.000000','18:00:00.000000'),
(1676,'2026-01-09',41,1,'20:00:00.000000','18:00:00.000000'),
(1677,'2026-01-09',46,1,'20:00:00.000000','18:00:00.000000'),
(1678,'2026-01-12',10,1,'20:00:00.000000','18:00:00.000000'),
(1679,'2026-01-12',12,1,'20:00:00.000000','18:00:00.000000'),
(1680,'2026-01-12',28,1,'16:00:00.000000','14:00:00.000000'),
(1681,'2026-01-12',29,1,'20:00:00.000000','18:00:00.000000'),
(1682,'2026-01-12',30,1,'16:00:00.000000','14:00:00.000000'),
(1683,'2026-01-12',38,1,'20:00:00.000000','18:00:00.000000'),
(1684,'2026-01-12',39,1,'20:00:00.000000','18:00:00.000000'),
(1685,'2026-01-12',41,1,'20:00:00.000000','18:00:00.000000'),
(1686,'2026-01-12',45,1,'20:00:00.000000','18:00:00.000000'),
(1687,'2026-01-12',46,1,'20:00:00.000000','18:00:00.000000'),
(1694,'2026-01-13',28,1,'16:00:00.000000','12:00:00.000000'),
(1695,'2026-01-13',29,1,'14:00:00.000000','12:00:00.000000'),
(1696,'2026-01-13',30,1,'16:00:00.000000','12:00:00.000000'),
(1697,'2026-01-13',33,1,'14:00:00.000000','12:00:00.000000'),
(1698,'2026-01-13',39,1,'14:00:00.000000','12:00:00.000000'),
(1699,'2026-01-13',45,1,'14:00:00.000000','12:00:00.000000'),
(1700,'2026-01-14',10,1,'20:00:00.000000','18:00:00.000000'),
(1701,'2026-01-14',12,1,'20:00:00.000000','18:00:00.000000'),
(1702,'2026-01-14',28,1,'16:00:00.000000','14:00:00.000000'),
(1703,'2026-01-14',29,1,'20:00:00.000000','18:00:00.000000'),
(1704,'2026-01-14',38,1,'20:00:00.000000','18:00:00.000000'),
(1705,'2026-01-14',39,1,'20:00:00.000000','18:00:00.000000'),
(1706,'2026-01-14',41,1,'20:00:00.000000','18:00:00.000000'),
(1707,'2026-01-14',45,1,'20:00:00.000000','18:00:00.000000'),
(1708,'2026-01-14',46,1,'20:00:00.000000','18:00:00.000000'),
(1709,'2026-01-15',12,1,'14:00:00.000000','12:00:00.000000'),
(1710,'2026-01-15',28,1,'16:00:00.000000','14:00:00.000000'),
(1711,'2026-01-15',29,1,'14:00:00.000000','12:00:00.000000'),
(1712,'2026-01-15',30,1,'16:00:00.000000','14:00:00.000000'),
(1713,'2026-01-15',33,1,'14:00:00.000000','12:00:00.000000'),
(1714,'2026-01-15',39,1,'14:00:00.000000','12:00:00.000000'),
(1715,'2026-01-15',41,1,'14:00:00.000000','12:00:00.000000'),
(1716,'2026-01-15',46,1,'14:00:00.000000','12:00:00.000000'),
(1717,'2026-01-16',10,1,'20:00:00.000000','18:00:00.000000'),
(1718,'2026-01-16',12,1,'20:00:00.000000','18:00:00.000000'),
(1719,'2026-01-16',28,1,'16:00:00.000000','14:00:00.000000'),
(1720,'2026-01-16',29,1,'20:00:00.000000','18:00:00.000000'),
(1721,'2026-01-16',30,1,'16:00:00.000000','14:00:00.000000'),
(1722,'2026-01-16',38,1,'20:00:00.000000','18:00:00.000000'),
(1723,'2026-01-16',39,1,'20:00:00.000000','18:00:00.000000'),
(1724,'2026-01-16',41,1,'20:00:00.000000','18:00:00.000000'),
(1725,'2026-01-16',46,1,'20:00:00.000000','18:00:00.000000');
/*!40000 ALTER TABLE `teachers_attendance` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `teachers_salary`
--

DROP TABLE IF EXISTS `teachers_salary`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `teachers_salary` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `year` int unsigned NOT NULL,
  `month` int unsigned NOT NULL,
  `work_days` int unsigned NOT NULL,
  `base_amount` int unsigned NOT NULL,
  `additional_amount` int unsigned NOT NULL,
  `total_amount` int unsigned NOT NULL,
  `teacher_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `teachers_salary_teacher_id_year_month_1956117e_uniq` (`teacher_id`,`year`,`month`),
  CONSTRAINT `teachers_salary_teacher_id_6ecab5b1_fk_teachers_teacher_id` FOREIGN KEY (`teacher_id`) REFERENCES `teachers_teacher` (`id`),
  CONSTRAINT `teachers_salary_additional_amount_887bc6c0_check` CHECK ((`additional_amount` >= 0)),
  CONSTRAINT `teachers_salary_base_amount_479855e6_check` CHECK ((`base_amount` >= 0)),
  CONSTRAINT `teachers_salary_month_cee94130_check` CHECK ((`month` >= 0)),
  CONSTRAINT `teachers_salary_total_amount_7694693d_check` CHECK ((`total_amount` >= 0)),
  CONSTRAINT `teachers_salary_work_days_bcd2257a_check` CHECK ((`work_days` >= 0)),
  CONSTRAINT `teachers_salary_year_68dc8393_check` CHECK ((`year` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=224 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `teachers_salary`
--

LOCK TABLES `teachers_salary` WRITE;
/*!40000 ALTER TABLE `teachers_salary` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `teachers_salary` VALUES
(23,2024,10,13,390000,0,390000,10),
(24,2024,10,13,390000,0,390000,11),
(25,2024,10,13,390000,0,390000,12),
(26,2024,10,11,330000,0,330000,13),
(27,2024,10,12,360000,0,360000,14),
(28,2024,10,12,360000,0,360000,15),
(29,2024,10,3,90000,0,90000,16),
(30,2024,10,3,90000,0,90000,17),
(32,2024,9,10,300000,0,300000,10),
(33,2024,9,11,330000,0,330000,11),
(34,2024,9,10,300000,0,300000,12),
(35,2024,9,11,330000,0,330000,13),
(36,2024,9,9,270000,0,270000,14),
(37,2024,9,9,270000,0,270000,15),
(38,2024,9,3,90000,0,90000,16),
(39,2024,9,4,120000,0,120000,17),
(40,2024,12,11,330000,0,330000,10),
(41,2024,12,0,0,0,0,11),
(42,2024,12,12,360000,0,360000,12),
(43,2024,12,0,0,0,0,13),
(44,2024,12,9,270000,0,270000,14),
(45,2024,12,11,330000,0,330000,15),
(46,2024,12,0,0,0,0,16),
(47,2024,12,0,0,0,0,17),
(48,2024,12,11,330000,0,330000,22),
(49,2024,12,12,360000,0,360000,25),
(50,2024,12,11,330000,0,330000,26),
(51,2024,11,12,360000,0,360000,10),
(52,2024,11,1,30000,0,30000,11),
(53,2024,11,13,390000,0,390000,12),
(54,2024,11,13,390000,0,390000,13),
(55,2024,11,13,390000,0,390000,14),
(56,2024,11,11,330000,0,330000,15),
(57,2024,11,0,0,0,0,16),
(58,2024,11,0,0,0,0,17),
(59,2024,11,13,390000,0,390000,22),
(60,2024,11,1,30000,0,30000,25),
(61,2024,11,2,60000,0,60000,26),
(62,2024,10,4,120000,0,120000,22),
(63,2024,10,0,0,0,0,25),
(64,2024,10,0,0,0,0,26),
(65,2024,9,0,0,0,0,22),
(66,2024,9,0,0,0,0,25),
(67,2024,9,0,0,0,0,26),
(68,2024,12,12,360000,0,360000,27),
(69,2024,12,10,300000,0,300000,28),
(70,2024,12,3,90000,0,90000,29),
(71,2025,1,9,270000,0,270000,10),
(72,2025,1,13,390000,0,390000,12),
(73,2025,1,8,240000,0,240000,15),
(74,2025,1,16,480000,0,480000,22),
(75,2025,1,7,210000,0,210000,25),
(76,2025,1,15,450000,0,450000,26),
(77,2025,1,15,450000,90000,540000,27),
(78,2025,1,15,450000,0,450000,28),
(79,2025,1,13,390000,0,390000,29),
(80,2025,1,12,360000,0,360000,30),
(81,2025,1,1,30000,0,30000,31),
(83,2025,2,11,330000,0,330000,10),
(84,2025,2,16,480000,0,480000,12),
(85,2025,2,13,390000,0,390000,15),
(86,2025,2,16,480000,0,480000,25),
(87,2025,2,15,450000,0,450000,26),
(88,2025,2,15,450000,0,450000,28),
(89,2025,2,14,420000,0,420000,29),
(90,2025,2,15,450000,0,450000,30),
(91,2025,2,13,390000,0,390000,33),
(92,2025,2,14,420000,0,420000,34),
(93,2025,2,12,360000,0,360000,27),
(94,2025,2,11,330000,0,330000,22),
(95,2025,3,11,330000,0,330000,10),
(96,2025,3,12,360000,0,360000,12),
(97,2025,3,8,240000,0,240000,15),
(98,2025,3,9,330000,320000,650000,28),
(99,2025,3,4,120000,0,120000,35),
(100,2025,3,8,240000,0,240000,36),
(101,2025,3,11,330000,0,330000,37),
(102,2025,3,10,300000,0,300000,38),
(103,2025,3,10,300000,0,300000,39),
(104,2025,3,5,150000,0,150000,40),
(105,2025,4,13,390000,0,390000,10),
(106,2025,4,12,360000,0,360000,12),
(107,2025,4,9,270000,0,270000,15),
(108,2025,4,9,300000,320000,620000,28),
(109,2025,4,7,210000,0,210000,36),
(110,2025,4,9,270000,0,270000,37),
(111,2025,4,11,330000,0,330000,38),
(112,2025,4,12,360000,0,360000,39),
(113,2025,4,13,390000,0,390000,40),
(114,2025,5,11,330000,0,330000,10),
(115,2025,5,12,360000,0,360000,12),
(116,2025,5,11,330000,240000,570000,28),
(117,2025,5,8,240000,0,240000,36),
(118,2025,5,11,330000,0,330000,37),
(119,2025,5,11,330000,0,330000,38),
(120,2025,5,11,330000,0,330000,39),
(121,2025,5,11,330000,0,330000,40),
(122,2025,5,11,330000,0,330000,41),
(123,2025,6,13,390000,0,390000,10),
(124,2025,6,12,360000,0,360000,12),
(125,2025,6,9,270000,320000,590000,28),
(126,2025,6,9,270000,0,270000,37),
(127,2025,6,11,330000,0,330000,38),
(128,2025,6,11,330000,0,330000,39),
(129,2025,6,11,330000,0,330000,40),
(130,2025,6,8,240000,0,240000,36),
(131,2025,6,9,270000,0,270000,41),
(132,2025,7,13,390000,0,390000,10),
(133,2025,7,15,450000,0,450000,12),
(134,2025,7,11,330000,320000,650000,27),
(135,2025,7,13,390000,0,390000,36),
(136,2025,7,12,360000,0,360000,38),
(137,2025,7,15,450000,0,450000,39),
(138,2025,7,14,420000,0,420000,41),
(141,2025,7,3,90000,0,90000,25),
(142,2025,7,2,60000,0,60000,30),
(143,2025,8,11,330000,0,330000,10),
(144,2025,8,15,450000,0,450000,12),
(145,2025,8,14,420000,0,420000,25),
(146,2025,8,8,240000,1010000,1250000,27),
(147,2025,8,12,360000,0,360000,36),
(148,2025,8,14,420000,0,420000,38),
(149,2025,8,13,390000,0,390000,39),
(150,2025,8,13,390000,0,390000,41),
(151,2025,8,2,60000,0,60000,30),
(152,2025,9,13,390000,0,390000,10),
(153,2025,9,13,540000,0,540000,12),
(154,2025,9,11,330000,0,330000,25),
(155,2025,9,13,390000,0,390000,36),
(156,2025,9,13,390000,0,390000,38),
(157,2025,9,12,360000,0,360000,39),
(158,2025,9,10,300000,0,300000,41),
(159,2025,10,11,330000,0,330000,10),
(160,2025,10,10,375000,0,375000,12),
(161,2025,10,10,300000,0,300000,25),
(162,2025,10,12,360000,0,360000,36),
(163,2025,10,11,330000,0,330000,38),
(164,2025,10,12,360000,0,360000,39),
(165,2025,10,11,330000,0,330000,41),
(166,2025,11,12,360000,0,360000,10),
(167,2025,11,10,300000,0,300000,12),
(168,2025,11,11,300000,0,300000,36),
(169,2025,11,12,360000,0,360000,38),
(170,2025,11,11,330000,0,330000,39),
(171,2025,11,12,360000,0,360000,41),
(172,2025,11,12,330000,0,330000,25),
(173,2025,11,3,90000,0,90000,28),
(174,2025,11,3,90000,0,90000,30),
(175,2025,11,1,30000,0,30000,29),
(176,2025,11,0,0,800000,800000,27),
(177,2025,12,13,390000,0,390000,10),
(178,2025,12,11,330000,0,330000,25),
(179,2025,12,14,420000,0,420000,28),
(180,2025,12,10,300000,0,300000,36),
(181,2025,12,10,300000,0,300000,38),
(182,2025,12,13,390000,0,390000,39),
(183,2025,12,13,390000,0,390000,41),
(184,2025,10,0,0,600000,600000,27),
(185,2025,10,0,0,0,0,28),
(186,2025,10,0,0,0,0,29),
(187,2025,10,0,0,0,0,30),
(188,2025,12,9,270000,0,270000,12),
(189,2025,12,0,0,600000,600000,27),
(190,2025,12,1,30000,0,30000,29),
(191,2025,12,3,90000,0,90000,30),
(192,2025,12,8,240000,0,240000,45),
(193,2025,12,4,120000,0,120000,46),
(194,2025,9,0,0,400000,400000,27),
(195,2025,9,0,0,0,0,28),
(196,2025,9,0,0,0,0,29),
(197,2025,9,0,0,0,0,30),
(198,2025,8,0,0,0,0,28),
(199,2025,8,0,0,0,0,29),
(200,2025,8,0,0,0,0,22),
(201,2025,7,0,0,0,0,28),
(202,2025,7,0,0,0,0,29),
(203,2025,7,0,0,0,0,22),
(204,2025,6,0,0,0,0,25),
(205,2025,6,0,0,240000,240000,27),
(206,2025,6,0,0,0,0,29),
(207,2025,6,0,0,0,0,30),
(208,2025,6,0,0,320000,320000,22),
(209,2025,5,0,0,80000,80000,25),
(210,2025,5,0,0,160000,160000,27),
(211,2025,5,0,0,0,0,29),
(212,2025,5,0,0,0,0,30),
(213,2025,5,0,0,240000,240000,22),
(214,2025,4,0,0,0,0,25),
(215,2025,4,0,0,320000,320000,27),
(216,2025,4,0,0,0,0,29),
(217,2025,4,0,0,0,0,30),
(218,2025,4,0,0,320000,320000,22),
(219,2025,3,0,0,0,0,25),
(220,2025,3,0,0,320000,320000,27),
(221,2025,3,0,0,0,0,29),
(222,2025,3,0,0,0,0,30),
(223,2025,3,0,0,320000,320000,22);
/*!40000 ALTER TABLE `teachers_salary` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `teachers_teacher`
--

DROP TABLE IF EXISTS `teachers_teacher`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `teachers_teacher` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `phone_number` varchar(11) DEFAULT NULL,
  `email` varchar(254) DEFAULT NULL,
  `gender` varchar(1) DEFAULT NULL,
  `hire_date` date DEFAULT NULL,
  `resignation_date` date DEFAULT NULL,
  `account_number` varchar(20) DEFAULT NULL,
  `bank_id` bigint DEFAULT NULL,
  `base_salary` int DEFAULT NULL,
  `extra_field1` varchar(100) DEFAULT NULL,
  `extra_field2` varchar(100) DEFAULT NULL,
  `extra_field3` varchar(100) DEFAULT NULL,
  `extra_field4` varchar(100) DEFAULT NULL,
  `other_info` longtext,
  `is_active` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `teachers_teacher_bank_id_383ea179_fk_common_bank_id` (`bank_id`),
  CONSTRAINT `teachers_teacher_bank_id_383ea179_fk_common_bank_id` FOREIGN KEY (`bank_id`) REFERENCES `common_bank` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=48 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `teachers_teacher`
--

LOCK TABLES `teachers_teacher` WRITE;
/*!40000 ALTER TABLE `teachers_teacher` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `teachers_teacher` VALUES
(10,'신유민','01067639333','cookietiger97@naver.com','F','2024-09-02',NULL,'110456508475',1,15000,NULL,NULL,NULL,NULL,'',1),
(11,'이지민',NULL,'gigkgigks7@gmail.com','M','2024-09-02','2024-11-04','3522016367113',2,15000,NULL,NULL,NULL,NULL,'',0),
(12,'이동준','01034438894','ehdwns2548@naver.com','M','2024-08-19',NULL,'3561068468713',2,15000,NULL,NULL,NULL,NULL,'',1),
(13,'정영훈','01023165898',NULL,'M','2024-01-01','2024-11-30','3521648635793',2,15000,NULL,NULL,NULL,NULL,'',0),
(14,'정진형','01097329927','isaacjjh@naver.com','M','2024-09-02','2024-12-20','3021416132351',2,15000,NULL,NULL,NULL,NULL,'',0),
(15,'권승현','01058544038','seank117@naver.com','M','2024-09-02','2025-04-30','42691053588207',3,15000,NULL,NULL,NULL,NULL,'',0),
(16,'김지원','01048014509',NULL,'F','2024-01-01','2024-10-31',NULL,NULL,15000,NULL,NULL,NULL,NULL,'',0),
(17,'김민종','01055720325',NULL,'M','2024-03-04','2024-10-31',NULL,NULL,15000,NULL,NULL,NULL,NULL,'',0),
(22,'이재훈','01077497011','7011james22@gmail.com','M','2024-10-21','2025-08-15','3521937541243',2,15000,NULL,NULL,NULL,NULL,'',0),
(25,'박주아','01033881742','prejua06@gmail.com','F','2024-11-22',NULL,'11130101106062',6,15000,NULL,NULL,NULL,NULL,'',1),
(26,'최예원','01028499369','tina_1228@naver.com','F','2024-11-27','2025-02-21','3521725635833',2,15000,NULL,NULL,NULL,NULL,'',0),
(27,'이시민','01041216228','leesimin20060120@gmail.com','F','2024-12-02','2025-12-31','100093704516',8,15000,NULL,NULL,NULL,NULL,'',0),
(28,'손정연','01073057566','sonnurilee@gmail.com','M','2024-10-06',NULL,'100168608527',8,15000,NULL,NULL,NULL,NULL,NULL,1),
(29,'김지원','01048014509','jiwoon0405@naver.com','F','2024-12-23',NULL,'3521745806253',2,15000,NULL,NULL,NULL,NULL,NULL,1),
(30,'김동근','01096283537','kimdg2006@gmail.com','M','2025-01-10',NULL,'40291032009707',3,15000,NULL,NULL,NULL,NULL,NULL,1),
(31,'이지언','01032440962',NULL,'F','2025-01-14','2025-01-31','110517599561',1,15000,NULL,NULL,NULL,NULL,NULL,0),
(33,'강연우',NULL,NULL,'F','2025-02-03',NULL,'22800104247039',6,15000,NULL,NULL,NULL,NULL,NULL,1),
(34,'이찬혁','01072773962','lch20030614@gmail.com','M','2025-02-03','2025-02-21','110501124240',1,15000,NULL,NULL,NULL,NULL,NULL,0),
(35,'권형준',NULL,NULL,'M','2025-03-03','2025-03-14',NULL,NULL,15000,NULL,NULL,NULL,NULL,NULL,0),
(36,'최재호','01049380551','jaho041125@naver.com','M','2025-03-05','2025-12-22','1002445637644',7,15000,NULL,NULL,NULL,NULL,NULL,0),
(37,'박준서','01068229962','amathmaster@naver.com','M','2025-03-07','2025-06-30','3521759931793',2,15000,NULL,NULL,NULL,NULL,NULL,0),
(38,'김민석','01042074719','alstjr4730@hanyang.ac.kr','M','2025-03-10',NULL,'100223685584',5,15000,NULL,NULL,NULL,NULL,NULL,1),
(39,'강재윤','01032773738','algud050@gmail.com','F','2025-03-10',NULL,'110491324214',1,15000,NULL,NULL,NULL,NULL,NULL,1),
(40,'김나영','01022720746','naroy0420@gmail.com','F','2025-03-19','2025-06-30','3333296598477',4,15000,NULL,NULL,NULL,NULL,NULL,0),
(41,'조희연','01064393960','happyhy04@naver.com','F','2025-05-02',NULL,'100077699577',8,15000,NULL,NULL,NULL,NULL,NULL,1),
(45,'유예지','01044761099','yooyeji803@gmail.com','F','2025-12-03',NULL,'3333347764551',4,15000,NULL,NULL,NULL,NULL,NULL,1),
(46,'최병희','01071016258','dhffkdlcmcm@gmail.com','M','2025-12-24',NULL,'110526135651',1,15000,NULL,NULL,NULL,NULL,NULL,1);
/*!40000 ALTER TABLE `teachers_teacher` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `teachers_teacherstudentassignment`
--

DROP TABLE IF EXISTS `teachers_teacherstudentassignment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `teachers_teacherstudentassignment` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `date` date NOT NULL,
  `memo` longtext,
  `created_at` datetime(6) NOT NULL,
  `student_id` bigint NOT NULL,
  `teacher_id` bigint DEFAULT NULL,
  `assignment_type` varchar(10) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `teachers_teacherstudentassignment_student_id_date_729e328d_uniq` (`student_id`,`date`),
  KEY `teachers_teacherstud_teacher_id_f72d6202_fk_teachers_` (`teacher_id`),
  CONSTRAINT `teachers_teacherstud_student_id_2ee914c4_fk_students_` FOREIGN KEY (`student_id`) REFERENCES `students_student` (`id`),
  CONSTRAINT `teachers_teacherstud_teacher_id_f72d6202_fk_teachers_` FOREIGN KEY (`teacher_id`) REFERENCES `teachers_teacher` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=102 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `teachers_teacherstudentassignment`
--

LOCK TABLES `teachers_teacherstudentassignment` WRITE;
/*!40000 ALTER TABLE `teachers_teacherstudentassignment` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `teachers_teacherstudentassignment` VALUES
(2,'2026-01-09',NULL,'2026-01-09 02:18:39.087327',48,39,'normal'),
(3,'2026-01-09',NULL,'2026-01-09 02:18:39.112804',16,39,'normal'),
(4,'2026-01-09',NULL,'2026-01-09 02:18:55.189161',55,30,'normal'),
(5,'2026-01-09',NULL,'2026-01-09 02:18:55.229359',49,30,'normal'),
(7,'2026-01-09',NULL,'2026-01-09 02:19:07.325792',64,38,'normal'),
(8,'2026-01-09',NULL,'2026-01-09 02:19:07.348223',51,38,'normal'),
(9,'2026-01-09',NULL,'2026-01-09 02:19:07.377933',60,38,'normal'),
(10,'2026-01-09',NULL,'2026-01-09 02:19:19.741635',65,30,'normal'),
(11,'2026-01-09',NULL,'2026-01-09 02:19:19.767370',17,29,'normal'),
(12,'2026-01-09',NULL,'2026-01-09 02:19:19.795199',47,29,'normal'),
(14,'2026-01-09',NULL,'2026-01-09 02:19:54.699614',19,28,'normal'),
(15,'2026-01-09',NULL,'2026-01-09 02:19:54.726887',61,29,'normal'),
(16,'2026-01-09',NULL,'2026-01-09 02:19:54.757797',24,28,'normal'),
(17,'2026-01-09',NULL,'2026-01-09 02:19:54.815603',44,28,'normal'),
(18,'2026-01-09',NULL,'2026-01-09 02:20:08.430599',20,10,'normal'),
(20,'2026-01-09',NULL,'2026-01-09 02:20:08.467402',13,10,'normal'),
(21,'2026-01-09',NULL,'2026-01-09 02:20:08.483328',56,10,'normal'),
(22,'2026-01-09',NULL,'2026-01-09 02:20:08.497105',21,10,'normal'),
(23,'2026-01-09',NULL,'2026-01-09 02:20:08.513627',25,10,'normal'),
(25,'2026-01-09',NULL,'2026-01-09 02:20:20.543280',67,12,'normal'),
(26,'2026-01-09',NULL,'2026-01-09 02:20:20.592304',14,12,'normal'),
(27,'2026-01-09',NULL,'2026-01-09 02:20:20.615605',45,12,'normal'),
(28,'2026-01-09',NULL,'2026-01-09 02:20:20.641501',62,12,'normal'),
(29,'2026-01-09',NULL,'2026-01-09 02:20:20.673662',53,12,'normal'),
(30,'2026-01-09',NULL,'2026-01-09 02:20:20.699470',66,12,'normal'),
(31,'2026-01-09',NULL,'2026-01-09 02:20:33.244549',18,41,'normal'),
(32,'2026-01-09',NULL,'2026-01-09 02:20:33.270923',58,41,'normal'),
(33,'2026-01-09',NULL,'2026-01-09 02:20:33.299258',43,46,'normal'),
(34,'2026-01-09',NULL,'2026-01-09 02:20:33.329271',39,41,'normal'),
(35,'2026-01-09',NULL,'2026-01-09 02:20:33.356112',42,41,'normal'),
(36,'2026-01-09',NULL,'2026-01-09 02:20:33.383565',54,41,'normal'),
(37,'2026-01-09',NULL,'2026-01-09 02:20:42.188009',46,46,'normal'),
(38,'2026-01-09',NULL,'2026-01-09 02:20:42.215969',50,46,'normal'),
(39,'2026-01-09',NULL,'2026-01-09 02:20:42.245892',41,46,'normal'),
(40,'2026-01-09',NULL,'2026-01-09 02:29:07.945713',52,39,'normal'),
(41,'2026-01-12',NULL,'2026-01-09 02:29:49.708708',41,39,'normal'),
(43,'2026-01-12',NULL,'2026-01-09 02:29:56.127721',39,30,'normal'),
(44,'2026-01-12',NULL,'2026-01-09 02:29:58.859940',45,29,'normal'),
(45,'2026-01-12',NULL,'2026-01-09 02:30:02.193852',44,39,'normal'),
(46,'2026-01-16',NULL,'2026-01-17 02:11:17.541517',82,39,'normal'),
(47,'2026-01-16',NULL,'2026-01-17 02:11:25.213685',83,39,'normal'),
(48,'2026-01-16',NULL,'2026-01-17 02:11:31.139596',79,46,'normal'),
(49,'2026-01-16',NULL,'2026-01-17 02:11:49.292717',77,41,'normal'),
(50,'2026-01-16',NULL,'2026-01-17 02:11:53.156772',80,10,'normal'),
(51,'2026-01-16',NULL,'2026-01-17 02:11:56.506646',78,10,'normal'),
(52,'2026-01-16',NULL,'2026-01-17 02:11:59.820329',75,29,'normal'),
(53,'2026-01-16',NULL,'2026-01-17 02:12:02.756972',69,10,'normal'),
(54,'2026-01-16',NULL,'2026-01-17 02:12:17.358854',68,29,'normal'),
(55,'2026-01-16',NULL,'2026-01-17 02:12:21.613084',71,46,'normal'),
(56,'2026-01-16',NULL,'2026-01-17 02:12:25.776400',73,41,'normal'),
(57,'2026-01-16',NULL,'2026-01-17 02:12:30.541715',70,46,'normal'),
(58,'2026-01-16',NULL,'2026-01-17 02:12:51.462952',81,41,'normal'),
(59,'2026-01-16',NULL,'2026-01-17 02:12:58.540100',84,29,'normal'),
(60,'2026-01-16',NULL,'2026-01-17 02:13:06.564875',74,39,'normal'),
(61,'2026-01-16',NULL,'2026-01-17 02:13:35.530595',93,38,'normal'),
(62,'2026-01-16',NULL,'2026-01-17 02:13:51.135726',91,38,'normal'),
(63,'2026-01-16',NULL,'2026-01-17 02:14:03.584642',101,30,'normal'),
(64,'2026-01-16',NULL,'2026-01-17 02:14:15.520715',97,28,'normal'),
(65,'2026-01-16',NULL,'2026-01-17 02:14:20.448790',99,28,'normal'),
(66,'2026-01-16',NULL,'2026-01-17 02:14:26.525775',102,30,'normal'),
(67,'2026-01-16',NULL,'2026-01-17 02:14:32.112108',100,28,'normal'),
(68,'2026-01-16',NULL,'2026-01-17 02:14:43.672301',108,30,'normal'),
(69,'2026-01-16',NULL,'2026-01-17 02:15:11.895594',112,12,'normal'),
(70,'2026-01-16',NULL,'2026-01-17 02:15:20.127280',107,12,'normal'),
(71,'2026-01-19',NULL,'2026-01-17 22:41:34.717168',101,30,'normal'),
(72,'2026-01-19',NULL,'2026-01-17 22:41:45.037187',102,30,'normal'),
(73,'2026-01-19',NULL,'2026-01-17 22:42:00.117194',108,30,'normal'),
(74,'2026-01-19',NULL,'2026-01-17 22:42:08.376921',82,45,'normal'),
(75,'2026-01-19',NULL,'2026-01-17 22:42:23.175869',83,39,'normal'),
(76,'2026-01-19',NULL,'2026-01-17 22:42:40.921850',74,39,'normal'),
(77,'2026-01-19',NULL,'2026-01-17 22:48:12.678888',112,12,'normal'),
(78,'2026-01-19',NULL,'2026-01-17 22:48:23.474373',107,12,'normal'),
(79,'2026-01-19',NULL,'2026-01-17 22:49:24.591555',76,25,'normal'),
(80,'2026-01-19',NULL,'2026-01-17 22:49:36.662465',72,25,'normal'),
(81,'2026-01-19',NULL,'2026-01-17 22:50:23.015848',93,38,'normal'),
(82,'2026-01-19',NULL,'2026-01-17 22:50:30.724735',92,38,'normal'),
(83,'2026-01-19',NULL,'2026-01-17 22:50:40.007354',91,38,'normal'),
(84,'2026-01-19',NULL,'2026-01-17 22:50:49.906109',75,29,'normal'),
(85,'2026-01-19',NULL,'2026-01-17 22:50:58.292833',68,29,'normal'),
(86,'2026-01-19',NULL,'2026-01-17 22:51:02.544839',84,29,'normal'),
(87,'2026-01-19',NULL,'2026-01-17 22:51:17.293706',97,28,'normal'),
(88,'2026-01-19',NULL,'2026-01-17 22:51:24.621650',100,28,'normal'),
(89,'2026-01-19',NULL,'2026-01-17 22:51:37.705612',99,NULL,'absent'),
(90,'2026-01-19',NULL,'2026-01-17 22:51:56.690108',80,10,'normal'),
(91,'2026-01-19',NULL,'2026-01-17 22:51:59.723906',78,10,'normal'),
(92,'2026-01-19',NULL,'2026-01-17 22:52:03.056303',69,10,'normal'),
(93,'2026-01-19',NULL,'2026-01-17 22:52:23.920767',79,46,'normal'),
(94,'2026-01-19',NULL,'2026-01-17 22:52:31.583668',77,41,'normal'),
(95,'2026-01-19',NULL,'2026-01-17 23:06:28.928161',81,41,'normal'),
(96,'2026-01-19',NULL,'2026-01-17 23:06:40.427780',73,41,'normal'),
(97,'2026-01-19',NULL,'2026-01-17 23:07:14.330076',71,46,'normal'),
(98,'2026-01-19',NULL,'2026-01-17 23:07:17.518917',70,46,'normal'),
(99,'2026-01-19',NULL,'2026-01-17 23:07:46.073725',96,45,'normal'),
(100,'2026-01-19',NULL,'2026-01-17 23:16:34.247220',94,NULL,'director'),
(101,'2026-01-19',NULL,'2026-01-17 23:16:44.297765',95,NULL,'director');
/*!40000 ALTER TABLE `teachers_teacherstudentassignment` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `teachers_teacherunavailability`
--

DROP TABLE IF EXISTS `teachers_teacherunavailability`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `teachers_teacherunavailability` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `date` date NOT NULL,
  `reason` varchar(20) NOT NULL,
  `memo` longtext,
  `created_at` datetime(6) NOT NULL,
  `teacher_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `teachers_teacherunavailability_teacher_id_date_08cec086_uniq` (`teacher_id`,`date`),
  CONSTRAINT `teachers_teacherunav_teacher_id_8bea4131_fk_teachers_` FOREIGN KEY (`teacher_id`) REFERENCES `teachers_teacher` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=73 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `teachers_teacherunavailability`
--

LOCK TABLES `teachers_teacherunavailability` WRITE;
/*!40000 ALTER TABLE `teachers_teacherunavailability` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `teachers_teacherunavailability` VALUES
(1,'2026-01-05','personal','일본 방문','2026-01-09 01:26:10.461309',25),
(2,'2026-01-06','personal','일본 방문','2026-01-09 01:26:10.519398',25),
(3,'2026-01-07','personal','일본 방문','2026-01-09 01:26:10.548026',25),
(4,'2026-01-08','personal','일본 방문','2026-01-09 01:26:10.573822',25),
(5,'2026-01-09','personal','일본 방문','2026-01-09 01:26:10.596634',25),
(6,'2026-01-10','personal','일본 방문','2026-01-09 01:26:10.619373',25),
(7,'2026-01-11','personal','일본 방문','2026-01-09 01:26:10.646688',25),
(8,'2026-01-12','personal','일본 방문','2026-01-09 01:26:10.673903',25),
(9,'2026-01-13','personal','일본 방문','2026-01-09 01:26:10.696959',25),
(10,'2026-01-14','personal','일본 방문','2026-01-09 01:26:10.722920',25),
(11,'2026-01-15','personal','일본 방문','2026-01-09 01:26:10.751668',25),
(12,'2026-01-16','personal','일본 방문','2026-01-09 01:26:10.774890',25),
(13,'2026-01-17','personal','일본 방문','2026-01-09 01:26:10.799429',25),
(14,'2026-01-18','personal','일본 방문','2026-01-09 01:26:10.824443',25),
(15,'2026-01-13','personal','학교 수업','2026-01-09 01:27:03.306131',12),
(16,'2026-01-13','personal','학교 수업','2026-01-09 01:28:03.890183',46),
(17,'2026-01-13','personal','학교 수업','2026-01-09 01:28:28.722616',41),
(18,'2026-02-09','personal','','2026-01-09 01:30:20.974031',25),
(19,'2026-02-10','personal','','2026-01-09 01:30:21.012167',25),
(20,'2026-02-02','personal','일본 여행','2026-01-09 01:30:43.319645',39),
(21,'2026-02-03','personal','일본 여행','2026-01-09 01:30:43.356933',39),
(22,'2026-01-30','personal','','2026-01-09 01:31:07.499475',41),
(23,'2026-02-03','personal','','2026-01-09 01:31:27.900663',41),
(24,'2026-02-05','personal','','2026-01-09 01:31:53.758713',41),
(25,'2026-02-06','personal','','2026-01-09 01:31:53.797254',41),
(26,'2026-02-07','personal','','2026-01-09 01:31:53.826192',41),
(27,'2026-02-08','personal','','2026-01-09 01:31:53.850916',41),
(28,'2026-02-09','personal','','2026-01-09 01:31:53.878353',41),
(29,'2026-02-10','personal','','2026-01-09 01:31:53.902242',41),
(30,'2026-01-15','personal','','2026-01-09 01:33:05.009355',45),
(31,'2026-01-16','personal','','2026-01-09 01:33:05.032769',45),
(32,'2026-01-23','personal','','2026-01-09 01:33:27.224391',45),
(33,'2026-01-29','personal','','2026-01-09 01:33:46.291672',45),
(34,'2026-01-30','personal','','2026-01-09 01:33:46.329926',45),
(35,'2026-02-03','personal','','2026-01-09 01:34:13.325406',45),
(36,'2026-02-04','personal','','2026-01-09 01:34:13.361846',45),
(37,'2026-02-05','personal','','2026-01-09 01:34:13.384754',45),
(38,'2026-02-06','personal','','2026-01-09 01:34:13.408690',45),
(39,'2026-02-13','personal','','2026-01-09 01:34:36.237567',45),
(40,'2026-02-20','personal','','2026-01-09 01:35:27.242409',45),
(41,'2026-02-27','personal','','2026-01-09 01:35:45.334355',45),
(42,'2026-01-09','personal','','2026-01-09 01:36:25.294199',45),
(43,'2026-01-09','personal','','2026-01-09 23:37:11.003736',38),
(44,'2026-01-13','personal','','2026-01-10 01:11:42.484845',38),
(45,'2026-01-15','personal','','2026-01-10 01:11:51.385794',38),
(46,'2026-01-20','personal','','2026-01-10 01:12:02.315980',38),
(47,'2026-01-22','personal','','2026-01-10 01:13:24.038115',38),
(48,'2026-01-27','personal','','2026-01-10 01:13:34.196298',38),
(49,'2026-01-29','personal','','2026-01-10 01:13:41.190233',38),
(51,'2026-02-03','personal','','2026-01-10 01:14:37.833216',38),
(52,'2026-02-05','personal','','2026-01-10 01:14:45.533716',38),
(53,'2026-02-10','personal','','2026-01-10 01:14:57.370597',38),
(54,'2026-02-12','personal','','2026-01-10 01:15:05.172477',38),
(55,'2026-01-13','personal','','2026-01-10 01:15:22.104854',10),
(56,'2026-01-15','personal','','2026-01-10 01:15:30.789816',10),
(57,'2026-01-20','personal','','2026-01-10 01:15:38.421296',10),
(58,'2026-01-22','personal','','2026-01-10 01:16:13.394393',10),
(59,'2026-01-27','personal','','2026-01-10 01:16:22.706949',10),
(60,'2026-01-29','personal','','2026-01-10 01:16:29.103051',10),
(61,'2026-02-03','personal','','2026-01-10 01:16:38.928977',10),
(62,'2026-02-05','personal','','2026-01-10 01:16:51.871162',10),
(63,'2026-02-10','personal','','2026-01-10 01:17:01.468545',10),
(64,'2026-02-12','personal','','2026-01-10 01:17:12.451303',10),
(65,'2026-01-14','personal','','2026-01-13 22:14:28.959348',33),
(66,'2026-01-16','personal','','2026-01-15 20:58:04.555197',33),
(67,'2026-01-19','personal','','2026-01-15 21:26:09.324786',33),
(68,'2026-01-21','personal','','2026-01-15 21:26:40.894268',33),
(69,'2026-01-21','personal','','2026-01-17 22:44:30.650022',38),
(70,'2026-01-28','personal','','2026-01-17 22:44:42.665757',38),
(71,'2026-02-04','personal','','2026-01-17 22:44:57.626963',38),
(72,'2026-02-11','personal','','2026-01-17 22:45:08.250937',38);
/*!40000 ALTER TABLE `teachers_teacherunavailability` ENABLE KEYS */;
UNLOCK TABLES;
commit;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*M!100616 SET NOTE_VERBOSITY=@OLD_NOTE_VERBOSITY */;

-- Dump completed on 2026-01-17 23:23:11
