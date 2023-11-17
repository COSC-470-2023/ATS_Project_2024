CREATE DATABASE IF NOT EXISTS ats_db;

USE ats_db;

-- Bonds tables --

CREATE TABLE `bonds` (
  `bond_id` BIGINT,
  `name` VARCHAR(300),
  `currency` VARCHAR(300),
  PRIMARY KEY (`bond_id`)
);

CREATE TABLE `bonds_values` (
  `bond_id` BIGINT,
  `date` DATETIME,
  `duration` VARCHAR(300),
  `rate` DECIMAL(5,2) NOT NULL,
  PRIMARY KEY (`bond_id`, `date`),
  FOREIGN KEY (`bond_id`) REFERENCES `bonds`(`bond_id`)
);

-- Commodities tables --

CREATE TABLE `commodities` (
  `id` BIGINT,
  `commoditiyName` VARCHAR(300) NOT NULL,
  `symbol` VARCHAR(10) NOT NULL,
  PRIMARY KEY (`id`)
);

CREATE TABLE `realtime_commoditiy_values` (
  `commodity_id` BIGINT,
  `date` DATETIME,
  `price` DECIMAL(12,2),
  `changePercentage` DECIMAL(6,6),
  `change` DECIMAL(12,2),
  `dayHigh` DECIMAL(12,2),
  `dayLow` DECIMAL(12,2),
  `yearHigh` DECIMAL(12,2),
  `yearLow` DECIMAL(12,2),
  `mktCap` BIGINT,
  `exhchange` VARCHAR(300),
  `open` DECIMAL(12,2),
  `prevClose` DECIMAL(12,2),
  `volume` DECIMAL(12,2),
  `volAvg` DECIMAL(12,2),
  PRIMARY KEY (`commodity_id`, `date`),
  FOREIGN KEY (`commodity_id`) REFERENCES `commodities`(`ID`)
);

CREATE TABLE `historical_commoditiy_values` (
  `commodity_id` BIGINT,
  `date` DATETIME,
  `open` DECIMAL(12,2),
  `high` DECIMAL(12,2),
  `low` DECIMAL(12,2),
  `close` DECIMAL(12,2),
  `adjClose` DECIMAL(12,2),
  `volume` DECIMAL(12,2),
  `unadjustedVolume` DECIMAL(12,2),
  `change` DECIMAL(12,2),
  `changePercentage` DECIMAL(6,6),
  `vwap` DECIMAL(12,2),
  `changeOverTime` DECIMAL(12,2),
  PRIMARY KEY (`commodity_id`, `date`),
  FOREIGN KEY (`commodity_id`) REFERENCES `commodities`(`ID`)
);

-- Company/Stocks tables --

CREATE TABLE `companies` (
  `id` BIGINT,
  `companyName` VARCHAR(300) NOT NULL,
  `symbol` VARCHAR(10) NOT NULL,
  `isListed` boolean,
  PRIMARY KEY (`id`)
);

CREATE TABLE `company_changelogs` (
  `company_id` BIGINT,
  `date` DATETIME,
  `companyName` VARCHAR(300) NOT NULL,
  `newCompanyName` VARCHAR(300),
  `nameChanged` BOOLEAN,
  `symbol` VARCHAR(10) NOT NULL,
  `newSymbol` VARCHAR(10),
  `symbolChanged` BOOLEAN,
  PRIMARY KEY (`company_id`, `date`),
  FOREIGN KEY (`company_id`) REFERENCES `companies`(`id`)
);

CREATE TABLE `company_statements` (
  `company_id` BIGINT,
  `date` DATETIME,
  `price` DECIMAL(12,2),
  `beta` DECIMAL(12,2),
  `volAvg` DECIMAL(12,2),
  `mktCap` BIGINT,
  `lastDiv` DECIMAL(12,2),
  `changes` DECIMAL(12,2),
  `currency` VARCHAR(300),
  `cik` VARCHAR(300),
  `isin` VARCHAR(300),
  `cusip` VARCHAR(300),
  `exchangeFullName` VARCHAR(300),
  `exchange` VARCHAR(300),
  `industry` VARCHAR(300),
  `ceo` VARCHAR(300),
  `sector` VARCHAR(300),
  `country` VARCHAR(300),
  `fullTimeEmployees` BIGINT,
  `phone` VARCHAR(300),
  `address` VARCHAR(300),
  `city` VARCHAR(300),
  `state` VARCHAR(300),
  `zip` VARCHAR(300),
  `dcfDiff` DECIMAL(12,2),
  `dcf` DECIMAL(12,2),
  `ipoDate` DATETIME,
  `isEtf` BOOLEAN,
  `isActivelyTrading` BOOLEAN,
  `isAdr` BOOLEAN,
  `isFund` BOOLEAN,
  PRIMARY KEY (`company_id`, `date`),
  FOREIGN KEY (`company_id`) REFERENCES `companies`(`id`)
);

CREATE TABLE `real_time_stock_values` (
  `company_id` BIGINT,
  `date` DATETIME,
  `price` DECIMAL(12,2),
  `changePercentage` DECIMAL(6,6),
  `change` DECIMAL(12,2),
  `dayHigh` DECIMAL(12,2),
  `dayLow` DECIMAL(12,2),
  `yearHigh` DECIMAL(12,2),
  `yearLow` DECIMAL(12,2),
  `mktCap` BIGINT,
  `exhchange` VARCHAR(300),
  `open` DECIMAL(12,2),
  `prevClose` DECIMAL(12,2),
  `volume` DECIMAL(12,2),
  `volAvg` DECIMAL(12,2),
  `eps` DECIMAL(12,2),
  `pe` DECIMAL(12,2),
  `earningsAnnouncement` DATETIME,
  `sharesOutstanding` BIGINT,
  PRIMARY KEY (`company_id`, `date`),
  FOREIGN KEY (`company_id`) REFERENCES `companies`(`id`)
);

CREATE TABLE `historical_stock_values` (
  `company_id` BIGINT,
  `date` DATETIME,
  `open` DECIMAL(12,2),
  `high` DECIMAL(12,2),
  `low` DECIMAL(12,2),
  `close` DECIMAL(12,2),
  `adjclose` DECIMAL(12,2),
  `volume` BIGINT,
  `unadjustedVolume` BIGINT,
  `change` DECIMAL(12,2),
  `changePercentage` DECIMAL(6,6),
  `vwap` DECIMAL(12,2),
  `changeOverTime` DECIMAL(12,2),
  PRIMARY KEY (`company_id`, `date`),
  FOREIGN KEY (`company_id`) REFERENCES `companies`(`id`)
);

-- Index tables --

CREATE TABLE `indexes` (
  `id` BIGINT,
  `indexname` VARCHAR(300) NOT NULL,
  `symbol` VARCHAR(10) NOT NULL,
  PRIMARY KEY (`id`)
);

CREATE TABLE `realtime_index_values` (
  `index_id` BIGINT,
  `date` DATETIME,
  `price` DECIMAL(12,2),
  `changePercentage` DECIMAL(6,6),
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
  FOREIGN KEY (`index_id`) REFERENCES `indexes`(`id`)
);

CREATE TABLE `historical_index_values` (
  `index_id` BIGINT,
  `date` DATETIME,
  `open` DECIMAL(12,2),
  `high` DECIMAL(12,2),
  `low` DECIMAL(12,2),
  `close` DECIMAL(12,2),
  `adjClose` DECIMAL(12,2),
  `volume` DECIMAL(12,2),
  `unadjustedVolume` DECIMAL(12,2),
  `change` DECIMAL(12,2),
  `changePercentage` DECIMAL(6,6),
  `vwap` DECIMAL(12,2),
  `changeOverTime` DECIMAL(12,2),
  PRIMARY KEY (`index_id`, `date`),
  FOREIGN KEY (`index_id`) REFERENCES `indexes`(`id`)
);
