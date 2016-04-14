

-- -----------------------------------------------------
-- Cleanup
-- -----------------------------------------------------
drop schema if exists `frontend`;

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


-- -----------------------------------------------------
-- Populate DB with test content
-- -----------------------------------------------------
insert into `frontend`.`mac` values (1,"00:00:00:00:00:00");
insert into `frontend`.`users` values (1,"admin","admin","1",null,1);


