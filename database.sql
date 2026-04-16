SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+03:00";

CREATE TABLE `access_level` (
  `id` int NOT NULL,
  `name` varchar(10) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `access_level` (`id`, `name`) VALUES
(1, 'FULL'),
(2, 'TRIAL'),
(3, 'ADMIN'),
(4, 'GUEST');

CREATE TABLE `details_key` (
  `id` int NOT NULL,
  `id_key` int NOT NULL,
  `id_protocol` int NOT NULL,
  `value1` varchar(50) NOT NULL,
  `value2` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `protocols` (
  `id` int NOT NULL,
  `name` varchar(30) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `protocols` (`id`, `name`) VALUES
(1, 'Hysteria'),
(2, 'VLESS');

CREATE TABLE `users` (
  `id` int NOT NULL,
  `tg_id` varchar(20) NOT NULL,
  `entry_date` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `access` int NOT NULL,
  `username` varchar(100) DEFAULT NULL,
  `isAvailable` tinyint(1) NOT NULL DEFAULT '1'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `_keys` (
  `id` int NOT NULL,
  `user_id` int NOT NULL,
  `expires_at` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

ALTER TABLE `access_level`
  ADD PRIMARY KEY (`id`);

ALTER TABLE `details_key`
  ADD PRIMARY KEY (`id`),
  ADD KEY `id_key` (`id_key`),
  ADD KEY `id_protocol` (`id_protocol`);

ALTER TABLE `protocols`
  ADD PRIMARY KEY (`id`);

ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD KEY `access` (`access`);

ALTER TABLE `_keys`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

ALTER TABLE `access_level`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

ALTER TABLE `details_key`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

ALTER TABLE `protocols`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

ALTER TABLE `users`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

ALTER TABLE `_keys`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

ALTER TABLE `details_key`
  ADD CONSTRAINT `details_key_ibfk_1` FOREIGN KEY (`id_key`) REFERENCES `_keys` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `details_key_ibfk_2` FOREIGN KEY (`id_protocol`) REFERENCES `protocols` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `users`
  ADD CONSTRAINT `users_ibfk_1` FOREIGN KEY (`access`) REFERENCES `access_level` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `_keys`
  ADD CONSTRAINT `_keys_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
