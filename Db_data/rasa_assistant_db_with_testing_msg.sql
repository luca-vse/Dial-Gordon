-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Nov 23, 2023 at 09:11 PM
-- Server version: 10.4.28-MariaDB
-- PHP Version: 8.2.4

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `rasa_assistant_db`
--
CREATE DATABASE IF NOT EXISTS `rasa_assistant_db` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `rasa_assistant_db`;

-- --------------------------------------------------------

--
-- Table structure for table `blacklist`
--

DROP TABLE IF EXISTS `blacklist`;
CREATE TABLE `blacklist` (
  `id_blacklist` int(10) NOT NULL,
  `id_user` int(10) NOT NULL,
  `phone_number_sender` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `contacts`
--

DROP TABLE IF EXISTS `contacts`;
CREATE TABLE `contacts` (
  `id_contact` int(10) NOT NULL,
  `id_user` int(10) NOT NULL,
  `phone_number` varchar(50) NOT NULL,
  `name` varchar(100) NOT NULL,
  `surname` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `contacts`
--

INSERT INTO `contacts` (`id_contact`, `id_user`, `phone_number`, `name`, `surname`) VALUES
(2, 2, '508802100', 'John', 'Clark'),
(3, 2, '702530610', 'Patric', 'Great'),
(4, 2, '805420341', 'Tom', 'Brown');

-- --------------------------------------------------------

--
-- Table structure for table `messages`
--

DROP TABLE IF EXISTS `messages`;
CREATE TABLE `messages` (
  `id_message` int(20) NOT NULL,
  `id_user` int(10) NOT NULL,
  `date_send` datetime NOT NULL,
  `number_sender` varchar(50) NOT NULL,
  `label` varchar(100) NOT NULL DEFAULT 'unread',
  `category` varchar(200) NOT NULL,
  `message_text` longtext NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `messages`
--

INSERT INTO `messages` (`id_message`, `id_user`, `date_send`, `number_sender`, `label`, `category`, `message_text`) VALUES
(22, 2, '2024-02-09 17:51:17', '508802100', 'unread', '', 'Hello Bob, John Clark calling you. The meeting will be on November 18 at 6 pm '),
(29, 2, '2024-02-11 09:48:24', '702530610', 'unread', '', 'Hello Bob, Patric calling. Please call me, we are in trouble and need to find solution fast'),
(30, 2, '2024-01-11 09:53:37', '805420341', 'unread', '', 'Hello Bob, my name is Tom. It is important that you call me for details what will happen tommorrow at the presentation'),
(32, 2, '2024-01-03 21:09:51', '606601100', 'unread', '', 'Hello bob, I have advantageous offer for you. If you want to know more let me know.');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id_user` int(10) NOT NULL,
  `name` varchar(100) NOT NULL,
  `surname` varchar(200) NOT NULL,
  `phone_number` varchar(50) NOT NULL,
  `pin` varchar(200) NOT NULL,
  `greeting_message` varchar(1000) NOT NULL DEFAULT '"The person you are calling is unavailable at the moment. Please, leave a message"'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id_user`, `name`, `surname`, `phone_number`, `pin`, `greeting_message`) VALUES
(2, 'Bob', 'Smith', '456230140', '$2b$12$MqxQm4O7Ra9Sa9o7DAHQ5.VTUGPKUNLZG3ia0Vxs7WmIRRHEvv3kW', 'hello you have called Bob please leave a message after the beep');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `blacklist`
--
ALTER TABLE `blacklist`
  ADD PRIMARY KEY (`id_blacklist`),
  ADD KEY `FK_blacklist_users_iduser` (`id_user`);

--
-- Indexes for table `contacts`
--
ALTER TABLE `contacts`
  ADD PRIMARY KEY (`id_contact`),
  ADD KEY `FK_contacts_users_id_user` (`id_user`);

--
-- Indexes for table `messages`
--
ALTER TABLE `messages`
  ADD PRIMARY KEY (`id_message`),
  ADD KEY `FK_messages_users_iduser` (`id_user`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id_user`),
  ADD UNIQUE KEY `IX_user_phone_number` (`phone_number`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `blacklist`
--
ALTER TABLE `blacklist`
  MODIFY `id_blacklist` int(10) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=37;

--
-- AUTO_INCREMENT for table `contacts`
--
ALTER TABLE `contacts`
  MODIFY `id_contact` int(10) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `messages`
--
ALTER TABLE `messages`
  MODIFY `id_message` int(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=33;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id_user` int(10) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `blacklist`
--
ALTER TABLE `blacklist`
  ADD CONSTRAINT `FK_blacklist_users_iduser` FOREIGN KEY (`id_user`) REFERENCES `users` (`id_user`) ON UPDATE CASCADE;

--
-- Constraints for table `contacts`
--
ALTER TABLE `contacts`
  ADD CONSTRAINT `FK_contacts_users_id_user` FOREIGN KEY (`id_user`) REFERENCES `users` (`id_user`) ON UPDATE CASCADE;

--
-- Constraints for table `messages`
--
ALTER TABLE `messages`
  ADD CONSTRAINT `FK_messages_users_iduser` FOREIGN KEY (`id_user`) REFERENCES `users` (`id_user`) ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
