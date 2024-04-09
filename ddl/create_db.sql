CREATE DATABASE IF NOT EXISTS ats_db;

USE ats_db;

-- Bonds tables --

CREATE TABLE `bonds` (
  `id` BIGINT,
  `treasuryName` VARCHAR(300),
  PRIMARY KEY (`id`)
);
CREATE INDEX treasury_idx ON bonds (treasuryName);

CREATE TABLE `bond_values` (
  `bond_id` BIGINT,
  `date` DATETIME,
  `1_month` DECIMAL(5,2),
  `2_month` DECIMAL(5,2),
  `3_month` DECIMAL(5,2),
  `6_month` DECIMAL(5,2),
  `1_year` DECIMAL(5,2),
  `2_year` DECIMAL(5,2),
  `3_year` DECIMAL(5,2),
  `5_year` DECIMAL(5,2),
  `7_year` DECIMAL(5,2),
  `10_year` DECIMAL(5,2),
  `20_year` DECIMAL(5,2),
  `30_year` DECIMAL(5,2),
  PRIMARY KEY (`bond_id`, `date`),
  FOREIGN KEY (`bond_id`) REFERENCES `bonds`(`id`)
);

-- Commodities tables --

CREATE TABLE `commodities` (
  `id` BIGINT,
  `commodityName` VARCHAR(300) NOT NULL,
  `symbol` VARCHAR(10) NOT NULL,
  PRIMARY KEY (`id`)
);
CREATE INDEX commodity_symbol_idx ON commodities (symbol);

CREATE TABLE `realtime_commodity_values` (
  `commodity_id` BIGINT,
  `date` DATETIME,
  `price` DECIMAL(16,2),
  `changePercentage` DECIMAL(12,4),
  `change` DECIMAL(16,2),
  `dayLow` DECIMAL(16,2),
  `dayHigh` DECIMAL(16,2),
  `yearHigh` DECIMAL(16,2),
  `yearLow` DECIMAL(16,2),
  `mktCap` BIGINT,
  `exchange` VARCHAR(300),
  `volume` BIGINT,
  `volumeAvg` BIGINT,
  `open` DECIMAL(16,2),
  `prevClose` DECIMAL(16,2),
  PRIMARY KEY (`commodity_id`, `date`),
  FOREIGN KEY (`commodity_id`) REFERENCES `commodities`(`ID`)
);

CREATE TABLE `historical_commodity_values` (
  `commodity_id` BIGINT,
  `date` DATETIME,
  `open` DECIMAL(16,2),
  `high` DECIMAL(16,2),
  `low` DECIMAL(16,2),
  `close` DECIMAL(16,2),
  `adjClose` DECIMAL(16,2),
  `volume` BIGINT,
  `unadjustedVolume` BIGINT,
  `change` DECIMAL(16,2),
  `changePercentage` DECIMAL(12,4),
  `vwap` DECIMAL(16,2),
  `changeOverTime` DECIMAL(16,2),
  PRIMARY KEY (`commodity_id`, `date`),
  FOREIGN KEY (`commodity_id`) REFERENCES `commodities`(`ID`)
);

-- Company/Stocks tables --

CREATE TABLE `companies` (
  `id` BIGINT,
  `companyName` VARCHAR(300),
  `symbol` VARCHAR(10) NOT NULL,
  PRIMARY KEY (`id`)
);
CREATE INDEX company_symbol_idx ON companies (symbol);

CREATE TABLE `company_changelogs` (
  `company_id` BIGINT,
  `date` DATETIME,
  `companyName` VARCHAR(300),
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
  `price` DECIMAL(16,2),
  `beta` DECIMAL(16,2),
  `volumeAvg` BIGINT,
  `mktCap` BIGINT,
  `lastDiv` DECIMAL(16,2),
  `changes` DECIMAL(16,2),
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
  `dcfDiff` DECIMAL(16,2),
  `dcf` DECIMAL(16,2),
  `ipoDate` DATETIME,
  `isEtf` BOOLEAN,
  `isActivelyTrading` BOOLEAN,
  `isAdr` BOOLEAN,
  `isFund` BOOLEAN,
  PRIMARY KEY (`company_id`, `date`),
  FOREIGN KEY (`company_id`) REFERENCES `companies`(`id`)
);

CREATE TABLE `realtime_stock_values` (
  `company_id` BIGINT,
  `date` DATETIME,
  `price` DECIMAL(16,2),
  `changePercentage` DECIMAL(12,4),
  `change` DECIMAL(16,2),
  `dayLow` DECIMAL(16,2),
  `dayHigh` DECIMAL(16,2),
  `yearHigh` DECIMAL(16,2),
  `yearLow` DECIMAL(16,2),
  `mktCap` BIGINT,
  `exchange` VARCHAR(300),
  `volume` BIGINT,
  `volumeAvg` BIGINT,
  `open` DECIMAL(16,2),
  `prevClose` DECIMAL(16,2),
  `eps` DECIMAL(16,2),
  `pe` DECIMAL(16,2),
  `earningsAnnouncement` DATETIME,
  `sharesOutstanding` BIGINT,
  PRIMARY KEY (`company_id`, `date`),
  FOREIGN KEY (`company_id`) REFERENCES `companies`(`id`)
);

CREATE TABLE `historical_stock_values` (
  `company_id` BIGINT,
  `date` DATETIME,
  `open` DECIMAL(16,2),
  `high` DECIMAL(16,2),
  `low` DECIMAL(16,2),
  `close` DECIMAL(16,2),
  `adjClose` DECIMAL(16,2),
  `volume` BIGINT,
  `unadjustedVolume` BIGINT,
  `change` DECIMAL(16,2),
  `changePercentage` DECIMAL(12,4),
  `vwap` DECIMAL(16,2),
  `changeOverTime` DECIMAL(16,2),
  PRIMARY KEY (`company_id`, `date`),
  FOREIGN KEY (`company_id`) REFERENCES `companies`(`id`)
);

-- Index tables --

CREATE TABLE `indexes` (
  `id` BIGINT,
  `indexName` VARCHAR(300),
  `symbol` VARCHAR(10) NOT NULL,
  PRIMARY KEY (`id`)
);
CREATE INDEX index_symbol_idx ON indexes (symbol);

CREATE TABLE `realtime_index_values` (
  `index_id` BIGINT,
  `date` DATETIME,
  `price` DECIMAL(16,2),
  `changePercentage` DECIMAL(12,4),
  `change` DECIMAL(16,2),
  `dayLow` DECIMAL(16,2),
  `dayHigh` DECIMAL(16,2),
  `yearHigh` DECIMAL(16,2),
  `yearLow` DECIMAL(16,2),
  `mktCap` BIGINT,
  `exchange` VARCHAR(300),
  `volume` BIGINT,
  `volumeAvg` BIGINT,
  `open` DECIMAL(16,2),
  `prevClose` DECIMAL(16,2),
  PRIMARY KEY (`index_id`, `date`),
  FOREIGN KEY (`index_id`) REFERENCES `indexes`(`id`)
);

CREATE TABLE `historical_index_values` (
  `index_id` BIGINT,
  `date` DATETIME,
  `open` DECIMAL(16,2),
  `high` DECIMAL(16,2),
  `low` DECIMAL(16,2),
  `close` DECIMAL(16,2),
  `adjClose` DECIMAL(16,2),
  `volume` BIGINT,
  `unadjustedVolume` BIGINT,
  `change` DECIMAL(16,2),
  `changePercentage` DECIMAL(12,4),
  `vwap` DECIMAL(16,2),
  `changeOverTime` DECIMAL(16,2),
  PRIMARY KEY (`index_id`, `date`),
  FOREIGN KEY (`index_id`) REFERENCES `indexes`(`id`)
);

-- User Tables --

CREATE TABLE `users` (
  `id` BIGINT AUTO_INCREMENT,
  `username` VARCHAR(300) NOT NULL,
  `password` VARCHAR(300) NOT NULL,
  `firstName` VARCHAR(300) NOT NULL,
  `lastName` VARCHAR(300) NOT NULL,
  `isAdmin` BOOLEAN NOT NULL,
  PRIMARY KEY (`id`)
);

-- System Logs Table --
CREATE TABLE `system_logs` (
  `id` BIGINT NOT NULL AUTO_INCREMENT
  PRIMARY KEY,
  `date` DATETIME NOT NULL,
  `timezone` VARCHAR(50),
  `level` VARCHAR(10),
  `message` VARCHAR(400)
);