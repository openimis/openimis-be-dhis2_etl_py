IF OBJECT_ID('dbo.ufn_dhis2_uid') IS NOT NULL
  DROP FUNCTION ufn_dhis2_uid
GO
CREATE FUNCTION dbo.ufn_dhis2_uid (@uuid varchar(50)) 
  RETURNS varchar(11)
  AS
  BEGIN 
	DECLARE @uuid_tmp varchar(36) = REPLACE(@uuid,'-','') ;
	DECLARE @lead varchar(32) = @uuid_tmp
	--SET @lead = CONCAT(substring(@lead,2,34), substring(@lead,34,2));
	DECLARE @tail1 int = 0, @tail2 int =0, @tail3 int = 0;
	DECLARE @i int = 0;
	DEcLARE @looprun int = 1;
	DECLARE @return varchar(12)='';
	DECLARE @HEX2DEC table(hex char, dec int);
	Insert Into @HEX2DEC
	Values 
	('0',0),('1',1),('2',2),('3',3),('4',4),('5',5),('6',6),('7',7),('8',8),('9',9),('A',10),('B',11),('C',12),('D',13),('E',14),('F',15),
	('G',16),('H',17),('I',18),('J',19),('K',20),('L',21),('M',22),('N',23),('O',24),('P',25),('Q',26),('R',27),
	('S',28),('T',29),('U',30),('V',31),('W',32),('X',33),('Y',34),('Z',35),('a',36),('b',37),('c',38),('d',39),
	('e',40),('f',41),('g',42),('h',43),('i',44),('j',45),('k',46),('l',47),('m',48),('n',49),('o',50),('p',51),
	('q',52),('r',53),('s',54),('t',55),('u',56),('v',57),('w',58),('x',59),('y',60),('z',61),('A',62),('B',63);
	WHILE (@i < 11)
	BEGIN 

		SET @tail1 = (SELECT TOP(1) dec FROM @HEX2DEC WHERE hex = substring(@lead,1,1));
		SET @tail2 = (SELECT TOP(1) dec FROM @HEX2DEC WHERE hex = substring(@lead,2,1)) ;

		SET @lead = CONCAT(substring(@lead,3,30), substring(@lead,1,2));
		SET @return = @return + CASE WHEN @i=0 AND (@tail1 * 4 + @tail2/4)<10 THEN
			 ((SELECT TOP(1) hex FROM @HEX2DEC WHERE dec = @tail1 * 4 + @tail2/4 + 10 ))
		ELSE 
			((SELECT TOP(1) hex FROM @HEX2DEC WHERE dec = @tail1 * 4 + @tail2/4))
		END
		SET @i = @i + 1
	END
	RETURN SUBSTRING(@return,1,12);
  END
  GO
-- removing not utf-8



IF OBJECT_ID('dbo.ufn_remove_not_utf_8') IS NOT NULL
  DROP FUNCTION ufn_remove_not_utf_8
GO
CREATE FUNCTION ufn_remove_not_utf_8 
(
    @nstring nvarchar(255)
)
RETURNS varchar(255)
AS
BEGIN

    DECLARE @Result varchar(255)
    SET @Result = ''

    DECLARE @nchar nvarchar(1)
    DECLARE @position int

    SET @position = 1
    WHILE @position <= LEN(@nstring)
    BEGIN
        SET @nchar = SUBSTRING(@nstring, @position, 1)
        --Unicode & ASCII are the same from 1 to 255.
        --Only Unicode goes beyond 255
        --0 to 31 are non-printable characters
        IF UNICODE(@nchar) between 32 and 255 
			IF UNICODE(@nchar) = 34
				SET @Result = @Result + ''''
			ELSE
				SET @Result = @Result + @nchar
        SET @position = @position + 1
    END

    RETURN @Result

END
GO

-- check uniqueness Location


-- check uniqueness Claims

-- Step 1: Enable Ole Automation Procedures
sp_configure 'show advanced options', 1;
GO
RECONFIGURE;
GO
sp_configure 'Ole Automation Procedures', 1;
GO
RECONFIGURE;
GO

DECLARE @ORG_UNITS_ATT_LOCID_CODE varchar(100) = 'gMNNTAdZbW1';
DECLARE @ORG_UNITS_ATT_TYPE_CODE  varchar(100) = 'ffZOxd5V2UK';
DECLARE @ORG_UNITS_ROOT varchar(11) = 'Paq10GBF7Wy';

-- Step 2: Write Text File
DECLARE @OLE INT
DECLARE @FileID INT
EXECUTE sp_OACreate 'Scripting.FileSystemObject', @OLE OUT
EXECUTE sp_OAMethod @OLE, 'OpenTextFile', @FileID OUT, 'C:\temp\DHIS2Data.json', 2, 1
DECLARE @StartOrgUnit varchar(MAX) = '{ "organisationUnits": [{"name":"root", "shortName":"root", "code":"root", "openingDate":"2000-01-01", "id":"'+@ORG_UNITS_ROOT+'"},';


-- starting the json
EXECUTE sp_OAMethod @FileID, 'WriteLine', Null, @StartOrgUnit
-- ORG Unit

DECLARE @LocationCode varchar(100)
DECLARE @LocationUUID varchar(100)
DECLARE @LocationUid varchar(100)
DECLARE @LocationName varchar(100)
DECLARE @LocationShortName varchar(100)
DECLARE @LocationParentUid varchar(100)
DECLARE @LocationAttLocId varchar(100)
DECLARE @LocationAttType varchar(100)
DECLARe @ValidityTo date

DECLARE @JSON nvarchar(MAX);
DECLARE @JSON1 nvarchar(MAX);
DECLARE @JSON2 nvarchar(MAX);

DECLARE @RunningTotal BIGINT = 0;

DECLARE @LOCATION TABLE(LocationCode  varchar(100),LocationUUID varchar(100),LocationUid  varchar(100),LocationName varchar(100), LocationParentUid varchar(100), LocationAttLocId varchar(100), LocationAttType varchar(100), LocationLevel int, ValidityTo date)

INSERT into @LOCATION  SELECT 
      l.[LocationCode] as LocationCode
	  ,l.LocationUUID
	  ,dbo.ufn_dhis2_uid(l.LocationUUID) as LocationUid
	  ,dbo.ufn_remove_not_utf_8(l.[LocationName])as LocationName
	  ,dbo.ufn_dhis2_uid(p.LocationUUID) as LocationParentUid
      ,l.[LocationUUID] as LocationAttLocId
	  ,l.[LocationType] as LocationAttType
	  ,l.ValidityTo
	  , 1 as LocationLevel
  FROM tblLocations l
  LEFT JOIN [tblLocations] p on  l.ParentLocationId = p.LocationId
  WHERE l.LegacyId is NULL and p.LegacyId is NULL 
  and l.LocationType in ('R')
  AND l.LocationName  not LIKE '%unding%' and l.LocationCode  not LIKE 'F%';

  INSERT into @LOCATION  SELECT 
      l.[LocationCode] as LocationCode
	  ,l.LocationUUID
	  ,dbo.ufn_dhis2_uid(l.LocationUUID) as LocationUid
	  ,dbo.ufn_remove_not_utf_8(l.[LocationName])as LocationName
	  ,dbo.ufn_dhis2_uid(p.LocationUUID) as LocationParentUid
      ,l.[LocationUUID] as LocationAttLocId
	  ,l.[LocationType] as LocationAttType
	  ,l.ValidityTo
	 , 2 as LocationLevel
  FROM tblLocations l
  LEFT JOIN [tblLocations] p on  l.ParentLocationId = p.LocationId
  WHERE l.LegacyId is NULL and p.LegacyId is NULL 
  and l.LocationType in ('D')
  AND l.LocationName  not LIKE '%unding%' and l.LocationCode  not LIKE 'F%'
  AND (SELECT COUNT(*) FROM @LOCATION  r WHERE r.LocationUUID=p.LocationUUID )=1;

  INSERT into @LOCATION  SELECT 
      l.[LocationCode] as LocationCode
	  ,l.LocationUUID
	  ,dbo.ufn_dhis2_uid(l.LocationUUID) as LocationUid
	  ,dbo.ufn_remove_not_utf_8(l.[LocationName])as LocationName
	  ,dbo.ufn_dhis2_uid(p.LocationUUID) as LocationParentUid
      ,l.[LocationUUID] as LocationAttLocId
	  ,l.[LocationType] as LocationAttType
	  ,l.ValidityTo
	 , 3 as LocationLevel
  FROM tblLocations l
  LEFT JOIN [tblLocations] p on  l.ParentLocationId = p.LocationId
  WHERE l.LegacyId is NULL and p.LegacyId is NULL 
  and l.LocationType in ('W')
  AND l.LocationName  not LIKE '%unding%' and l.LocationCode  not LIKE 'F%'
  AND (SELECT COUNT(*) FROM @LOCATION  r WHERE r.LocationUUID=p.LocationUUID )=1;

    INSERT into @LOCATION  SELECT 
      l.[LocationCode] as LocationCode
	  ,l.LocationUUID
	  ,dbo.ufn_dhis2_uid(l.LocationUUID) as LocationUid
	  ,dbo.ufn_remove_not_utf_8(l.[LocationName])as LocationName
	  ,dbo.ufn_dhis2_uid(p.LocationUUID) as LocationParentUid
      ,l.[LocationUUID] as LocationAttLocId
	  ,l.[LocationType] as LocationAttType
	  ,l.ValidityTo
	  , 4 as LocationLevel
  FROM tblLocations l
  LEFT JOIN [tblLocations] p on  l.ParentLocationId = p.LocationId
  WHERE l.LegacyId is NULL and p.LegacyId is NULL 
  and l.LocationType in ('V')
  AND l.LocationName  not LIKE '%unding%' and l.LocationCode  not LIKE 'F%'
  AND (SELECT COUNT(*) FROM @LOCATION  r WHERE r.LocationUUID=p.LocationUUID )=1;

      INSERT into @LOCATION  SELECT 
      l.[HFCode] as LocationCode
	  ,l.HfUUID
	  ,dbo.ufn_dhis2_uid(l.HfUUID) as LocationUid
	  ,dbo.ufn_remove_not_utf_8(l.[HFName])as LocationName
	  ,dbo.ufn_dhis2_uid(p.LocationUUID) as LocationParentUid
      ,l.[HfUUID] as LocationAttLocId
	  ,l.[HfLevel] as LocationAttType
	  ,l.ValidityTo
	  , 5 as LocationLevel
  FROM tblHF l
  LEFT JOIN [tblLocations] p on  l.LocationId = p.LocationId
  WHERE l.ValidityTo is NULL and p.ValidityTo is NULL 
  AND (SELECT COUNT(*) FROM @LOCATION  r WHERE r.LocationUUID=p.LocationUUID )=1;

DECLARE CUR_TEST CURSOR FAST_FORWARD FOR
    SELECT LocationCode, LocationUUID, LocationUid, LocationName, LocationParentUid, LocationAttLocId, LocationAttType, ValidityTo FROM @LOCATION
  ORDER BY LocationLevel 

OPEN CUR_TEST
FETCH NEXT FROM CUR_TEST INTO @LocationCode, @LocationUUID, @LocationUid, @LocationName, @LocationParentUid, @LocationAttLocId, @LocationAttType, @ValidityTo
 
WHILE @@FETCH_STATUS = 0
BEGIN
	SET @JSON = '{"name":"' +  @LocationName + '", "shortName":"' + @LocationName + '", "code":"' + @LocationUUID  + '", "openingDate":"2000-01-01", "id":"' + @LocationUid + '", "parent":{"id":"'
            + CASE WHEN LEN(@LocationParentUid)>1 THEN  @LocationParentUid  ELSE @ORG_UNITS_ROOT  END + '"}'

       
            + '},' + CASE WHEN  @ValidityTo IS NULL THEN  ''  ELSE ', "closedDate":"' + YEAR(@ValidityTo)+ '-' + MONTH(@ValidityTo) + DAY(@ValidityTo) END  ;
FETCH NEXT FROM CUR_TEST INTO @LocationCode, @LocationUUID, @LocationUid, @LocationName, @LocationParentUid, @LocationAttLocId, @LocationAttType,  @ValidityTo
	SET @JSON = CASE WHEN @@FETCH_STATUS = 0 THEN @JSON ELSE LEFT(@JSON, LEN(@JSON) - 1) END
	EXECUTE sp_OAMethod @FileID, 'WriteLine', Null, @JSON
END

-- EXECUTE sp_OAMethod @FileID, 'WriteLine', Null, '}'

CLOSE CUR_TEST
DEALLOCATE CUR_TEST






-- ending the json
EXECUTE sp_OAMethod @FileID, 'WriteLine', Null, ']'








EXECUTE sp_OADestroy @FileID
EXECUTE sp_OADestroy @OLE
GO

-- Step 3: Disable Ole Automation Procedures
sp_configure 'show advanced options', 1;
GO
RECONFIGURE;
GO
sp_configure 'Ole Automation Procedures', 0;
GO
RECONFIGURE;
GO

SELECT (0x38 + 0x0f +0x07)