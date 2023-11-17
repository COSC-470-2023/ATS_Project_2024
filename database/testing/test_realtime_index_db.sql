CREATE TABLE `test_indexes` (
`id` BIGINT,
`indexName` VARCHAR(300) NOT NULL,
`symbol` VARCHAR(10) NOT NULL,
PRIMARY KEY (`id`));

CREATE TABLE `test_realtime_index_values` (
`index_id` BIGINT,
`date` DATETIME,
`price` DECIMAL(12,2),
`changePercentage` DECIMAL(12,4),
`change` DECIMAL(12,2),
`dayHigh` DECIMAL(12,2),
`dayLow` DECIMAL(12,2),
`yearHigh` DECIMAL(12,2),
`yearLow` DECIMAL(12,2),
`mktCap` BIGINT,
`exchange` varchar(300),
`open` DECIMAL(12,2),
`prevClose` DECIMAL(12,2),
`volume` DECIMAL(12,2),
`volAvg` DECIMAL(12,2),
PRIMARY KEY (`index_id`, `date`),
FOREIGN KEY (`index_id`) REFERENCES `indexes`(`id`));
