CREATE TABLE `bonds` (
  `bond_id` BIGINT,
  `country` varchar(30),
  `duration` VARCHAR(10),
  `currency` VARCHAR(8),
  PRIMARY KEY (`bond_id`)
);

CREATE TABLE `bonds_values` (
  `bond_id` BIGINT,
  `date` DATETIME,
  `rate` DECIMAL(5,2) NOT NULL,
  PRIMARY KEY (`bond_id`, `date`),
  FOREIGN KEY (`bond_id`) REFERENCES `bonds`(`bond_id`)
);

CREATE TABLE `commodities` (
  `id` BIGINT,
  `commoditiyName` VARCHAR(30) NOT NULL,
  `symbol` VARCHAR(10) NOT NULL,
  PRIMARY KEY (`id`)
);

CREATE TABLE `commoditiy_values` (
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
  `changePercent` DECIMAL(12,2),
  `vwap` DECIMAL(12,2),
  `changeOverTime` DECIMAL(12,2),
  PRIMARY KEY (`commodity_id`, `date`),
  FOREIGN KEY (`commodity_id`) REFERENCES `commodities`(`ID`)
);

CREATE TABLE `Companies` (
  `ID` BIGINT,
  `CompanyName` VARCHAR(30) NOT NULL,
  `Symbol` VARCHAR(10) NOT NULL,
  PRIMARY KEY (`ID`)
);

CREATE TABLE `Changelogs` (
  `CompanyID` BIGINT,
  `Date` DATETIME,
  `NewSymbol` VARCHAR(10),
  `OldSymbol` VARCHAR(10) NOT NULL,
  `SymbolChanged` BOOLEAN,
  `NewName` VARCHAR(30),
  `OldName` VARCHAR(30) NOT NULL,
  `NameChanged` BOOLEAN,
  PRIMARY KEY (`CompanyID`, `Date`),
  FOREIGN KEY (`CompanyID`) REFERENCES `Companies`(`ID`)
);

CREATE TABLE `Stock_Values` (
  `CompanyID` BIGINT,
  `Date` DATETIME,
  `Open` DECIMAL(12,2),
  `High` DECIMAL(12,2),
  `Low` DECIMAL(12,2),
  `Close` DECIMAL(12,2),
  `Volume` DECIMAL(12,2),
  `Exchange` VARCHAR(20),
  PRIMARY KEY (`CompanyID`, `Date`),
  FOREIGN KEY (`CompanyID`) REFERENCES `Companies`(`ID`)
);

CREATE TABLE `Company_Statements` (
  `CompanyID` BIGINT,
  `Date` DATETIME,
  `Sector` VARCHAR(30),
  `Industry` VARCHAR(30),
  `FullTimeEmployees` DECIMAL,
  `MarketCap` DECIMAL(12,2),
  `TrailingPE` DECIMAL(12,2),
  `ShortOfFloat` DECIMAL(4,2),
  `TraillingAnnualDividendYield` DECIMAL(7,5),
  `EnterpriseValue` DECIMAL(13,2),
  `Revenue` DECIMAL(13,2),
  `ReturnOnAssets` DECIMAL(5,2),
  `ReturnOnEquity` DECIMAL(5,2),
  PRIMARY KEY (`CompanyID`, `Date`),
  FOREIGN KEY (`CompanyID`) REFERENCES `Companies`(`ID`)
);

CREATE TABLE `indexes` (
  `id` BIGINT,
  `indexname` VARCHAR(30) NOT NULL,
  `symbol` VARCHAR(10) NOT NULL,
  PRIMARY KEY (`id`)
);

CREATE TABLE `index_values` (
  `index_id` BIGINT,
  `date` DATETIME,
  `price` DECIMAL(12,2),
  `extendedPrice` DECIMAL(12,2),
  `change` DECIMAL(12,2),
  `dayHigh` DECIMAL(12,2),
  `dayLow` DECIMAL(12,2),
  `previousClose` DECIMAL(12,2),
  `volume` DECIMAL(12,2),
  `open` DECIMAL(12,2),
  `close` DECIMAL(12,2),
  `yearHigh` DECIMAL(12,2),
  `yearLow` DECIMAL(12,2),
  `changesPercentage` DECIMAL(12,2),
  PRIMARY KEY (`index_id`, `date`),
  FOREIGN KEY (`index_id`) REFERENCES `indexes`(`id`)
);