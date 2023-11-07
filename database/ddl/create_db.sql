CREATE TABLE `Bonds` (
  `Date` DATETIME,
  `BondDuration` VARCHAR(10),
  `Rate` DECIMAL(5,2) NOT NULL,
  PRIMARY KEY (`Date`, `BondDuration`)
);

CREATE TABLE `Commodity_List` (
  `ID` BIGINT,
  `Name` VARCHAR(30) NOT NULL,
  `Symbol` VARCHAR(5) NOT NULL,
  PRIMARY KEY (`ID`)
);

CREATE TABLE `Commodity_Values` (
  `CommodityID` BIGINT,
  `Date` DATETIME,
  `Open` DECIMAL(12,2),
  `High` DECIMAL(12,2),
  `Low` DECIMAL(12,2),
  `Close` DECIMAL(12,2),
  `Volume` DECIMAL(12,2),
  PRIMARY KEY (`CommodityID`, `Date`),
  FOREIGN KEY (`CommodityID`) REFERENCES `Commodity_List`(`ID`)
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

CREATE TABLE `Indices` (
  `ID` BIGINT,
  `Symbol` VARCHAR(10) NOT NULL,
  `Name` VARCHAR(20) NOT NULL,
  PRIMARY KEY (`ID`)
);

CREATE TABLE `Index_Values` (
  `Date` DATETIME,
  `IndexID` BIGINT,
  `Open` DECIMAL(12,2),
  `High` DECIMAL(12,2),
  `Low` DECIMAL(12,2),
  `Close` DECIMAL(12,2),
  `Volume` DECIMAL(12,2),
  PRIMARY KEY (`Date`, `IndexID`),
  FOREIGN KEY (`IndexID`) REFERENCES `Indices`(`ID`)
);