

-- -----------------------------------------------------
-- Cleanup
-- -----------------------------------------------------
drop schema if exists `frontend`;
drop schema if exists `Api-server`;
-- -----------------------------------------------------
-- Schema Api-server
-- -----------------------------------------------------

CREATE SCHEMA IF NOT EXISTS `Api-server` DEFAULT CHARACTER SET utf8 ;
USE `Api-server` ;

-- -----------------------------------------------------
-- Table `Api-server`.`Beacons`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Api-server`.`Beacons` (
  `serial` INT AUTO_INCREMENT  NOT NULL,
  `PSK` BLOB NOT NULL,
  `comment` VARCHAR(255) NULL,
  `last_seen` DATETIME NULL,
  PRIMARY KEY (`serial`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `Api-server`.`MAC`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Api-server`.`MAC` (
  `id` INT AUTO_INCREMENT  NOT NULL,
  `MAC` VARCHAR(45) NOT NULL,
  `last_seen` DATETIME NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `Api-server`.`EventType`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Api-server`.`EventType` (
  `Id` INT NOT NULL,
  `name` VARCHAR(45) NULL,
  PRIMARY KEY (`Id`))
ENGINE = InnoDB;



-- -----------------------------------------------------
-- Table `Api-server`.`VisibilityEvent`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Api-server`.`VisibilityEvent` (
  `id` INT AUTO_INCREMENT NOT NULL,
  `event_time` DATETIME NULL,
  `beacon` INT NOT NULL,
  `Mac` INT NOT NULL,
  `event_type` INT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_VisibilityEvent_Beacons_idx` (`beacon` ASC),
  INDEX `fk_VisibilityEvent_MAC1_idx` (`Mac` ASC),
  INDEX `fk_VisibilityEvent_EventType1_idx` (`event_type` ASC),
  CONSTRAINT `fk_VisibilityEvent_Beacons`
    FOREIGN KEY (`beacon`)
    REFERENCES `Api-server`.`Beacons` (`serial`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_VisibilityEvent_MAC1`
    FOREIGN KEY (`Mac`)
    REFERENCES `Api-server`.`MAC` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_VisibilityEvent_EventType1`
    FOREIGN KEY (`event_type`)
    REFERENCES `Api-server`.`EventType` (`Id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- ----------------------------------------------------
-- Schema frontend
-- -----------------------------------------------------

CREATE SCHEMA  `frontend` DEFAULT CHARACTER SET utf8 ;
USE `frontend` ;

-- -----------------------------------------------------
-- Table `forntend`.`mac`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `frontend`.`mac` (
  `id` INT AUTO_INCREMENT  NOT NULL,
  `mac` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `frontend`.`Users`
-- -----------------------------------------------------
drop table if exists `frontend`.`users`;
CREATE TABLE  `frontend`.`users` (
  `id` INT AUTO_INCREMENT NOT NULL ,
  `login` VARCHAR(45) NOT NULL,
  `password` VARCHAR(45) NOT NULL,
  `user_data` int NOT NULL,
  `picture` VARCHAR(45) NULL,
  `MAC_id` INT NULL,
  PRIMARY KEY (`id`),
   INDEX `fk_Users_MAC1_idx` (`MAC_id` ASC),
   CONSTRAINT `fk_Users_MAC1`
    FOREIGN KEY (`MAC_id`)
    REFERENCES `frontend`.`mac` (`id`)
     ON DELETE NO ACTION
     ON UPDATE NO ACTION )
ENGINE = InnoDB;

drop table if exists `frontend`.`user_has_device`;

CREATE TABLE `user_has_device` (
`id` int NOT NULL AUTO_INCREMENT,
`user_id` int, 
`mac_id` int,
`start_time` DATETIME,
`end_time` DATETIME,
PRIMARY KEY(id));


-- --------------------------------------------------
-- View `frontend`.`check_in`
-- -----------------------------------------------------
CREATE 
    ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `Api-server`.`new_view` AS
    SELECT 
        `Api-server`.`VisibilityEvent`.`event_time` AS `event_time`
    FROM
        ((`Api-server`.`VisibilityEvent`
        JOIN `Api-server`.`Beacons`)
        JOIN `Api-server`.`EventType` ON (((`Api-server`.`VisibilityEvent`.`beacon` = `Api-server`.`Beacons`.`serial`)
            AND (`Api-server`.`VisibilityEvent`.`event_type` = `Api-server`.`EventType`.`Id`))))
;
CREATE 
    ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `frontend`.`check_in_events` AS
    SELECT 
        `Api-server`.`VisibilityEvent`.`id` AS `check_id`,
        `Api-server`.`VisibilityEvent`.`event_time` AS `register_time`,
        `frontend`.`users`.`Login` AS `login`,
        `Api-server`.`MAC`.`MAC` AS `mac_address`,
        `Api-server`.`Beacons`.`comment` AS `beacon_name`,
        `Api-server`.`EventType`.`name` AS `event_name`,
        `frontend`.`users`.`id` as `user_id`,
        `Api-server`.`VisibilityEvent`.`event_type` AS `event_type`,
        `Api-server`.`MAC`.`id` AS `mac_id`,
        `Api-server`.`Beacons`.`serial` AS `beacon_id`
        
        
    FROM
       (((((`Api-server`.`VisibilityEvent`
		JOIN `Api-server`.`MAC`)
		JOIN `Api-server`.`Beacons`)
		JOIN `Api-server`.`EventType`)
		JOIN `frontend`.`users`
		 ON (((`Api-server`.`VisibilityEvent`.`beacon` = `Api-server`.`Beacons`.`serial`)
            AND (`Api-server`.`VisibilityEvent`.`event_type` = `Api-server`.`EventType`.`Id`)
            AND (`Api-server`.`VisibilityEvent`.`MAC` = `Api-server`.`MAC`.`id`)
            AND (`frontend`.`users`.`MAC_id` = `Api-server`.`MAC`.`id`)))));



-- -----------------------------------------------------
-- Populate DB with test content
-- -----------------------------------------------------


insert into `Api-server`.`MAC` (`id`,`MAC`,`last_seen`)values (1,"00:00:00:00:00:00",now());

insert into `frontend`.`mac` values (1,"00:00:00:00:00:00");
insert into `frontend`.`users` values (1,"admin","admin","1",null,1);

insert into `Api-server`.`EventType` values(1,"DHCP Discovery");
insert into `Api-server`.`EventType` values(2,"PING Event");
insert into `Api-server`.`EventType` values(3,"User Request");

 insert into `Api-server`.`Beacons` values (1,"secureKey001","comment on beacon1",null);
 insert into `Api-server`.`VisibilityEvent` values(1,now(),1,1,1);