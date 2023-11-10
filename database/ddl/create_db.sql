CREATE DATABASE IF NOT EXISTS ats_db;

USE ats_db;

-- Bonds tables --

CREATE TABLE `bonds` (
  `bond_id` BIGINT,
  `country` VARCHAR(300),
  `duration` VARCHAR(300),
  `currency` VARCHAR(300),
  PRIMARY KEY (`bond_id`)
);

CREATE TABLE `bonds_values` (
  `bond_id` BIGINT,
  `date` DATETIME,
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
  `changePercentage` DECIMAL(4,6),
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
  `changePercentage` DECIMAL(12,2),
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
  `listed` boolean,
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
  `sector` VARCHAR(300),
  `industry` VARCHAR(300),
  `fullTimeEmployees` DECIMAL,
  `marketCap` DECIMAL(12,2),
  `trailingPE` DECIMAL(12,2),
  `shortOfFloat` DECIMAL(4,2),
  `traillingAnnualDividendYield` DECIMAL(7,5),
  `enterpriseValue` DECIMAL(13,2),
  `netIncome` DECIMAL(13,2),
  `revenue` DECIMAL(13,2),
  `returnOnAssets` DECIMAL(5,2),
  `returnOnEquity` DECIMAL(5,2),
  PRIMARY KEY (`company_id`, `date`),
  FOREIGN KEY (`company_id`) REFERENCES `companies`(`id`)
);

CREATE TABLE `real_time_stock_values` (
  `company_id` BIGINT,
  `date` DATETIME,
  `price` DECIMAL(12,2),
  `changePercentage` DECIMAL(4,6),
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
  `earningsAnnouncement` DECIMAL(12,2),
  `sharesOutstanding` DECIMAL(12,2),
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
  `volume` DECIMAL(12,2),
  `unadj_Volume` DECIMAL(12,2),
  `change` DECIMAL(12,2),
  `changePercentage` DECIMAL(4,6),
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
  `changePercentage` DECIMAL(4,6),
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
  `unadj_Volume` DECIMAL(12,2),
  `change` DECIMAL(12,2),
  `changePercentage` DECIMAL(4,6),
  `vwap` DECIMAL(12,2),
  `changeOverTime` DECIMAL(12,2),
  PRIMARY KEY (`index_id`, `date`),
  FOREIGN KEY (`index_id`) REFERENCES `indexes`(`id`)
);
